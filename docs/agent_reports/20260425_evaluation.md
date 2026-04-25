# Agent 4 Method-Conditioned Evaluation

Date: 2026-04-25

## Scope

- Audited `app/models/training.py` and `tests/test_training.py`.
- Added method-conditioned and column-family holdout diagnostics.
- Added Spearman correlation where the evaluated target and predictions have usable variation.
- Added RT normalized MAE as percent of mean runtime.
- Persisted `reports/evaluation_matrix.csv`, `reports/evaluation_matrix.md`, and `reports/split_manifest.json`.

## Implementation Notes

- Evaluation rows are long-form and deduplicated by validation scope, target, model, split name, and holdout key.
- Source-family, method, and column-family holdouts share the same categorical holdout evaluator to avoid metric drift.
- Method and column diagnostics use adaptive minimum row thresholds and cap the number of held-out labels so full-matrix training remains diagnostic rather than exhaustive.
- `scripts/train_models.py` remains backward compatible; `train_forward_models` keeps its public call signature.

## Generated Diagnostics

- `method_holdout`: column name plus mobile phase system.
- `column_family_holdout`: column chemistry, falling back to stationary phase type if needed.
- `normalized_mae_runtime_pct`: RT MAE divided by mean `total_runtime_min` for the evaluated rows.
- `split_manifest`: grouped train, validation, and test split membership with group overlap counts.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests\test_training.py::test_train_forward_models_exports_sota_metadata_and_feature_importance -q`
- `.\.venv\Scripts\python.exe -m pytest tests\test_training.py -q`
