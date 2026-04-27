# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

- Feature set: `core`
- Morgan fingerprint features: 0

## Grouped CV Metrics

| validation_scope | target | model | group_column | n_folds | n_rows | n_groups | mae_mean | mae_std | rmse_mean | rmse_std | r2_mean | r2_std | spearman_mean | spearman_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_kfold | rt_min | linear_ridge | inchikey | 3 | 17367 | 4447 | 3.503 | 0.034 | 5.284 | 0.055 | 0.741 | 0.004 | 0.831 | 0.001 |
| group_kfold | rt_min | random_forest | inchikey | 3 | 17367 | 4447 | 1.756 | 0.046 | 2.991 | 0.173 | 0.917 | 0.007 | 0.944 | 0.006 |
| group_kfold | rt_min | extra_trees | inchikey | 3 | 17367 | 4447 | 1.639 | 0.054 | 2.874 | 0.231 | 0.923 | 0.01 | 0.949 | 0.004 |
| group_kfold | rt_min | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 1.912 | 0.028 | 3.049 | 0.119 | 0.914 | 0.004 | 0.936 | 0.002 |
| group_kfold | quality_score | linear_ridge | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.003 | 0.001 | 0.759 | 0.177 | 0.045 | 0.005 |
| group_kfold | quality_score | random_forest | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.002 | 0.001 | 0.947 | 0.028 | 1.0 | 0.0 |
| group_kfold | quality_score | extra_trees | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.001 | 0.001 | 0.946 | 0.049 | 1.0 | 0.0 |
| group_kfold | quality_score | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.005 | 0.001 | 0.353 | 0.023 | 0.06 | 0.014 |

## Evaluation Matrix

