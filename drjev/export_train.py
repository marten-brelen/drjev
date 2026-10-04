"""Write the training set in imajev's manifest format, plus the commands to train and serve the adapter.

Format checked against github.com/mohit67890/imajev at commit ccf586d4 (scripts/decision_data.py,
src/vision_decision/contracts.py): one JSON line per image with `request.fields` (boolean / ordinal),
`targets` keyed by field id (true/false, an integer level, or null for "unknown"), `partition`, and `images`.

Training itself needs a GPU and has NOT been run from this pipeline: treat the generated scripts as a
starting point and check the first steps of the training log."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import questions
from .splits import load_manifest
from .targets import UNKNOWN, target

Q3_SPLITS = {"train": "q3_train", "dev": "q3_dev"}


def field(q) -> dict:
    """A question as an imajev internal request field (the same mapping its server applies to a Jev request)."""
    if q.kind == "noul":
        return {"id": q.id, "type": "boolean", "question": q.instruction, "yes_description": q.options[1][1], "no_description": q.options[0][1]}
    if q.kind == "score":
        return {"id": q.id, "type": "ordinal", "question": q.instruction, "levels": [{"value": i, "description": d} for i, (_, d) in enumerate(q.options)]}
    return {"id": q.id, "type": "choice", "question": q.instruction, "options": [{"value": k, "description": d} for k, d in q.options]}


def to_target(q, t):
    if t == UNKNOWN:
        return None
    return bool(t) if q.kind == "noul" else int(t)


def records(cfg, rows, partition: str, qs, rng=None, balance: bool = False, prefix: str = "") -> list[dict]:
    out = []
    reps = np.ones(len(rows), int)
    if balance:  # grade-balanced sampling by repetition: every grade (and "ungradeable") approaches the size of the largest, capped at 5x
        key = np.where(rows["gradable"] == 0, -1, rows["grade"].fillna(-2)).astype(int)
        counts = {k: int((key == k).sum()) for k in np.unique(key)}
        top = max(counts.values())
        reps = np.array([min(5, max(1, round(top / counts[k]))) for k in key])
    for r, n in zip(rows.itertuples(), reps):
        fields, targets = [], {}
        for q in qs:
            t = target(q.id, r.grade, r.gradable, r.maculopathy)
            if t is None:
                continue
            fields.append(field(q))
            targets[q.id] = to_target(q, t)
        if not fields:
            continue
        for k in range(int(n)):
            rid = f"{prefix}{r.image_id.replace(':', '-')}" + (f"-r{k}" if k else "")
            out.append({"id": rid, "partition": partition, "source": r.dataset,
                        "request": {"schema_version": "1.0", "request_id": rid[:128], "state": {}, "fields": fields},
                        "targets": targets, "images": [{"image": r.path, "sha256": r.sha256}]})
    if rng is not None:
        rng.shuffle(out)
    return out


def run(cfg, run_name: str, imajev_dir: str = "../imajev") -> Path:
    spec = cfg.run(run_name)
    tr = spec.get("train") or {}
    if tr.get("recipe") != "imajev_lora":
        raise SystemExit(f"{run_name}: not an imajev fine-tuning run")
    man = load_manifest(cfg)
    qs = questions.load(cfg.questions_file, 0)
    rng = np.random.default_rng(cfg.seed + int(spec.get("seed", 0)))
    size = tr.get("train_size", "full")
    train = man[man["split"] == "train"]
    if size != "full":
        col = f"eff_{int(size)}"
        if col not in man:
            raise SystemExit(f"{run_name}: no subset column {col}; add {size} to splits.efficiency_subsets and re-split before locking")
        train = train[train[col]]
    recs = records(cfg, train, "train", qs, rng, balance=True)
    recs += records(cfg, man[man["split"] == "dev"], "dev", qs)
    q3 = [q for q in qs if q.id == "q3_maculopathy"]
    for part, split in Q3_SPLITS.items():      # maculopathy is taught from its own dataset (EyePACS has no labels)
        recs += records(cfg, man[man["split"] == split], part, q3, rng if part == "train" else None, prefix="q3-")
    version = f"drjev-{run_name}"
    root = (cfg.base / imajev_dir).resolve() if not Path(imajev_dir).is_absolute() else Path(imajev_dir)
    out_dir = root / "data" / "manifests" if root.is_dir() else cfg.work / "train_manifests"
    out_dir.mkdir(parents=True, exist_ok=True)
    mf = out_dir / f"{version}.jsonl"
    with open(mf, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    n_tr = sum(r["partition"] == "train" for r in recs)
    n_dec = sum(len(r["targets"]) for r in recs if r["partition"] == "train")
    unk = sum(v is None for r in recs if r["partition"] == "train" for v in r["targets"].values())
    seed = int(spec.get("seed", 0))
    port = spec.get("url", "http://127.0.0.1:8770/").rsplit(":", 1)[-1].split("/")[0]
    vision = bool(tr.get("vision_lora"))
    sh = cfg.work / "train_scripts" / f"{run_name}.sh"
    sh.parent.mkdir(parents=True, exist_ok=True)
    mt = cfg.machine["training"]["imajev"]                 # run-level settings win over the machine profile
    bsz, acc, budget = (tr.get(k) or mt[k] for k in ("batch_size", "accumulate", "token_budget"))
    py = spec.get("python") or "python"
    py = py if py == "python" or Path(py).is_absolute() else str(cfg.base / py)
    envs = " ".join(f'{k}="{v}"' for k, v in (cfg.machine.get("env") or {}).items())
    sh.write_text(f"""#!/usr/bin/env bash
