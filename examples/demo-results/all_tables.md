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
| mock_jev_zs | aptos | 303 | 0.502 (0.391 to 0.595) | 0.795 (0.739 to 0.852) | 0.110 | 0.013 |
| mock_jev_zs | mbrset | 336 | 0.518 (0.430 to 0.593) | 0.764 (0.711 to 0.817) | 0.080 | 0.012 |
| mock_jev_zs | messidor2 | 217 | 0.484 (0.390 to 0.587) | 0.794 (0.727 to 0.857) | 0.132 | 0.023 |
| mock_jev_zs | idrid | 120 | 0.481 (0.339 to 0.616) | 0.748 (0.665 to 0.839) | 0.105 | 0.017 |
| mock_jev_zs | ddr | 362 | 0.455 (0.358 to 0.539) | 0.771 (0.719 to 0.821) | 0.124 | 0.022 |
| mock_jev_zs | eyepacs | 476 | 0.570 (0.503 to 0.627) | 0.829 (0.792 to 0.869) | 0.081 | 0.013 |
| mock_noabstain_zs | aptos | 303 | 0.295 (0.203 to 0.394) | 0.705 (0.640 to 0.768) | 0.132 | 0.007 |
| mock_noabstain_zs | mbrset | 336 | 0.471 (0.373 to 0.562) | 0.747 (0.684 to 0.805) | 0.076 | 0.021 |
| mock_noabstain_zs | messidor2 | 217 | 0.309 (0.191 to 0.407) | 0.710 (0.635 to 0.772) | 0.095 | 0.018 |
| mock_noabstain_zs | idrid | 120 | 0.624 (0.507 to 0.723) | 0.866 (0.798 to 0.929) | 0.092 | 0.017 |
| mock_noabstain_zs | ddr | 362 | 0.452 (0.352 to 0.541) | 0.770 (0.715 to 0.813) | 0.140 | 0.011 |
| mock_noabstain_zs | eyepacs | 476 | 0.577 (0.505 to 0.634) | 0.827 (0.786 to 0.862) | 0.130 | 0.008 |

QWK: quadratic weighted kappa on five grades. Referable: grade 2 or worse (grade-only definition). Probabilities temperature-scaled on the EyePACS calibration split.

### Table 2. Fine-tuned decision models, specialist and generative baselines

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Arm | Dataset | Gradeable images | QWK | Referable AUROC | Referable sensitivity | Referable specificity | Grade ECE | AURC |
|---|---|---|---|---|---|---|---|---|---|
| mock_jev_ft | language + vision LoRA | aptos | 303 | 0.852 (0.814 to 0.878) | 0.955 (0.937 to 0.970) | 0.852 (0.791 to 0.906) | 0.912 (0.884 to 0.942) | 0.114 (0.097 to 0.157) | 0.189 (0.148 to 0.228) |
| mock_jev_ft | language + vision LoRA | mbrset | 336 | 0.859 (0.812 to 0.885) | 0.936 (0.911 to 0.956) | 0.869 (0.811 to 0.912) | 0.859 (0.825 to 0.895) | 0.108 (0.095 to 0.150) | 0.237 (0.196 to 0.286) |
| mock_jev_ft | language + vision LoRA | messidor2 | 217 | 0.783 (0.729 to 0.820) | 0.925 (0.904 to 0.950) | 0.734 (0.661 to 0.807) | 0.903 (0.871 to 0.935) | 0.160 (0.139 to 0.214) | 0.209 (0.164 to 0.262) |
| mock_jev_ft | language + vision LoRA | idrid | 120 | 0.882 (0.851 to 0.909) | 0.977 (0.961 to 0.992) | 0.877 (0.815 to 0.932) | 0.961 (0.924 to 0.991) | 0.170 (0.133 to 0.221) | 0.222 (0.170 to 0.281) |
| mock_jev_ft | language + vision LoRA | ddr | 362 | 0.865 (0.833 to 0.888) | 0.962 (0.945 to 0.975) | 0.832 (0.780 to 0.879) | 0.935 (0.912 to 0.959) | 0.106 (0.087 to 0.143) | 0.164 (0.135 to 0.200) |
| mock_jev_ft | language + vision LoRA | eyepacs | 476 | 0.888 (0.862 to 0.906) | 0.974 (0.964 to 0.982) | 0.890 (0.851 to 0.922) | 0.923 (0.898 to 0.944) | 0.064 (0.051 to 0.095) | 0.174 (0.146 to 0.204) |
| mock_jev_ft | language + vision LoRA | pooled_external | 1338 | 0.858 (0.842 to 0.871) | 0.951 (0.942 to 0.958) | 0.840 (0.816 to 0.862) | 0.908 (0.894 to 0.920) | 0.110 (0.098 to 0.128) | 0.199 (0.182 to 0.218) |
| mock_jev_ft_100 | language + vision LoRA | aptos | 303 | 0.694 (0.618 to 0.765) | 0.883 (0.842 to 0.917) | 0.815 (0.721 to 0.884) | 0.779 (0.726 to 0.834) | 0.118 (0.092 to 0.172) | 0.213 (0.165 to 0.277) |
| mock_jev_ft_100 | language + vision LoRA | mbrset | 336 | 0.672 (0.585 to 0.752) | 0.887 (0.845 to 0.927) | 0.903 (0.854 to 0.948) | 0.703 (0.624 to 0.765) | 0.156 (0.118 to 0.210) | 0.387 (0.308 to 0.484) |
| mock_jev_ft_100 | language + vision LoRA | messidor2 | 217 | 0.524 (0.408 to 0.628) | 0.841 (0.776 to 0.898) | 0.806 (0.692 to 0.907) | 0.690 (0.620 to 0.766) | 0.158 (0.134 to 0.231) | 0.327 (0.255 to 0.404) |
| mock_jev_ft_100 | language + vision LoRA | idrid | 120 | 0.737 (0.636 to 0.824) | 0.906 (0.857 to 0.950) | 0.870 (0.785 to 0.938) | 0.725 (0.610 to 0.839) | 0.100 (0.091 to 0.204) | 0.308 (0.223 to 0.413) |
| mock_jev_ft_100 | language + vision LoRA | ddr | 362 | 0.633 (0.555 to 0.696) | 0.848 (0.808 to 0.885) | 0.785 (0.706 to 0.866) | 0.706 (0.652 to 0.764) | 0.152 (0.127 to 0.201) | 0.262 (0.208 to 0.312) |
| mock_jev_ft_100 | language + vision LoRA | eyepacs | 476 | 0.761 (0.714 to 0.794) | 0.907 (0.873 to 0.934) | 0.890 (0.832 to 0.941) | 0.727 (0.675 to 0.777) | 0.093 (0.068 to 0.140) | 0.256 (0.212 to 0.308) |
| mock_jev_ft_100 | language + vision LoRA | pooled_external | 1338 | 0.665 (0.630 to 0.699) | 0.874 (0.855 to 0.893) | 0.841 (0.806 to 0.875) | 0.722 (0.694 to 0.748) | 0.107 (0.098 to 0.136) | 0.294 (0.267 to 0.324) |
| mock_jev_ft_300 | language + vision LoRA | aptos | 303 | 0.746 (0.668 to 0.801) | 0.903 (0.861 to 0.936) | 0.753 (0.644 to 0.838) | 0.833 (0.783 to 0.881) | 0.212 (0.175 to 0.254) | 0.233 (0.187 to 0.283) |
| mock_jev_ft_300 | language + vision LoRA | mbrset | 336 | 0.764 (0.696 to 0.808) | 0.907 (0.863 to 0.941) | 0.881 (0.799 to 0.944) | 0.757 (0.695 to 0.812) | 0.147 (0.117 to 0.198) | 0.318 (0.259 to 0.407) |
| mock_jev_ft_300 | language + vision LoRA | messidor2 | 217 | 0.731 (0.643 to 0.797) | 0.897 (0.844 to 0.941) | 0.790 (0.694 to 0.886) | 0.845 (0.773 to 0.908) | 0.138 (0.101 to 0.207) | 0.198 (0.142 to 0.261) |
| mock_jev_ft_300 | language + vision LoRA | idrid | 120 | 0.735 (0.646 to 0.812) | 0.923 (0.870 to 0.966) | 0.855 (0.763 to 0.938) | 0.843 (0.737 to 0.924) | 0.271 (0.208 to 0.340) | 0.391 (0.272 to 0.502) |
| mock_jev_ft_300 | language + vision LoRA | ddr | 362 | 0.805 (0.761 to 0.845) | 0.946 (0.920 to 0.968) | 0.850 (0.772 to 0.907) | 0.878 (0.841 to 0.915) | 0.181 (0.144 to 0.221) | 0.216 (0.166 to 0.263) |
| mock_jev_ft_300 | language + vision LoRA | eyepacs | 476 | 0.833 (0.796 to 0.858) | 0.949 (0.928 to 0.967) | 0.877 (0.825 to 0.926) | 0.864 (0.827 to 0.898) | 0.122 (0.098 to 0.165) | 0.230 (0.189 to 0.278) |
| mock_jev_ft_300 | language + vision LoRA | pooled_external | 1338 | 0.774 (0.741 to 0.797) | 0.919 (0.902 to 0.933) | 0.834 (0.799 to 0.868) | 0.832 (0.803 to 0.855) | 0.162 (0.147 to 0.185) | 0.254 (0.228 to 0.286) |
| mock_generative | generative | aptos | 303 | 0.823 (0.780 to 0.861) | 0.963 (0.935 to 0.980) | 0.926 (0.870 to 0.976) | 0.856 (0.804 to 0.898) | 0.126 (0.091 to 0.172) | 0.197 (0.152 to 0.253) |
| mock_generative | generative | mbrset | 336 | 0.810 (0.741 to 0.856) | 0.927 (0.889 to 0.953) | 0.896 (0.827 to 0.952) | 0.767 (0.697 to 0.818) | 0.148 (0.107 to 0.199) | 0.296 (0.230 to 0.377) |
| mock_generative | generative | messidor2 | 217 | 0.785 (0.723 to 0.843) | 0.939 (0.903 to 0.973) | 0.887 (0.816 to 0.958) | 0.903 (0.863 to 0.952) | 0.101 (0.065 to 0.170) | 0.226 (0.165 to 0.287) |
| mock_generative | generative | idrid | 120 | 0.877 (0.839 to 0.915) | 0.976 (0.954 to 0.994) | 0.928 (0.875 to 0.974) | 0.843 (0.743 to 0.936) | 0.118 (0.079 to 0.212) | 0.231 (0.156 to 0.311) |
| mock_generative | generative | ddr | 362 | 0.809 (0.765 to 0.846) | 0.946 (0.918 to 0.966) | 0.869 (0.794 to 0.929) | 0.859 (0.816 to 0.898) | 0.109 (0.079 to 0.159) | 0.167 (0.131 to 0.203) |
| mock_generative | generative | eyepacs | 476 | 0.885 (0.860 to 0.903) | 0.969 (0.954 to 0.982) | 0.904 (0.860 to 0.944) | 0.900 (0.864 to 0.931) | 0.055 (0.036 to 0.097) | 0.201 (0.163 to 0.245) |
| mock_generative | generative | pooled_external | 1338 | 0.825 (0.802 to 0.845) | 0.948 (0.935 to 0.960) | 0.898 (0.869 to 0.928) | 0.844 (0.817 to 0.866) | 0.109 (0.089 to 0.136) | 0.219 (0.192 to 0.249) |
| mock_specialist | specialist | aptos | 303 | 0.875 (0.833 to 0.906) | 0.965 (0.946 to 0.982) | 0.889 (0.811 to 0.948) | 0.914 (0.875 to 0.948) | 0.097 (0.069 to 0.150) | 0.141 (0.107 to 0.189) |
| mock_specialist | specialist | mbrset | 336 | 0.869 (0.825 to 0.895) | 0.945 (0.917 to 0.969) | 0.910 (0.856 to 0.955) | 0.842 (0.782 to 0.893) | 0.152 (0.113 to 0.209) | 0.258 (0.194 to 0.329) |
| mock_specialist | specialist | messidor2 | 217 | 0.835 (0.788 to 0.875) | 0.966 (0.945 to 0.983) | 0.871 (0.778 to 0.956) | 0.903 (0.852 to 0.946) | 0.137 (0.106 to 0.207) | 0.200 (0.145 to 0.263) |
| mock_specialist | specialist | idrid | 120 | 0.881 (0.836 to 0.915) | 0.975 (0.948 to 0.996) | 0.942 (0.890 to 0.986) | 0.922 (0.840 to 0.981) | 0.139 (0.098 to 0.242) | 0.245 (0.168 to 0.322) |
| mock_specialist | specialist | ddr | 362 | 0.867 (0.838 to 0.891) | 0.975 (0.961 to 0.989) | 0.925 (0.867 to 0.972) | 0.922 (0.888 to 0.952) | 0.137 (0.102 to 0.182) | 0.175 (0.135 to 0.214) |
| mock_specialist | specialist | eyepacs | 476 | 0.904 (0.882 to 0.920) | 0.977 (0.965 to 0.987) | 0.918 (0.867 to 0.963) | 0.930 (0.900 to 0.957) | 0.072 (0.047 to 0.109) | 0.127 (0.099 to 0.164) |
| mock_specialist | specialist | pooled_external | 1338 | 0.873 (0.856 to 0.887) | 0.964 (0.954 to 0.973) | 0.909 (0.883 to 0.934) | 0.898 (0.878 to 0.920) | 0.119 (0.099 to 0.143) | 0.195 (0.175 to 0.223) |
| mock_specialist_100 | specialist | aptos | 303 | 0.570 (0.472 to 0.650) | 0.844 (0.795 to 0.886) | 0.877 (0.803 to 0.940) | 0.640 (0.578 to 0.700) | 0.129 (0.112 to 0.193) | 0.293 (0.236 to 0.370) |
| mock_specialist_100 | specialist | mbrset | 336 | 0.601 (0.495 to 0.664) | 0.802 (0.741 to 0.848) | 0.851 (0.778 to 0.906) | 0.569 (0.492 to 0.650) | 0.129 (0.110 to 0.194) | 0.434 (0.350 to 0.521) |
| mock_specialist_100 | specialist | messidor2 | 217 | 0.534 (0.438 to 0.627) | 0.827 (0.769 to 0.881) | 0.839 (0.748 to 0.930) | 0.600 (0.530 to 0.674) | 0.171 (0.137 to 0.226) | 0.348 (0.275 to 0.424) |
| mock_specialist_100 | specialist | idrid | 120 | 0.606 (0.474 to 0.708) | 0.846 (0.783 to 0.911) | 0.913 (0.849 to 0.982) | 0.549 (0.415 to 0.692) | 0.144 (0.106 to 0.242) | 0.391 (0.281 to 0.489) |
| mock_specialist_100 | specialist | ddr | 362 | 0.537 (0.451 to 0.612) | 0.831 (0.790 to 0.878) | 0.841 (0.776 to 0.915) | 0.616 (0.563 to 0.673) | 0.163 (0.131 to 0.209) | 0.319 (0.263 to 0.370) |
| mock_specialist_100 | specialist | eyepacs | 476 | 0.675 (0.607 to 0.727) | 0.864 (0.820 to 0.900) | 0.897 (0.843 to 0.942) | 0.624 (0.562 to 0.672) | 0.088 (0.064 to 0.133) | 0.311 (0.262 to 0.371) |
| mock_specialist_100 | specialist | pooled_external | 1338 | 0.584 (0.540 to 0.624) | 0.831 (0.805 to 0.853) | 0.861 (0.830 to 0.893) | 0.605 (0.577 to 0.634) | 0.127 (0.106 to 0.152) | 0.348 (0.316 to 0.384) |
| mock_specialist_300 | specialist | aptos | 303 | 0.751 (0.682 to 0.808) | 0.901 (0.861 to 0.936) | 0.852 (0.769 to 0.919) | 0.793 (0.740 to 0.844) | 0.106 (0.076 to 0.165) | 0.212 (0.171 to 0.269) |
| mock_specialist_300 | specialist | mbrset | 336 | 0.758 (0.687 to 0.802) | 0.881 (0.838 to 0.915) | 0.881 (0.810 to 0.933) | 0.728 (0.659 to 0.790) | 0.163 (0.131 to 0.230) | 0.355 (0.278 to 0.440) |
| mock_specialist_300 | specialist | messidor2 | 217 | 0.686 (0.612 to 0.747) | 0.905 (0.866 to 0.940) | 0.823 (0.736 to 0.915) | 0.781 (0.712 to 0.836) | 0.147 (0.106 to 0.211) | 0.297 (0.231 to 0.368) |
| mock_specialist_300 | specialist | idrid | 120 | 0.773 (0.693 to 0.839) | 0.929 (0.882 to 0.967) | 0.928 (0.857 to 0.986) | 0.686 (0.559 to 0.804) | 0.156 (0.115 to 0.240) | 0.318 (0.221 to 0.408) |
| mock_specialist_300 | specialist | ddr | 362 | 0.715 (0.658 to 0.767) | 0.911 (0.880 to 0.943) | 0.879 (0.822 to 0.943) | 0.808 (0.760 to 0.852) | 0.143 (0.111 to 0.188) | 0.249 (0.201 to 0.297) |
| mock_specialist_300 | specialist | eyepacs | 476 | 0.800 (0.752 to 0.832) | 0.926 (0.899 to 0.950) | 0.897 (0.846 to 0.941) | 0.812 (0.763 to 0.849) | 0.082 (0.050 to 0.120) | 0.236 (0.198 to 0.290) |
| mock_specialist_300 | specialist | pooled_external | 1338 | 0.747 (0.719 to 0.774) | 0.904 (0.886 to 0.920) | 0.874 (0.844 to 0.909) | 0.774 (0.745 to 0.804) | 0.129 (0.109 to 0.152) | 0.277 (0.249 to 0.309) |

