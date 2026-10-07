# Instructions for Claude Code

This repository holds a research study and the program that runs it. Read this file first, then `README.md`, then `docs/dr-imagejev-study-protocol.md`.

## What this project is

A study of whether image decision models ("Jev-style" models such as imajev-4b: image + typed question + fixed options in, probabilities out, no generated text) can grade diabetic retinopathy from fundus photographs as well as a specialist classifier, with usable calibration and abstention.

- The protocol (`docs/dr-imagejev-study-protocol.md`, v0.5) defines the study: questions, datasets, splits, arms, statistics.
- The `drjev` Python package is the pipeline: datasets and models go in; tables, figures, a summary and per-image predictions come out.
- The owner is a clinician, not a software engineer. Explain what you did and found in plain language, and say clearly what was and was not checked.

## Current state: the pipeline is already written. Do not rewrite it.

Version 0.2.0 is complete and passes its 40 tests. Your job is to make it work on real data, real models and the real machine, not to start again.

Everything so far was built and tested on an ordinary x86 Linux sandbox with **synthetic images and mock models**. Nothing has touched a real fundus photograph, real model weights, a GPU or a DGX Spark. The table "What has and has not been tested" in `README.md` is the authoritative list.

The target machine is one **NVIDIA DGX Spark, 128 GB** (Arm aarch64, CUDA 13, CPU and GPU share one memory pool, DGX OS / Ubuntu 24.04, Python 3.12). Settings for it are in `config/machines/dgx-spark.yaml`.

## Before changing anything

```bash
bash scripts/setup_env.sh pipeline && source envs/pipeline/bin/activate
pip install -e ".[test,train]"
pytest                      # 40 tests, about 2 minutes; all must pass
drjev demo /tmp/drjev-demo && drjev run --config /tmp/drjev-demo/config/study.yaml --lock   # full run on synthetic data
```

If the tests or the demo fail on the Spark, fix that first and report what differed from x86.

## Work to do, in this order

Stop and report after each numbered step. Do not run ahead to the next one if a step fails.

1. **Machine check.** `drjev doctor`. Resolve everything it flags (swap on, low disk, GPU not visible).
2. **Model environments.** `bash scripts/setup_env.sh <name>` for one model at a time, starting with `imajev`, then `specialist`, then the others (`envs/README.md` lists them). This script has never been run; expect to adjust package versions for Arm and CUDA 13. PyTorch comes from `https://download.pytorch.org/whl/cu130`. Record what you changed in `scripts/setup_env.sh` itself so the install is repeatable.
3. **Datasets.** The owner places the downloads under `data/raw/`. Run `drjev ingest` and read `work/ingest_report.md`. The folder and column names in `config/datasets.yaml` were written from memory: correct them until the image counts match `expected_images`. Then `drjev preprocess` and `drjev split`; review `work/split_summary.csv` and `work/duplicates.csv`.
4. **Each model answers.** `drjev check-model <run>` for every enabled run in `config/models.yaml`. Only the imajev adapter was checked against the model's real code. The adapters in `drjev/adapters/others.py` (NeoHorse, Jev-Omni, JEV-27B-VL, Visual-Jev, Glance) were written from model cards and are untested: fix them against each model's actual interface. A model that cannot be made to run is disabled and reported, not worked around.
5. **Timing.** `drjev benchmark`, then `drjev export-train`, `PROBE=1 bash work/train_scripts/imajev4b_ftB_s0.sh` and `drjev benchmark --train`. Give the owner `work/benchmark_inference.md` and `work/benchmark_training.md`. The owner decides from these how many seeds and arms to run.
6. **Arm B patch.** `patches/imajev_vision_lora.patch` adds LoRA to imajev's vision tower (its trainer only adapts the language layers). It is untested. Apply it to the imajev clone at the commit noted in the README (`ccf586d4`), confirm with the probe run that vision-tower parameters are trainable, and fix it if not.
7. **Zero-shot run up to the lock.** `drjev run` stops by itself before any test split is read.
8. **Lock.** Only the owner decides to lock (see the rules below).
9. **Training, test-set predictions, analysis, report.** As in "Real run" in `README.md`.

Not built, and not to be built without the owner asking: the generative baseline (arm G), a RETFound baseline, a container image, and the adapter for the hosted OpenAI Decisions API (arm O, protocol sections 4.3, 5.4 and 6.8). Arm O is proposed in the protocol but not yet agreed.

## Rules that protect the study

