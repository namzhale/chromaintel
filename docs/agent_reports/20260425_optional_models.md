# Agent 6 Optional Models Status Report

## Scope

- Audited `requirements.txt`.
- Audited `app/models/training.py`.
- Added dependency-gated optional-model status documentation.
- Added a lightweight documentation contract test.

## Findings

- The current trainable stack is CPU-first tabular modeling in `app/models/training.py`.
- `training.py` already owns active wrappers for Ridge, RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, and CatBoost.
- XGBoost and CatBoost use the existing local-import, graceful-skip pattern in `_optional_boosting_models`.
- `requirements.txt` pins `xgboost` and `catboost`.
- `requirements.txt` does not include `lightgbm`, PyTorch, PyG/DGL, Chemprop, Transformers, BoTorch, Optuna, or scikit-optimize.

## Status Recorded

| Family | Recorded status |
| --- | --- |
| LightGBM | Not implemented; dependency-gated. |
| GCN | Roadmap only; graph stack dependency-gated. |
| GAT | Roadmap only; graph stack dependency-gated. |
| MPNN | Roadmap only; graph chemistry stack dependency-gated. |
| D-MPNN / Chemprop | Roadmap only; `chemprop` dependency-gated. |
| ChemBERTa | Roadmap only; Transformers/PyTorch/model-artifact gated. |
| MolFormer | Roadmap only; Transformers/PyTorch/model-artifact gated. |
| MoE | Design stub only; no runtime MoE wrapper added. |
| BO / active learning | Stub only; recommendation remains constrained enumeration plus reranking. |

## Files Changed

- `docs/model_architectures/optional_models_status.md`
- `tests/test_optional_model_status.py`
- `docs/agent_reports/20260425_optional_models.md`

## Verification

Passed:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_optional_model_status.py -q
git diff --check
```

Results:

- `tests/test_optional_model_status.py`: 1 passed in 0.02s.
- `git diff --check`: exit 0; PowerShell/Git emitted an unrelated CRLF warning for `tests/test_training.py`.

No dependencies, branches, staged files, commits, remotes, or training wrappers were added by this slice.
