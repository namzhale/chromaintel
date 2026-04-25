# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: 15052
- Compounds: 3945
- Source distribution: {'RepoRT:0044': 592, 'RepoRT:0024': 533, 'RepoRT:0002': 413, 'RepoRT:0019': 364, 'RepoRT:0009': 364, 'MCMRT:CM 30': 343, 'MCMRT:CM 26': 343, 'MCMRT:CM 27': 343, 'MCMRT:CM 25': 343, 'MCMRT:CM 28': 343, 'MCMRT:CM 29': 343, 'MCMRT:CM 04': 335, 'MCMRT:CM 17': 335, 'MCMRT:CM 16': 335, 'MCMRT:CM 15': 335, 'MCMRT:CM 14': 335, 'MCMRT:CM 13': 335, 'MCMRT:CM 12': 335, 'MCMRT:CM 11': 335, 'MCMRT:CM 01': 335, 'MCMRT:CM 10': 335, 'MCMRT:CM 09': 335, 'MCMRT:CM 08': 335, 'MCMRT:CM 19': 335, 'MCMRT:CM 03': 335, 'MCMRT:CM 07': 335, 'MCMRT:CM 02': 335, 'MCMRT:CM 18': 335, 'MCMRT:CM 05': 335, 'MCMRT:CM 06': 335, 'MCMRT:CM 21': 330, 'MCMRT:CM 22': 330, 'MCMRT:CM 23': 330, 'MCMRT:CM 24': 330, 'MCMRT:CM 20': 330, 'RepoRT:0027': 302, 'RepoRT:0017': 197, 'RepoRT:0004': 174, 'RepoRT:0045': 147, 'RepoRT:0007': 147, 'RepoRT:0018': 140, 'RepoRT:0020': 116, 'RepoRT:0015': 102, 'RepoRT:0003': 82, 'RepoRT:0040': 79, 'RepoRT:0025': 77, 'RepoRT:0041': 75, 'RepoRT:0010': 73, 'RepoRT:0001': 73, 'RepoRT:0005': 66, 'RepoRT:0038': 57, 'RepoRT:0042': 54, 'RepoRT:0039': 53, 'RepoRT:0036': 51, 'RepoRT:0032': 49, 'RepoRT:0033': 48, 'RepoRT:0028': 47, 'RepoRT:0029': 47, 'RepoRT:0030': 46, 'RepoRT:0023': 45, 'RepoRT:0043': 43, 'RepoRT:0031': 43, 'RepoRT:0021': 41, 'RepoRT:0034': 35, 'RepoRT:0008': 33, 'RepoRT:0037': 29, 'RepoRT:0014': 27, 'RepoRT:0016': 26, 'RepoRT:0013': 26, 'RepoRT:0006': 25, 'RepoRT:0026': 17, 'RepoRT:0022': 9, 'RepoRT': 5, 'internal_lab': 5, 'METLIN_SMRT': 2}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Validation Design

- Model selection: GroupKFold by `inchikey`.
- Final holdout: group-aware train/validation/test split with no compound identity overlap between splits.
- Source-family holdout: train without each large source family and test on that held-out family.

## Models Tested

- linear_ridge
- random_forest
- extra_trees
- hist_gradient_boosting
- xgboost
- catboost

## Best Models

- RT model: `extra_trees`
- Peak quality surrogate: `random_forest`

## Grouped CV Metrics

