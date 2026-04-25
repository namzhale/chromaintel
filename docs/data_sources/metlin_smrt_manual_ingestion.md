# METLIN SMRT manual ingestion

METLIN SMRT remains a manual-ingestion source. Do not bulk-download or redistribute raw METLIN SMRT tables until the publication, dataset, and any provider terms have been reviewed for the exact export being used.

## Existing adapter

`app/adapters/metlin_smrt.py` currently loads an authorized offline export with the legacy `load_table` and `validate_records` contract. It does not fetch data, scrape pages, or expand source-specific mappings.

## Manual workflow

1. Review the source publication, dataset page, and redistribution terms for the exact export.
2. Save only an approved local export in a reviewed data location.
3. Preserve source URL, citation, access date, license note, and export filename in ingestion notes.
4. Normalize into the canonical LC-MS/MS schema before merging with model training data.
5. Generate an ingestion report covering row count, duplicate count, missingness, source limitations, and license status.

## Minimum fields for a useful local export

- `compound_name`
- `smiles` or `canonical_smiles`
- `rt_min`
- condition or method identifier when available
- column and mobile phase metadata when available

## Expected missingness

METLIN SMRT-style exports may omit bioanalytical matrix, sample preparation, peak quality metrics, and MS transition details. Treat those omissions as known source limitations, not as inferred experimental negatives.
