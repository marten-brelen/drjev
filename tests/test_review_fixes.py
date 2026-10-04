"""Regression tests for problems found in an independent review of the analysis code."""
import numpy as np
import pandas as pd

from drjev import analyze, frames
from drjev import metrics as M
from tests.test_bootstrap import KW, frame


def test_pooled_unit_is_the_mean_of_its_seeds_not_a_blend():
    rng = np.random.default_rng(1)
    a = frame(800, 1, rng)
    b = a.copy()
    b["run"] = "r2"
    for k in range(5):                                         # seed 2 is far more confident than seed 1
        b[f"pg{k}"] = (b["grade"] == k) * 0.92 + 0.016
    b["pref"] = np.clip(b["pref"] * 1.3, 0, 0.999)
    pooled = pd.concat([a, b], ignore_index=True)
    one = lambda f: analyze.compute(frames.arrays(f), pd.factorize(f["patient_id"])[0], **KW)
    ma, mb = one(a), one(b)
    mp = analyze.compute_unit(frames.arrays(pooled), pd.factorize(pooled["patient_id"])[0], **KW)
    for met in ("ece_grade", "ref_auroc", "aurc_grade", "qwk", "patient_ref_sens", "patient_ref_spec", "n"):
        assert mp[met] == np.mean([ma[met], mb[met]]) or abs(mp[met] - np.mean([ma[met], mb[met]])) < 1e-12, met


def test_model_compared_with_itself_differs_by_exactly_zero():
    rng = np.random.default_rng(2)
    A = frames.arrays(frame(300, 1, rng))
    m, r = analyze.matched_sens(A, A, "ref", 2, "direct")
    assert m == r


def test_selective_prediction_does_not_depend_on_row_order():
    conf = np.full(100, 0.7)
    correct = np.r_[np.ones(60), np.zeros(40)]
    assert M.aurc(conf, correct) == M.aurc(conf, correct[::-1])


def test_specialist_learns_grades_only_from_the_grading_training_set():
    from drjev.specialist import _labels
    rows = pd.DataFrame({"grade": [3.0, 3.0], "gradable": [1.0, 1.0], "maculopathy": [1.0, 1.0], "split": ["train", "q3_train"]})
    y = _labels(rows)
    assert y[0].tolist() == [3, 1, 1]
    assert y[1].tolist() == [-1, -1, 1]                        # the maculopathy dataset teaches maculopathy only
