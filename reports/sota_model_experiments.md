# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

- Feature set: `core`
- Morgan fingerprint features: 0

## Grouped CV Metrics

| validation_scope | target | model | group_column | n_folds | n_rows | n_groups | mae_mean | mae_std | rmse_mean | rmse_std | r2_mean | r2_std | spearman_mean | spearman_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_kfold | rt_min | linear_ridge | inchikey | 3 | 17367 | 4447 | 3.602 | 0.087 | 5.456 | 0.097 | 0.724 | 0.007 | 0.818 | 0.01 |
| group_kfold | rt_min | random_forest | inchikey | 3 | 17367 | 4447 | 1.94 | 0.065 | 3.302 | 0.225 | 0.899 | 0.01 | 0.933 | 0.005 |
| group_kfold | rt_min | extra_trees | inchikey | 3 | 17367 | 4447 | 1.85 | 0.045 | 3.14 | 0.207 | 0.908 | 0.009 | 0.94 | 0.003 |
| group_kfold | rt_min | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 2.156 | 0.022 | 3.4 | 0.12 | 0.893 | 0.004 | 0.923 | 0.003 |
| group_kfold | quality_score | linear_ridge | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.003 | 0.001 | 0.759 | 0.177 | 0.045 | 0.005 |
| group_kfold | quality_score | random_forest | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.001 | 0.001 | 0.955 | 0.028 | 1.0 | 0.0 |
| group_kfold | quality_score | extra_trees | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.001 | 0.001 | 0.966 | 0.029 | 1.0 | 0.0 |
| group_kfold | quality_score | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.005 | 0.001 | 0.437 | 0.111 | 0.063 | 0.012 |

## Evaluation Matrix

