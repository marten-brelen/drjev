"""Turn stored predictions into one row per image, with calibrated probabilities and point decisions."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import calibrate
from .predict import load_preds

QS = {"q1_gradeable": "1", "q2_grade": "2", "q3_maculopathy": "3", "q4_refer": "4", "q5_sight": "5"}


def build(cfg, man: pd.DataFrame, run_name: str, dataset: str, split: str, variant: int = 0,
          calibrated: bool = True, subset: str | None = None) -> pd.DataFrame | None:
    preds = load_preds(cfg, run_name, dataset, split, variant)
    if preds is None:
        return None
    sub = man[(man["dataset"] == dataset) & (man["split"] == split)]
    if subset:
        sub = sub[sub[subset]]
    sub = sub[sub["image_id"].isin(set(preds["image_id"]))].reset_index(drop=True)
    if sub.empty:
        return None
    ids = sub["image_id"].tolist()
    cal = calibrate.load(cfg, run_name)
    temp = cal.get("temperature", {}) if calibrated else {}
    thr = cal.get("thresholds", {})
    f = sub[["image_id", "dataset", "patient_id", "grade", "gradable", "maculopathy"]].copy()
    f["run"] = run_name
    n = len(f)
    nan = np.full(n, np.nan)
    arr = {}
    for qid, tag in QS.items():
        p, u, have = calibrate.question_arrays(preds, qid, ids)
        if p is None:
            arr[tag] = (None, None)
            continue
        ok = have
        pc, uc = calibrate.apply_temperature(p[ok], None if u is None else u[ok], float(temp.get(qid, 1.0)))
        pf = np.full(p.shape, np.nan)
        pf[ok] = pc
        uf = nan.copy()
        if uc is not None:
            uf[ok] = uc
        arr[tag] = (pf, uf)
    p2, u2 = arr["2"]
    if p2 is None:
        return None
    for k in range(5):
        f[f"pg{k}"] = p2[:, k]
    f["u2"] = u2
    f["pgrad"] = arr["1"][0][:, 1] if arr["1"][0] is not None else nan
    for tag, col in (("3", "pmac"), ("4", "pref"), ("5", "pst")):
        p, u = arr[tag]
        f[col] = p[:, 1] if p is not None else nan
        f[f"u{tag}"] = u if u is not None else nan
    f["pref_der"] = p2[:, 2:].sum(1)
    f["pst_der"] = p2[:, 3:].sum(1)
    f["d_ref_dir"] = f["pref"] >= thr.get("ref_direct", 0.5)
    f["d_st_dir"] = f["pst"] >= thr.get("st_direct", 0.5)
    f["d_ref_der"] = f["pref_der"] >= thr.get("ref_derived", 0.5)
    f["d_st_der"] = f["pst_der"] >= thr.get("st_derived", 0.5)
    f["d_mac"] = f["pmac"] >= thr.get("mac", 0.5)

    def abst(u, top):  # "unknown" is the single most likely outcome
        u = np.nan_to_num(np.asarray(u, float), nan=0.0)
        return u > (1 - u) * np.nan_to_num(np.asarray(top, float), nan=1.0)

    f["ab2"] = abst(f["u2"], p2.max(1))
    f["ab3"] = abst(f["u3"], np.maximum(f["pmac"], 1 - f["pmac"]))
    f["ab4"] = abst(f["u4"], np.maximum(f["pref"], 1 - f["pref"]))
    f["ab5"] = abst(f["u5"], np.maximum(f["pst"], 1 - f["pst"]))
    f["ms"] = preds.groupby("image_id")["ms"].mean().reindex(ids).to_numpy()
    return f[f["pg0"].notna()].reset_index(drop=True)


def unit_frame(cfg, man, runs: list[str], dataset: str, split: str, **kw) -> pd.DataFrame | None:
    """A unit is one run, or several seeds of the same arm pooled row-wise."""
    fr = [build(cfg, man, r, dataset, split, **kw) for r in runs]
    fr = [x for x in fr if x is not None]
    return pd.concat(fr, ignore_index=True) if fr else None


def arrays(f: pd.DataFrame) -> dict:
    """Numpy view of a frame, for fast resampling."""
    a = {"grade": f["grade"].to_numpy(float), "gradable": f["gradable"].to_numpy(float), "mac": f["maculopathy"].to_numpy(float),
         "pg": f[[f"pg{k}" for k in range(5)]].to_numpy(float)}
    for c in ("u2", "u3", "u4", "u5", "pgrad", "pmac", "pref", "pst", "pref_der", "pst_der"):
        a[c] = f[c].to_numpy(float)
    for c in ("d_ref_dir", "d_st_dir", "d_ref_der", "d_st_der", "d_mac", "ab2", "ab3", "ab4", "ab5"):
        a[c] = f[c].to_numpy(bool)
    a["run_code"] = pd.factorize(f["run"])[0]            # which seed each row came from
    return a