| validation_scope | target | model | group_column | n_folds | n_rows | n_groups | mae_mean | mae_std | rmse_mean | rmse_std | r2_mean | r2_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_kfold | rt_min | linear_ridge | inchikey | 5 | 15052 | 2785 | 3.776 | 0.107 | 5.681 | 0.094 | 0.709 | 0.033 |
| group_kfold | rt_min | random_forest | inchikey | 5 | 15052 | 2785 | 1.983 | 0.046 | 3.346 | 0.194 | 0.898 | 0.019 |
| group_kfold | rt_min | extra_trees | inchikey | 5 | 15052 | 2785 | 1.849 | 0.075 | 3.163 | 0.156 | 0.909 | 0.017 |
| group_kfold | rt_min | hist_gradient_boosting | inchikey | 5 | 15052 | 2785 | 2.072 | 0.062 | 3.396 | 0.195 | 0.895 | 0.021 |
| group_kfold | rt_min | xgboost | inchikey | 5 | 15052 | 2785 | 2.03 | 0.061 | 3.32 | 0.205 | 0.9 | 0.018 |
| group_kfold | rt_min | catboost | inchikey | 5 | 15052 | 2785 | 2.164 | 0.079 | 3.363 | 0.187 | 0.897 | 0.021 |
| group_kfold | quality_score | linear_ridge | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.003 | 0.005 | 0.554 | 0.338 |
| group_kfold | quality_score | random_forest | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.001 | 0.95 | 0.027 |
| group_kfold | quality_score | extra_trees | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.901 | 0.065 |
| group_kfold | quality_score | hist_gradient_boosting | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.005 | 0.005 | 0.2 | 0.096 |
| group_kfold | quality_score | xgboost | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.897 | 0.038 |
| group_kfold | quality_score | catboost | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.919 | 0.003 |

## Final Grouped Holdout RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 3.653 | 5.479 | 0.717 | 3.891 | 5.737 | 0.737 |
| random_forest | 2.09 | 3.372 | 0.893 | 1.989 | 3.474 | 0.904 |
| extra_trees | 1.917 | 3.226 | 0.902 | 1.861 | 3.173 | 0.92 |
| hist_gradient_boosting | 2.056 | 3.171 | 0.905 | 2.095 | 3.463 | 0.904 |
| xgboost | 2.074 | 3.281 | 0.898 | 1.991 | 3.36 | 0.91 |
| catboost | 2.238 | 3.325 | 0.896 | 2.186 | 3.494 | 0.903 |

## Final Grouped Holdout Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.85 |
| random_forest | 0.0 | 0.0 |  | 0.0 | 0.002 | 0.938 |
| extra_trees | 0.0 | 0.0 |  | 0.0 | 0.002 | 0.948 |
| hist_gradient_boosting | 0.0 | 0.001 |  | 0.0 | 0.005 | 0.69 |
| xgboost | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.908 |
| catboost | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.912 |

## Source-wise Performance

