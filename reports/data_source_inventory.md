# Public Data Source Inventory for ChromaIntel

## Model constraints to relay to Beauvoir

Public data can improve RT modeling and source-aware recommendation evaluation, but it will not supply the most important practical BE-assay labels. RepoRT is the best immediate public source because it provides real small-molecule RTs with structured chromatographic metadata: compound identifiers, RT, column name/USP code/dimensions, temperature, flow, solvent composition, pH, and gradient start/end/time tables. It does not provide sample matrix, sample preparation, injection context, MRM transitions, source settings, peak area/height, S/N, asymmetry, tailing, resolution, analyst acceptance labels, failed methods, or failure reasons.

The demo model matrix has already been regenerated after the `quality_score` preservation fix: `quality_score` has 11 unique values across 12 demo rows. Public RepoRT-derived rows should keep `quality_score` null unless a source explicitly provides a measured or manually labeled quality outcome; otherwise the feature pipeline's fallback quality surrogate must be treated as a transparent proxy, not ground truth.

Beauvoir should prioritize these internal data fields over more public RT rows:

- Accepted and rejected method-development runs, including rejected candidate methods.
- Method-variation series where one or a few LC/MS parameters changed at a time.
- Replicate QC, calibrator, blank, carryover, and system-suitability injections.
- Full LC gradient time/%B tables, not only initial/final organic percentages.
- Platform metadata: LC model, MS model, detector type, software, column lot/age, guard column, dead volume/dwell volume where available.
- MS transitions and source settings: precursor/product m/z, collision energy, declustering/cone voltage, polarity, ion source, gas/temperature settings, dwell time, scheduled windows.
- Matrix/sample prep metadata: plasma/serum/urine/tissue, anticoagulant, extraction, dilution, protein precipitation/SPE/LLE, reconstitution solvent, injection solvent.
- Peak metrics and labels: peak area/height, S/N, asymmetry, tailing, width, resolution, carryover, matrix factor, recovery, IS response, calibration residuals, manual quality label, acceptance decision, and failure reason.
- Run provenance: method version, operator/site, instrument id, batch id, acquisition date, raw-file pointer, processing method version, integration override flag.

## Current repo state

Existing adapters include offline-first loaders for authorized METLIN SMRT exports, RepoRT-style normalized records, internal lab templates, MassBank, MoNA, ChEMBL annotations, and a small PubChem PUG REST client. The active canonical schema is defined in `app/schemas/dataset.py` with identity, LC condition, MS, RT, peak-quality, matrix, success, quality-score, notes, and missingness fields.

`scripts/fetch_public_datasets.py` now supports two bounded public-data paths: the existing tiny RepoRT dataset fetcher, and a local-file import path for small CSV/TSV/JSON/XLSX exports that have already had licensing and redistribution reviewed. The local importer records source URL, license note, and source filename in `notes`, requires usable compound name plus RT after alias normalization, and writes only a normalized sample under `data/processed`.

The current checked-in demo data already assembles mock-like `internal_lab`, `METLIN_SMRT`, and `RepoRT` rows into `data/processed/master_dataset.csv` and `data/processed/model_matrix.csv`. The demo model matrix currently has 12 rows, 11 unique `quality_score` values, and no null `quality_score` values.

## Source inventory

