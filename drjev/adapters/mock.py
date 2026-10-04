"""A stand-in model for testing the pipeline. It reads the answer from the manifest and adds noise,
so its "performance" is set by its parameters and means nothing. Runs that use it are stamped
SYNTHETIC in every table and figure."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from ..questions import UNKNOWN_KEY
from .base import Adapter


def _sig(x):
    return 1 / (1 + np.exp(-x))


class MockAdapter(Adapter):
    tested = True

    def load(self):
        from ..splits import load_manifest
        m = load_manifest(self.cfg)
        self.truth = {r.path: (r.grade, r.gradable, r.maculopathy, r.dataset) for r in m.itertuples()}
        self.noise = float(self.run.get("noise", 0.7))          # grading error (standard deviation, in grades)
        self.sharp = float(self.run.get("sharpness", 2.5))      # >1.5 or so is over-confident
        self.shift = float(self.run.get("external_shift", 1.3))  # extra noise away from EyePACS
        self.seed = int(self.run.get("seed", 0))
        self.has_abstain = bool(self.run.get("has_abstain", True))
        if self.run.get("noisy"):
            print("Loading checkpoint shards: 100%|##########| 2/2")   # what model libraries print while loading

    def _rng(self, *parts):
        h = hashlib.sha256("|".join(str(p) for p in (self.seed, *parts)).encode()).digest()
        return np.random.default_rng(int.from_bytes(h[:8], "little"))

    def _score(self, image_path, q):
        grade, gradable, mac, dataset = self.truth[image_path]
        r = self._rng(self.name.split("_s")[0], image_path)     # per-image latent, shared by all questions
        ok = gradable != 0
        noise = self.noise * (1.0 if dataset == "eyepacs" else self.shift)
        s = (grade if pd.notna(grade) else r.uniform(0, 4)) + r.normal(0, noise)
        quality = (2.0 if ok else -2.0) + r.normal(0, 1.0)
        macv = (mac if pd.notna(mac) else float(r.random() < 0.1))
        mac_logit = 2.2 * (2 * macv - 1) + r.normal(0, 1.3)
        rq = self._rng(self.name, image_path, q.id, q.variant)   # small per-question, per-wording jitter
        s = s + rq.normal(0, 0.15)
        if q.id == "q1_gradeable":
            p_yes = _sig(1.5 * quality)
            return [1 - p_yes, p_yes], None
        u = float(_sig(-1.6 * quality - 0.5)) if self.has_abstain or q.keys[-1] == UNKNOWN_KEY else None
        if q.id == "q2_grade":
            z = -self.sharp * (np.arange(5) - s) ** 2
            p = np.exp(z - z.max())
        elif q.id == "q3_maculopathy":
            y = _sig(self.sharp * 0.6 * mac_logit)
            p = np.array([1 - y, y])
        else:
            cut = 1.5 if q.id == "q4_refer" else 2.5
            y = _sig(self.sharp * 1.1 * (s - cut) + rq.normal(0, 0.4))
            p = np.array([1 - y, y])
        p = p / p.sum()
        if q.keys[-1] == UNKNOWN_KEY:                           # model without its own abstain output
            return list(p * (1 - u)) + [u], None
        return list(p), u
