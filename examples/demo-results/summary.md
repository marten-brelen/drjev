# Results summary

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

Generated 2026-10-03 by drjev 0.1.0. Models analysed: 9. Test sets: aptos, mbrset, messidor2, idrid, ddr, eyepacs.

## Pre-specified tests

- **H2_qwk** (ddr, qwk): mock_jev_ft was not shown non-inferior to mock_specialist; 0.860 versus 0.874, advantage -0.014 (95% CI -0.044 to +0.015), margin 0.05.
- **H2_ref_sens** (ddr, ref_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.780 versus 0.832, advantage -0.051 (95% CI -0.179 to +0.040), margin 0.05.
- **H3_ece** (ddr, ece_grade): mock_jev_ft was not shown better than mock_generative; 0.114 versus 0.161, advantage +0.047 (95% CI -0.003 to +0.095).
- **H3_aurc** (ddr, aurc_grade): mock_jev_ft was not shown better than mock_generative; 0.157 versus 0.198, advantage +0.041 (95% CI -0.002 to +0.086).
- **H4_ece** (ddr, ece_grade): mock_jev_ft was non-inferior to mock_specialist; 0.114 versus 0.153, advantage +0.038 (95% CI -0.011 to +0.091), margin 0.02.
- **H4_aurc** (ddr, aurc_grade): mock_jev_ft was non-inferior to mock_specialist; 0.157 versus 0.190, advantage +0.033 (95% CI -0.013 to +0.084), margin 0.02.
- **H5_vision_lora** (ddr, qwk): mock_jev_ft was better than mock_jev_zs; 0.860 versus 0.524, advantage +0.335 (95% CI +0.261 to +0.412).
- **H2_qwk** (messidor2, qwk): mock_jev_ft was not shown non-inferior to mock_specialist; 0.799 versus 0.826, advantage -0.027 (95% CI -0.081 to +0.024), margin 0.05.
- **H2_ref_sens** (messidor2, ref_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.685 versus 0.758, advantage -0.073 (95% CI -0.266 to +0.076), margin 0.05.
- **H3_ece** (messidor2, ece_grade): mock_jev_ft was not shown better than mock_generative; 0.138 versus 0.163, advantage +0.024 (95% CI -0.036 to +0.091).
- **H3_aurc** (messidor2, aurc_grade): mock_jev_ft was not shown better than mock_generative; 0.184 versus 0.236, advantage +0.052 (95% CI -0.016 to +0.127).
- **H4_ece** (messidor2, ece_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.138 versus 0.152, advantage +0.014 (95% CI -0.044 to +0.079), margin 0.02.
- **H4_aurc** (messidor2, aurc_grade): mock_jev_ft was not shown non-inferior to mock_specialist; 0.184 versus 0.183, advantage -0.001 (95% CI -0.058 to +0.052), margin 0.02.
- **H5_vision_lora** (messidor2, qwk): mock_jev_ft was better than mock_jev_zs; 0.799 versus 0.347, advantage +0.453 (95% CI +0.336 to +0.577).
- **H2_st_sens** (pooled_external, st_sens_matched): mock_jev_ft was not shown non-inferior to mock_specialist; 0.843 versus 0.883, advantage -0.040 (95% CI -0.126 to +0.021), margin 0.05.

## Decision gate G3

The positive-paper condition (every primary H2 test passed after Holm adjustment, plus at least one H3 or H4 test) is **not** met on these data; the pre-planned alternative is the negative-result paper.

## Headline numbers on the primary external test sets

- mock_jev_ft (language + vision LoRA). messidor2: QWK 0.799 (0.745 to 0.844), referable AUROC 0.920 (0.889 to 0.946), grade ECE 0.138; ddr: QWK 0.860 (0.830 to 0.884), referable AUROC 0.960 (0.945 to 0.973), grade ECE 0.114.
- mock_generative (generative). messidor2: QWK 0.775 (0.715 to 0.824), referable AUROC 0.939 (0.905 to 0.966), grade ECE 0.163; ddr: QWK 0.786 (0.731 to 0.833), referable AUROC 0.928 (0.901 to 0.952), grade ECE 0.161.
- mock_specialist (specialist). messidor2: QWK 0.826 (0.772 to 0.870), referable AUROC 0.948 (0.917 to 0.972), grade ECE 0.152; ddr: QWK 0.874 (0.843 to 0.899), referable AUROC 0.967 (0.945 to 0.983), grade ECE 0.153.
- mock_jev_zs (zero-shot). messidor2: QWK 0.347 (0.229 to 0.453), referable AUROC 0.737 (0.661 to 0.807), grade ECE 0.117; ddr: QWK 0.524 (0.441 to 0.601), referable AUROC 0.818 (0.768 to 0.866), grade ECE 0.138.
- mock_noabstain_zs (zero-shot). messidor2: QWK 0.361 (0.235 to 0.482), referable AUROC 0.735 (0.660 to 0.807), grade ECE 0.113; ddr: QWK 0.349 (0.250 to 0.442), referable AUROC 0.727 (0.670 to 0.780), grade ECE 0.128.

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
