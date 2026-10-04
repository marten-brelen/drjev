"""Running a model outside the pipeline's own Python process.

Two ways, both owned by the pipeline from start to stop:
  ServerMixin        a model served over HTTP by its own program (imajev, JEV-27B-VL)
  SubprocessAdapter  any in-process adapter, run by `drjev.worker` under another environment's Python

Separate environments are needed because the models pin library versions that conflict with each other."""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from dataclasses import asdict
from pathlib import Path

from ..machine import Managed, load_profile
from .base import Adapter, Answer

ROOT = Path(__file__).resolve().parent.parent.parent      # the pipeline folder, put on the worker's import path


class _Keep(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def profile_of(adapter) -> dict:
    return adapter.cfg.machine if getattr(adapter, "cfg", None) is not None else load_profile(None)


def env_python(adapter) -> str:
    """The interpreter of this run's environment (`python:` in models.yaml), or the current one."""
    py = adapter.run.get("python")
    if not py:
        return "python"
    p = Path(py)
    if not p.is_absolute() and getattr(adapter, "cfg", None) is not None:
        p = adapter.cfg.base / p
    if not p.exists():
        raise RuntimeError(f"[{adapter.name}] environment not found: {p}. Create it with scripts/setup_env.sh (see envs/README.md).")
    return str(p)


class ServerMixin:
    """Start, verify and stop a model server described by the run's `server:` block."""

    managed = None

    def _ready(self, srv) -> bool:
        import requests
        try:
            return requests.get(srv.get("ready_url", self.url), timeout=3).status_code < 500
        except requests.RequestException:
            return False

    def start_server(self):
        srv = self.run.get("server")
        if not srv:
            return
        if self._ready(srv):                               # never borrow a server: it may hold another run's model
            raise RuntimeError(f"[{self.name}] a server is already answering at {srv.get('ready_url', self.url)}. Stop it first; "
                               "the pipeline starts one server per run so that each run is answered by its own model.")
        py = env_python(self)
        cmd = srv["cmd"].format_map(_Keep(python=py, venv=str(Path(py).parent.parent) if py != "python" else ""))
        cwd = srv.get("cwd")
        if cwd and getattr(self, "cfg", None) is not None and not os.path.isabs(cwd):
            cwd = str(self.cfg.base / cwd)
        if cwd and not Path(cwd).is_dir():
            raise RuntimeError(f"[{self.name}] server folder not found: {cwd}")
        print(f"[{self.name}] starting model server: {cmd}")
        self.srv = srv
        self.managed = Managed(cmd, self.name, profile_of(self), cwd=cwd, env=srv.get("env"))
        deadline = time.time() + float(srv.get("startup_seconds", 600))
        while not self._ready(srv):
            try:
                self.managed.check()
            except RuntimeError:
                self.stop_server()
                raise
            if time.time() > deadline:
                self.stop_server()
                raise RuntimeError(f"[{self.name}] server not ready after {srv.get('startup_seconds', 600)} s")
            time.sleep(1)

    def stop_server(self):
        if self.managed is None:
            return
        self.managed.stop()
        deadline = time.time() + 30
        while self._ready(self.srv) and time.time() < deadline:   # the port must be free before the next run starts
            time.sleep(0.5)
        still = self._ready(self.srv)
        self.managed = None
        if still:
            raise RuntimeError(f"[{self.name}] the model server did not stop; stop it by hand before the next run")


class SubprocessAdapter(Adapter):
    """Runs another adapter inside `python -m drjev.worker`, started with that model's own interpreter."""

    def __init__(self, run: dict, kind: str):
        super().__init__(run)
        self.kind = kind
        self.managed = None

    def load(self):
        py = env_python(self)
        env = {"PYTHONPATH": str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", ""), "PYTHONUNBUFFERED": "1"}
        self.managed = Managed([py, "-m", "drjev.worker"], self.name, profile_of(self), env=env, shell=False,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.lines: queue.Queue = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        cfg = getattr(self, "cfg", None)
        self._send({"adapter": self.kind, "run": {k: v for k, v in self.run.items() if k != "python"},
                    "config": str(cfg.path) if cfg is not None else None, "base": str(cfg.base) if cfg is not None else None})
        hello = self._receive(float(self.run.get("startup_seconds", 1800)))
        self.tested = bool(hello.get("tested"))

    def _reader(self):
        for line in self.managed.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def _send(self, obj):
        try:
            self.managed.proc.stdin.write((json.dumps(obj) + "\n").encode())
            self.managed.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            self.managed.check()
            raise

    def _receive(self, timeout: float) -> dict:
        deadline = time.time() + timeout
        while True:
            try:
                line = self.lines.get(timeout=1.0)
            except queue.Empty:
                self.managed.check()
                if time.time() > deadline:
                    raise RuntimeError(f"[{self.name}] no answer from the model process after {timeout:.0f} s")
                continue
            if line is None:
                self.managed.check()
                raise RuntimeError(f"[{self.name}] the model process closed its output")
            msg = json.loads(line)
            if msg.get("error"):
                raise RuntimeError(f"[{self.name}] error inside the model process:\n{msg['error']}")
            return msg

    def answer(self, image_path, questions):
        self._send({"image": image_path, "questions": [asdict(q) for q in questions]})
        msg = self._receive(float(self.run.get("request_seconds", 600)))
        return [Answer(a["p"], a["u"], a["ms"]) for a in msg["answers"]]

    def close(self):
        if self.managed is None:
            return
        try:
            self._send({"cmd": "close"})
            self.managed.proc.wait(timeout=20)
        except Exception:
            pass
        self.managed.stop()
        self.managed = None
