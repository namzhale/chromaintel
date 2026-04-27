# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: 213941
- Compounds: 202834
- Source distribution: {'METLIN_SMRT_Figshare': 79957, 'ReTiNA:metlin': 79938, 'ReTiNA:enaminert': 19487, 'ReTiNA:mcmrt': 9923, 'ReTiNA:report': 5024, 'ReTiNA:retip': 2179, 'ReTiNA:massbank': 2084, 'RepoRT:0044': 592, 'RepoRT:0024': 533, 'RepoRT:0002': 413, 'RepoRT:0009': 364, 'RepoRT:0019': 364, 'MCMRT:CM 30': 343, 'MCMRT:CM 29': 343, 'MCMRT:CM 28': 343, 'MCMRT:CM 27': 343, 'MCMRT:CM 26': 343, 'MCMRT:CM 25': 343, 'MCMRT:CM 14': 335, 'MCMRT:CM 19': 335, 'MCMRT:CM 01': 335, 'MCMRT:CM 17': 335, 'MCMRT:CM 16': 335, 'MCMRT:CM 15': 335, 'MCMRT:CM 18': 335, 'MCMRT:CM 13': 335, 'MCMRT:CM 08': 335, 'MCMRT:CM 02': 335, 'MCMRT:CM 03': 335, 'MCMRT:CM 04': 335, 'MCMRT:CM 05': 335, 'MCMRT:CM 06': 335, 'MCMRT:CM 12': 335, 'MCMRT:CM 07': 335, 'MCMRT:CM 09': 335, 'MCMRT:CM 10': 335, 'MCMRT:CM 11': 335, 'MCMRT:CM 24': 330, 'MCMRT:CM 23': 330, 'MCMRT:CM 22': 330, 'MCMRT:CM 21': 330, 'MCMRT:CM 20': 330, 'RepoRT:0027': 302, 'RepoRT:0017': 197, 'ReTiNA:dynastl': 188, 'RepoRT:0004': 174, 'RepoRT:0045': 147, 'RepoRT:0007': 147, 'RepoRT:0018': 140, 'RepoRT:0020': 116, 'ReTiNA:nz': 109, 'RepoRT:0015': 102, 'RepoRT:0003': 82, 'RepoRT:0040': 79, 'RepoRT:0025': 77, 'RepoRT:0041': 75, 'RepoRT:0001': 73, 'RepoRT:0010': 73, 'RepoRT:0005': 66, 'RepoRT:0038': 57, 'RepoRT:0042': 54, 'RepoRT:0039': 53, 'RepoRT:0036': 51, 'RepoRT:0032': 49, 'RepoRT:0033': 48, 'RepoRT:0029': 47, 'RepoRT:0028': 47, 'RepoRT:0030': 46, 'RepoRT:0023': 45, 'RepoRT:0031': 43, 'RepoRT:0043': 43, 'RepoRT:0021': 41, 'RepoRT:0034': 35, 'RepoRT:0008': 33, 'RepoRT:0037': 29, 'RepoRT:0014': 27, 'RepoRT:0016': 26, 'RepoRT:0013': 26, 'RepoRT:0006': 25, 'RepoRT:0026': 17, 'RepoRT:0022': 9, 'RepoRT': 5, 'internal_lab': 5, 'METLIN_SMRT': 2}

## Feature Set

Feature set: `core`.

Feature group counts: {'compound': 55, 'fingerprints': 0, 'lc_numeric': 9, 'lc_categorical': 6, 'ms': 3, 'combined': 73}

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints can be enabled as an explicit training feature set and are reported separately to prevent silent descriptor-set changes.

## Validation Design

- Model selection: GroupKFold by `inchikey`.
- Final holdout: group-aware train/validation/test split with no compound identity overlap between splits.
- Source-family holdout: train without each large source family and test on that held-out family.
- Method holdout: train without whole LC method condition families and test on the held-out method.
- Column-family holdout: train without each column chemistry family and test on that held-out family.

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

