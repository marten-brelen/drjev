"""Stage 3: patient-level splits, de-duplication across datasets, and fixed subsets.

split values
  train, dev                  EyePACS Kaggle-train patients
  calibration, test_internal  EyePACS Kaggle-test patients (sampled); the rest is `reserve`
  test                        external datasets (official test part where one exists)
  q3_train, q3_dev, q3_cal    the dataset used to train the maculopathy question
  unused                      everything else
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PRIORITY = ["test", "test_internal", "calibration", "q3_cal", "dev", "q3_dev", "q3_train", "train", "reserve", "unused"]


def _patient_table(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby("patient_id")
    return pd.DataFrame({"n": g.size(), "stratum": g["grade"].max().fillna(-1).astype(int)})


def _take_patients(pt: pd.DataFrame, fractions: dict[str, float], rng) -> dict[str, str]:
    """Assign patients to named parts by fraction, stratified by the patient's worst grade.
    Whatever is left over goes to the part named 'rest'."""
    out = {}
    for _, grp in pt.groupby("stratum"):
        ids = grp.index.to_numpy().copy()
        rng.shuffle(ids)
        start = 0
        for part, frac in fractions.items():
            k = int(round(frac * len(ids)))
            for pid in ids[start: start + k]:
                out[pid] = part
            start += k
        for pid in ids[start:]:
            out[pid] = "rest"
    return out


def _stratified_order(d: pd.DataFrame, rng) -> np.ndarray:
    """A fixed ordering of rows such that every prefix is (nearly) stratified by grade.
    Used for nested subsets: the 1,000-image subset is a prefix of the 5,000-image one."""
    key = d["grade"].fillna(-1).astype(int).to_numpy()
    pos = np.empty(len(d))
    for s in np.unique(key):
        idx = np.where(key == s)[0]
        rng.shuffle(idx)
        pos[idx] = (np.arange(len(idx)) + rng.random()) / len(idx)
    return np.argsort(pos, kind="stable")


def duplicate_groups(hashes: list[str], thumbs: list[str], max_bits: int = 7, max_mad: float = 4.0) -> list[list[int]]:
    """Groups of row positions that hold the same photograph, including re-encoded copies.

    Candidates share one of eight interleaved bands of the difference hash, which is guaranteed to
    happen for any pair differing in at most seven bits; a pair is
    confirmed when the hashes differ in at most max_bits bits and the grey thumbnails differ by at
    most max_mad grey levels on average, and by little relative to the contrast in the image (so that
    two different near-black, ungradeable photographs are not mistaken for copies)."""
    H = np.array([np.unpackbits(np.frombuffer(bytes.fromhex(h), dtype=np.uint8)) for h in hashes])
    T = np.array([np.frombuffer(bytes.fromhex(t), dtype=np.uint8) for t in thumbs], dtype=np.float32)
    S = T.std(axis=1)
    parent = list(range(len(hashes)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = set()
    for band in range(8):
        keys: dict[bytes, list[int]] = {}
        for i, row in enumerate(np.packbits(H[:, band::8], axis=1)):
            keys.setdefault(row.tobytes(), []).append(i)
        for idx in keys.values():
            if len(idx) < 2 or len(idx) > 2000:        # a band shared by thousands carries no information
                continue
            for a_pos, a in enumerate(idx):
                for b in idx[a_pos + 1:]:
                    if (a, b) in seen:
                        continue
                    seen.add((a, b))
                    mad = np.abs(T[a] - T[b]).mean()
                    if (H[a] != H[b]).sum() <= max_bits and mad <= max_mad and mad <= 0.08 * min(S[a], S[b]):
                        parent[find(b)] = find(a)
    out: dict[int, list[int]] = {}
    for i in range(len(hashes)):
        out.setdefault(find(i), []).append(i)
    return [g for g in out.values() if len(g) > 1]


def run(cfg) -> pd.DataFrame:
    m = pd.read_csv(cfg.manifest_proc, dtype={"grade_raw": str, "eye": str})
    sp = cfg.splits
    rng = np.random.default_rng(cfg.seed)
    m["split"] = "unused"
    for name, spec in cfg.datasets.items():
        role = spec.get("role", "off")
        sel = m["dataset"] == name
        if not sel.any():
            continue
        if role == "internal":
            tr = sel & (m["official_split"] == "kaggle_train")
            te = sel & (m["official_split"] == "kaggle_test")
            a = _take_patients(_patient_table(m[tr]), {"dev": sp["eyepacs_dev_fraction"]}, rng)
            m.loc[tr, "split"] = m.loc[tr, "patient_id"].map(a).replace({"rest": "train"})
            n_te = int(te.sum())
            if n_te:
                fc = min(1.0, sp["eyepacs_calibration_images"] / n_te)
                ft = min(1.0 - fc, sp["eyepacs_internal_test_images"] / n_te)
                a = _take_patients(_patient_table(m[te]), {"calibration": fc, "test_internal": ft}, rng)
                m.loc[te, "split"] = m.loc[te, "patient_id"].map(a).replace({"rest": "reserve"})
        elif role == "external":
            parts = spec.get("test_parts")
            m.loc[sel & (m["official_split"].isin(parts) if parts else True), "split"] = "test"
        elif role == "q3_train":
            f = sp["q3_fractions"]
            a = _take_patients(_patient_table(m[sel]), {"q3_dev": f["dev"], "q3_cal": f["calibration"]}, rng)
            m.loc[sel, "split"] = m.loc[sel, "patient_id"].map(a).replace({"rest": "q3_train"})

    # ---- duplicates: the copy in the highest-priority split is kept, the others are excluded ----
    m["excluded"] = ""
    m["dup_of"] = ""
    rank = {s: i for i, s in enumerate(PRIORITY)}
    groups = duplicate_groups(m["dhash"].tolist(), m["thumb"].tolist())
    conflicts = 0
    for idx in groups:
        grp = m.iloc[idx].assign(_rank=lambda d: d["split"].map(rank)).sort_values(["_rank", "image_id"])
        m.loc[grp.index[1:], "excluded"] = "duplicate"
        m.loc[grp.index[1:], "dup_of"] = grp.iloc[0]["image_id"]
        conflicts += int(grp["grade"].dropna().nunique() > 1)
    n_dup = int((m["excluded"] == "duplicate").sum())
    m = m.drop(columns=["thumb"])
    m[m["excluded"] == "duplicate"][["image_id", "dataset", "split", "grade", "dup_of"]].to_csv(cfg.work / "duplicates.csv", index=False)

    # ---- fixed subsets ----
    ok = m["excluded"] == ""
    train = m[ok & (m["split"] == "train")]
    order = train.index.to_numpy()[_stratified_order(train, rng)]
    for n in sorted(sp.get("efficiency_subsets", [])):
        m[f"eff_{n}"] = False
        m.loc[order[:n], f"eff_{n}"] = True
    m["para_subset"] = False
    m["recal_subset"] = False
    for (ds, split), grp in m[ok & m["split"].isin(["test", "test_internal", "calibration"])].groupby(["dataset", "split"]):
        o = grp.index.to_numpy()[_stratified_order(grp, rng)]
        m.loc[o[: int(sp["paraphrase_subset"])], "para_subset"] = True
        if split == "test":
            m.loc[rng.permutation(grp.index.to_numpy())[: int(sp["local_recalibration"])], "recal_subset"] = True

    m.to_csv(cfg.manifest, index=False)
    # ---- Table 0: dataset flow ----
    t = m.copy()
    t["label"] = np.where(t["gradable"] == 0, "ungradeable", t["grade"].map(lambda g: "no grade" if pd.isna(g) else f"grade {int(g)}"))
    flow = (t[t["excluded"] == ""].groupby(["dataset", "split", "label"]).size().unstack(fill_value=0))
    flow["total"] = flow.sum(axis=1)
    flow["patients"] = t[t["excluded"] == ""].groupby(["dataset", "split"])["patient_id"].nunique()
    flow["maculopathy labelled"] = t[t["excluded"] == ""].groupby(["dataset", "split"])["maculopathy"].count()
    flow["maculopathy present"] = t[t["excluded"] == ""].groupby(["dataset", "split"])["maculopathy"].sum().astype(int)
    flow.to_csv(cfg.work / "split_summary.csv")
    print(f"split: {len(m)} images; {n_dup} duplicates excluded ({conflicts} duplicate groups with conflicting grades)")
    print(flow.to_string())
    return m


def load_manifest(cfg, include_excluded: bool = False) -> pd.DataFrame:
    m = pd.read_csv(cfg.manifest, dtype={"grade_raw": str, "eye": str, "excluded": str, "dup_of": str}, keep_default_na=True)
    m["excluded"] = m["excluded"].fillna("")
    return m if include_excluded else m[m["excluded"] == ""].reset_index(drop=True)
