"""Protocol lock: freezes the split manifest, the question wording and the analysis plan.

Test splits can only be read after the lock exists, and every read is logged."""
from __future__ import annotations

import datetime
import json

from .config import TEST_SPLITS


def create(cfg, note: str = "") -> dict:
    if cfg.lock_file.exists():
        raise SystemExit(f"Already locked ({cfg.lock_file}). A lock is created once; see README for what a re-lock implies.")
    if not cfg.manifest.exists():
        raise SystemExit("No split manifest yet: run `drjev split` first.")
    payload = dict(cfg.frozen_payload(), locked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), note=note)
    cfg.lock_file.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"lock: protocol frozen -> {cfg.lock_file}")
    return payload


def check(cfg) -> dict:
    """Raises if the lock is missing or if anything frozen has changed since."""
    if not cfg.lock_file.exists():
        raise SystemExit("Test splits are locked out until the protocol is frozen. Run `drjev lock` when the "
                         "questions, splits and analysis plan are final.")
    lock = json.loads(cfg.lock_file.read_text())
    now = cfg.frozen_payload()
    changed = [k for k in now if lock.get(k) != now[k]]
    if changed:
        raise SystemExit("Frozen files changed after the lock: " + ", ".join(changed) +
                         ". Restore them, or document the deviation and re-lock.")
    return lock


def guard(cfg, split: str, run_name: str, dataset: str, n_images: int):
    if split in TEST_SPLITS:
        check(cfg)
        with open(cfg.work / "test_access_log.jsonl", "a") as f:
            f.write(json.dumps({"time": datetime.datetime.now(datetime.timezone.utc).isoformat(), "run": run_name,
                                "dataset": dataset, "split": split, "images": n_images}) + "\n")
