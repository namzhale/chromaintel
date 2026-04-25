# ML Data Preparation Source Summary

Generated for the `expanded_ml` source selection policy on 2026-04-25.

## Row Counts By Source

| Status | Source | Rows | Path | Policy |
| --- | --- | ---: | --- | --- |
| included | mock training records | 12 | `data/mock_training_records.csv` | primary local training seed |
| included | ReTiNA Hugging Face full | 119039 | `data/processed/external_retina_hf_full.csv` | target rows |
| included | MCMRT supplement | 10073 | `data/processed/external_mcmrt_supplement.csv` | target rows |
| included | RepoRT bulk 5k | 5000 | `data/processed/external_report_bulk_5k.csv` | target rows |
| included | METLIN Figshare canonical rows | 79957 | `data/processed/external_metlin_smrt_figshare.csv` | target rows |
| excluded | Kaggle descriptor-aligned canonical export | 77901 | `data/processed/external_kaggle_metlin_descriptors.csv` | excluded from target rows to prevent METLIN double-counting |
| sidecar | Kaggle METLIN descriptor sidecar | 77901 | `data/processed/external_kaggle_metlin_descriptors_descriptors.csv` | retained as sidecar metadata; not target rows |

Expected expanded target-row input count before canonical deduplication: 214081 rows.

## Excluded Duplicate/Sidecar Policy

- The `expanded_ml` profile uses ReTiNA, MCMRT, RepoRT, and METLIN Figshare canonical rows.
- The Kaggle METLIN canonical CSV is descriptor-aligned to the same METLIN row family and is excluded from target-row assembly.
- The Kaggle descriptor sidecar remains available as metadata for future descriptor joins, but it is not appended as additional target rows.
