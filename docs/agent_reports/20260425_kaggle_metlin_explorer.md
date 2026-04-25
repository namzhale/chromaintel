# Kaggle METLIN dataset explorer

Audit date: 2026-04-25

## Existing implementation audit

- Public ingestion is intentionally offline-first. `scripts/fetch_public_datasets.py` supports live RepoRT samples/bulk, MCMRT workbook normalization, and a generic `--local-export` path for reviewed CSV/TSV/JSON/XLSX files.
- The generic local importer normalizes through `app.services.dataset_assembly.normalize_source_frame`, writes `data/processed/external_<name>_sample.csv`, and appends `source_url`, `license`, and `source_file` to row notes.
- `app/adapters/public_rt.py` adds config-first fixture adapters for PredRet, GMCRT, and MultiConditionRT-style reviewed local exports. Tests cover CSV/TSV/JSONL local imports and no Kaggle/Figshare credentials are required.
- `docs/data_sources/metlin_smrt_manual_ingestion.md` already marks METLIN SMRT as manual/offline and warns against bulk download/redistribution until source terms are reviewed.
- Current gap: the original Figshare `SMRT_dataset.csv` has only `pubchem`, `rt`, and `inchi`; the current generic local importer requires populated `compound_name` and `rt_min`, so the raw Figshare CSV does not ingest directly. A METLIN-specific preprocessor is needed to convert InChI to SMILES/InChIKey and map PubChem IDs before calling the canonical normalizer.

## Access status

- Local Kaggle CLI/package status: unavailable. `kaggle` and `kagglehub` are not installed in `.\.venv`, no `kaggle.exe` was found, and no local Kaggle credentials were detected in env vars or common config paths.
- Kaggle public metadata is reachable without local credentials via unauthenticated HTTP metadata endpoints. Download/list-file endpoints tested without credentials returned 404, so local tests should not depend on Kaggle auth.
- Kaggle dataset inspected: `satwikmurarka/meltin-retention-times-with-molecular-descriptors`, title `LCMS Retention Time Dataset`, version 1, updated `2023-04-26T08:38:40.723Z`, public, license `Attribution 4.0 International (CC BY 4.0)`. Public metadata reports compressed/list size about `48,451,281` bytes in `datasets/list` and `134,243,919` bytes in `datasets/view`.
- Kaggle description says the dataset contains RP HPLC-MS retention time target `rt` in seconds and RDKit-derived 2D molecular descriptors from molecule SMILES. It also says the original Figshare dataset had 80,038 molecules, with molecules below 2 minutes RT and molecules whose RDKit descriptors could not be obtained removed.
- Kaggle unauthenticated metadata did not expose file names, exact columns, or exact row count. Likely Kaggle shape: one or more tabular files with `rt` target seconds, SMILES/structure identifier, and RDKit 2D descriptor columns; exact file/column list needs either Kaggle credentials/CLI or a user-supplied local Kaggle export.
- Original Figshare DOI `10.6084/m9.figshare.8038913` is reachable without auth. Figshare metadata reports Apache 2.0 license, version 1, published `2019-12-19T20:26:56Z`, modified `2023-05-30T18:04:59Z`, total size `1,007,002,981` bytes.
- Figshare file list:
  - `SMRT_ECFP_1024_Fingerprints.txt`, 82,751,894 bytes
  - `SMRT_molecular_descriptors.zip`, 521,225,537 bytes
  - `SMRT_dataset.sdf`, 376,339,847 bytes
  - `SMRT_dataset.csv`, 12,607,820 bytes
  - `Deep learning model and results.zip`, 14,077,883 bytes
- Original Figshare `SMRT_dataset.csv` is semicolon-delimited with 80,038 rows and 3 columns: `pubchem`, `rt`, `inchi`. `rt` range in the downloaded CSV is 0.3 to 1471.7 seconds; all three columns are populated.
- In this local RDKit environment, the Figshare CSV has 2,041 rows with `rt < 120` seconds, 77,997 rows with `rt >= 120` seconds, and 81 InChI-to-molecule failures. Applying both `rt >= 120` and local RDKit InChI conversion success gives 77,917 rows. Treat this as a local reproducibility estimate, not a verified Kaggle row count.

Sources checked: Kaggle dataset page/API (`https://www.kaggle.com/datasets/satwikmurarka/meltin-retention-times-with-molecular-descriptors`), Figshare page/API (`https://figshare.com/articles/dataset/The_METLIN_small_molecule_dataset_for_machine_learning-based_retention_time_prediction/8038913`, `https://api.figshare.com/v2/articles/8038913`), and Nature Communications article (`https://www.nature.com/articles/s41467-019-13680-7`).

## Mapping proposal

For a Kaggle local export:

