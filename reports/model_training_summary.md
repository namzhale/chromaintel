# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: 213941
- Compounds: 202834
- Source distribution: {'METLIN_SMRT_Figshare': 79957, 'ReTiNA:metlin': 79938, 'ReTiNA:enaminert': 19487, 'ReTiNA:mcmrt': 9923, 'ReTiNA:report': 5024, 'ReTiNA:retip': 2179, 'ReTiNA:massbank': 2084, 'RepoRT:0044': 592, 'RepoRT:0024': 533, 'RepoRT:0002': 413, 'RepoRT:0009': 364, 'RepoRT:0019': 364, 'MCMRT:CM 30': 343, 'MCMRT:CM 29': 343, 'MCMRT:CM 28': 343, 'MCMRT:CM 27': 343, 'MCMRT:CM 26': 343, 'MCMRT:CM 25': 343, 'MCMRT:CM 14': 335, 'MCMRT:CM 19': 335, 'MCMRT:CM 01': 335, 'MCMRT:CM 17': 335, 'MCMRT:CM 16': 335, 'MCMRT:CM 15': 335, 'MCMRT:CM 18': 335, 'MCMRT:CM 13': 335, 'MCMRT:CM 08': 335, 'MCMRT:CM 02': 335, 'MCMRT:CM 03': 335, 'MCMRT:CM 04': 335, 'MCMRT:CM 05': 335, 'MCMRT:CM 06': 335, 'MCMRT:CM 12': 335, 'MCMRT:CM 07': 335, 'MCMRT:CM 09': 335, 'MCMRT:CM 10': 335, 'MCMRT:CM 11': 335, 'MCMRT:CM 24': 330, 'MCMRT:CM 23': 330, 'MCMRT:CM 22': 330, 'MCMRT:CM 21': 330, 'MCMRT:CM 20': 330, 'RepoRT:0027': 302, 'RepoRT:0017': 197, 'ReTiNA:dynastl': 188, 'RepoRT:0004': 174, 'RepoRT:0045': 147, 'RepoRT:0007': 147, 'RepoRT:0018': 140, 'RepoRT:0020': 116, 'ReTiNA:nz': 109, 'RepoRT:0015': 102, 'RepoRT:0003': 82, 'RepoRT:0040': 79, 'RepoRT:0025': 77, 'RepoRT:0041': 75, 'RepoRT:0001': 73, 'RepoRT:0010': 73, 'RepoRT:0005': 66, 'RepoRT:0038': 57, 'RepoRT:0042': 54, 'RepoRT:0039': 53, 'RepoRT:0036': 51, 'RepoRT:0032': 49, 'RepoRT:0033': 48, 'RepoRT:0029': 47, 'RepoRT:0028': 47, 'RepoRT:0030': 46, 'RepoRT:0023': 45, 'RepoRT:0031': 43, 'RepoRT:0043': 43, 'RepoRT:0021': 41, 'RepoRT:0034': 35, 'RepoRT:0008': 33, 'RepoRT:0037': 29, 'RepoRT:0014': 27, 'RepoRT:0016': 26, 'RepoRT:0013': 26, 'RepoRT:0006': 25, 'RepoRT:0026': 17, 'RepoRT:0022': 9, 'RepoRT': 5, 'internal_lab': 5, 'METLIN_SMRT': 2}

## Feature Set

Feature set: `core`.

Feature group counts: {'compound': 10, 'fingerprints': 0, 'lc_numeric': 9, 'lc_categorical': 6, 'ms': 3, 'combined': 28}

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
| group_kfold | rt_min | linear_ridge | inchikey | 3 | 17367 | 4447 | 3.602 | 0.087 | 5.456 | 0.097 | 0.724 | 0.007 | 0.818 | 0.01 |
| group_kfold | rt_min | random_forest | inchikey | 3 | 17367 | 4447 | 1.94 | 0.065 | 3.302 | 0.225 | 0.899 | 0.01 | 0.933 | 0.005 |
| group_kfold | rt_min | extra_trees | inchikey | 3 | 17367 | 4447 | 1.85 | 0.045 | 3.14 | 0.207 | 0.908 | 0.009 | 0.94 | 0.003 |
| group_kfold | rt_min | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 2.156 | 0.022 | 3.4 | 0.12 | 0.893 | 0.004 | 0.923 | 0.003 |
| group_kfold | quality_score | linear_ridge | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.003 | 0.001 | 0.759 | 0.177 | 0.045 | 0.005 |
| group_kfold | quality_score | random_forest | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.001 | 0.001 | 0.955 | 0.028 | 1.0 | 0.0 |
| group_kfold | quality_score | extra_trees | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.001 | 0.001 | 0.966 | 0.029 | 1.0 | 0.0 |
| group_kfold | quality_score | hist_gradient_boosting | inchikey | 3 | 17367 | 4447 | 0.0 | 0.0 | 0.005 | 0.001 | 0.437 | 0.111 | 0.063 | 0.012 |

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

