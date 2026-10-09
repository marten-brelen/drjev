# Results summary

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

Generated 2026-10-09 by drjev 0.2.0. Models analysed: 9. Test sets: aptos, mbrset, messidor2, idrid, ddr, eyepacs.

## Pre-specified tests

Each test is one-sided at 2.5%. Primary tests are decided on the Holm-adjusted p-value, which corrects for running several primary tests at once; the 95% intervals shown are unadjusted, so a primary test can fail even when its interval alone would clear the margin. Secondary tests are decided on the unadjusted p-value.

- **H2_qwk** (ddr, qwk): mock_jev_ft was not shown non-inferior to mock_specialist; 0.865 versus 0.867, advantage -0.002 (95% CI -0.030 to +0.024), margin 0.05; primary, Holm-adjusted p = 0.027 (unadjusted p = 0.003).
- **H2_ref_sens** (ddr, ref_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.855 versus 0.925, advantage -0.070 (95% CI -0.146 to +0.005), margin 0.05; primary, Holm-adjusted p = 1.000 (unadjusted p = 0.658).
- **H3_ece** (ddr, ece_grade): mock_jev_ft was not shown better than mock_generative; 0.106 versus 0.109, advantage +0.003 (95% CI -0.037 to +0.054); primary, Holm-adjusted p = 1.000 (unadjusted p = 0.392).
- **H3_aurc** (ddr, aurc_grade): mock_jev_ft was not shown better than mock_generative; 0.164 versus 0.167, advantage +0.003 (95% CI -0.040 to +0.047); primary, Holm-adjusted p = 1.000 (unadjusted p = 0.419).
- **H4_ece** (ddr, ece_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.106 versus 0.137, advantage +0.031 (95% CI -0.019 to +0.080), margin 0.02; secondary, p = 0.027.
- **H4_aurc** (ddr, aurc_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.164 versus 0.175, advantage +0.011 (95% CI -0.036 to +0.056), margin 0.02; secondary, p = 0.100.
- **H5_vision_lora** (ddr, qwk): mock_jev_ft was better than mock_jev_zs; 0.865 versus 0.455, advantage +0.409 (95% CI +0.329 to +0.499); secondary, p = 0.003.
- **H2_qwk** (messidor2, qwk): mock_jev_ft was not shown non-inferior to mock_specialist; 0.783 versus 0.835, advantage -0.052 (95% CI -0.100 to -0.008), margin 0.05; primary, Holm-adjusted p = 1.000 (unadjusted p = 0.571).
- **H2_ref_sens** (messidor2, ref_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.734 versus 0.871, advantage -0.137 (95% CI -0.256 to +0.000), margin 0.05; primary, Holm-adjusted p = 1.000 (unadjusted p = 0.887).
- **H3_ece** (messidor2, ece_grade): mock_jev_ft was not shown better than mock_generative; 0.160 versus 0.101, advantage -0.059 (95% CI -0.111 to +0.005); primary, Holm-adjusted p = 1.000 (unadjusted p = 0.957).
- **H3_aurc** (messidor2, aurc_grade): mock_jev_ft was not shown better than mock_generative; 0.209 versus 0.226, advantage +0.017 (95% CI -0.056 to +0.086); primary, Holm-adjusted p = 1.000 (unadjusted p = 0.382).
- **H4_ece** (messidor2, ece_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.160 versus 0.137, advantage -0.022 (95% CI -0.084 to +0.036), margin 0.02; secondary, p = 0.495.
- **H4_aurc** (messidor2, aurc_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.209 versus 0.200, advantage -0.009 (95% CI -0.064 to +0.042), margin 0.02; secondary, p = 0.379.
- **H5_vision_lora** (messidor2, qwk): mock_jev_ft was better than mock_jev_zs; 0.783 versus 0.484, advantage +0.299 (95% CI +0.200 to +0.380); secondary, p = 0.003.
- **H2_st_sens** (pooled_external, st_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.832 versus 0.848, advantage -0.016 (95% CI -0.088 to +0.051), margin 0.05; secondary, p = 0.159.

## Decision gate G3

The positive-paper condition (every primary H2 test passed after Holm adjustment, plus at least one H3 or H4 test) is **not** met on these data; the pre-planned alternative is the negative-result paper.

## Headline numbers on the primary external test sets

- mock_jev_ft (language + vision LoRA). messidor2: QWK 0.783 (0.729 to 0.820), referable AUROC 0.925 (0.904 to 0.950), grade ECE 0.160; ddr: QWK 0.865 (0.833 to 0.888), referable AUROC 0.962 (0.945 to 0.975), grade ECE 0.106.
- mock_generative (generative). messidor2: QWK 0.785 (0.723 to 0.843), referable AUROC 0.939 (0.903 to 0.973), grade ECE 0.101; ddr: QWK 0.809 (0.765 to 0.846), referable AUROC 0.946 (0.918 to 0.966), grade ECE 0.109.
- mock_specialist (specialist). messidor2: QWK 0.835 (0.788 to 0.875), referable AUROC 0.966 (0.945 to 0.983), grade ECE 0.137; ddr: QWK 0.867 (0.838 to 0.891), referable AUROC 0.975 (0.961 to 0.989), grade ECE 0.137.
- mock_jev_zs (zero-shot). messidor2: QWK 0.484 (0.390 to 0.587), referable AUROC 0.794 (0.727 to 0.857), grade ECE 0.132; ddr: QWK 0.455 (0.358 to 0.539), referable AUROC 0.771 (0.719 to 0.821), grade ECE 0.124.
- mock_noabstain_zs (zero-shot). messidor2: QWK 0.309 (0.191 to 0.407), referable AUROC 0.710 (0.635 to 0.772), grade ECE 0.095; ddr: QWK 0.452 (0.352 to 0.541), referable AUROC 0.770 (0.715 to 0.813), grade ECE 0.140.

## Calibration notes

- mock_jev_zs: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_noabstain_zs: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_jev_ft_s0: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_jev_ft_s1: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_jev_ft_100: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_jev_ft_300: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_generative: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_specialist: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_specialist_100: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1
- mock_specialist_300: q3_maculopathy: only 28 labelled calibration images (fewer than 100); temperature left at 1

## Files

- `tables/`: every table as .csv and .md
- `figures/`: every figure as .png and .pdf
- `metrics_long.csv`: every metric, model and dataset with intervals
- `comparisons.csv`: the pre-specified tests
- `per_image/`: calibrated per-image predictions (image identifiers only, no images)
- `run_manifest.json`: configuration, model revisions, lock and test-set access log