Values are point estimates with 95% patient-clustered bootstrap intervals. Sensitivity and specificity use the threshold fixed on the calibration split for 90% sensitivity. Seeds of one arm are pooled.

### Table 3. Gradeability and abstention on ungradeable images

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Ungradeable images | Gradeability AUROC (Q1) | Ungradeable detected (Q1) | Gradeable kept (Q1) | Unknown-probability AUROC (Q2) | Abstained on ungradeable (Q2) | Abstained on gradeable (Q2) |
|---|---|---|---|---|---|---|---|---|
| mock_jev_zs | mbrset | 24 | 1.000 (0.999 to 1.000) | 1.000 (1.000 to 1.000) | 0.988 (0.976 to 0.997) | 0.965 (0.940 to 0.985) | 1.000 (1.000 to 1.000) | 0.012 (0.003 to 0.024) |
| mock_jev_zs | messidor2 | 3 | 0.997 (0.986 to 1.000) | 1.000 (1.000 to 1.000) | 0.968 (0.940 to 0.986) | 0.869 (0.744 to 0.954) | 1.000 (1.000 to 1.000) | 0.023 (0.005 to 0.046) |
| mock_jev_zs | ddr | 38 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.970 (0.951 to 0.986) | 0.892 (0.841 to 0.936) | 1.000 (1.000 to 1.000) | 0.022 (0.008 to 0.038) |
| mock_jev_zs | eyepacs | 24 | 0.999 (0.998 to 1.000) | 1.000 (1.000 to 1.000) | 0.971 (0.956 to 0.985) | 0.919 (0.877 to 0.958) | 1.000 (1.000 to 1.000) | 0.013 (0.002 to 0.023) |
| mock_noabstain_zs | mbrset | 24 | 0.997 (0.991 to 1.000) | 1.000 (1.000 to 1.000) | 0.964 (0.941 to 0.982) | 0.929 (0.887 to 0.964) | 0.917 (0.773 to 1.000) | 0.021 (0.009 to 0.039) |
| mock_noabstain_zs | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.950 to 0.991) | 0.863 (0.639 to 1.000) | 1.000 (1.000 to 1.000) | 0.018 (0.005 to 0.037) |
| mock_noabstain_zs | ddr | 38 | 0.998 (0.995 to 1.000) | 0.974 (0.910 to 1.000) | 0.981 (0.967 to 0.993) | 0.867 (0.826 to 0.909) | 0.947 (0.874 to 1.000) | 0.011 (0.001 to 0.022) |
| mock_noabstain_zs | eyepacs | 24 | 0.996 (0.991 to 0.999) | 0.917 (0.778 to 1.000) | 0.983 (0.968 to 0.994) | 0.847 (0.800 to 0.891) | 0.875 (0.710 to 0.988) | 0.008 (0.002 to 0.019) |
| mock_jev_ft | mbrset | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.982 (0.971 to 0.991) | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.016 (0.008 to 0.026) |
| mock_jev_ft | messidor2 | 3 | 0.998 (0.993 to 1.000) | 1.000 (1.000 to 1.000) | 0.984 (0.970 to 0.994) | 0.998 (0.993 to 1.000) | 1.000 (1.000 to 1.000) | 0.014 (0.005 to 0.025) |
| mock_jev_ft | ddr | 38 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.975 (0.963 to 0.985) | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.022 (0.014 to 0.033) |
| mock_jev_ft | eyepacs | 24 | 0.997 (0.991 to 1.000) | 0.979 (0.924 to 1.000) | 0.980 (0.970 to 0.988) | 0.997 (0.990 to 1.000) | 0.979 (0.924 to 1.000) | 0.015 (0.008 to 0.023) |
| mock_jev_ft_100 | mbrset | 24 | 0.998 (0.995 to 1.000) | 1.000 (1.000 to 1.000) | 0.967 (0.947 to 0.984) | 0.997 (0.992 to 1.000) | 1.000 (1.000 to 1.000) | 0.027 (0.012 to 0.047) |
| mock_jev_ft_100 | messidor2 | 3 | 0.995 (0.982 to 1.000) | 1.000 (1.000 to 1.000) | 0.977 (0.958 to 0.995) | 0.991 (0.970 to 1.000) | 1.000 (1.000 to 1.000) | 0.018 (0.005 to 0.037) |
| mock_jev_ft_100 | ddr | 38 | 0.999 (0.996 to 1.000) | 0.974 (0.919 to 1.000) | 0.970 (0.952 to 0.986) | 0.995 (0.989 to 1.000) | 0.974 (0.919 to 1.000) | 0.025 (0.011 to 0.042) |
| mock_jev_ft_100 | eyepacs | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.975 (0.959 to 0.987) | 0.997 (0.993 to 1.000) | 1.000 (1.000 to 1.000) | 0.017 (0.008 to 0.028) |
| mock_jev_ft_300 | mbrset | 24 | 0.992 (0.980 to 1.000) | 0.917 (0.804 to 1.000) | 0.973 (0.954 to 0.993) | 0.991 (0.977 to 1.000) | 0.917 (0.804 to 1.000) | 0.021 (0.006 to 0.038) |
| mock_jev_ft_300 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.982 (0.963 to 0.995) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.014 (0.000 to 0.028) |
| mock_jev_ft_300 | ddr | 38 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.986 (0.975 to 0.997) | 1.000 (0.999 to 1.000) | 1.000 (1.000 to 1.000) | 0.008 (0.000 to 0.017) |
| mock_jev_ft_300 | eyepacs | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.968 (0.951 to 0.981) | 0.998 (0.996 to 1.000) | 1.000 (1.000 to 1.000) | 0.019 (0.008 to 0.031) |
| mock_generative | mbrset | 24 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.979 (0.961 to 0.994) | 0.995 (0.987 to 0.999) | 1.000 (1.000 to 1.000) | 0.012 (0.003 to 0.027) |
| mock_generative | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.977 (0.950 to 0.995) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.009 (0.000 to 0.023) |
| mock_generative | ddr | 38 | 0.999 (0.997 to 1.000) | 1.000 (1.000 to 1.000) | 0.972 (0.953 to 0.989) | 0.994 (0.988 to 0.999) | 1.000 (1.000 to 1.000) | 0.017 (0.005 to 0.030) |
| mock_generative | eyepacs | 24 | 0.997 (0.992 to 1.000) | 1.000 (1.000 to 1.000) | 0.968 (0.953 to 0.983) | 0.993 (0.984 to 0.998) | 0.958 (0.854 to 1.000) | 0.021 (0.009 to 0.034) |
| mock_specialist | mbrset | 24 | 0.992 (0.982 to 0.998) | 0.917 (0.789 to 1.000) | 0.973 (0.956 to 0.988) | 0.993 (0.984 to 0.999) | 0.917 (0.789 to 1.000) | 0.021 (0.006 to 0.036) |
| mock_specialist | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.959 (0.929 to 0.982) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.037 (0.014 to 0.064) |
| mock_specialist | ddr | 38 | 0.999 (0.996 to 1.000) | 0.974 (0.917 to 1.000) | 0.981 (0.966 to 0.992) | 0.998 (0.995 to 1.000) | 0.974 (0.917 to 1.000) | 0.014 (0.003 to 0.026) |
| mock_specialist | eyepacs | 24 | 0.998 (0.995 to 1.000) | 0.958 (0.862 to 1.000) | 0.983 (0.970 to 0.995) | 0.997 (0.993 to 1.000) | 0.917 (0.810 to 1.000) | 0.008 (0.000 to 0.017) |
| mock_specialist_100 | mbrset | 24 | 0.992 (0.982 to 0.998) | 0.917 (0.789 to 1.000) | 0.973 (0.956 to 0.988) | 0.970 (0.945 to 0.994) | 0.917 (0.789 to 1.000) | 0.012 (0.003 to 0.025) |
| mock_specialist_100 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.959 (0.929 to 0.982) | 0.978 (0.941 to 1.000) | 1.000 (1.000 to 1.000) | 0.037 (0.014 to 0.064) |
| mock_specialist_100 | ddr | 38 | 0.999 (0.996 to 1.000) | 0.974 (0.917 to 1.000) | 0.981 (0.966 to 0.992) | 0.942 (0.905 to 0.970) | 0.974 (0.917 to 1.000) | 0.011 (0.003 to 0.022) |
| mock_specialist_100 | eyepacs | 24 | 0.998 (0.995 to 1.000) | 0.958 (0.862 to 1.000) | 0.983 (0.970 to 0.995) | 0.952 (0.919 to 0.987) | 0.917 (0.810 to 1.000) | 0.006 (0.000 to 0.014) |
| mock_specialist_300 | mbrset | 24 | 0.992 (0.982 to 0.998) | 0.917 (0.789 to 1.000) | 0.973 (0.956 to 0.988) | 0.992 (0.981 to 0.999) | 0.917 (0.789 to 1.000) | 0.012 (0.003 to 0.025) |
| mock_specialist_300 | messidor2 | 3 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.959 (0.929 to 0.982) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.037 (0.014 to 0.064) |
| mock_specialist_300 | ddr | 38 | 0.999 (0.996 to 1.000) | 0.974 (0.917 to 1.000) | 0.981 (0.966 to 0.992) | 0.996 (0.992 to 0.999) | 0.974 (0.917 to 1.000) | 0.014 (0.003 to 0.025) |
| mock_specialist_300 | eyepacs | 24 | 0.998 (0.995 to 1.000) | 0.958 (0.862 to 1.000) | 0.983 (0.970 to 0.995) | 0.992 (0.982 to 1.000) | 0.917 (0.810 to 1.000) | 0.008 (0.000 to 0.017) |

