# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: 4978
- Compounds: 3681
- Source distribution: {'RepoRT:0044': 592, 'RepoRT:0024': 533, 'RepoRT:0002': 413, 'RepoRT:0019': 364, 'RepoRT:0009': 364, 'RepoRT:0027': 302, 'RepoRT:0017': 197, 'RepoRT:0004': 174, 'RepoRT:0045': 147, 'RepoRT:0007': 147, 'RepoRT:0018': 140, 'RepoRT:0020': 116, 'RepoRT:0015': 102, 'RepoRT:0003': 82, 'RepoRT:0040': 78, 'RepoRT:0025': 77, 'RepoRT:0041': 75, 'RepoRT:0001': 73, 'RepoRT:0010': 73, 'RepoRT:0005': 66, 'RepoRT:0038': 57, 'RepoRT:0042': 54, 'RepoRT:0039': 53, 'RepoRT:0036': 51, 'RepoRT:0032': 49, 'RepoRT:0033': 48, 'RepoRT:0028': 47, 'RepoRT:0030': 46, 'RepoRT:0029': 46, 'RepoRT:0023': 45, 'RepoRT:0043': 43, 'RepoRT:0031': 43, 'RepoRT:0021': 41, 'RepoRT:0034': 35, 'RepoRT:0008': 33, 'RepoRT:0037': 29, 'RepoRT:0014': 27, 'RepoRT:0013': 26, 'RepoRT:0016': 26, 'RepoRT:0006': 25, 'RepoRT:0026': 17, 'RepoRT:0022': 9, 'internal_lab': 5, 'RepoRT': 5, 'METLIN_SMRT': 2, 'RepoRT:0029;RepoRT:0040': 1}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Models Tested

- Linear baseline: Ridge regression
- RandomForestRegressor
- ExtraTreesRegressor
- HistGradientBoostingRegressor

## Best Models

- RT model: `extra_trees`
- Peak quality surrogate: `random_forest`

## RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 4.156 | 6.604 | 0.671 | 4.202 | 6.83 | 0.578 |
| random_forest | 2.176 | 4.193 | 0.867 | 1.918 | 3.62 | 0.881 |
| extra_trees | 2.13 | 4.791 | 0.827 | 1.887 | 3.869 | 0.864 |
| hist_gradient_boosting | 2.363 | 4.403 | 0.854 | 2.162 | 4.047 | 0.852 |

## Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.004 | 0.739 | 0.0 | 0.004 | 0.806 |
| random_forest | 0.0 | 0.003 | 0.838 | 0.0 | 0.0 | 0.999 |
| extra_trees | 0.0 | 0.003 | 0.795 | 0.0 | 0.007 | 0.38 |
| hist_gradient_boosting | 0.0 | 0.003 | 0.858 | 0.001 | 0.007 | 0.416 |

## Source-wise Performance

