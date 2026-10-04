"""Model worker: runs one adapter under the model's own Python environment.

Started by the pipeline as `<env python> -m drjev.worker`. Speaks one JSON object per line on the
pipes it was started with. Needs only the standard library plus whatever the model itself needs,
so the model environments do not have to install the pipeline's analysis dependencies.
Anything the model's libraries print goes to the terminal, never into the protocol."""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace


def main():
    out = os.fdopen(os.dup(1), "w", buffering=1)          # the protocol keeps the original pipe ...
    os.dup2(2, 1)                                          # ... and ordinary prints are sent to stderr
    sys.stdout = sys.stderr

    def reply(obj):
        out.write(json.dumps(obj) + "\n")
        out.flush()

    try:
        init = json.loads(sys.stdin.readline())
        from drjev import adapters
        from drjev.questions import Question
        cfg = None
        if init.get("config"):
            try:
                from drjev.config import Config
                cfg = Config(init["config"])
            except ImportError:                            # this environment lacks the pipeline's own dependencies: paths are enough
                cfg = SimpleNamespace(base=Path(init["base"]), machine={})
        adapter = adapters.make(dict(init["run"], adapter=init["adapter"]), cfg, in_process=True)
        adapter.load()
        reply({"ok": True, "tested": adapter.tested, "pid": os.getpid()})
    except Exception:
        reply({"error": traceback.format_exc()})
        return 1
    for line in sys.stdin:
        msg = json.loads(line)
        if msg.get("cmd") == "close":
            break
        try:
            qs = [Question(q["id"], q["kind"], q["instruction"], [tuple(o) for o in q["options"]], q["allow_unknown"], q["variant"], q["meta"])
                  for q in msg["questions"]]
            reply({"answers": [{"p": a.p, "u": a.u, "ms": a.ms} for a in adapter.answer(msg["image"], qs)]})
        except Exception:
            reply({"error": traceback.format_exc()})
    adapter.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
