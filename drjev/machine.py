"""Machine profile and process control: memory on a shared CPU/GPU pool, and clean start/stop of model processes."""
from __future__ import annotations

import os
import shlex
import signal
import subprocess
import threading
import time
from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parent.parent / "config" / "machines" / "generic.yaml"


def load_profile(path: Path | None) -> dict:
    prof = yaml.safe_load(DEFAULT.read_text())
    if path:
        mine = yaml.safe_load(Path(path).read_text()) or {}
        for k, v in mine.items():
            prof[k] = {**prof.get(k, {}), **v} if isinstance(v, dict) and isinstance(prof.get(k), dict) else v
    return prof


def meminfo() -> dict[str, float]:
    """Memory figures in GB from /proc/meminfo (empty off Linux)."""
    out = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            out[k] = int(v.split()[0]) / 1024 ** 2
    except OSError:
        pass
    return out


def available_gb() -> float:
    return meminfo().get("MemAvailable", float("inf"))


def wait_for_memory(need_gb: float, seconds: float, label: str = "") -> bool:
    """Wait until `need_gb` is available (the previous model may still be releasing memory)."""
    deadline = time.time() + seconds
    while available_gb() < need_gb:
        if time.time() >= deadline:
            print(f"[{label}] WARNING only {available_gb():.0f} GB available, wanted {need_gb:.0f} GB; starting anyway")
            return False
        time.sleep(2)
    return True


class Managed:
    """A model process the pipeline owns: started in its own process group with the profile's environment,
    watched for memory, and stopped completely (the shell and everything it started)."""

    def __init__(self, cmd, label: str, profile: dict, cwd=None, env=None, shell=True, stdin=None, stdout=None):
        mem = profile.get("memory", {})
        wait_for_memory(float(mem.get("free_before_model_gb", 0)), float(mem.get("wait_seconds", 0)), label)
        full_env = dict(os.environ, **{k: str(v) for k, v in (profile.get("env") or {}).items()}, **{k: str(v) for k, v in (env or {}).items()})
        prefix = (mem.get("launch_prefix") or "").strip()
        if prefix:
            cmd = f"{prefix} {cmd}" if shell else shlex.split(prefix) + list(cmd)
        self.label, self.floor = label, float(mem.get("floor_gb", 0))
        self.killed_for_memory = False
        self.min_available = available_gb()
        self.proc = subprocess.Popen(cmd, shell=shell, cwd=cwd, env=full_env, start_new_session=True, stdin=stdin, stdout=stdout)
        self._stop = threading.Event()
        self._watch = threading.Thread(target=self._watchdog, daemon=True)
        self._watch.start()

    def _watchdog(self):
        while not self._stop.wait(1.0):
            a = available_gb()
            self.min_available = min(self.min_available, a)
            if a < self.floor and self.proc.poll() is None:
                self.killed_for_memory = True
                print(f"[{self.label}] available memory fell to {a:.1f} GB (floor {self.floor:.0f} GB): stopping the model process")
                self._signal(signal.SIGKILL)
                return

    def _signal(self, sig):
        try:
            os.killpg(os.getpgid(self.proc.pid), sig)
        except (ProcessLookupError, PermissionError):
            pass

    def alive(self) -> bool:
        return self.proc.poll() is None

    def check(self):
        if self.killed_for_memory:
            raise RuntimeError(f"[{self.label}] stopped because available memory fell below {self.floor:.0f} GB")
        if not self.alive():
            raise RuntimeError(f"[{self.label}] the model process exited with code {self.proc.returncode}")

    def stop(self, grace: float = 30):
        self._stop.set()
        for sig in (signal.SIGTERM, signal.SIGKILL):
            if self.proc.poll() is not None:
                break
            self._signal(sig)
            try:
                self.proc.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                continue
        self._signal(signal.SIGKILL)                  # children that outlived the shell
