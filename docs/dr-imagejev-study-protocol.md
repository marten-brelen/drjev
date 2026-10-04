# Study protocol: image decision models ("Jev-style") for diabetic retinopathy grading

**Version:** 0.4 (draft for implementation planning)
**Changes in 0.4:** hardware fixed as one NVIDIA DGX Spark, 128 GB (section 13.1); a benchmark gate added before the lock; JEV-27B-VL back in the zero-shot arm.
**Changes in 0.3:** split sizes set from a power check (5.3, 8.1); calibration moved to the EyePACS Kaggle-test half; model interfaces read from their documentation (4.1); NeoHorse fine-tuning dropped; implementation status of each arm stated (6.4); pipeline described (14).
**Changes in 0.2:** five clinical questions replace the original three (section 6.2); maculopathy added; sight-threatening definition confirmed; coherence, action-rule and patient-level analyses added.
**Date:** 3 October 2026
**Status:** Not yet frozen. Items marked **[CONFIRM]** need a decision; items marked **[VERIFY]** are from memory or inference and must be checked before the protocol is locked.

---

## 1. Summary

We test whether small, non-generative image decision models (Jev-style models such as imajev-4b) can grade diabetic retinopathy (DR) from colour fundus photographs. These models take an image and a typed question with a fixed set of options and return a probability for each option in a single forward pass, with no text generation.

We evaluate them as released (zero-shot) and after LoRA fine-tuning, on public DR datasets, with external validation on datasets from different countries and cameras. The comparison is against (a) a specialist image classifier and (b) a generative vision-language model on the same backbone.

The headline claim we are testing:

> A single small local model can match specialist accuracy for DR grading, report calibrated confidence, know when not to answer, and take new clinical questions without retraining.

A negative result (the models do not transfer, or do not beat a simple calibrated classifier) is also publishable and is a pre-planned outcome.

---

## 2. Background and rationale

### 2.1 Why now

- Jev (TypeSafe AI) was released in August 2026. Open image-capable variants followed within weeks: Visual Jev (22 Sep), PixelJev (25 Sep), imajev (late Sep), Jev-Omni and others.
- These models are being adopted quickly across domains. Someone will point one at medical images; evidence on whether that works is needed either way.

### 2.2 Prior art and the gap

| Work | What it did | What it leaves open |
|---|---|---|
| OmniMed-Jev (HKU, arXiv 2610.00381, 30 Sep 2026) | MedGemma-1.5-4B + decision head + LoRA across 15 medical datasets. Fundus appears as RetinaMNIST, a 5-point ordered score. Calibration error fell sharply versus a generative fine-tune of the same backbone. | 726 held-out cases; fundus pooled with cardiac ultrasound (n=200); held-out data from same sources as training; no out-of-distribution or per-source analysis; no comparison with general Jev-style models or DR specialists; the ordinal/regression family benefited least; its explicit "none" option probe failed. Code repo currently contains only a licence and README. |
| "Can Jev Judge Radiology Reports?" (arXiv 2609.27607) | Jev judging report text against references. | Text only, no images. |
| Visual Jev, PixelJev, imajev, Jev-Omni | General image decision models. | No medical evaluation. PixelJev states it is not validated for medical use. |

We found no DR-specific study of Jev-style models and no medical Jev-style model on Hugging Face (search on 3 Oct 2026; not exhaustive).

### 2.3 Motivation (what reviewers will ask)

Speed, cost and local deployment alone are a weak case, because a small specialist CNN is faster, cheaper and easier to run locally than a 4B-parameter model. The case rests on what a decision model offers that the alternatives do not.

**Versus generative vision-language models**
- Native probabilities over the supplied options, rather than confidence reconstructed from token likelihoods.
- No free text: nothing to parse, no hallucinated narrative, answer always within the option set.
- Lower latency and cost (imajev-4b measured at about $0.02 per 1,000 decisions and 0.1 s median latency on Image JevBench) and local deployment, which helps with data governance.

**Versus specialist CNNs**
- The label set is an input, not a trained head: grading scale, referral question or a new finding can be asked without retraining.
- Trained abstention ("unknown") for ungradable images in the same model.
- Image plus record input (imajev accepts up to two images and a text/JSON record), enabling metadata-aware or two-image questions.
- One generalist model to maintain rather than one network per task.
- Possible data efficiency when adapting to a new camera or population (a hypothesis we test).

**Scientific and safety case**
- Tests whether consumer-photo training transfers to fine lesion detail.
- Calibration for ordinal medical grading under dataset shift is an open question.

---

## 3. Objectives and hypotheses

### 3.1 Primary objectives

1. Measure zero-shot DR grading performance of current image decision models.
2. Measure performance after LoRA fine-tuning and test non-inferiority to a specialist classifier on external datasets.
3. Compare calibration and selective prediction against a generative VLM baseline and a temperature-scaled specialist, under external dataset shift.

### 3.2 Hypotheses

