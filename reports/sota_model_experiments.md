# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

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

Candidate models: linear_ridge, random_forest, extra_trees, hist_gradient_boosting, xgboost, catboost

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. Model selection uses GroupKFold by compound identity; source-family holdouts are diagnostic transfer checks.