## Models Tested

- linear_ridge
- random_forest
- extra_trees
- hist_gradient_boosting

## Best Models

- RT model: `extra_trees`
- Peak quality surrogate: `extra_trees`

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

## Source-wise Performance

| source_dataset | n_test | rt_mae | rt_rmse | mean_bias | median_abs_error | ad_flagged |
| --- | --- | --- | --- | --- | --- | --- |
| RepoRT:0039 | 10 | 8.649 | 11.418 | -2.423 | 5.661 | 0 |
| MCMRT:CM 16 | 62 | 5.383 | 7.874 | -0.058 | 3.722 | 0 |
| RepoRT:0037 | 6 | 5.075 | 5.573 | -1.981 | 4.644 | 0 |
| RepoRT:0022 | 4 | 4.365 | 4.665 | 4.365 | 4.343 | 0 |
| RepoRT:0036 | 10 | 4.317 | 5.179 | -0.016 | 3.885 | 0 |
| RepoRT:0001 | 13 | 4.026 | 5.872 | -3.858 | 3.43 | 0 |
| RepoRT:0006 | 5 | 3.568 | 4.969 | 0.141 | 2.786 | 0 |
| RepoRT:0017 | 34 | 3.085 | 4.228 | -1.017 | 2.044 | 0 |
| RepoRT:0028 | 13 | 3.074 | 3.796 | -0.231 | 3.053 | 0 |
| MCMRT:CM 22 | 61 | 2.907 | 4.092 | 0.561 | 2.199 | 0 |
| RepoRT:0002 | 87 | 2.872 | 4.382 | -0.295 | 1.701 | 0 |
| MCMRT:CM 15 | 62 | 2.87 | 4.203 | 0.615 | 1.668 | 0 |
| MCMRT:CM 24 | 61 | 2.864 | 4.086 | 0.487 | 2.223 | 0 |
| MCMRT:CM 13 | 62 | 2.863 | 4.146 | 0.52 | 1.785 | 0 |
| RepoRT:0032 | 12 | 2.796 | 3.6 | 0.011 | 1.928 | 0 |
| MCMRT:CM 12 | 62 | 2.78 | 3.846 | 0.302 | 1.833 | 0 |
| RepoRT:0021 | 10 | 2.761 | 3.601 | 2.327 | 2.055 | 0 |
| MCMRT:CM 14 | 62 | 2.753 | 3.87 | 0.677 | 1.674 | 0 |
| MCMRT:CM 23 | 61 | 2.534 | 3.675 | 0.764 | 1.577 | 0 |
| RepoRT:0020 | 28 | 2.172 | 2.988 | -0.396 | 1.485 | 0 |
| MCMRT:CM 10 | 62 | 2.101 | 2.704 | -0.689 | 1.659 | 0 |
| RepoRT:0040 | 14 | 2.004 | 2.826 | 0.114 | 1.26 | 0 |
| ReTiNA:nz | 27 | 1.929 | 2.649 | -0.57 | 1.565 | 0 |
| MCMRT:CM 11 | 62 | 1.918 | 2.51 | -0.51 | 1.545 | 0 |
| MCMRT:CM 08 | 62 | 1.896 | 2.485 | -0.333 | 1.467 | 0 |
| RepoRT:0014 | 7 | 1.829 | 2.047 | -1.786 | 2.138 | 0 |
| RepoRT:0005 | 13 | 1.813 | 2.347 | -1.533 | 0.957 | 0 |
| RepoRT:0029 | 12 | 1.787 | 2.163 | -1.533 | 1.847 | 0 |
| ReTiNA:mcmrt | 1831 | 1.735 | 2.837 | 0.019 | 1.082 | 0 |
| MCMRT:CM 09 | 62 | 1.733 | 2.255 | -0.131 | 1.311 | 0 |
| RepoRT:0018 | 34 | 1.69 | 2.655 | -0.988 | 0.806 | 0 |
| RepoRT:0007 | 24 | 1.673 | 2.53 | -0.513 | 1.075 | 0 |
| RepoRT:0015 | 17 | 1.643 | 2.288 | 0.047 | 1.469 | 0 |
| MCMRT:CM 27 | 63 | 1.563 | 2.026 | -0.997 | 1.229 | 0 |
| RepoRT:0019 | 74 | 1.535 | 2.291 | 0.73 | 0.988 | 0 |
| MCMRT:CM 29 | 63 | 1.46 | 1.925 | -0.924 | 1.174 | 0 |
| MCMRT:CM 07 | 62 | 1.445 | 1.966 | 0.143 | 1.069 | 0 |
| RepoRT:0016 | 3 | 1.438 | 1.444 | 0.536 | 1.353 | 0 |
| RepoRT:0044 | 104 | 1.424 | 2.193 | 0.546 | 0.608 | 0 |
| ReTiNA:report | 1029 | 1.413 | 2.741 | -0.065 | 0.57 | 0 |
| RepoRT:0045 | 35 | 1.38 | 2.11 | -0.361 | 0.8 | 0 |
| RepoRT:0023 | 12 | 1.369 | 1.78 | 0.826 | 0.719 | 0 |
| internal_lab | 2 | 1.362 | 1.381 | 1.362 | 1.362 | 0 |
| RepoRT:0025 | 6 | 1.249 | 1.463 | 0.366 | 1.023 | 0 |
| METLIN_SMRT_Figshare | 16011 | 1.247 | 1.954 | -0.019 | 0.747 | 0 |
| ReTiNA:metlin | 16010 | 1.247 | 1.954 | -0.019 | 0.747 | 0 |
| RepoRT:0024 | 104 | 1.246 | 2.149 | 0.25 | 0.499 | 0 |
| RepoRT:0031 | 11 | 1.245 | 1.479 | -0.53 | 1.171 | 0 |
| MCMRT:CM 20 | 61 | 1.223 | 1.675 | 0.315 | 0.926 | 0 |
| RepoRT:0010 | 10 | 1.21 | 1.444 | -0.049 | 1.263 | 0 |
| MCMRT:CM 06 | 62 | 1.21 | 1.681 | -0.05 | 0.803 | 0 |
| MCMRT:CM 28 | 63 | 1.202 | 1.587 | -0.235 | 0.888 | 0 |
| RepoRT:0026 | 3 | 1.148 | 1.276 | -0.364 | 1.177 | 0 |
| RepoRT:0027 | 53 | 1.147 | 1.878 | 0.249 | 0.679 | 0 |
| METLIN_SMRT | 1 | 1.118 | 1.118 | 1.118 | 1.118 | 0 |
| RepoRT:0004 | 27 | 1.084 | 1.457 | 0.449 | 0.729 | 0 |
| RepoRT:0038 | 12 | 1.035 | 1.538 | 0.822 | 0.637 | 0 |
| MCMRT:CM 03 | 62 | 1.027 | 1.437 | 0.046 | 0.752 | 0 |
| MCMRT:CM 19 | 62 | 1.005 | 1.574 | 0.304 | 0.526 | 0 |
| MCMRT:CM 05 | 62 | 0.969 | 1.37 | 0.085 | 0.694 | 0 |
| MCMRT:CM 25 | 63 | 0.969 | 1.322 | -0.434 | 0.69 | 0 |
| RepoRT | 1 | 0.959 | 0.959 | 0.959 | 0.959 | 0 |
| MCMRT:CM 21 | 61 | 0.947 | 1.462 | 0.357 | 0.593 | 0 |
| MCMRT:CM 30 | 63 | 0.946 | 1.245 | -0.135 | 0.808 | 0 |
| MCMRT:CM 18 | 62 | 0.934 | 1.323 | 0.057 | 0.684 | 0 |
| RepoRT:0043 | 13 | 0.932 | 1.509 | -0.04 | 0.375 | 0 |
| MCMRT:CM 04 | 62 | 0.924 | 1.312 | 0.153 | 0.658 | 0 |
| MCMRT:CM 26 | 63 | 0.913 | 1.216 | -0.242 | 0.663 | 0 |
| RepoRT:0034 | 9 | 0.846 | 1.144 | 0.777 | 0.454 | 0 |
| MCMRT:CM 02 | 62 | 0.83 | 1.159 | -0.0 | 0.486 | 0 |
| RepoRT:0033 | 12 | 0.812 | 0.98 | 0.509 | 0.648 | 0 |
| RepoRT:0003 | 18 | 0.756 | 0.884 | 0.619 | 0.719 | 0 |
| MCMRT:CM 17 | 62 | 0.72 | 0.982 | 0.073 | 0.465 | 0 |
| RepoRT:0042 | 11 | 0.717 | 1.103 | 0.648 | 0.257 | 0 |
| ReTiNA:retip | 439 | 0.635 | 1.355 | 0.039 | 0.174 | 0 |
| MCMRT:CM 01 | 62 | 0.601 | 0.823 | 0.041 | 0.47 | 0 |
| RepoRT:0013 | 3 | 0.562 | 0.864 | 0.551 | 0.185 | 0 |
| ReTiNA:massbank | 398 | 0.542 | 0.914 | 0.08 | 0.288 | 0 |
| RepoRT:0041 | 17 | 0.465 | 0.625 | 0.229 | 0.524 | 0 |
| RepoRT:0030 | 12 | 0.343 | 0.452 | 0.165 | 0.227 | 0 |
| RepoRT:0009 | 68 | 0.225 | 0.452 | 0.189 | 0.096 | 0 |
| RepoRT:0008 | 6 | 0.18 | 0.249 | -0.049 | 0.168 | 0 |
| ReTiNA:enaminert | 3915 | 0.137 | 0.179 | -0.004 | 0.111 | 0 |
| ReTiNA:dynastl | 32 | 0.027 | 0.058 | 0.021 | 0.0 | 0 |

