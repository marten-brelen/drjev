"""Adapter registry. Imports are lazy so that a model's dependencies are needed only when it is used."""
from importlib import import_module

REGISTRY = {
    "mock": ("mock", "MockAdapter"),
    "imajev_http": ("imajev", "ImajevHTTP"),
    "neohorse": ("others", "NeoHorse"),
    "jev_omni": ("others", "JevOmni"),
    "jev27b_http": ("others", "Jev27bHTTP"),
    "visual_jev": ("others", "VisualJev"),
    "glance": ("others", "GlanceAdapter"),
    "specialist": ("specialist", "SpecialistAdapter"),
}


SERVED = {"imajev_http", "jev27b_http"}     # these have their own server process; `python:` names the server's environment


def make(run: dict, cfg=None, in_process: bool = False):
    kind = run["adapter"]
    if kind not in REGISTRY:
        raise KeyError(f"Unknown adapter '{kind}'. Known: {sorted(REGISTRY)}")
    if run.get("python") and kind not in SERVED and not in_process:
        from .proc import SubprocessAdapter               # the model lives in its own environment
        a = SubprocessAdapter(run, kind)
    else:
        mod, cls = REGISTRY[kind]
        a = getattr(import_module(f"{__name__}.{mod}"), cls)(run)
    a.cfg = cfg
    return a
