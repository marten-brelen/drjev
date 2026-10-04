"""`drjev benchmark`: time each model on a few hundred non-test images and project the cost of the full study.

Run it before committing to the plan: on a small machine the projection decides how many seeds and arms fit."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import adapters, machine, questions
from .splits import load_manifest

TIMING_SPLITS = ("calibration", "dev", "train")           # never a test split: no lock needed, nothing leaks


class MemoryTrace:
    """Lowest available memory seen while a block runs."""

    def __enter__(self):
        self.start = self.low = machine.available_gb()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()
        return self

    def _loop(self):
        while not self._stop.wait(0.5):
            self.low = min(self.low, machine.available_gb())

    def __exit__(self, *a):
        self._stop.set()
        self._t.join()
        self.low = min(self.low, machine.available_gb())

    @property
    def used(self) -> float:
        return max(0.0, self.start - self.low)


def workload(cfg, man: pd.DataFrame) -> dict:
    """How many images each model must answer in the full study."""
    nv = questions.n_variants(cfg.questions_file)
    primary = int(man["split"].isin(["calibration", "q3_cal", "test_internal", "test"]).sum())
    para = int((man["split"].isin(["test_internal", "test"]) & man["para_subset"]).sum()) * (nv - 1)
    return {"primary_images": primary, "paraphrase_images": para, "total_images": primary + para}


def inference(cfg, runs: list[str], n: int = 200, warmup: int = 3) -> pd.DataFrame:
    man = load_manifest(cfg)
    pool = man[man["split"].isin(TIMING_SPLITS)]
    rows_ = pd.concat([pool[pool["split"] == s] for s in TIMING_SPLITS]).head(n + warmup)
    if len(rows_) <= warmup:
        raise SystemExit("benchmark: no non-test images in the manifest; run `drjev split` first")
    qs = questions.load(cfg.questions_file, 0)
    load_ = workload(cfg, man)
    out = []
    for name in runs:
        row = {"run": name, "arm": cfg.runs[name].get("arm", ""), "status": "ok"}
        a = None
        try:
            a = adapters.make(cfg.run(name), cfg)
            with MemoryTrace() as mem:
                t0 = time.time()
                a.load()
                row["load_seconds"] = round(time.time() - t0, 1)
                for r in rows_.head(warmup).itertuples():       # first requests compile and cache: not timed
                    a.answer(r.path, qs)
                per_image, per_decision = [], []
                for r in rows_.iloc[warmup:].itertuples():
                    t1 = time.time()
                    ans = a.answer(r.path, qs)
                    per_image.append(time.time() - t1)
                    per_decision += [x.ms for x in ans]
            sec = float(np.mean(per_image))
            row.update(images_timed=len(per_image), seconds_per_image=round(sec, 4), images_per_second=round(1 / sec, 2),
                       ms_per_decision_p50=round(float(np.median(per_decision)), 1), ms_per_decision_p95=round(float(np.quantile(per_decision, 0.95)), 1),
                       memory_used_gb=round(mem.used, 1), lowest_available_gb=round(mem.low, 1),
                       hours_primary=round(sec * load_["primary_images"] / 3600, 2), hours_paraphrases=round(sec * load_["paraphrase_images"] / 3600, 2),
                       hours_total=round(sec * load_["total_images"] / 3600, 2))
        except SystemExit:
            raise
        except Exception as e:
            row["status"] = f"FAILED: {type(e).__name__}: {str(e)[:300]}"
        finally:
            if a is not None:
                try:
                    a.close()
                except Exception as e:
                    row["status"] += f"; close failed: {e}"
        out.append(row)
        shown = f"{row['seconds_per_image']:.3f} s per image, about {row['hours_total']:.1f} h for the study" if row["status"] == "ok" else row["status"]
        print(f"benchmark [{name}]: {shown}")
    df = pd.DataFrame(out)
    df.attrs["workload"] = load_
    return df


def imajev_training(cfg, run_name: str, imajev_dir: str) -> dict:
    """Projection from a probe of imajev's trainer (`PROBE=1 bash work/train_scripts/<run>.sh`)."""
    root = Path(imajev_dir) if Path(imajev_dir).is_absolute() else cfg.base / imajev_dir
    log = root / "runs" / f"drjev-{run_name}-probe" / "log.jsonl"
    script = cfg.work / "train_scripts" / f"{run_name}.sh"
    if not log.exists():
        return {"run": run_name, "status": f"no probe yet: run `drjev export-train --run {run_name}` then `PROBE=1 bash {script}`"}
    steps = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
    if len(steps) < 3:
        return {"run": run_name, "status": f"probe log has only {len(steps)} steps"}
    per_step = (steps[-1]["seconds"] - steps[1]["seconds"]) / (len(steps) - 2)     # the first step includes start-up
    total = steps[-1]["of"]
    return {"run": run_name, "status": "ok", "steps_timed": len(steps) - 2, "seconds_per_step": round(per_step, 2), "steps_total": int(total),
            "examples_per_second": round(float(np.mean([s["examples_per_second"] for s in steps[1:]])), 2),
            "hours_total": round(per_step * total / 3600, 1)}


