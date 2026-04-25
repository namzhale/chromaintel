# ReTiNA and Kaggle METLIN SMRT Ingestion

## Existing implementation audit

ChromaIntel already had a single public-source CLI in `scripts/fetch_public_datasets.py` for RepoRT, MCMRT, and reviewed local exports. This slice extends that CLI instead of adding a duplicate downloader.

## ReTiNA

- Source: https://huggingface.co/datasets/natelgrw/ReTiNA
- License: MIT per Hugging Face dataset card.
- Relevant file: `data/retina_dataset.csv`
- Approximate scale: Hugging Face reports the dataset in the 100K to 1M row category; the model card reports about 119K rows.
- Useful fields: SMILES, source, method number, solvents, gradient, column tuple, flow rate, temperature, RT.
- RT units: seconds in the source; converted to minutes for the canonical schema.

Command:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --retina --rows 1000 --output-name retina_hf_1k
```

Full import:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --retina --rows 0 --output-name retina_hf_full
```

Use `--retina-local-csv <path>` if the HF file has already been downloaded.

## Kaggle METLIN SMRT Descriptors

- Source: https://www.kaggle.com/datasets/satwikmurarka/meltin-retention-times-with-molecular-descriptors/data
- Original dataset DOI: https://doi.org/10.6084/m9.figshare.8038913
- License: CC-BY-4.0 per Kaggle data card.
- Useful fields: SMILES and RT, with optional compound names and descriptor columns.
- RT units: seconds by default; converted to minutes for the canonical schema.
- Access caveat: Kaggle programmatic downloads usually require a user API token, so ChromaIntel ingests a reviewed local CSV/TSV export.

Command after downloading the Kaggle file:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --kaggle-metlin-local data\raw\public_sources\kaggle_metlin.csv --output-name kaggle_metlin_smrt
```

If the Kaggle file is the descriptor-only `descriptors.csv` export, provide the original Figshare `SMRT_dataset.csv` as the identity companion:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --kaggle-metlin-local data\raw\public_sources\descriptors.csv --kaggle-metlin-figshare-csv data\raw\public_sources\SMRT_dataset.csv --output-name kaggle_metlin_descriptors
```

The command writes two outputs:

- `external_kaggle_metlin_descriptors.csv`: canonical LC-MS RT rows with PubChem-derived IDs and RDKit-derived structures.
- `external_kaggle_metlin_descriptors_descriptors.csv`: sidecar descriptor table keyed by `source_record_id`, `inchikey`, and `canonical_smiles`.

Because Kaggle CLI/API credentials are not present on the current machine, ChromaIntel also supports the original auth-free Figshare CSV behind the Kaggle derivative:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --metlin-smrt-figshare --rows 0 --output-name metlin_smrt_figshare
```

This path downloads `SMRT_dataset.csv`, derives SMILES/InChIKey from InChI with RDKit, converts RT seconds to minutes, and writes a rejection report for structures RDKit cannot parse.

If the local file already stores RT in minutes:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py --kaggle-metlin-local data\raw\public_sources\kaggle_metlin.csv --kaggle-metlin-rt-units minutes
```

## Mapping Caveats

ReTiNA is more valuable for method-conditioned transfer because it has method metadata and method/scaffold split files. Kaggle METLIN is more valuable for compound-level pretraining because it is a large single-method RP-LC-MS corpus with descriptors but limited method diversity.
