# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 1.558 | 1.825 | -2.431 | 2.901 | 3.298 | -0.791 |
| random_forest | 1.703 | 1.943 | -2.889 | 2.168 | 2.589 | -0.104 |
| extra_trees | 2.128 | 2.593 | -5.927 | 1.952 | 2.121 | 0.259 |
| hist_gradient_boosting | 1.733 | 1.994 | -3.096 | 2.072 | 2.678 | -0.182 |

ExtraTrees is included as a low-dependency nonlinear baseline. Treat all scores as diagnostics until larger source-aware splits are available.
