# Inverse Recommendation Model Metrics

- Training rows: 10000
- Label source: `synthetic_proxy`
- Best model: `logistic_regression`

## Classification Metrics

| model | roc_auc | pr_auc | accuracy | balanced_accuracy | brier_score | n_test | label_source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| logistic_regression | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 2294 | synthetic_proxy |
| random_forest | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 2294 | synthetic_proxy |
| extra_trees | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 2294 | synthetic_proxy |
| hist_gradient_boosting | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 2294 | synthetic_proxy |
| xgboost | 1.0 | 1.0 | 1.0 | 1.0 | 0.002 | 2294 | synthetic_proxy |
| catboost | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 2294 | synthetic_proxy |

## Top-k Suitability Proxy

| model | top_1_success | top_3_success | top_5_success | mean_first_suitable_rank | label_source |
| --- | --- | --- | --- | --- | --- |
| logistic_regression | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |
| random_forest | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |
| extra_trees | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |
| hist_gradient_boosting | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |
| xgboost | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |
| catboost | 1.0 | 1.0 | 1.0 | 1.0 | synthetic_proxy |

## Limitations

- Labels are generated from forward-model style suitability rules, not accepted laboratory outcomes.
- Treat this as an inverse ranking baseline until internal assay development results are connected.
