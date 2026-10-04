"""Common interface for every model: image + questions in, a probability per option out."""
from __future__ import annotations

import time
from dataclasses import dataclass

from ..questions import UNKNOWN_KEY, Question


@dataclass
class Answer:
    p: list[float]          # probability of each option, given that the model answers (sums to 1)
    u: float | None         # probability of "unknown"; None when the question has no abstain option
    ms: float = 0.0         # wall-clock milliseconds for this question


class Adapter:
    """Subclasses implement _score(image_path, question) -> list of probabilities over question.options,
    or _score_many for models that take several questions in one request.

    has_abstain: the model has its own trained "unknown" output (only imajev at the time of writing).
    For models without one, questions that allow "unknown" are sent as a single choice among the
    options plus an explicit "unknown" option (protocol section 6.2)."""

    has_abstain = False
    explicit_unknown = True  # False for models that cannot take an extra "unknown" option at all
    tested = False          # set True only for adapters exercised by the test suite

    def __init__(self, run: dict):
        self.run = run
        self.name = run["name"]
        if "has_abstain" in run:
            self.has_abstain = bool(run["has_abstain"])

    def load(self):
        pass

    def close(self):
        pass

    # ---- to implement ----
    def _score(self, image_path: str, q: Question):
        """Return (probabilities over q.options, unknown probability or None)."""
        raise NotImplementedError

    def _score_many(self, image_path: str, qs: list[Question]):
        return [self._score(image_path, q) for q in qs]

    # ---- shared logic ----
    def _as_sent(self, q: Question) -> Question:
        """The question as this model receives it."""
        if self.has_abstain or not q.allow_unknown or not self.explicit_unknown:
            return q
        opts = list(q.options) + [(UNKNOWN_KEY, q.meta.get("unknown_option", "unknown").split(":", 1)[-1].strip())]
        return Question(q.id, "choice", q.instruction, opts, False, q.variant, q.meta)

    def answer(self, image_path: str, questions: list[Question]) -> list[Answer]:
        sent = [self._as_sent(q) for q in questions]
        t0 = time.perf_counter()
        raw = self._score_many(image_path, sent)
        ms = (time.perf_counter() - t0) * 1000 / max(1, len(questions))
        return [finalise(q, s, p, u, ms) for q, s, (p, u) in zip(questions, sent, raw)]


def finalise(q: Question, sent: Question, p, u, ms: float) -> Answer:
    """Map what the model returned onto the question as defined in the protocol."""
    p = [max(0.0, float(x)) for x in p]
    if len(p) != len(sent.options):
        raise ValueError(f"{q.id}: model returned {len(p)} probabilities for {len(sent.options)} options")
    if sent is not q:                      # an explicit "unknown" option was appended: split it off
        tot = sum(p) or 1.0
        u = p[-1] / tot
        p = p[:-1]
    s = sum(p)
    p = [x / s for x in p] if s > 0 else [1.0 / len(p)] * len(p)
    if u is not None:
        u = min(1.0, max(0.0, float(u)))
        if not q.allow_unknown:            # no abstain on this question: "unknown" counts as the first option ("no")
            p = [x * (1 - u) for x in p]
            p[0] += u
            u = None
    return Answer(p, u, ms)
