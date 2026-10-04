"""End-to-end run on synthetic data with mock models: every stage, then independent checks of the outputs."""
import json

import numpy as np
import pandas as pd
import pytest
import yaml
from sklearn.metrics import cohen_kappa_score, roc_auc_score

from drjev import analyze, calibrate, demo, ingest, lock, predict, preprocess, report, splits
from drjev.config import Config

def test_data_stages(ws):
    cfg = ws
    m = splits.load_manifest(cfg, include_excluded=True)
    e = m[m["dataset"] == "eyepacs"]
    assert (e.groupby("patient_id")["split"].nunique() == 1).all()                 # no patient in two splits
    assert set(e["split"]) == {"train", "dev", "calibration", "test_internal", "reserve"}
    assert set(m.loc[m["dataset"] == "ddr", "split"]) == {"test", "unused"}          # only DDR's official test part is tested
    assert (m.loc[(m["dataset"] == "ddr") & (m["official_split"] == "test"), "split"] == "test").all()
    dup = m[m["excluded"] == "duplicate"]
    assert set(dup["dup_of"]) == {"aptos:dupdupdup000", "aptos:dupdupdup001", "aptos:dupdupdup002"}   # the planted copies, nothing else
    assert (dup["split"] == "train").all()                                           # the training copy is dropped, the test copy kept
    assert "corrupt000000" in (cfg.work / "preprocess_errors.csv").read_text()       # unreadable file reported
    assert "1 image files missing" in (cfg.work / "ingest_report.md").read_text()    # label without an image reported
    assert m[m["eff_100"]]["eff_300"].all() and (m[m["eff_300"]]["split"] == "train").all()
    un = m[(m["dataset"] == "ddr") & (m["gradable"] == 0)]
    assert len(un) and un["grade"].isna().all()                                      # DDR class 5 became "ungradeable", not a grade
    assert m.loc[m["dataset"] == "mbrset", "maculopathy"].notna().any()              # "yes"/"no" labels were read


def test_test_sets_are_locked_out(ws):
    cfg = ws
    if cfg.lock_file.exists():
        pytest.skip("already locked by an earlier test")
    with pytest.raises(SystemExit, match="locked out"):
        predict.run(cfg, "mock_jev_zs", splits=("test",), datasets=["idrid"])
    assert not (cfg.preds_dir / "mock_jev_zs").exists()