## Source-wise Performance

| source_dataset | n_test | rt_mae | rt_rmse | mean_bias | median_abs_error | ad_flagged |
| --- | --- | --- | --- | --- | --- | --- |
| RepoRT:0039 | 10 | 10.99 | 14.025 | -0.56 | 7.144 | 0 |
| RepoRT:0022 | 4 | 7.549 | 8.032 | 7.549 | 7.904 | 0 |
| MCMRT:CM 16 | 62 | 6.584 | 9.465 | 0.382 | 4.823 | 0 |
| RepoRT:0037 | 6 | 5.456 | 5.974 | -0.157 | 5.587 | 0 |
| RepoRT:0036 | 10 | 4.803 | 6.034 | -0.879 | 3.927 | 0 |
| RepoRT:0001 | 13 | 4.62 | 6.643 | -4.469 | 2.722 | 0 |
| MCMRT:CM 15 | 62 | 3.66 | 5.146 | 0.801 | 2.654 | 0 |
| RepoRT:0002 | 87 | 3.632 | 5.416 | -0.4 | 2.366 | 0 |
| RepoRT:0032 | 12 | 3.606 | 4.461 | 0.468 | 3.122 | 0 |
| MCMRT:CM 13 | 62 | 3.527 | 5.008 | 0.76 | 2.759 | 0 |
| RepoRT:0017 | 34 | 3.355 | 4.546 | -0.445 | 2.201 | 0 |
| MCMRT:CM 14 | 62 | 3.337 | 4.691 | 0.819 | 2.614 | 0 |
| MCMRT:CM 12 | 62 | 3.306 | 4.592 | 0.628 | 2.722 | 0 |
| MCMRT:CM 22 | 61 | 3.251 | 4.682 | 0.896 | 2.188 | 0 |
| MCMRT:CM 24 | 61 | 3.189 | 4.63 | 0.838 | 2.382 | 0 |
| RepoRT:0028 | 13 | 3.184 | 3.857 | -0.514 | 2.655 | 0 |
| MCMRT:CM 23 | 61 | 2.865 | 4.07 | 0.85 | 2.149 | 0 |
| RepoRT:0006 | 5 | 2.727 | 3.828 | 0.107 | 1.793 | 0 |
| RepoRT:0021 | 10 | 2.63 | 3.492 | 1.698 | 2.425 | 0 |
| RepoRT:0020 | 28 | 2.447 | 3.071 | -0.238 | 1.867 | 0 |
| ReTiNA:nz | 27 | 2.328 | 2.866 | -0.268 | 1.846 | 0 |
| MCMRT:CM 10 | 62 | 2.311 | 3.158 | 0.005 | 1.834 | 0 |
| RepoRT:0044 | 104 | 2.256 | 3.136 | 0.532 | 1.628 | 0 |
| RepoRT:0007 | 24 | 2.233 | 3.073 | 0.512 | 0.989 | 0 |
| MCMRT:CM 08 | 62 | 2.176 | 3.018 | 0.187 | 1.751 | 0 |
| MCMRT:CM 11 | 62 | 2.174 | 2.957 | 0.082 | 1.563 | 0 |
| RepoRT:0040 | 14 | 2.146 | 2.774 | -0.063 | 1.876 | 0 |
| RepoRT:0014 | 7 | 2.142 | 2.519 | -2.089 | 1.989 | 0 |
| MCMRT:CM 09 | 62 | 2.008 | 2.79 | 0.263 | 1.514 | 0 |
| ReTiNA:mcmrt | 1831 | 1.996 | 3.326 | 0.254 | 1.166 | 0 |
| RepoRT:0029 | 12 | 1.86 | 2.341 | -1.183 | 1.294 | 0 |
| RepoRT:0005 | 13 | 1.855 | 2.464 | -1.441 | 1.086 | 0 |
| RepoRT:0025 | 6 | 1.822 | 2.221 | 0.54 | 1.527 | 0 |
| MCMRT:CM 07 | 62 | 1.788 | 2.402 | 0.311 | 1.483 | 0 |
| RepoRT:0015 | 17 | 1.756 | 2.401 | -0.06 | 1.503 | 0 |
| RepoRT:0018 | 34 | 1.673 | 2.649 | -0.926 | 0.415 | 0 |
| RepoRT:0045 | 35 | 1.658 | 2.317 | -0.706 | 1.258 | 0 |
| internal_lab | 2 | 1.652 | 1.772 | 1.652 | 1.652 | 0 |
| RepoRT:0019 | 74 | 1.646 | 2.32 | 0.527 | 1.306 | 0 |
| ReTiNA:report | 1029 | 1.6 | 3.1 | -0.087 | 0.635 | 0 |
| METLIN_SMRT_Figshare | 16011 | 1.519 | 2.267 | -0.012 | 0.976 | 0 |
| ReTiNA:metlin | 16010 | 1.519 | 2.267 | -0.012 | 0.975 | 0 |
| RepoRT:0016 | 3 | 1.493 | 1.505 | 0.654 | 1.497 | 0 |
| MCMRT:CM 27 | 63 | 1.465 | 1.901 | -0.338 | 1.211 | 0 |
| MCMRT:CM 06 | 62 | 1.445 | 2.081 | 0.136 | 0.955 | 0 |
| MCMRT:CM 20 | 61 | 1.438 | 1.971 | 0.344 | 1.078 | 0 |
| MCMRT:CM 29 | 63 | 1.436 | 1.904 | -0.33 | 0.975 | 0 |
| MCMRT:CM 28 | 63 | 1.356 | 1.721 | 0.095 | 1.101 | 0 |
| RepoRT:0027 | 53 | 1.338 | 1.843 | 0.37 | 0.982 | 0 |
| RepoRT:0010 | 10 | 1.306 | 1.609 | -0.122 | 1.226 | 0 |
| RepoRT:0023 | 12 | 1.276 | 1.645 | 0.521 | 0.894 | 0 |
| RepoRT:0024 | 104 | 1.247 | 1.997 | 0.107 | 0.933 | 0 |
| MCMRT:CM 19 | 62 | 1.215 | 1.809 | 0.254 | 0.789 | 0 |
| MCMRT:CM 03 | 62 | 1.181 | 1.68 | 0.138 | 0.882 | 0 |
| RepoRT:0004 | 27 | 1.143 | 1.515 | 0.264 | 0.926 | 0 |
| RepoRT:0031 | 11 | 1.129 | 1.283 | -0.399 | 1.081 | 0 |
| MCMRT:CM 21 | 61 | 1.086 | 1.597 | 0.295 | 0.779 | 0 |
| MCMRT:CM 05 | 62 | 1.067 | 1.532 | 0.097 | 0.824 | 0 |
| MCMRT:CM 18 | 62 | 1.051 | 1.508 | 0.147 | 0.755 | 0 |
| MCMRT:CM 04 | 62 | 1.049 | 1.504 | 0.185 | 0.855 | 0 |
| RepoRT:0038 | 12 | 1.044 | 1.646 | 0.712 | 0.511 | 0 |
| RepoRT:0043 | 13 | 1.028 | 1.61 | -0.3 | 0.579 | 0 |
| MCMRT:CM 30 | 63 | 0.967 | 1.296 | -0.05 | 0.716 | 0 |
| MCMRT:CM 02 | 62 | 0.964 | 1.32 | 0.041 | 0.769 | 0 |
| MCMRT:CM 26 | 63 | 0.939 | 1.28 | -0.128 | 0.669 | 0 |
| MCMRT:CM 25 | 63 | 0.919 | 1.269 | -0.22 | 0.712 | 0 |
| MCMRT:CM 17 | 62 | 0.828 | 1.154 | 0.093 | 0.633 | 0 |
| RepoRT:0034 | 9 | 0.824 | 1.051 | 0.709 | 0.406 | 0 |
| RepoRT:0033 | 12 | 0.772 | 0.899 | 0.386 | 0.642 | 0 |
| RepoRT:0026 | 3 | 0.755 | 0.957 | -0.755 | 0.514 | 0 |
| ReTiNA:retip | 439 | 0.669 | 1.406 | 0.061 | 0.193 | 0 |
| MCMRT:CM 01 | 62 | 0.662 | 0.937 | 0.094 | 0.46 | 0 |
| RepoRT:0042 | 11 | 0.629 | 0.904 | 0.277 | 0.327 | 0 |
| ReTiNA:massbank | 398 | 0.605 | 0.974 | 0.009 | 0.342 | 0 |
| METLIN_SMRT | 1 | 0.567 | 0.567 | 0.567 | 0.567 | 0 |
| RepoRT:0003 | 18 | 0.47 | 0.561 | 0.392 | 0.47 | 0 |
| RepoRT | 1 | 0.462 | 0.462 | 0.462 | 0.462 | 0 |
| RepoRT:0041 | 17 | 0.448 | 0.558 | -0.137 | 0.432 | 0 |
| RepoRT:0030 | 12 | 0.305 | 0.362 | 0.012 | 0.251 | 0 |
| RepoRT:0013 | 3 | 0.298 | 0.439 | 0.298 | 0.102 | 0 |
| RepoRT:0009 | 68 | 0.214 | 0.359 | 0.11 | 0.118 | 0 |
| ReTiNA:enaminert | 3915 | 0.162 | 0.207 | -0.01 | 0.133 | 0 |
| RepoRT:0008 | 6 | 0.088 | 0.156 | 0.035 | 0.021 | 0 |
| ReTiNA:dynastl | 32 | 0.012 | 0.033 | 0.003 | 0.0 | 0 |

