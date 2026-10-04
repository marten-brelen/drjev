"""Stage 6: every protocol metric with patient-clustered bootstrap intervals, and the pre-specified tests.

Outputs (results/): metrics_long.csv, comparisons.csv, prompt_sensitivity.csv, deployment.csv"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import calibrate, frames, lock
from . import metrics as M
from .predict import load_preds
from .questions import n_variants
from .splits import load_manifest

NAN = float("nan")
RAW_METRICS = ("ece_grade", "brier_grade", "ece_ref", "aurc_grade")
SENS_METRICS = {"ref_sens_matched": ("ref", 2), "st_sens_matched": ("st", 3)}


def _has(x) -> bool:
    return not np.isnan(x).all()


def _primary(A, which: str, primary: str):
    """(score, decision, abstain flag) for referral ('ref') or sight-threatening ('st')."""
    direct = A["pref" if which == "ref" else "pst"]
    if primary == "direct" and _has(direct):
        return direct, A[f"d_{which}_dir"], A["ab4" if which == "ref" else "ab5"]
    return A[f"p{which}_der"], A[f"d_{which}_der"], A["ab2"]


def compute(A: dict, pid: np.ndarray, primary: str = "direct", bins: int = 15, sel_acc: float = 0.95) -> dict:
    """All metrics for one model on one set of images. A holds numpy arrays; pid is the patient code per row."""
    o = {}
    grade, gradable, mac, pg = A["grade"], A["gradable"], A["mac"], A["pg"]
    ev = ~np.isnan(grade) & (gradable != 0)              # gradeable images with a grade
    o["n"], o["n_gradable"] = float(len(grade)), float(ev.sum())
    g = grade[ev].astype(int)
    gh = pg[ev].argmax(1)
    correct = (gh == g).astype(float)
    # P1: five-class grading
    o["qwk"] = M.qwk(g, gh)
    o["acc"] = float(correct.mean()) if len(g) else NAN
    o["macro_f1"] = M.macro_f1(g, gh)
    for k in range(5):
        o[f"recall_{k}"] = float((gh[g == k] == k).mean()) if (g == k).any() else NAN
    # P2 / K3: referable and sight-threatening disease, grade-only truth
    not_gradeable = (A["pgrad"] < 0.5) if _has(A["pgrad"]) else np.zeros(len(grade), bool)
    for which, cut in (("ref", 2), ("st", 3)):
        y = grade[ev] >= cut
        s, d, ab = _primary(A, which, primary)
        o[f"{which}_auroc"] = M.auroc(y, s[ev])
        o[f"{which}_sens"], o[f"{which}_spec"] = M.sens_spec(y, d[ev])
        dp = A["pref" if which == "ref" else "pst"]
        o[f"{which}_auroc_direct"] = M.auroc(y, dp[ev]) if _has(dp) else NAN
        o[f"{which}_auroc_derived"] = M.auroc(y, A[f"p{which}_der"][ev])
        o[f"{which}_auroc_dir_minus_der"] = o[f"{which}_auroc_direct"] - o[f"{which}_auroc_derived"]
        o[f"{which}_sens_derived"], o[f"{which}_spec_derived"] = M.sens_spec(y, A[f"d_{which}_der"][ev])
        act = d | ab | not_gradeable                    # action rule: refer if disease, ungradeable or abstaining
        o[f"{which}_sens_action"], o[f"{which}_spec_action"] = M.sens_spec(y, act[ev])
        if which == "ref":
            o["referral_rate_action"] = float(act.mean())
            # K7: patient level, worse eye
            npat = int(pid.max()) + 1 if len(pid) else 0
            yp, pp, seen = np.zeros(npat), np.zeros(npat), np.zeros(npat, bool)
            np.maximum.at(yp, pid[ev], y.astype(float))
            np.maximum.at(pp, pid[ev], act[ev].astype(float))   # the same gradeable eyes on both sides
            seen[pid[ev]] = True
            o["patient_ref_sens"], o["patient_ref_spec"] = M.sens_spec(yp[seen] > 0, pp[seen] > 0)
    # K1, K2, K4: maculopathy and the full clinical definitions, where maculopathy is labelled
    mv = ~np.isnan(mac) & (gradable != 0)
    o["n_mac"] = float(mv.sum())
    if _has(A["pmac"]) and mv.any():
        o["mac_auroc"] = M.auroc(mac[mv] == 1, A["pmac"][mv])
        o["mac_sens"], o["mac_spec"] = M.sens_spec(mac[mv] == 1, A["d_mac"][mv])
    else:
        o["mac_auroc"] = o["mac_sens"] = o["mac_spec"] = NAN
    fv = ev & ~np.isnan(mac)
    for which, cut in (("ref", 2), ("st", 3)):
        if not fv.any():
            for k in ("auroc_direct", "auroc_derived", "sens_direct", "spec_direct", "sens_derived", "spec_derived"):
                o[f"{which}full_{k}"] = NAN
            continue
        y = (grade[fv] >= cut) | (mac[fv] == 1)
        dp = A["pref" if which == "ref" else "pst"]
        o[f"{which}full_auroc_direct"] = M.auroc(y, dp[fv]) if _has(dp) else NAN
        o[f"{which}full_sens_direct"], o[f"{which}full_spec_direct"] = M.sens_spec(y, A[f"d_{which}_dir"][fv]) if _has(dp) else (NAN, NAN)
        if _has(A["pmac"]):
            o[f"{which}full_auroc_derived"] = M.auroc(y, np.maximum(A[f"p{which}_der"], A["pmac"])[fv])
            o[f"{which}full_sens_derived"], o[f"{which}full_spec_derived"] = M.sens_spec(y, (A[f"d_{which}_der"] | A["d_mac"])[fv])
        else:
            o[f"{which}full_auroc_derived"] = o[f"{which}full_sens_derived"] = o[f"{which}full_spec_derived"] = NAN
    # P3: calibration
    top = pg[ev].max(1)
    o["ece_grade"] = M.ece(top, correct, bins)
    o["brier_grade"] = M.brier_multiclass(pg[ev], g)
    sref, _, _ = _primary(A, "ref", primary)
    rv = ev & ~np.isnan(sref)
    o["ece_ref"] = M.ece(sref[rv], (grade[rv] >= 2).astype(float), bins)
    o["brier_ref"] = M.brier_binary(sref[rv], grade[rv] >= 2)
    # P4: selective prediction (confidence = top probability x probability of answering)
    conf = top * (1 - np.nan_to_num(A["u2"][ev], nan=0.0))
    o["aurc_grade"] = M.aurc(conf, correct)
    for c in (50, 80, 90):
        o[f"err_cov{c}"] = M.risk_at_coverage(conf, correct, c / 100)
    o["auto_rate"] = M.coverage_at_accuracy(conf, correct, sel_acc)
    # P5: gradeability and abstention
    gl = np.where(np.isnan(gradable) & ~np.isnan(grade), 1.0, gradable)
    df = ~np.isnan(gl)
    un = gl[df] == 0
    o["n_ungradable"] = float(un.sum())
    if _has(A["pgrad"]):
        o["grad_auroc"] = M.auroc(un, 1 - A["pgrad"][df])
        o["grad_sens"], o["grad_spec"] = M.sens_spec(un, A["pgrad"][df] < 0.5)
    else:
        o["grad_auroc"] = o["grad_sens"] = o["grad_spec"] = NAN
    if _has(A["u2"]):
        o["abst_auroc"] = M.auroc(un, A["u2"][df])
        o["abst_rate_ungradable"] = float(A["ab2"][df][un].mean()) if un.any() else NAN
        o["refer_abst_rate_ungradable"] = float(A["ab4"][df][un].mean()) if un.any() and _has(A["u4"]) else NAN
        o["false_abst_rate"] = float(A["ab2"][ev].mean()) if ev.any() else NAN
    else:
        o["abst_auroc"] = o["abst_rate_ungradable"] = o["refer_abst_rate_ungradable"] = o["false_abst_rate"] = NAN
    # K5: coherence of the five answers
    if _has(A["pref"]) and _has(A["pst"]):
        gall = pg.argmax(1)
        m_hat = (A["pmac"] >= 0.5) if _has(A["pmac"]) else np.zeros(len(grade), bool)
        r_hat, s_hat = A["pref"] >= 0.5, A["pst"] >= 0.5
        any_ab = A["ab2"] | A["ab3"] | A["ab4"] | A["ab5"]
        ok = (r_hat == ((gall >= 2) | m_hat)) & (s_hat == ((gall >= 3) | m_hat)) & (~s_hat | r_hat)
        o["coherence"] = float(ok[~any_ab].mean()) if (~any_ab).any() else NAN
        all_ab = A["ab2"] & A["ab4"] & A["ab5"]
        o["abstain_consistency"] = float(all_ab[any_ab].mean()) if any_ab.any() else NAN
    else:
        o["coherence"] = o["abstain_consistency"] = NAN
    return o


def _seeds(A: dict):
    """The rows of each seed in a unit, one seed at a time."""
    for c in np.unique(A["run_code"]):
        yield _subset(A, A["run_code"] == c)


def _mean(values) -> float:
    v = [x for x in values if not np.isnan(x)]
    return float(np.mean(v)) if v else NAN


def matched_sens(Am: dict, Ar: dict, which: str, cut: int, primary: str) -> tuple[float, float]:
    """Sensitivity of the model and of the reference at one common specificity: the specificity the
    reference reaches at its own pre-fixed threshold. Both are read off their score at that
    specificity in the same way, so a model compared with itself differs by exactly zero.
    With several seeds, each seed is evaluated separately and the results are averaged."""
    def parts(A):
        ev = ~np.isnan(A["grade"]) & (A["gradable"] != 0)
        s, d, _ = _primary(A, which, primary)
        return A["grade"][ev] >= cut, s[ev], d[ev]

    spec0 = _mean(M.sens_spec(y, d)[1] for y, _, d in map(parts, _seeds(Ar)))
    at = lambda A: _mean(M.sens_at_spec(y, s, spec0) for y, s, _ in map(parts, _seeds(A)))
    return at(Am), at(Ar)


def compute_unit(A: dict, pid: np.ndarray, **kw) -> dict:
    """Metrics for a unit. A unit with several seeds is scored seed by seed and averaged, so pooling
    never makes a model look better (or worse) than its seeds are."""
    if A["run_code"].max(initial=0) == 0:
        return compute(A, pid, **kw)
    outs = [compute(_subset(A, A["run_code"] == c), pid[A["run_code"] == c], **kw) for c in np.unique(A["run_code"])]
    return {k: _mean(o[k] for o in outs) for k in outs[0]}


class Sampler:
    """Draws the same patient-level bootstrap sample for every model on a dataset."""

    def __init__(self, patient_ids: list[str]):
        self.codes = {p: i for i, p in enumerate(sorted(set(patient_ids)))}
        self.n = len(self.codes)

    def rows(self, f: pd.DataFrame) -> np.ndarray:
        """Matrix: one line per patient, holding that patient's row numbers in f, padded with -1."""
        code = f["patient_id"].map(self.codes).to_numpy()
        order = np.argsort(code, kind="stable")
        counts = np.bincount(code, minlength=self.n)
        R = np.full((self.n, max(1, counts.max())), -1)
        start = np.concatenate([[0], np.cumsum(counts)[:-1]])
        pos = np.arange(len(code)) - np.repeat(start, counts)
        R[code[order], pos] = order
        return R

    @staticmethod
    def take(R: np.ndarray, sample: np.ndarray):
        block = R[sample]
        mask = block >= 0
        inst = np.broadcast_to(np.arange(len(sample))[:, None], block.shape)[mask]
        return block[mask], inst


