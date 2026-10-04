### Table 0. Images by dataset, split and label after exclusions

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| dataset | split | grade 0 | grade 1 | grade 2 | grade 3 | grade 4 | ungradeable | total | patients | maculopathy labelled | maculopathy present |
|---|---|---|---|---|---|---|---|---|---|---|---|
| aptos | test | 187 | 35 | 43 | 16 | 22 | 0 | 303 | 303 | 0 | 0 |
| brset | q3_cal | 15 | 6 | 5 | 1 | 1 | 0 | 28 | 14 | 28 | 4 |
| brset | q3_dev | 15 | 7 | 3 | 2 | 1 | 0 | 28 | 14 | 28 | 1 |
| brset | q3_train | 108 | 65 | 37 | 18 | 16 | 0 | 244 | 122 | 244 | 39 |
| ddr | test | 222 | 33 | 57 | 28 | 22 | 38 | 400 | 400 | 0 | 0 |
| ddr | unused | 90 | 19 | 36 | 12 | 11 | 12 | 180 | 180 | 0 | 0 |
| eyepacs | calibration | 231 | 103 | 65 | 39 | 36 | 26 | 500 | 250 | 0 | 0 |
| eyepacs | dev | 38 | 11 | 9 | 3 | 6 | 3 | 70 | 35 | 0 | 0 |
| eyepacs | reserve | 94 | 44 | 25 | 17 | 13 | 7 | 200 | 100 | 0 | 0 |
| eyepacs | test_internal | 237 | 93 | 68 | 47 | 31 | 24 | 500 | 250 | 0 | 0 |
| eyepacs | train | 327 | 109 | 72 | 47 | 35 | 37 | 627 | 314 | 0 | 0 |
| idrid | test | 45 | 6 | 29 | 22 | 18 | 0 | 120 | 120 | 120 | 40 |
| mbrset | test | 126 | 76 | 56 | 35 | 43 | 24 | 360 | 90 | 336 | 48 |
| messidor2 | test | 128 | 27 | 45 | 9 | 8 | 3 | 220 | 220 | 217 | 38 |

Duplicates across datasets are listed in work/duplicates.csv; unreadable files in work/preprocess_errors.csv.

### Table 1. Zero-shot performance of released models

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Gradeable images | QWK (95% CI) | Referable AUROC (95% CI) | Grade ECE | Abstained on gradeable images |
|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 303 | 0.469 (0.365 to 0.563) | 0.809 (0.754 to 0.860) | 0.141 | 0.010 |
| mock_jev_zs | mbrset | 336 | 0.543 (0.435 to 0.627) | 0.821 (0.763 to 0.870) | 0.064 | 0.009 |
| mock_jev_zs | messidor2 | 217 | 0.347 (0.229 to 0.453) | 0.737 (0.661 to 0.807) | 0.117 | 0.009 |
| mock_jev_zs | idrid | 120 | 0.463 (0.300 to 0.608) | 0.763 (0.671 to 0.847) | 0.096 | 0.017 |
| mock_jev_zs | ddr | 362 | 0.524 (0.441 to 0.601) | 0.818 (0.768 to 0.866) | 0.138 | 0.011 |
| mock_jev_zs | eyepacs | 476 | 0.636 (0.565 to 0.701) | 0.860 (0.820 to 0.896) | 0.100 | 0.013 |
| mock_noabstain_zs | aptos | 303 | 0.482 (0.387 to 0.569) | 0.796 (0.739 to 0.848) | 0.193 | 0.010 |
| mock_noabstain_zs | mbrset | 336 | 0.432 (0.314 to 0.535) | 0.758 (0.695 to 0.813) | 0.067 | 0.006 |
| mock_noabstain_zs | messidor2 | 217 | 0.361 (0.235 to 0.482) | 0.735 (0.660 to 0.807) | 0.113 | 0.018 |
| mock_noabstain_zs | idrid | 120 | 0.433 (0.275 to 0.578) | 0.735 (0.645 to 0.823) | 0.057 | 0.025 |
| mock_noabstain_zs | ddr | 362 | 0.349 (0.250 to 0.442) | 0.727 (0.670 to 0.780) | 0.128 | 0.006 |
| mock_noabstain_zs | eyepacs | 476 | 0.577 (0.498 to 0.648) | 0.823 (0.779 to 0.862) | 0.133 | 0.019 |

QWK: quadratic weighted kappa on five grades. Referable: grade 2 or worse (grade-only definition). Probabilities temperature-scaled on the EyePACS calibration split.

