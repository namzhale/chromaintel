# Public Dataset Expansion Summary

Date: 2026-04-25

## Newly Processed Local Sources

| Source | Local output | Rows | Notes |
| --- | --- | ---: | --- |
| Hugging Face ReTiNA | `data/processed/external_retina_hf_full.csv` | 119,039 | Method-conditioned RT rows; RT converted from seconds to minutes; MIT license. |
| METLIN SMRT Figshare | `data/processed/external_metlin_smrt_figshare.csv` | 79,957 | Original auth-free SMRT CSV; InChI converted to SMILES/InChIKey with RDKit; 81 rows rejected. |
| Kaggle METLIN descriptors | `data/processed/external_kaggle_metlin_descriptors.csv` | 77,901 | Descriptor-only Kaggle export aligned to Figshare identities by ordered RT sequence. |
| Kaggle descriptor sidecar | `data/processed/external_kaggle_metlin_descriptors_descriptors.csv` | 77,901 | 124 Kaggle descriptor columns plus `source_record_id`, `inchikey`, and `canonical_smiles`. |

## Important Interpretation

ReTiNA already includes a METLIN-derived method among its 73 LC-MS environments. The METLIN Figshare/Kaggle files should not all be blindly concatenated into one training split without duplicate/source weighting, otherwise the single METLIN method can dominate model fitting.

Recommended next training view:

1. Use ReTiNA as the main method-conditioned expansion source.
2. Use Kaggle descriptor sidecar to enrich METLIN rows where `source_record_id`/InChIKey matches.
3. Keep METLIN Figshare as a separate compound-pretraining/benchmark corpus or downweight it during final method-conditioned training.

## Access Notes

Kaggle CLI/API credentials were not present locally. The provided local file `C:\Users\namzh\Downloads\archive\descriptors.csv` was processed without needing Kaggle auth. The original Figshare CSV was downloaded directly from `https://doi.org/10.6084/m9.figshare.8038913`.

## Verification

- `tests/test_public_data_import.py`: 13 passed.
- ReTiNA full normalization: 119,039 rows.
- METLIN Figshare normalization: 79,957 accepted rows, 81 rejected rows.
- Kaggle descriptor alignment: 77,901 rows matched; descriptor sidecar written.