def training(cfg, runs: list[str], imajev_dir: str, steps: int = 30, device=None) -> pd.DataFrame:
    out = []
    for name in runs:
        recipe = (cfg.runs[name].get("train") or {}).get("recipe")
        if recipe == "specialist":
            from . import specialist
            from .cli import in_env
            try:
                tmp = cfg.work / f"probe_{name}.json"
                if in_env(cfg, name, ["probe-specialist", "--run", name, "--steps", str(steps), "--out", str(tmp)] + (["--device", device] if device else [])):
                    out.append(json.loads(tmp.read_text()))
                else:
                    out.append(specialist.probe(cfg, name, steps=steps, device=device))
            except Exception as e:
                out.append({"run": name, "status": f"FAILED: {type(e).__name__}: {str(e)[:300]}"})
        elif recipe == "imajev_lora":
            out.append(imajev_training(cfg, name, imajev_dir))
        if out:
            r = out[-1]
            print(f"benchmark [{name}] training: " + (f"about {r['hours_total']} h" if r["status"] == "ok" else r["status"]))
    return pd.DataFrame(out)


def run(cfg, runs=None, n: int = 200, train: bool = False, imajev_dir: str = "../imajev", steps: int = 30, device=None):
    cfg.work.mkdir(parents=True, exist_ok=True)
    lines = ["# Benchmark", "", f"Machine profile: {cfg.machine['name']}. Timed on {n} non-test images per model; projections scale that to the full study.", ""]
    if not train:
        df = inference(cfg, runs or cfg.enabled_runs(), n)
        df.to_csv(cfg.work / "benchmark_inference.csv", index=False)
        w = df.attrs["workload"]
        ok = df[df["status"] == "ok"]
        lines += [f"Each model answers {w['primary_images']:,} images with the primary wording and {w['paraphrase_images']:,} more for the two paraphrases.", ""]
        if len(ok):
            lines += ["| Model | Seconds per image | Memory used (GB) | Hours, primary | Hours, paraphrases | Hours, total |", "|---|---|---|---|---|---|"]
            lines += [f"| {r.run} | {r.seconds_per_image:.3f} | {r.memory_used_gb:.0f} | {r.hours_primary:.1f} | {r.hours_paraphrases:.1f} | {r.hours_total:.1f} |" for r in ok.itertuples()]
            lines += ["", f"**All timed models, one after another: about {ok['hours_total'].sum():.0f} hours** ({ok['hours_total'].sum() / 24:.1f} days)."]
            print(f"\nbenchmark: inference for {len(ok)} models would take about {ok['hours_total'].sum():.0f} hours in total")
        for r in df[df["status"] != "ok"].itertuples():
            lines.append(f"- {r.run}: {r.status}")
        target = cfg.work / "benchmark_inference.md"
    else:
        names = runs or [n_ for n_, s in cfg.runs.items() if (s.get("train") or {}).get("recipe")]
        df = training(cfg, names, imajev_dir, steps, device)
        df.to_csv(cfg.work / "benchmark_training.csv", index=False)
        ok = df[df["status"] == "ok"] if len(df) else df
        if len(ok):
            lines += ["| Run | Seconds per step | Steps | Hours |", "|---|---|---|---|"]
            lines += [f"| {r.run} | {r.seconds_per_step} | {r.steps_total:,} | {r.hours_total} |" for r in ok.itertuples()]
            lines += ["", f"**All timed training runs: about {ok['hours_total'].sum():.0f} hours** ({ok['hours_total'].sum() / 24:.1f} days)."]
            print(f"\nbenchmark: {len(ok)} timed training runs would take about {ok['hours_total'].sum():.0f} hours in total")
        for r in (df[df["status"] != "ok"].itertuples() if len(df) else []):
            lines.append(f"- {r.run}: {r.status}")
        target = cfg.work / "benchmark_training.md"
    target.write_text("\n".join(lines) + "\n")
    print(f"benchmark: -> {target}")
    return df