| validation_scope | split_name | holdout_key | target | model | n_rows | n_train | n_holdout | n_groups | n_folds | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_grouped_holdout | test | test | rt_min | linear_ridge | 42533 |  | 42533.0 |  |  | 21.961 | 2.253 | 3.296 | 0.712 | 0.758 | 10.261 |  |  |
| final_grouped_holdout | test | test | rt_min | random_forest | 42533 |  | 42533.0 |  |  | 21.961 | 1.464 | 2.375 | 0.851 | 0.861 | 6.666 |  |  |
| final_grouped_holdout | test | test | rt_min | extra_trees | 42533 |  | 42533.0 |  |  | 21.961 | 1.429 | 2.313 | 0.858 | 0.867 | 6.507 |  |  |
| final_grouped_holdout | test | test | rt_min | hist_gradient_boosting | 42533 |  | 42533.0 |  |  | 21.961 | 1.785 | 2.607 | 0.82 | 0.817 | 8.126 |  |  |
| final_grouped_holdout | test | test | quality_score | linear_ridge | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.002 | 0.524 | 0.017 |  |  |  |
| final_grouped_holdout | test | test | quality_score | random_forest | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.001 | 0.904 | 1.0 |  |  |  |
| final_grouped_holdout | test | test | quality_score | extra_trees | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.001 | 0.836 | 1.0 |  |  |  |
| final_grouped_holdout | test | test | quality_score | hist_gradient_boosting | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.002 | 0.391 | 0.04 |  |  |  |
| group_kfold | mean | GroupKFold | rt_min | linear_ridge | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 3.602 | 5.456 | 0.724 | 0.818 | 16.342 |  |  |
| group_kfold | mean | GroupKFold | rt_min | random_forest | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 1.94 | 3.302 | 0.899 | 0.933 | 8.803 |  |  |
| group_kfold | mean | GroupKFold | rt_min | extra_trees | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 1.85 | 3.14 | 0.908 | 0.94 | 8.396 |  |  |
| group_kfold | mean | GroupKFold | rt_min | hist_gradient_boosting | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 2.156 | 3.4 | 0.893 | 0.923 | 9.782 |  |  |
| group_kfold | mean | GroupKFold | quality_score | linear_ridge | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.003 | 0.759 | 0.045 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | random_forest | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.001 | 0.955 | 1.0 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | extra_trees | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.001 | 0.966 | 1.0 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | hist_gradient_boosting | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.005 | 0.437 | 0.063 |  |  |  |
| source_family_holdout | holdout | MCMRT | rt_min | linear_ridge | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 4.207 | 5.889 | 0.658 | 0.741 | 13.067 | 0.274 | 3.195 |
| source_family_holdout | holdout | MCMRT | rt_min | random_forest | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.255 | 3.534 | 0.877 | 0.913 | 7.006 | 0.207 | 1.424 |
| source_family_holdout | holdout | MCMRT | rt_min | extra_trees | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.422 | 3.742 | 0.862 | 0.901 | 7.523 | 0.29 | 1.599 |
| source_family_holdout | holdout | MCMRT | rt_min | hist_gradient_boosting | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.375 | 3.537 | 0.877 | 0.907 | 7.379 | 0.106 | 1.621 |
| source_family_holdout | holdout | MCMRT | quality_score | linear_ridge | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.082 | 0.082 |  |  |  | 0.082 | 0.081 |
| source_family_holdout | holdout | MCMRT | quality_score | random_forest | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.002 | 0.002 |  |  |  | 0.002 | 0.003 |
| source_family_holdout | holdout | MCMRT | quality_score | extra_trees | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | MCMRT | quality_score | hist_gradient_boosting | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.038 | 0.057 |  |  |  | 0.038 | 0.012 |
| source_family_holdout | holdout | RepoRT | rt_min | linear_ridge | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 7.895 | 10.621 | 0.124 | 0.354 | 32.499 | 3.901 | 5.917 |
| source_family_holdout | holdout | RepoRT | rt_min | random_forest | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.364 | 6.606 | 0.661 | 0.628 | 17.962 | -1.341 | 2.949 |
| source_family_holdout | holdout | RepoRT | rt_min | extra_trees | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.239 | 6.543 | 0.668 | 0.662 | 17.447 | -1.934 | 2.517 |
| source_family_holdout | holdout | RepoRT | rt_min | hist_gradient_boosting | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.651 | 6.564 | 0.665 | 0.639 | 19.144 | 0.605 | 3.292 |
| source_family_holdout | holdout | RepoRT | quality_score | linear_ridge | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.336 | 0.373 | -2210.296 | -0.049 |  | 0.335 | 0.41 |
| source_family_holdout | holdout | RepoRT | quality_score | random_forest | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.059 | 0.066 | -68.858 | 0.058 |  | 0.059 | 0.066 |
| source_family_holdout | holdout | RepoRT | quality_score | extra_trees | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.072 | 0.081 | -103.86 | 0.058 |  | 0.072 | 0.078 |
| source_family_holdout | holdout | RepoRT | quality_score | hist_gradient_boosting | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.011 | 0.021 | -5.747 | 0.058 |  | 0.008 | 0.0 |
| source_family_holdout | holdout | ReTiNA | rt_min | linear_ridge | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 7.414 | 9.451 | -0.366 | 0.438 | 34.945 | -2.884 | 5.761 |
| source_family_holdout | holdout | ReTiNA | rt_min | random_forest | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.63 | 4.691 | 0.664 | 0.676 | 17.11 | 2.542 | 3.015 |
| source_family_holdout | holdout | ReTiNA | rt_min | extra_trees | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.075 | 3.757 | 0.784 | 0.777 | 14.495 | 0.879 | 2.814 |
| source_family_holdout | holdout | ReTiNA | rt_min | hist_gradient_boosting | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.448 | 4.387 | 0.706 | 0.744 | 16.25 | 2.06 | 3.125 |
| source_family_holdout | holdout | ReTiNA | quality_score | linear_ridge | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.005 | 0.006 |  |  |  | -0.001 | 0.003 |
| source_family_holdout | holdout | ReTiNA | quality_score | random_forest | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | ReTiNA | quality_score | extra_trees | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | ReTiNA | quality_score | hist_gradient_boosting | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.012 | 0.031 |  |  |  | 0.012 | 0.0 |

