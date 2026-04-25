# Public Parser Strategy

## Current ingestion baseline

The MVP already has a bounded RepoRT importer in `scripts/fetch_public_datasets.py`.
It downloads the four small `processed_data/<dataset_id>` TSVs needed for one RepoRT
dataset, writes raw provenance copies under `data/raw/public_sources`, and emits a
canonical sample under `data/processed`. RepoRT rows are useful RT/method-condition
supervision only: MS transitions, sample matrix, peak metrics, and manual quality
labels remain intentionally null.

The adapters are offline-first. MassBank, MoNA, ChEMBL, and METLIN SMRT loaders
expect local files or authorized exports rather than private scraping or broad
network harvests.

## Recommended expansion order

1. **RepoRT selected datasets**
   - Keep as the primary public RT source because processed TSVs are small,
     structured, and carry clear CC-BY-SA-4.0 provenance in the repo inventory.
   - Expand by explicit dataset IDs, not by cloning or downloading the full
     repository blindly.

2. **Metabolomics Workbench RT/manual exports**
   - Use the public RT search and REST documentation to identify studies, then
     import small, reviewed CSV/TSV/mwTab-derived tables locally.
   - Treat study-level assay tables as heterogeneous. Require compound name and
     RT after alias normalization, and preserve source URL, study ID, and license
     note in `notes`.

3. **MCMRT / Scientific Data 2024**
   - High-value candidate for method-transfer evaluation because the same
     compounds appear across many reversed-phase LC methods and replicates.
   - Do not add an automated downloader until the Science Data Bank package
     license and table layout are reviewed. Prefer a local supplementary-table
     import first.

4. **MassBank, MoNA, and GNPS spectral libraries**
   - Use as MS/MS metadata enrichments rather than primary RT training data.
   - Import only small, license-checked local exports. Record-level licenses can
     vary, and public library downloads can be large.

5. **PredRet**
   - Prefer RepoRT-hosted copies where available. Direct PredRet exports should
     remain a manual/local import until export licensing and redistribution terms
     are confirmed.

## Parser contract for local public exports

The patched importer accepts reviewed local CSV, TSV, JSON/JSONL, or Excel files:

```powershell
.venv\Scripts\python.exe scripts\fetch_public_datasets.py `
  --local-export data\raw\public_sources\my_reviewed_rt_table.tsv `
  --source-name "MetabolomicsWorkbench:STxxxxxx" `
  --source-url "https://www.metabolomicsworkbench.org/..." `
  --license-note "public repository; study license reviewed YYYY-MM-DD" `
  --rows 50 `
  --output-name mw_stxxxxxx
```

After existing alias normalization, a public RT import must have populated
`compound_name` and `rt_min`. Optional fields should map into the canonical schema
when present: SMILES/InChIKey, column, mobile phases, pH, temperature, flow,
gradient, ion mode, precursor/product m/z, matrix, and source record IDs.

## Guardrails

- No private scraping, authentication bypass, or vendor-library ingestion.
- No bulk downloads without an explicit size/license review.
- Keep raw copies and processed outputs separate.
- Keep `quality_score` null unless the source has measured or manually labeled
  quality outcomes.
- Put source URL, license/access note, and source file name in every imported row's
  `notes` field.
