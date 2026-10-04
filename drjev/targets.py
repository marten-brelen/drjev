"""Ground truth for each question, in one place. Used for training targets, calibration and analysis.

Definitions (protocol 5.2):
  referable          = grade >= 2, or maculopathy present
  sight-threatening  = grade >= 3, or maculopathy present
Where a dataset has no maculopathy label the grade-only rule applies.
For an ungradeable image the correct answer to Q2-Q5 is "unknown"."""
from __future__ import annotations

import pandas as pd

UNKNOWN = "unknown"
QIDS = ("q1_gradeable", "q2_grade", "q3_maculopathy", "q4_refer", "q5_sight")
GRADE_CUT = {"q4_refer": 2, "q5_sight": 3}


def target(qid: str, grade, gradable, mac):
    """Index of the correct option, the string 'unknown', or None when the image has no label for this question."""
    has_grade = pd.notna(grade)
    if qid == "q1_gradeable":
        if gradable == 0:
            return 0
        if gradable == 1 or has_grade:
            return 1
        return None
    if gradable == 0:
        return UNKNOWN
    if qid == "q2_grade":
        return int(grade) if has_grade else None
    if qid == "q3_maculopathy":
        return int(mac) if pd.notna(mac) else None
    if not has_grade:
        return None
    return int(grade >= GRADE_CUT[qid] or (pd.notna(mac) and mac == 1))