### Table 2. Fine-tuned decision models, specialist and generative baselines

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Arm | Dataset | Gradeable images | QWK | Referable AUROC | Referable sensitivity | Referable specificity | Grade ECE | AURC |
|---|---|---|---|---|---|---|---|---|---|
| mock_jev_ft | language + vision LoRA | aptos | 303 | 0.844 (0.805 to 0.872) | 0.950 (0.927 to 0.969) | 0.852 (0.791 to 0.905) | 0.928 (0.901 to 0.953) | 0.129 (0.108 to 0.169) | 0.177 (0.143 to 0.216) |
| mock_jev_ft | language + vision LoRA | mbrset | 336 | 0.851 (0.811 to 0.878) | 0.944 (0.921 to 0.963) | 0.847 (0.791 to 0.896) | 0.884 (0.852 to 0.912) | 0.137 (0.114 to 0.184) | 0.264 (0.214 to 0.318) |
| mock_jev_ft | language + vision LoRA | messidor2 | 217 | 0.799 (0.745 to 0.844) | 0.920 (0.889 to 0.946) | 0.750 (0.674 to 0.820) | 0.903 (0.870 to 0.936) | 0.138 (0.110 to 0.184) | 0.184 (0.144 to 0.228) |
| mock_jev_ft | language + vision LoRA | idrid | 120 | 0.873 (0.836 to 0.902) | 0.954 (0.928 to 0.977) | 0.855 (0.793 to 0.914) | 0.931 (0.870 to 0.980) | 0.150 (0.119 to 0.210) | 0.236 (0.177 to 0.309) |
| mock_jev_ft | language + vision LoRA | ddr | 362 | 0.860 (0.830 to 0.884) | 0.960 (0.945 to 0.973) | 0.836 (0.782 to 0.890) | 0.929 (0.905 to 0.952) | 0.114 (0.094 to 0.149) | 0.157 (0.130 to 0.190) |
| mock_jev_ft | language + vision LoRA | eyepacs | 476 | 0.881 (0.857 to 0.900) | 0.965 (0.952 to 0.977) | 0.866 (0.822 to 0.911) | 0.927 (0.906 to 0.946) | 0.079 (0.067 to 0.112) | 0.179 (0.153 to 0.207) |
| mock_jev_ft | language + vision LoRA | pooled_external | 1338 | 0.854 (0.838 to 0.868) | 0.948 (0.939 to 0.956) | 0.833 (0.808 to 0.858) | 0.914 (0.900 to 0.927) | 0.123 (0.109 to 0.140) | 0.197 (0.180 to 0.217) |
| mock_jev_ft_100 | language + vision LoRA | aptos | 303 | 0.706 (0.625 to 0.773) | 0.902 (0.862 to 0.939) | 0.815 (0.727 to 0.899) | 0.788 (0.736 to 0.842) | 0.137 (0.109 to 0.187) | 0.206 (0.159 to 0.259) |
| mock_jev_ft_100 | language + vision LoRA | mbrset | 336 | 0.724 (0.642 to 0.782) | 0.883 (0.838 to 0.922) | 0.784 (0.693 to 0.861) | 0.787 (0.724 to 0.844) | 0.147 (0.112 to 0.199) | 0.364 (0.289 to 0.442) |
| mock_jev_ft_100 | language + vision LoRA | messidor2 | 217 | 0.584 (0.467 to 0.681) | 0.809 (0.743 to 0.864) | 0.677 (0.556 to 0.790) | 0.735 (0.662 to 0.801) | 0.126 (0.089 to 0.194) | 0.286 (0.214 to 0.365) |
| mock_jev_ft_100 | language + vision LoRA | idrid | 120 | 0.760 (0.677 to 0.822) | 0.893 (0.834 to 0.942) | 0.783 (0.678 to 0.870) | 0.824 (0.711 to 0.922) | 0.160 (0.111 to 0.254) | 0.377 (0.277 to 0.494) |
| mock_jev_ft_100 | language + vision LoRA | ddr | 362 | 0.634 (0.556 to 0.705) | 0.874 (0.835 to 0.910) | 0.776 (0.697 to 0.856) | 0.780 (0.728 to 0.830) | 0.138 (0.115 to 0.190) | 0.273 (0.218 to 0.331) |
| mock_jev_ft_100 | language + vision LoRA | eyepacs | 476 | 0.767 (0.713 to 0.808) | 0.923 (0.894 to 0.947) | 0.890 (0.835 to 0.940) | 0.779 (0.734 to 0.821) | 0.111 (0.079 to 0.157) | 0.293 (0.241 to 0.348) |
| mock_jev_ft_100 | language + vision LoRA | pooled_external | 1338 | 0.694 (0.659 to 0.728) | 0.875 (0.855 to 0.895) | 0.773 (0.732 to 0.816) | 0.779 (0.752 to 0.805) | 0.121 (0.105 to 0.147) | 0.291 (0.260 to 0.324) |
| mock_jev_ft_300 | language + vision LoRA | aptos | 303 | 0.782 (0.724 to 0.830) | 0.925 (0.888 to 0.956) | 0.852 (0.769 to 0.923) | 0.811 (0.757 to 0.861) | 0.110 (0.076 to 0.158) | 0.205 (0.159 to 0.261) |
| mock_jev_ft_300 | language + vision LoRA | mbrset | 336 | 0.778 (0.711 to 0.829) | 0.886 (0.847 to 0.920) | 0.851 (0.782 to 0.907) | 0.718 (0.655 to 0.773) | 0.124 (0.098 to 0.181) | 0.326 (0.255 to 0.398) |
| mock_jev_ft_300 | language + vision LoRA | messidor2 | 217 | 0.660 (0.560 to 0.742) | 0.876 (0.818 to 0.928) | 0.790 (0.681 to 0.889) | 0.852 (0.791 to 0.906) | 0.123 (0.084 to 0.191) | 0.245 (0.186 to 0.316) |
| mock_jev_ft_300 | language + vision LoRA | idrid | 120 | 0.853 (0.798 to 0.896) | 0.948 (0.907 to 0.979) | 0.841 (0.750 to 0.920) | 0.922 (0.843 to 0.981) | 0.091 (0.065 to 0.188) | 0.250 (0.170 to 0.349) |
| mock_jev_ft_300 | language + vision LoRA | ddr | 362 | 0.753 (0.697 to 0.800) | 0.928 (0.897 to 0.955) | 0.869 (0.802 to 0.929) | 0.859 (0.814 to 0.899) | 0.148 (0.122 to 0.196) | 0.251 (0.202 to 0.306) |
| mock_jev_ft_300 | language + vision LoRA | eyepacs | 476 | 0.825 (0.783 to 0.859) | 0.928 (0.900 to 0.954) | 0.863 (0.801 to 0.921) | 0.827 (0.785 to 0.867) | 0.089 (0.062 to 0.128) | 0.229 (0.186 to 0.278) |
| mock_jev_ft_300 | language + vision LoRA | pooled_external | 1338 | 0.775 (0.745 to 0.800) | 0.910 (0.893 to 0.927) | 0.845 (0.810 to 0.880) | 0.817 (0.791 to 0.845) | 0.107 (0.092 to 0.135) | 0.255 (0.227 to 0.286) |
| mock_generative | generative | aptos | 303 | 0.842 (0.799 to 0.878) | 0.964 (0.942 to 0.981) | 0.901 (0.833 to 0.961) | 0.896 (0.853 to 0.933) | 0.128 (0.092 to 0.175) | 0.169 (0.129 to 0.217) |
| mock_generative | generative | mbrset | 336 | 0.843 (0.794 to 0.878) | 0.931 (0.899 to 0.958) | 0.873 (0.798 to 0.937) | 0.802 (0.745 to 0.855) | 0.100 (0.069 to 0.157) | 0.262 (0.202 to 0.327) |
| mock_generative | generative | messidor2 | 217 | 0.775 (0.715 to 0.824) | 0.939 (0.905 to 0.966) | 0.871 (0.776 to 0.950) | 0.832 (0.769 to 0.889) | 0.163 (0.121 to 0.224) | 0.236 (0.170 to 0.314) |
| mock_generative | generative | idrid | 120 | 0.874 (0.822 to 0.916) | 0.973 (0.945 to 0.993) | 0.971 (0.924 to 1.000) | 0.863 (0.767 to 0.946) | 0.099 (0.077 to 0.185) | 0.183 (0.114 to 0.273) |
| mock_generative | generative | ddr | 362 | 0.786 (0.731 to 0.833) | 0.928 (0.901 to 0.952) | 0.850 (0.782 to 0.918) | 0.816 (0.768 to 0.861) | 0.161 (0.127 to 0.207) | 0.198 (0.160 to 0.244) |
| mock_generative | generative | eyepacs | 476 | 0.871 (0.839 to 0.895) | 0.968 (0.953 to 0.981) | 0.925 (0.883 to 0.963) | 0.861 (0.822 to 0.895) | 0.059 (0.042 to 0.110) | 0.190 (0.153 to 0.232) |
| mock_generative | generative | pooled_external | 1338 | 0.831 (0.810 to 0.851) | 0.945 (0.934 to 0.957) | 0.887 (0.856 to 0.917) | 0.838 (0.815 to 0.864) | 0.114 (0.097 to 0.140) | 0.212 (0.186 to 0.239) |
| mock_specialist | specialist | aptos | 303 | 0.826 (0.782 to 0.861) | 0.957 (0.932 to 0.977) | 0.815 (0.724 to 0.893) | 0.923 (0.888 to 0.956) | 0.195 (0.154 to 0.247) | 0.233 (0.185 to 0.288) |
| mock_specialist | specialist | mbrset | 336 | 0.884 (0.847 to 0.911) | 0.954 (0.929 to 0.974) | 0.858 (0.788 to 0.919) | 0.881 (0.833 to 0.923) | 0.137 (0.104 to 0.196) | 0.240 (0.187 to 0.297) |
| mock_specialist | specialist | messidor2 | 217 | 0.826 (0.772 to 0.870) | 0.948 (0.917 to 0.972) | 0.758 (0.645 to 0.860) | 0.935 (0.896 to 0.971) | 0.152 (0.116 to 0.217) | 0.183 (0.135 to 0.237) |
| mock_specialist | specialist | idrid | 120 | 0.885 (0.845 to 0.916) | 0.972 (0.945 to 0.991) | 0.797 (0.701 to 0.885) | 0.980 (0.936 to 1.000) | 0.214 (0.162 to 0.306) | 0.253 (0.179 to 0.342) |
| mock_specialist | specialist | ddr | 362 | 0.874 (0.843 to 0.899) | 0.967 (0.945 to 0.983) | 0.832 (0.757 to 0.899) | 0.961 (0.935 to 0.983) | 0.153 (0.118 to 0.204) | 0.190 (0.149 to 0.239) |
| mock_specialist | specialist | eyepacs | 476 | 0.901 (0.877 to 0.920) | 0.971 (0.957 to 0.983) | 0.877 (0.823 to 0.926) | 0.933 (0.906 to 0.959) | 0.057 (0.041 to 0.105) | 0.154 (0.123 to 0.189) |
| mock_specialist | specialist | pooled_external | 1338 | 0.867 (0.849 to 0.882) | 0.958 (0.948 to 0.967) | 0.821 (0.787 to 0.858) | 0.930 (0.913 to 0.947) | 0.154 (0.133 to 0.181) | 0.215 (0.192 to 0.240) |
| mock_specialist_100 | specialist | aptos | 303 | 0.461 (0.371 to 0.542) | 0.789 (0.731 to 0.842) | 0.840 (0.757 to 0.915) | 0.572 (0.509 to 0.636) | 0.196 (0.169 to 0.245) | 0.343 (0.279 to 0.411) |
| mock_specialist_100 | specialist | mbrset | 336 | 0.610 (0.525 to 0.675) | 0.839 (0.790 to 0.883) | 0.858 (0.792 to 0.917) | 0.589 (0.522 to 0.654) | 0.112 (0.088 to 0.163) | 0.410 (0.335 to 0.484) |
| mock_specialist_100 | specialist | messidor2 | 217 | 0.478 (0.371 to 0.576) | 0.780 (0.704 to 0.847) | 0.774 (0.662 to 0.873) | 0.626 (0.547 to 0.700) | 0.138 (0.114 to 0.207) | 0.355 (0.277 to 0.436) |
| mock_specialist_100 | specialist | idrid | 120 | 0.632 (0.514 to 0.729) | 0.820 (0.745 to 0.883) | 0.783 (0.687 to 0.871) | 0.647 (0.511 to 0.774) | 0.164 (0.118 to 0.253) | 0.403 (0.302 to 0.524) |
| mock_specialist_100 | specialist | ddr | 362 | 0.581 (0.498 to 0.659) | 0.845 (0.800 to 0.887) | 0.832 (0.757 to 0.901) | 0.659 (0.599 to 0.717) | 0.132 (0.100 to 0.180) | 0.318 (0.260 to 0.383) |
| mock_specialist_100 | specialist | eyepacs | 476 | 0.695 (0.632 to 0.748) | 0.877 (0.840 to 0.910) | 0.904 (0.846 to 0.955) | 0.664 (0.611 to 0.717) | 0.063 (0.049 to 0.115) | 0.323 (0.267 to 0.380) |
| mock_specialist_100 | specialist | pooled_external | 1338 | 0.565 (0.518 to 0.602) | 0.819 (0.794 to 0.842) | 0.826 (0.790 to 0.860) | 0.615 (0.583 to 0.646) | 0.116 (0.099 to 0.142) | 0.356 (0.324 to 0.389) |
| mock_specialist_300 | specialist | aptos | 303 | 0.664 (0.587 to 0.729) | 0.888 (0.845 to 0.927) | 0.914 (0.849 to 0.969) | 0.707 (0.648 to 0.765) | 0.170 (0.148 to 0.227) | 0.287 (0.228 to 0.353) |
| mock_specialist_300 | specialist | mbrset | 336 | 0.761 (0.695 to 0.808) | 0.893 (0.849 to 0.930) | 0.873 (0.806 to 0.931) | 0.693 (0.633 to 0.752) | 0.140 (0.105 to 0.191) | 0.326 (0.265 to 0.392) |
| mock_specialist_300 | specialist | messidor2 | 217 | 0.622 (0.524 to 0.706) | 0.865 (0.807 to 0.915) | 0.806 (0.707 to 0.900) | 0.761 (0.690 to 0.826) | 0.146 (0.111 to 0.210) | 0.253 (0.188 to 0.324) |
| mock_specialist_300 | specialist | idrid | 120 | 0.805 (0.735 to 0.857) | 0.907 (0.855 to 0.949) | 0.797 (0.703 to 0.887) | 0.804 (0.702 to 0.909) | 0.171 (0.133 to 0.268) | 0.324 (0.237 to 0.432) |
| mock_specialist_300 | specialist | ddr | 362 | 0.752 (0.692 to 0.803) | 0.917 (0.883 to 0.947) | 0.860 (0.789 to 0.922) | 0.808 (0.759 to 0.857) | 0.145 (0.116 to 0.195) | 0.259 (0.205 to 0.321) |
| mock_specialist_300 | specialist | eyepacs | 476 | 0.810 (0.765 to 0.845) | 0.937 (0.910 to 0.960) | 0.911 (0.855 to 0.959) | 0.806 (0.762 to 0.850) | 0.077 (0.055 to 0.125) | 0.238 (0.194 to 0.285) |
| mock_specialist_300 | specialist | pooled_external | 1338 | 0.734 (0.701 to 0.761) | 0.894 (0.875 to 0.912) | 0.857 (0.824 to 0.888) | 0.748 (0.719 to 0.776) | 0.141 (0.123 to 0.168) | 0.283 (0.255 to 0.312) |

Values are point estimates with 95% patient-clustered bootstrap intervals. Sensitivity and specificity use the threshold fixed on the calibration split for 90% sensitivity. Seeds of one arm are pooled.

