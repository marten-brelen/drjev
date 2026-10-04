"""Command line for the study pipeline. `drjev run` does every stage in order."""
from __future__ import annotations

import argparse
import sys

from .config import Config


def _cfg(a) -> Config:
    return Config(a.config)


def cmd_demo(a):
    from . import demo
    path = demo.make(a.target, scale=a.scale)
    print(f"demo workspace ready. Next:\n  drjev run --config {path} --lock")


def cmd_ingest(a):
    from . import ingest
    ingest.run(_cfg(a))


def cmd_preprocess(a):
    from . import preprocess
    preprocess.run(_cfg(a))


def cmd_split(a):
    from . import splits
    cfg = _cfg(a)
    if cfg.lock_file.exists():
        raise SystemExit("The protocol is locked; the splits cannot be redrawn.")
    splits.run(cfg)


def cmd_lock(a):
    from . import lock
    lock.create(_cfg(a), a.note)


def cmd_check_model(a):
    from . import predict
    predict.check_model(_cfg(a), a.run, a.n)


def cmd_predict(a):
    from . import predict, questions
    cfg = _cfg(a)
    runs = a.run or cfg.enabled_runs()
    nv = questions.n_variants(cfg.questions_file)
    for r in runs:
        predict.run(cfg, r, splits=a.splits or predict.DEFAULT_SPLITS, datasets=a.datasets,
                    variants=range(nv) if a.paraphrases else (0,), limit=a.limit)


def cmd_export_train(a):
    from . import export_train
    cfg = _cfg(a)
    for r in a.run or [n for n, s in cfg.runs.items() if (s.get("train") or {}).get("recipe") == "imajev_lora"]:
        export_train.run(cfg, r, a.imajev_dir)


def in_env(cfg, run_name: str, args: list[str]) -> bool:
    """Re-run a drjev command with the run's own interpreter. Returns False when the run has no separate environment."""
    import os
    import subprocess
    from pathlib import Path
    py = cfg.runs[run_name].get("python")
    if not py or os.environ.get("DRJEV_IN_ENV"):
        return False
    p = Path(py) if Path(py).is_absolute() else cfg.base / py
    if not p.exists():
        raise SystemExit(f"[{run_name}] environment not found: {p}. Create it with scripts/setup_env.sh.")
    root = str(Path(__file__).resolve().parent.parent)
    env = dict(os.environ, DRJEV_IN_ENV="1", PYTHONPATH=root + os.pathsep + os.environ.get("PYTHONPATH", ""),
               **{k: str(v) for k, v in (cfg.machine.get("env") or {}).items()})
    code = subprocess.run([str(p), "-m", "drjev", "--config", str(cfg.path), *args], env=env).returncode
    if code:
        raise SystemExit(code)
    return True


def cmd_train_specialist(a):
    from . import specialist
    cfg = _cfg(a)
    for r in a.run or [n for n, s in cfg.runs.items() if (s.get("train") or {}).get("recipe") == "specialist"]:
        if not in_env(cfg, r, ["train-specialist", "--run", r] + (["--device", a.device] if a.device else [])):
            specialist.train(cfg, r, device=a.device)


def cmd_probe_specialist(a):
    import json
    from . import specialist
    res = specialist.probe(_cfg(a), a.run, steps=a.steps, device=a.device)
    open(a.out, "w").write(json.dumps(res))


def cmd_doctor(a):
    from . import doctor
    code = doctor.run(_cfg(a))
    if code and not a.allow_fail:
        sys.exit(code)


def cmd_benchmark(a):
    from . import benchmark
    benchmark.run(_cfg(a), a.run, n=a.images, train=a.train, imajev_dir=a.imajev_dir, steps=a.steps, device=a.device)


def cmd_calibrate(a):
    from . import calibrate
    calibrate.run(_cfg(a), a.run)


def cmd_analyze(a):
    from . import analyze
    analyze.run(_cfg(a), a.bootstrap)


def cmd_report(a):
    from . import report
    report.run(_cfg(a))


def cmd_status(a):
    from . import report
    report.status(_cfg(a))