These are requirements of the protocol, not preferences. Breaking them invalidates the results.

- **Never read a test split before the lock.** Test splits are `test` and `test_internal`; the `reserve` split is held back and is not read at all. The code enforces the lock for the test splits (`drjev/lock.py`); do not bypass, weaken or stub out the check, and do not open test images or their labels by any other route (notebooks, ad-hoc scripts, looking at files in `work/images/`). Development uses `train`, `dev`, `calibration` and the `q3_*` splits only.
- **Never run `drjev lock` or `drjev run --lock` on the real study yourself** (the synthetic demo is fine), and never delete or edit `work/lock.json` or `work/test_access_log.jsonl`. Ask the owner.
- **After the lock, do not change** `config/questions.yaml`, the `splits` or `analysis` blocks of `config/study.yaml`, or the split manifest. If a change is unavoidable, stop and tell the owner: it is a protocol deviation that must be written up.
- **Thresholds and temperatures come from calibration splits only.** Never tune anything on a test split.
- **Ground-truth rules live in one place**, `drjev/targets.py`. Do not re-derive labels elsewhere.
- **Do not change a statistical method, a metric definition, a margin or a pre-specified comparison** to make a result look better or a test pass. Bugs in them are fixed with a regression test and reported to the owner.
- **No fabricated or placeholder numbers.** If something did not run, say so. Output from synthetic data must keep its SYNTHETIC stamp.
- **Data stays on the machine.** Do not upload images, labels or per-image predictions anywhere. The single exception is arm O: a dataset's images may be sent to the OpenAI Decisions API only if section 5.4 of the protocol records the owner's clearance for that dataset and gate G-API (section 10) has been passed. Until then only synthetic images may be sent to it. Never send a label, a patient identifier or a file name, and never send images to any other hosted service. Never commit `data/`, `work/`, `results/`, model weights or credentials (`.gitignore` covers the folders). mBRSET and BRSET are under a PhysioNet credentialed licence.
- **One model in memory at a time.** The pipeline starts and stops each model itself; do not start model servers by hand alongside it.

## Decisions that belong to the owner

Section 15 of the protocol lists the open items. Items marked **[CONFIRM]** are the owner's to decide: ask, do not choose. Items marked **[VERIFY]** are facts you can check and report. The main open decisions:

- Referable = moderate NPDR or worse, or any maculopathy (proposed, not confirmed)
- Maculopathy wording and distance criterion
- How the maculopathy question is trained (protocol section 6.5; BRSET proposed)
- Direct or derived answer as primary for referral and sight-threatening
- Non-inferiority margins (currently placeholders: QWK 0.05, sensitivity 5 points)
- Whether to build the generative baseline and RETFound, or drop hypothesis H3
- Whether to include the hosted OpenAI Decisions API (arm O) at all, and which datasets may be sent to it (protocol section 5.4)
- Split sizes, and the pooled sight-threatening test
- The order of cuts if the full plan does not fit one machine (protocol section 13.1)

Already confirmed: sight-threatening = any maculopathy, or severe NPDR, or PDR. The maculopathy question is included.

## Working conventions

- Python 3.12, standard library plus the dependencies in `pyproject.toml`. Keep the pipeline a command-line package; do not turn it into an application or add a web interface.
- Settings live in `config/`; code reads them through `drjev/config.py`. Machine-specific settings go in `config/machines/`, never in the study settings, so they cannot change a result.
- Every bug fix gets a test in `tests/`. Run `pytest` before every commit.
- When behaviour changes, update `README.md` (including its tested / not tested table) in the same commit. When the study design changes, update the protocol, raise its version number, and tick or add the item in section 15.
- Commit small, with messages that say what changed and why. Work on a branch and open a pull request for anything that touches `drjev/metrics.py`, `drjev/analyze.py`, `drjev/calibrate.py`, `drjev/targets.py`, `drjev/splits.py` or `drjev/lock.py`.

## Where things are

| Path | What |
|---|---|
| `docs/dr-imagejev-study-protocol.md` | The study protocol |
| `README.md` | How to install and run; what is tested |
| `config/` | Study, dataset, model, question and machine settings |
| `drjev/` | The pipeline; `drjev/adapters/` has one file per model family |
| `scripts/setup_env.sh`, `envs/README.md` | One software environment per model |
| `patches/` | The vision-tower LoRA patch for arm B |
| `tests/` | Unit tests and an end-to-end test on synthetic data |
| `examples/demo-results/` | Output of a synthetic run, to show what results look like |
