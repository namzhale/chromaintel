# ReTiNA dataset explorer report

Date: 2026-04-25

## Existing implementation audit

- Current public ingestion is local/sample-first. `scripts/fetch_public_datasets.py` supports RepoRT tiny/bulk sample fetches, MCMRT supplement normalization, and `--local-export` for reviewed CSV/TSV/JSON/XLSX files. It avoids direct live ingestion for mixed-license sources.
- `app/adapters/public_rt.py` has config-first local adapters for PredRet, GMCRT, and MultiConditionRT. It renames source columns, applies defaults, calls `normalize_source_frame()`, and writes missingness/duplicate reports.
- Legacy `app/adapters/base.py`, `app/adapters/report.py`, and `app/adapters/metlin_smrt.py` validate an older required-column contract, not the current nullable canonical training schema.
- Canonical training columns are in `app/schemas/dataset.py`: compound identity, source metadata, LC conditions, MS fields, RT/peak metrics, matrix/success/quality, notes, and `missing_fields_count`.
- `normalize_source_frame()` has aliases that help partly with ReTiNA (`rt` -> `rt_min`, `temp` -> `temperature_c`, `source` -> `source_dataset`, `column` -> `column_name`), but a generic import is not safe: ReTiNA `compound` is a SMILES string, while the repo aliases `compound` to `compound_name`. It also does not parse ReTiNA `solvents`, `gradient`, or tuple-encoded `column`, and it does not alias `flow_rate`.

## Dataset files

Hugging Face dataset: `natelgrw/ReTiNA`

- Repository SHA inspected: `5263a29274785296ee8da35fb1c468be18f5ca1f`
- Last modified: `2025-12-25T16:18:30.000Z`
- License tag/card: MIT
- Public/gated status: public, not gated
- Dataset card config: `default`, data file `data/retina_dataset.csv`
- Dataset-server split: `default/train`
- Dataset-server row/column count: 119,039 rows, 9 columns
- Auto-converted parquet: `default/train/0000.parquet`, 3,079,994 bytes
- Original configured CSV size: 28,866,318 bytes
- Direct download URL pattern: `https://huggingface.co/datasets/natelgrw/ReTiNA/resolve/main/<path>`

Exact repository files from the Hugging Face tree API:

| Path | Bytes |
| --- | ---: |
| `.gitattributes` | 126 |
| `README.md` | 2,602 |
| `data/README.md` | 3,867 |
| `data/additives/README.md` | 476 |
| `data/additives/add.smi` | 167 |
| `data/additives/add_descriptors.csv` | 16,545 |
| `data/cluster_split/cluster_1.csv` | 15,137,399 |
| `data/cluster_split/cluster_2.csv` | 6,286,181 |
| `data/cluster_split/cluster_3.csv` | 4,165,851 |
| `data/cluster_split/cluster_4.csv` | 3,627,182 |
| `data/cluster_split/cluster_5.csv` | 4,341,002 |
| `data/cluster_split/figures/cluster_assignments.csv` | 7,695,580 |
| `data/cluster_split/figures/cluster_rt.png` | 344,135 |
| `data/cluster_split/figures/cluster_umap.png` | 573,888 |
| `data/compounds/README.md` | 8,310 |
| `data/compounds/comp.smi` | 6,091,768 |
| `data/compounds/comp_descriptors.csv` | 348,748,041 |
| `data/lcms_methods.csv` | 16,640 |
| `data/method_split/figures/methods_rt.png` | 259,086 |
| `data/method_split/figures/methods_umap.png` | 272,314 |
| `data/method_split/methods_1.csv` | 1,313,997 |
| `data/method_split/methods_2.csv` | 1,315,427 |
| `data/method_split/methods_3.csv` | 1,089,765 |
| `data/method_split/methods_4.csv` | 6,077,386 |
| `data/method_split/methods_5.csv` | 19,186,922 |
| `data/retina_dataset.csv` | 28,866,318 |
| `data/scaffold_split/figures/scaffold_assignments.csv` | 2,028,108 |
| `data/scaffold_split/figures/scaffold_rt.png` | 303,766 |
| `data/scaffold_split/figures/scaffold_umap.png` | 1,636,496 |
| `data/scaffold_split/fold_1.csv` | 5,897,260 |
| `data/scaffold_split/fold_2.csv` | 5,770,319 |
| `data/scaffold_split/fold_3.csv` | 5,699,489 |
| `data/scaffold_split/fold_4.csv` | 5,720,713 |
| `data/scaffold_split/fold_5.csv` | 5,759,302 |
| `data/scripts/cluster_split.py` | 14,245 |
| `data/scripts/method_split.py` | 13,244 |
| `data/scripts/scaffold_split.py` | 16,801 |
| `data/solvents/README.md` | 8,306 |
| `data/solvents/solv.smi` | 61 |
| `data/solvents/solv_descriptors.csv` | 18,660 |

Observed headers from ranged samples:

- `data/retina_dataset.csv`: `compound, solvents, gradient, column, flow_rate, temp, rt, source, method_number`
- `data/lcms_methods.csv`: `method_number, datapoint_count, solvents, gradient, column, flow_rate, temp, source`
- `data/method_split/methods_*.csv`: main 9 columns plus `fold`
- `data/scaffold_split/fold_*.csv`: same 9 columns as the main dataset
- `data/cluster_split/cluster_*.csv`: main 9 columns plus `fold, umap_x, umap_y`
- `cluster_assignments.csv`: `compound, cluster, fold, umap_x, umap_y`
- `scaffold_assignments.csv`: `scaffold, fold, datapoint_count`
- Descriptor CSVs: `smiles` plus RDKit descriptor/fingerprint columns