### Table 3. Gradeability and abstention on ungradeable images

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Ungradeable images | Gradeability AUROC (Q1) | Ungradeable detected (Q1) | Gradeable kept (Q1) | Unknown-probability AUROC (Q2) | Abstained on ungradeable (Q2) | Abstained on gradeable (Q2) |
|---|---|---|---|---|---|---|---|---|
| mock_jev_zs | mbrset | 24 | 0.998 (0.993 to 1.000) | 0.958 (0.852 to 1.000) | 0.991 (0.979 to 1.000) | 0.870 (0.810 to 0.918) | 0.958 (0.852 to 1.000) | 0.009 (0.000 to 0.021) |
| mock_jev_zs | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.986 (0.968 to 1.000) | 0.799 (0.615 to 1.000) | 1.000 (1.000 to 1.000) | 0.009 (0.000 to 0.023) |
| mock_jev_zs | ddr | 38 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.983 (0.970 to 0.995) | 0.880 (0.835 to 0.923) | 0.974 (0.909 to 1.000) | 0.011 (0.003 to 0.022) |
| mock_jev_zs | eyepacs | 24 | 0.999 (0.998 to 1.000) | 1.000 (1.000 to 1.000) | 0.981 (0.968 to 0.992) | 0.886 (0.841 to 0.928) | 1.000 (1.000 to 1.000) | 0.013 (0.004 to 0.023) |
| mock_noabstain_zs | mbrset | 24 | 1.000 (0.999 to 1.000) | 1.000 (1.000 to 1.000) | 0.979 (0.964 to 0.991) | 0.812 (0.748 to 0.879) | 1.000 (1.000 to 1.000) | 0.006 (0.000 to 0.015) |
| mock_noabstain_zs | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.982 (0.963 to 0.995) | 0.977 (0.922 to 1.000) | 1.000 (1.000 to 1.000) | 0.018 (0.005 to 0.037) |
| mock_noabstain_zs | ddr | 38 | 0.999 (0.997 to 1.000) | 0.974 (0.912 to 1.000) | 0.978 (0.961 to 0.992) | 0.856 (0.807 to 0.901) | 0.974 (0.912 to 1.000) | 0.006 (0.000 to 0.014) |
| mock_noabstain_zs | eyepacs | 24 | 0.998 (0.995 to 1.000) | 1.000 (1.000 to 1.000) | 0.966 (0.950 to 0.981) | 0.861 (0.802 to 0.914) | 1.000 (1.000 to 1.000) | 0.019 (0.008 to 0.032) |
| mock_jev_ft | mbrset | 24 | 1.000 (0.999 to 1.000) | 1.000 (1.000 to 1.000) | 0.975 (0.963 to 0.986) | 1.000 (0.999 to 1.000) | 1.000 (1.000 to 1.000) | 0.022 (0.012 to 0.034) |
| mock_jev_ft | messidor2 | 3 | 0.998 (0.993 to 1.000) | 1.000 (1.000 to 1.000) | 0.986 (0.975 to 0.995) | 0.998 (0.993 to 1.000) | 1.000 (1.000 to 1.000) | 0.012 (0.002 to 0.023) |
| mock_jev_ft | ddr | 38 | 0.998 (0.996 to 1.000) | 1.000 (1.000 to 1.000) | 0.979 (0.969 to 0.989) | 0.998 (0.996 to 1.000) | 0.987 (0.957 to 1.000) | 0.018 (0.008 to 0.028) |
| mock_jev_ft | eyepacs | 24 | 0.998 (0.996 to 1.000) | 0.979 (0.929 to 1.000) | 0.982 (0.973 to 0.990) | 0.998 (0.995 to 1.000) | 0.958 (0.891 to 1.000) | 0.015 (0.007 to 0.023) |
| mock_jev_ft_100 | mbrset | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.979 (0.964 to 0.991) | 0.998 (0.992 to 1.000) | 1.000 (1.000 to 1.000) | 0.018 (0.006 to 0.033) |
| mock_jev_ft_100 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.991 (0.977 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.005 (0.000 to 0.014) |
| mock_jev_ft_100 | ddr | 38 | 0.991 (0.981 to 0.999) | 0.921 (0.833 to 1.000) | 0.964 (0.944 to 0.981) | 0.989 (0.978 to 0.998) | 0.921 (0.833 to 1.000) | 0.033 (0.017 to 0.053) |
| mock_jev_ft_100 | eyepacs | 24 | 0.998 (0.994 to 1.000) | 0.958 (0.857 to 1.000) | 0.979 (0.966 to 0.992) | 0.996 (0.990 to 1.000) | 0.958 (0.857 to 1.000) | 0.019 (0.008 to 0.032) |
| mock_jev_ft_300 | mbrset | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.964 (0.939 to 0.985) | 0.998 (0.995 to 1.000) | 1.000 (1.000 to 1.000) | 0.027 (0.012 to 0.047) |
| mock_jev_ft_300 | messidor2 | 3 | 0.994 (0.981 to 1.000) | 1.000 (1.000 to 1.000) | 0.977 (0.954 to 0.995) | 0.994 (0.981 to 1.000) | 1.000 (1.000 to 1.000) | 0.014 (0.000 to 0.032) |
| mock_jev_ft_300 | ddr | 38 | 0.997 (0.992 to 1.000) | 0.974 (0.913 to 1.000) | 0.978 (0.961 to 0.992) | 0.995 (0.988 to 1.000) | 0.974 (0.913 to 1.000) | 0.014 (0.003 to 0.027) |
| mock_jev_ft_300 | eyepacs | 24 | 0.999 (0.995 to 1.000) | 1.000 (1.000 to 1.000) | 0.966 (0.950 to 0.981) | 0.998 (0.994 to 1.000) | 0.958 (0.862 to 1.000) | 0.027 (0.015 to 0.042) |
| mock_generative | mbrset | 24 | 0.998 (0.992 to 1.000) | 0.958 (0.852 to 1.000) | 0.979 (0.964 to 0.994) | 0.987 (0.969 to 0.998) | 0.958 (0.852 to 1.000) | 0.021 (0.009 to 0.037) |
| mock_generative | messidor2 | 3 | 0.995 (0.982 to 1.000) | 1.000 (1.000 to 1.000) | 0.968 (0.944 to 0.991) | 0.992 (0.977 to 1.000) | 1.000 (1.000 to 1.000) | 0.028 (0.009 to 0.051) |
| mock_generative | ddr | 38 | 0.999 (0.998 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.954 to 0.989) | 0.995 (0.988 to 0.999) | 1.000 (1.000 to 1.000) | 0.014 (0.003 to 0.027) |
| mock_generative | eyepacs | 24 | 0.998 (0.994 to 1.000) | 0.958 (0.864 to 1.000) | 0.981 (0.968 to 0.992) | 0.991 (0.980 to 0.998) | 0.958 (0.864 to 1.000) | 0.015 (0.006 to 0.026) |
| mock_specialist | mbrset | 24 | 0.998 (0.994 to 1.000) | 1.000 (1.000 to 1.000) | 0.976 (0.960 to 0.991) | 0.998 (0.994 to 1.000) | 0.917 (0.783 to 1.000) | 0.015 (0.003 to 0.029) |
| mock_specialist | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.949 to 0.991) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.023 (0.005 to 0.042) |
| mock_specialist | ddr | 38 | 0.991 (0.979 to 0.999) | 0.921 (0.833 to 1.000) | 0.975 (0.958 to 0.989) | 0.990 (0.978 to 0.998) | 0.921 (0.833 to 1.000) | 0.022 (0.008 to 0.038) |
| mock_specialist | eyepacs | 24 | 0.996 (0.989 to 1.000) | 0.958 (0.867 to 1.000) | 0.985 (0.974 to 0.996) | 0.996 (0.988 to 1.000) | 0.958 (0.867 to 1.000) | 0.011 (0.002 to 0.019) |
| mock_specialist_100 | mbrset | 24 | 0.998 (0.994 to 1.000) | 1.000 (1.000 to 1.000) | 0.976 (0.960 to 0.991) | 0.966 (0.941 to 0.987) | 0.917 (0.783 to 1.000) | 0.018 (0.006 to 0.033) |
| mock_specialist_100 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.949 to 0.991) | 0.957 (0.909 to 1.000) | 1.000 (1.000 to 1.000) | 0.028 (0.009 to 0.051) |
| mock_specialist_100 | ddr | 38 | 0.991 (0.979 to 0.999) | 0.921 (0.833 to 1.000) | 0.975 (0.958 to 0.989) | 0.931 (0.890 to 0.967) | 0.868 (0.750 to 0.971) | 0.017 (0.005 to 0.030) |
| mock_specialist_100 | eyepacs | 24 | 0.996 (0.989 to 1.000) | 0.958 (0.867 to 1.000) | 0.985 (0.974 to 0.996) | 0.943 (0.886 to 0.983) | 0.958 (0.867 to 1.000) | 0.011 (0.002 to 0.019) |
| mock_specialist_300 | mbrset | 24 | 0.998 (0.994 to 1.000) | 1.000 (1.000 to 1.000) | 0.976 (0.960 to 0.991) | 0.996 (0.990 to 1.000) | 0.917 (0.783 to 1.000) | 0.021 (0.009 to 0.037) |
| mock_specialist_300 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.949 to 0.991) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.023 (0.005 to 0.046) |
| mock_specialist_300 | ddr | 38 | 0.991 (0.979 to 0.999) | 0.921 (0.833 to 1.000) | 0.975 (0.958 to 0.989) | 0.981 (0.961 to 0.996) | 0.921 (0.833 to 1.000) | 0.014 (0.003 to 0.027) |
| mock_specialist_300 | eyepacs | 24 | 0.996 (0.989 to 1.000) | 0.958 (0.867 to 1.000) | 0.985 (0.974 to 0.996) | 0.992 (0.977 to 1.000) | 0.958 (0.867 to 1.000) | 0.015 (0.004 to 0.025) |

