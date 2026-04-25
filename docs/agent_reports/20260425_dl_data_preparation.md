# Agent DL Data Preparation Report

Date: 2026-04-25

## Existing implementation audit

- `app/models/graph_optional.py` already had dependency-safe graph support: backend detection, RDKit molecule featurization, graph family metadata, skip reports, and a tiny optional PyTorch CPU smoke path. It does not train graph models.
- `app/models/transformer_embeddings.py` already had dependency-safe transformer support: local Hugging Face availability checks, cached embedding loading, sidecar metadata, and joins between cached embeddings and method features. It does not download, tokenize, encode live, or fine-tune.
- `requirements.txt` still has no mandatory PyTorch, PyG, DGL, Chemprop, Transformers, or Hugging Face model dependency.
- Existing processed sources use a compatible canonical schema: `master_dataset.csv`, `model_matrix.csv`, ReTiNA, METLIN SMRT Figshare, and Kaggle METLIN descriptor-aligned files expose `canonical_smiles`, `inchikey`, `source_dataset`, method fields, and `rt_min`.

## Implemented

- Added `scripts/prepare_dl_datasets.py`, a lightweight manifest builder for graph and SMILES-transformer experiments.
- The script writes:
  - `data/processed/dl/graph_manifest.csv`
  - `data/processed/dl/smiles_transformer_manifest.csv`
  - `reports/benchmarks/dl_dataset_prep_report.json`
- Both manifests include `canonical_smiles`, `inchikey`, `source_dataset`, `source_record_id`, `compound_name`, LC/MS method fields, `matrix`, `rt_min`, and `split`.
- SMILES are validated and canonicalized through the existing RDKit-backed descriptor utility. Invalid or missing SMILES rows are filtered.
- Existing split labels are preserved from `split`, `split_label`, or `data_split`; otherwise splits are generated deterministically by stable hash over compound identity and seed.
- `--max-rows` caps rows before canonicalization so smoke runs do not process the full large local datasets.
- Added `.gitignore` entries for generated DL manifests and the generated prep report.
- Added tests for invalid SMILES filtering, output columns, source split preservation, and generated split reproducibility.

## Still optional

- No graph training dataset object, PyTorch DataLoader, PyG/DGL conversion, Chemprop wrapper, GPU path, or checkpointing was added.
- No live SMILES transformer encoding, tokenizer loading, model download, embedding generation, or fine-tuning was added.
- No changes were made to the active tabular training assembly in `app/models/training.py`.
- Generated CSV/JSON outputs are local artifacts and are ignored to avoid committing large data files.

## Verification results

- Red TDD run: `.\.venv\Scripts\python.exe -m pytest tests\test_prepare_dl_datasets.py -q` failed with `ModuleNotFoundError: No module named 'scripts.prepare_dl_datasets'`.
- Focused green run after implementation: `.\.venv\Scripts\python.exe -m pytest tests\test_prepare_dl_datasets.py -q` passed with `3 passed in 0.58s`.
- Final targeted optional-DL suite: `.\.venv\Scripts\python.exe -m pytest tests\test_prepare_dl_datasets.py tests\test_graph_optional.py tests\test_transformer_embeddings.py -q` passed with `14 passed in 0.66s`.
- Smoke command: `.\.venv\Scripts\python.exe scripts\prepare_dl_datasets.py --max-rows 25` completed with:
  - input rows: 307001
  - valid rows: 25
  - filtered invalid/missing SMILES: 0
  - split strategy: deterministic_hash
  - graph manifest: `data/processed/dl/graph_manifest.csv`
  - SMILES transformer manifest: `data/processed/dl/smiles_transformer_manifest.csv`
  - report: `reports/benchmarks/dl_dataset_prep_report.json`
- Smoke dependency status in the generated report:
  - RDKit available
  - torch, PyG, DGL, Chemprop unavailable
  - Transformers unavailable
  - no model download attempted

## Files changed

- `.gitignore`
- `scripts/prepare_dl_datasets.py`
- `tests/test_prepare_dl_datasets.py`
- `docs/model_architectures/graph_models.md`
- `docs/model_architectures/transformer_embeddings.md`
- `docs/agent_reports/20260425_dl_data_preparation.md`