## Source-Family Holdout Metrics

| validation_scope | holdout_family | holdout_key | target | model | n_train | n_holdout | n_train_sources | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_family_holdout | MCMRT | MCMRT | rt_min | linear_ridge | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 4.047 | 5.671 | 0.683 | 0.764 | 12.573 | 0.115 | 3.05 |
| source_family_holdout | MCMRT | MCMRT | rt_min | random_forest | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.197 | 3.424 | 0.884 | 0.92 | 6.825 | 0.147 | 1.404 |
| source_family_holdout | MCMRT | MCMRT | rt_min | extra_trees | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.288 | 3.453 | 0.882 | 0.913 | 7.107 | -0.191 | 1.51 |
| source_family_holdout | MCMRT | MCMRT | rt_min | hist_gradient_boosting | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.223 | 3.306 | 0.892 | 0.917 | 6.904 | -0.088 | 1.52 |
| source_family_holdout | MCMRT | MCMRT | quality_score | linear_ridge | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.081 | 0.082 |  |  |  | 0.081 | 0.081 |
| source_family_holdout | MCMRT | MCMRT | quality_score | random_forest | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | MCMRT | MCMRT | quality_score | extra_trees | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | MCMRT | MCMRT | quality_score | hist_gradient_boosting | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.041 | 0.055 |  |  |  | 0.041 | 0.02 |
| source_family_holdout | RepoRT | RepoRT | rt_min | linear_ridge | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 7.576 | 10.156 | 0.199 | 0.325 | 31.185 | 1.347 | 5.745 |
| source_family_holdout | RepoRT | RepoRT | rt_min | random_forest | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.305 | 6.628 | 0.659 | 0.649 | 17.722 | -1.307 | 2.858 |
| source_family_holdout | RepoRT | RepoRT | rt_min | extra_trees | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.217 | 6.503 | 0.672 | 0.679 | 17.358 | -1.818 | 2.466 |
| source_family_holdout | RepoRT | RepoRT | rt_min | hist_gradient_boosting | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.477 | 6.44 | 0.678 | 0.631 | 18.428 | 0.11 | 3.261 |
| source_family_holdout | RepoRT | RepoRT | quality_score | linear_ridge | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.336 | 0.373 | -2211.69 | -0.049 |  | 0.335 | 0.41 |
| source_family_holdout | RepoRT | RepoRT | quality_score | random_forest | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.057 | 0.063 | -62.511 | 0.058 |  | 0.057 | 0.069 |
| source_family_holdout | RepoRT | RepoRT | quality_score | extra_trees | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.086 | 0.096 | -145.45 | 0.058 |  | 0.086 | 0.107 |
| source_family_holdout | RepoRT | RepoRT | quality_score | hist_gradient_boosting | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.012 | 0.022 | -6.52 | 0.058 |  | 0.008 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | linear_ridge | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 7.321 | 9.279 | -0.317 | 0.416 | 34.507 | -2.065 | 5.927 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | random_forest | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.434 | 4.487 | 0.692 | 0.706 | 16.186 | 2.406 | 2.68 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | extra_trees | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.081 | 3.788 | 0.781 | 0.748 | 14.521 | 0.979 | 2.868 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | hist_gradient_boosting | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.447 | 4.482 | 0.693 | 0.706 | 16.247 | 2.008 | 2.909 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | linear_ridge | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.005 | 0.006 |  |  |  | -0.001 | 0.003 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | random_forest | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | extra_trees | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | hist_gradient_boosting | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.011 | 0.028 |  |  |  | 0.011 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | linear_ridge | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.539 | 3.197 | 0.255 | 0.561 | 11.038 | -0.609 | 2.082 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | random_forest | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.319 | 3.045 | 0.324 | 0.611 | 10.081 | 1.005 | 1.846 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | extra_trees | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.579 | 3.219 | 0.245 | 0.61 | 11.214 | -1.425 | 2.105 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | hist_gradient_boosting | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.228 | 2.935 | 0.372 | 0.621 | 9.688 | -0.236 | 1.659 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | linear_ridge | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.015 | 0.015 |  |  |  | 0.015 | 0.015 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | random_forest | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | extra_trees | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | hist_gradient_boosting | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |

## Method Holdout Metrics

| validation_scope | holdout_method | holdout_key | target | model | n_train | n_holdout | n_train_methods | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | linear_ridge | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 3.049 | 3.918 | 0.746 | 0.877 | 10.697 | -1.166 | 2.493 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | random_forest | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.73 | 2.584 | 0.89 | 0.966 | 6.071 | -1.149 | 1.012 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | extra_trees | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.515 | 1.932 | 0.938 | 0.974 | 5.317 | -0.757 | 1.172 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | hist_gradient_boosting | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.475 | 1.921 | 0.939 | 0.972 | 5.174 | -0.744 | 1.132 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | linear_ridge | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.014 | 0.014 |  |  |  | -0.014 | 0.014 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | random_forest | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | extra_trees | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | hist_gradient_boosting | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.001 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 6.65 | 9.958 | 0.71 | 0.886 | 13.926 | -2.087 | 3.362 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.688 | 5.447 | 0.913 | 0.968 | 5.629 | -0.091 | 1.017 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.761 | 4.695 | 0.936 | 0.964 | 5.783 | -0.96 | 1.211 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.48 | 4.537 | 0.94 | 0.98 | 5.193 | -0.2 | 1.398 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 2.221 | 2.823 | 0.689 | 0.913 | 10.332 | -0.282 | 1.864 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.72 | 0.924 | 0.967 | 0.983 | 3.348 | 0.463 | 0.552 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.641 | 0.807 | 0.975 | 0.99 | 2.98 | 0.506 | 0.505 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.9 | 1.209 | 0.943 | 0.972 | 4.188 | 0.238 | 0.671 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.009 | 0.013 |  |  |  | 0.009 | 0.009 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.001 |  |  |  | 0.0 | 0.0 |