| validation_scope | split_name | holdout_key | target | model | n_rows | n_train | n_holdout | n_groups | n_folds | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_grouped_holdout | test | test | rt_min | linear_ridge | 42533 |  | 42533.0 |  |  | 21.961 | 2.077 | 3.099 | 0.746 | 0.803 | 9.46 |  |  |
| final_grouped_holdout | test | test | rt_min | random_forest | 42533 |  | 42533.0 |  |  | 21.961 | 1.244 | 2.104 | 0.883 | 0.903 | 5.664 |  |  |
| final_grouped_holdout | test | test | rt_min | extra_trees | 42533 |  | 42533.0 |  |  | 21.961 | 1.187 | 1.994 | 0.895 | 0.909 | 5.405 |  |  |
| final_grouped_holdout | test | test | rt_min | hist_gradient_boosting | 42533 |  | 42533.0 |  |  | 21.961 | 1.575 | 2.322 | 0.857 | 0.863 | 7.17 |  |  |
| final_grouped_holdout | test | test | quality_score | linear_ridge | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.002 | 0.524 | 0.017 |  |  |  |
| final_grouped_holdout | test | test | quality_score | random_forest | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.001 | 0.904 | 1.0 |  |  |  |
| final_grouped_holdout | test | test | quality_score | extra_trees | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.001 | 0.868 | 1.0 |  |  |  |
| final_grouped_holdout | test | test | quality_score | hist_gradient_boosting | 42533 |  | 42533.0 |  |  | 21.961 | 0.0 | 0.002 | 0.286 | 0.033 |  |  |  |
| group_kfold | mean | GroupKFold | rt_min | linear_ridge | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 3.503 | 5.284 | 0.741 | 0.831 | 15.894 |  |  |
| group_kfold | mean | GroupKFold | rt_min | random_forest | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 1.756 | 2.991 | 0.917 | 0.944 | 7.969 |  |  |
| group_kfold | mean | GroupKFold | rt_min | extra_trees | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 1.639 | 2.874 | 0.923 | 0.949 | 7.439 |  |  |
| group_kfold | mean | GroupKFold | rt_min | hist_gradient_boosting | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 1.912 | 3.049 | 0.914 | 0.936 | 8.675 |  |  |
| group_kfold | mean | GroupKFold | quality_score | linear_ridge | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.003 | 0.759 | 0.045 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | random_forest | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.002 | 0.947 | 1.0 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | extra_trees | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.001 | 0.946 | 1.0 |  |  |  |
| group_kfold | mean | GroupKFold | quality_score | hist_gradient_boosting | 17367 |  |  | 4447.0 | 3.0 | 22.04 | 0.0 | 0.005 | 0.353 | 0.06 |  |  |  |
| source_family_holdout | holdout | MCMRT | rt_min | linear_ridge | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 4.047 | 5.671 | 0.683 | 0.764 | 12.573 | 0.115 | 3.05 |
| source_family_holdout | holdout | MCMRT | rt_min | random_forest | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.197 | 3.424 | 0.884 | 0.92 | 6.825 | 0.147 | 1.404 |
| source_family_holdout | holdout | MCMRT | rt_min | extra_trees | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.288 | 3.453 | 0.882 | 0.913 | 7.107 | -0.191 | 1.51 |
| source_family_holdout | holdout | MCMRT | rt_min | hist_gradient_boosting | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 2.223 | 3.306 | 0.892 | 0.917 | 6.904 | -0.088 | 1.52 |
| source_family_holdout | holdout | MCMRT | quality_score | linear_ridge | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.081 | 0.082 |  |  |  | 0.081 | 0.081 |
| source_family_holdout | holdout | MCMRT | quality_score | random_forest | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | MCMRT | quality_score | extra_trees | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | MCMRT | quality_score | hist_gradient_boosting | 10073 | 7294.0 | 10073.0 | 343.0 |  | 32.192 | 0.041 | 0.055 |  |  |  | 0.041 | 0.02 |
| source_family_holdout | holdout | RepoRT | rt_min | linear_ridge | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 7.576 | 10.156 | 0.199 | 0.325 | 31.185 | 1.347 | 5.745 |
| source_family_holdout | holdout | RepoRT | rt_min | random_forest | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.305 | 6.628 | 0.659 | 0.649 | 17.722 | -1.307 | 2.858 |
| source_family_holdout | holdout | RepoRT | rt_min | extra_trees | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.217 | 6.503 | 0.672 | 0.679 | 17.358 | -1.818 | 2.466 |
| source_family_holdout | holdout | RepoRT | rt_min | hist_gradient_boosting | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 4.477 | 6.44 | 0.678 | 0.631 | 18.428 | 0.11 | 3.261 |
| source_family_holdout | holdout | RepoRT | quality_score | linear_ridge | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.336 | 0.373 | -2211.69 | -0.049 |  | 0.335 | 0.41 |
| source_family_holdout | holdout | RepoRT | quality_score | random_forest | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.057 | 0.063 | -62.511 | 0.058 |  | 0.057 | 0.069 |
| source_family_holdout | holdout | RepoRT | quality_score | extra_trees | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.086 | 0.096 | -145.45 | 0.058 |  | 0.086 | 0.107 |
| source_family_holdout | holdout | RepoRT | quality_score | hist_gradient_boosting | 4491 | 12876.0 | 4491.0 | 2304.0 |  | 24.294 | 0.012 | 0.022 | -6.52 | 0.058 |  | 0.008 | 0.0 |
| source_family_holdout | holdout | ReTiNA | rt_min | linear_ridge | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 7.321 | 9.279 | -0.317 | 0.416 | 34.507 | -2.065 | 5.927 |
| source_family_holdout | holdout | ReTiNA | rt_min | random_forest | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.434 | 4.487 | 0.692 | 0.706 | 16.186 | 2.406 | 2.68 |
| source_family_holdout | holdout | ReTiNA | rt_min | extra_trees | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.081 | 3.788 | 0.781 | 0.748 | 14.521 | 0.979 | 2.868 |
| source_family_holdout | holdout | ReTiNA | rt_min | hist_gradient_boosting | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 3.447 | 4.482 | 0.693 | 0.706 | 16.247 | 2.008 | 2.909 |
| source_family_holdout | holdout | ReTiNA | quality_score | linear_ridge | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.005 | 0.006 |  |  |  | -0.001 | 0.003 |
| source_family_holdout | holdout | ReTiNA | quality_score | random_forest | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | ReTiNA | quality_score | extra_trees | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | holdout | ReTiNA | quality_score | hist_gradient_boosting | 2439 | 14928.0 | 2439.0 | 2145.0 |  | 21.216 | 0.011 | 0.028 |  |  |  | 0.011 | 0.0 |