### Table 3b. Clinical decisions: referral, sight-threatening disease and maculopathy

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Refer, grade-only: sens / spec | Refer, action rule: sens / spec | Share referred under action rule | Sight-threatening, grade-only: AUROC | Sight-threatening, grade-only: sens / spec | Maculopathy AUROC | Refer, full definition: AUROC | Sight-threatening, full definition: AUROC |
|---|---|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.852 / 0.486 | 0.852 / 0.477 | 0.611 | 0.853 (0.784 to 0.918) | 0.868 / 0.536 | no labels | no labels | no labels |
| mock_jev_zs | mbrset | 0.881 / 0.460 | 0.888 / 0.460 | 0.700 | 0.809 (0.769 to 0.859) | 0.923 / 0.508 | 0.992 (0.980 to 0.999) | 0.761 (0.709 to 0.808) | 0.774 (0.719 to 0.826) |
| mock_jev_zs | messidor2 | 0.806 / 0.529 | 0.823 / 0.516 | 0.586 | 0.872 (0.750 to 0.965) | 0.941 / 0.545 | 0.981 (0.960 to 0.993) | 0.766 (0.695 to 0.836) | 0.756 (0.674 to 0.842) |
| mock_jev_zs | idrid | 0.899 / 0.490 | 0.899 / 0.490 | 0.733 | 0.762 (0.677 to 0.848) | 0.875 / 0.425 | 0.992 (0.981 to 0.999) | 0.746 (0.651 to 0.841) | 0.715 (0.622 to 0.808) |
| mock_jev_zs | ddr | 0.850 / 0.553 | 0.850 / 0.549 | 0.610 | 0.835 (0.769 to 0.893) | 0.880 / 0.567 | no labels | no labels | no labels |
| mock_jev_zs | eyepacs | 0.911 / 0.494 | 0.911 / 0.479 | 0.658 | 0.847 (0.803 to 0.888) | 0.936 / 0.545 | no labels | no labels | no labels |
| mock_jev_zs | pooled_external | 0.861 / 0.507 | 0.865 / 0.502 | 0.640 | 0.825 (0.794 to 0.852) | 0.897 / 0.532 | 0.989 (0.980 to 0.995) | 0.765 (0.731 to 0.799) | 0.758 (0.723 to 0.792) |
| mock_noabstain_zs | aptos | 0.815 / 0.477 | 0.815 / 0.468 | 0.607 | 0.755 (0.674 to 0.842) | 0.789 / 0.623 | no labels | no labels | no labels |
| mock_noabstain_zs | mbrset | 0.873 / 0.475 | 0.873 / 0.460 | 0.694 | 0.808 (0.745 to 0.867) | 0.846 / 0.636 | 0.995 (0.990 to 0.999) | 0.743 (0.684 to 0.797) | 0.783 (0.726 to 0.841) |
| mock_noabstain_zs | messidor2 | 0.790 / 0.484 | 0.790 / 0.484 | 0.600 | 0.821 (0.693 to 0.915) | 0.765 / 0.610 | 0.989 (0.978 to 0.997) | 0.648 (0.565 to 0.716) | 0.605 (0.495 to 0.693) |
| mock_noabstain_zs | idrid | 0.899 / 0.627 | 0.899 / 0.608 | 0.683 | 0.819 (0.727 to 0.888) | 0.925 / 0.613 | 0.993 (0.986 to 0.999) | 0.854 (0.777 to 0.918) | 0.815 (0.734 to 0.885) |
| mock_noabstain_zs | ddr | 0.850 / 0.502 | 0.860 / 0.490 | 0.647 | 0.831 (0.755 to 0.889) | 0.840 / 0.670 | no labels | no labels | no labels |
| mock_noabstain_zs | eyepacs | 0.897 / 0.506 | 0.897 / 0.494 | 0.644 | 0.867 (0.815 to 0.904) | 0.885 / 0.688 | no labels | no labels | no labels |
| mock_noabstain_zs | pooled_external | 0.850 / 0.494 | 0.852 / 0.484 | 0.646 | 0.812 (0.783 to 0.838) | 0.843 / 0.636 | 0.992 (0.987 to 0.996) | 0.743 (0.704 to 0.779) | 0.751 (0.704 to 0.789) |
| mock_jev_ft | aptos | 0.852 / 0.912 | 0.852 / 0.894 | 0.305 | 0.975 (0.962 to 0.986) | 0.947 / 0.925 | no labels | no labels | no labels |
| mock_jev_ft | mbrset | 0.869 / 0.859 | 0.869 / 0.842 | 0.479 | 0.952 (0.925 to 0.972) | 0.840 / 0.897 | 0.991 (0.985 to 0.996) | 0.916 (0.877 to 0.943) | 0.900 (0.841 to 0.933) |
| mock_jev_ft | messidor2 | 0.734 / 0.903 | 0.742 / 0.890 | 0.300 | 0.950 (0.916 to 0.980) | 0.824 / 0.900 | 0.988 (0.980 to 0.994) | 0.868 (0.817 to 0.910) | 0.805 (0.718 to 0.872) |
| mock_jev_ft | idrid | 0.877 / 0.961 | 0.884 / 0.941 | 0.533 | 0.943 (0.913 to 0.967) | 0.912 / 0.806 | 0.994 (0.986 to 1.000) | 0.967 (0.943 to 0.987) | 0.917 (0.879 to 0.955) |
| mock_jev_ft | ddr | 0.832 / 0.935 | 0.832 / 0.908 | 0.376 | 0.977 (0.966 to 0.987) | 0.920 / 0.941 | no labels | no labels | no labels |
| mock_jev_ft | eyepacs | 0.890 / 0.923 | 0.890 / 0.902 | 0.373 | 0.982 (0.972 to 0.988) | 0.917 / 0.943 | no labels | no labels | no labels |
| mock_jev_ft | pooled_external | 0.840 / 0.908 | 0.842 / 0.888 | 0.389 | 0.965 (0.956 to 0.972) | 0.888 / 0.910 | 0.991 (0.987 to 0.994) | 0.913 (0.892 to 0.931) | 0.883 (0.849 to 0.908) |
| mock_jev_ft_100 | aptos | 0.815 / 0.779 | 0.815 / 0.748 | 0.403 | 0.925 (0.888 to 0.959) | 0.895 / 0.808 | no labels | no labels | no labels |
| mock_jev_ft_100 | mbrset | 0.903 / 0.703 | 0.918 / 0.673 | 0.592 | 0.876 (0.820 to 0.923) | 0.872 / 0.717 | 0.991 (0.979 to 0.998) | 0.863 (0.813 to 0.905) | 0.833 (0.771 to 0.881) |
| mock_jev_ft_100 | messidor2 | 0.806 / 0.690 | 0.806 / 0.671 | 0.473 | 0.881 (0.814 to 0.950) | 0.824 / 0.730 | 0.989 (0.976 to 0.998) | 0.741 (0.662 to 0.812) | 0.673 (0.566 to 0.777) |
| mock_jev_ft_100 | idrid | 0.870 / 0.725 | 0.870 / 0.725 | 0.617 | 0.878 (0.808 to 0.932) | 0.850 / 0.688 | 0.990 (0.977 to 0.998) | 0.893 (0.825 to 0.942) | 0.857 (0.792 to 0.918) |
| mock_jev_ft_100 | ddr | 0.785 / 0.706 | 0.804 / 0.682 | 0.512 | 0.887 (0.829 to 0.929) | 0.840 / 0.798 | no labels | no labels | no labels |
| mock_jev_ft_100 | eyepacs | 0.890 / 0.727 | 0.890 / 0.709 | 0.500 | 0.950 (0.930 to 0.968) | 0.936 / 0.822 | no labels | no labels | no labels |
| mock_jev_ft_100 | pooled_external | 0.841 / 0.722 | 0.850 / 0.697 | 0.512 | 0.893 (0.871 to 0.911) | 0.861 / 0.761 | 0.990 (0.984 to 0.995) | 0.835 (0.799 to 0.867) | 0.801 (0.756 to 0.838) |
| mock_jev_ft_300 | aptos | 0.753 / 0.833 | 0.765 / 0.820 | 0.337 | 0.973 (0.951 to 0.988) | 0.895 / 0.932 | no labels | no labels | no labels |
| mock_jev_ft_300 | mbrset | 0.881 / 0.757 | 0.881 / 0.748 | 0.533 | 0.918 (0.883 to 0.950) | 0.821 / 0.857 | 0.992 (0.985 to 0.998) | 0.878 (0.821 to 0.915) | 0.867 (0.815 to 0.909) |
| mock_jev_ft_300 | messidor2 | 0.790 / 0.845 | 0.790 / 0.839 | 0.350 | 0.940 (0.900 to 0.973) | 0.824 / 0.905 | 0.989 (0.978 to 0.999) | 0.834 (0.763 to 0.887) | 0.805 (0.707 to 0.872) |
| mock_jev_ft_300 | idrid | 0.855 / 0.843 | 0.855 / 0.824 | 0.567 | 0.870 (0.799 to 0.932) | 0.775 / 0.825 | 1.000 (1.000 to 1.000) | 0.905 (0.854 to 0.955) | 0.855 (0.788 to 0.916) |
| mock_jev_ft_300 | ddr | 0.850 / 0.878 | 0.850 / 0.871 | 0.405 | 0.964 (0.947 to 0.981) | 0.900 / 0.920 | no labels | no labels | no labels |
| mock_jev_ft_300 | eyepacs | 0.877 / 0.864 | 0.877 / 0.836 | 0.412 | 0.959 (0.938 to 0.976) | 0.833 / 0.912 | no labels | no labels | no labels |
| mock_jev_ft_300 | pooled_external | 0.834 / 0.832 | 0.837 / 0.821 | 0.428 | 0.942 (0.926 to 0.955) | 0.843 / 0.899 | 0.994 (0.990 to 0.997) | 0.871 (0.840 to 0.898) | 0.851 (0.818 to 0.881) |
| mock_generative | aptos | 0.926 / 0.856 | 0.926 / 0.842 | 0.363 | 0.972 (0.953 to 0.989) | 0.947 / 0.857 | no labels | no labels | no labels |
| mock_generative | mbrset | 0.896 / 0.767 | 0.896 / 0.743 | 0.544 | 0.932 (0.881 to 0.964) | 0.910 / 0.806 | 0.996 (0.991 to 0.999) | 0.913 (0.872 to 0.941) | 0.897 (0.835 to 0.936) |
| mock_generative | messidor2 | 0.887 / 0.903 | 0.887 / 0.877 | 0.350 | 0.965 (0.939 to 0.992) | 0.882 / 0.835 | 0.990 (0.972 to 1.000) | 0.870 (0.798 to 0.920) | 0.804 (0.694 to 0.882) |
| mock_generative | idrid | 0.928 / 0.843 | 0.928 / 0.843 | 0.600 | 0.961 (0.929 to 0.985) | 1.000 / 0.738 | 0.989 (0.975 to 0.999) | 0.977 (0.956 to 0.995) | 0.920 (0.869 to 0.966) |
| mock_generative | ddr | 0.869 / 0.859 | 0.869 / 0.831 | 0.435 | 0.957 (0.937 to 0.974) | 0.920 / 0.859 | no labels | no labels | no labels |
| mock_generative | eyepacs | 0.904 / 0.900 | 0.911 / 0.870 | 0.400 | 0.978 (0.967 to 0.988) | 0.987 / 0.874 | no labels | no labels | no labels |
| mock_generative | pooled_external | 0.898 / 0.844 | 0.898 / 0.823 | 0.448 | 0.956 (0.943 to 0.969) | 0.933 / 0.833 | 0.992 (0.986 to 0.997) | 0.917 (0.890 to 0.941) | 0.886 (0.853 to 0.920) |
| mock_specialist | aptos | 0.889 / 0.914 | 0.889 / 0.905 | 0.307 | 0.986 (0.974 to 0.994) | 0.947 / 0.940 | no labels | no labels | no labels |
| mock_specialist | mbrset | 0.910 / 0.842 | 0.910 / 0.807 | 0.514 | 0.968 (0.947 to 0.982) | 0.821 / 0.946 | 0.986 (0.971 to 0.997) | 0.913 (0.870 to 0.944) | 0.899 (0.841 to 0.937) |
| mock_specialist | messidor2 | 0.871 / 0.903 | 0.871 / 0.877 | 0.345 | 0.975 (0.952 to 0.993) | 0.941 / 0.920 | 0.998 (0.995 to 1.000) | 0.899 (0.842 to 0.939) | 0.814 (0.735 to 0.882) |
| mock_specialist | idrid | 0.942 / 0.922 | 0.942 / 0.902 | 0.583 | 0.938 (0.893 to 0.974) | 0.825 / 0.850 | 0.988 (0.969 to 0.998) | 0.971 (0.947 to 0.992) | 0.905 (0.851 to 0.961) |
| mock_specialist | ddr | 0.925 / 0.922 | 0.925 / 0.898 | 0.405 | 0.974 (0.959 to 0.986) | 0.800 / 0.955 | no labels | no labels | no labels |
| mock_specialist | eyepacs | 0.918 / 0.930 | 0.918 / 0.912 | 0.372 | 0.985 (0.977 to 0.993) | 0.859 / 0.965 | no labels | no labels | no labels |
| mock_specialist | pooled_external | 0.909 / 0.898 | 0.909 / 0.876 | 0.418 | 0.972 (0.965 to 0.980) | 0.848 / 0.935 | 0.990 (0.983 to 0.996) | 0.922 (0.899 to 0.945) | 0.883 (0.848 to 0.912) |
| mock_specialist_100 | aptos | 0.877 / 0.640 | 0.877 / 0.631 | 0.505 | 0.902 (0.853 to 0.936) | 0.947 / 0.728 | no labels | no labels | no labels |
| mock_specialist_100 | mbrset | 0.851 / 0.569 | 0.851 / 0.550 | 0.636 | 0.844 (0.791 to 0.888) | 0.795 / 0.663 | 0.986 (0.971 to 0.997) | 0.772 (0.705 to 0.815) | 0.783 (0.713 to 0.827) |
| mock_specialist_100 | messidor2 | 0.839 / 0.600 | 0.839 / 0.574 | 0.550 | 0.860 (0.782 to 0.923) | 0.941 / 0.705 | 0.998 (0.995 to 1.000) | 0.780 (0.712 to 0.836) | 0.714 (0.620 to 0.790) |
| mock_specialist_100 | idrid | 0.913 / 0.549 | 0.913 / 0.549 | 0.717 | 0.807 (0.726 to 0.883) | 0.850 / 0.475 | 0.988 (0.969 to 0.998) | 0.841 (0.772 to 0.908) | 0.798 (0.720 to 0.877) |
| mock_specialist_100 | ddr | 0.841 / 0.616 | 0.841 / 0.604 | 0.570 | 0.861 (0.813 to 0.910) | 0.800 / 0.696 | no labels | no labels | no labels |
| mock_specialist_100 | eyepacs | 0.897 / 0.624 | 0.897 / 0.606 | 0.570 | 0.899 (0.869 to 0.930) | 0.872 / 0.751 | no labels | no labels | no labels |
| mock_specialist_100 | pooled_external | 0.861 / 0.605 | 0.861 / 0.590 | 0.582 | 0.860 (0.836 to 0.883) | 0.843 / 0.682 | 0.990 (0.983 to 0.996) | 0.792 (0.756 to 0.829) | 0.776 (0.737 to 0.813) |
| mock_specialist_300 | aptos | 0.852 / 0.793 | 0.852 / 0.784 | 0.386 | 0.954 (0.921 to 0.974) | 0.947 / 0.838 | no labels | no labels | no labels |
| mock_specialist_300 | mbrset | 0.881 / 0.728 | 0.881 / 0.703 | 0.561 | 0.914 (0.872 to 0.945) | 0.821 / 0.806 | 0.986 (0.971 to 0.997) | 0.851 (0.800 to 0.888) | 0.852 (0.784 to 0.892) |
| mock_specialist_300 | messidor2 | 0.823 / 0.781 | 0.823 / 0.755 | 0.418 | 0.929 (0.885 to 0.965) | 0.941 / 0.810 | 0.998 (0.995 to 1.000) | 0.853 (0.793 to 0.897) | 0.770 (0.686 to 0.845) |
| mock_specialist_300 | idrid | 0.928 / 0.686 | 0.928 / 0.667 | 0.675 | 0.880 (0.813 to 0.935) | 0.875 / 0.662 | 0.988 (0.969 to 0.998) | 0.923 (0.880 to 0.967) | 0.867 (0.797 to 0.932) |
| mock_specialist_300 | ddr | 0.879 / 0.808 | 0.879 / 0.788 | 0.463 | 0.934 (0.902 to 0.961) | 0.840 / 0.843 | no labels | no labels | no labels |
| mock_specialist_300 | eyepacs | 0.897 / 0.812 | 0.897 / 0.794 | 0.446 | 0.947 (0.926 to 0.968) | 0.872 / 0.854 | no labels | no labels | no labels |
| mock_specialist_300 | pooled_external | 0.874 / 0.774 | 0.874 / 0.755 | 0.483 | 0.927 (0.911 to 0.941) | 0.865 / 0.814 | 0.990 (0.983 to 0.996) | 0.868 (0.840 to 0.899) | 0.839 (0.805 to 0.872) |

