# Local Artifact Manifest

Generated on 2026-04-25 for the expanded ChromaIntel data/model slice.

## Current local generated artifacts

| Artifact | Approx. size | Status | Notes |
| --- | ---: | --- | --- |
| `data/processed/master_dataset.csv` | 151 MB | local generated artifact | 213,941 canonical rows after expanded merge/deduplication |
| `data/processed/model_matrix.csv` | 90 MB | local generated artifact | 213,941 rows x 43 feature/target columns |
| `data/processed/models/trained_forward_bundle.joblib` | 188 MB | local generated artifact | quick-mode forward bundle trained on the expanded matrix |
| `data/processed/dl/graph_manifest.csv` | 94 MB | ignored local generated artifact | graph/DL preparation manifest |
| `data/processed/dl/smiles_transformer_manifest.csv` | 108 MB | ignored local generated artifact | SMILES transformer preparation manifest |

## Policy

These artifacts are reproducible and should not be committed to normal git history. See `docs/artifact_policy.md` for rebuild commands and future artifact-store options.

## Current source composition

- ReTiNA Hugging Face full: 119,039 rows
- METLIN SMRT Figshare canonical: 79,957 rows
- MCMRT supplement: 10,073 rows
- RepoRT bulk 5k: 5,000 rows
- mock/internal seed: 12 rows
- Kaggle/METLIN descriptor sidecar: 77,901 descriptor rows, not appended as RT targets