### Table 3b. Clinical decisions: referral, sight-threatening disease and maculopathy

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Refer, grade-only: sens / spec | Refer, action rule: sens / spec | Share referred under action rule | Sight-threatening, grade-only: AUROC | Sight-threatening, grade-only: sens / spec | Maculopathy AUROC | Refer, full definition: AUROC | Sight-threatening, full definition: AUROC |
|---|---|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.827 / 0.581 | 0.827 / 0.577 | 0.531 | 0.825 (0.751 to 0.888) | 0.763 / 0.691 | no labels | no labels | no labels |
| mock_jev_zs | mbrset | 0.836 / 0.599 | 0.836 / 0.589 | 0.606 | 0.811 (0.738 to 0.867) | 0.833 / 0.663 | 0.992 (0.985 to 0.997) | 0.797 (0.736 to 0.847) | 0.787 (0.716 to 0.843) |
| mock_jev_zs | messidor2 | 0.677 / 0.639 | 0.677 / 0.632 | 0.464 | 0.786 (0.687 to 0.868) | 0.706 / 0.710 | 0.985 (0.968 to 0.997) | 0.715 (0.641 to 0.787) | 0.739 (0.652 to 0.819) |
| mock_jev_zs | idrid | 0.739 / 0.608 | 0.754 / 0.608 | 0.600 | 0.777 (0.684 to 0.859) | 0.725 / 0.650 | 0.994 (0.984 to 1.000) | 0.746 (0.653 to 0.830) | 0.714 (0.621 to 0.803) |
| mock_jev_zs | ddr | 0.832 / 0.592 | 0.841 / 0.584 | 0.585 | 0.831 (0.764 to 0.892) | 0.800 / 0.702 | no labels | no labels | no labels |
| mock_jev_zs | eyepacs | 0.890 / 0.642 | 0.890 / 0.630 | 0.552 | 0.876 (0.835 to 0.914) | 0.795 / 0.784 | no labels | no labels | no labels |
| mock_jev_zs | pooled_external | 0.797 / 0.600 | 0.801 / 0.593 | 0.561 | 0.814 (0.781 to 0.845) | 0.785 / 0.688 | 0.991 (0.985 to 0.995) | 0.764 (0.724 to 0.801) | 0.761 (0.715 to 0.801) |
| mock_noabstain_zs | aptos | 0.877 / 0.491 | 0.877 / 0.486 | 0.611 | 0.795 (0.714 to 0.866) | 0.842 / 0.506 | no labels | no labels | no labels |
| mock_noabstain_zs | mbrset | 0.888 / 0.490 | 0.888 / 0.475 | 0.692 | 0.767 (0.693 to 0.835) | 0.833 / 0.516 | 0.998 (0.994 to 1.000) | 0.744 (0.679 to 0.802) | 0.722 (0.638 to 0.791) |
| mock_noabstain_zs | messidor2 | 0.790 / 0.523 | 0.790 / 0.523 | 0.573 | 0.788 (0.662 to 0.890) | 0.882 / 0.540 | 0.995 (0.987 to 0.999) | 0.719 (0.649 to 0.788) | 0.724 (0.642 to 0.803) |
| mock_noabstain_zs | idrid | 0.826 / 0.490 | 0.826 / 0.451 | 0.708 | 0.748 (0.650 to 0.834) | 0.825 / 0.450 | 0.996 (0.989 to 1.000) | 0.721 (0.629 to 0.811) | 0.670 (0.572 to 0.766) |
| mock_noabstain_zs | ddr | 0.860 / 0.467 | 0.860 / 0.455 | 0.672 | 0.769 (0.700 to 0.831) | 0.860 / 0.545 | no labels | no labels | no labels |
| mock_noabstain_zs | eyepacs | 0.904 / 0.524 | 0.911 / 0.500 | 0.644 | 0.854 (0.806 to 0.897) | 0.872 / 0.553 | no labels | no labels | no labels |
| mock_noabstain_zs | pooled_external | 0.857 / 0.489 | 0.857 / 0.479 | 0.651 | 0.780 (0.746 to 0.813) | 0.843 / 0.521 | 0.996 (0.994 to 0.999) | 0.737 (0.694 to 0.776) | 0.716 (0.668 to 0.762) |
| mock_jev_ft | aptos | 0.852 / 0.928 | 0.852 / 0.899 | 0.302 | 0.971 (0.954 to 0.985) | 0.842 / 0.943 | no labels | no labels | no labels |
| mock_jev_ft | mbrset | 0.847 / 0.884 | 0.854 / 0.861 | 0.463 | 0.963 (0.946 to 0.978) | 0.814 / 0.930 | 0.995 (0.989 to 1.000) | 0.926 (0.898 to 0.949) | 0.913 (0.873 to 0.943) |
| mock_jev_ft | messidor2 | 0.750 / 0.903 | 0.758 / 0.897 | 0.300 | 0.947 (0.911 to 0.979) | 0.735 / 0.927 | 0.991 (0.979 to 0.998) | 0.864 (0.817 to 0.907) | 0.793 (0.718 to 0.864) |
| mock_jev_ft | idrid | 0.855 / 0.931 | 0.855 / 0.892 | 0.538 | 0.950 (0.920 to 0.975) | 0.812 / 0.900 | 0.995 (0.988 to 0.999) | 0.943 (0.914 to 0.968) | 0.903 (0.858 to 0.944) |
| mock_jev_ft | ddr | 0.836 / 0.929 | 0.836 / 0.908 | 0.378 | 0.972 (0.960 to 0.983) | 0.820 / 0.942 | no labels | no labels | no labels |
| mock_jev_ft | eyepacs | 0.866 / 0.927 | 0.870 / 0.911 | 0.361 | 0.976 (0.964 to 0.985) | 0.846 / 0.957 | no labels | no labels | no labels |
| mock_jev_ft | pooled_external | 0.833 / 0.914 | 0.837 / 0.892 | 0.385 | 0.965 (0.957 to 0.972) | 0.814 / 0.934 | 0.994 (0.989 to 0.997) | 0.912 (0.892 to 0.931) | 0.882 (0.852 to 0.907) |
| mock_jev_ft_100 | aptos | 0.815 / 0.788 | 0.815 / 0.779 | 0.380 | 0.919 (0.860 to 0.965) | 0.868 / 0.796 | no labels | no labels | no labels |
| mock_jev_ft_100 | mbrset | 0.784 / 0.787 | 0.784 / 0.777 | 0.483 | 0.903 (0.856 to 0.943) | 0.897 / 0.783 | 0.995 (0.988 to 0.999) | 0.870 (0.823 to 0.910) | 0.859 (0.802 to 0.905) |
| mock_jev_ft_100 | messidor2 | 0.677 / 0.735 | 0.677 / 0.729 | 0.395 | 0.916 (0.857 to 0.964) | 0.941 / 0.770 | 0.995 (0.984 to 1.000) | 0.759 (0.689 to 0.822) | 0.748 (0.660 to 0.833) |
| mock_jev_ft_100 | idrid | 0.783 / 0.824 | 0.783 / 0.804 | 0.533 | 0.889 (0.826 to 0.943) | 0.850 / 0.713 | 0.993 (0.981 to 1.000) | 0.891 (0.830 to 0.939) | 0.841 (0.774 to 0.906) |
| mock_jev_ft_100 | ddr | 0.776 / 0.780 | 0.785 / 0.757 | 0.458 | 0.903 (0.860 to 0.938) | 0.880 / 0.798 | no labels | no labels | no labels |
| mock_jev_ft_100 | eyepacs | 0.890 / 0.779 | 0.890 / 0.761 | 0.466 | 0.933 (0.909 to 0.955) | 0.936 / 0.796 | no labels | no labels | no labels |
| mock_jev_ft_100 | pooled_external | 0.773 / 0.779 | 0.775 / 0.765 | 0.444 | 0.907 (0.886 to 0.928) | 0.883 / 0.783 | 0.995 (0.991 to 0.998) | 0.843 (0.811 to 0.873) | 0.828 (0.790 to 0.865) |
| mock_jev_ft_300 | aptos | 0.852 / 0.811 | 0.852 / 0.788 | 0.383 | 0.973 (0.955 to 0.987) | 0.921 / 0.917 | no labels | no labels | no labels |
| mock_jev_ft_300 | mbrset | 0.851 / 0.718 | 0.858 / 0.698 | 0.556 | 0.931 (0.901 to 0.958) | 0.808 / 0.903 | 0.980 (0.952 to 0.998) | 0.870 (0.826 to 0.907) | 0.876 (0.824 to 0.917) |
| mock_jev_ft_300 | messidor2 | 0.790 / 0.852 | 0.790 / 0.819 | 0.364 | 0.932 (0.883 to 0.976) | 0.765 / 0.895 | 0.980 (0.951 to 0.998) | 0.814 (0.742 to 0.878) | 0.749 (0.653 to 0.837) |
| mock_jev_ft_300 | idrid | 0.841 / 0.922 | 0.841 / 0.922 | 0.517 | 0.953 (0.914 to 0.981) | 0.850 / 0.912 | 0.987 (0.970 to 0.997) | 0.947 (0.905 to 0.978) | 0.904 (0.847 to 0.951) |
| mock_jev_ft_300 | ddr | 0.869 / 0.859 | 0.869 / 0.831 | 0.435 | 0.937 (0.908 to 0.962) | 0.760 / 0.904 | no labels | no labels | no labels |
| mock_jev_ft_300 | eyepacs | 0.863 / 0.827 | 0.863 / 0.794 | 0.436 | 0.963 (0.944 to 0.979) | 0.808 / 0.957 | no labels | no labels | no labels |
| mock_jev_ft_300 | pooled_external | 0.845 / 0.817 | 0.848 / 0.793 | 0.450 | 0.946 (0.931 to 0.957) | 0.821 / 0.906 | 0.983 (0.969 to 0.994) | 0.867 (0.837 to 0.895) | 0.849 (0.813 to 0.882) |
| mock_generative | aptos | 0.901 / 0.896 | 0.901 / 0.874 | 0.333 | 0.972 (0.954 to 0.987) | 0.895 / 0.928 | no labels | no labels | no labels |
| mock_generative | mbrset | 0.873 / 0.802 | 0.881 / 0.787 | 0.514 | 0.961 (0.941 to 0.978) | 0.936 / 0.899 | 0.985 (0.959 to 0.999) | 0.914 (0.876 to 0.945) | 0.916 (0.873 to 0.950) |
| mock_generative | messidor2 | 0.871 / 0.832 | 0.887 / 0.819 | 0.391 | 0.978 (0.955 to 0.993) | 1.000 / 0.880 | 0.998 (0.995 to 1.000) | 0.845 (0.782 to 0.901) | 0.738 (0.646 to 0.828) |
| mock_generative | idrid | 0.971 / 0.863 | 0.971 / 0.863 | 0.617 | 0.936 (0.890 to 0.971) | 0.875 / 0.775 | 0.991 (0.977 to 1.000) | 0.973 (0.943 to 0.993) | 0.900 (0.841 to 0.951) |
| mock_generative | ddr | 0.850 / 0.816 | 0.850 / 0.784 | 0.460 | 0.935 (0.902 to 0.962) | 0.780 / 0.891 | no labels | no labels | no labels |
| mock_generative | eyepacs | 0.925 / 0.861 | 0.925 / 0.842 | 0.422 | 0.976 (0.960 to 0.988) | 0.949 / 0.925 | no labels | no labels | no labels |
| mock_generative | pooled_external | 0.887 / 0.838 | 0.892 / 0.818 | 0.449 | 0.958 (0.948 to 0.969) | 0.888 / 0.891 | 0.991 (0.981 to 0.998) | 0.909 (0.885 to 0.932) | 0.874 (0.837 to 0.906) |
| mock_specialist | aptos | 0.815 / 0.923 | 0.815 / 0.896 | 0.294 | 0.983 (0.969 to 0.993) | 0.895 / 0.943 | no labels | no labels | no labels |
| mock_specialist | mbrset | 0.858 / 0.881 | 0.858 / 0.847 | 0.472 | 0.967 (0.946 to 0.983) | 0.910 / 0.895 | 0.990 (0.980 to 0.997) | 0.937 (0.906 to 0.961) | 0.913 (0.865 to 0.949) |
| mock_specialist | messidor2 | 0.758 / 0.935 | 0.774 / 0.916 | 0.291 | 0.967 (0.938 to 0.989) | 0.824 / 0.905 | 0.991 (0.980 to 0.998) | 0.881 (0.822 to 0.935) | 0.788 (0.701 to 0.869) |
| mock_specialist | idrid | 0.797 / 0.980 | 0.797 / 0.980 | 0.467 | 0.979 (0.957 to 0.994) | 0.925 / 0.925 | 0.995 (0.987 to 1.000) | 0.968 (0.939 to 0.990) | 0.934 (0.889 to 0.969) |
| mock_specialist | ddr | 0.832 / 0.961 | 0.832 / 0.937 | 0.355 | 0.979 (0.962 to 0.991) | 0.820 / 0.952 | no labels | no labels | no labels |
| mock_specialist | eyepacs | 0.877 / 0.933 | 0.877 / 0.921 | 0.356 | 0.989 (0.981 to 0.995) | 0.936 / 0.947 | no labels | no labels | no labels |
| mock_specialist | pooled_external | 0.821 / 0.930 | 0.823 / 0.905 | 0.371 | 0.975 (0.967 to 0.983) | 0.883 / 0.926 | 0.992 (0.987 to 0.996) | 0.925 (0.902 to 0.944) | 0.883 (0.850 to 0.914) |
| mock_specialist_100 | aptos | 0.840 / 0.572 | 0.840 / 0.550 | 0.554 | 0.835 (0.773 to 0.893) | 0.789 / 0.657 | no labels | no labels | no labels |
| mock_specialist_100 | mbrset | 0.858 / 0.589 | 0.858 / 0.564 | 0.631 | 0.858 (0.807 to 0.902) | 0.846 / 0.671 | 0.990 (0.980 to 0.997) | 0.822 (0.774 to 0.864) | 0.810 (0.753 to 0.858) |
| mock_specialist_100 | messidor2 | 0.774 / 0.626 | 0.790 / 0.613 | 0.509 | 0.834 (0.752 to 0.908) | 0.824 / 0.675 | 0.991 (0.980 to 0.998) | 0.739 (0.661 to 0.814) | 0.680 (0.585 to 0.772) |
| mock_specialist_100 | idrid | 0.783 / 0.647 | 0.783 / 0.647 | 0.600 | 0.891 (0.829 to 0.945) | 0.875 / 0.775 | 0.995 (0.987 to 1.000) | 0.811 (0.730 to 0.877) | 0.781 (0.692 to 0.855) |
| mock_specialist_100 | ddr | 0.832 / 0.659 | 0.832 / 0.639 | 0.547 | 0.866 (0.809 to 0.915) | 0.800 / 0.737 | no labels | no labels | no labels |
| mock_specialist_100 | eyepacs | 0.904 / 0.664 | 0.904 / 0.658 | 0.538 | 0.923 (0.893 to 0.948) | 0.949 / 0.754 | no labels | no labels | no labels |
| mock_specialist_100 | pooled_external | 0.826 / 0.615 | 0.828 / 0.595 | 0.569 | 0.860 (0.834 to 0.882) | 0.830 / 0.694 | 0.992 (0.987 to 0.996) | 0.793 (0.759 to 0.828) | 0.764 (0.723 to 0.805) |
| mock_specialist_300 | aptos | 0.914 / 0.707 | 0.914 / 0.685 | 0.475 | 0.934 (0.900 to 0.963) | 0.816 / 0.830 | no labels | no labels | no labels |
| mock_specialist_300 | mbrset | 0.873 / 0.693 | 0.873 / 0.658 | 0.583 | 0.921 (0.880 to 0.953) | 0.846 / 0.806 | 0.990 (0.980 to 0.997) | 0.875 (0.830 to 0.912) | 0.871 (0.817 to 0.914) |
| mock_specialist_300 | messidor2 | 0.806 / 0.761 | 0.823 / 0.748 | 0.423 | 0.916 (0.859 to 0.961) | 0.882 / 0.825 | 0.991 (0.980 to 0.998) | 0.813 (0.743 to 0.878) | 0.741 (0.651 to 0.825) |
| mock_specialist_300 | idrid | 0.797 / 0.804 | 0.797 / 0.804 | 0.542 | 0.945 (0.904 to 0.978) | 0.875 / 0.887 | 0.995 (0.987 to 1.000) | 0.898 (0.839 to 0.945) | 0.867 (0.798 to 0.921) |
| mock_specialist_300 | ddr | 0.860 / 0.808 | 0.860 / 0.784 | 0.460 | 0.933 (0.894 to 0.963) | 0.800 / 0.875 | no labels | no labels | no labels |
| mock_specialist_300 | eyepacs | 0.911 / 0.806 | 0.911 / 0.794 | 0.450 | 0.972 (0.956 to 0.985) | 0.936 / 0.882 | no labels | no labels | no labels |
| mock_specialist_300 | pooled_external | 0.857 / 0.748 | 0.859 / 0.725 | 0.496 | 0.929 (0.912 to 0.944) | 0.839 / 0.840 | 0.992 (0.987 to 0.996) | 0.860 (0.832 to 0.888) | 0.832 (0.795 to 0.868) |