Action rule: refer if referable disease, ungradeable, or the model abstains. Full definition adds maculopathy and is reported only where maculopathy is labelled.

### Table 3c. Coherence of the five answers, direct versus derived referral, patient-level referral

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Coherent answers | Referable AUROC, direct | Referable AUROC, derived | Direct minus derived | Patient-level refer: sens / spec |
|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.856 (0.816 to 0.894) | 0.795 | 0.788 | 0.008 (-0.002 to 0.019) | 0.852 / 0.477 |
| mock_jev_zs | mbrset | 0.855 (0.815 to 0.887) | 0.764 | 0.755 | 0.009 (-0.005 to 0.020) | 1.000 / 0.045 |
| mock_jev_zs | messidor2 | 0.830 (0.776 to 0.877) | 0.794 | 0.794 | 0.001 (-0.009 to 0.011) | 0.823 / 0.516 |
| mock_jev_zs | idrid | 0.737 (0.667 to 0.811) | 0.748 | 0.749 | -0.001 (-0.020 to 0.019) | 0.899 / 0.490 |
| mock_jev_zs | ddr | 0.878 (0.842 to 0.913) | 0.771 | 0.760 | 0.011 (0.000 to 0.021) | 0.850 / 0.549 |
| mock_jev_zs | eyepacs | 0.862 (0.833 to 0.895) | 0.829 | 0.825 | 0.004 (-0.004 to 0.011) | 1.000 / 0.258 |
| mock_noabstain_zs | aptos | 0.876 (0.834 to 0.913) | 0.705 | 0.699 | 0.006 (-0.005 to 0.018) | 0.815 / 0.468 |
| mock_noabstain_zs | mbrset | 0.872 (0.835 to 0.905) | 0.747 | 0.738 | 0.009 (-0.003 to 0.020) | 1.000 / 0.068 |
| mock_noabstain_zs | messidor2 | 0.788 (0.730 to 0.842) | 0.710 | 0.699 | 0.011 (0.000 to 0.024) | 0.790 / 0.484 |
| mock_noabstain_zs | idrid | 0.847 (0.782 to 0.907) | 0.866 | 0.843 | 0.024 (0.008 to 0.043) | 0.899 / 0.608 |
| mock_noabstain_zs | ddr | 0.838 (0.805 to 0.877) | 0.770 | 0.777 | -0.006 (-0.017 to 0.004) | 0.860 / 0.490 |
| mock_noabstain_zs | eyepacs | 0.852 (0.822 to 0.885) | 0.827 | 0.825 | 0.002 (-0.006 to 0.008) | 0.988 / 0.288 |
| mock_jev_ft | aptos | 0.823 (0.795 to 0.854) | 0.955 | 0.966 | -0.011 (-0.019 to -0.004) | 0.852 / 0.894 |
| mock_jev_ft | mbrset | 0.847 (0.812 to 0.879) | 0.936 | 0.939 | -0.004 (-0.011 to 0.004) | 0.967 / 0.580 |
| mock_jev_ft | messidor2 | 0.806 (0.757 to 0.849) | 0.925 | 0.936 | -0.011 (-0.021 to -0.002) | 0.742 / 0.890 |
| mock_jev_ft | idrid | 0.821 (0.770 to 0.875) | 0.977 | 0.979 | -0.002 (-0.009 to 0.004) | 0.884 / 0.941 |
| mock_jev_ft | ddr | 0.832 (0.803 to 0.860) | 0.962 | 0.964 | -0.002 (-0.009 to 0.004) | 0.832 / 0.908 |
| mock_jev_ft | eyepacs | 0.828 (0.803 to 0.851) | 0.974 | 0.978 | -0.004 (-0.009 to -0.000) | 0.953 / 0.856 |
| mock_jev_ft_100 | aptos | 0.844 (0.798 to 0.882) | 0.883 | 0.886 | -0.003 (-0.013 to 0.006) | 0.815 / 0.748 |
| mock_jev_ft_100 | mbrset | 0.844 (0.800 to 0.877) | 0.887 | 0.882 | 0.005 (-0.004 to 0.014) | 0.978 / 0.318 |
| mock_jev_ft_100 | messidor2 | 0.825 (0.770 to 0.870) | 0.841 | 0.845 | -0.004 (-0.016 to 0.009) | 0.806 / 0.671 |
| mock_jev_ft_100 | idrid | 0.765 (0.683 to 0.833) | 0.906 | 0.909 | -0.003 (-0.015 to 0.011) | 0.870 / 0.725 |
| mock_jev_ft_100 | ddr | 0.790 (0.751 to 0.832) | 0.848 | 0.854 | -0.006 (-0.016 to 0.004) | 0.804 / 0.682 |
| mock_jev_ft_100 | eyepacs | 0.795 (0.750 to 0.834) | 0.907 | 0.910 | -0.003 (-0.013 to 0.007) | 0.965 / 0.528 |
| mock_jev_ft_300 | aptos | 0.860 (0.819 to 0.897) | 0.903 | 0.905 | -0.003 (-0.011 to 0.007) | 0.765 / 0.820 |
| mock_jev_ft_300 | mbrset | 0.840 (0.795 to 0.878) | 0.907 | 0.911 | -0.004 (-0.014 to 0.003) | 0.978 / 0.364 |
| mock_jev_ft_300 | messidor2 | 0.808 (0.762 to 0.860) | 0.897 | 0.915 | -0.018 (-0.031 to -0.005) | 0.790 / 0.839 |
| mock_jev_ft_300 | idrid | 0.724 (0.638 to 0.800) | 0.923 | 0.919 | 0.003 (-0.016 to 0.025) | 0.855 / 0.824 |
| mock_jev_ft_300 | ddr | 0.818 (0.782 to 0.857) | 0.946 | 0.941 | 0.005 (-0.002 to 0.014) | 0.850 / 0.871 |
| mock_jev_ft_300 | eyepacs | 0.822 (0.790 to 0.857) | 0.949 | 0.955 | -0.006 (-0.014 to 0.003) | 0.942 / 0.718 |
| mock_generative | aptos | 0.837 (0.797 to 0.881) | 0.963 | 0.964 | -0.001 (-0.007 to 0.004) | 0.926 / 0.842 |
| mock_generative | mbrset | 0.876 (0.833 to 0.909) | 0.927 | 0.926 | 0.001 (-0.006 to 0.008) | 1.000 / 0.477 |
| mock_generative | messidor2 | 0.827 (0.777 to 0.875) | 0.939 | 0.941 | -0.002 (-0.011 to 0.008) | 0.887 / 0.877 |
| mock_generative | idrid | 0.798 (0.720 to 0.866) | 0.976 | 0.975 | 0.001 (-0.003 to 0.006) | 0.928 / 0.843 |
| mock_generative | ddr | 0.845 (0.811 to 0.880) | 0.946 | 0.939 | 0.007 (-0.001 to 0.018) | 0.869 / 0.831 |
| mock_generative | eyepacs | 0.828 (0.794 to 0.865) | 0.969 | 0.971 | -0.003 (-0.008 to 0.001) | 0.988 / 0.785 |
| mock_specialist | aptos | 0.806 (0.758 to 0.849) | 0.965 | 0.969 | -0.004 (-0.010 to 0.002) | 0.889 / 0.905 |
| mock_specialist | mbrset | 0.825 (0.780 to 0.856) | 0.945 | 0.942 | 0.003 (-0.005 to 0.011) | 0.978 / 0.591 |
| mock_specialist | messidor2 | 0.746 (0.684 to 0.800) | 0.966 | 0.965 | 0.001 (-0.009 to 0.010) | 0.871 / 0.877 |
| mock_specialist | idrid | 0.750 (0.668 to 0.831) | 0.975 | 0.978 | -0.003 (-0.012 to 0.004) | 0.942 / 0.902 |
| mock_specialist | ddr | 0.882 (0.847 to 0.912) | 0.975 | 0.973 | 0.002 (-0.004 to 0.007) | 0.925 / 0.898 |
| mock_specialist | eyepacs | 0.829 (0.793 to 0.864) | 0.977 | 0.976 | 0.001 (-0.004 to 0.005) | 0.953 / 0.847 |
| mock_specialist_100 | aptos | 0.833 (0.794 to 0.880) | 0.844 | 0.840 | 0.004 (-0.005 to 0.014) | 0.877 / 0.631 |
| mock_specialist_100 | mbrset | 0.847 (0.806 to 0.884) | 0.802 | 0.805 | -0.003 (-0.010 to 0.004) | 1.000 / 0.159 |
| mock_specialist_100 | messidor2 | 0.780 (0.722 to 0.831) | 0.827 | 0.825 | 0.002 (-0.011 to 0.014) | 0.839 / 0.574 |
| mock_specialist_100 | idrid | 0.793 (0.713 to 0.863) | 0.846 | 0.848 | -0.001 (-0.015 to 0.013) | 0.913 / 0.549 |
| mock_specialist_100 | ddr | 0.896 (0.861 to 0.926) | 0.831 | 0.829 | 0.002 (-0.007 to 0.010) | 0.841 / 0.604 |
| mock_specialist_100 | eyepacs | 0.803 (0.772 to 0.835) | 0.864 | 0.862 | 0.002 (-0.004 to 0.009) | 0.965 / 0.423 |
| mock_specialist_300 | aptos | 0.819 (0.776 to 0.863) | 0.901 | 0.917 | -0.016 (-0.026 to -0.007) | 0.852 / 0.784 |
| mock_specialist_300 | mbrset | 0.844 (0.800 to 0.883) | 0.881 | 0.878 | 0.003 (-0.005 to 0.013) | 0.978 / 0.318 |
| mock_specialist_300 | messidor2 | 0.756 (0.696 to 0.810) | 0.905 | 0.903 | 0.003 (-0.011 to 0.014) | 0.823 / 0.755 |
| mock_specialist_300 | idrid | 0.846 (0.790 to 0.902) | 0.929 | 0.929 | 0.000 (-0.011 to 0.012) | 0.928 / 0.667 |
| mock_specialist_300 | ddr | 0.885 (0.850 to 0.918) | 0.911 | 0.910 | 0.001 (-0.006 to 0.008) | 0.879 / 0.788 |
| mock_specialist_300 | eyepacs | 0.833 (0.795 to 0.866) | 0.926 | 0.929 | -0.003 (-0.010 to 0.006) | 0.977 / 0.663 |