## Source-Family Holdout Metrics

| validation_scope | holdout_family | holdout_key | target | model | n_train | n_holdout | n_train_sources | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_family_holdout | MCMRT | MCMRT | rt_min | linear_ridge | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 4.207 | 5.889 | 0.658 | 0.741 | 13.067 | 0.274 | 3.195 |
| source_family_holdout | MCMRT | MCMRT | rt_min | random_forest | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.255 | 3.534 | 0.877 | 0.913 | 7.006 | 0.207 | 1.424 |
| source_family_holdout | MCMRT | MCMRT | rt_min | extra_trees | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.422 | 3.742 | 0.862 | 0.901 | 7.523 | 0.29 | 1.599 |
| source_family_holdout | MCMRT | MCMRT | rt_min | hist_gradient_boosting | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 2.375 | 3.537 | 0.877 | 0.907 | 7.379 | 0.106 | 1.621 |
| source_family_holdout | MCMRT | MCMRT | quality_score | linear_ridge | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.082 | 0.082 |  |  |  | 0.082 | 0.081 |
| source_family_holdout | MCMRT | MCMRT | quality_score | random_forest | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.002 | 0.002 |  |  |  | 0.002 | 0.003 |
| source_family_holdout | MCMRT | MCMRT | quality_score | extra_trees | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | MCMRT | MCMRT | quality_score | hist_gradient_boosting | 7294 | 10073 | 54 | 4356 | 343 | 32.192 | 0.038 | 0.057 |  |  |  | 0.038 | 0.012 |
| source_family_holdout | RepoRT | RepoRT | rt_min | linear_ridge | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 7.895 | 10.621 | 0.124 | 0.354 | 32.499 | 3.901 | 5.917 |
| source_family_holdout | RepoRT | RepoRT | rt_min | random_forest | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.364 | 6.606 | 0.661 | 0.628 | 17.962 | -1.341 | 2.949 |
| source_family_holdout | RepoRT | RepoRT | rt_min | extra_trees | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.239 | 6.543 | 0.668 | 0.662 | 17.447 | -1.934 | 2.517 |
| source_family_holdout | RepoRT | RepoRT | rt_min | hist_gradient_boosting | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 4.651 | 6.564 | 0.665 | 0.639 | 19.144 | 0.605 | 3.292 |
| source_family_holdout | RepoRT | RepoRT | quality_score | linear_ridge | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.336 | 0.373 | -2210.296 | -0.049 |  | 0.335 | 0.41 |
| source_family_holdout | RepoRT | RepoRT | quality_score | random_forest | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.059 | 0.066 | -68.858 | 0.058 |  | 0.059 | 0.066 |
| source_family_holdout | RepoRT | RepoRT | quality_score | extra_trees | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.072 | 0.081 | -103.86 | 0.058 |  | 0.072 | 0.078 |
| source_family_holdout | RepoRT | RepoRT | quality_score | hist_gradient_boosting | 12876 | 4491 | 41 | 2615 | 2304 | 24.294 | 0.011 | 0.021 | -5.747 | 0.058 |  | 0.008 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | linear_ridge | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 7.414 | 9.451 | -0.366 | 0.438 | 34.945 | -2.884 | 5.761 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | random_forest | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.63 | 4.691 | 0.664 | 0.676 | 17.11 | 2.542 | 3.015 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | extra_trees | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.075 | 3.757 | 0.784 | 0.777 | 14.495 | 0.879 | 2.814 |
| source_family_holdout | ReTiNA | ReTiNA | rt_min | hist_gradient_boosting | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 3.448 | 4.387 | 0.706 | 0.744 | 16.25 | 2.06 | 3.125 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | linear_ridge | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.005 | 0.006 |  |  |  | -0.001 | 0.003 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | random_forest | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | extra_trees | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | ReTiNA | ReTiNA | quality_score | hist_gradient_boosting | 14928 | 2439 | 76 | 2940 | 2145 | 21.216 | 0.012 | 0.031 |  |  |  | 0.012 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | linear_ridge | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.67 | 3.382 | 0.167 | 0.445 | 11.61 | -0.567 | 2.309 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | random_forest | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.347 | 3.155 | 0.274 | 0.595 | 10.203 | 0.991 | 1.974 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | extra_trees | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.395 | 3.087 | 0.306 | 0.539 | 10.414 | -0.398 | 1.979 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | rt_min | hist_gradient_boosting | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 2.373 | 3.185 | 0.261 | 0.512 | 10.317 | -0.187 | 1.879 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | linear_ridge | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.015 | 0.015 |  |  |  | 0.015 | 0.015 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | random_forest | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | extra_trees | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| source_family_holdout | METLIN_SMRT_Figshare | METLIN_SMRT_Figshare | quality_score | hist_gradient_boosting | 17010 | 357 | 83 | 4091 | 357 | 23.0 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |

