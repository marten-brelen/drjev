"""imajev over its documented HTTP interface (POST /v1/systemone, multipart: `request` + `image`).

Written against github.com/mohit67890/imajev at commit ccf586d4 (1 Oct 2026):
  noul   -> {"noul": P(yes) + unknown/2, "unknown_probability": u}
  score  -> {"probabilities": {"0": p0, ...} (given that it answers), "unknown_probability": u}
  choice -> {"probabilities": {option: p}, "unknown_probability": u}
Serve it WITHOUT --calibration and with --rotations 1: this pipeline fits its own temperature.
"""
from __future__ import annotations

import json
import time

import requests

from ..questions import Question
from .base import Adapter
from .proc import ServerMixin


def build_request(qs: list[Question]) -> dict:
    out = {}
    for q in qs:
        if q.kind == "noul":
            no, yes = q.options[0][1], q.options[1][1]
            out[q.id] = {"type": "noul", "instructions": q.instruction, "criteria": {"true": yes, "false": no}}
        elif q.kind == "score":
            out[q.id] = {"type": "score", "instructions": q.instruction, "criteria": [d for _, d in q.options]}
        else:
            out[q.id] = {"type": "choice", "instructions": q.instruction, "criteria": {k: d for k, d in q.options}}
    return {"state": {}, "questions": out}


def parse_answer(q: Question, a: dict):
    u = float(a.get("unknown_probability", 0.0))
    if q.kind == "noul":
        yes_mass = float(a["noul"]) - 0.5 * u            # the server adds half the unknown mass to P(yes)
        p_yes = min(1.0, max(0.0, yes_mass / (1 - u))) if u < 1 else 0.5
        return [1 - p_yes, p_yes], u
    probs = a["probabilities"]
    if q.kind == "score":
        return [float(probs[str(i)]) for i in range(len(q.options))], u
    return [float(probs[k]) for k in q.keys], u


class ImajevHTTP(ServerMixin, Adapter):
    has_abstain = True
    tested = True
    expect = None
    checked = False

    def load(self):
        self.url = self.run["url"]
        self.session = requests.Session()
        self.expect = self.run.get("model_name")           # the server reports its --model-name in every response
        self.checked = False
        self.start_server()

    def close(self):
        self.stop_server()

    def _score_many(self, image_path, qs):
        body = json.dumps(build_request(qs))
        last = None
        if self.managed is not None:
            self.managed.check()                           # stopped for memory, or crashed: say so instead of timing out
        for attempt in range(3):
            try:
                with open(image_path, "rb") as f:
                    r = self.session.post(self.url, files={"image": f}, data={"request": body}, timeout=300)
                if r.status_code == 200:
                    body_ = r.json()
                    if self.expect and not self.checked:
                        if body_.get("model") != self.expect:
                            raise SystemExit(f"[{self.name}] the server at {self.url} is serving '{body_.get('model')}', not '{self.expect}'. "
                                             "Predictions would be attributed to the wrong model.")
                        self.checked = True
                    ans = body_["answers"]
                    return [parse_answer(q, ans[q.id]) for q in qs]
                last = f"HTTP {r.status_code}: {r.text[:300]}"
                if r.status_code < 500:
                    break
            except requests.RequestException as e:
                last = repr(e)
            time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"[{self.name}] request failed for {image_path}: {last}")