def _subset(A: dict, rows: np.ndarray) -> dict:
    return {k: v[rows] for k, v in A.items()}


def analyze_dataset(kw: dict, units: dict[str, pd.DataFrame], B: int, seed: int, pairs: list[tuple]) -> tuple[dict, dict, dict, dict]:
    """Point estimates and bootstrap replicates for every unit, plus paired quantities for `pairs`."""
    sampler = Sampler(pd.concat([f["patient_id"] for f in units.values()]).tolist())
    A = {u: frames.arrays(f) for u, f in units.items()}
    R = {u: sampler.rows(f) for u, f in units.items()}
    full = np.arange(sampler.n)
    point, boot = {}, {}
    cur = {}
    for u in units:
        rows, inst = Sampler.take(R[u], full)
        cur[u] = _subset(A[u], rows)
        point[u] = compute_unit(cur[u], inst, **kw)
        boot[u] = {k: np.full(B, np.nan) for k in point[u]}
    ppoint, pboot = {}, {}
    for (m, r, metric) in pairs:
        which, cut = SENS_METRICS[metric]
        ppoint[(m, r, metric)] = matched_sens(cur[m], cur[r], which, cut, kw["primary"])
        pboot[(m, r, metric)] = np.full((B, 2), np.nan)
    rng = np.random.default_rng(seed)
    for b in range(B):
        sample = rng.integers(0, sampler.n, sampler.n)
        cur = {}
        for u in units:
            rows, inst = Sampler.take(R[u], sample)
            cur[u] = _subset(A[u], rows)
            for k, v in compute_unit(cur[u], inst, **kw).items():
                boot[u][k][b] = v
        for (m, r, metric) in pairs:
            which, cut = SENS_METRICS[metric]
            pboot[(m, r, metric)][b] = matched_sens(cur[m], cur[r], which, cut, kw["primary"])
    return point, boot, ppoint, pboot