## Final Grouped Holdout RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | validation_spearman | test_mae | test_rmse | test_r2 | test_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 2.318 | 3.434 | 0.711 | 0.761 | 2.253 | 3.296 | 0.712 | 0.758 |
| random_forest | 1.451 | 2.338 | 0.866 | 0.869 | 1.464 | 2.375 | 0.851 | 0.861 |
| extra_trees | 1.429 | 2.326 | 0.867 | 0.871 | 1.429 | 2.313 | 0.858 | 0.867 |
| hist_gradient_boosting | 1.799 | 2.649 | 0.828 | 0.817 | 1.785 | 2.607 | 0.82 | 0.817 |

## Final Grouped Holdout Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | validation_spearman | test_mae | test_rmse | test_r2 | test_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.0 |  |  | 0.0 | 0.002 | 0.524 | 0.017 |
| random_forest | 0.0 | 0.0 |  |  | 0.0 | 0.001 | 0.904 | 1.0 |
| extra_trees | 0.0 | 0.0 |  |  | 0.0 | 0.001 | 0.836 | 1.0 |
| hist_gradient_boosting | 0.0 | 0.0 |  |  | 0.0 | 0.002 | 0.391 | 0.04 |

Candidate models: linear_ridge, random_forest, extra_trees, hist_gradient_boosting

## Retention-Order Diagnostic