| Source field | Canonical field | Notes |
| --- | --- | --- |
| `rt` | `rt_min` | Convert seconds to minutes if canonical `rt_min` is strict minutes. Current code aliases `rt` directly, so a METLIN adapter should explicitly divide by 60. |
| `SMILES`/`smiles` | `smiles` and derived `canonical_smiles` | Use existing RDKit canonicalization in `normalize_source_frame`. |
| `InChIKey`/derived InChIKey | `inchikey` | Preserve if supplied; otherwise derive from InChI/SMILES. |
| `pubchem`/CID | `source_record_id` | Use `PubChem:<cid>` or raw CID with provenance note. |
| RDKit descriptor columns | feature-only sidecar or `notes` summary | Do not force descriptor columns into `CANONICAL_DATASET_COLUMNS`; keep as optional modeling features joined by `source_record_id`/InChIKey. |
| missing method metadata | canonical nullable fields | Fill constants below and leave unavailable fields null. |

For the original Figshare CSV:

| Source field | Canonical field | Notes |
| --- | --- | --- |
| `pubchem` | `source_record_id` | Prefix with `PubChem:` for clarity. |
| `rt` | `rt_min` | Divide seconds by 60. Preserve raw seconds in notes if useful. |
| `inchi` | derive `smiles`, `canonical_smiles`, `inchikey` | RDKit can convert most rows locally; rows that fail conversion should be quarantined with a rejection report. |
| absent compound name | `compound_name` | Use a stable placeholder such as `PubChem CID <id>` unless PubChem enrichment is explicitly enabled. |
| absent chromatography constants | `column_name`, `column_chemistry`, `stationary_phase_type`, `mobile_phase_a`, `mobile_phase_b`, `gradient_profile`, `flow_ml_min`, `ion_mode`, `matrix`, `success_flag` | Populate from the article where known: Zorbax Extend-C18 2.1 x 50 mm, 1.8 um; reversed phase/C18; A water + 0.1% formic acid; B acetonitrile + 0.1% formic acid; gradient 5% B 3 min, 50% B over 2 min, 85% B over 15 min, held 3 min; flow 0.1 mL/min; ion mode both; matrix reference; success true. |

Recommended fallback command shape after creating a reviewed local export/preprocessed CSV:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_public_datasets.py `
  --local-export data\raw\public_sources\metlin_smrt_reviewed.csv `
  --source-name METLIN_SMRT `
  --source-url https://doi.org/10.6084/m9.figshare.8038913 `
  --license-note "Apache-2.0 source; Kaggle derivative CC-BY-4.0 if using Kaggle export; reviewed local export" `
  --output-name metlin_smrt
```

## Ingestion risks

- License mismatch: original Figshare is Apache 2.0, while the Kaggle derivative reports CC BY 4.0. Preserve both provenance chains and do not merge raw Kaggle descriptors without recording derivative terms.
- Unit risk: Kaggle/Figshare `rt` is seconds; canonical schema says `rt_min`. Current generic aliasing would keep seconds as minutes unless a source-specific conversion is added.
- Missing identity/name: original Figshare CSV lacks compound names and SMILES. PubChem enrichment would add names but introduces network dependency and rate/availability risk; an auth-free test path should use `PubChem CID <id>` placeholders and RDKit-derived SMILES/InChIKey.
- Descriptor sidecar risk: RDKit/Kaggle descriptor columns are not canonical experimental fields. Keep them separate from canonical ingestion unless a modeling feature table is intentionally added.
- Failed structures: local RDKit failed on 81 original Figshare InChIs; reject/quarantine rather than silently dropping without a report.
- Non-retained molecules: Kaggle removed low-RT/non-retained rows, while original Figshare retains them. Decide whether to keep all 80,038 for traceability or filter `rt < 120` seconds for model training.
- Method metadata is article-level, not row-level. Treat it as a constant source-method annotation and note expected RT variability from batch acquisition.
- Kaggle CLI and credentials are absent locally; CI/tests should use tiny local fixtures or a user-provided local export, not Kaggle network/auth.

## Exact commands/results

```powershell
git status --short
```

Result: no output; worktree was clean before this report was written.

```powershell
.\.venv\Scripts\python.exe -V
```

Result: `Python 3.10.11`

```powershell
.\.venv\Scripts\python.exe -m pip show kaggle kagglehub | Select-String -Pattern 'Name:|Version:|WARNING'
```

Result: `WARNING: Package(s) not found: kaggle, kagglehub`

```powershell
Get-Command kaggle -ErrorAction SilentlyContinue | Select-Object Source,Version
Test-Path .\.venv\Scripts\kaggle.exe
```

Result: `False` for `.venv\Scripts\kaggle.exe`; no `kaggle` command object printed.

```powershell
$paths = @($env:KAGGLE_CONFIG_DIR, (Join-Path $env:USERPROFILE '.kaggle\kaggle.json'), (Join-Path (Get-Location) '.kaggle\kaggle.json')) | Where-Object { $_ }
foreach ($p in $paths) { [pscustomobject]@{ Path=$p; Exists=(Test-Path $p) } }
[pscustomobject]@{ Path='env:KAGGLE_USERNAME'; Exists=[bool]$env:KAGGLE_USERNAME }
[pscustomobject]@{ Path='env:KAGGLE_KEY'; Exists=[bool]$env:KAGGLE_KEY }
```

