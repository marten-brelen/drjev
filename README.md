# drjev: pipeline for the image decision model study on diabetic retinopathy grading

Datasets and models go in; tables, figures, a results summary and per-image predictions come out.
The pipeline implements the study protocol (`docs/dr-imagejev-study-protocol.md`).

## What has and has not been tested

| Part | Status |
|---|---|
| Ingest, preprocessing, duplicate detection, patient-level splits, protocol lock | Tested on synthetic datasets written in the real folder layouts |
| Metrics, calibration, clustered bootstrap, non-inferiority tests, tables, figures | Tested; QWK, AUROC and F1 agree with scikit-learn, interval widths agree with theory. An independent review found eight problems; all are fixed and have regression tests |
| imajev adapter and training-set export | Tested against imajev's own request, response and data-loading code (commit ccf586d4), without the model weights |
| Specialist classifier trainer and adapter | Smoke-tested on CPU with a small network on synthetic images |
| Real dataset layouts (`config/datasets.yaml`) | **Not tested**: column and folder names were written from memory; `drjev ingest` reports mismatches |
| NeoHorse, Jev-Omni, JEV-27B-VL, Visual-Jev, Glance adapters | **Not tested**: written from each model's documentation; use `drjev check-model` |
| imajev fine-tuning on a GPU; vision-tower LoRA patch | **Not tested**: scripts and patch are generated, nothing has been trained |
| Machine check, benchmark, memory protection, running a model in a separate environment | Tested with stand-in models on an ordinary (x86) Linux machine |
| Anything on the DGX Spark itself: `scripts/setup_env.sh`, the Arm / CUDA 13 installs, real timings | **Not tested**: no Spark was available while writing this |
| Generative baseline (arm G) | **Not implemented** |

Nothing in this repository has touched a real fundus photograph, real model weights or a DGX Spark.

## The DGX Spark (128 GB)

`config/study.yaml` selects the machine profile `config/machines/dgx-spark.yaml`. It changes how work is scheduled, never a result, and is not part of the protocol lock.

- **One model in memory at a time.** The CPU and GPU share one 128 GB pool. The pipeline starts each model, uses it, stops its whole process group, and waits for the memory to come back before the next.
- **Memory floor.** If available memory falls below 8 GB the model process is stopped and the run is reported as failed, instead of the machine freezing. Turn swap off (`sudo swapoff -a`); `drjev doctor` warns if it is on.
- **One environment per model.** The models pin conflicting library versions, and packages for Arm with CUDA 13 often need their own index or a source build. `scripts/setup_env.sh <name>` makes `envs/<name>`; see `envs/README.md`.
- **The 27B model is enabled.** Its 52 GB of weights fit in 128 GB. It needs a CUDA 13 build of vLLM, the least certain install; if it will not start it is skipped and listed.
- **Measure before planning.** `drjev benchmark` times every model on 200 non-test images and projects the hours for the whole study; `drjev benchmark --train` does the same for training. Speeds quoted by the model authors are from data-centre GPUs and will not hold here.

Order on a new machine:

```bash
bash scripts/setup_env.sh pipeline && source envs/pipeline/bin/activate
drjev doctor                         # machine, memory, swap, disk, GPU driver
bash scripts/setup_env.sh imajev     # then the other models, one at a time
drjev doctor                         # now also: does each environment see the GPU?
drjev ingest && drjev preprocess && drjev split
drjev check-model imajev4b_zs        # two images, printed answers
drjev benchmark                      # hours per model for the whole study -> work/benchmark_inference.md
drjev export-train && PROBE=1 bash work/train_scripts/imajev4b_ftB_s0.sh
drjev benchmark --train              # hours per training run -> work/benchmark_training.md
```

Decide the number of seeds and arms from those two benchmark files before `drjev lock`.

## Install

```bash
pip install -e .            # pipeline
pip install -e ".[train]"   # plus torch and torchvision for the specialist baseline
pip install -e ".[test]" && IMAJEV_DIR=../imajev pytest    # 40 tests, about 2 minutes
```

## Try it without any data

```bash
drjev demo /tmp/drjev-demo
drjev run --config /tmp/drjev-demo/config/study.yaml --lock
```

This draws about 3,800 synthetic images, runs mock models through every stage and writes
`/tmp/drjev-demo/results/`. Every table and figure from the demo is stamped SYNTHETIC.

## Real run