Action rule: refer if referable disease, ungradeable, or the model abstains. Full definition adds maculopathy and is reported only where maculopathy is labelled.

### Table 3c. Coherence of the five answers, direct versus derived referral, patient-level referral

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Coherent answers | Referable AUROC, direct | Referable AUROC, derived | Direct minus derived | Patient-level refer: sens / spec |
|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.843 (0.801 to 0.883) | 0.809 | 0.802 | 0.007 (-0.003 to 0.018) | 0.827 / 0.577 |
| mock_jev_zs | mbrset | 0.847 (0.810 to 0.881) | 0.821 | 0.812 | 0.009 (-0.002 to 0.020) | 0.957 / 0.114 |
| mock_jev_zs | messidor2 | 0.851 (0.802 to 0.896) | 0.737 | 0.739 | -0.002 (-0.019 to 0.015) | 0.677 / 0.632 |
| mock_jev_zs | idrid | 0.780 (0.701 to 0.852) | 0.763 | 0.749 | 0.014 (-0.008 to 0.041) | 0.754 / 0.608 |
| mock_jev_zs | ddr | 0.849 (0.811 to 0.884) | 0.818 | 0.818 | 0.000 (-0.011 to 0.011) | 0.841 / 0.584 |
| mock_jev_zs | eyepacs | 0.861 (0.829 to 0.891) | 0.860 | 0.856 | 0.003 (-0.004 to 0.010) | 0.965 / 0.442 |
| mock_noabstain_zs | aptos | 0.863 (0.824 to 0.900) | 0.796 | 0.793 | 0.003 (-0.006 to 0.012) | 0.877 / 0.486 |
| mock_noabstain_zs | mbrset | 0.862 (0.825 to 0.897) | 0.758 | 0.756 | 0.002 (-0.009 to 0.013) | 0.978 / 0.045 |
| mock_noabstain_zs | messidor2 | 0.789 (0.730 to 0.841) | 0.735 | 0.735 | 0.000 (-0.014 to 0.014) | 0.790 / 0.523 |
| mock_noabstain_zs | idrid | 0.795 (0.720 to 0.866) | 0.735 | 0.725 | 0.010 (-0.013 to 0.034) | 0.826 / 0.451 |
| mock_noabstain_zs | ddr | 0.858 (0.822 to 0.893) | 0.727 | 0.715 | 0.012 (0.002 to 0.021) | 0.860 / 0.455 |
| mock_noabstain_zs | eyepacs | 0.816 (0.781 to 0.851) | 0.823 | 0.821 | 0.002 (-0.005 to 0.009) | 0.965 / 0.264 |
| mock_jev_ft | aptos | 0.824 (0.791 to 0.854) | 0.950 | 0.954 | -0.004 (-0.014 to 0.004) | 0.852 / 0.899 |
| mock_jev_ft | mbrset | 0.863 (0.832 to 0.891) | 0.944 | 0.950 | -0.006 (-0.014 to 0.000) | 0.978 / 0.659 |
| mock_jev_ft | messidor2 | 0.816 (0.772 to 0.858) | 0.920 | 0.931 | -0.011 (-0.021 to -0.002) | 0.758 / 0.897 |
| mock_jev_ft | idrid | 0.758 (0.695 to 0.817) | 0.954 | 0.962 | -0.008 (-0.018 to 0.001) | 0.855 / 0.892 |
| mock_jev_ft | ddr | 0.818 (0.789 to 0.846) | 0.960 | 0.961 | -0.002 (-0.007 to 0.005) | 0.836 / 0.908 |
| mock_jev_ft | eyepacs | 0.816 (0.791 to 0.841) | 0.965 | 0.971 | -0.006 (-0.011 to -0.001) | 0.913 / 0.844 |
| mock_jev_ft_100 | aptos | 0.827 (0.784 to 0.867) | 0.902 | 0.901 | 0.001 (-0.007 to 0.007) | 0.815 / 0.779 |
| mock_jev_ft_100 | mbrset | 0.845 (0.802 to 0.885) | 0.883 | 0.883 | -0.000 (-0.009 to 0.008) | 0.913 / 0.455 |
| mock_jev_ft_100 | messidor2 | 0.796 (0.743 to 0.850) | 0.809 | 0.820 | -0.011 (-0.026 to 0.003) | 0.677 / 0.729 |
| mock_jev_ft_100 | idrid | 0.831 (0.754 to 0.897) | 0.893 | 0.900 | -0.006 (-0.021 to 0.007) | 0.783 / 0.804 |
| mock_jev_ft_100 | ddr | 0.823 (0.784 to 0.862) | 0.874 | 0.874 | -0.000 (-0.010 to 0.009) | 0.785 / 0.757 |
| mock_jev_ft_100 | eyepacs | 0.821 (0.787 to 0.853) | 0.923 | 0.930 | -0.008 (-0.015 to -0.001) | 0.930 / 0.601 |
| mock_jev_ft_300 | aptos | 0.856 (0.815 to 0.894) | 0.925 | 0.932 | -0.007 (-0.018 to 0.003) | 0.852 / 0.788 |
| mock_jev_ft_300 | mbrset | 0.843 (0.800 to 0.883) | 0.886 | 0.892 | -0.005 (-0.016 to 0.004) | 0.957 / 0.273 |
| mock_jev_ft_300 | messidor2 | 0.738 (0.678 to 0.798) | 0.876 | 0.889 | -0.013 (-0.032 to 0.002) | 0.790 / 0.819 |
| mock_jev_ft_300 | idrid | 0.767 (0.692 to 0.842) | 0.948 | 0.955 | -0.007 (-0.017 to 0.003) | 0.841 / 0.922 |
| mock_jev_ft_300 | ddr | 0.818 (0.778 to 0.860) | 0.928 | 0.923 | 0.005 (-0.002 to 0.013) | 0.869 / 0.831 |
| mock_jev_ft_300 | eyepacs | 0.803 (0.765 to 0.840) | 0.928 | 0.938 | -0.010 (-0.019 to 0.001) | 0.942 / 0.699 |
| mock_generative | aptos | 0.842 (0.803 to 0.881) | 0.964 | 0.964 | -0.000 (-0.007 to 0.006) | 0.901 / 0.874 |
| mock_generative | mbrset | 0.860 (0.821 to 0.897) | 0.931 | 0.930 | 0.001 (-0.006 to 0.008) | 0.935 / 0.477 |
| mock_generative | messidor2 | 0.820 (0.765 to 0.869) | 0.939 | 0.936 | 0.003 (-0.006 to 0.013) | 0.887 / 0.819 |
| mock_generative | idrid | 0.773 (0.700 to 0.847) | 0.973 | 0.973 | 0.000 (-0.010 to 0.010) | 0.971 / 0.863 |
| mock_generative | ddr | 0.863 (0.826 to 0.894) | 0.928 | 0.928 | 0.000 (-0.007 to 0.007) | 0.850 / 0.784 |
| mock_generative | eyepacs | 0.811 (0.773 to 0.844) | 0.968 | 0.967 | 0.001 (-0.003 to 0.006) | 0.977 / 0.730 |
| mock_specialist | aptos | 0.817 (0.771 to 0.858) | 0.957 | 0.958 | -0.001 (-0.011 to 0.009) | 0.815 / 0.896 |
| mock_specialist | mbrset | 0.849 (0.808 to 0.885) | 0.954 | 0.962 | -0.008 (-0.016 to -0.000) | 0.978 / 0.682 |
| mock_specialist | messidor2 | 0.797 (0.742 to 0.847) | 0.948 | 0.947 | 0.000 (-0.010 to 0.011) | 0.774 / 0.916 |
| mock_specialist | idrid | 0.773 (0.700 to 0.847) | 0.972 | 0.980 | -0.008 (-0.027 to 0.009) | 0.797 / 0.980 |
| mock_specialist | ddr | 0.852 (0.812 to 0.887) | 0.967 | 0.972 | -0.005 (-0.013 to 0.002) | 0.832 / 0.937 |
| mock_specialist | eyepacs | 0.824 (0.787 to 0.858) | 0.971 | 0.977 | -0.006 (-0.011 to -0.002) | 0.953 / 0.871 |
| mock_specialist_100 | aptos | 0.804 (0.759 to 0.847) | 0.789 | 0.790 | -0.001 (-0.012 to 0.009) | 0.840 / 0.550 |
| mock_specialist_100 | mbrset | 0.854 (0.822 to 0.885) | 0.839 | 0.835 | 0.004 (-0.003 to 0.012) | 1.000 / 0.205 |
| mock_specialist_100 | messidor2 | 0.810 (0.757 to 0.860) | 0.780 | 0.781 | -0.001 (-0.012 to 0.010) | 0.790 / 0.613 |
| mock_specialist_100 | idrid | 0.731 (0.650 to 0.808) | 0.820 | 0.818 | 0.002 (-0.011 to 0.017) | 0.783 / 0.647 |
| mock_specialist_100 | ddr | 0.807 (0.765 to 0.849) | 0.845 | 0.839 | 0.007 (-0.002 to 0.016) | 0.832 / 0.639 |
| mock_specialist_100 | eyepacs | 0.816 (0.779 to 0.853) | 0.877 | 0.881 | -0.004 (-0.011 to 0.002) | 0.942 / 0.466 |
| mock_specialist_300 | aptos | 0.801 (0.754 to 0.844) | 0.888 | 0.883 | 0.005 (-0.005 to 0.015) | 0.914 / 0.685 |
| mock_specialist_300 | mbrset | 0.838 (0.801 to 0.874) | 0.893 | 0.905 | -0.012 (-0.022 to -0.002) | 1.000 / 0.295 |
| mock_specialist_300 | messidor2 | 0.768 (0.709 to 0.822) | 0.865 | 0.864 | 0.001 (-0.013 to 0.014) | 0.823 / 0.748 |
| mock_specialist_300 | idrid | 0.756 (0.681 to 0.831) | 0.907 | 0.907 | -0.001 (-0.017 to 0.016) | 0.797 / 0.804 |
| mock_specialist_300 | ddr | 0.855 (0.818 to 0.889) | 0.917 | 0.921 | -0.003 (-0.012 to 0.005) | 0.860 / 0.784 |
| mock_specialist_300 | eyepacs | 0.796 (0.758 to 0.833) | 0.937 | 0.938 | -0.001 (-0.007 to 0.005) | 0.942 / 0.663 |

