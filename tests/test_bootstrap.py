"""The patient-clustered bootstrap gives intervals of the right width."""
import numpy as np
import pandas as pd

from drjev import analyze

KW = dict(primary="direct", bins=15, sel_acc=0.95)


def frame(n_patients: int, eyes: int, rng) -> pd.DataFrame:
    grade = rng.choice(5, n_patients, p=[0.5, 0.1, 0.2, 0.1, 0.1])
    pref = np.clip(0.5 + 0.35 * np.where(grade >= 2, 1, -1) + rng.normal(0, 0.3, n_patients), 0.001, 0.999)
    one = pd.DataFrame({"patient_id": [f"p{i}" for i in range(n_patients)], "grade": grade.astype(float), "gradable": 1.0, "maculopathy": np.nan,
                        "pref": pref, "pst": pref * 0.5, "pmac": np.nan, "pgrad": 0.9, "u2": np.nan, "u3": np.nan, "u4": np.nan, "u5": np.nan,
                        "pref_der": pref, "pst_der": pref * 0.5, "run": "r"})
    for k in range(5):
        one[f"pg{k}"] = (grade == k) * 0.6 + 0.08
    for c in ("d_ref_dir", "d_ref_der"):
        one[c] = one["pref"] >= 0.5
    for c in ("d_st_dir", "d_st_der", "d_mac", "ab2", "ab3", "ab4", "ab5"):
        one[c] = False
    return pd.concat([one] * eyes, ignore_index=True)      # "eyes" identical copies per patient: perfectly correlated


def half_width(f, seed=0, B=400):
    point, boot, _, _ = analyze.analyze_dataset(KW, {"m": f}, B, seed, [])
    lo, hi = analyze._ci(boot["m"]["ref_sens"])
    return point["m"]["ref_sens"], (hi - lo) / 2, float((f.drop_duplicates("patient_id")["grade"] >= 2).sum())


def test_interval_width_matches_binomial_theory():
    rng = np.random.default_rng(5)
    f = frame(3000, 1, rng)
    sens, hw, n_pos = half_width(f)
    theory = 1.96 * np.sqrt(sens * (1 - sens) / n_pos)
    assert abs(hw - theory) / theory < 0.15


def test_clustering_does_not_shrink_intervals():
    rng = np.random.default_rng(6)
    one = frame(1500, 1, rng)
    two = pd.concat([one, one], ignore_index=True)            # every patient contributes two identical eyes
    s1, hw1, _ = half_width(one)
    s2, hw2, _ = half_width(two)
    assert s1 == s2
    assert abs(hw2 - hw1) / hw1 < 0.15                        # an image-level bootstrap would give hw1 / sqrt(2)