| Source | URL | License/access notes | Expected fields | Adapter strategy | ChromaIntel value | Gaps/blockers |
| --- | --- | --- | --- | --- | --- | --- |
| RepoRT processed data | https://github.com/michaelwitting/RepoRT | Public GitHub repository, CC-BY-SA-4.0. Small TSVs can be fetched directly; large full imports should be reported before download. | `id`, name, formula, RT, standardized SMILES/InChI/InChIKey, ClassyFire classes, column name/USP/dimensions, temperature, flow, solvent composition, pH, gradient start/end and optional full gradient TSV. | Add offline normalizer from `processed_data/<id>/*_rtdata_canonical_success.tsv`, `*_metadata.tsv`, `*_gradient.tsv`, and `*_info.tsv` into the canonical schema. Keep source IDs and license notes. | Highest-value public RT source. Improves RT model coverage, column/mobile-phase diversity, method-transfer evaluation, source holdout tests. | No biological matrix, sample prep, MRM/product ions, source settings, injection volume in many datasets, peak metrics, `quality_score`, acceptance/rejection labels, or failure reasons. |
| PredRet | https://predret.org/ | Public web resource with "Get all data" download, but license should be checked before automated redistribution. Several PredRet datasets are already represented inside RepoRT. | Experimental RTs across chromatographic systems, compound identifiers, method/system descriptors depending on export. | Prefer RepoRT copies first for normalized metadata and clear GitHub license. If direct PredRet import is needed, download manually or with explicit approval and keep provenance. | Useful for method-transfer benchmarks and RT projection/mapping evaluation. | Direct export format/licensing needs confirmation; not BE assay-specific; likely lacks peak quality/MS transitions. |
| Metabolomics Workbench / NMDR RT data | https://www.metabolomicsworkbench.org/data/search_rt_form.php and https://www.metabolomicsworkbench.org/tools/MWRestAPIv1.2.pdf | Public NIH repository and REST API. Individual study terms and file sizes should be reviewed before import; avoid broad study downloads. | Study metadata, analytical platform/method metadata, metabolite structures, experimental result tables, and RT search outputs for LC-MS studies. | Use reviewed local CSV/TSV/mwTab-derived exports through the generic local public importer. Preserve study ID, source URL, and license/access note. | Good candidate for expanding matrix/study context and real LC-MS RT observations beyond curated standard libraries. | Heterogeneous tables; study files can be large; RT search may require RefMet names; peak-quality and targeted MRM labels are not reliably structured. |
| MCMRT / Scientific Data 2024 | https://www.nature.com/articles/s41597-024-03780-5 and https://doi.org/10.57760/sciencedb.15823 | Open article; dataset hosted at Science Data Bank. Review dataset license before ingesting or redistributing. | >10,000 experimental RT entries, 343 small molecules, 30 reversed-phase LC methods, 3 replicate analyses, LC setup tables, Orbitrap Q-Exactive Plus platform/source settings in article. | High-value candidate for a later importer if license permits. Normalize supplementary tables into compound/method/replicate canonical rows. | Excellent for method-variation and transfer-learning evaluation because compounds overlap across many LC setups. | Needs license/access review and supplementary-table parsing. Mostly HRMS/full-scan, not targeted bioanalytical MRM. Peak-quality/manual acceptance labels not obvious. |
| MassBank data | https://github.com/MassBank/MassBank-data | Public official repository of open MassBank records; individual records carry license metadata and releases are available via Zenodo. Do not bulk-download until size and record-level licensing are reviewed. | Compound IDs, exact mass/formula, instrument type, ionization, precursor type/mz, collision energy, MS2 peaks, sometimes chromatography fields. | Use as optional enrichment by InChIKey/name for MS settings and spectral metadata, not as primary RT training. Respect record-level license. | Improves MS feature coverage, precursor/adduct/fragment context, library-evaluation metadata. | LC gradient and bioanalytical method details are often sparse; RT may be absent or incomparable; no peak quality/acceptance labels. |
| MoNA | https://mona.fiehnlab.ucdavis.edu/downloads and https://github.com/metabolomics-us/mona | Public downloads exist, but files can be large and library-specific licenses vary. The public app code is LGPL-3.0, which is not the data license. | MS/MS spectra, SPLASH, compound metadata, ionization/adduct, instrument/collision metadata, sometimes RT. | Use only small, license-checked exports or user-provided offline files. Normalize MS metadata to optional annotation fields. | Useful for spectral/MS settings enrichment and candidate matching evaluation. | Large downloads; per-library license ambiguity; RT/chromatography details not consistently sufficient for LC method modeling. |
| PubChem PUG REST / downloads | https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest and https://pubchem.ncbi.nlm.nih.gov/docs/downloads | Free public resource. PubChem advises checking data-source-specific license information for deposited data. PUG REST is rate-limited by normal public API etiquette. | CID, canonical/isomeric SMILES, formula, molecular weight, synonyms, xrefs, depositor/source metadata. | Keep current lightweight lookup client; cache small enrichment outputs offline by CID/InChIKey. | Improves compound identity standardization and descriptor reproducibility. | Does not provide LC-MS method outcomes, peak metrics, or BE assay labels. |
| ChEMBL | https://www.ebi.ac.uk/chembl/ and https://chembl.gitbook.io/chembl-interface-documentation | ChEMBL data is CC-BY-SA-3.0. Best used through documented downloads/API or small offline exports. | ChEMBL IDs, canonical structures, mechanism/target/activity annotations, drug-like molecule metadata. | Optional annotation table joined by InChIKey/SMILES; do not mix bioactivity labels with assay-quality labels. | Helpful for compound class/context and drug-likeness enrichment. | No chromatographic conditions, RT, peak quality, MS transitions, or method-development outcomes. |

## Tiny normalized sample created

Created a 10-row RepoRT sample from dataset `0001`:

- Raw source files: `data/raw/public_sources/report_0001_rtdata_canonical_success.tsv`, `report_0001_metadata.tsv`, `report_0001_gradient.tsv`, `report_0001_info.tsv`.
- Normalized sample: `data/processed/external_report_0001_sample.csv`.
- Fetch/normalization script: `scripts/fetch_public_datasets.py`.
- Local reviewed-export normalizer: `scripts/fetch_public_datasets.py --local-export <file> --source-name <name> --source-url <url> --license-note <note>`.

The normalized sample matches the current canonical schema, including the restored `quality_score` column. `quality_score` is intentionally null for these public rows because no measured peak-quality or manual acceptance field exists in the RepoRT source files used.

## Offline import plan

1. Start with RepoRT because it is license-clear and method-rich. Import selected `processed_data` datasets with full provenance and source-record IDs.
2. Keep public RT rows separate from internal BE assay rows during validation. Use source-holdout and method-holdout splits rather than random splits only.
3. Treat public rows as RT/method-condition supervision only. Do not train practical recommendation quality as if public rows had accepted/rejected labels.
4. Add optional enrichment tables from PubChem/ChEMBL by CID/InChIKey for compound identity and annotations.
5. Add MassBank/MoNA only as small, license-checked MS metadata enrichments unless a specific dataset supplies usable LC conditions.
6. Reserve model selection and recommendation calibration for internal accepted/rejected runs with peak metrics and failure reasons.

## Exact missing public-data fields for SOTA/practical models

Public sources do not reliably supply these fields, but Beauvoir should assume they are required for practical recommendation models:

- Outcome labels: accepted/rejected method, analyst quality score, failure reason, rework reason.
- Peak labels: S/N, asymmetry/tailing, peak width, area/height, resolution from nearest interference, carryover, IS response, integration override.
- Bioanalytical context: matrix, sample prep, calibration/QC level, dilution, extraction recovery, matrix factor, stability condition.
- Targeted MS method: precursor/product ions, qualifier/quantifier transitions, collision energy, cone/declustering voltage, source temperature/gases, dwell time, scheduled RT window.
- LC operational context: exact gradient table, autosampler temperature, injection solvent/volume, column age/lot, guard column, dead/dwell volume, equilibration time.
- Provenance and drift: instrument/platform/site/operator, batch, date, raw data link, processing method, replicate id, sequence position, maintenance state.