Coherent: the referral and sight-threatening answers agree with the grade and maculopathy answers. Patient level uses the worse eye and equals image level where a dataset has no patient identifiers.

### Table 4a. Sensitivity to question wording (fixed subset of each test set)

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Metric | Wordings | Mean | Lowest | Highest | Range |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | qwk | 3 | 0.46 | 0.448 | 0.473 | 0.025 |
| mock_jev_zs | aptos | ref_auroc | 3 | 0.8 | 0.794 | 0.805 | 0.011 |
| mock_jev_zs | aptos | ece_grade | 3 | 0.154 | 0.143 | 0.161 | 0.017 |
| mock_jev_zs | ddr | qwk | 3 | 0.483 | 0.478 | 0.488 | 0.01 |
| mock_jev_zs | ddr | ref_auroc | 3 | 0.808 | 0.806 | 0.81 | 0.003 |
| mock_jev_zs | ddr | ece_grade | 3 | 0.145 | 0.123 | 0.174 | 0.051 |
| mock_jev_zs | idrid | qwk | 3 | 0.467 | 0.463 | 0.471 | 0.008 |
| mock_jev_zs | idrid | ref_auroc | 3 | 0.768 | 0.763 | 0.771 | 0.008 |
| mock_jev_zs | idrid | ece_grade | 3 | 0.106 | 0.088 | 0.132 | 0.043 |
| mock_jev_zs | mbrset | qwk | 3 | 0.506 | 0.494 | 0.519 | 0.025 |
| mock_jev_zs | mbrset | ref_auroc | 3 | 0.831 | 0.828 | 0.835 | 0.007 |
| mock_jev_zs | mbrset | ece_grade | 3 | 0.105 | 0.072 | 0.123 | 0.051 |
| mock_jev_zs | messidor2 | qwk | 3 | 0.341 | 0.334 | 0.349 | 0.015 |
| mock_jev_zs | messidor2 | ref_auroc | 3 | 0.765 | 0.764 | 0.767 | 0.003 |
| mock_jev_zs | messidor2 | ece_grade | 3 | 0.13 | 0.128 | 0.132 | 0.005 |
| mock_jev_zs | eyepacs | qwk | 3 | 0.653 | 0.643 | 0.663 | 0.02 |
| mock_jev_zs | eyepacs | ref_auroc | 3 | 0.839 | 0.835 | 0.844 | 0.009 |
| mock_jev_zs | eyepacs | ece_grade | 3 | 0.084 | 0.07 | 0.094 | 0.024 |
| mock_noabstain_zs | aptos | qwk | 3 | 0.505 | 0.493 | 0.522 | 0.03 |
| mock_noabstain_zs | aptos | ref_auroc | 3 | 0.815 | 0.809 | 0.822 | 0.013 |
| mock_noabstain_zs | aptos | ece_grade | 3 | 0.213 | 0.203 | 0.227 | 0.024 |
| mock_noabstain_zs | ddr | qwk | 3 | 0.335 | 0.328 | 0.342 | 0.014 |
| mock_noabstain_zs | ddr | ref_auroc | 3 | 0.686 | 0.675 | 0.695 | 0.02 |
| mock_noabstain_zs | ddr | ece_grade | 3 | 0.181 | 0.162 | 0.203 | 0.041 |
| mock_noabstain_zs | idrid | qwk | 3 | 0.427 | 0.423 | 0.433 | 0.01 |
| mock_noabstain_zs | idrid | ref_auroc | 3 | 0.738 | 0.735 | 0.742 | 0.007 |
| mock_noabstain_zs | idrid | ece_grade | 3 | 0.08 | 0.057 | 0.094 | 0.037 |
| mock_noabstain_zs | mbrset | qwk | 3 | 0.417 | 0.41 | 0.424 | 0.014 |
| mock_noabstain_zs | mbrset | ref_auroc | 3 | 0.734 | 0.733 | 0.735 | 0.003 |
| mock_noabstain_zs | mbrset | ece_grade | 3 | 0.107 | 0.099 | 0.115 | 0.016 |
| mock_noabstain_zs | messidor2 | qwk | 3 | 0.361 | 0.35 | 0.37 | 0.02 |
| mock_noabstain_zs | messidor2 | ref_auroc | 3 | 0.761 | 0.753 | 0.765 | 0.011 |
| mock_noabstain_zs | messidor2 | ece_grade | 3 | 0.133 | 0.125 | 0.145 | 0.019 |
| mock_noabstain_zs | eyepacs | qwk | 3 | 0.621 | 0.6 | 0.642 | 0.042 |
| mock_noabstain_zs | eyepacs | ref_auroc | 3 | 0.853 | 0.848 | 0.858 | 0.009 |
| mock_noabstain_zs | eyepacs | ece_grade | 3 | 0.142 | 0.124 | 0.151 | 0.027 |
| mock_jev_ft | aptos | qwk | 3 | 0.815 | 0.804 | 0.826 | 0.022 |
| mock_jev_ft | aptos | ref_auroc | 3 | 0.935 | 0.928 | 0.94 | 0.012 |
| mock_jev_ft | aptos | ece_grade | 3 | 0.163 | 0.139 | 0.187 | 0.049 |
| mock_jev_ft | ddr | qwk | 3 | 0.868 | 0.857 | 0.876 | 0.019 |
| mock_jev_ft | ddr | ref_auroc | 3 | 0.97 | 0.965 | 0.974 | 0.009 |
| mock_jev_ft | ddr | ece_grade | 3 | 0.123 | 0.093 | 0.148 | 0.055 |
| mock_jev_ft | idrid | qwk | 3 | 0.873 | 0.872 | 0.874 | 0.003 |
| mock_jev_ft | idrid | ref_auroc | 3 | 0.955 | 0.954 | 0.956 | 0.001 |
| mock_jev_ft | idrid | ece_grade | 3 | 0.145 | 0.141 | 0.15 | 0.009 |
| mock_jev_ft | mbrset | qwk | 3 | 0.86 | 0.859 | 0.863 | 0.004 |
| mock_jev_ft | mbrset | ref_auroc | 3 | 0.948 | 0.946 | 0.951 | 0.005 |
| mock_jev_ft | mbrset | ece_grade | 3 | 0.147 | 0.141 | 0.16 | 0.019 |
| mock_jev_ft | messidor2 | qwk | 3 | 0.806 | 0.798 | 0.811 | 0.012 |
| mock_jev_ft | messidor2 | ref_auroc | 3 | 0.921 | 0.917 | 0.926 | 0.009 |
| mock_jev_ft | messidor2 | ece_grade | 3 | 0.12 | 0.109 | 0.133 | 0.024 |
| mock_jev_ft | eyepacs | qwk | 3 | 0.864 | 0.861 | 0.868 | 0.007 |
| mock_jev_ft | eyepacs | ref_auroc | 3 | 0.959 | 0.955 | 0.962 | 0.007 |
| mock_jev_ft | eyepacs | ece_grade | 3 | 0.099 | 0.089 | 0.111 | 0.022 |
| mock_jev_ft_100 | aptos | qwk | 3 | 0.767 | 0.758 | 0.773 | 0.014 |
| mock_jev_ft_100 | aptos | ref_auroc | 3 | 0.919 | 0.907 | 0.928 | 0.021 |
| mock_jev_ft_100 | aptos | ece_grade | 3 | 0.129 | 0.106 | 0.143 | 0.037 |
| mock_jev_ft_100 | ddr | qwk | 3 | 0.61 | 0.597 | 0.619 | 0.021 |
| mock_jev_ft_100 | ddr | ref_auroc | 3 | 0.849 | 0.847 | 0.85 | 0.004 |
| mock_jev_ft_100 | ddr | ece_grade | 3 | 0.12 | 0.114 | 0.126 | 0.013 |
| mock_jev_ft_100 | idrid | qwk | 3 | 0.757 | 0.754 | 0.76 | 0.006 |
| mock_jev_ft_100 | idrid | ref_auroc | 3 | 0.894 | 0.89 | 0.897 | 0.007 |
| mock_jev_ft_100 | idrid | ece_grade | 3 | 0.175 | 0.16 | 0.196 | 0.036 |
| mock_jev_ft_100 | mbrset | qwk | 3 | 0.694 | 0.687 | 0.7 | 0.013 |
| mock_jev_ft_100 | mbrset | ref_auroc | 3 | 0.855 | 0.849 | 0.861 | 0.012 |
| mock_jev_ft_100 | mbrset | ece_grade | 3 | 0.204 | 0.2 | 0.207 | 0.007 |
| mock_jev_ft_100 | messidor2 | qwk | 3 | 0.621 | 0.61 | 0.64 | 0.031 |
| mock_jev_ft_100 | messidor2 | ref_auroc | 3 | 0.839 | 0.83 | 0.846 | 0.016 |
| mock_jev_ft_100 | messidor2 | ece_grade | 3 | 0.116 | 0.107 | 0.13 | 0.022 |
| mock_jev_ft_100 | eyepacs | qwk | 3 | 0.766 | 0.758 | 0.775 | 0.016 |
| mock_jev_ft_100 | eyepacs | ref_auroc | 3 | 0.901 | 0.893 | 0.91 | 0.016 |
| mock_jev_ft_100 | eyepacs | ece_grade | 3 | 0.142 | 0.124 | 0.153 | 0.029 |
| mock_jev_ft_300 | aptos | qwk | 3 | 0.816 | 0.806 | 0.828 | 0.022 |
| mock_jev_ft_300 | aptos | ref_auroc | 3 | 0.963 | 0.958 | 0.97 | 0.013 |
| mock_jev_ft_300 | aptos | ece_grade | 3 | 0.128 | 0.119 | 0.139 | 0.021 |
| mock_jev_ft_300 | ddr | qwk | 3 | 0.783 | 0.767 | 0.798 | 0.032 |
| mock_jev_ft_300 | ddr | ref_auroc | 3 | 0.916 | 0.912 | 0.924 | 0.012 |
| mock_jev_ft_300 | ddr | ece_grade | 3 | 0.139 | 0.137 | 0.142 | 0.005 |
| mock_jev_ft_300 | idrid | qwk | 3 | 0.852 | 0.848 | 0.856 | 0.008 |
| mock_jev_ft_300 | idrid | ref_auroc | 3 | 0.943 | 0.937 | 0.948 | 0.011 |
| mock_jev_ft_300 | idrid | ece_grade | 3 | 0.078 | 0.058 | 0.091 | 0.033 |
| mock_jev_ft_300 | mbrset | qwk | 3 | 0.792 | 0.783 | 0.804 | 0.021 |
| mock_jev_ft_300 | mbrset | ref_auroc | 3 | 0.915 | 0.909 | 0.919 | 0.01 |
| mock_jev_ft_300 | mbrset | ece_grade | 3 | 0.138 | 0.136 | 0.14 | 0.005 |
| mock_jev_ft_300 | messidor2 | qwk | 3 | 0.646 | 0.618 | 0.673 | 0.055 |
| mock_jev_ft_300 | messidor2 | ref_auroc | 3 | 0.903 | 0.894 | 0.907 | 0.014 |
| mock_jev_ft_300 | messidor2 | ece_grade | 3 | 0.145 | 0.141 | 0.151 | 0.01 |
| mock_jev_ft_300 | eyepacs | qwk | 3 | 0.808 | 0.781 | 0.825 | 0.044 |
| mock_jev_ft_300 | eyepacs | ref_auroc | 3 | 0.918 | 0.907 | 0.927 | 0.02 |
| mock_jev_ft_300 | eyepacs | ece_grade | 3 | 0.107 | 0.074 | 0.156 | 0.083 |
| mock_generative | aptos | qwk | 3 | 0.835 | 0.832 | 0.837 | 0.005 |
| mock_generative | aptos | ref_auroc | 3 | 0.954 | 0.947 | 0.961 | 0.014 |
| mock_generative | aptos | ece_grade | 3 | 0.123 | 0.109 | 0.138 | 0.028 |
| mock_generative | ddr | qwk | 3 | 0.768 | 0.757 | 0.778 | 0.021 |
| mock_generative | ddr | ref_auroc | 3 | 0.922 | 0.919 | 0.925 | 0.006 |
| mock_generative | ddr | ece_grade | 3 | 0.185 | 0.146 | 0.236 | 0.09 |
| mock_generative | idrid | qwk | 3 | 0.871 | 0.864 | 0.874 | 0.01 |
| mock_generative | idrid | ref_auroc | 3 | 0.974 | 0.973 | 0.974 | 0.001 |
| mock_generative | idrid | ece_grade | 3 | 0.104 | 0.099 | 0.109 | 0.01 |
| mock_generative | mbrset | qwk | 3 | 0.848 | 0.845 | 0.851 | 0.006 |
| mock_generative | mbrset | ref_auroc | 3 | 0.92 | 0.919 | 0.922 | 0.003 |
| mock_generative | mbrset | ece_grade | 3 | 0.09 | 0.069 | 0.105 | 0.036 |
| mock_generative | messidor2 | qwk | 3 | 0.768 | 0.764 | 0.772 | 0.008 |
| mock_generative | messidor2 | ref_auroc | 3 | 0.93 | 0.926 | 0.932 | 0.006 |
| mock_generative | messidor2 | ece_grade | 3 | 0.139 | 0.118 | 0.159 | 0.041 |
| mock_generative | eyepacs | qwk | 3 | 0.886 | 0.881 | 0.89 | 0.008 |
| mock_generative | eyepacs | ref_auroc | 3 | 0.971 | 0.968 | 0.973 | 0.005 |
| mock_generative | eyepacs | ece_grade | 3 | 0.065 | 0.061 | 0.07 | 0.008 |
| mock_specialist | aptos | qwk | 3 | 0.813 | 0.809 | 0.819 | 0.009 |
| mock_specialist | aptos | ref_auroc | 3 | 0.968 | 0.967 | 0.97 | 0.003 |
| mock_specialist | aptos | ece_grade | 3 | 0.21 | 0.208 | 0.212 | 0.003 |
| mock_specialist | ddr | qwk | 3 | 0.865 | 0.862 | 0.869 | 0.006 |
| mock_specialist | ddr | ref_auroc | 3 | 0.974 | 0.972 | 0.975 | 0.004 |
| mock_specialist | ddr | ece_grade | 3 | 0.164 | 0.155 | 0.17 | 0.015 |
| mock_specialist | idrid | qwk | 3 | 0.884 | 0.877 | 0.891 | 0.013 |
| mock_specialist | idrid | ref_auroc | 3 | 0.976 | 0.972 | 0.979 | 0.007 |
| mock_specialist | idrid | ece_grade | 3 | 0.212 | 0.195 | 0.228 | 0.033 |
| mock_specialist | mbrset | qwk | 3 | 0.886 | 0.88 | 0.89 | 0.01 |
| mock_specialist | mbrset | ref_auroc | 3 | 0.964 | 0.963 | 0.967 | 0.004 |
| mock_specialist | mbrset | ece_grade | 3 | 0.151 | 0.144 | 0.157 | 0.012 |
| mock_specialist | messidor2 | qwk | 3 | 0.803 | 0.798 | 0.809 | 0.011 |
| mock_specialist | messidor2 | ref_auroc | 3 | 0.934 | 0.929 | 0.938 | 0.009 |
| mock_specialist | messidor2 | ece_grade | 3 | 0.176 | 0.162 | 0.196 | 0.034 |
| mock_specialist | eyepacs | qwk | 3 | 0.9 | 0.897 | 0.906 | 0.008 |
| mock_specialist | eyepacs | ref_auroc | 3 | 0.963 | 0.959 | 0.969 | 0.01 |
| mock_specialist | eyepacs | ece_grade | 3 | 0.08 | 0.063 | 0.092 | 0.029 |
| mock_specialist_100 | aptos | qwk | 3 | 0.417 | 0.409 | 0.423 | 0.014 |
| mock_specialist_100 | aptos | ref_auroc | 3 | 0.786 | 0.782 | 0.792 | 0.01 |
| mock_specialist_100 | aptos | ece_grade | 3 | 0.194 | 0.184 | 0.209 | 0.025 |
| mock_specialist_100 | ddr | qwk | 3 | 0.527 | 0.513 | 0.547 | 0.034 |
| mock_specialist_100 | ddr | ref_auroc | 3 | 0.842 | 0.832 | 0.852 | 0.02 |
| mock_specialist_100 | ddr | ece_grade | 3 | 0.121 | 0.111 | 0.129 | 0.018 |
| mock_specialist_100 | idrid | qwk | 3 | 0.627 | 0.623 | 0.632 | 0.01 |
| mock_specialist_100 | idrid | ref_auroc | 3 | 0.819 | 0.817 | 0.82 | 0.004 |
| mock_specialist_100 | idrid | ece_grade | 3 | 0.141 | 0.126 | 0.164 | 0.038 |
| mock_specialist_100 | mbrset | qwk | 3 | 0.618 | 0.613 | 0.625 | 0.012 |
| mock_specialist_100 | mbrset | ref_auroc | 3 | 0.857 | 0.852 | 0.859 | 0.007 |
| mock_specialist_100 | mbrset | ece_grade | 3 | 0.142 | 0.135 | 0.152 | 0.017 |
| mock_specialist_100 | messidor2 | qwk | 3 | 0.457 | 0.447 | 0.465 | 0.018 |
| mock_specialist_100 | messidor2 | ref_auroc | 3 | 0.768 | 0.764 | 0.771 | 0.007 |
| mock_specialist_100 | messidor2 | ece_grade | 3 | 0.163 | 0.153 | 0.171 | 0.018 |
| mock_specialist_100 | eyepacs | qwk | 3 | 0.662 | 0.657 | 0.667 | 0.01 |
| mock_specialist_100 | eyepacs | ref_auroc | 3 | 0.856 | 0.848 | 0.862 | 0.014 |
| mock_specialist_100 | eyepacs | ece_grade | 3 | 0.1 | 0.071 | 0.128 | 0.058 |
| mock_specialist_300 | aptos | qwk | 3 | 0.65 | 0.645 | 0.657 | 0.012 |
| mock_specialist_300 | aptos | ref_auroc | 3 | 0.891 | 0.882 | 0.906 | 0.025 |
| mock_specialist_300 | aptos | ece_grade | 3 | 0.222 | 0.212 | 0.24 | 0.028 |
| mock_specialist_300 | ddr | qwk | 3 | 0.712 | 0.71 | 0.714 | 0.004 |
| mock_specialist_300 | ddr | ref_auroc | 3 | 0.928 | 0.924 | 0.931 | 0.007 |
| mock_specialist_300 | ddr | ece_grade | 3 | 0.167 | 0.138 | 0.189 | 0.051 |
| mock_specialist_300 | idrid | qwk | 3 | 0.789 | 0.768 | 0.805 | 0.037 |
| mock_specialist_300 | idrid | ref_auroc | 3 | 0.901 | 0.894 | 0.907 | 0.012 |
| mock_specialist_300 | idrid | ece_grade | 3 | 0.17 | 0.168 | 0.171 | 0.004 |
| mock_specialist_300 | mbrset | qwk | 3 | 0.768 | 0.764 | 0.77 | 0.006 |
| mock_specialist_300 | mbrset | ref_auroc | 3 | 0.909 | 0.9 | 0.914 | 0.014 |
| mock_specialist_300 | mbrset | ece_grade | 3 | 0.153 | 0.146 | 0.167 | 0.021 |
| mock_specialist_300 | messidor2 | qwk | 3 | 0.62 | 0.6 | 0.641 | 0.041 |
| mock_specialist_300 | messidor2 | ref_auroc | 3 | 0.852 | 0.85 | 0.854 | 0.004 |
| mock_specialist_300 | messidor2 | ece_grade | 3 | 0.172 | 0.149 | 0.19 | 0.042 |
| mock_specialist_300 | eyepacs | qwk | 3 | 0.789 | 0.782 | 0.794 | 0.013 |
| mock_specialist_300 | eyepacs | ref_auroc | 3 | 0.92 | 0.912 | 0.924 | 0.012 |
| mock_specialist_300 | eyepacs | ece_grade | 3 | 0.119 | 0.099 | 0.152 | 0.053 |