0. **Machine.** Follow "Order on a new machine" above as far as `drjev doctor` passing.
1. **Data.** Put each dataset under `data/raw/` as laid out in `config/datasets.yaml`.
2. **Check the reading.** `drjev ingest`, then read `work/ingest_report.md`. Fix names in `config/datasets.yaml` until counts match.
3. **Models.** Clone `mohit67890/imajev` next to this folder and download its weights. Pin `revision` for each run in `config/models.yaml`.
4. **Smoke-test each model.** `drjev check-model imajev4b_zs` (and each other run) prints answers for two non-test images.
5. **Zero-shot, up to the lock.** `drjev run` ingests, preprocesses, splits, predicts on the calibration splits and stops.
6. **Freeze.** Review `work/split_summary.csv`, `config/questions.yaml` and the `analysis` block of `config/study.yaml`. Then `drjev lock`.
7. **Train.**
   - `drjev export-train` writes imajev training files and one shell script per run under `work/train_scripts/`.
   - `drjev train-specialist --run specialist_s0 specialist_s1 specialist_s2` trains the baseline.
   - Set `enabled: true` for each trained run in `config/models.yaml`.
8. **Everything else.** `drjev run` predicts on the test sets (resuming where it stopped), calibrates, analyses and reports.

`drjev status` shows what has been done. A model that fails to load is skipped and listed at the end.

## Stages

| Command | Does | Writes |
|---|---|---|
| `doctor` | Checks the machine against its profile, the datasets and every model environment | `work/doctor_report.md` |
| `benchmark` | Times models (or training with `--train`) on non-test images and projects the study's cost | `work/benchmark_inference.md`, `work/benchmark_training.md` |
| `ingest` | Reads label files into one manifest; checks counts | `work/manifest_raw.csv`, `work/ingest_report.md` |
| `preprocess` | Crops to the fundus disc, pads square, resizes to 630 px, hashes | `work/images/`, `work/preprocess_errors.csv` |
| `split` | Patient-level splits, duplicate removal, fixed subsets | `work/manifest.csv`, `work/split_summary.csv`, `work/duplicates.csv` |
| `lock` | Freezes splits, question wording and analysis plan | `work/lock.json` |
| `predict` | Runs a model over splits; resumable | `work/preds/<run>/*.jsonl` |
| `calibrate` | Temperature per question and 90%-sensitivity thresholds, calibration splits only | `work/calibration/<run>.json` |
| `analyze` | All metrics, 95% patient-clustered bootstrap intervals, pre-specified tests with Holm adjustment | `results/metrics_long.csv`, `results/comparisons.csv` |
| `report` | Tables (csv and md), figures (png and pdf), summary, per-image predictions, run manifest | `results/` |

## Splits

| Split | Source | Use |
|---|---|---|
| `train`, `dev` | EyePACS Kaggle-train patients, 90% / 10% | Training; early stopping |
| `calibration` | 10,000 images from EyePACS Kaggle-test | Temperature and thresholds |
| `test_internal` | 10,000 images from EyePACS Kaggle-test | Locked test |
| `reserve` | Rest of EyePACS Kaggle-test | Untouched |
| `test` | Messidor-2, DDR official test part, APTOS, IDRiD, mBRSET | Locked external tests |
| `q3_train`, `q3_dev`, `q3_cal` | BRSET | Maculopathy question only |

Test splits cannot be read before `drjev lock`, and every read is logged in `work/test_access_log.jsonl`.

## Design choices worth knowing

- **Questions.** Five per image (gradeable, grade, maculopathy, refer, sight-threatening), each with three wordings in `config/questions.yaml`. Wordings 1 and 2 run on a fixed 2,000-image subset per test set.
- **"Unknown".** imajev has its own abstain output. Every other model gets "unknown" as an extra option, and its probability is split off afterwards.
- **Truth for referral and sight-threatening.** Grade-only everywhere; grade or maculopathy where maculopathy is labelled (`drjev/targets.py`).
- **Seeds.** Runs that share a `group` are scored seed by seed and averaged, inside every bootstrap sample too; the spread across seeds is reported alongside.
- **Paired tests.** Models are compared on the same bootstrap samples of patients, one-sided at 2.5%. Sensitivity is compared at the reference model's specificity. Primary tests are decided on the Holm-adjusted p-value; keep `bootstrap` at 2,000 or more, or they cannot pass.
- **Complete predictions only.** A model that has not predicted every image of a test set is left out of that set and listed in `results/incomplete.csv`.
- **One server per run.** The pipeline starts each imajev server itself, checks the model name in the first answer, and stops the whole process group afterwards. It refuses to use a server that is already running on the port.
- **Duplicates.** Found by difference hash and confirmed on a thumbnail; the copy in a test set is kept and the other dropped. Review `work/duplicates.csv`.

## Layout

```
config/     study.yaml, datasets.yaml, models.yaml, questions.yaml, machines/ (machine profiles)
scripts/    setup_env.sh (one environment per model)
envs/       the model environments and their recorded package versions
drjev/      the pipeline (adapters/ holds one file per model family)
patches/    imajev_vision_lora.patch (arm B)
tests/      unit tests and an end-to-end test on synthetic data
docs/       study protocol
examples/   output of the synthetic demo run, to show what the results look like
```