| ID | Hypothesis | Type |
|---|---|---|
| H1 | Zero-shot Jev-style models perform well below specialist level on DR grading. | Descriptive |
| H2 | Fine-tuned imajev-4b is non-inferior to the specialist on 5-class QWK and on referable-DR sensitivity at matched specificity, on external test sets. | Non-inferiority |
| H3 | Fine-tuned imajev-4b has lower calibration error and lower AURC than a generative fine-tune of the same backbone. | Superiority |
| H4 | Fine-tuned imajev-4b is not worse than the temperature-scaled specialist on external calibration and selective prediction. | Non-inferiority (exploratory superiority) |
| H5 | Adding vision-tower LoRA improves over language-only LoRA. | Superiority |
| H6 | p(unknown) separates ungradable from gradable images. | Descriptive (AUROC) |
| H7 | Exploratory: data efficiency, and answering new question types without retraining. | Exploratory |

---

## 4. Models

Pin every model to a specific Hugging Face revision (commit hash) at download time and record it. This field is moving daily.

### 4.1 Jev-style models

| Model | Repo | Base | Licence | Zero-shot | Fine-tune |
|---|---|---|---|---|---|
| imajev-4b (primary) | `mohit67890/imajev-4b` | Qwen3.5-4B | Apache-2.0 | Yes | Yes |
| NeoHorse Jev 4B | `TokenRhythm/NeoHorse-Jev-4B` | NeoHorse-1-4B | Apache-2.0 | Yes | No (no training code published) |
| Jev-Omni | `akhilaaa3/Jev-Omni` | Gemma 4 12B | Apache-2.0 | Yes | No |
| AutoJev-27B | `autotrust/JEV-27B-VL` **[VERIFY identity]** | Qwen3.8-27B (27.8B params) | Apache-2.0 | Yes | No |
| Visual-Jev 4B Answer-SFT | `guanxuyu/visual-jev-4b-answer-sft` | Qwen3-VL-4B | Apache-2.0 | Yes | No |
| Glance (frozen control) | `untappedvc/glance-qwen3-vl-4b` | Qwen3-VL-4B, frozen | Apache-2.0 | Yes | No |
| Optional size ablation | `mohit67890/imajev-2b`, `imajev-9b` | Qwen3.5-2B / 9B | Apache-2.0 | Yes | Optional |

Why these:
- imajev-4b and NeoHorse Jev 4B are level on Image JevBench accuracy and calibration (Intelligence 73.8 vs 72.9; Calibration 90.5 vs 91.2).
- Jev-Omni is kept for its non-Qwen backbone, not its rank (Intelligence 63.9).
- AutoJev-27B is the scale check.
- Glance and Visual-Jev share a base, so the pair shows what the decision adapter adds.

Not included: jev-spatial (spatial pointing), decider-2b-vision, JPT (CC-BY-NC, redundant Qwen variant), OmniJev 4B, Reflex 4B (repo identity unclear), Wity-1 (weights availability unconfirmed; do not send dataset images to a hosted API).

Known interface facts for imajev-4b:
- Rank-16 LoRA on language layers; vision encoder frozen.
- Question types: `noul` (yes/no), `choice` (2–254 options), `score` (2–10 ordered levels), plus a trained `unknown`.
- Up to 2 images per request, each resized to at most 400,000 pixels (about 630 × 630); 4,096-token limit; English only.
- Shipped calibration temperature was fitted on text-style items; authors recommend fitting your own.

Known limits for Jev-Omni: best at ≤20 options, no abstain output, images capped at roughly 256–280 tokens.

Interfaces of the other models, read from their model cards and repositories on 3 Oct 2026 (not yet run):

| Model | Question types | Built-in abstain | Image budget | Training code | Notes |
|---|---|---|---|---|---|
| NeoHorse Jev 4B | yes/no, choice, ordered score | No | up to 1,024 image tokens; one question per request | Not published | Vision weights are stock Qwen3.5-4B |
| Jev-Omni | one list of plain option strings | No | 280 image tokens | Not published | No option descriptions; best at 20 options or fewer |
| JEV-27B-VL | yes/no, choice, score fixed at 0-5 | No | card suggests 448 px or less | Not published | Decision head trained on text only; needs an 80 GB GPU |
| Visual-Jev 4B | choice only (2-16 options) | No | 200,704 pixels | Published | Custom prompts are outside its tested setup |
| Glance | yes/no, choice, ordered score (library) | No | 768 image tokens | None (frozen model) | Control for Visual-Jev |

Consequence: only imajev can abstain natively. Every other model receives "unknown" as an explicit extra option on Q2-Q5, sent as a single choice question.

### 4.2 Baselines and controls