### Table 4b. Effect of temperature scaling fitted on the EyePACS calibration split

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Grade ECE, raw | Grade ECE, calibrated | Referable ECE, raw | Referable ECE, calibrated | AURC, raw | AURC, calibrated |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.370 | 0.141 | 0.229 | 0.172 | 0.316 | 0.289 |
| mock_jev_zs | mbrset | 0.460 | 0.064 | 0.209 | 0.154 | 0.530 | 0.477 |
| mock_jev_zs | messidor2 | 0.426 | 0.117 | 0.243 | 0.184 | 0.388 | 0.351 |
| mock_jev_zs | idrid | 0.473 | 0.096 | 0.287 | 0.213 | 0.477 | 0.486 |
| mock_jev_zs | ddr | 0.397 | 0.138 | 0.215 | 0.161 | 0.348 | 0.323 |
| mock_jev_zs | eyepacs | 0.341 | 0.100 | 0.123 | 0.084 | 0.365 | 0.313 |
| mock_noabstain_zs | aptos | 0.388 | 0.193 | 0.224 | 0.179 | 0.361 | 0.309 |
| mock_noabstain_zs | mbrset | 0.463 | 0.067 | 0.266 | 0.196 | 0.531 | 0.501 |
| mock_noabstain_zs | messidor2 | 0.432 | 0.113 | 0.241 | 0.182 | 0.430 | 0.399 |
| mock_noabstain_zs | idrid | 0.467 | 0.057 | 0.302 | 0.233 | 0.530 | 0.486 |
| mock_noabstain_zs | ddr | 0.389 | 0.128 | 0.238 | 0.182 | 0.415 | 0.344 |
| mock_noabstain_zs | eyepacs | 0.385 | 0.133 | 0.180 | 0.114 | 0.386 | 0.342 |
| mock_jev_ft | aptos | 0.141 | 0.129 | 0.068 | 0.060 | 0.179 | 0.177 |
| mock_jev_ft | mbrset | 0.167 | 0.137 | 0.067 | 0.075 | 0.266 | 0.264 |
| mock_jev_ft | messidor2 | 0.157 | 0.138 | 0.064 | 0.074 | 0.186 | 0.184 |
| mock_jev_ft | idrid | 0.161 | 0.150 | 0.099 | 0.105 | 0.237 | 0.236 |
| mock_jev_ft | ddr | 0.130 | 0.114 | 0.061 | 0.052 | 0.159 | 0.157 |
| mock_jev_ft | eyepacs | 0.096 | 0.079 | 0.076 | 0.045 | 0.181 | 0.179 |
| mock_jev_ft_100 | aptos | 0.231 | 0.137 | 0.114 | 0.124 | 0.219 | 0.206 |
| mock_jev_ft_100 | mbrset | 0.302 | 0.147 | 0.105 | 0.122 | 0.377 | 0.364 |
| mock_jev_ft_100 | messidor2 | 0.243 | 0.126 | 0.150 | 0.179 | 0.309 | 0.286 |
| mock_jev_ft_100 | idrid | 0.317 | 0.160 | 0.150 | 0.163 | 0.403 | 0.377 |
| mock_jev_ft_100 | ddr | 0.269 | 0.138 | 0.106 | 0.125 | 0.287 | 0.273 |
| mock_jev_ft_100 | eyepacs | 0.213 | 0.111 | 0.095 | 0.097 | 0.304 | 0.293 |
| mock_jev_ft_300 | aptos | 0.164 | 0.110 | 0.104 | 0.103 | 0.215 | 0.205 |
| mock_jev_ft_300 | mbrset | 0.238 | 0.124 | 0.088 | 0.132 | 0.341 | 0.326 |
| mock_jev_ft_300 | messidor2 | 0.188 | 0.123 | 0.100 | 0.097 | 0.261 | 0.245 |
| mock_jev_ft_300 | idrid | 0.179 | 0.091 | 0.100 | 0.107 | 0.246 | 0.250 |
| mock_jev_ft_300 | ddr | 0.234 | 0.148 | 0.066 | 0.065 | 0.268 | 0.251 |
| mock_jev_ft_300 | eyepacs | 0.130 | 0.089 | 0.075 | 0.059 | 0.240 | 0.229 |
| mock_generative | aptos | 0.287 | 0.128 | 0.066 | 0.063 | 0.229 | 0.169 |
| mock_generative | mbrset | 0.325 | 0.100 | 0.112 | 0.099 | 0.327 | 0.262 |
| mock_generative | messidor2 | 0.345 | 0.163 | 0.115 | 0.122 | 0.305 | 0.236 |
| mock_generative | idrid | 0.263 | 0.099 | 0.072 | 0.073 | 0.255 | 0.183 |
| mock_generative | ddr | 0.328 | 0.161 | 0.119 | 0.116 | 0.278 | 0.198 |
| mock_generative | eyepacs | 0.246 | 0.059 | 0.065 | 0.064 | 0.236 | 0.190 |
| mock_specialist | aptos | 0.220 | 0.195 | 0.071 | 0.064 | 0.237 | 0.233 |
| mock_specialist | mbrset | 0.168 | 0.137 | 0.058 | 0.085 | 0.243 | 0.240 |
| mock_specialist | messidor2 | 0.161 | 0.152 | 0.048 | 0.080 | 0.185 | 0.183 |
| mock_specialist | idrid | 0.244 | 0.214 | 0.085 | 0.095 | 0.254 | 0.253 |
| mock_specialist | ddr | 0.177 | 0.153 | 0.037 | 0.045 | 0.192 | 0.190 |
| mock_specialist | eyepacs | 0.084 | 0.057 | 0.052 | 0.052 | 0.155 | 0.154 |
| mock_specialist_100 | aptos | 0.408 | 0.196 | 0.238 | 0.220 | 0.384 | 0.343 |
| mock_specialist_100 | mbrset | 0.416 | 0.112 | 0.188 | 0.169 | 0.438 | 0.410 |
| mock_specialist_100 | messidor2 | 0.386 | 0.138 | 0.195 | 0.183 | 0.386 | 0.355 |
| mock_specialist_100 | idrid | 0.435 | 0.164 | 0.230 | 0.209 | 0.395 | 0.403 |
| mock_specialist_100 | ddr | 0.347 | 0.132 | 0.155 | 0.132 | 0.368 | 0.318 |
| mock_specialist_100 | eyepacs | 0.316 | 0.063 | 0.117 | 0.100 | 0.352 | 0.323 |
| mock_specialist_300 | aptos | 0.328 | 0.170 | 0.148 | 0.149 | 0.315 | 0.287 |
| mock_specialist_300 | mbrset | 0.311 | 0.140 | 0.133 | 0.135 | 0.341 | 0.326 |
| mock_specialist_300 | messidor2 | 0.294 | 0.146 | 0.125 | 0.123 | 0.272 | 0.253 |
| mock_specialist_300 | idrid | 0.330 | 0.171 | 0.130 | 0.136 | 0.335 | 0.324 |
| mock_specialist_300 | ddr | 0.280 | 0.145 | 0.072 | 0.070 | 0.290 | 0.259 |
| mock_specialist_300 | eyepacs | 0.230 | 0.077 | 0.066 | 0.074 | 0.248 | 0.238 |