# Generated by drjev export-train for run {run_name} (machine profile: {cfg.machine['name']}).
# NOT yet run on a GPU by the pipeline authors: watch the first steps.
# {n_tr} training records, {n_dec} decisions, {unk} of them with the target "unknown" ({100 * unk / max(1, n_dec):.1f}%).
#
#   bash {sh.name}            full training run
#   PROBE=1 bash {sh.name}    20 steps only, to time it; then `drjev benchmark --train --run {run_name}`
set -euo pipefail
cd "{root}"
export {envs}
{'export DRJEV_LORA_TARGET_REGEX=".*(language_model|visual|vision_tower).*"   # arm B: needs patches/imajev_vision_lora.patch applied' if vision else '# arm A: language-layer LoRA only (the imajev recipe)'}
OUT=runs/{version}
EXTRA=""
if [ "${{PROBE:-0}}" = "1" ]; then OUT=runs/{version}-probe; EXTRA="--max-steps 20 --dev-cases 8"; rm -rf "$OUT"; fi
PYTHONPATH=src:scripts {py} scripts/train_decision_lora_torch.py \\
  --model {tr.get('base_model', 'Qwen/Qwen3.5-4B')} --revision {tr.get('base_revision', '851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a')} \\
  --init-adapter {tr.get('init_adapter', 'adapters/imajev-4b')} \\
  --version {version} --output "$OUT" \\
  --epochs {tr.get('epochs', 3)} --lr {tr.get('lr', 5e-5)} --seed {seed} \\
  --batch-size {bsz} --accumulate {acc} --token-budget {budget} \\
  --pixels 400000 --ordinal-weight {tr.get('ordinal_weight', 0.0)} \\
  --dev-every {tr.get('dev_every', 100)} --dev-cases {tr.get('dev_cases', 600)} --select dev_loss $EXTRA
# The trainer keeps its best checkpoint (lowest dev loss) in runs/{version}/best and a log in runs/{version}/log.jsonl.
# If a batch does not fit in memory the trainer splits it and carries on; lower --token-budget if that happens often.
# When it has finished, set `enabled: true` for {run_name} in config/models.yaml: `drjev run` then serves
# runs/{version}/best on port {port} by itself (no --calibration: the pipeline fits its own temperature).
""")
    sh.chmod(0o755)
    print(f"export-train [{run_name}]: {n_tr} records / {n_dec} decisions ({unk} unknown) -> {mf}\n  training script: {sh}")
    return mf