Coherent: the referral and sight-threatening answers agree with the grade and maculopathy answers. Patient level uses the worse eye and equals image level where a dataset has no patient identifiers.

### Table 4a. Sensitivity to question wording (fixed subset of each test set)

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Metric | Wordings | Mean | Lowest | Highest | Range |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | qwk | 3 | 0.488 | 0.484 | 0.49 | 0.006 |
| mock_jev_zs | aptos | ref_auroc | 3 | 0.816 | 0.812 | 0.822 | 0.01 |
| mock_jev_zs | aptos | ece_grade | 3 | 0.136 | 0.119 | 0.158 | 0.038 |
| mock_jev_zs | ddr | qwk | 3 | 0.455 | 0.44 | 0.466 | 0.026 |
| mock_jev_zs | ddr | ref_auroc | 3 | 0.807 | 0.806 | 0.807 | 0.001 |
| mock_jev_zs | ddr | ece_grade | 3 | 0.101 | 0.091 | 0.112 | 0.021 |
| mock_jev_zs | idrid | qwk | 3 | 0.462 | 0.444 | 0.481 | 0.037 |
| mock_jev_zs | idrid | ref_auroc | 3 | 0.744 | 0.739 | 0.748 | 0.009 |
| mock_jev_zs | idrid | ece_grade | 3 | 0.113 | 0.101 | 0.132 | 0.03 |
| mock_jev_zs | mbrset | qwk | 3 | 0.446 | 0.43 | 0.46 | 0.03 |
| mock_jev_zs | mbrset | ref_auroc | 3 | 0.744 | 0.738 | 0.749 | 0.011 |
| mock_jev_zs | mbrset | ece_grade | 3 | 0.131 | 0.122 | 0.148 | 0.026 |
| mock_jev_zs | messidor2 | qwk | 3 | 0.522 | 0.511 | 0.528 | 0.018 |
| mock_jev_zs | messidor2 | ref_auroc | 3 | 0.838 | 0.837 | 0.839 | 0.002 |
| mock_jev_zs | messidor2 | ece_grade | 3 | 0.116 | 0.093 | 0.139 | 0.046 |
| mock_jev_zs | eyepacs | qwk | 3 | 0.535 | 0.532 | 0.537 | 0.004 |
| mock_jev_zs | eyepacs | ref_auroc | 3 | 0.762 | 0.755 | 0.766 | 0.011 |
| mock_jev_zs | eyepacs | ece_grade | 3 | 0.127 | 0.124 | 0.133 | 0.009 |
| mock_noabstain_zs | aptos | qwk | 3 | 0.301 | 0.297 | 0.308 | 0.011 |
| mock_noabstain_zs | aptos | ref_auroc | 3 | 0.715 | 0.71 | 0.72 | 0.01 |
| mock_noabstain_zs | aptos | ece_grade | 3 | 0.155 | 0.153 | 0.159 | 0.006 |
| mock_noabstain_zs | ddr | qwk | 3 | 0.405 | 0.4 | 0.411 | 0.01 |
| mock_noabstain_zs | ddr | ref_auroc | 3 | 0.757 | 0.752 | 0.761 | 0.009 |
| mock_noabstain_zs | ddr | ece_grade | 3 | 0.139 | 0.125 | 0.151 | 0.025 |
| mock_noabstain_zs | idrid | qwk | 3 | 0.627 | 0.622 | 0.633 | 0.011 |
| mock_noabstain_zs | idrid | ref_auroc | 3 | 0.862 | 0.857 | 0.866 | 0.009 |
| mock_noabstain_zs | idrid | ece_grade | 3 | 0.084 | 0.046 | 0.115 | 0.068 |
| mock_noabstain_zs | mbrset | qwk | 3 | 0.403 | 0.399 | 0.407 | 0.008 |
| mock_noabstain_zs | mbrset | ref_auroc | 3 | 0.731 | 0.726 | 0.736 | 0.01 |
| mock_noabstain_zs | mbrset | ece_grade | 3 | 0.107 | 0.087 | 0.126 | 0.039 |
| mock_noabstain_zs | messidor2 | qwk | 3 | 0.318 | 0.316 | 0.322 | 0.006 |
| mock_noabstain_zs | messidor2 | ref_auroc | 3 | 0.701 | 0.694 | 0.704 | 0.01 |
| mock_noabstain_zs | messidor2 | ece_grade | 3 | 0.118 | 0.114 | 0.122 | 0.008 |
| mock_noabstain_zs | eyepacs | qwk | 3 | 0.493 | 0.467 | 0.509 | 0.042 |
| mock_noabstain_zs | eyepacs | ref_auroc | 3 | 0.799 | 0.797 | 0.8 | 0.003 |
| mock_noabstain_zs | eyepacs | ece_grade | 3 | 0.153 | 0.139 | 0.181 | 0.042 |
| mock_jev_ft | aptos | qwk | 3 | 0.862 | 0.855 | 0.87 | 0.015 |
| mock_jev_ft | aptos | ref_auroc | 3 | 0.961 | 0.956 | 0.965 | 0.009 |
| mock_jev_ft | aptos | ece_grade | 3 | 0.144 | 0.126 | 0.156 | 0.029 |
| mock_jev_ft | ddr | qwk | 3 | 0.833 | 0.826 | 0.84 | 0.015 |
| mock_jev_ft | ddr | ref_auroc | 3 | 0.949 | 0.943 | 0.954 | 0.011 |
| mock_jev_ft | ddr | ece_grade | 3 | 0.143 | 0.129 | 0.155 | 0.026 |
| mock_jev_ft | idrid | qwk | 3 | 0.88 | 0.876 | 0.882 | 0.006 |
| mock_jev_ft | idrid | ref_auroc | 3 | 0.977 | 0.976 | 0.977 | 0.002 |
| mock_jev_ft | idrid | ece_grade | 3 | 0.146 | 0.123 | 0.17 | 0.048 |
| mock_jev_ft | mbrset | qwk | 3 | 0.844 | 0.834 | 0.858 | 0.024 |
| mock_jev_ft | mbrset | ref_auroc | 3 | 0.943 | 0.939 | 0.946 | 0.007 |
| mock_jev_ft | mbrset | ece_grade | 3 | 0.146 | 0.126 | 0.166 | 0.041 |
| mock_jev_ft | messidor2 | qwk | 3 | 0.781 | 0.776 | 0.79 | 0.014 |
| mock_jev_ft | messidor2 | ref_auroc | 3 | 0.936 | 0.933 | 0.937 | 0.005 |
| mock_jev_ft | messidor2 | ece_grade | 3 | 0.15 | 0.137 | 0.158 | 0.022 |
| mock_jev_ft | eyepacs | qwk | 3 | 0.893 | 0.892 | 0.895 | 0.004 |
| mock_jev_ft | eyepacs | ref_auroc | 3 | 0.977 | 0.972 | 0.98 | 0.008 |
| mock_jev_ft | eyepacs | ece_grade | 3 | 0.068 | 0.064 | 0.076 | 0.012 |
| mock_jev_ft_100 | aptos | qwk | 3 | 0.695 | 0.686 | 0.702 | 0.016 |
| mock_jev_ft_100 | aptos | ref_auroc | 3 | 0.883 | 0.874 | 0.888 | 0.015 |
| mock_jev_ft_100 | aptos | ece_grade | 3 | 0.145 | 0.127 | 0.171 | 0.044 |
| mock_jev_ft_100 | ddr | qwk | 3 | 0.659 | 0.652 | 0.667 | 0.015 |
| mock_jev_ft_100 | ddr | ref_auroc | 3 | 0.867 | 0.865 | 0.869 | 0.004 |
| mock_jev_ft_100 | ddr | ece_grade | 3 | 0.15 | 0.121 | 0.171 | 0.051 |
| mock_jev_ft_100 | idrid | qwk | 3 | 0.728 | 0.721 | 0.737 | 0.016 |
| mock_jev_ft_100 | idrid | ref_auroc | 3 | 0.904 | 0.899 | 0.906 | 0.007 |
| mock_jev_ft_100 | idrid | ece_grade | 3 | 0.116 | 0.1 | 0.136 | 0.036 |
| mock_jev_ft_100 | mbrset | qwk | 3 | 0.694 | 0.689 | 0.705 | 0.016 |
| mock_jev_ft_100 | mbrset | ref_auroc | 3 | 0.882 | 0.877 | 0.887 | 0.01 |
| mock_jev_ft_100 | mbrset | ece_grade | 3 | 0.165 | 0.159 | 0.173 | 0.014 |
| mock_jev_ft_100 | messidor2 | qwk | 3 | 0.558 | 0.527 | 0.578 | 0.052 |
| mock_jev_ft_100 | messidor2 | ref_auroc | 3 | 0.867 | 0.862 | 0.87 | 0.009 |
| mock_jev_ft_100 | messidor2 | ece_grade | 3 | 0.165 | 0.153 | 0.18 | 0.027 |
| mock_jev_ft_100 | eyepacs | qwk | 3 | 0.759 | 0.757 | 0.763 | 0.006 |
| mock_jev_ft_100 | eyepacs | ref_auroc | 3 | 0.897 | 0.893 | 0.899 | 0.006 |
| mock_jev_ft_100 | eyepacs | ece_grade | 3 | 0.087 | 0.059 | 0.127 | 0.068 |
| mock_jev_ft_300 | aptos | qwk | 3 | 0.763 | 0.759 | 0.766 | 0.007 |
| mock_jev_ft_300 | aptos | ref_auroc | 3 | 0.943 | 0.937 | 0.948 | 0.01 |
| mock_jev_ft_300 | aptos | ece_grade | 3 | 0.181 | 0.163 | 0.214 | 0.051 |
| mock_jev_ft_300 | ddr | qwk | 3 | 0.775 | 0.768 | 0.779 | 0.01 |
| mock_jev_ft_300 | ddr | ref_auroc | 3 | 0.922 | 0.914 | 0.93 | 0.016 |
| mock_jev_ft_300 | ddr | ece_grade | 3 | 0.172 | 0.144 | 0.207 | 0.064 |
| mock_jev_ft_300 | idrid | qwk | 3 | 0.743 | 0.735 | 0.755 | 0.02 |
| mock_jev_ft_300 | idrid | ref_auroc | 3 | 0.919 | 0.914 | 0.923 | 0.008 |
| mock_jev_ft_300 | idrid | ece_grade | 3 | 0.247 | 0.23 | 0.271 | 0.041 |
| mock_jev_ft_300 | mbrset | qwk | 3 | 0.743 | 0.734 | 0.757 | 0.024 |
| mock_jev_ft_300 | mbrset | ref_auroc | 3 | 0.917 | 0.91 | 0.92 | 0.011 |
| mock_jev_ft_300 | mbrset | ece_grade | 3 | 0.173 | 0.133 | 0.198 | 0.065 |
| mock_jev_ft_300 | messidor2 | qwk | 3 | 0.732 | 0.725 | 0.736 | 0.011 |
| mock_jev_ft_300 | messidor2 | ref_auroc | 3 | 0.898 | 0.892 | 0.902 | 0.01 |
| mock_jev_ft_300 | messidor2 | ece_grade | 3 | 0.155 | 0.149 | 0.159 | 0.009 |
| mock_jev_ft_300 | eyepacs | qwk | 3 | 0.833 | 0.815 | 0.853 | 0.038 |
| mock_jev_ft_300 | eyepacs | ref_auroc | 3 | 0.938 | 0.929 | 0.949 | 0.02 |
| mock_jev_ft_300 | eyepacs | ece_grade | 3 | 0.073 | 0.057 | 0.104 | 0.047 |
| mock_generative | aptos | qwk | 3 | 0.814 | 0.806 | 0.82 | 0.015 |
| mock_generative | aptos | ref_auroc | 3 | 0.949 | 0.946 | 0.951 | 0.005 |
| mock_generative | aptos | ece_grade | 3 | 0.149 | 0.13 | 0.171 | 0.04 |
| mock_generative | ddr | qwk | 3 | 0.809 | 0.788 | 0.825 | 0.037 |
| mock_generative | ddr | ref_auroc | 3 | 0.95 | 0.945 | 0.953 | 0.008 |
| mock_generative | ddr | ece_grade | 3 | 0.133 | 0.122 | 0.143 | 0.021 |
| mock_generative | idrid | qwk | 3 | 0.879 | 0.875 | 0.885 | 0.01 |
| mock_generative | idrid | ref_auroc | 3 | 0.974 | 0.973 | 0.976 | 0.003 |
| mock_generative | idrid | ece_grade | 3 | 0.126 | 0.118 | 0.134 | 0.016 |
| mock_generative | mbrset | qwk | 3 | 0.832 | 0.828 | 0.835 | 0.007 |
| mock_generative | mbrset | ref_auroc | 3 | 0.951 | 0.947 | 0.954 | 0.008 |
| mock_generative | mbrset | ece_grade | 3 | 0.19 | 0.172 | 0.221 | 0.049 |
| mock_generative | messidor2 | qwk | 3 | 0.791 | 0.789 | 0.793 | 0.004 |
| mock_generative | messidor2 | ref_auroc | 3 | 0.941 | 0.939 | 0.943 | 0.004 |
| mock_generative | messidor2 | ece_grade | 3 | 0.098 | 0.077 | 0.115 | 0.038 |
| mock_generative | eyepacs | qwk | 3 | 0.885 | 0.875 | 0.894 | 0.019 |
| mock_generative | eyepacs | ref_auroc | 3 | 0.966 | 0.965 | 0.968 | 0.003 |
| mock_generative | eyepacs | ece_grade | 3 | 0.085 | 0.075 | 0.095 | 0.02 |
| mock_specialist | aptos | qwk | 3 | 0.888 | 0.882 | 0.895 | 0.013 |
| mock_specialist | aptos | ref_auroc | 3 | 0.957 | 0.952 | 0.959 | 0.008 |
| mock_specialist | aptos | ece_grade | 3 | 0.101 | 0.087 | 0.118 | 0.032 |
| mock_specialist | ddr | qwk | 3 | 0.854 | 0.851 | 0.86 | 0.01 |
| mock_specialist | ddr | ref_auroc | 3 | 0.972 | 0.968 | 0.976 | 0.008 |
| mock_specialist | ddr | ece_grade | 3 | 0.126 | 0.106 | 0.138 | 0.032 |
| mock_specialist | idrid | qwk | 3 | 0.883 | 0.873 | 0.896 | 0.023 |
| mock_specialist | idrid | ref_auroc | 3 | 0.975 | 0.973 | 0.977 | 0.004 |
| mock_specialist | idrid | ece_grade | 3 | 0.141 | 0.116 | 0.168 | 0.052 |
| mock_specialist | mbrset | qwk | 3 | 0.866 | 0.864 | 0.868 | 0.004 |
| mock_specialist | mbrset | ref_auroc | 3 | 0.949 | 0.938 | 0.957 | 0.019 |
| mock_specialist | mbrset | ece_grade | 3 | 0.177 | 0.173 | 0.18 | 0.007 |
| mock_specialist | messidor2 | qwk | 3 | 0.861 | 0.857 | 0.866 | 0.009 |
| mock_specialist | messidor2 | ref_auroc | 3 | 0.962 | 0.957 | 0.967 | 0.01 |
| mock_specialist | messidor2 | ece_grade | 3 | 0.124 | 0.096 | 0.139 | 0.043 |
| mock_specialist | eyepacs | qwk | 3 | 0.923 | 0.917 | 0.927 | 0.01 |
| mock_specialist | eyepacs | ref_auroc | 3 | 0.993 | 0.99 | 0.996 | 0.006 |
| mock_specialist | eyepacs | ece_grade | 3 | 0.057 | 0.042 | 0.065 | 0.023 |
| mock_specialist_100 | aptos | qwk | 3 | 0.58 | 0.575 | 0.584 | 0.009 |
| mock_specialist_100 | aptos | ref_auroc | 3 | 0.823 | 0.82 | 0.825 | 0.005 |
| mock_specialist_100 | aptos | ece_grade | 3 | 0.142 | 0.129 | 0.16 | 0.03 |
| mock_specialist_100 | ddr | qwk | 3 | 0.497 | 0.489 | 0.505 | 0.016 |
| mock_specialist_100 | ddr | ref_auroc | 3 | 0.827 | 0.823 | 0.832 | 0.01 |
| mock_specialist_100 | ddr | ece_grade | 3 | 0.173 | 0.167 | 0.178 | 0.012 |
| mock_specialist_100 | idrid | qwk | 3 | 0.608 | 0.602 | 0.617 | 0.014 |
| mock_specialist_100 | idrid | ref_auroc | 3 | 0.844 | 0.842 | 0.846 | 0.005 |
| mock_specialist_100 | idrid | ece_grade | 3 | 0.111 | 0.091 | 0.144 | 0.053 |
| mock_specialist_100 | mbrset | qwk | 3 | 0.569 | 0.56 | 0.577 | 0.017 |
| mock_specialist_100 | mbrset | ref_auroc | 3 | 0.82 | 0.816 | 0.826 | 0.01 |
| mock_specialist_100 | mbrset | ece_grade | 3 | 0.159 | 0.137 | 0.178 | 0.041 |
| mock_specialist_100 | messidor2 | qwk | 3 | 0.563 | 0.552 | 0.577 | 0.024 |
| mock_specialist_100 | messidor2 | ref_auroc | 3 | 0.828 | 0.821 | 0.831 | 0.01 |
| mock_specialist_100 | messidor2 | ece_grade | 3 | 0.139 | 0.128 | 0.161 | 0.033 |
| mock_specialist_100 | eyepacs | qwk | 3 | 0.721 | 0.714 | 0.733 | 0.019 |
| mock_specialist_100 | eyepacs | ref_auroc | 3 | 0.93 | 0.925 | 0.935 | 0.01 |
| mock_specialist_100 | eyepacs | ece_grade | 3 | 0.082 | 0.077 | 0.09 | 0.013 |
| mock_specialist_300 | aptos | qwk | 3 | 0.728 | 0.717 | 0.737 | 0.021 |
| mock_specialist_300 | aptos | ref_auroc | 3 | 0.901 | 0.89 | 0.909 | 0.019 |
| mock_specialist_300 | aptos | ece_grade | 3 | 0.15 | 0.111 | 0.185 | 0.074 |
| mock_specialist_300 | ddr | qwk | 3 | 0.669 | 0.664 | 0.675 | 0.011 |
| mock_specialist_300 | ddr | ref_auroc | 3 | 0.9 | 0.895 | 0.903 | 0.008 |
| mock_specialist_300 | ddr | ece_grade | 3 | 0.148 | 0.132 | 0.175 | 0.042 |
| mock_specialist_300 | idrid | qwk | 3 | 0.764 | 0.753 | 0.773 | 0.019 |
| mock_specialist_300 | idrid | ref_auroc | 3 | 0.927 | 0.925 | 0.929 | 0.004 |
| mock_specialist_300 | idrid | ece_grade | 3 | 0.157 | 0.155 | 0.16 | 0.005 |
| mock_specialist_300 | mbrset | qwk | 3 | 0.72 | 0.712 | 0.73 | 0.018 |
| mock_specialist_300 | mbrset | ref_auroc | 3 | 0.891 | 0.886 | 0.897 | 0.01 |
| mock_specialist_300 | mbrset | ece_grade | 3 | 0.197 | 0.182 | 0.21 | 0.028 |
| mock_specialist_300 | messidor2 | qwk | 3 | 0.698 | 0.677 | 0.718 | 0.041 |
| mock_specialist_300 | messidor2 | ref_auroc | 3 | 0.904 | 0.899 | 0.907 | 0.008 |
| mock_specialist_300 | messidor2 | ece_grade | 3 | 0.13 | 0.098 | 0.155 | 0.057 |
| mock_specialist_300 | eyepacs | qwk | 3 | 0.828 | 0.819 | 0.833 | 0.014 |
| mock_specialist_300 | eyepacs | ref_auroc | 3 | 0.974 | 0.965 | 0.981 | 0.017 |
| mock_specialist_300 | eyepacs | ece_grade | 3 | 0.085 | 0.077 | 0.096 | 0.019 |