## Method Holdout Metrics

| validation_scope | holdout_method | holdout_key | target | model | n_train | n_holdout | n_train_methods | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | linear_ridge | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 3.369 | 4.337 | 0.689 | 0.842 | 11.823 | -1.235 | 2.616 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | random_forest | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.674 | 2.457 | 0.9 | 0.966 | 5.873 | -1.063 | 1.011 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | extra_trees | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.56 | 2.057 | 0.93 | 0.974 | 5.474 | -0.876 | 1.154 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | rt_min | hist_gradient_boosting | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 1.624 | 2.16 | 0.923 | 0.964 | 5.699 | -0.694 | 1.216 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | linear_ridge | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.014 | 0.014 |  |  |  | -0.014 | 0.014 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | random_forest | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | extra_trees | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | Acclaim RSLC 120 C18 \| meoh_formic_acid | quality_score | hist_gradient_boosting | 15357 | 2010 | 93 | 4447 | 335 | 28.5 | 0.0 | 0.001 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 6.912 | 10.33 | 0.688 | 0.87 | 14.475 | -2.105 | 3.37 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.884 | 5.832 | 0.901 | 0.955 | 6.04 | 0.559 | 1.083 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.716 | 4.724 | 0.935 | 0.959 | 5.689 | -0.623 | 1.329 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | rt_min | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 2.993 | 5.245 | 0.92 | 0.968 | 6.269 | 0.739 | 1.765 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | quality_score | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 47.75 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 2.254 | 2.914 | 0.668 | 0.877 | 10.482 | -0.261 | 1.833 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.764 | 1.0 | 0.961 | 0.977 | 3.554 | 0.498 | 0.537 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.631 | 0.817 | 0.974 | 0.989 | 2.935 | 0.472 | 0.493 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | rt_min | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 1.014 | 1.372 | 0.926 | 0.959 | 4.718 | 0.324 | 0.767 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | linear_ridge | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.009 | 0.013 |  |  |  | 0.009 | 0.009 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | random_forest | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | extra_trees | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | Thermo Hypersil GOLD \| meoh_formic_acid | quality_score | hist_gradient_boosting | 16027 | 1340 | 93 | 4447 | 335 | 21.5 | 0.0 | 0.001 |  |  |  | 0.0 | 0.0 |

