"""Create a self-contained demo workspace: synthetic data plus mock models, to prove the pipeline runs."""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from . import synth

HERE = Path(__file__).resolve().parent.parent


def make(target: Path, scale: int = 1, seed: int = 1) -> Path:
    target = Path(target).resolve()
    (target / "config").mkdir(parents=True, exist_ok=True)
    synth.make(target / "data" / "raw", scale=scale, seed=seed)
    for f in ("datasets.yaml", "questions.yaml"):
        shutil.copy(HERE / "config" / f, target / "config" / f)
    study = yaml.safe_load((HERE / "config" / "study.yaml").read_text())
    study["study"]["name"] = "SYNTHETIC DEMO"
    study.pop("machine", None)                             # the demo runs anywhere: generic machine profile
    study["splits"].update(eyepacs_calibration_images=500 * scale, eyepacs_internal_test_images=500 * scale,
                           efficiency_subsets=[100, 300], paraphrase_subset=150, local_recalibration=40)
    study["analysis"]["bootstrap"] = 300
    study["preprocess"].update(size=224, workers=4)
    ref, mod, gen = "mock_specialist", "mock_jev_ft", "mock_generative"
    for c in study["analysis"]["comparisons"]:
        c["model"] = {"imajev4b_ftB": mod, "imajev4b_ftA": "mock_jev_zs"}.get(c["model"], c["model"])
        c["reference"] = {"specialist": ref, "generative_ft": gen, "imajev4b_ftA": "mock_jev_zs"}.get(c["reference"], c["reference"])
    (target / "config" / "study.yaml").write_text(yaml.safe_dump(study, sort_keys=False))
    mock = lambda arm, **kw: dict(enabled=True, adapter="mock", arm=arm, synthetic=True, **kw)
    runs = {
        "mock_jev_zs": mock("Z", noise=1.6, sharpness=2.5, has_abstain=True),
        "mock_noabstain_zs": mock("Z", noise=1.8, sharpness=2.0, has_abstain=False),
        "mock_jev_ft_s0": mock("B", group=mod, seed=0, noise=0.65, sharpness=1.6, has_abstain=True, train={"train_size": "full"}),
        "mock_jev_ft_s1": mock("B", group=mod, seed=1, noise=0.65, sharpness=1.6, has_abstain=True, train={"train_size": "full"}),
        "mock_jev_ft_100": mock("B", seed=0, noise=1.1, sharpness=1.6, has_abstain=True, train={"train_size": 100}),
        "mock_jev_ft_300": mock("B", seed=0, noise=0.85, sharpness=1.6, has_abstain=True, train={"train_size": 300}),
        "mock_generative": mock("G", noise=0.7, sharpness=5.0, has_abstain=False),
        "mock_specialist": mock("S", noise=0.6, sharpness=2.2, has_abstain=False, train={"train_size": "full"}),
        "mock_specialist_100": mock("S", noise=1.4, sharpness=2.2, has_abstain=False, train={"train_size": 100}),
        "mock_specialist_300": mock("S", noise=0.95, sharpness=2.2, has_abstain=False, train={"train_size": 300}),
    }
    (target / "config" / "models.yaml").write_text(yaml.safe_dump({"runs": runs}, sort_keys=False))
    return target / "config" / "study.yaml"