### Table 5. Latency as measured during prediction

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Arm | Adapter | Repository | Revision | Decisions timed | Median ms per decision | 95th percentile ms |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | Z | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_noabstain_zs | Z | mock | – | – | 9515 | 0.1 | 0.2 |
| mock_jev_ft | B | mock | – | – | 19030 | 0.1 | 0.2 |
| mock_jev_ft_100 | B | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_jev_ft_300 | B | mock | – | – | 9515 | 0.1 | 0.2 |
| mock_generative | G | mock | – | – | 9515 | 0.1 | 0.2 |
| mock_specialist | S | mock | – | – | 9515 | 0.1 | 0.2 |
| mock_specialist_100 | S | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_specialist_300 | S | mock | – | – | 9515 | 0.1 | 0.1 |

Wall-clock time per question on the hardware used for the run; record that hardware alongside this table.

### Pre-specified comparisons

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Test | Type | Metric | Dataset | Model | Reference | Model value | Reference value | Advantage (95% CI) | Margin | p | Holm p | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H2_qwk | noninferiority | qwk | ddr | mock_jev_ft | mock_specialist | 0.860 | 0.874 | -0.014 (-0.044 to 0.015) | 0.05 | 0.0075 | 0.0600 | not shown non-inferior (Holm) |
| H2_ref_sens | noninferiority | ref_sens_matched | ddr | mock_jev_ft | mock_specialist | 0.780 | 0.832 | -0.051 (-0.179 to 0.040) | 0.05 | 0.5827 | 1.0000 | not shown non-inferior (Holm) |
| H3_ece | superiority | ece_grade | ddr | mock_jev_ft | mock_generative | 0.114 | 0.161 | 0.047 (-0.003 to 0.095) | – | 0.0390 | 0.2339 | not shown superior (Holm) |
| H3_aurc | superiority | aurc_grade | ddr | mock_jev_ft | mock_generative | 0.157 | 0.198 | 0.041 (-0.002 to 0.086) | – | 0.0300 | 0.2099 | not shown superior (Holm) |
| H4_ece | noninferiority | ece_grade | ddr | mock_jev_ft | mock_specialist | 0.114 | 0.153 | 0.038 (-0.011 to 0.091) | 0.02 | 0.0105 | not primary | non-inferior |
| H4_aurc | noninferiority | aurc_grade | ddr | mock_jev_ft | mock_specialist | 0.157 | 0.190 | 0.033 (-0.013 to 0.084) | 0.02 | 0.0135 | not primary | non-inferior |
| H5_vision_lora | superiority | qwk | ddr | mock_jev_ft | mock_jev_zs | 0.860 | 0.524 | 0.335 (0.261 to 0.412) | – | 0.0005 | not primary | superior |
| H2_qwk | noninferiority | qwk | messidor2 | mock_jev_ft | mock_specialist | 0.799 | 0.826 | -0.027 (-0.081 to 0.024) | 0.05 | 0.1919 | 0.7676 | not shown non-inferior (Holm) |
| H2_ref_sens | noninferiority | ref_sens_matched | messidor2 | mock_jev_ft | mock_specialist | 0.685 | 0.758 | -0.073 (-0.266 to 0.076) | 0.05 | 0.6242 | 1.0000 | not shown non-inferior (Holm) |
| H3_ece | superiority | ece_grade | messidor2 | mock_jev_ft | mock_generative | 0.138 | 0.163 | 0.024 (-0.036 to 0.091) | – | 0.2264 | 0.7676 | not shown superior (Holm) |
| H3_aurc | superiority | aurc_grade | messidor2 | mock_jev_ft | mock_generative | 0.184 | 0.236 | 0.052 (-0.016 to 0.127) | – | 0.0625 | 0.3123 | not shown superior (Holm) |
| H4_ece | noninferiority | ece_grade | messidor2 | mock_jev_ft | mock_specialist | 0.138 | 0.152 | 0.014 (-0.044 to 0.079) | 0.02 | 0.1069 | not primary | not shown non-inferior |
| H4_aurc | noninferiority | aurc_grade | messidor2 | mock_jev_ft | mock_specialist | 0.184 | 0.183 | -0.001 (-0.058 to 0.052) | 0.02 | 0.2619 | not primary | not shown non-inferior |
| H5_vision_lora | superiority | qwk | messidor2 | mock_jev_ft | mock_jev_zs | 0.799 | 0.347 | 0.453 (0.336 to 0.577) | – | 0.0005 | not primary | superior |
| H2_st_sens | noninferiority | st_sens_matched | pooled_external | mock_jev_ft | mock_specialist | 0.843 | 0.883 | -0.040 (-0.126 to 0.021) | 0.05 | 0.4903 | not primary | not shown non-inferior |

Advantage is model minus reference, sign-flipped for metrics where lower is better, so positive favours the model. Tests are one-sided at 2.5%, from the paired patient-level bootstrap. Primary tests are decided on the Holm-adjusted p-value over the whole pre-specified primary family; a primary test that could not be run counts as failed. Intervals are unadjusted.