| source_dataset | n_test | rt_mae | rt_rmse | mean_bias | median_abs_error | ad_flagged |
| --- | --- | --- | --- | --- | --- | --- |
| RepoRT:0039 | 9 | 18.655 | 22.64 | 12.929 | 18.2 | 0 |
| RepoRT:0022 | 1 | 8.176 | 8.176 | 8.176 | 8.176 | 0 |
| RepoRT:0037 | 5 | 7.602 | 9.148 | -6.452 | 10.481 | 0 |
| RepoRT:0032 | 11 | 6.271 | 9.06 | 4.678 | 4.946 | 0 |
| RepoRT:0007 | 21 | 3.945 | 4.763 | -0.054 | 3.435 | 0 |
| RepoRT:0036 | 7 | 3.703 | 4.599 | 0.653 | 4.462 | 0 |
| RepoRT:0006 | 7 | 3.611 | 4.845 | 3.464 | 1.582 | 0 |
| RepoRT:0028 | 13 | 3.434 | 5.395 | -0.448 | 2.334 | 0 |
| RepoRT:0002 | 88 | 3.363 | 6.477 | -0.285 | 1.815 | 0 |
| RepoRT:0017 | 38 | 3.21 | 4.471 | 0.557 | 2.722 | 0 |
| RepoRT:0021 | 11 | 2.934 | 3.704 | 0.408 | 1.776 | 0 |
| RepoRT:0040 | 14 | 2.695 | 3.139 | -0.574 | 2.453 | 0 |
| RepoRT:0020 | 22 | 2.265 | 3.04 | 0.971 | 1.607 | 0 |
| RepoRT:0001 | 18 | 2.246 | 3.187 | 1.089 | 2.045 | 0 |
| RepoRT:0044 | 104 | 2.193 | 3.143 | 0.096 | 1.45 | 0 |
| RepoRT:0045 | 33 | 1.908 | 2.458 | -0.071 | 1.285 | 0 |
| RepoRT:0005 | 16 | 1.753 | 2.398 | -1.215 | 1.108 | 0 |
| RepoRT:0029 | 11 | 1.49 | 1.963 | 0.063 | 1.068 | 0 |
| RepoRT:0016 | 5 | 1.445 | 1.74 | -0.144 | 1.601 | 0 |
| RepoRT:0015 | 27 | 1.391 | 1.919 | 0.324 | 0.962 | 0 |
| RepoRT:0038 | 16 | 1.388 | 1.813 | 0.142 | 1.212 | 0 |
| RepoRT:0010 | 16 | 1.386 | 2.945 | -0.75 | 0.503 | 0 |
| RepoRT:0019 | 65 | 1.343 | 1.8 | -0.137 | 0.896 | 0 |
| RepoRT:0027 | 59 | 1.26 | 2.101 | -0.166 | 0.412 | 0 |
| RepoRT | 1 | 1.216 | 1.216 | 1.216 | 1.216 | 0 |
| RepoRT:0018 | 28 | 1.17 | 1.697 | 0.545 | 0.722 | 0 |
| RepoRT:0014 | 7 | 1.116 | 1.353 | 0.047 | 1.124 | 0 |
| RepoRT:0004 | 40 | 0.979 | 1.459 | 0.022 | 0.493 | 0 |
| RepoRT:0023 | 6 | 0.795 | 1.0 | 0.253 | 0.691 | 0 |
| RepoRT:0033 | 15 | 0.785 | 0.902 | 0.126 | 0.6 | 0 |
| RepoRT:0024 | 96 | 0.779 | 1.364 | -0.032 | 0.278 | 0 |
| RepoRT:0025 | 11 | 0.742 | 1.094 | 0.56 | 0.533 | 0 |
| RepoRT:0043 | 14 | 0.736 | 1.317 | -0.08 | 0.251 | 0 |
| RepoRT:0042 | 12 | 0.717 | 0.948 | -0.391 | 0.708 | 0 |
| RepoRT:0031 | 12 | 0.678 | 1.084 | 0.031 | 0.392 | 0 |
| RepoRT:0030 | 10 | 0.67 | 0.844 | 0.644 | 0.509 | 0 |
| RepoRT:0003 | 17 | 0.648 | 0.894 | 0.205 | 0.49 | 0 |
| RepoRT:0041 | 14 | 0.568 | 0.762 | -0.423 | 0.411 | 0 |
| RepoRT:0026 | 2 | 0.546 | 0.74 | -0.546 | 0.546 | 0 |
| RepoRT:0034 | 7 | 0.345 | 0.403 | 0.103 | 0.287 | 0 |
| RepoRT:0013 | 6 | 0.34 | 0.56 | 0.308 | 0.128 | 0 |
| RepoRT:0009 | 73 | 0.183 | 0.291 | 0.036 | 0.068 | 0 |
| RepoRT:0008 | 8 | 0.13 | 0.19 | 0.051 | 0.117 | 0 |

## Parameter Significance

`reports/feature_importance.csv` contains permutation importance for the selected RT model with feature groups, z-like stability scores, and significance labels: `positive`, `weak_positive`, `neutral_or_unstable`, and `negative`. These labels are diagnostic only on the current small held-out split.

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently 3.864 min.
- Split-conformal q90 absolute RT residual: 4.999 min.

## Current Limitations

- The checked-in dataset is a small mock/demo set, not yet a validated internal laboratory history.
- Public RT datasets often lack peak quality, matrix, sample preparation, and MS transition metadata.
- Quality score is provisional. It uses observed quality_score when present; otherwise it is a transparent proxy from S/N, resolution, asymmetry, and tailing.
- Source-aware validation is reported by source distribution and source-wise error; larger datasets should use source holdout splits.

## Next Steps

1. Import internal historical BE assay development runs using the internal template.
2. Calibrate RT and quality models on accepted lab methods by instrument platform and matrix.
3. Add explicit uncertainty calibration and applicability-domain checks.
4. Expand candidate search spaces to match available columns, solvents, and validated operating ranges.
