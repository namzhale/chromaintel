# 2026-04-26 Inverse ML And Peak Target Slice

## Existing Implementation Audit

### Already Exists

- Forward RT and provisional quality model training pipeline in `app/models/training.py`.
- Recommendation candidate generation, score decomposition, configurable search space, and OOD penalties in `app/services/recommendation.py`.
- DL preparation skeleton for graph and SMILES-transformer manifests in `scripts/prepare_dl_datasets.py`.
- Russian PDF dashboard generator in `scripts/generate_dashboard_pdf.py`.
- Streamlit training and recommendation pages in `app/gui/streamlit_app.py`.

### Partially Exists

- Peak metrics existed in the canonical schema, but the project did not report which direct targets were trainable versus proxy-only or unavailable.
- Recommendation scoring existed, but there was no persisted inverse suitability model that could rerank candidates.
- DL data preparation existed for future neural branches, but it did not expose pairwise retention-order or inverse-task manifests.
- Dashboard reporting existed, but did not show target readiness or inverse model metrics.

### Newly Implemented

- `app/services/target_readiness.py` builds measured/proxy/unavailable target coverage reports for RT, quality, peak-shape metrics, intensity metrics, and derived risks.
- `app/models/inverse_training.py` trains CPU-friendly inverse recommendation classifiers on transparent synthetic/proxy labels.
- `scripts/analyze_target_readiness.py` regenerates target-readiness reports.
- `scripts/train_inverse_models.py` trains inverse recommendation ML baselines and writes metrics/top-k reports.
- `scripts/prepare_dl_datasets.py` now writes graph, SMILES-transformer, pairwise retention-order, and inverse-task manifests with target label-source metadata.
- `app/services/recommendation.py` optionally loads `data/processed/models/inverse_recommendation_bundle.joblib` and adds inverse score components to candidate ranking.
- `app/gui/streamlit_app.py` now displays target-readiness and inverse ML reports and warns that inverse labels are proxy-trained.
- `scripts/generate_dashboard_pdf.py` includes a target/inverse-model page in the Russian presentation PDF.

### Intentionally Skipped

- Neural network training was not run in this slice. The goal was data preparation and ML inverse modeling only.
- The inverse bundle is not committed because `data/processed/models/*.joblib` artifacts are ignored/local under the current artifact policy.
- Claims about production peak-quality prediction are avoided because public data do not yet provide measured asymmetry, width, resolution, S/N, peak area, or peak height labels at useful coverage.

### Files Reused

- `app/services/recommendation.py`
- `app/gui/streamlit_app.py`
- `scripts/prepare_dl_datasets.py`
- `scripts/generate_dashboard_pdf.py`
- `README.md`
- `.PLAN`

### Files Modified

- `app/schemas/prediction.py`
- `app/services/recommendation.py`
- `app/gui/streamlit_app.py`
- `scripts/prepare_dl_datasets.py`
- `scripts/generate_dashboard_pdf.py`
- `tests/test_dashboard_pdf.py`
- `tests/test_prepare_dl_datasets.py`
- `tests/test_recommendation.py`
- `README.md`
- `.PLAN`

### Files Created

- `app/services/target_readiness.py`
- `app/models/inverse_training.py`
- `scripts/analyze_target_readiness.py`
- `scripts/train_inverse_models.py`
- `tests/test_target_readiness.py`
- `tests/test_inverse_training.py`
- `tests/test_slice_cli_scripts.py`
- `reports/target_coverage_matrix.csv`
- `reports/peak_metric_target_readiness.md`
- `reports/inverse_model_metrics.csv`
- `reports/inverse_model_metrics.md`
- `reports/inverse_topk_evaluation.csv`
- `reports/inverse_training_table_sample.csv`

## Verification Notes

Targeted tests were run during implementation for target readiness, inverse training, DL preparation, recommendation integration, and dashboard PDF generation. Full repository verification is handled by the integrating agent before commit.