def test_full_run_and_independent_recomputation(ws):
    cfg = ws
    for r in cfg.enabled_runs():
        predict.run(cfg, r, splits=("calibration", "q3_cal"))
    lock.create(cfg, "test")
    for r in cfg.enabled_runs():
        predict.run(cfg, r, splits=("test", "test_internal"), variants=(0, 1, 2) if r == "mock_jev_zs" else (0,))
    calibrate.run(cfg, cfg.enabled_runs())
    analyze.run(cfg, bootstrap=60)
    report.run(cfg)
    res = cfg.results
    long = pd.read_csv(res / "metrics_long.csv")
    cal = long[long["calibrated"]]

    def value(unit, ds, metric):
        return float(cal[(cal["unit"] == unit) & (cal["dataset"] == ds) & (cal["metric"] == metric)]["value"].iloc[0])

    # 1. recompute headline metrics from the released per-image file with scikit-learn
    pi = pd.read_csv(res / "per_image" / "mock_jev_zs.csv.gz")
    for ds in ("ddr", "messidor2", "eyepacs"):
        d = pi[(pi["dataset"] == ds) & pi["grade"].notna() & (pi["gradable"] != 0)]
        pred = d[[f"pg{k}" for k in range(5)]].to_numpy().argmax(1)
        assert value("mock_jev_zs", ds, "qwk") == pytest.approx(cohen_kappa_score(d["grade"].astype(int), pred, weights="quadratic"), abs=5e-4)
        assert value("mock_jev_zs", ds, "ref_auroc") == pytest.approx(roc_auc_score(d["grade"] >= 2, d["pref"]), abs=5e-4)
        assert value("mock_jev_zs", ds, "acc") == pytest.approx((pred == d["grade"]).mean(), abs=5e-4)
    # full clinical definition on a dataset with maculopathy labels
    d = pi[(pi["dataset"] == "messidor2") & pi["grade"].notna() & (pi["gradable"] != 0) & pi["maculopathy"].notna()]
    truth = (d["grade"] >= 3) | (d["maculopathy"] == 1)
    assert value("mock_jev_zs", "messidor2", "stfull_auroc_direct") == pytest.approx(roc_auc_score(truth, d["pst"]), abs=5e-4)

    # 2. the confidence interval brackets the estimate; the pooled unit holds both seeds
    q = cal[(cal["metric"] == "qwk") & (cal["dataset"] == "ddr")].set_index("unit")
    assert ((q["ci_low"] <= q["value"]) & (q["value"] <= q["ci_high"])).all()
    assert int(q.loc["mock_jev_ft", "n_seeds"]) == 2 and not np.isnan(q.loc["mock_jev_ft", "seed_sd"])

    # 3. the mock models behave as configured: fine-tuned beats zero-shot; the over-confident "generative" mock is worse calibrated than the fine-tuned one before scaling
    assert value("mock_jev_ft", "ddr", "qwk") > value("mock_jev_zs", "ddr", "qwk") + 0.1
    raw = long[~long["calibrated"] & (long["metric"] == "ece_grade") & (long["dataset"] == "eyepacs")].set_index("unit")["value"]
    assert raw["mock_generative"] > raw["mock_jev_ft"] + 0.1
    assert value("mock_generative", "eyepacs", "ece_grade") < raw["mock_generative"]          # temperature scaling helped
    t = json.loads((cfg.calib_dir / "mock_generative.json").read_text())["temperature"]["q2_grade"]
    assert t > 1.3                                                                            # and found it over-confident

    # 4. thresholds were set for 90% sensitivity on the calibration split, without reading a test split
    c = json.loads((cfg.calib_dir / "mock_specialist.json").read_text())
    from drjev import frames
    fr = frames.build(cfg, splits.load_manifest(cfg), "mock_specialist", "eyepacs", "calibration")
    ev = fr["grade"].notna() & (fr["gradable"] != 0)
    sens = (fr.loc[ev & (fr["grade"] >= 2), "pref"] >= c["thresholds"]["ref_direct"]).mean()
    assert 0.90 <= sens < 0.93

    # 5. a model without its own "unknown" still reports one (explicit option), and abstains on ungradeable images
    assert value("mock_noabstain_zs", "ddr", "abst_rate_ungradable") > 0.7
    assert value("mock_noabstain_zs", "ddr", "false_abst_rate") < 0.1

    # 6. pre-specified tests ran, Holm p-values are not smaller than raw ones, matched-specificity test present
    comp = pd.read_csv(res / "comparisons.csv")
    ok = comp[comp["status"] == "ok"]
    assert {"H2_qwk", "H2_ref_sens", "H2_st_sens", "H3_ece"} <= set(ok["id"])
    p = ok[ok["primary"]]
    assert (p["p_holm"] >= p["p_value"] - 1e-12).all()
    assert (ok.loc[ok["id"] == "H2_st_sens", "dataset"] == "pooled_external").all()

    # 7. prompt sensitivity only for the model that was run with three wordings
    ps = pd.read_csv(res / "prompt_sensitivity.csv")
    assert set(ps["unit"]) == {"mock_jev_zs"} and (ps["n_wordings"] == 3).all()

    # 8. outputs exist and carry the synthetic stamp; test-set reads were logged
    for name in ("table0_datasets", "table1_zero_shot", "table2_main", "table3_abstention", "table3b_clinical", "table3c_coherence", "hypothesis_tests"):
        assert (res / "tables" / f"{name}.csv").exists()
        assert "SYNTHETIC" in (res / "tables" / f"{name}.md").read_text()
    for name in ("fig1_reliability", "fig2_risk_coverage", "figS1_zero_shot_qwk", "figS2_confusion"):
        assert (res / "figures" / f"{name}.pdf").stat().st_size > 5000
    man = json.loads((res / "run_manifest.json").read_text())
    assert man["synthetic"] and man["lock"]["manifest_sha256"] and len(man["test_set_reads"]) > 5

    # 9. the lock notices a change to a frozen file
    qf = cfg.questions_file
    original = qf.read_text()
    qf.write_text(original.replace("Grade the severity", "Please grade the severity"))
    with pytest.raises(SystemExit, match="changed after the lock"):
        lock.check(cfg)
    qf.write_text(original)
    lock.check(cfg)


