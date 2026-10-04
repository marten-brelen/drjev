"""Stage 1: read each dataset's label files and build one manifest.

Output columns: image_id, dataset, raw_path, patient_id, eye, grade (0-4 or empty),
gradable (1, 0 or empty = not labelled), maculopathy (1, 0 or empty), official_split, grade_raw.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}


def norm(v) -> str:
    """Normalise a label value for comparison: 1, 1.0, '1 ' and 'Yes' become '1', '1', '1', 'yes'."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return str(int(v)) if float(v).is_integer() else str(v)
    return str(v).strip().lower()


def index_images(folder: Path) -> dict[str, Path]:
    """Lower-cased file stem -> path, for every image under folder."""
    out = {}
    if folder.is_dir():
        for p in folder.rglob("*"):
            if p.suffix.lower() in IMAGE_EXT:
                out.setdefault(p.stem.lower(), p)
    return out


def _stem(image_id: str) -> str:
    s = str(image_id).strip()
    return s[: s.rfind(".")] if Path(s).suffix.lower() in IMAGE_EXT else s


def _read(path: Path, spec: dict) -> pd.DataFrame:
    rd = spec.get("read", {})
    kw = {"sep": rd.get("sep", ",")}
    if rd.get("header", True) is False:
        kw.update(header=None, names=rd["names"])
    df = pd.read_csv(path, **kw)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def ingest_dataset(name: str, spec: dict, raw_root: Path):
    """Returns (rows DataFrame or None, list of report lines)."""
    root = raw_root / spec["root"]
    rep = [f"## {name}", ""]
    if not root.is_dir():
        rep.append(f"- **Not found**: `{root}`. Dataset skipped.")
        return None, rep
    frames = []
    for part in spec["parts"]:
        lab = root / part["labels"]
        if not lab.exists():
            rep.append(f"- Label file missing: `{lab}` (part `{part['official_split']}` skipped)")
            continue
        df = _read(lab, spec)
        for col in (spec["id_column"], spec["grade_column"]):
            if col not in df.columns:
                raise ValueError(f"{name}: column '{col}' not in {lab.name}; columns are {list(df.columns)}")
        files = index_images(root / part["images"])
        stems = df[spec["id_column"]].map(_stem)
        out = pd.DataFrame({"stem": stems})
        out["raw_path"] = [str(files.get(s.lower(), "")) for s in stems]
        graw = df[spec["grade_column"]]
        out["grade_raw"] = graw.map(norm)
        grade = pd.to_numeric(graw, errors="coerce")
        gradable = pd.Series(np.nan, index=df.index)
        ungr = {norm(v) for v in spec.get("ungradable_grades", [])}
        if ungr:
            is_un = out["grade_raw"].isin(ungr)
            gradable = gradable.where(~is_un, 0.0).where(is_un, 1.0)
            grade = grade.where(~is_un)
        if spec.get("gradable_column"):
            ok = {norm(v) for v in spec.get("gradable_true_values", [1])}
            g = df[spec["gradable_column"]].map(norm)
            gradable = g.isin(ok).astype(float)
        if spec.get("missing_grade_is_ungradable"):
            gradable = gradable.where(grade.notna(), 0.0)
        grade = grade.where(gradable != 0)           # an ungradeable image has no grade to predict
        bad = grade.notna() & ~grade.isin([0, 1, 2, 3, 4])
        if bad.any():
            raise ValueError(f"{name}: grades outside 0-4 in {lab.name}: {sorted(set(grade[bad]))[:5]}")
        out["grade"] = grade
        out["gradable"] = gradable
        if spec.get("maculopathy_column"):
            pos = {norm(v) for v in spec.get("maculopathy_positive", [1])}
            m = df[spec["maculopathy_column"]].map(norm)
            mac = m.isin(pos).astype(float).where(m != "")
            out["maculopathy"] = mac.where(gradable != 0)
        else:
            out["maculopathy"] = np.nan
        if spec.get("patient_column"):
            out["patient"] = df[spec["patient_column"]].map(norm)
        elif spec.get("patient_regex"):
            rx = re.compile(spec["patient_regex"])
            out["patient"] = [m.group(1) if (m := rx.search(s)) else s for s in stems]
        else:
            out["patient"] = stems
        if spec.get("eye_regex"):
            rx = re.compile(spec["eye_regex"])
            out["eye"] = [m.group(1) if (m := rx.search(s)) else "" for s in stems]
        else:
            out["eye"] = ""
        out["official_split"] = part["official_split"]
        n_missing = int((out["raw_path"] == "").sum())
        exp = (spec.get("expected_images") or {}).get(part["official_split"])
        line = f"- `{part['official_split']}`: {len(out)} label rows, {len(out) - n_missing} images found"
        if n_missing:
            line += f", **{n_missing} image files missing**"
        if exp is not None:
            line += f" (expected {exp}{'' if exp == len(out) else ': MISMATCH'})"
        rep.append(line)
        frames.append(out[out["raw_path"] != ""])
    if not frames:
        return None, rep
    d = pd.concat(frames, ignore_index=True)
    dup = d["stem"].duplicated()
    if dup.any():
        rep.append(f"- {int(dup.sum())} repeated image ids dropped (first kept)")
        d = d[~dup]
    for ov in spec.get("quality_overlays", []):
        f = root / ov["file"]
        if not f.exists():
            if not ov.get("optional"):
                rep.append(f"- Quality file missing: `{f}`")
            continue
        q = pd.read_csv(f)
        q.columns = [str(c).strip() for c in q.columns]
        qmap = dict(zip(q[ov["id_column"]].map(_stem), q[ov["quality_column"]].map(norm)))
        bad = {norm(v) for v in ov["ungradable_values"]}
        qv = d["stem"].map(qmap)
        has = qv.notna()
        d.loc[has, "gradable"] = (~qv[has].isin(bad)).astype(float)
        d.loc[has & qv.isin(bad), ["grade", "maculopathy"]] = np.nan
        rep.append(f"- Quality labels from `{ov['file']}`: {int(has.sum())} images, {int((has & qv.isin(bad)).sum())} ungradeable")
    d.insert(0, "image_id", name + ":" + d["stem"])
    d.insert(1, "dataset", name)
    d["patient_id"] = name + ":" + d["patient"].astype(str)
    cnt = d["grade"].value_counts(dropna=False).sort_index()
    rep.append("- Grades: " + ", ".join(f"{'none' if pd.isna(k) else int(k)}: {v}" for k, v in cnt.items()))
    rep.append(f"- Ungradeable: {int((d['gradable'] == 0).sum())}; maculopathy labelled: {int(d['maculopathy'].notna().sum())}"
               f" (positive {int((d['maculopathy'] == 1).sum())}); patients: {d['patient_id'].nunique()}")
    cols = ["image_id", "dataset", "raw_path", "patient_id", "eye", "grade", "gradable", "maculopathy", "official_split", "grade_raw"]
    return d[cols], rep


def run(cfg) -> pd.DataFrame:
    cfg.work.mkdir(parents=True, exist_ok=True)
    frames, report = [], ["# Ingest report", "",
                          "Check every MISMATCH and missing-file line before going further.", ""]
    for name, spec in cfg.datasets.items():
        if spec.get("role", "off") == "off":
            continue
        d, rep = ingest_dataset(name, spec, cfg.raw)
        report += rep + [""]
        if d is not None:
            frames.append(d)
    if not frames:
        raise SystemExit(f"No datasets found under {cfg.raw}. See config/datasets.yaml for the expected layout.")
    m = pd.concat(frames, ignore_index=True)
    m.to_csv(cfg.manifest_raw, index=False)
    (cfg.work / "ingest_report.md").write_text("\n".join(report) + "\n")
    print(f"ingest: {len(m)} images from {m['dataset'].nunique()} datasets -> {cfg.manifest_raw}")
    print(f"        read {cfg.work / 'ingest_report.md'} before continuing")
    return m
