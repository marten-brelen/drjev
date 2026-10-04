"""`drjev doctor`: is this computer ready for the study? Run it first, and again after each setup step."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from . import machine

OK, WARN, FAIL = "OK", "WARN", "FAIL"
TORCH_PROBE = ("import torch,json;c=torch.cuda.is_available();print(json.dumps({'torch':torch.__version__,'cuda':c,"
               "'cuda_build':torch.version.cuda,'device':torch.cuda.get_device_name(0) if c else None,"
               "'capability':list(torch.cuda.get_device_capability(0)) if c else None}))")


def _run(cmd, timeout=60) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def checks(cfg) -> list[tuple[str, str, str]]:
    prof = cfg.machine
    exp = prof.get("expect", {})
    out: list[tuple[str, str, str]] = []
    add = lambda status, what, detail: out.append((status, what, detail))

    add(OK, "Machine profile", f"{prof['name']} ({cfg.machine_file or 'built-in generic profile'})")
    arch = platform.machine()
    add(OK if not exp.get("arch") or arch == exp["arch"] else WARN, "Processor architecture",
        arch + ("" if not exp.get("arch") or arch == exp["arch"] else f"; the profile expects {exp['arch']}"))
    pv = platform.python_version()
    add(OK if not exp.get("python") or pv.startswith(str(exp["python"])) else WARN, "Python", pv + (f"; the profile expects {exp['python']}" if exp.get("python") and not pv.startswith(str(exp["python"])) else ""))

    mem = machine.meminfo()
    if mem:
        total, avail = mem.get("MemTotal", 0), mem.get("MemAvailable", 0)
        need = float(exp.get("memory_gb", 0))
        add(OK if total >= need else WARN, "Memory", f"{total:.0f} GB total, {avail:.0f} GB available" + (f"; the profile expects at least {need:.0f} GB" if total < need else ""))
        swap = mem.get("SwapTotal", 0)
        if prof["memory"].get("warn_if_swap"):
            add(OK if swap == 0 else WARN, "Swap", "off" if swap == 0 else f"{swap:.0f} GB of swap is on. On shared CPU/GPU memory an over-sized model then freezes the machine instead of failing; "
                                                                             "turn it off with `sudo swapoff -a`")
        floor = float(prof["memory"].get("floor_gb", 0))
        add(OK if avail > floor * 2 else (WARN if avail > floor else FAIL), "Memory floor", f"model processes are stopped below {floor:.0f} GB available"
            + ("" if avail > floor * 2 else f"; only {avail:.0f} GB is available now" + ("" if avail > floor else ", so models would be stopped at once")))
    else:
        add(WARN, "Memory", "cannot read /proc/meminfo; memory protection is off")

    for label, path in (("Disk for work files", cfg.work), ("Disk for raw datasets", cfg.raw)):
        p = path
        while not p.exists():
            p = p.parent
        free = shutil.disk_usage(p).free / 1024 ** 3
        need = float(prof.get("disk", {}).get("min_free_gb", 0))
        add(OK if free >= need else WARN, label, f"{free:.0f} GB free at {p}" + ("" if free >= need else f"; the profile suggests {need:.0f} GB"))

    code, text = _run("nvidia-smi --query-gpu=name,driver_version --format=csv,noheader")
    want_gpu = bool(exp.get("cuda"))
    add(OK if code == 0 else (FAIL if want_gpu else WARN), "GPU driver", text.splitlines()[0] if code == 0 and text else "nvidia-smi not found or failed")
    add(OK if shutil.which("cc") or shutil.which("gcc") else WARN, "C compiler", shutil.which("cc") or shutil.which("gcc") or "none found; some model packages build GPU kernels at install or first run")
    for k, v in (prof.get("env") or {}).items():
        if str(v).startswith("/"):
            add(OK if Path(str(v)).exists() else WARN, f"Environment {k}", f"{v}" + ("" if Path(str(v)).exists() else " does not exist"))
    prefix = (prof["memory"].get("launch_prefix") or "").strip()
    if prefix:
        code, text = _run(f"{prefix} true")
        add(OK if code == 0 else FAIL, "Memory cap command", prefix if code == 0 else f"`{prefix}` failed: {text[:200]}")

    found = [n for n, s in cfg.datasets.items() if s.get("role", "off") != "off" and (cfg.raw / s["root"]).is_dir()]
    missing = [n for n, s in cfg.datasets.items() if s.get("role", "off") != "off" and not (cfg.raw / s["root"]).is_dir()]
    add(OK if not missing else WARN, "Datasets", f"found: {', '.join(found) or 'none'}" + (f"; not found: {', '.join(missing)}" if missing else ""))
    add(OK, "Protocol lock", "locked" if cfg.lock_file.exists() else "not locked yet (test sets cannot be read)")

    seen_env = {}
    for name in cfg.enabled_runs():
        run = cfg.run(name)
        py = run.get("python")
        problems = []
        if py:
            p = Path(py) if Path(py).is_absolute() else cfg.base / py
            if not p.exists():
                problems.append(f"environment missing ({py}); run scripts/setup_env.sh")
            elif str(p) not in seen_env:
                code, text = _run([str(p), "-c", TORCH_PROBE], timeout=180)
                seen_env[str(p)] = (code, text.splitlines()[-1] if text else "")
            if str(p) in seen_env:
                code, text = seen_env[str(p)]
                if code != 0:
                    problems.append(f"PyTorch does not import in {py}: {text[:160]}")
                elif '"cuda": true' not in text and want_gpu:
                    problems.append(f"PyTorch in {py} cannot see the GPU: {text[:200]}")
        srv = run.get("server") or {}
        if srv.get("cwd"):
            cwd = Path(srv["cwd"]) if os.path.isabs(srv["cwd"]) else cfg.base / srv["cwd"]
            if not cwd.is_dir():
                problems.append(f"server folder missing: {srv['cwd']}")
        for key in ("model_dir", "repo_dir", "checkpoint"):
            if run.get(key):
                p = Path(run[key]) if os.path.isabs(run[key]) else cfg.base / run[key]
                if not p.exists():
                    problems.append(f"{key} missing: {run[key]}")
        if not run.get("revision") and run.get("hf_repo"):
            problems.append("revision not pinned")
        hard = [x for x in problems if "not pinned" not in x]
        add(FAIL if hard else (WARN if problems else OK), f"Model {name}", "; ".join(problems) or "environment and files present")
    return out


def run(cfg) -> int:
    res = checks(cfg)
    width = max(len(w) for _, w, _ in res)
    for status, what, detail in res:
        print(f"  {status:4s}  {what:{width}s}  {detail}")
    cfg.work.mkdir(parents=True, exist_ok=True)
    (cfg.work / "doctor_report.md").write_text("# Machine check\n\n| Status | Check | Detail |\n|---|---|---|\n"
                                               + "\n".join(f"| {s} | {w} | {d} |" for s, w, d in res) + "\n")
    n_fail, n_warn = sum(s == FAIL for s, _, _ in res), sum(s == WARN for s, _, _ in res)
    print(f"\ndoctor: {n_fail} failed, {n_warn} warnings, {len(res) - n_fail - n_warn} ok -> {cfg.work / 'doctor_report.md'}")
    return 1 if n_fail else 0