## Column-Family Holdout Metrics

| validation_scope | holdout_column_family | holdout_key | target | model | n_train | n_holdout | n_train_column_families | n_train_groups | n_holdout_groups | mean_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| column_family_holdout | C18 | C18 | rt_min | linear_ridge | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 5.188 | 7.142 | 0.577 | 0.693 | 16.8 | -1.024 | 3.77 |
| column_family_holdout | C18 | C18 | rt_min | random_forest | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 2.978 | 4.849 | 0.805 | 0.854 | 9.643 | -0.602 | 1.774 |
| column_family_holdout | C18 | C18 | rt_min | extra_trees | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 3.023 | 4.899 | 0.801 | 0.862 | 9.79 | -0.987 | 1.911 |
| column_family_holdout | C18 | C18 | rt_min | hist_gradient_boosting | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 3.034 | 4.966 | 0.796 | 0.861 | 9.825 | -0.292 | 1.872 |
| column_family_holdout | C18 | C18 | quality_score | linear_ridge | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.046 | 0.05 |  |  |  | 0.046 | 0.04 |
| column_family_holdout | C18 | C18 | quality_score | random_forest | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| column_family_holdout | C18 | C18 | quality_score | extra_trees | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.0 | 0.0 |  |  |  | -0.0 | 0.0 |
| column_family_holdout | C18 | C18 | quality_score | hist_gradient_boosting | 4303 | 13064 | 3 | 2350 | 2890 | 30.88 | 0.003 | 0.008 |  |  |  | 0.002 | 0.0 |
| column_family_holdout | unknown | unknown | rt_min | linear_ridge | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 5.176 | 7.684 | -0.235 | 0.693 | 24.709 | -2.359 | 3.228 |
| column_family_holdout | unknown | unknown | rt_min | random_forest | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.51 | 3.497 | 0.744 | 0.792 | 11.983 | 1.296 | 1.721 |
| column_family_holdout | unknown | unknown | rt_min | extra_trees | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.396 | 3.194 | 0.787 | 0.832 | 11.438 | 1.055 | 1.643 |
| column_family_holdout | unknown | unknown | rt_min | hist_gradient_boosting | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 2.677 | 3.685 | 0.716 | 0.768 | 12.777 | 1.443 | 1.849 |
| column_family_holdout | unknown | unknown | quality_score | linear_ridge | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.009 | 0.012 |  |  |  | 0.006 | 0.008 |
| column_family_holdout | unknown | unknown | quality_score | random_forest | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| column_family_holdout | unknown | unknown | quality_score | extra_trees | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.0 | 0.0 |  |  |  | 0.0 | 0.0 |
| column_family_holdout | unknown | unknown | quality_score | hist_gradient_boosting | 13076 | 4291 | 3 | 2892 | 2343 | 20.948 | 0.012 | 0.032 |  |  |  | 0.011 | 0.0 |

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

## Parameter Significance

`reports/feature_importance.csv` contains permutation importance for the selected RT model with feature groups, z-like stability scores, and significance labels: `positive`, `weak_positive`, `neutral_or_unstable`, and `negative`. These labels are diagnostic only on the current small held-out split.

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently 2.313 min.
- Split-conformal q90 absolute RT residual: 3.505 min.

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