def test_training_export_targets(ws):
    from drjev import export_train
    cfg = ws
    cfg.runs["ft_demo"] = dict(enabled=False, arm="A", seed=0, adapter="imajev_http", train=dict(recipe="imajev_lora", train_size=100))
    mf = export_train.run(cfg, "ft_demo", imajev_dir="does-not-exist")
    recs = [json.loads(x) for x in mf.read_text().splitlines()]
    man = splits.load_manifest(cfg).set_index("path")
    assert {r["partition"] for r in recs} == {"train", "dev"}
    for r in recs:
        row = man.loc[r["images"][0]["image"]]
        assert row["split"] in ("train", "dev", "q3_train", "q3_dev")            # nothing from calibration or any test split
        t = r["targets"]
        if row["gradable"] == 0:
            assert t["q1_gradeable"] is False and t["q2_grade"] is None and t["q4_refer"] is None
        elif "q2_grade" in t:
            assert t["q2_grade"] == int(row["grade"]) and t["q4_refer"] == (row["grade"] >= 2) and t["q5_sight"] == (row["grade"] >= 3)
    tr = [r for r in recs if r["partition"] == "train" and r["source"] == "eyepacs"]
    assert len({r["images"][0]["image"] for r in tr}) <= 100                     # the 100-image subset, repeated for balance


def test_analysis_refuses_changed_plan_and_incomplete_models(ws):
    cfg = ws
    study = cfg.path.read_text()
    # 1. loosening a margin after the lock is refused by the analysis itself, not only by prediction
    cfg.path.write_text(study.replace("margin: 0.05", "margin: 0.5"))
    with pytest.raises(SystemExit, match="changed after the lock"):
        analyze.run(Config(cfg.path), bootstrap=30)
    cfg.path.write_text(study)

    # 2. a model with missing predictions is left out of that dataset and of the pooled analysis, and reported
    f = predict.pred_file(cfg, "mock_generative", "idrid", "test", 0)
    lines = f.read_text().splitlines()
    f.write_text("\n".join(lines[: len(lines) // 2]) + "\n")
    analyze.run(cfg, bootstrap=30)
    long = pd.read_csv(cfg.results / "metrics_long.csv")
    gen = long[long["unit"] == "mock_generative"]
    assert "idrid" not in set(gen["dataset"]) and "pooled_external" not in set(gen["dataset"]) and "ddr" in set(gen["dataset"])
    inc = pd.read_csv(cfg.results / "incomplete.csv")
    assert list(inc["unit"]) == ["mock_generative"] and list(inc["dataset"]) == ["idrid"]
    assert "pooled_external" in set(long[long["unit"] == "mock_specialist"]["dataset"])

    # 3. the pooled two-seed unit reports the per-seed image count, and primary decisions come from the Holm p-value
    n = long[(long["unit"] == "mock_jev_ft") & (long["dataset"] == "ddr") & (long["metric"] == "n") & long["calibrated"]]["value"].iloc[0]
    assert n == len(splits.load_manifest(cfg).query("dataset == 'ddr' and split == 'test'"))
    comp = pd.read_csv(cfg.results / "comparisons.csv")
    p = comp[comp["primary"] & (comp["status"] == "ok")]
    assert ((p["passed"].astype(str) == "True") == (p["p_holm"] < 0.025)).all()
    report.run(cfg)
    assert "mock_generative on idrid" in (cfg.results / "summary.md").read_text()
