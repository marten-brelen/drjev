"""Ground-truth rules, answer handling and the imajev request/response mapping."""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

from drjev import questions
from drjev.adapters import base, imajev
from drjev.analyze import Sampler
from drjev.targets import UNKNOWN, target

QFILE = Path(__file__).resolve().parent.parent / "config" / "questions.yaml"
nan = float("nan")


def test_clinical_definitions():
    # sight-threatening = any maculopathy, or severe NPDR, or PDR
    assert target("q5_sight", 1, 1, 1) == 1 and target("q5_sight", 3, 1, 0) == 1 and target("q5_sight", 4, 1, nan) == 1
    assert target("q5_sight", 2, 1, 0) == 0 and target("q5_sight", 2, 1, nan) == 0
    # referable = moderate NPDR or worse, or any maculopathy
    assert target("q4_refer", 2, 1, 0) == 1 and target("q4_refer", 0, 1, 1) == 1 and target("q4_refer", 1, 1, 0) == 0
    # an ungradeable image: "no" to Q1, "unknown" to everything else
    assert target("q1_gradeable", nan, 0, nan) == 0
    assert all(target(q, nan, 0, nan) == UNKNOWN for q in ("q2_grade", "q3_maculopathy", "q4_refer", "q5_sight"))
    # a graded image with no quality label counts as gradeable; no maculopathy label means no Q3 target
    assert target("q1_gradeable", 2, nan, nan) == 1 and target("q3_maculopathy", 2, nan, nan) is None


def test_questions_load_three_wordings():
    assert questions.n_variants(QFILE) == 3
    for v in range(3):
        qs = {q.id: q for q in questions.load(QFILE, v)}
        assert list(qs) == ["q1_gradeable", "q2_grade", "q3_maculopathy", "q4_refer", "q5_sight"]
        assert qs["q2_grade"].kind == "score" and len(qs["q2_grade"].options) == 5
        assert qs["q1_gradeable"].keys == ["no", "yes"] and not qs["q1_gradeable"].allow_unknown


def test_explicit_unknown_option_is_split_off():
    q = questions.load(QFILE, 0)[3]                          # q4_refer

    class NoAbstain(base.Adapter):
        def _score(self, path, sent):
            assert sent.keys == ["no", "yes", "unknown"] and sent.kind == "choice"
            return [0.2, 0.3, 0.5], None

    a = NoAbstain({"name": "x"}).answer("img", [q])[0]
    assert a.u == pytest.approx(0.5) and a.p == pytest.approx([0.4, 0.6])


def test_unknown_folds_into_ungradeable_for_q1():
    q1 = questions.load(QFILE, 0)[0]
    a = base.finalise(q1, q1, [0.1, 0.9], 0.5, 1.0)          # half the mass on "unknown"
    assert a.u is None and a.p == pytest.approx([0.55, 0.45])


def test_imajev_parse_documented_response():
    qs = questions.load(QFILE, 0)
    q1, q2 = qs[0], qs[1]
    # README: noul = P(yes) + unknown/2
    p, u = imajev.parse_answer(qs[3], {"type": "noul", "noul": 0.082, "unknown_probability": 0.022})
    assert u == 0.022 and p[1] == pytest.approx((0.082 - 0.011) / (1 - 0.022))
    p, u = imajev.parse_answer(q2, {"type": "score", "probabilities": {str(i): x for i, x in enumerate([0.1, 0.2, 0.3, 0.25, 0.15])}, "unknown_probability": 0.3})
    assert p == [0.1, 0.2, 0.3, 0.25, 0.15] and u == 0.3
    body = imajev.build_request([q1, q2])
    assert body["questions"]["q2_grade"]["type"] == "score" and len(body["questions"]["q2_grade"]["criteria"]) == 5
    assert set(body["questions"]["q1_gradeable"]["criteria"]) == {"true", "false"}


IMAJEV = os.environ.get("IMAJEV_DIR")


@pytest.mark.skipif(not IMAJEV or not Path(IMAJEV, "src", "vision_decision").is_dir(), reason="set IMAJEV_DIR to a checkout of mohit67890/imajev")
def test_round_trip_through_imajev_own_code():
    """Our request must pass imajev's request validation, and our parser must invert its response builder."""
    sys.path[:0] = [str(Path(IMAJEV, "src")), str(Path(IMAJEV, "scripts"))]
    from vision_decision.jev_api import to_request_with_plan, to_response
    from vision_decision.scoring import compile_question, result_from_logits
    rng = np.random.default_rng(1)
    qs = questions.load(QFILE, 0)

    class FakeSession:
        """Stands in for the HTTP server: runs imajev's real request -> prompt -> response code on random logits."""

        def post(self, url, files, data, timeout):
            request, plan = to_request_with_plan(json.loads(data["request"]))
            results, self.truth = [], {}
            for f in request.fields:
                _, choices, _ = compile_question(f, request.state)
                logits = rng.normal(0, 1.5, len(choices)).tolist()
                results.append(result_from_logits(choices, logits))
                e = np.exp(np.array(logits) - max(logits))
                self.truth[f.id] = e / e.sum()                # imajev orders candidates options..., unknown last
            payload = to_response(request, results, "stub", plan)

            class R:
                status_code = 200

                def json(self_inner):
                    return payload
            return R()

    a = imajev.ImajevHTTP({"name": "stub", "url": "http://stub"})
    a.session = FakeSession()
    a.url = "http://stub"
    img = Path(__file__)
    for _ in range(25):
        ans = a.answer(str(img), qs)
        for q, an in zip(qs, ans):
            full = a.session.truth[q.id]
            known = full[:-1] / full[:-1].sum()
            if q.kind == "noul":                              # imajev's boolean candidates are (yes, no); ours are (no, yes)
                known = known[::-1]
            if q.allow_unknown:
                assert an.u == pytest.approx(full[-1], abs=1e-6)
                assert an.p == pytest.approx(known.tolist(), abs=1e-5)
            else:                                             # Q1: unknown counts as "no"
                assert an.u is None and an.p[1] == pytest.approx(full[0], abs=1e-5)


def test_bootstrap_sampler_keeps_patients_together():
    import pandas as pd
    f = pd.DataFrame({"patient_id": ["a", "a", "b", "c", "c", "c"]})
    s = Sampler(f["patient_id"].tolist())
    R = s.rows(f)
    rows, inst = Sampler.take(R, np.arange(3))
    assert sorted(rows.tolist()) == [0, 1, 2, 3, 4, 5]
    rows, inst = Sampler.take(R, np.array([2, 2, 0]))        # patient c twice, patient a once
    assert sorted(rows.tolist()) == [0, 1, 3, 3, 4, 4, 5, 5]
    assert len(set(inst.tolist())) == 3                      # the two copies of c are separate patients
