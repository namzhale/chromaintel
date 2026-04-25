# Optional Model Architectures Status

Date: 2026-04-25

This note records which optional model families are available in the current ChromaIntel MVP and which are dependency-gated future work. It is intentionally documentation-only: `app/models/training.py` already owns the trainable wrappers, and no duplicate wrappers should be added until a dependency is deliberately introduced and tested.

## Current Runtime Baseline

The checked-in training path is a CPU-first tabular ensemble in `app/models/training.py`.

| Family | Runtime status | Dependency status | Current implementation |
| --- | --- | --- | --- |
| Ridge | Active | `scikit-learn` pinned | Candidate model in `_candidate_models`. |
| RandomForest | Active | `scikit-learn` pinned | Candidate model in `_candidate_models`. |
| ExtraTrees | Active | `scikit-learn` pinned | Candidate model in `_candidate_models`. |
| HistGradientBoosting | Active | `scikit-learn` pinned | Candidate model in `_candidate_models`. |
| XGBoost | Active when import succeeds | `xgboost` pinned | Dependency-gated candidate in `_optional_boosting_models`. |
| CatBoost | Active when import succeeds | `catboost` pinned | Dependency-gated candidate in `_optional_boosting_models`. |

The existing optional-wrapper pattern is local import plus graceful skip. New optional families should follow that pattern only after their dependencies are intentionally added.

## Dependency-Gated Optional Families

| Family | Status | Required dependency gate | Notes for next implementation |
| --- | --- | --- | --- |
| LightGBM | Not implemented | `lightgbm` is not in `requirements.txt` | Best next CPU tabular candidate. Add beside XGBoost/CatBoost only after dependency approval; avoid a separate model wrapper module. |
| GCN | Roadmap only | PyTorch plus PyG or DGL are not in `requirements.txt` | Needs graph featurization, scaffold/group splits, and enough internal rows to justify graph learning. |
| GAT | Roadmap only | PyTorch plus PyG or DGL are not in `requirements.txt` | Same gate as GCN; should share graph dataset plumbing rather than create a parallel loader. |
| MPNN | Roadmap only | PyTorch plus graph chemistry stack are not in `requirements.txt` | Treat as molecular encoder research, not replacement for LC method features. |
| D-MPNN / Chemprop | Roadmap only | `chemprop` is not in `requirements.txt` | Candidate for compound encoder plus LC tabular side features once data volume and labels support it. |
| ChemBERTa | Roadmap only for live encoder; frozen cached embeddings optional | `transformers`, `torch`, and tokenizer/model artifacts are not in `requirements.txt` | `app/models/transformer_embeddings.py` can detect local encoder availability and join precomputed offline embeddings. Fine-tuning remains out of scope. |
| MolFormer | Roadmap only for live encoder; frozen cached embeddings optional | `transformers`/MolFormer-compatible stack and model artifacts are not in `requirements.txt` | Same gate as ChemBERTa; current support is cache/provenance plumbing, not downloads or training. |
| Mixture of Experts (MoE) | Design stub only | No new package is strictly required for a simple router, but no MoE runtime exists | Start as a documented routing strategy by column/source/assay family; do not add neural MoE dependencies yet. |
| Bayesian optimization / active learning | Stub only | `scikit-optimize`, `optuna`, `botorch`, or equivalent are not in `requirements.txt` | Current recommendation path is constrained enumeration plus reranking. Add BO only after objectives, constraints, and lab feedback labels are stable. |

## Implementation Rules

1. Do not add duplicate model wrappers outside `app/models/training.py` for tabular candidates.
2. Keep optional models dependency-gated with local imports and graceful skip behavior.
3. Do not add PyTorch, Transformers, PyG/DGL, Chemprop, LightGBM, BoTorch, Optuna, or scikit-optimize as a side effect of documentation work.
4. Keep graph and transformer architectures behind explicit experiment flags and provenance records when implemented.
5. Validate new model families with grouped CV, source-family holdout, retention-order diagnostics, uncertainty metadata, and applicability-domain reporting before presenting them as available.

## Frozen Transformer Embedding Baseline

`app/models/transformer_embeddings.py` now provides dependency-gated support for optional SMILES transformer embeddings without adding `transformers` or `torch` to `requirements.txt`.

- Live ChemBERTa, MolFormer, and generic Hugging Face encoders are availability-checked with local imports and `local_files_only=True` by default.
- Offline runs should use precomputed embedding caches with explicit sidecar metadata.
- Tests use mocked cached embeddings under `tests/fixtures/embeddings/` and do not download model weights.
- The helper joins cached molecular embedding columns to existing LC/MS method features and records skip/fill metadata for missing cache rows.

## Recommended Order

1. LightGBM as the next optional CPU tabular backend, if dependency policy allows.
2. Frozen ChemBERTa or MolFormer embeddings as feature columns, not end-to-end fine-tuning.
3. Chemprop/D-MPNN with LC method side features once internal historical rows are large enough.
4. Simple MoE/router over existing trained candidates by method/source/assay family.
5. Bayesian optimization or active learning around the recommendation scorer after wet-lab feedback labels exist.