def _ci(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    x = x[~np.isnan(x)]
    if len(x) < 20:
        return NAN, NAN
    return float(np.quantile(x, alpha / 2)), float(np.quantile(x, 1 - alpha / 2))


def complete_frames(cfg, man, units: dict[str, list[str]], ds: str, split: str, problems: list, **kw) -> dict[str, pd.DataFrame]:
    """Frames for the units that predicted EVERY image of this test set with every seed.
    A model with missing images is left out and recorded: comparing models on different images is not a comparison."""
    expected = int(((man["dataset"] == ds) & (man["split"] == split)).sum())
    out = {}
    for u, runs in units.items():
        parts = [frames.build(cfg, man, r, ds, split, **kw) for r in runs]
        got = [0 if f is None else len(f) for f in parts]
        if all(g == expected for g in got):
            out[u] = pd.concat(parts, ignore_index=True)
        elif any(got):
            problems.append({"unit": u, "dataset": ds, "split": split, "expected_images": expected,
                             "predicted_images": "/".join(map(str, got)), "action": "left out of this dataset and of the pooled analysis"})
    return out


def run(cfg, bootstrap: int | None = None) -> None:
    lock.check(cfg)                                        # the analysis plan must be the one that was frozen
    an = cfg.analysis
    B = int(bootstrap or an["bootstrap"])
    alpha = float(an.get("alpha", 0.05))
    man = load_manifest(cfg)
    units = {u: [r for r in runs if (cfg.preds_dir / r).exists()] for u, runs in cfg.units().items()}
    units = {u: r for u, r in units.items() if r}
    if not units:
        raise SystemExit("No predictions found. Run `drjev predict` first.")
    for runs in units.values():                            # every run is calibrated before it is analysed
        for r in runs:
            if not (cfg.calib_dir / f"{r}.json").exists():
                calibrate.run_one(cfg, r)
    arm = {u: cfg.runs[r[0]].get("arm", "") for u, r in units.items()}
    synthetic = {u: bool(cfg.runs[r[0]].get("synthetic")) for u, r in units.items()}
    sets = [(ds, "test") for ds in sorted(man.loc[man["split"] == "test", "dataset"].unique())]
    sets += [(ds, "test_internal") for ds in sorted(man.loc[man["split"] == "test_internal", "dataset"].unique())]
    comps = an.get("comparisons", [])
    rows, crow, problems = [], [], []
    pooled = {u: [] for u in units}
    pool_sets = [ds for ds, split in sets if split == "test" and ds in an.get("pooled_external", [])]
    cfg.results.mkdir(parents=True, exist_ok=True)
    kw = dict(primary=an["primary_referral_answer"], bins=int(an["ece_bins"]), sel_acc=float(an["selective_accuracy"]))
    jobs = []

    def pairs_for(label, fr):
        return [(c["model"], c["reference"], c["metric"]) for c in comps
                if c["metric"] in SENS_METRICS and label in c["datasets"] and c["model"] in fr and c["reference"] in fr]

    def do(label: str, split: str, fr: dict[str, pd.DataFrame], result):
        point, boot, ppoint, pboot = result
        for u in fr:
            seeds = [compute(s_, np.arange(len(s_["grade"])), **kw) for s_ in _seeds(frames.arrays(fr[u]))] if len(units[u]) > 1 else []
            for met, val in point[u].items():
                lo, hi = _ci(boot[u][met], alpha)
                sv = [s_[met] for s_ in seeds if met not in ("patient_ref_sens", "patient_ref_spec")]
                rows.append({"unit": u, "arm": arm[u], "dataset": label, "split": split, "metric": met, "value": val,
                             "ci_low": lo, "ci_high": hi, "calibrated": True, "n_seeds": len(units[u]),
                             "seed_sd": float(np.nanstd(sv, ddof=1)) if len(sv) > 1 and not np.isnan(sv).all() else NAN,
                             "synthetic": synthetic[u]})
        for c in comps:
            if label not in c["datasets"]:
                continue
            m, r, met = c["model"], c["reference"], c["metric"]
            base = {"id": c["id"], "test": c["test"], "metric": met, "model": m, "reference": r, "dataset": label,
                    "margin": c.get("margin", NAN), "primary": bool(c.get("primary")), "synthetic": synthetic.get(m, False) or synthetic.get(r, False)}
            if m not in fr or r not in fr:
                crow.append(dict(base, status="not run: no complete predictions for " + ", ".join(x for x in (m, r) if x not in fr)))
                continue
            if met in SENS_METRICS:
                pm, pr = ppoint[(m, r, met)]
                d = pboot[(m, r, met)]
                bm, br = d[:, 0], d[:, 1]
            else:
                pm, pr, bm, br = point[m][met], point[r][met], boot[m][met], boot[r][met]
            sign = -1.0 if c.get("lower_is_better") else 1.0
            adv = sign * (bm - br)                         # positive = the model is better
            adv = adv[~np.isnan(adv)]
            lo, hi = _ci(adv, alpha)
            limit = -float(c["margin"]) if c["test"] == "noninferiority" else 0.0
            p = float((np.sum(adv <= limit) + 1) / (len(adv) + 1)) if len(adv) >= 20 else NAN
            crow.append(dict(base, model_value=pm, reference_value=pr, advantage=sign * (pm - pr), ci_low=lo, ci_high=hi,
                             p_value=p, status="ok" if not np.isnan(p) else "not run: metric undefined on this dataset"))

    k = 0
    for ds, split in sets:
        fr = complete_frames(cfg, man, units, ds, split, problems)
        if not fr:
            continue
        k += 1
        print(f"analyze: {ds}/{split}: {len(fr)} models, {B} bootstrap samples")
        jobs.append((ds, split, fr, cfg.seed + k))
        if ds in pool_sets and split == "test":
            for u, f in fr.items():
                pooled[u].append(f)
        raw_fr = complete_frames(cfg, man, units, ds, split, [], calibrated=False)   # uncalibrated point estimates
        for u, f in raw_fr.items():
            raw = compute_unit(frames.arrays(f), pd.factorize(f["patient_id"])[0], **kw)
            for met in RAW_METRICS:
                rows.append({"unit": u, "arm": arm[u], "dataset": ds, "split": split, "metric": met, "value": raw[met], "ci_low": NAN,
                             "ci_high": NAN, "calibrated": False, "n_seeds": len(units[u]), "seed_sd": NAN, "synthetic": synthetic[u]})
    fr = {u: pd.concat(v, ignore_index=True) for u, v in pooled.items() if len(v) == len(pool_sets) and v}   # only models complete on every pooled set
    if fr:
        print(f"analyze: pooled_external ({', '.join(pool_sets)}): {len(fr)} models")
        jobs.append(("pooled_external", "test", fr, cfg.seed + k + 1))
    workers = max(1, min(int(cfg.machine["workers"]["analysis"]), len(jobs)))
    if workers > 1:                                        # one dataset per process
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(workers) as ex:
            futs = [ex.submit(analyze_dataset, kw, f, B, sd, pairs_for(lab, f)) for lab, _, f, sd in jobs]
            results = [x.result() for x in futs]
    else:
        results = [analyze_dataset(kw, f, B, sd, pairs_for(lab, f)) for lab, _, f, sd in jobs]
    for (lab, split, f, _), res_ in zip(jobs, results):
        do(lab, split, f, res_)
    done = {(c["id"], c["dataset"]) for c in crow}
    for c in comps:                                        # a pre-specified test on a dataset with no data at all still counts
        for ds in c["datasets"]:
            if (c["id"], ds) not in done:
                crow.append({"id": c["id"], "test": c["test"], "metric": c["metric"], "model": c["model"], "reference": c["reference"], "dataset": ds,
                             "margin": c.get("margin", NAN), "primary": bool(c.get("primary")), "synthetic": False, "status": "not run: no predictions on this dataset"})

    res = pd.DataFrame(rows)
    res.to_csv(cfg.results / "metrics_long.csv", index=False)
    pd.DataFrame(problems, columns=["unit", "dataset", "split", "expected_images", "predicted_images", "action"]).to_csv(cfg.results / "incomplete.csv", index=False)
    for pr_ in problems:
        print(f"analyze: WARNING {pr_['unit']} predicted {pr_['predicted_images']} of {pr_['expected_images']} images on {pr_['dataset']}: {pr_['action']}")
    cdf = pd.DataFrame(crow)
    if len(cdf):
        for col in ("p_value", "model_value", "reference_value", "advantage", "ci_low", "ci_high"):
            if col not in cdf:
                cdf[col] = NAN
        # Holm over the WHOLE pre-specified primary family: a test that could not be run counts as p = 1.
        prim = cdf["primary"]
        cdf["p_holm"] = NAN
        if prim.any():
            cdf.loc[prim, "p_holm"] = M.holm(cdf.loc[prim, "p_value"].fillna(1.0).tolist())
        # One-sided tests at alpha/2, which matches the lower limit of the two-sided 95% interval.
        decide = np.where(prim, cdf["p_holm"], cdf["p_value"])
        cdf["passed"] = np.where(cdf["status"] == "ok", decide < alpha / 2, None)
        cdf["decided_on"] = np.where(prim, "Holm-adjusted p", "unadjusted p")
    cdf.to_csv(cfg.results / "comparisons.csv", index=False)

    # ---- prompt sensitivity: the same images under each wording ----
    ps = []
    nv = n_variants(cfg.questions_file)
    for u, runs in units.items():
        for ds, split in sets:
            vals = {}
            for v in range(nv):
                f = frames.unit_frame(cfg, man, runs, ds, split, variant=v, subset="para_subset")
                if f is not None:
                    vals[v] = compute_unit(frames.arrays(f), pd.factorize(f["patient_id"])[0], **kw)
            if len(vals) > 1:
                for met in ("qwk", "ref_auroc", "ece_grade"):
                    x = [vals[v][met] for v in sorted(vals)]
                    ps.append({"unit": u, "arm": arm[u], "dataset": ds, "metric": met, "n_wordings": len(x), "mean": float(np.nanmean(x)),
                               "min": float(np.nanmin(x)), "max": float(np.nanmax(x)), "range": float(np.nanmax(x) - np.nanmin(x)),
                               **{f"v{v}": vals[v][met] for v in sorted(vals)}, "synthetic": synthetic[u]})
    pd.DataFrame(ps).to_csv(cfg.results / "prompt_sensitivity.csv", index=False)

    # ---- deployment: latency per decision, as measured during prediction ----
    dep = []
    for u, runs in units.items():
        ms = []
        for r in runs:
            for ds, split in sets:
                p = load_preds(cfg, r, ds, split, 0)
                if p is not None:
                    ms.append(p["ms"].to_numpy(float))
        if ms:
            ms = np.concatenate(ms)
            spec = cfg.runs[runs[0]]
            dep.append({"unit": u, "arm": arm[u], "adapter": spec.get("adapter"), "hf_repo": spec.get("hf_repo", ""), "revision": spec.get("revision") or "",
                        "decisions": len(ms), "ms_p50": float(np.median(ms)), "ms_p95": float(np.quantile(ms, 0.95)), "synthetic": synthetic[u]})
    pd.DataFrame(dep).to_csv(cfg.results / "deployment.csv", index=False)
    cal = {r: calibrate.load(cfg, r) for runs in units.values() for r in runs}
    (cfg.results / "calibration.json").write_text(json.dumps(cal, indent=2) + "\n")
    (cfg.results / "analysis_settings.json").write_text(json.dumps({"bootstrap_samples": B, "alpha": alpha}, indent=2) + "\n")
    print(f"analyze: {len(res)} metric rows, {len(cdf)} comparisons -> {cfg.results}")