The dataset card says ReTiNA has 119,039 molecule-environment combinations, 105,809 unique compounds, 6 unique solvents, 8 unique additives, and 73 LC-MS setup environments. `data/README.md` says each entry has 7 columns, but the current served dataset and CSV header have 9 columns because `rt` and `method_number` are present.

## Mapping proposal

Implement a ReTiNA-specific local adapter instead of using `--local-export` directly.

| ReTiNA field | Canonical target | Notes |
| --- | --- | --- |
| `compound` | `smiles`, then RDKit-derived `canonical_smiles`/`inchikey` | Do not map to `compound_name`; source docs define this as SMILES. |
| `solvents` | `mobile_phase_a`, `mobile_phase_b`, `notes` | Parse with `ast.literal_eval()`. Convert common solvent SMILES (`O`, `CC#N`, `CO`) and additives (`C(=O)O`, etc.) to readable labels where possible; preserve raw dict in notes. |
| `gradient` | `gradient_profile`, `initial_organic_pct`, `final_organic_pct`, `gradient_duration_min`, `total_runtime_min` | Parse list of `(time, percent_B)`. Confirm time units before numeric conversion; docs conflict between "min" and "seconds". |
| `column` | `column_name`, `stationary_phase_type`, `notes` | Parse tuple: first element `RP`/`HI`, then internal diameter, length, particle size. Current canonical schema has no dedicated column dimension fields, so encode dimensions in `column_name` and/or `notes`. |
| `flow_rate` | `flow_ml_min` | Add alias or adapter rename. |
| `temp` | `temperature_c` | Already aliased. |
| `rt` | `rt_min` | Dataset card says RT is in seconds, so likely `rt / 60`; verify source convention before ingestion. |
| `source` | `source_dataset` | Consider prefix `ReTiNA:<source>` for provenance. |
| `method_number` | `source_record_id` or method grouping note | Useful to join `data/lcms_methods.csv`; row-level IDs are not otherwise present. |

Recommended minimal normalized defaults: `matrix="reference"`, `success_flag=True`, `ion_mode="unknown"`, `notes` containing `source_url`, `license=MIT`, raw ReTiNA method encodings, and unit assumptions.

## Ingestion risks

- Unit ambiguity is the highest risk. The top README says RT values are in seconds and gradient over time in minutes; `data/README.md` says gradient tuple times are seconds. The repo canonical field is `rt_min`, so an unverified direct alias would be wrong if seconds are intended.
- Generic import would put SMILES into `compound_name` and leave `smiles` blank, damaging canonicalization and downstream descriptors.
- The `solvents`, `gradient`, and `column` fields are Python literal strings, not JSON. They need `ast.literal_eval()` with validation and fallback notes.
- ReTiNA lacks explicit peak metrics, MS transitions, sample matrix, pH field, compound names, source URLs per row, and per-row licenses. Most MS/peak/sample canonical fields will remain missing.
- Large descriptor table `data/compounds/comp_descriptors.csv` is 348.7 MB and should not be pulled for core RT ingestion. The default converted parquet is much smaller for the main table.
- Split files are evaluation artifacts, not additional independent observations. Ingesting the main dataset plus split files together would duplicate rows.
- Source-level counts in the README sum above the final 119,039 served rows, so use the served dataset count for ingestion size.

## Exact commands/results

- `git status --short`
  - Result: clean worktree before report creation.
- `Get-ChildItem -Path app,scripts,config,tests,docs -Recurse -File`
  - Result: found relevant files including `app/adapters/public_rt.py`, `scripts/fetch_public_datasets.py`, `app/schemas/dataset.py`, `app/schemas/canonical.py`, and public ingestion tests.
- `Get-Content app\adapters\public_rt.py`
  - Result: local fixture adapters for PredRet, GMCRT, MultiConditionRT; no ReTiNA adapter.
- `Get-Content scripts\fetch_public_datasets.py`
  - Result: RepoRT sample/bulk fetch, MCMRT supplement normalizer, reviewed local export path.
- `Get-Content app\schemas\dataset.py`
  - Result: canonical training columns listed above; required internal columns are not the same as public nullable canonical columns.
- Python API query: `https://huggingface.co/api/datasets/natelgrw/ReTiNA`
  - Result: public MIT dataset, config `default`, data file `data/retina_dataset.csv`, 40 repository files, SHA `5263a29274785296ee8da35fb1c468be18f5ca1f`.
- Python dataset-server queries: `/splits`, `/parquet`, `/size`
  - Result: one split `default/train`; parquet `0000.parquet` size 3,079,994 bytes; dataset 119,039 rows, 9 columns, original files 28,866,318 bytes.
- Python dataset-server query: `/first-rows?dataset=natelgrw/ReTiNA&config=default&split=train`
  - Result: features `compound`, `solvents`, `gradient`, `column`, `flow_rate`, `temp`, `rt`, `source`, `method_number`; first rows from `enaminert`.
- Python Hugging Face tree query: `/api/datasets/natelgrw/ReTiNA/tree/main?recursive=1`
  - Result: exact 40-file list and byte sizes in the table above.
- Python ranged reads with `Range: bytes=0-2047` for representative files
  - Result: confirmed CSV headers without full downloads; main file header is `compound,solvents,gradient,column,flow_rate,temp,rt,source,method_number`.

No full dataset download was performed.
