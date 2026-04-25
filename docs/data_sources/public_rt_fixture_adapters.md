# Public RT fixture adapters

This slice adds config-first adapters for small, reviewed local tabular exports from PredRet, GMCRT, and MultiConditionRT-style public RT sources.

## Scope

- Adapter module: `app/adapters/public_rt.py`
- Test fixtures: `tests/fixtures/public_rt/`
- Ingestion reports: `reports/ingestion/*_fixture_ingestion.md`
- Network policy: no live bulk downloads; inputs must be local CSV/TSV/JSON/XLSX files that have already passed license and provenance review.

## Adapter contract

Each source is represented by a `PublicRTAdapterConfig` with:

- source name
- raw-to-canonical column map
- required raw columns
- provenance URL or reviewed-export marker
- license note
- known source missingness
- default canonical values such as `matrix=reference`, `success_flag=True`, and `ion_mode=unknown`

The loader normalizes rows into `CANONICAL_DATASET_COLUMNS` via the existing `normalize_source_frame` service. It also appends provenance and license notes to every row.

## Current fixture findings

| Source | Rows | Duplicate rows | Main missingness |
| --- | ---: | ---: | --- |
| PredRet | 2 | 0 | MS transitions, peak quality metrics, sample matrix |
| GMCRT | 3 | 1 | method details, MS transitions, peak quality metrics |
| MultiConditionRT | 2 | 0 | mobile phase details, MS transitions, peak quality metrics |

## Operational notes

- Fixtures are deliberately tiny and synthetic/local-review shaped.
- Duplicate reporting uses `compound_name`, `canonical_smiles`, `column_name`, and `rt_min`.
- Reports are Markdown so future agents can diff missingness and duplicate counts before a larger reviewed import.