## Final Grouped Holdout RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | validation_spearman | test_mae | test_rmse | test_r2 | test_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 2.142 | 3.239 | 0.742 | 0.802 | 2.077 | 3.099 | 0.746 | 0.803 |
| random_forest | 1.24 | 2.114 | 0.89 | 0.903 | 1.244 | 2.104 | 0.883 | 0.903 |
| extra_trees | 1.185 | 2.019 | 0.9 | 0.91 | 1.187 | 1.994 | 0.895 | 0.909 |
| hist_gradient_boosting | 1.604 | 2.391 | 0.86 | 0.863 | 1.575 | 2.322 | 0.857 | 0.863 |

## Final Grouped Holdout Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | validation_spearman | test_mae | test_rmse | test_r2 | test_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.0 |  |  | 0.0 | 0.002 | 0.524 | 0.017 |
| random_forest | 0.0 | 0.0 |  |  | 0.0 | 0.001 | 0.904 | 1.0 |
| extra_trees | 0.0 | 0.0 |  |  | 0.0 | 0.001 | 0.868 | 1.0 |
| hist_gradient_boosting | 0.0 | 0.0 |  |  | 0.0 | 0.002 | 0.286 | 0.033 |

Candidate models: linear_ridge, random_forest, extra_trees, hist_gradient_boosting

## Retention-Order Diagnostic

