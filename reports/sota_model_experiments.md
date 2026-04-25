# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

## RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 4.156 | 6.604 | 0.671 | 4.202 | 6.83 | 0.578 |
| random_forest | 2.176 | 4.193 | 0.867 | 1.918 | 3.62 | 0.881 |
| extra_trees | 2.13 | 4.791 | 0.827 | 1.887 | 3.869 | 0.864 |
| hist_gradient_boosting | 2.363 | 4.403 | 0.854 | 2.162 | 4.047 | 0.852 |
| xgboost | 2.233 | 4.458 | 0.85 | 2.023 | 3.821 | 0.868 |
| catboost | 2.529 | 4.218 | 0.866 | 2.299 | 3.578 | 0.884 |

## Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.004 | 0.739 | 0.0 | 0.004 | 0.806 |
| random_forest | 0.0 | 0.003 | 0.838 | 0.0 | 0.0 | 0.999 |
| extra_trees | 0.0 | 0.003 | 0.795 | 0.0 | 0.007 | 0.38 |
| hist_gradient_boosting | 0.0 | 0.003 | 0.858 | 0.001 | 0.007 | 0.416 |
| xgboost | 0.0 | 0.001 | 0.962 | 0.0 | 0.0 | 0.999 |
| catboost | 0.0 | 0.002 | 0.937 | 0.0 | 0.003 | 0.849 |

Candidate models: linear_ridge, random_forest, extra_trees, hist_gradient_boosting, xgboost, catboost

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. Treat public-source performance as diagnostic until source/group holdout validation is added.