| Baseline | Purpose |
|---|---|
| Untuned Qwen3.5-4B with option-logit readout | What the Jev adapter adds before any DR training |
| Generative VLM, zero-shot (Qwen3.5-4B generating the grade as text) | Supports cost, latency and calibration claims |
| Generative VLM, LoRA fine-tuned on the same data and schedule | Interface-controlled comparison (same design as OmniMed-Jev) |
| Specialist: RETFound and ConvNeXt (or ResNet-50), fine-tuned on the same data, with temperature scaling | The bar for H2 and H4 |
| Optional: MedGemma-1.5-4B zero-shot | Medical-backbone reference. **Contaminated on EyePACS** (it is in MedGemma's training mix); report external sets only |

---

## 5. Datasets

### 5.1 Roles

| Dataset | Size | Origin | Role | Access |
|---|---|---|---|---|
| EyePACS (Kaggle) | 88,702 (35,126 train / 53,576 test) | USA | Train, dev, calibration, internal test | Kaggle competition rules; no redistribution |
| Messidor-2 | 1,748 (1,744 gradable); grades adjudicated by three retina specialists (Krause et al.) | France | External test, best labels | Research/education use; no redistribution |
| DDR | 13,673 from 147 hospitals; 6,835 / 2,733 / 4,105 split; sixth class "ungradable" | China | External test, abstention test | GitHub (`nkicsl/DDR-dataset`); licence unclear **[VERIFY]** |
| APTOS 2019 | 3,662 labelled | India | External test | Non-commercial; no redistribution |
| IDRiD | 516 | India | External test | Open **[VERIFY licence]** |
| mBRSET | 5,164 images, 1,291 patients, handheld camera | Brazil | Hardest shift test | PhysioNet credentialed + data use agreement |
| BRSET (optional) | 16,266 | Brazil | Extra external | PhysioNet credentialed |
| EyeQ quality labels (optional) | Quality labels for a subset of EyePACS **[VERIFY]** | USA | Source of "unknown" training targets | To check |

Excluded: DeepDRiD, because RetinaMNIST (used by OmniMed-Jev) is believed to derive from it **[VERIFY]**.

Notes:
- EyePACS labels come from a single grader and are noisy. Headline claims rest on Messidor-2 and DDR.
- DDR stays purely external (not used for training) **[CONFIRM]**.
- No private clinical data is assumed **[CONFIRM]**.
- Start PhysioNet credentialing immediately; it is the slowest step.

### 5.2 Label harmonisation

All datasets are mapped to ICDR 0–4 (none, mild NPDR, moderate NPDR, severe NPDR, proliferative DR).

| Label | Definition | Status |
|---|---|---|
| Sight-threatening | Any maculopathy, or severe NPDR, or PDR | Confirmed |
| Referable | Moderate NPDR or worse, or any maculopathy | **[CONFIRM]** |
| Maculopathy | Present / absent, mapped from each dataset's macular oedema label | Mapping per dataset **[VERIFY]** |
| Ungradeable | DDR class 5; Messidor-2 adjudicated ungradable (4 images) | |

Maculopathy labels are not available in every dataset, so "referable" and "sight-threatening" are each reported in two versions:

| Version | Definition used | Datasets |
|---|---|---|
| Grade-only | Referable = grade ≥ 2; sight-threatening = grade ≥ 3 | All |
| Full clinical | Grade criteria or any maculopathy | Only datasets with maculopathy labels |

Maculopathy label availability:
- mBRSET: macular oedema labelled (confirmed).
- IDRiD, Messidor-2 (adjudicated), BRSET: believed labelled **[VERIFY]**.
- EyePACS, APTOS, DDR: believed not labelled **[VERIFY]**.

Consequences to state as limitations:
- EyePACS training targets for the referral and sight-threatening questions are grade-only, so an EyePACS image with maculopathy but mild or no retinopathy is labelled "not refer".
- Maculopathy on a single fundus photograph is a surrogate (lesions near the fovea), not a measurement of retinal thickening.

### 5.3 Splits and leakage controls

| Split | Source | Images | Use |
|---|---|---|---|
| Train | EyePACS Kaggle-train, 90% of patients | about 31,600 | Fine-tuning and specialist training |
| Dev | EyePACS Kaggle-train, 10% of patients | about 3,500 | Early stopping, learning-rate choice |
| Calibration | EyePACS Kaggle-test, patient sample | 10,000 | Temperature and operating thresholds |
| Internal test | EyePACS Kaggle-test, patient sample | 10,000 | Locked test |
| Reserve | Rest of EyePACS Kaggle-test | about 33,600 | Untouched |
| External tests | Messidor-2 1,744; DDR official test 4,105; APTOS 3,662; IDRiD 516; mBRSET 5,164 | about 15,200 | Locked tests, never trained on |
| Maculopathy training | BRSET, patient-level 80 / 10 / 10 | about 16,300 | Train, dev and calibration for Q3 only |

- Calibration uses the Kaggle-test half because 10% of Kaggle-train holds only about 160 sight-threatening eyes, too few to fix a 90%-sensitivity threshold; 10,000 images hold about 450.
- Counts above are from published tables and memory; the pipeline recomputes them from the downloads (`work/split_summary.csv`).
- DDR's train and validation parts stay unused.
- Both eyes of a patient always in the same split.
- Perceptual-hash de-duplication across all datasets (composite Kaggle datasets repeat images).
- Data-efficiency subsets of EyePACS-train: 1,000 / 5,000 / full, nested and stratified by grade.
- Paraphrase subset: a fixed 2,000 images per test set, stratified by grade, for wordings 1 and 2.
- Local-recalibration subset: a fixed 200 images per external test set.
- When a duplicate spans a training split and a test set, the test copy is kept and the other dropped.
- Write a split manifest (image ID, dataset, patient ID, split, label) and freeze it before any test-set inference.

Limitation to state: we cannot exclude that base model pretraining saw public fundus images.

---

## 6. Methods

### 6.1 Preprocessing

- Crop to the fundus disc bounding box, pad to square.
- Resize so the image is within imajev's 400,000-pixel cap (about 630 px on a side). Other models use their own processors on the same cropped image.
- No contrast enhancement in the primary analysis. One sensitivity run with standard enhancement.
- Same preprocessing for all arms, including the specialist (which may also be run at its native resolution as a secondary analysis).

### 6.2 Questions

Five fixed questions per image, following the sequence of decisions made when reviewing a diabetic patient in clinic. Wording is frozen before any test-set inference.

| # | Question | Options | Abstain |
|---|---|---|---|
| Q1 | Gradeability | gradeable / ungradeable | None ("ungradeable" is the can't-tell answer) |
| Q2 | DR grade | no DR / mild NPDR / moderate NPDR / severe NPDR / PDR | unknown |
| Q3 | Maculopathy | absent / present | unknown |
| Q4 | Referral | not refer / refer | unknown |
| Q5 | Sight-threatening | not sight-threatening / sight-threatening | unknown |

Draft wording:

**Q1, gradeability**
"Is this fundus photograph of sufficient quality to grade diabetic retinopathy?"

**Q2, DR grade (`score`, 5 ordered levels)**
"Grade the severity of diabetic retinopathy in this fundus photograph."
- 0: No apparent retinopathy. No abnormalities.
- 1: Mild non-proliferative. Microaneurysms only.
- 2: Moderate non-proliferative. More than microaneurysms but less than severe.
- 3: Severe non-proliferative. Extensive intraretinal haemorrhages in all four quadrants, venous beading in two or more quadrants, or prominent intraretinal microvascular abnormalities, with no signs of proliferative disease.
- 4: Proliferative. Neovascularisation, or vitreous or preretinal haemorrhage.

**Q3, maculopathy**
"Is diabetic maculopathy present in this fundus photograph?"
Draft definition: exudates, haemorrhages or retinal thickening at or near the macula **[CONFIRM wording and distance criterion]**.

**Q4, referral**
"Does this fundus photograph show referable diabetic eye disease: moderate non-proliferative retinopathy or worse, or any maculopathy?"

**Q5, sight-threatening**
"Does this fundus photograph show sight-threatening diabetic eye disease: severe non-proliferative retinopathy, proliferative retinopathy, or any maculopathy?"

How "unknown" works:
- "Unknown" is the model abstaining, not a disease category.
- Where a model has a built-in abstain output (imajev), use it. Where it does not (for example Jev-Omni), add "unknown" as an explicit option. Expect the explicit option to be weaker: OmniMed-Jev's explicit "none" probe failed.
- Ground truth: for a gradeable image, the dataset label. For an ungradeable image, the correct answer to Q2–Q5 is "unknown".

Rules:
- Three paraphrases of each question are written in advance; report mean and range across them (prompt sensitivity).
- Option order is never rotated for `score` (position encodes the level).
- Q4 and Q5 are about disease present in the image, not about the action to take. The action rule is applied in code (section 6.3).
- Rubric and question text **[CONFIRM]**.
- Exact request schema to be taken from each model's README **[VERIFY]**.

### 6.3 Deriving predictions

**Point predictions**
- Grade: argmax of the Q2 distribution (primary); rounded expectation (secondary).
- Q1, Q3, Q4, Q5: the more probable option, or "unknown" when abstention is the single most likely outcome.
- imajev implementation note: its `noul` yes-probability includes half the unknown mass; subtract `unknown_probability / 2` to get the plain probability.

**Direct versus derived**
Referral and sight-threatening status can be read directly (Q4, Q5) or derived from Q2 and Q3:

| Decision | Direct | Derived |
|---|---|---|
| Referable | Q4 | grade ≥ 2 (Q2) or maculopathy present (Q3) |
| Sight-threatening | Q5 | grade ≥ 3 (Q2) or maculopathy present (Q3) |

- Derived probability for ROC analysis: the larger of P(grade ≥ k) and P(maculopathy). This is a lower bound on the true union and avoids assuming the two are independent.
- Report both, and state before test inference which is primary. Proposed: direct **[CONFIRM]**.

**Coherence rate**
Share of images where the five answers are mutually consistent, for example no "mild NPDR, maculopathy absent" paired with "refer", and no "sight-threatening" paired with "not refer". Reported per model, before and after fine-tuning.

**Action rule (applied in code, not asked of the model)**
Refer the patient if any of: referable disease, ungradeable image, or the model abstains.
- Conservative screening analysis: sensitivity and specificity with abstentions and ungradeable images counted as referrals.
- Also report the gradeable rate and abstention rate separately, so the referral workload is visible.

**Patient-level analysis (secondary)**
Clinic decisions are per patient. Two approaches on datasets with eye pairing (EyePACS, Messidor-2):
- Worse-eye rule applied to per-image answers.
- For imajev, both eyes sent in one request (it accepts two images) with a patient-level referral question.

### 6.4 Experimental arms

| Arm | Description |
|---|---|
| Z | Zero-shot: all six Jev-style models plus controls, all test sets |
| A | imajev-4b, language-only LoRA (the imajev recipe), continuing from the shipped adapter |
| B | imajev-4b, language LoRA + vision-tower LoRA. imajev's trainer applies LoRA to language layers only, so this arm needs a small patch (`patches/imajev_vision_lora.patch`, untested) |
| C (optional) | Base Qwen3.5-4B + same LoRA and readout, no imajev adapter. Isolates the value of Jev pretraining |
| G | Generative LoRA fine-tune, same backbone, data and step count. Not yet implemented in the pipeline |
| S | Specialist: ConvNeXt-Tiny with grade, gradeability and maculopathy heads (RETFound optional, not yet implemented) |

Arm N (NeoHorse fine-tuned) is dropped: no training code is published.

### 6.5 Fine-tuning

- Trainer: imajev's `scripts/train_decision_lora_torch.py` (PyTorch + PEFT) for arms A–C, starting from the shipped adapter (`--init-adapter`); the checkpoint with the lowest dev loss is kept.
- The training file is written by `drjev export-train` and has been checked against imajev's own loader and prompt renderer.
- LoRA rank 16, alpha 32 (matching imajev).
- Learning rate: small sweep on dev, proposed {2e-5, 5e-5, 1e-4}.
- Up to 3 epochs, early stopping on dev loss.
- Class imbalance: grade-balanced sampling by repeating under-represented grades up to five times (about 74% of EyePACS is grade 0). The trainer has no sampling weights.
- "Unknown" targets: for ungradeable images (EyeQ "reject" subset if verified), the target for Q2–Q5 is "unknown" and for Q1 is "ungradeable".
- Each training image contributes Q1, Q2, Q4 and Q5 as separate decisions. On EyePACS the Q4 and Q5 targets are grade-only.
- Q3 (maculopathy) cannot be trained from EyePACS, which has no maculopathy labels. Options **[CONFIRM]**:
  - (a) Evaluate Q3 zero-shot only, and report full-definition referral and sight-threatening results as derived from a zero-shot Q3.
  - (b) Train Q3 on a labelled set held out for that purpose (proposed: BRSET, if credentialed and its labels are verified) and keep Messidor-2, IDRiD and mBRSET as external tests.
  - (c) Train Q3 on the IDRiD official training split and test on the IDRiD test split, Messidor-2 and mBRSET.
  - Proposed default: (b), falling back to (c).
- Three seeds per arm.
- Images from the maculopathy-training dataset teach Q3 only, for the decision model and for the specialist alike.
- Data-efficiency runs (1k / 5k / full) for arm B and for the specialist.

Compute estimate: a few GPU-hours per run on a single high-memory GPU. This is an estimate scaled from imajev's reported runs (about 2 hours on 4 GPUs for roughly 870k decisions); confirm with a pilot.

### 6.6 Calibration

- One temperature per question, fitted on the EyePACS calibration split only (Q3 on the BRSET calibration part). imajev is served without its shipped calibration file.
- Operating thresholds for referral, sight-threatening disease and maculopathy: the largest threshold reaching 90% sensitivity on the calibration split.
- Report raw and calibrated results.
- Never fit on external test sets in the primary analysis.
- Secondary: local recalibration with 200 images from each external site, to show how much local data closes the gap.

### 6.7 Flexibility experiments (exploratory, H7)

Collapsed scales (any DR, 3-level) are a weak test, because a CNN's 5-class probabilities can be summed to answer them. Prefer questions not derivable from the grade:
- Lesion presence (DDR has 757 images with lesion annotations).
- A question the model was never trained on, asked after DR fine-tuning (for example laser scars present, where labels exist **[VERIFY]**).
- Optional: grading with patient metadata supplied as a record (mBRSET has clinical metadata).

---

## 7. Outcomes

### 7.1 Primary

| ID | Outcome | Metric |
|---|---|---|
| P1 | 5-class grading | Quadratic weighted kappa (QWK) |
| P2 | Referable disease, grade-only version (all datasets) | AUROC; sensitivity and specificity at a threshold fixed on EyePACS dev for 90% sensitivity; repeated under the action rule |
| P3 | Calibration | Expected calibration error (15 bins), Brier score, reliability diagrams |
| P4 | Selective prediction | AURC; error at 50 / 80 / 90% coverage; share of images automated at a stated accuracy |
| P5 | Gradeability and abstention | Q1 accuracy and AUROC (DDR); rate of "unknown" on Q2–Q5 for ungradeable images; false-abstention rate on gradeable images |

Primary datasets for H2–H4: Messidor-2 and DDR test. Other external sets are reported in full as supporting evidence.

### 7.2 Key secondary (clinical questions limited by label availability)

| ID | Outcome | Metric | Datasets |
|---|---|---|---|
| K1 | Sight-threatening disease, full definition | AUROC, sensitivity, specificity | Those with maculopathy labels |
| K2 | Referable disease, full definition | AUROC, sensitivity, specificity | Those with maculopathy labels |
| K3 | Sight-threatening disease, grade-only | AUROC, sensitivity, specificity | All |
| K4 | Maculopathy | AUROC, sensitivity, specificity | Those with maculopathy labels |
| K5 | Coherence rate across Q1–Q5 | Proportion consistent | All |
| K6 | Direct versus derived referral and sight-threatening answers | Paired difference in AUROC and calibration | All |
| K7 | Patient-level referral | Sensitivity, specificity | EyePACS, Messidor-2 |

### 7.3 Other secondary

- Macro-F1, per-grade recall (especially grades 1, 3 and 4), confusion matrices.
- Prompt-sensitivity range.
- Latency (p50, p95), peak GPU memory, model size, cost per 1,000 decisions, all on stated hardware.
- Subgroup results by dataset, camera type and image quality where metadata allows.

---

## 8. Statistical analysis

- 95% confidence intervals by bootstrap (at least 2,000 resamples), clustered by patient where patient IDs exist, otherwise by image.
- Model-to-model differences by paired bootstrap on the same images.
- **Non-inferiority (H2, H4).** Margins must be fixed before test-set inference. Proposed starting points **[CONFIRM with a clinician]**:
  - QWK: margin 0.05.
  - rDR sensitivity at matched specificity: margin 5 percentage points.
  - "No significant difference" is not treated as equivalence.
- **Superiority (H3, H5):** paired bootstrap on ECE, AURC and QWK.
- Sensitivity comparisons are made at the reference model's specificity on the same images.
- Multiplicity: Holm correction across the pre-specified primary hypotheses. Everything else is labelled exploratory.
- Seeds: each seed is scored separately and the seeds are averaged, both for the point estimate and inside every bootstrap sample; the standard deviation across seeds is reported alongside. Rows are never blended across seeds.
- Tests are one-sided at 2.5%, matching the lower limit of the two-sided 95% interval. Primary tests are decided on the Holm-adjusted p-value over the whole pre-specified primary family; a primary test that cannot be run counts as failed.
- Models are compared only on test sets where both predicted every image. At least 2,000 bootstrap samples are needed for the Holm-adjusted tests to be able to pass.
- The locked external evaluation is run once. Any re-run is documented with the reason.

### 8.1 Precision and power of the test sets

Estimated before any model was run, from grade counts in published tables (EyePACS and APTOS counts from memory; DDR test scaled from the full set).

| Test set | Referable eyes (grade 2+) | Sight-threatening eyes (grade 3+) | 95% CI half-width on 90% sensitivity: referable / sight-threatening | Power of a 5-point non-inferiority test: referable / sight-threatening |
|---|---|---|---|---|
| EyePACS internal (10,000) | about 1,955 | about 448 | ±1.3 / ±2.8 points | 1.00 / 0.92 |
| Messidor-2 | 457 | 110 | ±2.8 / ±5.6 | 0.92 / 0.38 |
| DDR test | about 1,690 | about 345 | ±1.4 / ±3.2 | 1.00 / 0.84 |
| APTOS | about 1,490 | about 490 | ±1.5 / ±2.7 | 1.00 / 0.94 |
| mBRSET | 864 | 294 | ±2.0 / ±3.4 | 1.00 / 0.77 |
| IDRiD | 323 | 155 | ±3.3 / ±4.7 | 0.81 / 0.50 |
| External pooled | about 4,820 | about 1,390 | ±0.8 / ±1.6 | 1.00 / 1.00 |

- Power assumes the two models disagree on 10% of positive eyes; at 20% disagreement Messidor-2's referable power falls to 0.67.
- Grade agreement (QWK) is well powered everywhere: simulated 95% intervals are about ±0.01 to ±0.015.
- Consequence: the sight-threatening non-inferiority test is run on the pooled external sets and is reported per dataset descriptively only.

---

## 9. Planned outputs

| Output | Content |
|---|---|
| Table 1 | Zero-shot: QWK and rDR AUROC, every model × dataset |
| Table 2 | Fine-tuned arms vs specialist vs generative baseline, internal and external |
| Figure 1 | Reliability diagrams and ECE: EyePACS vs each external set |
| Figure 2 | Risk–coverage curves |
| Table 3 | Gradeability and abstention on ungradeable images |
| Table 3b | Clinical decisions: maculopathy, referral and sight-threatening (grade-only and full definition), with the action-rule analysis |
| Table 3c | Coherence rate; direct versus derived answers; patient-level referral |
| Figure 3 | Data-efficiency curves (decision model vs specialist) |
| Table 4 | Ablations: vision LoRA, adapter vs base readout, model size, prompt paraphrase |
| Table 5 | Deployment: latency, memory, size, cost |
| Supplement | Confusion matrices, subgroup results, flexibility experiments, local recalibration |

---

## 10. Decision gates

| Gate | Condition | Action |
|---|---|---|
| G0 (before the lock) | `drjev benchmark` and `drjev benchmark --train` results in | Fix the number of seeds, arms and data-efficiency runs so that the projected hours fit the machine; record the choice here |
| G1 (end of week 1) | Zero-shot results in | Confirms H1; confirm which adapters run and which models stay in the zero-shot table |
| G2 (mid week 2) | Arm B dev QWK within reach of specialist dev QWK | Proceed to locked evaluation. If far below, try higher resolution or tiling, then reassess |
| G3 (after locked evaluation) | H2 met and H3 or H4 met | Positive paper |
| G3 alternative | H2 not met, or no calibration/selective benefit | Negative-result paper: "general image decision models do not yet transfer to DR grading" |

---

## 11. Risks and limitations

| Risk | Mitigation |
|---|---|
| Being scooped (multiple papers per day in this area) | Preprint as soon as external validation is complete |
| Pretraining contamination | State as a limitation; exclude MedGemma from EyePACS results |
| Label noise in EyePACS | Headline claims on adjudicated or multi-grader external sets |
| 400,000-pixel cap loses microaneurysm detail | Ablation with tiling or two-crop input (imajev accepts two images) |
| Interface differences between models | Document per model; fall back to 5-way choice |
| Model and benchmark churn | Pin revisions; record dates |
| Dataset licences | Release code and split manifests only, not images; check whether fine-tuned weights may be released **[VERIFY]** |
| Not clinically validated | State clearly: retrospective, public data, no diagnostic claim |

---

## 12. Ethics, governance and reporting

- Public, de-identified datasets only; no new patient data.
- PhysioNet data use agreement for mBRSET and BRSET; named credentialed user **[CONFIRM who]**.
- No dataset images sent to third-party hosted APIs.
- Reporting to follow TRIPOD+AI and CLAIM checklists.
- The paper states that no component is intended or validated for diagnostic use.

---

## 13. Timeline (target about 3 weeks to preprint)

| Period | Work |
|---|---|
| Days 1–2 | Dataset access requests; download; preprocessing; split manifest; environment; pin model revisions; freeze questions and margins |
| Days 3–5 | Zero-shot sweep (arm Z) on dev and internal data; start specialist training (arm S) |
| Week 2 | Fine-tuning arms A and B (C and G if built); ablations; data-efficiency runs; fit calibration |
| Start of week 3 | Protocol lock; locked evaluation on all test sets, run once |
| Rest of week 3 | Analysis, figures, write-up, preprint |

### 13.1 Hardware and compute

- All inference and training run on one NVIDIA DGX Spark, 128 GB (Arm processor, CUDA 13, memory shared between CPU and GPU). Nothing leaves the machine.
- One model is held in memory at a time; each model runs in its own software environment, whose package versions are recorded with the results.
- JEV-27B-VL (52 GB of weights) fits in memory and is back in the zero-shot arm, subject to its server installing on this machine.
- Published speeds for these models come from data-centre GPUs. The timeline above is therefore provisional until gate G0: the benchmark measures seconds per image and per training step on this machine and projects the total.
- If the projection does not fit, the pre-agreed order of cuts is: paraphrase runs on fewer models; data-efficiency runs; seeds on arm A; then arm A itself. The primary comparison (arm B against the specialist, three seeds each) is cut last. **[CONFIRM]**

---

## 14. Pipeline

The study is run by the `drjev` program in this repository (see `README.md`). Datasets and models go in; tables, figures, a results summary, per-image predictions and a run manifest come out.

| Stage | Command |
|---|---|
| Read datasets, preprocess, split | `drjev ingest`, `preprocess`, `split` |
| Freeze splits, questions and analysis plan | `drjev lock` (test splits cannot be read before this) |
| Run models | `drjev predict`, `drjev check-model` |
| Training | `drjev export-train` (imajev arms), `drjev train-specialist` |
| Check the machine; time the models | `drjev doctor`, `drjev benchmark` |
| Calibrate, analyse, report | `drjev calibrate`, `analyze`, `report` |
| All of the above in order | `drjev run` |

Status on 3 Oct 2026: data stages, analysis and reporting are tested on synthetic data; the imajev adapter and training export are tested against imajev's own code without weights; nothing has been run on real images, real weights or a GPU.

---

## 15. Open items before protocol lock

- [ ] **[CONFIRM]** DDR stays external only
- [ ] **[CONFIRM]** No private clinical data
- [x] Sight-threatening = any maculopathy, or severe NPDR, or PDR (confirmed 3 Oct 2026)
- [x] Maculopathy question added (confirmed 3 Oct 2026)
- [ ] **[CONFIRM]** Referable = moderate NPDR or worse, or any maculopathy
- [ ] **[CONFIRM]** Maculopathy wording and distance criterion
- [ ] **[CONFIRM]** How Q3 is trained: option (a), (b) or (c) in section 6.5
- [ ] **[CONFIRM]** Direct or derived answer as primary for referral and sight-threatening
- [ ] **[CONFIRM]** Non-inferiority margins and rubric wording
- [ ] **[VERIFY]** Maculopathy labels and their mapping in IDRiD, Messidor-2, BRSET; absence in EyePACS, APTOS, DDR
- [ ] **[CONFIRM]** Who holds PhysioNet credentials
- [ ] **[VERIFY]** EyeQ quality labels: size, access, licence
- [ ] **[VERIFY]** DeepDRiD / RetinaMNIST relationship
- [ ] **[VERIFY]** IDRiD and DDR licences; IDRiD and Messidor-2 macular oedema labels
- [ ] **[VERIFY]** AutoJev-27B = `autotrust/JEV-27B-VL`
- [x] Score and abstain support for each non-imajev model: read from model cards (section 4.1); to be confirmed by running `drjev check-model`
- [x] NeoHorse Jev 4B training code: not published; arm N dropped
- [ ] **[VERIFY]** Dataset folder and column names in `config/datasets.yaml` against the real downloads (`drjev ingest` report)
- [ ] **[VERIFY]** Each untested adapter on a GPU; the vision-LoRA patch for arm B
- [ ] **[CONFIRM]** Whether to build the generative baseline (arm G) and RETFound, or drop H3 and report against ConvNeXt only
- [ ] **[CONFIRM]** The split sizes in section 5.3 and the pooled sight-threatening test in section 8.1
- [ ] **[CONFIRM]** The order of cuts in section 13.1 if the benchmark shows the full plan does not fit one machine
- [ ] **[VERIFY]** That imajev, its trainer and each other model install and run on the DGX Spark (Arm, CUDA 13)
- [ ] **[VERIFY]** Whether fine-tuned weights can be released under dataset terms
- [ ] Re-run the prior-art search the day before submission

---

## 16. References

Models and benchmarks
- imajev technical report: https://mohit67890.github.io/imajev/report/
- imajev technical specification: https://github.com/mohit67890/imajev/blob/main/docs/technical-specification.md
- imajev repository: https://github.com/mohit67890/imajev
- Jev-Omni: https://huggingface.co/akhilaaa3/Jev-Omni
- NeoHorse-Jev-4B: https://hf.co/TokenRhythm/NeoHorse-Jev-4B
- JEV-27B-VL: https://hf.co/autotrust/JEV-27B-VL
- Visual-Jev 4B Answer-SFT: https://hf.co/guanxuyu/visual-jev-4b-answer-sft
- Glance: https://hf.co/untappedvc/glance-qwen3-vl-4b
- Image JevBench: https://benchmarkheaven.com/image-jev-bench
- decision-vision-bench: https://github.com/gasvn/decision-vision-bench

Prior art
- OmniMed-Jev: https://arxiv.org/abs/2610.00381 (repo: https://github.com/lytang63/OmniMed-Jev)
- Visual Jev: https://arxiv.org/abs/2609.25845
- PixelJev: https://arxiv.org/abs/2609.29283
- Can Jev Judge Radiology Reports?: https://arxiv.org/abs/2609.27607
- Retina-RAG (zero-shot vs adapted VLM on DR): https://arxiv.org/abs/2605.06173
- CLIP-based DR grading: https://arxiv.org/abs/2603.13403
- Toward Reliable Diabetic Retinopathy Screening (MedGemma and EyePACS): https://pmc.ncbi.nlm.nih.gov/articles/PMC13418815/
- Ordinal conformal prediction for DR grading under shift: https://pmc.ncbi.nlm.nih.gov/articles/PMC13512306/

Datasets
- EyePACS (Kaggle): https://www.kaggle.com/c/diabetic-retinopathy-detection
- APTOS 2019: https://www.kaggle.com/c/aptos2019-blindness-detection
- Messidor-2: https://www.adcis.net/en/third-party/messidor2/
- DDR: https://github.com/nkicsl/DDR-dataset
- mBRSET: https://physionet.org/content/mbrset/1.0/
- BRSET: https://physionet.org/content/brazilian-ophthalmological/1.0.0/
