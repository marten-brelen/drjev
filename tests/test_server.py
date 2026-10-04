"""The pipeline starts one model server per run, checks which model answers, and stops it completely."""
import socket
import sys
import time
from pathlib import Path

import pytest
import requests

from drjev import questions
from drjev.adapters.imajev import ImajevHTTP

HERE = Path(__file__).resolve().parent
QFILE = HERE.parent / "config" / "questions.yaml"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_spec(port, served, expected):
    return {"name": "r", "url": f"http://127.0.0.1:{port}/v1/systemone", "model_name": expected,
            "server": {"cmd": f"{sys.executable} {HERE / 'stub_server.py'} {port} {served}", "ready_url": f"http://127.0.0.1:{port}/v1/models", "startup_seconds": 20}}


def answering(port) -> bool:
    try:
        return requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=1).ok
    except requests.RequestException:
        return False


def test_server_started_used_and_fully_stopped():
    port = free_port()
    a = ImajevHTTP(run_spec(port, "seed0", "seed0"))
    a.load()
    qs = questions.load(QFILE, 0)
    ans = {q.id: x for q, x in zip(qs, a.answer(str(QFILE), qs))}
    assert ans["q2_grade"].p == pytest.approx([0.6, 0.2, 0.1, 0.05, 0.05]) and ans["q2_grade"].u == pytest.approx(0.1)
    assert ans["q4_refer"].p[1] == pytest.approx((0.3 - 0.1) / 0.8) and ans["q4_refer"].u == pytest.approx(0.2)
    assert ans["q1_gradeable"].u is None and ans["q1_gradeable"].p == pytest.approx([0.1, 0.9])
    a.close()
    assert not answering(port)                                 # the shell AND the server it started are gone
    b = ImajevHTTP(run_spec(port, "seed1", "seed1"))            # so the next seed gets its own model on the same port
    b.load()
    b.answer(str(QFILE), qs)
    b.close()
    assert not answering(port)


def test_refuses_to_borrow_a_running_server_or_a_wrong_model():
    port = free_port()
    a = ImajevHTTP(run_spec(port, "seed0", "seed0"))
    a.load()
    try:
        with pytest.raises(RuntimeError, match="already answering"):
            ImajevHTTP(run_spec(port, "seed1", "seed1")).load()
    finally:
        a.close()
    c = ImajevHTTP(run_spec(port, "some-other-model", "seed2"))
    c.load()
    try:
        with pytest.raises(SystemExit, match="not 'seed2'"):
            c.answer(str(QFILE), questions.load(QFILE, 0))
    finally:
        c.close()
