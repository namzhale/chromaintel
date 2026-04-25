# Dataset Assembly Summary

- Source profile: `expanded_ml`
- Primary source: `mock training records` (12 rows)
- Additional target-row sources before canonical deduplication: 214,069 rows
- Master rows after canonical merge/deduplication: 213,941
- Model matrix shape: 213,941 rows x 43 columns
- Local DL manifests prepared from the deduplicated master table: 213,941 valid rows

## Row Counts By Source

| Status | Source | Rows | Path | Policy |
| --- | --- | ---: | --- | --- |
| included | mock training records | 12 | `data/mock_training_records.csv` | primary local training seed |
| included | ReTiNA Hugging Face full | 119,039 | `data/processed/external_retina_hf_full.csv` | target rows |
| included | MCMRT supplement | 10,073 | `data/processed/external_mcmrt_supplement.csv` | target rows |
| included | RepoRT bulk 5k | 5,000 | `data/processed/external_report_bulk_5k.csv` | target rows |
| included | METLIN Figshare canonical rows | 79,957 | `data/processed/external_metlin_smrt_figshare.csv` | target rows |
| excluded | Kaggle descriptor-aligned canonical export | 77,901 | `data/processed/external_kaggle_metlin_descriptors.csv` | excluded from target rows to prevent METLIN double-counting |
| sidecar | Kaggle METLIN descriptor sidecar | 77,901 | `data/processed/external_kaggle_metlin_descriptors_descriptors.csv` | retained as descriptor metadata; not target rows |

## Excluded duplicate/sidecar policy

- The `expanded_ml` profile uses ReTiNA, MCMRT, RepoRT, and METLIN Figshare canonical rows.
- The Kaggle METLIN canonical CSV is aligned to the same METLIN row family and is intentionally excluded from target-row assembly.
- The Kaggle descriptor sidecar remains available for future descriptor joins, but it is not appended as new RT target rows.
- Large generated CSV and model artifacts are local reproducible outputs; do not stage them unless an artifact or LFS policy is introduced.
