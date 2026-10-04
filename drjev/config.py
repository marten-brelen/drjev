"""Configuration loading. One Config object carries the study, dataset, question and model files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

TEST_SPLITS = ("test", "test_internal")  # splits that may only be read after `drjev lock`


class Config:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.base = self.path.parent.parent if self.path.parent.name == "config" else self.path.parent
        self.study = yaml.safe_load(self.path.read_text())
        self.seed = int(self.study["study"]["seed"])
        p = self.study["paths"]
        self.raw = self._abs(p["raw"])
        self.work = self._abs(p["work"])
        self.results = self._abs(p["results"])
        self.datasets_file = self._abs(self.study["datasets_file"])
        self.questions_file = self._abs(self.study["questions_file"])
        self.models_file = self._abs(self.study["models_file"])
        self.datasets = yaml.safe_load(self.datasets_file.read_text())
        self.models = yaml.safe_load(self.models_file.read_text())
        self.runs = self.models.get("runs", {}) or {}
        self.splits = self.study["splits"]
        self.analysis = self.study["analysis"]
        self.preprocess = self.study["preprocess"]
        from .machine import load_profile
        mp = self.study.get("machine")
        self.machine_file = self._abs(mp) if mp else None
        self.machine = load_profile(self.machine_file)   # scheduling only; never part of the lock

    def _abs(self, p) -> Path:
        p = Path(p)
        return p if p.is_absolute() else (self.base / p)

    # ---- well-known files ----
    @property
    def manifest_raw(self): return self.work / "manifest_raw.csv"
    @property
    def manifest_proc(self): return self.work / "manifest_proc.csv"
    @property
    def manifest(self): return self.work / "manifest.csv"
    @property
    def lock_file(self): return self.work / "lock.json"
    @property
    def preds_dir(self): return self.work / "preds"
    @property
    def calib_dir(self): return self.work / "calibration"

    def run(self, name: str) -> dict:
        if name not in self.runs:
            raise KeyError(f"Run '{name}' is not defined in {self.models_file}")
        run = dict(self.runs[name], name=name)
        tpl = self.models.get("imajev_finetuned_server")
        if tpl and "server" not in run and (run.get("train") or {}).get("recipe") == "imajev_lora" and run.get("url"):
            port = run["url"].rsplit(":", 1)[-1].split("/")[0]   # a fine-tuned imajev adapter is served from the trainer's "best" folder
            keep = type("Keep", (dict,), {"__missing__": lambda self, k: "{" + k + "}"})   # {python} is filled when the server starts
            fill = lambda v: v.format_map(keep(name=name, port=port, adapter=f"runs/drjev-{name}/best")) if isinstance(v, str) else v
            run["server"] = {k: fill(v) for k, v in tpl.items()}
            run.setdefault("model_name", name)             # checked against what the server says it is serving
        return run

    def enabled_runs(self) -> list[str]:
        return [n for n, r in self.runs.items() if r.get("enabled")]

    def units(self) -> dict[str, list[str]]:
        """Analysis units: a group of seeds is analysed as one unit; an ungrouped run is its own unit."""
        out: dict[str, list[str]] = {}
        for n, r in self.runs.items():
            out.setdefault(r.get("group") or n, []).append(n)
        return out

    def frozen_payload(self) -> dict:
        """What `drjev lock` freezes: splits, questions and the analysis plan."""
        return {
            "manifest_sha256": sha256_file(self.manifest) if self.manifest.exists() else None,
            "questions_sha256": sha256_file(self.questions_file),
            "analysis_sha256": sha256_text(json.dumps(self.analysis, sort_keys=True)),
            "splits_sha256": sha256_text(json.dumps(self.splits, sort_keys=True)),
        }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