| source_dataset | column_name | mobile_phase_system | n_rows | n_pairs | pairwise_order_accuracy | spearman_rt |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | ALL | 42533 | 195428 | 0.883 | 0.909 |
| MCMRT:CM 01 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1888 | 0.867 | 0.896 |
| MCMRT:CM 02 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1889 | 0.873 | 0.898 |
| MCMRT:CM 03 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.874 | 0.905 |
| MCMRT:CM 04 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1888 | 0.878 | 0.909 |
| MCMRT:CM 05 | ACQUITY BEH C18 | meoh_formic_acid | 62 | 1890 | 0.863 | 0.897 |
| MCMRT:CM 06 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1889 | 0.883 | 0.916 |
| MCMRT:CM 07 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.885 | 0.925 |
| MCMRT:CM 08 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1891 | 0.885 | 0.922 |
| MCMRT:CM 09 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1891 | 0.893 | 0.93 |
| MCMRT:CM 10 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1888 | 0.88 | 0.914 |
| MCMRT:CM 11 | ACQUITY BEH C18 | meoh_formic_acid | 62 | 1890 | 0.884 | 0.923 |
| MCMRT:CM 12 | Acclaim RSLC 120 C18 | meoh_formic_acid | 62 | 1890 | 0.885 | 0.912 |
| MCMRT:CM 13 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1887 | 0.875 | 0.893 |
| MCMRT:CM 14 | ACQUITY UPLC HSS T3 | meoh_formic_acid | 62 | 1888 | 0.881 | 0.904 |
| MCMRT:CM 15 | Acclaim 120 C18 | meoh_formic_acid | 62 | 1890 | 0.874 | 0.896 |
| MCMRT:CM 16 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 62 | 1888 | 0.885 | 0.922 |
| MCMRT:CM 17 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1883 | 0.871 | 0.899 |
| MCMRT:CM 18 | Thermo Hypersil GOLD | meoh_formic_acid | 62 | 1890 | 0.876 | 0.908 |
| MCMRT:CM 19 | Acclaim RSLC 120 C18 | acn_formic_acid | 62 | 1890 | 0.863 | 0.873 |
| MCMRT:CM 20 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 61 | 1828 | 0.861 | 0.877 |
| MCMRT:CM 21 | Thermo Hypersil GOLD | acn_formic_acid | 61 | 1828 | 0.865 | 0.875 |
| MCMRT:CM 22 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 61 | 1829 | 0.866 | 0.881 |
| MCMRT:CM 23 | ACQUITY UPLC HSS T3 | acn_formic_acid | 61 | 1828 | 0.869 | 0.881 |
| MCMRT:CM 24 | Acclaim 120 C18 | acn_formic_acid | 61 | 1829 | 0.869 | 0.887 |
| MCMRT:CM 25 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 63 | 1949 | 0.893 | 0.93 |
| MCMRT:CM 26 | ACQUITY UPLC HSS T3 | meoh_ammonium | 63 | 1949 | 0.89 | 0.933 |
| MCMRT:CM 27 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 63 | 1953 | 0.881 | 0.924 |
| MCMRT:CM 28 | ACQUITY UPLC HSS T3 | meoh_ammonium | 63 | 1949 | 0.898 | 0.937 |
| MCMRT:CM 29 | Acclaim 120 C18 | meoh_ammonium | 63 | 1950 | 0.892 | 0.93 |
| MCMRT:CM 30 | Acclaim RSLC 120 C18 | meoh_ammonium | 63 | 1949 | 0.877 | 0.916 |
| METLIN_SMRT_Figshare | Agilent Zorbax Extend-C18 2.1 x 50 mm, 1.8 um | acn_formic_acid | 16011 | 5000 | 0.93 | 0.841 |
| ReTiNA:dynastl | RP column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 32 | 483 | 0.967 | 0.987 |
| ReTiNA:enaminert | RP column 4.6 x 30 mm, 2.7 um | acn_formic_acid | 3915 | 5000 | 0.955 | 0.766 |
| ReTiNA:massbank | RP column 2.1 x 50 mm, 1.7 um | acn_formic_acid | 262 | 5000 | 0.891 | 0.915 |
| ReTiNA:massbank | RP column 2.1 x 50 mm, 1.7 um | acn_unbuffered | 48 | 1128 | 0.921 | 0.962 |
| ReTiNA:massbank | RP column 2.1 x 80 mm, 1.8 um | meoh_unbuffered | 88 | 3824 | 0.885 | 0.919 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.7 um | meoh_formic_acid | 122 | 5000 | 0.904 | 0.947 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.9 um | acn_formic_acid | 60 | 1768 | 0.856 | 0.865 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 1.9 um | meoh_formic_acid | 244 | 5000 | 0.923 | 0.944 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | acn_formic_acid | 61 | 1829 | 0.863 | 0.873 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | meoh_formic_acid | 366 | 5000 | 0.923 | 0.944 |
| ReTiNA:mcmrt | RP column 2.1 x 100 mm, 2.2 um | meoh_unbuffered | 62 | 1887 | 0.876 | 0.916 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | acn_formic_acid | 120 | 5000 | 0.881 | 0.912 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | meoh_formic_acid | 244 | 5000 | 0.941 | 0.958 |
| ReTiNA:mcmrt | RP column 2.1 x 105 mm, 1.8 um | meoh_unbuffered | 124 | 5000 | 0.885 | 0.918 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 60 | 1768 | 0.87 | 0.881 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | meoh_formic_acid | 61 | 1827 | 0.879 | 0.902 |
| ReTiNA:mcmrt | RP column 2.1 x 50 mm, 1.8 um | meoh_unbuffered | 124 | 5000 | 0.892 | 0.931 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | acn_formic_acid | 60 | 1769 | 0.868 | 0.886 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | meoh_formic_acid | 61 | 1829 | 0.872 | 0.894 |
| ReTiNA:mcmrt | RP column 4.6 x 150 mm, 5 um | meoh_unbuffered | 62 | 1888 | 0.89 | 0.927 |
| ReTiNA:metlin | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 16010 | 5000 | 0.904 | 0.841 |
| ReTiNA:nz | HI column 2.1 x 100 mm, 5 um | acn_formic_acid | 27 | 351 | 0.826 | 0.846 |
| ReTiNA:report | HI column 2.1 x 100 mm, 3.5 um | acn_formic_acid | 63 | 1945 | 0.847 | 0.821 |
| ReTiNA:report | HI column 2.1 x 150 mm, 1.7 um | acn_unbuffered | 86 | 3643 | 0.777 | 0.687 |
| ReTiNA:report | HI column 2.1 x 150 mm, 5 um | acn_unbuffered | 102 | 5000 | 0.917 | 0.946 |
| ReTiNA:report | RP column 0.5 x 100 mm, 2.7 um | acn_formic_acid | 11 | 53 | 0.887 | 0.862 |
| ReTiNA:report | RP column 0.5 x 50 mm, 2.7 um | acn_formic_acid | 14 | 89 | 0.921 | 0.951 |
| ReTiNA:report | RP column 2 x 150 mm, 1.7 um | acn_formic_acid | 30 | 431 | 0.8 | 0.789 |
| ReTiNA:report | RP column 2 x 150 mm, 4 um | acn_formic_acid | 14 | 89 | 0.933 | 0.965 |
| ReTiNA:report | RP column 2 x 250 mm, 4 um | acn_formic_acid | 25 | 295 | 0.939 | 0.966 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.6 um | acn_formic_acid | 26 | 322 | 0.876 | 0.891 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.7 um | acn_formic_acid | 46 | 1032 | 0.862 | 0.876 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.8 um | acn_formic_acid | 25 | 297 | 0.933 | 0.954 |
| ReTiNA:report | RP column 2.1 x 100 mm, 1.8 um | meoh_formic_acid | 118 | 5000 | 0.924 | 0.962 |
| ReTiNA:report | RP column 2.1 x 100 mm, 2.6 um | acn_formic_acid | 18 | 153 | 0.83 | 0.826 |
| ReTiNA:report | RP column 2.1 x 100 mm, 3 um | acn_unbuffered | 15 | 104 | 0.894 | 0.879 |
| ReTiNA:report | RP column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 152 | 5000 | 0.915 | 0.955 |
| ReTiNA:report | RP column 2.1 x 150 mm, 1.8 um | meoh_formic_acid | 13 | 78 | 0.692 | 0.582 |
| ReTiNA:report | RP column 2.1 x 150 mm, 2.6 um | acn_formic_acid | 40 | 772 | 0.745 | 0.539 |
| ReTiNA:report | RP column 2.1 x 150 mm, 2.7 um | acn_formic_acid | 17 | 136 | 0.963 | 0.988 |
| ReTiNA:report | RP column 2.1 x 200 mm, 1.9 um | acn_formic_acid | 19 | 167 | 0.928 | 0.96 |
| ReTiNA:report | RP column 2.1 x 5 mm, 1.9 um | acn_formic_acid | 9 | 35 | 0.943 | 0.95 |
| ReTiNA:report | RP column 2.1 x 50 mm, 1.8 um | acn_formic_acid | 21 | 210 | 0.781 | 0.735 |
| ReTiNA:report | RP column 2.1 x 50 mm, 3.5 um | meoh_formic_acid | 83 | 3376 | 0.851 | 0.852 |
| ReTiNA:report | RP column 3 x 100 mm, 2.7 um | acn_formic_acid | 29 | 403 | 0.873 | 0.86 |
| ReTiNA:report | RP column 4 x 250 mm, 5 um | acn_formic_acid | 13 | 77 | 0.857 | 0.857 |
| ReTiNA:report | RP column 4.6 x 100 mm, 5 um | meoh_unbuffered | 10 | 44 | 0.818 | 0.768 |
| ReTiNA:report | RP column 4.6 x 150 mm, 3 um | acn_formic_acid | 14 | 89 | 0.921 | 0.938 |
| ReTiNA:report | RP column 4.6 x 250 mm, 5 um | acn_unbuffered | 16 | 118 | 0.856 | 0.867 |
| ReTiNA:retip | HI column 2.1 x 150 mm, 1.7 um | acn_formic_acid | 270 | 5000 | 0.817 | 0.697 |
| ReTiNA:retip | RP column 2.1 x 100 mm, 1.7 um | acn_formic_acid | 169 | 5000 | 0.896 | 0.906 |
| RepoRT:0001 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 13 | 78 | 0.718 | 0.621 |
| RepoRT:0002 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 87 | 3740 | 0.908 | 0.943 |
| RepoRT:0003 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 18 | 153 | 0.876 | 0.919 |
| RepoRT:0004 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 27 | 325 | 0.846 | 0.842 |
| RepoRT:0005 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 13 | 78 | 0.859 | 0.919 |
| RepoRT:0006 | Hichrom Alltima HP C18 | acn_formic_acid | 5 | 10 | 0.9 | 0.975 |
| RepoRT:0007 | Merck SeQuant ZIC-pHILIC | acn_unbuffered | 24 | 274 | 0.872 | 0.884 |
| RepoRT:0008 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 6 | 15 | 0.933 | 0.943 |
| RepoRT:0009 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 68 | 2259 | 0.885 | 0.916 |
| RepoRT:0010 | Merck Supelco Ascentis Express C18 | acn_formic_acid | 10 | 45 | 0.956 | 0.976 |
| RepoRT:0013 |  | acn_formic_acid | 3 | 3 | 0.333 | -0.5 |
| RepoRT:0014 |  | acn_formic_acid | 7 | 21 | 0.476 | -0.071 |
| RepoRT:0015 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 17 | 136 | 0.728 | 0.595 |
| RepoRT:0016 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 3 | 3 | 0.333 | 0.0 |
| RepoRT:0017 | Phenomenex Kinetex C18 | meoh_formic_acid | 34 | 557 | 0.786 | 0.734 |
| RepoRT:0018 | Waters Atlantis T3 | acn_formic_acid | 34 | 561 | 0.881 | 0.939 |
| RepoRT:0019 | Waters XBridge C18 | meoh_formic_acid | 74 | 2685 | 0.842 | 0.841 |
| RepoRT:0020 | Merck SeQuant ZIC-pHILIC | other_unbuffered | 28 | 378 | 0.765 | 0.704 |
| RepoRT:0021 | Waters Symmetry C18 | acn_formic_acid | 10 | 45 | 0.844 | 0.806 |
| RepoRT:0022 | Agilent ZORBAX RRHD Eclipse Plus C18 | acn_formic_acid | 4 | 6 | 1.0 | 1.0 |
| RepoRT:0023 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 12 | 66 | 0.924 | 0.951 |
| RepoRT:0024 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 104 | 5000 | 0.81 | 0.787 |
| RepoRT:0025 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 6 | 15 | 0.467 | 0.029 |
| RepoRT:0026 | Thermo Scientific Hypersil GOLD PFP | acn_formic_acid | 3 | 3 | 0.667 | 0.5 |
| RepoRT:0027 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 53 | 1377 | 0.824 | 0.789 |
| RepoRT:0028 | Phenomenex Synergi Hydro-RP | acn_formic_acid | 13 | 78 | 0.885 | 0.927 |
| RepoRT:0029 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 12 | 65 | 0.923 | 0.935 |
| RepoRT:0030 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 12 | 66 | 0.803 | 0.804 |
| RepoRT:0031 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 11 | 55 | 0.873 | 0.882 |
| RepoRT:0032 | Phenomenex Luna C18 | acn_formic_acid | 12 | 66 | 0.909 | 0.944 |
| RepoRT:0033 |  | acn_formic_acid | 12 | 66 | 0.864 | 0.902 |
| RepoRT:0034 |  | acn_formic_acid | 9 | 36 | 0.583 | 0.167 |
| RepoRT:0036 | Merck Supelco SUPELCOSIL LC-C18 | acn_unbuffered | 10 | 45 | 0.867 | 0.903 |
| RepoRT:0037 | Phenomenex Kinetex PFP | acn_unbuffered | 6 | 14 | 0.714 | 0.522 |
| RepoRT:0038 | Waters Atlantis T3 | acn_unbuffered | 12 | 66 | 0.848 | 0.797 |
| RepoRT:0039 | Merck LiChrospher RP-18 | acn_formic_acid | 10 | 45 | 0.867 | 0.855 |
| RepoRT:0040 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 14 | 91 | 0.835 | 0.811 |
| RepoRT:0041 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 17 | 136 | 0.743 | 0.647 |
| RepoRT:0042 | Phenomenex Kinetex EVO C18 | acn_formic_acid | 11 | 55 | 0.782 | 0.761 |
| RepoRT:0043 | Waters ACQUITY UPLC HSS T3 | acn_unbuffered | 13 | 78 | 0.872 | 0.83 |
| RepoRT:0044 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 104 | 5000 | 0.881 | 0.924 |
| RepoRT:0045 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 35 | 593 | 0.799 | 0.743 |

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. When enabled, Morgan fingerprints are included as sparse binary compound features. Model selection uses GroupKFold by compound identity; source-family holdouts and retention-order metrics are diagnostic transfer checks.