### Table 4b. Effect of temperature scaling fitted on the EyePACS calibration split

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Dataset | Grade ECE, raw | Grade ECE, calibrated | Referable ECE, raw | Referable ECE, calibrated | AURC, raw | AURC, calibrated |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | aptos | 0.366 | 0.110 | 0.238 | 0.207 | 0.374 | 0.315 |
| mock_jev_zs | mbrset | 0.443 | 0.080 | 0.245 | 0.185 | 0.465 | 0.441 |
| mock_jev_zs | messidor2 | 0.457 | 0.132 | 0.219 | 0.188 | 0.452 | 0.387 |
| mock_jev_zs | idrid | 0.451 | 0.105 | 0.247 | 0.197 | 0.428 | 0.442 |
| mock_jev_zs | ddr | 0.391 | 0.124 | 0.230 | 0.187 | 0.334 | 0.328 |
| mock_jev_zs | eyepacs | 0.405 | 0.081 | 0.171 | 0.139 | 0.411 | 0.354 |
| mock_noabstain_zs | aptos | 0.433 | 0.132 | 0.282 | 0.239 | 0.414 | 0.377 |
| mock_noabstain_zs | mbrset | 0.460 | 0.076 | 0.270 | 0.194 | 0.518 | 0.491 |
| mock_noabstain_zs | messidor2 | 0.441 | 0.095 | 0.270 | 0.220 | 0.413 | 0.384 |
| mock_noabstain_zs | idrid | 0.441 | 0.092 | 0.154 | 0.135 | 0.474 | 0.416 |
| mock_noabstain_zs | ddr | 0.359 | 0.140 | 0.230 | 0.161 | 0.350 | 0.330 |
| mock_noabstain_zs | eyepacs | 0.386 | 0.130 | 0.176 | 0.128 | 0.408 | 0.384 |
| mock_jev_ft | aptos | 0.129 | 0.114 | 0.083 | 0.061 | 0.191 | 0.189 |
| mock_jev_ft | mbrset | 0.135 | 0.108 | 0.061 | 0.074 | 0.239 | 0.237 |
| mock_jev_ft | messidor2 | 0.172 | 0.160 | 0.071 | 0.078 | 0.210 | 0.209 |
| mock_jev_ft | idrid | 0.169 | 0.170 | 0.108 | 0.081 | 0.224 | 0.222 |
| mock_jev_ft | ddr | 0.109 | 0.106 | 0.074 | 0.042 | 0.165 | 0.164 |
| mock_jev_ft | eyepacs | 0.074 | 0.064 | 0.077 | 0.042 | 0.176 | 0.174 |
| mock_jev_ft_100 | aptos | 0.231 | 0.118 | 0.093 | 0.104 | 0.229 | 0.213 |
| mock_jev_ft_100 | mbrset | 0.334 | 0.156 | 0.107 | 0.118 | 0.397 | 0.387 |
| mock_jev_ft_100 | messidor2 | 0.309 | 0.158 | 0.163 | 0.171 | 0.337 | 0.327 |
| mock_jev_ft_100 | idrid | 0.262 | 0.100 | 0.142 | 0.130 | 0.317 | 0.308 |
| mock_jev_ft_100 | ddr | 0.244 | 0.152 | 0.129 | 0.124 | 0.283 | 0.262 |
| mock_jev_ft_100 | eyepacs | 0.222 | 0.093 | 0.084 | 0.082 | 0.265 | 0.256 |
| mock_jev_ft_300 | aptos | 0.253 | 0.212 | 0.080 | 0.106 | 0.240 | 0.233 |
| mock_jev_ft_300 | mbrset | 0.225 | 0.147 | 0.075 | 0.101 | 0.324 | 0.318 |
| mock_jev_ft_300 | messidor2 | 0.190 | 0.138 | 0.060 | 0.081 | 0.206 | 0.198 |
| mock_jev_ft_300 | idrid | 0.321 | 0.271 | 0.070 | 0.101 | 0.401 | 0.391 |
| mock_jev_ft_300 | ddr | 0.202 | 0.181 | 0.062 | 0.052 | 0.223 | 0.216 |
| mock_jev_ft_300 | eyepacs | 0.153 | 0.122 | 0.061 | 0.052 | 0.233 | 0.230 |
| mock_generative | aptos | 0.284 | 0.126 | 0.082 | 0.077 | 0.240 | 0.197 |
| mock_generative | mbrset | 0.365 | 0.148 | 0.130 | 0.113 | 0.344 | 0.296 |
| mock_generative | messidor2 | 0.302 | 0.101 | 0.085 | 0.069 | 0.278 | 0.226 |
| mock_generative | idrid | 0.320 | 0.118 | 0.081 | 0.078 | 0.294 | 0.231 |
| mock_generative | ddr | 0.296 | 0.109 | 0.081 | 0.073 | 0.218 | 0.167 |
| mock_generative | eyepacs | 0.262 | 0.055 | 0.057 | 0.056 | 0.245 | 0.201 |
| mock_specialist | aptos | 0.111 | 0.097 | 0.053 | 0.052 | 0.145 | 0.141 |
| mock_specialist | mbrset | 0.193 | 0.152 | 0.054 | 0.068 | 0.262 | 0.258 |
| mock_specialist | messidor2 | 0.167 | 0.137 | 0.052 | 0.062 | 0.208 | 0.200 |
| mock_specialist | idrid | 0.206 | 0.139 | 0.088 | 0.080 | 0.252 | 0.245 |
| mock_specialist | ddr | 0.171 | 0.137 | 0.040 | 0.039 | 0.179 | 0.175 |
| mock_specialist | eyepacs | 0.078 | 0.072 | 0.043 | 0.035 | 0.130 | 0.127 |
| mock_specialist_100 | aptos | 0.347 | 0.129 | 0.159 | 0.141 | 0.333 | 0.293 |
| mock_specialist_100 | mbrset | 0.432 | 0.129 | 0.216 | 0.194 | 0.456 | 0.434 |
| mock_specialist_100 | messidor2 | 0.402 | 0.171 | 0.173 | 0.149 | 0.387 | 0.348 |
| mock_specialist_100 | idrid | 0.366 | 0.144 | 0.158 | 0.137 | 0.412 | 0.391 |
| mock_specialist_100 | ddr | 0.381 | 0.163 | 0.185 | 0.170 | 0.337 | 0.319 |
| mock_specialist_100 | eyepacs | 0.333 | 0.088 | 0.133 | 0.111 | 0.349 | 0.311 |
| mock_specialist_300 | aptos | 0.228 | 0.106 | 0.090 | 0.104 | 0.231 | 0.212 |
| mock_specialist_300 | mbrset | 0.338 | 0.163 | 0.118 | 0.124 | 0.369 | 0.355 |
| mock_specialist_300 | messidor2 | 0.287 | 0.147 | 0.093 | 0.099 | 0.318 | 0.297 |
| mock_specialist_300 | idrid | 0.284 | 0.156 | 0.104 | 0.084 | 0.345 | 0.318 |
| mock_specialist_300 | ddr | 0.282 | 0.143 | 0.090 | 0.095 | 0.272 | 0.249 |
| mock_specialist_300 | eyepacs | 0.231 | 0.082 | 0.064 | 0.068 | 0.255 | 0.236 |