| source_dataset | column_name | mobile_phase_system | n_rows | n_pairs | pairwise_order_accuracy | spearman_rt |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | ALL | 42533 | 195428 | 0.861 | 0.867 |
| MCMRT:CM 01 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1888 | 0.832 | 0.821 |
| MCMRT:CM 02 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1889 | 0.84 | 0.84 |
| MCMRT:CM 03 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.854 | 0.858 |
| MCMRT:CM 04 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1888 | 0.861 | 0.864 |
| MCMRT:CM 05 | ACQUITY BEH C18 | meoh_formic_acid | 62 | 1890 | 0.854 | 0.862 |
| MCMRT:CM 06 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1889 | 0.842 | 0.844 |
| MCMRT:CM 07 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.844 | 0.856 |
| MCMRT:CM 08 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1891 | 0.844 | 0.859 |
| MCMRT:CM 09 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1891 | 0.852 | 0.868 |
| MCMRT:CM 10 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1888 | 0.838 | 0.845 |
| MCMRT:CM 11 | ACQUITY BEH C18 | meoh_formic_acid | 62 | 1890 | 0.848 | 0.861 |
| MCMRT:CM 12 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.852 | 0.862 |
| MCMRT:CM 13 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1887 | 0.845 | 0.845 |
| MCMRT:CM 14 | ACQUITY UPLC HSS T3 | meoh_formic_acid | 62 | 1888 | 0.855 | 0.866 |
| MCMRT:CM 15 | Acclaim 120 C18 | meoh_formic_acid | 62 | 1890 | 0.853 | 0.852 |
| MCMRT:CM 16 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1888 | 0.847 | 0.862 |
| MCMRT:CM 17 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1883 | 0.85 | 0.851 |
| MCMRT:CM 18 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1890 | 0.862 | 0.865 |
| MCMRT:CM 19 | Acclaim RSLC 120 C18 | acn_formic_acid | 62 | 1890 | 0.828 | 0.82 |
| MCMRT:CM 20 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 61 | 1828 | 0.827 | 0.818 |
| MCMRT:CM 21 | Thermo Hypersil GOLD | acn_formic_acid | 61 | 1828 | 0.832 | 0.817 |
| MCMRT:CM 22 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 61 | 1829 | 0.838 | 0.836 |
| MCMRT:CM 23 | ACQUITY UPLC HSS T3 | acn_formic_acid | 61 | 1828 | 0.845 | 0.848 |
| MCMRT:CM 24 | Acclaim 120 C18 | acn_formic_acid | 61 | 1829 | 0.841 | 0.838 |
| MCMRT:CM 25 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 63 | 1949 | 0.874 | 0.906 |
| MCMRT:CM 26 | ACQUITY UPLC HSS T3 | meoh_ammonium | 63 | 1949 | 0.864 | 0.897 |
| MCMRT:CM 27 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 63 | 1953 | 0.864 | 0.894 |
| MCMRT:CM 28 | ACQUITY UPLC HSS T3 | meoh_ammonium | 63 | 1949 | 0.867 | 0.9 |
| MCMRT:CM 29 | Acclaim 120 C18 | meoh_ammonium | 63 | 1950 | 0.862 | 0.891 |
| MCMRT:CM 30 | Acclaim RSLC 120 C18 | meoh_ammonium | 63 | 1949 | 0.873 | 0.905 |
| METLIN_SMRT_Figshare | Agilent Zorbax Extend-C18 2.1 x 50 mm, 1.8 um | acn_formic_acid | 16011 | 5000 | 0.909 | 0.761 |
| ReTiNA:dynastl | RP column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 32 | 483 | 0.996 | 0.999 |
| ReTiNA:enaminert | RP column 4.6 x 30 mm, 2.7 um | acn_formic_acid | 3915 | 5000 | 0.942 | 0.666 |
| ReTiNA:massbank | RP column 2.1 x 50 mm, 1.7 um | acn_formic_acid | 262 | 5000 | 0.89 | 0.916 |
| ReTiNA:massbank | RP column 2.1 x 50 mm, 1.7 um | acn_unbuffered | 48 | 1128 | 0.914 | 0.954 |
| ReTiNA:massbank | RP column 2.1 x 80 mm, 1.8 um | meoh_unbuffered | 88 | 3824 | 0.869 | 0.904 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.7 um | meoh_formic_acid | 122 | 5000 | 0.895 | 0.923 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.9 um | acn_formic_acid | 60 | 1768 | 0.831 | 0.818 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.9 um | meoh_formic_acid | 244 | 5000 | 0.893 | 0.911 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | acn_formic_acid | 61 | 1829 | 0.827 | 0.818 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | meoh_formic_acid | 366 | 5000 | 0.907 | 0.918 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | meoh_unbuffered | 62 | 1887 | 0.869 | 0.902 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | acn_formic_acid | 120 | 5000 | 0.866 | 0.879 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | meoh_formic_acid | 244 | 5000 | 0.914 | 0.951 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | meoh_unbuffered | 124 | 5000 | 0.873 | 0.911 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 60 | 1768 | 0.843 | 0.846 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | meoh_formic_acid | 61 | 1827 | 0.853 | 0.865 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | meoh_unbuffered | 124 | 5000 | 0.871 | 0.911 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | acn_formic_acid | 60 | 1769 | 0.84 | 0.836 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | meoh_formic_acid | 61 | 1829 | 0.851 | 0.85 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | meoh_unbuffered | 62 | 1888 | 0.863 | 0.892 |
| ReTiNA:metlin | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 16010 | 5000 | 0.881 | 0.761 |
| ReTiNA:nz | HI column 2.1 x 100 mm, 5 um | acn_formic_acid | 27 | 351 | 0.769 | 0.731 |
| ReTiNA:report | HI column 2.1 x 100 mm, 3.5 um | acn_formic_acid | 63 | 1945 | 0.819 | 0.795 |
| ReTiNA:report | HI column 2.1 x 150 mm, 1.7 um | acn_unbuffered | 86 | 3643 | 0.769 | 0.686 |
| ReTiNA:report | HI column 2.1 x 150 mm, 5 um | acn_unbuffered | 102 | 5000 | 0.899 | 0.928 |
| ReTiNA:report | RP column 0.5 x 100 mm, 2.7 um | acn_formic_acid | 11 | 53 | 0.849 | 0.835 |
| ReTiNA:report | RP column 0.5 x 50 mm, 2.7 um | acn_formic_acid | 14 | 89 | 0.91 | 0.938 |
| ReTiNA:report | RP column 2 x 150 mm, 1.7 um | acn_formic_acid | 30 | 431 | 0.798 | 0.777 |
| ReTiNA:report | RP column 2 x 150 mm, 4 um | acn_formic_acid | 14 | 89 | 0.921 | 0.96 |
| ReTiNA:report | RP column 2 x 250 mm, 4 um | acn_formic_acid | 25 | 295 | 0.912 | 0.947 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.6 um | acn_formic_acid | 26 | 322 | 0.907 | 0.921 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.7 um | acn_formic_acid | 46 | 1032 | 0.859 | 0.849 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.8 um | acn_formic_acid | 25 | 297 | 0.912 | 0.94 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.8 um | meoh_formic_acid | 118 | 5000 | 0.899 | 0.943 |
| ReTiNA:report | RP column 2.1 x 100 mm, 2.6 um | acn_formic_acid | 18 | 153 | 0.889 | 0.915 |
| ReTiNA:report | RP column 2.1 x 100 mm, 3 um | acn_unbuffered | 15 | 104 | 0.875 | 0.855 |
| ReTiNA:report | RP column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 152 | 5000 | 0.899 | 0.934 |
| ReTiNA:report | RP column 2.1 x 150 mm, 1.8 um | meoh_formic_acid | 13 | 78 | 0.705 | 0.588 |
| ReTiNA:report | RP column 2.1 x 150 mm, 2.6 um | acn_formic_acid | 40 | 772 | 0.71 | 0.518 |
| ReTiNA:report | RP column 2.1 x 150 mm, 2.7 um | acn_formic_acid | 17 | 136 | 0.971 | 0.99 |
| ReTiNA:report | RP column 2.1 x 200 mm, 1.9 um | acn_formic_acid | 19 | 167 | 0.97 | 0.986 |
| ReTiNA:report | RP column 2.1 x 5 mm, 1.9 um | acn_formic_acid | 9 | 35 | 0.971 | 0.983 |
| ReTiNA:report | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 21 | 210 | 0.719 | 0.583 |
| ReTiNA:report | RP column 2.1 x 50 mm, 3.5 um | meoh_formic_acid | 83 | 3376 | 0.833 | 0.832 |
| ReTiNA:report | RP column 3 x 100 mm, 2.7 um | acn_formic_acid | 29 | 403 | 0.859 | 0.846 |
| ReTiNA:report | RP column 4 x 250 mm, 5 um | acn_formic_acid | 13 | 77 | 0.753 | 0.592 |
| ReTiNA:report | RP column 4.6 x 100 mm, 5 um | meoh_unbuffered | 10 | 44 | 0.795 | 0.72 |
| ReTiNA:report | RP column 4.6 x 150 mm, 3 um | acn_formic_acid | 14 | 89 | 0.921 | 0.938 |
| ReTiNA:report | RP column 4.6 x 250 mm, 5 um | acn_unbuffered | 16 | 118 | 0.771 | 0.787 |
| ReTiNA:retip | HI column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 270 | 5000 | 0.776 | 0.634 |
| ReTiNA:retip | RP column 2.1 x 100 mm, 1.7 um | acn_formic_acid | 169 | 5000 | 0.87 | 0.881 |
| RepoRT:0001 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 13 | 78 | 0.718 | 0.621 |
| RepoRT:0002 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 87 | 3740 | 0.894 | 0.925 |
| RepoRT:0003 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 18 | 153 | 0.85 | 0.902 |
| RepoRT:0004 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 27 | 325 | 0.778 | 0.754 |
| RepoRT:0005 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 13 | 78 | 0.859 | 0.919 |
| RepoRT:0006 | Hichrom Alltima HP C18 | acn_formic_acid | 5 | 10 | 0.9 | 0.975 |
| RepoRT:0007 | Merck SeQuant ZIC-pHILIC | acn_unbuffered | 24 | 274 | 0.839 | 0.819 |
| RepoRT:0008 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 6 | 15 | 1.0 | 1.0 |
| RepoRT:0009 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 68 | 2259 | 0.873 | 0.903 |
| RepoRT:0010 | Merck Supelco Ascentis Express C18 | acn_formic_acid | 10 | 45 | 0.956 | 0.976 |
| RepoRT:0013 |  | acn_formic_acid | 3 | 3 | 0.333 | -0.5 |
| RepoRT:0014 |  | acn_formic_acid | 7 | 21 | 0.381 | -0.357 |
| RepoRT:0015 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 17 | 136 | 0.699 | 0.553 |
| RepoRT:0016 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 3 | 3 | 0.0 |  |
| RepoRT:0017 | Phenomenex Kinetex C18 | meoh_formic_acid | 34 | 557 | 0.761 | 0.674 |
| RepoRT:0018 | Waters Atlantis T3 | acn_formic_acid | 34 | 561 | 0.859 | 0.918 |
| RepoRT:0019 | Waters XBridge C18 | meoh_formic_acid | 74 | 2685 | 0.829 | 0.83 |
| RepoRT:0020 | Merck SeQuant ZIC-pHILIC | other_unbuffered | 28 | 378 | 0.693 | 0.581 |
| RepoRT:0021 | Waters Symmetry C18 | acn_formic_acid | 10 | 45 | 0.8 | 0.77 |
| RepoRT:0022 | Agilent ZORBAX RRHD Eclipse Plus C18 | acn_formic_acid | 4 | 6 | 0.833 | 0.8 |
| RepoRT:0023 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 12 | 66 | 0.939 | 0.958 |
| RepoRT:0024 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 104 | 5000 | 0.826 | 0.825 |
| RepoRT:0025 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 6 | 15 | 0.267 | -0.493 |
| RepoRT:0026 | Thermo Scientific Hypersil GOLD PFP | acn_formic_acid | 3 | 3 | 1.0 | 1.0 |
| RepoRT:0027 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 53 | 1377 | 0.837 | 0.859 |
| RepoRT:0028 | Phenomenex Synergi Hydro-RP | acn_formic_acid | 13 | 78 | 0.897 | 0.949 |
| RepoRT:0029 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 12 | 65 | 0.831 | 0.767 |
| RepoRT:0030 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 12 | 66 | 0.924 | 0.965 |
| RepoRT:0031 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 11 | 55 | 0.891 | 0.909 |
| RepoRT:0032 | Phenomenex Luna C18 | acn_formic_acid | 12 | 66 | 0.909 | 0.93 |
| RepoRT:0033 |  | acn_formic_acid | 12 | 66 | 0.909 | 0.944 |
| RepoRT:0034 |  | acn_formic_acid | 9 | 36 | 0.722 | 0.55 |
| RepoRT:0036 | Merck Supelco SUPELCOSIL LC-C18 | acn_unbuffered | 10 | 45 | 0.778 | 0.815 |
| RepoRT:0037 | Phenomenex Kinetex PFP | acn_unbuffered | 6 | 14 | 0.571 | 0.232 |
| RepoRT:0038 | Waters Atlantis T3 | acn_unbuffered | 12 | 66 | 0.788 | 0.753 |
| RepoRT:0039 | Merck LiChrospher RP-18 | acn_formic_acid | 10 | 45 | 0.8 | 0.697 |
| RepoRT:0040 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 14 | 91 | 0.846 | 0.789 |
| RepoRT:0041 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 17 | 136 | 0.757 | 0.688 |
| RepoRT:0042 | Phenomenex Kinetex EVO C18 | acn_formic_acid | 11 | 55 | 0.8 | 0.779 |
| RepoRT:0043 | Waters ACQUITY UPLC HSS T3 | acn_unbuffered | 13 | 78 | 0.846 | 0.786 |
| RepoRT:0044 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 104 | 5000 | 0.822 | 0.835 |
| RepoRT:0045 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 35 | 593 | 0.764 | 0.696 |

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. When enabled, Morgan fingerprints are included as sparse binary compound features. Model selection uses GroupKFold by compound identity; source-family holdouts and retention-order metrics are diagnostic transfer checks.
