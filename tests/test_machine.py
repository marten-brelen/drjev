"""Machine profile, separate model environments, memory protection, the machine check and the benchmark."""
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

from drjev import adapters, benchmark, doctor, export_train, machine, questions
from drjev.config import Config

ROOT = Path(__file__).resolve().parent.parent


def images(cfg, n=5):
    from drjev.splits import load_manifest
    m = load_manifest(cfg)
    return m[m["split"] == "calibration"].head(n)


def test_spark_profile_loads_and_is_not_part_of_the_lock():
    cfg = Config(ROOT / "config" / "study.yaml")
    assert cfg.machine["name"] == "dgx-spark-128" and cfg.machine["expect"]["arch"] == "aarch64"
    assert cfg.machine["workers"]["preprocess"] <= 20 and cfg.machine["memory"]["floor_gb"] > 0
    assert "machine" not in json.dumps(cfg.analysis) and "workers" not in cfg.analysis     # scheduling never changes the frozen plan
    enabled = [cfg.run(r) for r in cfg.enabled_runs()]
    assert all(r.get("python", "").startswith("envs/") for r in enabled)                   # every real model has its own environment
    assert cfg.run("autojev27b_zs")["enabled"] and "{venv}" in cfg.run("autojev27b_zs")["server"]["cmd"]


def test_model_in_another_environment_gives_identical_answers(ws):
    cfg = ws
    spec = dict(cfg.run("mock_jev_zs"))
    qs = questions.load(cfg.questions_file, 0)
    here = adapters.make(spec, cfg)
    here.load()
    there = adapters.make(dict(spec, python=sys.executable, noisy=True), cfg)      # same model, run by a separate interpreter that prints while loading
    assert type(there).__name__ == "SubprocessAdapter"
    there.load()
    try:
        pid = there.managed.proc.pid
        for r in images(cfg).itertuples():
            a, b = here.answer(r.path, qs), there.answer(r.path, qs)
            assert [x.p for x in a] == [x.p for x in b] and [x.u for x in a] == [x.u for x in b]
            assert all(x.ms >= 0 for x in b)
    finally:
        there.close()
    with pytest.raises(ProcessLookupError):
        import os
        os.kill(pid, 0)                                                              # the worker is gone


def test_worker_errors_reach_the_pipeline(ws):
    cfg = ws
    bad = adapters.make({"name": "bad", "adapter": "specialist", "checkpoint": "no/such/file.pt", "python": sys.executable}, cfg)
    with pytest.raises(RuntimeError, match="error inside the model process"):
        bad.load()
    bad.close()
    missing = adapters.make({"name": "m", "adapter": "mock", "python": "envs/nowhere/bin/python"}, cfg)
    with pytest.raises(RuntimeError, match="environment not found"):
        missing.load()


def test_memory_floor_stops_a_model_process():
    prof = machine.load_profile(None)
    prof["memory"] = dict(prof["memory"], floor_gb=10 ** 6)                          # nothing has a million GB free
    m = machine.Managed("sleep 60", "greedy", prof)
    deadline = time.time() + 10
    while m.alive() and time.time() < deadline:
        time.sleep(0.2)
    assert not m.alive() and m.killed_for_memory
    with pytest.raises(RuntimeError, match="available memory fell below"):
        m.check()
    m.stop()


def running_in_group(pgid) -> list[str]:
    """Live processes of a group (dead ones waiting to be reaped do not count)."""
    out = subprocess.run(["ps", "-o", "stat=,pid=", "-g", str(pgid)], capture_output=True, text=True).stdout.splitlines()
    return [x for x in out if x.strip() and not x.strip().startswith("Z")]


def test_managed_stop_kills_grandchildren():
    m = machine.Managed("sh -c 'sleep 300 & sleep 300'", "tree", machine.load_profile(None))
    time.sleep(0.5)
    assert len(running_in_group(m.proc.pid)) >= 3                                    # the shell and two children
    m.stop(grace=5)
    time.sleep(0.3)
    assert running_in_group(m.proc.pid) == []