| source_dataset | n_test | rt_mae | rt_rmse | mean_bias | median_abs_error | ad_flagged |
| --- | --- | --- | --- | --- | --- | --- |
| RepoRT:0039 | 14 | 12.001 | 17.435 | 0.588 | 7.2 | 0 |
| RepoRT:0022 | 1 | 11.966 | 11.966 | -11.966 | 11.966 | 0 |
| MCMRT:CM 16 | 73 | 5.856 | 7.823 | -1.414 | 4.38 | 0 |
| RepoRT:0036 | 10 | 4.869 | 6.078 | -2.674 | 3.342 | 0 |
| RepoRT:0037 | 7 | 4.116 | 5.336 | -0.273 | 3.946 | 0 |
| RepoRT:0002 | 88 | 3.414 | 7.089 | 0.168 | 1.632 | 0 |
| MCMRT:CM 15 | 73 | 3.376 | 4.25 | -0.555 | 2.886 | 0 |
| MCMRT:CM 14 | 73 | 3.372 | 4.366 | -0.696 | 2.901 | 0 |
| MCMRT:CM 13 | 73 | 3.371 | 4.336 | -0.624 | 2.791 | 0 |
| RepoRT:0028 | 13 | 3.308 | 4.171 | -0.913 | 2.584 | 0 |
| RepoRT:0032 | 14 | 3.218 | 4.085 | 0.046 | 2.647 | 0 |
| MCMRT:CM 12 | 73 | 3.181 | 4.096 | -0.664 | 2.821 | 0 |
| MCMRT:CM 22 | 70 | 3.175 | 4.235 | -0.408 | 2.418 | 0 |
| MCMRT:CM 24 | 70 | 3.156 | 4.297 | -0.395 | 2.166 | 0 |
| RepoRT:0017 | 44 | 2.821 | 3.804 | -0.588 | 2.279 | 0 |
| MCMRT:CM 23 | 70 | 2.766 | 3.824 | -0.362 | 1.992 | 0 |
| RepoRT:0021 | 11 | 2.606 | 3.108 | 0.484 | 1.795 | 0 |
| RepoRT:0040 | 24 | 2.557 | 3.127 | 0.24 | 2.11 | 0 |
| RepoRT:0044 | 140 | 2.352 | 3.184 | -0.036 | 1.801 | 0 |
| RepoRT:0005 | 19 | 2.129 | 2.582 | -0.886 | 1.717 | 0 |
| MCMRT:CM 08 | 73 | 2.014 | 2.592 | -0.423 | 1.762 | 0 |
| MCMRT:CM 10 | 73 | 2.014 | 2.591 | -0.413 | 1.773 | 0 |
| RepoRT:0020 | 21 | 1.995 | 2.592 | 0.721 | 1.68 | 0 |
| RepoRT:0007 | 32 | 1.983 | 2.708 | -0.264 | 1.582 | 0 |
| RepoRT:0018 | 28 | 1.978 | 2.804 | 0.127 | 1.777 | 0 |
| RepoRT:0029 | 13 | 1.943 | 2.497 | 1.065 | 1.622 | 0 |
| MCMRT:CM 11 | 73 | 1.909 | 2.465 | -0.434 | 1.668 | 0 |
| MCMRT:CM 09 | 73 | 1.879 | 2.435 | -0.37 | 1.617 | 0 |
| RepoRT:0001 | 12 | 1.796 | 2.342 | -0.295 | 1.369 | 0 |
| MCMRT:CM 07 | 73 | 1.731 | 2.19 | -0.304 | 1.579 | 0 |
| internal_lab | 2 | 1.704 | 1.753 | 1.704 | 1.704 | 0 |
| RepoRT:0045 | 25 | 1.686 | 2.083 | -0.147 | 1.658 | 0 |
| RepoRT:0019 | 62 | 1.605 | 2.236 | 0.211 | 1.084 | 0 |
| MCMRT:CM 27 | 75 | 1.48 | 1.971 | -0.321 | 1.128 | 0 |
| RepoRT:0027 | 61 | 1.433 | 2.139 | -0.34 | 0.812 | 0 |
| MCMRT:CM 28 | 75 | 1.428 | 1.872 | -0.35 | 0.993 | 0 |
| MCMRT:CM 29 | 75 | 1.427 | 1.925 | -0.28 | 1.034 | 0 |
| RepoRT:0013 | 7 | 1.395 | 2.344 | 1.395 | 0.237 | 0 |
| RepoRT:0015 | 18 | 1.39 | 2.011 | -0.234 | 0.869 | 0 |
| RepoRT:0010 | 14 | 1.359 | 2.115 | -0.223 | 0.761 | 0 |
| MCMRT:CM 06 | 73 | 1.304 | 1.715 | -0.293 | 1.176 | 0 |
| MCMRT:CM 20 | 70 | 1.281 | 1.643 | -0.141 | 1.087 | 0 |
| RepoRT:0016 | 5 | 1.212 | 1.712 | -0.171 | 0.65 | 0 |
| RepoRT | 1 | 1.211 | 1.211 | 1.211 | 1.211 | 0 |
| MCMRT:CM 19 | 73 | 1.2 | 1.579 | -0.241 | 0.9 | 0 |
| RepoRT:0004 | 43 | 1.173 | 1.781 | -0.269 | 0.727 | 0 |
| RepoRT:0006 | 3 | 1.172 | 1.657 | 0.783 | 0.583 | 0 |
| MCMRT:CM 03 | 73 | 1.14 | 1.462 | -0.203 | 0.907 | 0 |
| RepoRT:0038 | 10 | 1.125 | 1.427 | -0.502 | 0.989 | 0 |
| RepoRT:0023 | 12 | 1.061 | 1.382 | 0.735 | 0.832 | 0 |
| MCMRT:CM 18 | 73 | 1.041 | 1.319 | -0.204 | 0.84 | 0 |
| MCMRT:CM 05 | 73 | 1.028 | 1.324 | -0.158 | 0.754 | 0 |
| MCMRT:CM 21 | 70 | 1.015 | 1.346 | -0.07 | 0.747 | 0 |
| MCMRT:CM 04 | 73 | 1.004 | 1.29 | -0.143 | 0.836 | 0 |
| MCMRT:CM 30 | 75 | 0.994 | 1.334 | -0.227 | 0.727 | 0 |
| MCMRT:CM 25 | 75 | 0.966 | 1.346 | -0.373 | 0.533 | 0 |
| MCMRT:CM 26 | 75 | 0.956 | 1.347 | -0.374 | 0.595 | 0 |
| RepoRT:0024 | 93 | 0.867 | 1.503 | 0.329 | 0.307 | 0 |
| MCMRT:CM 17 | 73 | 0.77 | 1.001 | -0.115 | 0.618 | 0 |
| MCMRT:CM 02 | 73 | 0.745 | 0.983 | -0.167 | 0.566 | 0 |
| RepoRT:0025 | 10 | 0.703 | 0.838 | 0.23 | 0.539 | 0 |
| RepoRT:0014 | 2 | 0.67 | 0.856 | -0.67 | 0.67 | 0 |
| RepoRT:0033 | 13 | 0.646 | 0.781 | -0.02 | 0.518 | 0 |
| RepoRT:0003 | 13 | 0.6 | 0.755 | 0.222 | 0.549 | 0 |
| RepoRT:0042 | 12 | 0.595 | 0.738 | -0.131 | 0.575 | 0 |
| RepoRT:0031 | 11 | 0.595 | 0.802 | -0.331 | 0.296 | 0 |
| RepoRT:0026 | 2 | 0.588 | 0.593 | -0.588 | 0.588 | 0 |
| MCMRT:CM 01 | 73 | 0.507 | 0.662 | -0.06 | 0.404 | 0 |
| RepoRT:0034 | 10 | 0.397 | 0.567 | 0.122 | 0.204 | 0 |
| RepoRT:0041 | 23 | 0.386 | 0.486 | -0.232 | 0.363 | 0 |
| RepoRT:0030 | 12 | 0.337 | 0.434 | 0.065 | 0.341 | 0 |
| RepoRT:0043 | 10 | 0.308 | 0.375 | 0.189 | 0.295 | 0 |
| RepoRT:0009 | 90 | 0.221 | 0.371 | -0.014 | 0.126 | 0 |
| RepoRT:0008 | 5 | 0.158 | 0.245 | 0.118 | 0.101 | 0 |