### Table 5. Latency as measured during prediction

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Model | Arm | Adapter | Repository | Revision | Decisions timed | Median ms per decision | 95th percentile ms |
|---|---|---|---|---|---|---|---|
| mock_jev_zs | Z | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_noabstain_zs | Z | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_jev_ft | B | mock | – | – | 19030 | 0.1 | 0.1 |
| mock_jev_ft_100 | B | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_jev_ft_300 | B | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_generative | G | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_specialist | S | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_specialist_100 | S | mock | – | – | 9515 | 0.1 | 0.1 |
| mock_specialist_300 | S | mock | – | – | 9515 | 0.1 | 0.1 |

Wall-clock time per question on the hardware used for the run; record that hardware alongside this table.

### Pre-specified comparisons

**SYNTHETIC DEMO DATA: mock models on drawn images. Not study results.**

| Test | Type | Metric | Dataset | Model | Reference | Model value | Reference value | Advantage (95% CI) | Margin | p | Holm p | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H2_qwk | noninferiority | qwk | ddr | mock_jev_ft | mock_specialist | 0.865 | 0.867 | -0.002 (-0.030 to 0.024) | 0.05 | 0.0033 | 0.0266 | not shown non-inferior (Holm) |
| H2_ref_sens | noninferiority | ref_sens_matched | ddr | mock_jev_ft | mock_specialist | 0.855 | 0.925 | -0.070 (-0.146 to 0.005) | 0.05 | 0.6578 | 1.0000 | not shown non-inferior (Holm) |
| H3_ece | superiority | ece_grade | ddr | mock_jev_ft | mock_generative | 0.106 | 0.109 | 0.003 (-0.037 to 0.054) | – | 0.3920 | 1.0000 | not shown superior (Holm) |
| H3_aurc | superiority | aurc_grade | ddr | mock_jev_ft | mock_generative | 0.164 | 0.167 | 0.003 (-0.040 to 0.047) | – | 0.4186 | 1.0000 | not shown superior (Holm) |
| H4_ece | noninferiority | ece_grade | ddr | mock_jev_ft | mock_specialist | 0.106 | 0.137 | 0.031 (-0.019 to 0.080) | 0.02 | 0.0266 | not primary | not shown non-inferior |
| H4_aurc | noninferiority | aurc_grade | ddr | mock_jev_ft | mock_specialist | 0.164 | 0.175 | 0.011 (-0.036 to 0.056) | 0.02 | 0.0997 | not primary | not shown non-inferior |
| H5_vision_lora | superiority | qwk | ddr | mock_jev_ft | mock_jev_zs | 0.865 | 0.455 | 0.409 (0.329 to 0.499) | – | 0.0033 | not primary | superior |
| H2_qwk | noninferiority | qwk | messidor2 | mock_jev_ft | mock_specialist | 0.783 | 0.835 | -0.052 (-0.100 to -0.008) | 0.05 | 0.5714 | 1.0000 | not shown non-inferior (Holm) |
| H2_ref_sens | noninferiority | ref_sens_matched | messidor2 | mock_jev_ft | mock_specialist | 0.734 | 0.871 | -0.137 (-0.256 to 0.000) | 0.05 | 0.8870 | 1.0000 | not shown non-inferior (Holm) |
| H3_ece | superiority | ece_grade | messidor2 | mock_jev_ft | mock_generative | 0.160 | 0.101 | -0.059 (-0.111 to 0.005) | – | 0.9568 | 1.0000 | not shown superior (Holm) |
| H3_aurc | superiority | aurc_grade | messidor2 | mock_jev_ft | mock_generative | 0.209 | 0.226 | 0.017 (-0.056 to 0.086) | – | 0.3821 | 1.0000 | not shown superior (Holm) |
| H4_ece | noninferiority | ece_grade | messidor2 | mock_jev_ft | mock_specialist | 0.160 | 0.137 | -0.022 (-0.084 to 0.036) | 0.02 | 0.4950 | not primary | not shown non-inferior |
| H4_aurc | noninferiority | aurc_grade | messidor2 | mock_jev_ft | mock_specialist | 0.209 | 0.200 | -0.009 (-0.064 to 0.042) | 0.02 | 0.3787 | not primary | not shown non-inferior |
| H5_vision_lora | superiority | qwk | messidor2 | mock_jev_ft | mock_jev_zs | 0.783 | 0.484 | 0.299 (0.200 to 0.380) | – | 0.0033 | not primary | superior |
| H2_st_sens | noninferiority | st_sens_matched | pooled_external | mock_jev_ft | mock_specialist | 0.832 | 0.848 | -0.016 (-0.088 to 0.051) | 0.05 | 0.1595 | not primary | not shown non-inferior |

Advantage is model minus reference, sign-flipped for metrics where lower is better, so positive favours the model. Tests are one-sided at 2.5%, from the paired patient-level bootstrap. Primary tests are decided on the Holm-adjusted p-value over the whole pre-specified primary family; a primary test that could not be run counts as failed. Intervals are unadjusted.