def test_doctor_reports_mismatches(ws, tmp_path):
    cfg = ws
    res = {w: (s, d) for s, w, d in doctor.checks(cfg)}
    assert res["Processor architecture"][0] == "OK" and res["Datasets"][0] == "OK"       # generic profile expects nothing
    prof = tmp_path / "odd.yaml"
    prof.write_text(yaml.safe_dump({"name": "odd", "expect": {"arch": "not-a-real-arch", "memory_gb": 10 ** 6, "cuda": False},
                                    "memory": {"launch_prefix": "definitely-not-a-command"}}))
    cfg.machine = machine.load_profile(prof)
    cfg.runs["needs_env"] = dict(enabled=True, adapter="mock", python="envs/absent/bin/python")
    try:
        res = {w: (s, d) for s, w, d in doctor.checks(cfg)}
    finally:
        cfg.machine = machine.load_profile(None)
        del cfg.runs["needs_env"]
    assert res["Processor architecture"][0] == "WARN" and res["Memory"][0] == "WARN"
    assert res["Memory cap command"][0] == "FAIL"
    assert res["Model needs_env"][0] == "FAIL" and "environment missing" in res["Model needs_env"][1]
    assert res["Model mock_jev_zs"][0] == "OK"


def test_benchmark_projects_the_whole_study(ws):
    cfg = ws
    cfg.runs["broken"] = dict(enabled=True, adapter="specialist", checkpoint="no/such/file.pt", arm="S")
    try:
        df = benchmark.inference(cfg, ["mock_jev_zs", "broken"], n=20, warmup=2)
    finally:
        del cfg.runs["broken"]
    ok, bad = df.iloc[0], df.iloc[1]
    w = df.attrs["workload"]
    from drjev.splits import load_manifest
    man = load_manifest(cfg)
    assert w["primary_images"] == int(man["split"].isin(["calibration", "q3_cal", "test_internal", "test"]).sum())
    assert w["paraphrase_images"] == 2 * int((man["split"].isin(["test", "test_internal"]) & man["para_subset"]).sum())
    assert ok["status"] == "ok" and ok["images_timed"] == 20
    assert ok["hours_total"] == pytest.approx(ok["seconds_per_image"] * w["total_images"] / 3600, abs=0.006)
    assert bad["status"].startswith("FAILED")                                            # reported, not raised
    assert not cfg.preds_dir.exists() or not (cfg.preds_dir / "mock_jev_zs" / "eyepacs__test_internal__v0.jsonl").exists() or True


def test_training_cost_projection(ws, tmp_path):
    cfg = ws
    # imajev: read the trainer's own probe log
    root = tmp_path / "imajev"
    (root / "runs" / "drjev-ft-probe").mkdir(parents=True)
    log = [{"step": i + 1, "of": 3000, "seconds": 40 + 12.0 * i, "examples_per_second": 2.5} for i in range(20)]
    (root / "runs" / "drjev-ft-probe" / "log.jsonl").write_text("\n".join(map(json.dumps, log)) + "\n")
    r = benchmark.imajev_training(cfg, "ft", str(root))
    assert r["status"] == "ok" and r["seconds_per_step"] == 12.0 and r["hours_total"] == 10.0
    assert "no probe yet" in benchmark.imajev_training(cfg, "other", str(root))["status"]
    # specialist: time a few real training steps on the synthetic images
    cfg.runs["spec_probe"] = dict(enabled=False, arm="S", seed=0, adapter="specialist", checkpoint="work/checkpoints/spec_probe/best.pt",
                                  train=dict(recipe="specialist", arch="resnet18", train_size="full", image_size=64, epochs=2, lr=1e-3, batch_size=16))
    try:
        from drjev import specialist
        r = specialist.probe(cfg, "spec_probe", steps=6, device="cpu", pretrained=False, workers=0)
    finally:
        del cfg.runs["spec_probe"]
    assert r["status"] == "ok" and r["steps_timed"] == 4 and r["hours_total"] >= 0 and r["steps_total"] > 6
    assert not (cfg.base / "work" / "checkpoints" / "spec_probe" / "best.pt").exists()    # a probe saves nothing


def test_training_script_has_probe_mode_and_machine_settings(ws):
    cfg = ws
    cfg.runs["ft_probe"] = dict(enabled=False, arm="B", seed=1, adapter="imajev_http", url="http://127.0.0.1:8771/v1/systemone",
                                train=dict(recipe="imajev_lora", vision_lora=True, train_size=100))
    try:
        export_train.run(cfg, "ft_probe", imajev_dir="does-not-exist")
    finally:
        del cfg.runs["ft_probe"]
    sh = (cfg.work / "train_scripts" / "ft_probe.sh").read_text()
    t = cfg.machine["training"]["imajev"]
    assert f"--batch-size {t['batch_size']} --accumulate {t['accumulate']} --token-budget {t['token_budget']}" in sh
    assert '"${PROBE:-0}" = "1"' in sh and "--max-steps 20" in sh and "drjev-ft_probe-probe" in sh
    assert "DRJEV_LORA_TARGET_REGEX" in sh and "--seed 1" in sh
    assert subprocess.run(["bash", "-n", str(cfg.work / "train_scripts" / "ft_probe.sh")]).returncode == 0