## Source-Family Holdout Metrics

| validation_scope | holdout_family | target | model | n_train | n_holdout | n_train_sources | n_train_groups | n_holdout_groups | mae | rmse | r2 | mean_bias | median_abs_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_family_holdout | MCMRT | rt_min | linear_ridge | 4979 | 10073 | 45 | 2509 | 343 | 5.335 | 6.998 | 0.517 | 3.841 | 4.364 |
| source_family_holdout | MCMRT | rt_min | random_forest | 4979 | 10073 | 45 | 2509 | 343 | 3.625 | 4.858 | 0.767 | -1.118 | 2.797 |
| source_family_holdout | MCMRT | rt_min | extra_trees | 4979 | 10073 | 45 | 2509 | 343 | 4.016 | 5.464 | 0.705 | -0.575 | 2.921 |
| source_family_holdout | MCMRT | rt_min | hist_gradient_boosting | 4979 | 10073 | 45 | 2509 | 343 | 3.585 | 4.904 | 0.763 | -0.477 | 2.579 |
| source_family_holdout | MCMRT | rt_min | xgboost | 4979 | 10073 | 45 | 2509 | 343 | 3.666 | 5.007 | 0.753 | -1.367 | 2.641 |
| source_family_holdout | MCMRT | rt_min | catboost | 4979 | 10073 | 45 | 2509 | 343 | 4.172 | 5.852 | 0.662 | -0.277 | 2.854 |
| source_family_holdout | MCMRT | quality_score | linear_ridge | 4979 | 10073 | 45 | 2509 | 343 | 0.096 | 0.096 |  | 0.096 | 0.096 |
| source_family_holdout | MCMRT | quality_score | random_forest | 4979 | 10073 | 45 | 2509 | 343 | 0.063 | 0.064 |  | 0.063 | 0.067 |
| source_family_holdout | MCMRT | quality_score | extra_trees | 4979 | 10073 | 45 | 2509 | 343 | 0.129 | 0.13 |  | 0.129 | 0.132 |
| source_family_holdout | MCMRT | quality_score | hist_gradient_boosting | 4979 | 10073 | 45 | 2509 | 343 | 0.009 | 0.024 |  | 0.008 | 0.001 |
| source_family_holdout | MCMRT | quality_score | xgboost | 4979 | 10073 | 45 | 2509 | 343 | 0.023 | 0.025 |  | 0.023 | 0.023 |
| source_family_holdout | MCMRT | quality_score | catboost | 4979 | 10073 | 45 | 2509 | 343 | 0.035 | 0.037 |  | 0.035 | 0.035 |
| source_family_holdout | RepoRT | rt_min | linear_ridge | 10080 | 4972 | 32 | 350 | 2507 | 49.538 | 64.865 | -33.162 | -40.567 | 30.983 |
| source_family_holdout | RepoRT | rt_min | random_forest | 10080 | 4972 | 32 | 350 | 2507 | 8.679 | 13.822 | -0.551 | 4.606 | 4.434 |
| source_family_holdout | RepoRT | rt_min | extra_trees | 10080 | 4972 | 32 | 350 | 2507 | 5.254 | 7.765 | 0.51 | -0.552 | 3.715 |
| source_family_holdout | RepoRT | rt_min | hist_gradient_boosting | 10080 | 4972 | 32 | 350 | 2507 | 5.184 | 8.075 | 0.471 | -1.21 | 3.305 |
| source_family_holdout | RepoRT | rt_min | xgboost | 10080 | 4972 | 32 | 350 | 2507 | 5.528 | 8.445 | 0.421 | -2.358 | 3.466 |
| source_family_holdout | RepoRT | rt_min | catboost | 10080 | 4972 | 32 | 350 | 2507 | 5.187 | 7.76 | 0.511 | -0.024 | 3.776 |
| source_family_holdout | RepoRT | quality_score | linear_ridge | 10080 | 4972 | 32 | 350 | 2507 | 0.343 | 0.377 | -2493.717 | 0.342 | 0.41 |
| source_family_holdout | RepoRT | quality_score | random_forest | 10080 | 4972 | 32 | 350 | 2507 | 0.078 | 0.085 | -124.719 | 0.078 | 0.078 |
| source_family_holdout | RepoRT | quality_score | extra_trees | 10080 | 4972 | 32 | 350 | 2507 | 0.076 | 0.082 | -117.018 | 0.076 | 0.082 |
| source_family_holdout | RepoRT | quality_score | hist_gradient_boosting | 10080 | 4972 | 32 | 350 | 2507 | 0.004 | 0.009 | -0.583 | 0.003 | 0.001 |
| source_family_holdout | RepoRT | quality_score | xgboost | 10080 | 4972 | 32 | 350 | 2507 | 0.005 | 0.005 | 0.485 | 0.005 | 0.004 |
| source_family_holdout | RepoRT | quality_score | catboost | 10080 | 4972 | 32 | 350 | 2507 | 0.062 | 0.069 | -83.609 | 0.062 | 0.059 |

## Parameter Significance

`reports/feature_importance.csv` contains permutation importance for the selected RT model with feature groups, z-like stability scores, and significance labels: `positive`, `weak_positive`, `neutral_or_unstable`, and `negative`. These labels are diagnostic only on the current small held-out split.

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently 3.163 min.
- Split-conformal q90 absolute RT residual: 4.517 min.

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
