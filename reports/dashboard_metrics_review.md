# Dashboard Metrics Review

## Implemented Artifacts

- `reports/feature_importance.csv`: RT permutation importance with `feature_group`, `importance_z`, and `significance` labels.
- `reports/test_predictions.csv`: held-out predictions with signed/absolute RT error and applicability-domain flags.
- `reports/source_metrics.csv`: source-wise `n_test`, RT MAE/RMSE, mean bias, median absolute error, and AD flag counts.
- `reports/model_training_summary.md`: validation metrics, source-wise metrics, parameter-significance note, and uncertainty metadata.

## Streamlit Display

The Dashboard and Training pages now read these artifacts directly when present:

- held-out predicted-vs-actual RT scatter with y=x reference line;
- RT residual histogram;
- worst-error table with AD flag/reason columns;
- source-wise RT error table and bar chart;
- permutation-importance chart colored by significance.

## Current Interpretation Limits

The checked-in demo data is small, so permutation significance and source-wise errors are diagnostics, not evidence of production robustness. Source-wise metrics can be one row per source after the current random split. The split-conformal q90 residual is exposed as uncertainty metadata, but it should be recalibrated on a larger validation set before user-facing confidence claims.
