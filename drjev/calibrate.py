"""Stage 5: temperature scaling and operating thresholds, fitted on calibration splits only.

One temperature per run and question (protocol 6.6). Thresholds for referral, sight-threatening
disease and maculopathy are the largest values that reach the target sensitivity on the calibration
split. Nothing here reads a test split."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from . import metrics as M
from .predict import load_preds
from .splits import load_manifest
from .targets import QIDS, UNKNOWN, target

CAL_SPLIT = {"q1_gradeable": "calibration", "q2_grade": "calibration", "q3_maculopathy": "q3_cal",
             "q4_refer": "calibration", "q5_sight": "calibration"}
EPS = 1e-12
MIN_CAL = 100   # fewer labelled calibration images than this: no temperature is fitted


def full_matrix(p: np.ndarray, u: np.ndarray | None) -> np.ndarray:
    """Options (and 'unknown' as a last column when the model reports it) as one distribution."""
    if u is None:
        return p
    return np.column_stack([p * (1 - u[:, None]), u])


def apply_temperature(p: np.ndarray, u: np.ndarray | None, t: float):
    """Returns (p, u) after dividing log-probabilities by t. t = 1 leaves them unchanged."""
    if t == 1.0:
        return p, u
    z = np.log(np.clip(full_matrix(p, u), EPS, 1)) / t
    z = np.exp(z - z.max(1, keepdims=True))
    z /= z.sum(1, keepdims=True)
    if u is None:
        return z, None
    un = z[:, -1]
    rest = z[:, :-1]
    s = rest.sum(1, keepdims=True)
    return np.where(s > 0, rest / np.where(s > 0, s, 1), 1.0 / rest.shape[1]), un


def fit_temperature(full: np.ndarray, y: np.ndarray) -> float:
    """Temperature that minimises negative log-likelihood of the true column."""
    logp = np.log(np.clip(full, EPS, 1))

    def nll(log_t):
        z = logp / np.exp(log_t)
        z = z - z.max(1, keepdims=True)
        lse = np.log(np.exp(z).sum(1))
        return -(z[np.arange(len(y)), y] - lse).mean()

    res = minimize_scalar(nll, bounds=(-3, 3), method="bounded")
    return float(np.exp(res.x))


def question_arrays(preds: pd.DataFrame, qid: str, ids: list[str]):
    """(p matrix, u vector or None) for one question, rows in the order of ids. Missing rows are nan."""
    d = preds[preds["q"] == qid].set_index("image_id").reindex(ids)
    have = d["p"].notna().to_numpy()
    if not have.any():
        return None, None, have
    k = len(d["p"][have].iloc[0])
    p = np.full((len(ids), k), np.nan)
    p[have] = np.array(d["p"][have].tolist(), float)
    uu = pd.to_numeric(d["u"], errors="coerce").to_numpy(float)
    u = uu if np.isfinite(uu[have]).all() else None
    return p, u, have


def _truth(man: pd.DataFrame, qid: str, with_unknown: bool, k: int):
    """Column index of the truth per manifest row; -1 where there is no usable label."""
    out = np.full(len(man), -1)
    for i, r in enumerate(man.itertuples()):
        t = target(qid, r.grade, r.gradable, r.maculopathy)
        if t == UNKNOWN:
            out[i] = k if with_unknown else -1
        elif t is not None:
            out[i] = t
    return out


def run_one(cfg, run_name: str) -> dict:
    man = load_manifest(cfg)
    target_sens = float(cfg.analysis["target_sensitivity"])
    out = {"run": run_name, "temperature": {}, "thresholds": {}, "n": {}, "notes": []}
    cal = {}
    for qid in QIDS:
        split = CAL_SPLIT[qid]
        sub = man[man["split"] == split]
        frames = [load_preds(cfg, run_name, ds, split, 0) for ds in sub["dataset"].unique()]
        frames = [f for f in frames if f is not None]
        if not frames:
            out["temperature"][qid] = 1.0
            out["notes"].append(f"{qid}: no predictions on the '{split}' split; temperature left at 1")
            continue
        preds = pd.concat(frames)
        sub = sub[sub["image_id"].isin(set(preds["image_id"]))].reset_index(drop=True)
        p, u, have = question_arrays(preds, qid, sub["image_id"].tolist())
        if p is None:
            out["temperature"][qid] = 1.0
            continue
        y = _truth(sub, qid, u is not None, p.shape[1])
        ok = have & (y >= 0)
        if ok.sum() < MIN_CAL:
            out["temperature"][qid] = 1.0
            out["notes"].append(f"{qid}: only {int(ok.sum())} labelled calibration images (fewer than {MIN_CAL}); temperature left at 1")
        else:
            t = fit_temperature(full_matrix(p[ok], None if u is None else u[ok]), y[ok])
            out["temperature"][qid] = t
            if t < 0.06 or t > 19:
                out["notes"].append(f"{qid}: fitted temperature {t:.2f} is at the edge of the search range; check the calibration data")
        out["n"][qid] = int(ok.sum())
        pc, uc = apply_temperature(p, u, out["temperature"][qid])
        cal[qid] = (sub, pc, have)

    def thr(name, qid, score_fn, truth_fn):
        if qid not in cal:
            out["thresholds"][name] = 0.5
            out["notes"].append(f"{name}: no calibration predictions; threshold left at 0.5")
            return
        sub, pc, have = cal[qid]
        yy = truth_fn(sub)
        ok = have & yy.notna().to_numpy() & (sub["gradable"] != 0).to_numpy()
        if ok.sum() == 0 or yy[ok].sum() == 0:
            out["thresholds"][name] = 0.5
            out["notes"].append(f"{name}: no positive calibration cases; threshold left at 0.5")
            return
        out["thresholds"][name] = M.threshold_for_sensitivity(yy[ok].to_numpy(bool), score_fn(pc)[ok], target_sens)

    grade_ge = lambda k: (lambda s: (s["grade"] >= k).where(s["grade"].notna()))
    thr("ref_direct", "q4_refer", lambda p: p[:, 1], grade_ge(2))
    thr("st_direct", "q5_sight", lambda p: p[:, 1], grade_ge(3))
    thr("ref_derived", "q2_grade", lambda p: p[:, 2:].sum(1), grade_ge(2))
    thr("st_derived", "q2_grade", lambda p: p[:, 3:].sum(1), grade_ge(3))
    thr("mac", "q3_maculopathy", lambda p: p[:, 1], lambda s: s["maculopathy"])
    cfg.calib_dir.mkdir(parents=True, exist_ok=True)
    (cfg.calib_dir / f"{run_name}.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


def load(cfg, run_name: str) -> dict:
    f = cfg.calib_dir / f"{run_name}.json"
    if f.exists():
        return json.loads(f.read_text())
    return {"run": run_name, "temperature": {}, "thresholds": {}, "notes": ["not calibrated"]}


def run(cfg, runs=None):
    if cfg.lock_file.exists():                              # after the lock, the target sensitivity and splits must be the frozen ones
        from . import lock
        lock.check(cfg)
    for r in runs or [n for n in cfg.runs if (cfg.preds_dir / n).exists()]:
        o = run_one(cfg, r)
        t = ", ".join(f"{k.split('_')[0]}={v:.2f}" for k, v in o["temperature"].items())
        print(f"calibrate [{r}] temperatures: {t}")
