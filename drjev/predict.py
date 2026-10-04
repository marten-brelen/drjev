"""Stage 4: run a model over a split and store one row per image, question and wording.

Files: work/preds/<run>/<dataset>__<split>__v<variant>.jsonl
Row:   {"image_id", "q", "v", "p": [...], "u": float or null, "ms": float}
Interrupted runs resume where they stopped."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd

from . import adapters, lock, questions
from .config import TEST_SPLITS
from .splits import load_manifest

DEFAULT_SPLITS = ("calibration", "q3_cal", "test_internal", "test")


def pred_file(cfg, run_name, dataset, split, variant) -> Path:
    return cfg.preds_dir / run_name / f"{dataset}__{split}__v{variant}.jsonl"


def _done_ids(path: Path, n_questions: int) -> set[str]:
    if not path.exists():
        return set()
    counts: dict[str, int] = {}
    with open(path) as f:
        for line in f:
            try:
                counts[json.loads(line)["image_id"]] = counts.get(json.loads(line)["image_id"], 0) + 1
            except (json.JSONDecodeError, KeyError):
                continue
    return {k for k, v in counts.items() if v >= n_questions}


def run(cfg, run_name: str, splits=DEFAULT_SPLITS, datasets=None, variants=(0,), limit: int | None = None,
        question_ids=None) -> int:
    spec = cfg.run(run_name)
    m = load_manifest(cfg)
    m = m[m["split"].isin(splits)]
    if datasets:
        m = m[m["dataset"].isin(datasets)]
    if m.empty:
        print(f"[{run_name}] nothing to predict for splits {list(splits)}")
        return 0
    adapter = adapters.make(spec, cfg)
    total = 0
    loaded = False
    try:
        for variant in variants:
            qs = questions.load(cfg.questions_file, variant)
            if question_ids:
                qs = [q for q in qs if q.id in question_ids]
            for (dataset, split), grp in m.groupby(["dataset", "split"], sort=True):
                if variant > 0:                       # paraphrases run on the fixed subset only
                    grp = grp[grp["para_subset"]]
                if limit:
                    grp = grp.head(limit)
                out = pred_file(cfg, run_name, dataset, split, variant)
                done = _done_ids(out, len(qs))
                todo = grp[~grp["image_id"].isin(done)]
                if todo.empty:
                    continue
                lock.guard(cfg, split, run_name, dataset, len(todo))
                if not loaded:
                    adapter.load()
                    loaded = True
                out.parent.mkdir(parents=True, exist_ok=True)
                t0 = time.time()
                with open(out, "a") as f:
                    for k, r in enumerate(todo.itertuples(), 1):
                        answers = adapter.answer(r.path, qs)
                        for q, a in zip(qs, answers):
                            f.write(json.dumps({"image_id": r.image_id, "q": q.id, "v": variant,
                                                "p": a.p, "u": a.u,        # full precision: rounding would cap how far a sharp model can be calibrated
                                                "ms": round(a.ms, 2)}) + "\n")
                        if k % 500 == 0:
                            f.flush()
                            rate = k / (time.time() - t0)
                            print(f"[{run_name}] {dataset}/{split} v{variant}: {k}/{len(todo)} ({rate:.1f} images/s)")
                total += len(todo)
                print(f"[{run_name}] {dataset}/{split} v{variant}: {len(todo)} images -> {out.name}")
    finally:
        if loaded:
            adapter.close()
    return total


def check_model(cfg, run_name: str, n: int = 2) -> None:
    """Smoke test: run a model on n calibration images and print what comes back."""
    spec = cfg.run(run_name)
    m = load_manifest(cfg)
    rows = m[m["split"].isin(["calibration", "dev", "train"])].head(n)
    a = adapters.make(spec, cfg)
    a.load()
    try:
        qs = questions.load(cfg.questions_file, 0)
        for r in rows.itertuples():
            print(f"\n{r.image_id}  (grade {r.grade}, gradable {r.gradable})")
            for q, ans in zip(qs, a.answer(r.path, qs)):
                assert len(ans.p) == len(q.options) and abs(sum(ans.p) - 1) < 1e-3, "probabilities must cover the options and sum to 1"
                shown = ", ".join(f"{k}={p:.3f}" for k, p in zip(q.keys, ans.p))
                print(f"  {q.id:15s} {shown}   unknown={'-' if ans.u is None else f'{ans.u:.3f}'}   {ans.ms:.0f} ms")
    finally:
        a.close()
    print(f"\n[{run_name}] adapter returned well-formed answers. Adapter tested in the test suite: {a.tested}")


def load_preds(cfg, run_name: str, dataset: str, split: str, variant: int = 0) -> pd.DataFrame | None:
    """Long table of predictions, last write wins if an image was predicted twice."""
    f = pred_file(cfg, run_name, dataset, split, variant)
    if not f.exists():
        return None
    rows = [json.loads(line) for line in open(f) if line.strip()]
    if not rows:
        return None
    d = pd.DataFrame(rows).drop_duplicates(["image_id", "q"], keep="last")
    return d