def cmd_run(a):
    """Every stage, in order. Stages whose outputs exist are reused; predictions resume."""
    from . import analyze, calibrate, ingest, lock, predict, preprocess, questions, report, splits
    cfg = _cfg(a)
    if not cfg.manifest.exists():
        ingest.run(cfg)
        preprocess.run(cfg)
        splits.run(cfg)
    else:
        print(f"run: using the existing split manifest ({cfg.manifest})")
    runs = a.run or cfg.enabled_runs()
    nv = questions.n_variants(cfg.questions_file)
    failed: dict[str, str] = {}

    def safely(r, **kw):                 # one model failing to load must not stop the others
        if r in failed:
            return
        try:
            predict.run(cfg, r, **kw)
        except SystemExit:
            raise
        except Exception as e:
            failed[r] = f"{type(e).__name__}: {e}"
            print(f"[{r}] FAILED and skipped: {failed[r]}")

    for r in runs:                       # calibration splits first: they do not need the lock
        safely(r, splits=("calibration", "q3_cal"), variants=(0,))
    if not cfg.lock_file.exists():
        if not a.lock:
            calibrate.run(cfg, [r for r in runs if r not in failed and (cfg.preds_dir / r).exists()])
            print("\nrun: stopped before the test sets. Review the splits, questions and analysis plan, then rerun with --lock "
                  "(or run `drjev lock`) to freeze the protocol and continue.")
            return
        lock.create(cfg, "created by `drjev run --lock`")
    for r in runs:
        safely(r, splits=("test_internal", "test"), variants=range(nv) if not a.no_paraphrases else (0,))
    done = [r for r in runs if r not in failed and (cfg.preds_dir / r).exists()]
    calibrate.run(cfg, done)
    analyze.run(cfg, a.bootstrap)
    report.run(cfg)
    if failed:
        print("\nrun: these models failed and are not in the results:")
        for r, why in failed.items():
            print(f"  {r}: {why}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="drjev", description="Pipeline for the image decision model study on diabetic retinopathy grading")
    p.add_argument("--config", default="config/study.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        s = sub.add_parser(name, help=help_)
        s.add_argument("--config", default=argparse.SUPPRESS)
        s.set_defaults(fn=fn)
        return s

    s = add("demo", cmd_demo, "create a synthetic demo workspace (no patient data)")
    s.add_argument("target")
    s.add_argument("--scale", type=int, default=1)
    add("ingest", cmd_ingest, "read dataset label files into one manifest")
    add("preprocess", cmd_preprocess, "crop, resize and hash every image")
    add("split", cmd_split, "patient-level splits, duplicate removal, fixed subsets")
    s = add("lock", cmd_lock, "freeze splits, questions and analysis plan; required before any test-set prediction")
    s.add_argument("--note", default="")
    s = add("check-model", cmd_check_model, "run one model on a few non-test images and print its answers")
    s.add_argument("run")
    s.add_argument("-n", type=int, default=2)
    s = add("predict", cmd_predict, "run models over splits (resumes)")
    s.add_argument("--run", nargs="*")
    s.add_argument("--splits", nargs="*")
    s.add_argument("--datasets", nargs="*")
    s.add_argument("--paraphrases", action="store_true", help="also run wordings 1 and 2 on the fixed subset")
    s.add_argument("--limit", type=int)
    s = add("export-train", cmd_export_train, "write imajev training manifests and run scripts")
    s.add_argument("--run", nargs="*")
    s.add_argument("--imajev-dir", default="../imajev")
    s = add("train-specialist", cmd_train_specialist, "train the specialist image classifier baseline")
    s.add_argument("--run", nargs="*")
    s.add_argument("--device", default=None)
    s = add("doctor", cmd_doctor, "check this computer, the datasets and the model environments")
    s.add_argument("--allow-fail", action="store_true")
    s = add("benchmark", cmd_benchmark, "time each model on non-test images and project the cost of the study")
    s.add_argument("--run", nargs="*")
    s.add_argument("--images", type=int, default=200)
    s.add_argument("--train", action="store_true", help="time training instead of inference")
    s.add_argument("--steps", type=int, default=30)
    s.add_argument("--imajev-dir", default="../imajev")
    s.add_argument("--device", default=None)
    s = add("probe-specialist", cmd_probe_specialist, argparse.SUPPRESS)    # used by `benchmark --train` inside the model environment
    s.add_argument("--run", required=True)
    s.add_argument("--steps", type=int, default=30)
    s.add_argument("--device", default=None)
    s.add_argument("--out", required=True)
    s = add("calibrate", cmd_calibrate, "fit temperatures and thresholds on the calibration splits")
    s.add_argument("--run", nargs="*")
    s = add("analyze", cmd_analyze, "compute all metrics, intervals and pre-specified tests")
    s.add_argument("--bootstrap", type=int)
    add("report", cmd_report, "write tables, figures and the results summary")
    add("status", cmd_status, "show what has been done so far")
    s = add("run", cmd_run, "all stages in order")
    s.add_argument("--run", nargs="*")
    s.add_argument("--lock", action="store_true", help="freeze the protocol and continue to the test sets")
    s.add_argument("--no-paraphrases", action="store_true")
    s.add_argument("--bootstrap", type=int)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
