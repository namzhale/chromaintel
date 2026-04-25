# Implementation Report: Data Adapters, Evaluation Matrix, And Optional Neural Paths

## Executive Summary

This autonomous slice extends ChromaIntel beyond the existing RepoRT/MCMRT tabular baseline by adding canonical registry helpers, public RT fixture adapters, offline compound identity resolution, method/column-family evaluation, a unified benchmark matrix, and dependency-gated neural branches for graph models and molecular transformer embeddings.

The implementation deliberately avoids mandatory live downloads, GPU dependencies, or duplicate CLIs. New public-data and neural paths are fixture/manual-ingestion first, so they are safe for local development and CI.

## What Was Implemented

- Canonical registry schema helpers and documentation.
- `method_hash`, duplicate-key policy, source-quality scoring, and canonical validation helpers.
- Public RT fixture adapters for PredRet-style, GMCRT-style, and MultiConditionRT-style tables.
- METLIN SMRT manual ingestion documentation.
- Offline compound identity resolver with confidence labels and ambiguous/unresolved reports.
- Method-holdout and column-family-holdout diagnostics in the training pipeline.
- Spearman and normalized MAE by runtime in evaluation outputs.
- Unified benchmark outputs: `model_benchmark_matrix.csv`, `.md`, `.json`.
- Optional graph model support stubs for GCN, GAT, MPNN, D-MPNN/Chemprop-style.
- Optional cached SMILES transformer embedding support for ChemBERTa, MolFormer, and generic Hugging Face encoders.

## Dataset Adapters Added

- `app/adapters/public_rt.py`
- Fixtures under `tests/fixtures/public_rt/`
- Ingestion reports under `reports/ingestion/`
- Documentation under `docs/data_sources/`

These adapters normalize reviewed local exports into the existing canonical nullable schema. No live bulk download is required or run in tests.

## Data Row Counts

Current checked-in full training matrix remains:

- Master rows: 15,052
- Model rows: 15,052
- Compounds: 3,945
- Main source families: RepoRT, MCMRT, internal/mock, METLIN_SMRT placeholder rows

Fixture adapters add tested ingestion paths, not new production-scale rows, because METLIN SMRT and other large resources require reviewed local download/license handling.

## Model Benchmark Matrix

The benchmark matrix is generated from `reports/evaluation_matrix.csv` and written to:

- `reports/model_benchmark_matrix.csv`
- `reports/model_benchmark_matrix.md`
- `reports/model_benchmark_matrix.json`

It includes model family, feature set, target, split, holdout key, MAE, RMSE, R2, Spearman, normalized MAE runtime percent, and row counts.

Current full core run highlights:

- Final grouped holdout best RT MAE: `extra_trees`, 1.861 min.
- Final grouped holdout best RT R2: `extra_trees`, 0.920.
- Final grouped holdout best RT Spearman: `extra_trees`, 0.950.
- Final grouped holdout normalized MAE: `extra_trees`, 6.285% of mean runtime.

## Best Model By Split

The current best RT model from the regenerated full training artifact remains `extra_trees`.

Reported split families now include:

- final grouped holdout
- GroupKFold by compound identity
- source-family holdout
- method holdout
- column-family holdout

Scaffold split is not yet implemented in this slice; it remains a next-step validation mode.

## Morgan vs Core

The `--feature-set morgan` path exists and is tested. A full large-matrix Morgan benchmark remains a follow-up because it creates a much wider feature matrix and can be slow on the current laptop workflow and may generate a large binary artifact. The benchmark matrix currently labels the regenerated default model as `core`.

## Graph And Transformer Status

Graph models:

- Optional smoke module: `app/models/graph_optional.py`
- Docs: `docs/model_architectures/graph_models.md`
- Benchmark/skip report: `reports/benchmarks/graph_models.csv`
- Current status: RDKit graph featurization works; PyTorch/PyG/DGL/Chemprop training is dependency-gated.

Transformer embeddings:

- Optional cache module: `app/models/transformer_embeddings.py`
- Docs: `docs/model_architectures/transformer_embeddings.md`
- Benchmark/skip report: `reports/benchmarks/transformer_embeddings.csv`
- Current status: cached embeddings can be joined to method features offline; live ChemBERTa/MolFormer encoding is dependency-gated and local-files-only by default.

## Recommendation Engine Changes

This slice builds on the previous JSON-configured recommendation search space. No duplicate recommender was added. Optional graph/transformer outputs are documented as future ensemble inputs and are not yet used in candidate ranking.

## Validation And Reporting Changes

- Added canonical schema tests.
- Added public RT adapter fixture tests.
- Added offline compound identity tests.
- Added method/column holdout tests.
- Added optional graph/transformer offline tests.
- Added benchmark matrix generation tests.

## Known Limitations

- No new large public RT source was bulk-imported in this slice; METLIN SMRT remains manual-reviewed ingestion.
- Public datasets still lack robust peak-quality labels for bioanalytical acceptance decisions.
- Graph and transformer paths are smoke/embedding infrastructure, not full neural training runs yet.
- Scaffold split and full Morgan-vs-core large benchmark remain open follow-ups.

## Next Autonomous Slice

1. Run reviewed METLIN SMRT local import when the raw file is available.
2. Add scaffold split and time-based internal split once lab timestamps exist.
3. Run full Morgan comparison artifact.
4. Add graph/transformer training when optional dependencies are installed.
5. Wire evaluation matrix into the Russian PDF dashboard more deeply.