Result: `C:\Users\namzh\.kaggle\kaggle.json` false, repo `.kaggle\kaggle.json` false, `KAGGLE_USERNAME` false, `KAGGLE_KEY` false.

```powershell
Invoke-RestMethod https://www.kaggle.com/api/v1/datasets/metadata/satwikmurarka/meltin-retention-times-with-molecular-descriptors
```

Result summary: dataset id `3186598`, owner `satwikmurarka`, title `LCMS Retention Time Dataset`, expected update frequency `never`, license `Attribution 4.0 International (CC BY 4.0)`, description says `rt` is seconds and RDKit 2D descriptors were calculated from SMILES; `data` array was empty.

```powershell
Invoke-RestMethod https://www.kaggle.com/api/v1/datasets/view/satwikmurarka/meltin-retention-times-with-molecular-descriptors
Invoke-RestMethod https://www.kaggle.com/api/v1/datasets/list?search=meltin-retention-times-with-molecular-descriptors
```

Result summary: public metadata returned successfully. `datasets/view` reported `totalBytes=134243919`; `datasets/list` reported `totalBytes=48451281`; neither exposed usable file/column metadata.

```powershell
Invoke-RestMethod https://www.kaggle.com/api/v1/datasets/list-files?owner_slug=satwikmurarka&dataset_slug=meltin-retention-times-with-molecular-descriptors
Invoke-WebRequest -Method Head https://www.kaggle.com/api/v1/datasets/download/satwikmurarka/meltin-retention-times-with-molecular-descriptors
```

Result: both unauthenticated file/download probes returned `404 Not Found`.

```powershell
Invoke-RestMethod https://api.figshare.com/v2/articles/8038913
```

Result summary: title `The METLIN small molecule dataset for machine learning-based retention time prediction`, DOI `10.6084/m9.figshare.8038913.v1`, license `Apache 2.0`, published `2019-12-19T20:26:56Z`, modified `2023-05-30T18:04:59Z`, size `1007002981`.

```powershell
Invoke-RestMethod https://api.figshare.com/v2/articles/8038913/files
```

Result: five files listed: `SMRT_ECFP_1024_Fingerprints.txt`, `SMRT_molecular_descriptors.zip`, `SMRT_dataset.sdf`, `SMRT_dataset.csv`, and `Deep learning model and results.zip`.

```powershell
Invoke-WebRequest -Uri https://ndownloader.figshare.com/files/18130628 -OutFile $env:TEMP\SMRT_dataset.csv
Get-Content $env:TEMP\SMRT_dataset.csv -TotalCount 5
```

Result summary: downloaded 12,607,820-byte CSV. First line was `"pubchem";"rt";"inchi"`, confirming semicolon delimiter.

```powershell
@'
import os
import pandas as pd
path = os.path.join(os.environ['TEMP'], 'SMRT_dataset.csv')
df = pd.read_csv(path, sep=';')
print('rows', len(df))
print('columns', len(df.columns))
print(df.columns.tolist())
print('rt_min_seconds', df['rt'].min(), df['rt'].max())
print(df.notna().sum().to_string())
'@ | .\.venv\Scripts\python.exe -
```

Result: `rows 80038`, `columns 3`, columns `['pubchem', 'rt', 'inchi']`, RT range `0.3 1471.7`, all columns had 80,038 non-null values.

```powershell
@'
import os
import pandas as pd
from rdkit import Chem, RDLogger
RDLogger.DisableLog('rdApp.*')
path = os.path.join(os.environ['TEMP'], 'SMRT_dataset.csv')
df = pd.read_csv(path, sep=';')
ok = [Chem.MolFromInchi(inchi, sanitize=True, removeHs=True) is not None for inchi in df['inchi']]
df['rdkit_ok'] = ok
print('inchi_to_mol_failed', int((~df['rdkit_ok']).sum()))
print('retained_rt_ge_120s', int((df['rt'] >= 120).sum()))
print('rt_ge_120_and_rdkit_ok', int(((df['rt'] >= 120) & df['rdkit_ok']).sum()))
'@ | .\.venv\Scripts\python.exe -
```

Result: `inchi_to_mol_failed 81`, `retained_rt_ge_120s 77997`, `rt_ge_120_and_rdkit_ok 77917`.

```powershell
@'
from scripts.fetch_public_datasets import import_local_public_export
import os
path = os.path.join(os.environ['TEMP'], 'SMRT_dataset.csv')
try:
    out = import_local_public_export(path, 'METLIN_SMRT', 'https://doi.org/10.6084/m9.figshare.8038913', 'Apache-2.0; audit only', rows=10)
    print('WROTE', out)
except Exception as exc:
    print(type(exc).__name__ + ': ' + str(exc))
'@ | .\.venv\Scripts\python.exe -
```

Result: `ValueError: C:\Users\namzh\AppData\Local\Temp\SMRT_dataset.csv does not contain usable public RT rows after normalization; missing populated columns: ['compound_name']`.
