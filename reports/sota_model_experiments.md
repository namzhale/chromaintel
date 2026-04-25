# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 4.156 | 6.604 | 0.671 | 4.202 | 6.83 | 0.578 |
| random_forest | 2.176 | 4.193 | 0.867 | 1.918 | 3.62 | 0.881 |
| extra_trees | 2.13 | 4.791 | 0.827 | 1.887 | 3.869 | 0.864 |
| hist_gradient_boosting | 2.363 | 4.403 | 0.854 | 2.162 | 4.047 | 0.852 |

ExtraTrees is included as a low-dependency nonlinear baseline. Treat all scores as diagnostics until larger source-aware splits are available.