## Column-Family Holdout Metrics

| validation_scope | holdout_column_family | holdout_key | target | model | n_train | n_holdout | n_train_column_families | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| column_family_holdout | C18 | C18 | rt_min | linear_ridge | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 5.046 | 7.016 | 0.592 | 0.711 | 16.341 | -1.081 | 3.615 |
| column_family_holdout | C18 | C18 | rt_min | random_forest | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 2.92 | 4.722 | 0.815 | 0.86 | 9.456 | -0.798 | 1.713 |
| column_family_holdout | C18 | C18 | rt_min | extra_trees | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 2.879 | 4.616 | 0.823 | 0.873 | 9.322 | -0.78 | 1.846 |
| column_family_holdout | C18 | C18 | rt_min | hist_gradient_boosting | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 2.894 | 4.775 | 0.811 | 0.877 | 9.373 | -0.179 | 1.804 |
| column_family_holdout | C18 | C18 | quality_score | linear_ridge | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.046 | 0.05 |  |  |  | 0.046 | 0.039 |
| column_family_holdout | C18 | C18 | quality_score | random_forest | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| column_family_holdout | C18 | C18 | quality_score | extra_trees | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| column_family_holdout | C18 | C18 | quality_score | hist_gradient_boosting | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.004 | 0.009 |  |  |  | 0.002 | 0.0 |
| column_family_holdout | unknown | unknown | rt_min | linear_ridge | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 5.081 | 7.462 | -0.165 | 0.692 | 24.257 | -1.899 | 3.107 |
| column_family_holdout | unknown | unknown | rt_min | random_forest | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.424 | 3.348 | 0.766 | 0.807 | 11.573 | 1.35 | 1.658 |
| column_family_holdout | unknown | unknown | rt_min | extra_trees | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.448 | 3.287 | 0.774 | 0.812 | 11.685 | 1.256 | 1.691 |
| column_family_holdout | unknown | unknown | rt_min | hist_gradient_boosting | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.721 | 3.79 | 0.7 | 0.75 | 12.989 | 1.667 | 1.794 |
| column_family_holdout | unknown | unknown | quality_score | linear_ridge | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.009 | 0.012 |  |  |  | 0.006 | 0.008 |
| column_family_holdout | unknown | unknown | quality_score | random_forest | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| column_family_holdout | unknown | unknown | quality_score | extra_trees | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| column_family_holdout | unknown | unknown | quality_score | hist_gradient_boosting | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.013 | 0.039 |  |  |  | 0.013 | 0.0 |

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

## Parameter Significance

`reports/feature_importance.csv` contains permutation importance for the selected RT model with feature groups, z-like stability scores, and significance labels: `positive`, `weak_positive`, `neutral_or_unstable`, and `negative`. These labels are diagnostic only on the current small held-out split.

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently 1.994 min.
- Split-conformal q90 absolute RT residual: 2.882 min.

## Current Limitations

- The checked-in dataset is a small mock/demo set, not yet a validated internal laboratory history.
- Public RT datasets often lack peak quality, matrix, sample preparation, and MS transition metadata.
- Quality score is provisional. It uses observed quality_score when present; otherwise it is a transparent proxy from S/N, resolution, asymmetry, and tailing.
- Source-family holdout is now reported, but it is still public-to-public transfer rather than internal lab validation.

## Next Steps

1. Import internal historical BE assay development runs using the internal template.
2. Calibrate RT and quality models on accepted lab methods by instrument platform and matrix.
3. Add explicit uncertainty calibration and applicability-domain checks.
4. Expand candidate search spaces to match available columns, solvents, and validated operating ranges.
