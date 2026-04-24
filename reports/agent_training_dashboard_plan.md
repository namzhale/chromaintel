# Training and Dashboard Planning Check

## Current Training Outputs

The current `scripts/train_models.py` path loads or assembles `data/processed/model_matrix.csv`, trains the forward RT and provisional quality models through `app.models.training.train_forward_models`, and writes:

- `data/processed/master_dataset.csv`
- `data/processed/model_matrix.csv`
- `data/processed/models/trained_forward_bundle.joblib`
- `reports/model_training_summary.md`
- `reports/test_predictions.csv`
- `reports/feature_importance.csv`
- `data/processed/plots/predicted_vs_actual_rt.html`
- `data/processed/plots/rt_error_distribution.html`
- `data/processed/plots/source_wise_performance.html`
- `data/processed/plots/feature_importance.html`

Observed current run state:

- Model matrix: 12 rows, 8 compounds.
- Source distribution: internal_lab 5, RepoRT 5, METLIN_SMRT 2.
- Split implied by report/code: train 7, validation 2, test 3.
- Best RT model by validation MAE: `linear_ridge`.
- Best quality model by validation MAE: `linear_ridge`.
- Current RT test metrics: linear_ridge MAE 2.901 min, RMSE 3.298 min, R2 -0.791; random_forest test MAE 2.168; hist_gradient_boosting test MAE 2.072.
- Current source-wise test MAE: METLIN_SMRT 5.006, RepoRT 2.454, internal_lab 1.242.
- Current quality target is constant at 0.55 for all 12 rows, so quality metrics of 0.0 error are not meaningful.

## Dashboard Panels To Add

### 1. Training Artifact Status

- Cards for artifact/report freshness, row counts, train/validation/test counts, best RT model, best quality model, feature count, and source counts.
- Warning banner when `trained_forward_bundle.joblib` is missing and predictor is using baseline or heuristic fallback.
- Link/list of generated report assets and plots.

### 2. RT Performance

- Metric table from report metadata: validation/test MAE, RMSE, R2 for each candidate model.
- Predicted vs actual RT scatter from `reports/test_predictions.csv`, colored by source, with y=x reference line.
- Residual histogram and absolute-error-by-RT plot.
- Worst-error table with compound, source, actual RT, predicted RT, signed error, absolute error.
- Residual standard deviation card and clear note that current uncertainty is test-split residual std only.

### 3. Quality Surrogate

- Observed quality distribution and variance card.
- Warning when quality has too few unique values; current data should show "constant quality target, surrogate not validated".
- Predicted vs observed quality only when target variance is non-zero.
- Proxy component coverage cards for S/N, resolution, asymmetry, tailing factor, peak area, peak height.
- Table showing which rows used explicit quality versus proxy-derived quality once explicit/proxy provenance is available.

### 4. Source-Wise Metrics

- Source counts for full matrix and test split.
- Source-wise RT MAE/RMSE, mean bias, median absolute error, and n-test.
- Faceted residual distributions by source.
- Coverage/missingness by source for LC, MS, quality, and peak-shape fields.
- Source-holdout placeholder panel for future larger datasets.

### 5. Recommendation Proxy

- Candidate search summary: number generated, number surviving constraints, top N returned.
- Score decomposition per top candidate: RT fit, predicted quality, runtime penalty, confidence contribution.
- Target-fit plot: target RT vs predicted RT delta for top candidates.
- Runtime vs predicted quality scatter, colored by column/phase and sized by confidence.
- Diversity cards for top N: unique columns, solvent systems, pH values, gradient durations.
- Offline proxy on held-out rows: generate recommendations using each held-out row's compound/target RT and report top-k RT success within tolerances such as +/-0.5 and +/-1.0 min.

### 6. Feature Importance

- Top feature importance bar chart from `reports/feature_importance.csv` with error bars.
- Table including negative/near-zero importances, because current tiny test split produces unstable signs.
- Grouped importances by compound descriptors, LC numeric, LC categorical, and MS settings.
- Tooltip/caption explaining permutation importance was computed on the RT model and current n-test is only 3.

### 7. Data Missingness

- Full model-matrix missingness heatmap/table.
- Current critical missingness: peak_area, peak_height, sn_ratio, asymmetry, tailing_factor, and resolution are 100% missing.
- Missingness by source and by feature group.
- Target completeness cards for RT and quality-supporting fields.
- Default-imputation audit for LC/MS fields, because feature engineering currently fills several missing method fields with defaults.

## Static Risks And Likely Bugs

- `app/services/feature_engineering.py` lists `quality_score` in `TARGET_COLUMNS`, but `_target_fields` explicitly excludes it. `build_model_matrix` then calls `_quality_score(feature_row)`, so explicit source `quality_score` values appear to be ignored before proxy calculation. This can collapse quality targets to the default/proxy value.
- Current processed data has quality_score = 0.55 for all 12 rows and 100% missing S/N, resolution, asymmetry, tailing, peak area, and peak height. Quality model metrics are therefore non-informative.
- Training selects best model by validation MAE, but with 12 rows the validation/test splits are about 2/3 rows. The selected linear RT model has worse test MAE than random forest and hist gradient boosting in the current report.
- Source-wise performance is computed only on the tiny test split, currently one row per source. Treat as diagnostic, not model evidence.
- Missing LC/MS method fields are converted to defaults in feature engineering, which is useful for prediction but can hide data quality problems unless dashboards report pre-default missingness.
- Confidence is a global residual-std heuristic scaled by predicted RT, not calibrated uncertainty.
- The Streamlit model evaluation page still trains/evaluates the legacy baseline path and does not appear to consume the newer `reports/*` and `trained_forward_bundle.joblib` outputs.

## Tests Inspected

The existing tests cover dataset normalization/deduplication, RDKit descriptors, feature matrix/proxy quality, internal template validation, and recommendation ranking. I did not run the test suite during this read-only check.
