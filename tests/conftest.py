"""Shared synthetic workspace: ingest, preprocess and split are run once for the whole test session."""
import pytest
import yaml

from drjev import demo, ingest, preprocess, splits
from drjev.config import Config

KEEP = ["mock_jev_zs", "mock_noabstain_zs", "mock_jev_ft_s0", "mock_jev_ft_s1", "mock_generative", "mock_specialist"]


@pytest.fixture(scope="session")
def ws(tmp_path_factory):
    root = tmp_path_factory.mktemp("demo")
    path = demo.make(root, scale=1, seed=3)
    mf = root / "config" / "models.yaml"
    m = yaml.safe_load(mf.read_text())
    m["runs"] = {k: v for k, v in m["runs"].items() if k in KEEP}
    mf.write_text(yaml.safe_dump(m, sort_keys=False))
    cfg = Config(path)
    ingest.run(cfg)
    preprocess.run(cfg)
    splits.run(cfg)
    return cfg


