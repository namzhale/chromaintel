# ChromaIntel Model Literature and Architecture Review

## Data requirements to relay to Carver

Carver should prioritize data that preserves the full experimental context, not just compound and RT pairs. The current matrix can train a demo RT model, but practical LC-MS/MS method recommendation needs repeated internal runs with conditions, outcomes, and failures.

### P0 internal assay records

- Compound identity: `compound_name`, `canonical_smiles`, `inchikey`, `source_record_id`, `source_dataset`, salt/freebase form if known, analyte class or project tag, standard purity where available.
- LC method metadata: `column_name`, vendor, stationary phase chemistry, column dimensions, particle size, pore size if available, column age or injection count if available, `mobile_phase_a`, `mobile_phase_b`, additive names and concentrations, buffer concentration, measured or nominal `ph`, `gradient_profile` as full time/%B steps, `initial_organic_pct`, `final_organic_pct`, `gradient_duration_min`, `total_runtime_min`, equilibration time, `flow_ml_min`, `temperature_c`, `injection_ul`, autosampler temperature if available.
- Platform metadata: LC vendor/model, MS vendor/model, source type, instrument method identifier, dwell volume or delay volume if known.
- MS method metadata: `ion_mode`, adduct if known, charge, `precursor_mz`, `product_mz`, collision energy, cone/declustering/fragmentor voltage, dwell time, source gas/temperature/voltage settings if available.
- Sample context: `matrix`, species, anticoagulant, sample prep type, extraction solvent, dilution factor, internal standard identity and concentration, calibrator/QC/sample type.
- Outcomes: `rt_min`, peak width, `peak_area`, `peak_height`, `sn_ratio`, `tailing_factor`, `asymmetry`, `resolution`, carryover flag, matrix-effect/suppression estimate if available, observed interference flag, manual `quality_score` or accepted/rejected label, `success_flag`, reason for failure.
- Replication/provenance: run/batch ID, injection ID, date, analyst or system ID if allowed, injection order, concentration, replicate number, raw file reference, notes.

### P1 dataset priorities

1. Accepted and rejected internal bioanalytical runs for common matrices such as plasma, serum, urine, and buffer. Failed or marginal methods are especially valuable for quality and risk models.
2. Method-variation series where the same compound was run under different gradients, columns, pH/additives, flow, temperature, or polarity. These rows teach condition effects rather than only compound effects.
3. Replicate QC/calibrator injections under stable methods. These are needed for uncertainty, reproducibility, and peak-quality calibration.
4. Public RT datasets such as METLIN SMRT and RepoRT for broad chemistry coverage, but mark them as public/source-specific and expect missing matrix, transition, and peak-quality labels.
5. Library transition/intensity records, when available, to support ionization/intensity risk and transition-quality tasks.

### Immediate warning for the main agent

The current canonical schema now preserves `quality_score` when it is present and computes a transparent proxy when it is absent. The checked-in demo data is still too small for a reliable peak-quality model, so Carver should prioritize real accepted/rejected peak labels, peak metrics, and failure reasons from internal assay development runs.

## Existing Pipeline Observations

Files inspected:

- `app/models/training.py`
- `app/models/baseline.py`
- `app/services/feature_engineering.py`
- `app/services/dataset_assembly.py`
- `scripts/train_models.py`
- `reports/model_training_summary.md`
- `data/processed/model_matrix.csv`

The implemented MVP trainer is appropriate for a CPU demo:

- RT target: `rt_min`
- Quality target: `quality_score`, using observed labels when present and a provisional proxy from peak metrics when labels are missing.
- Features: 10 RDKit descriptors, 9 LC numeric summaries, 6 LC categorical/mobile-phase fields, and 3 MS features.
- Models: Ridge, RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor.
- Selection: lowest validation MAE, with 60/20/20 train/validation/test split for 12 usable rows.
- Artifact: `data/processed/models/trained_forward_bundle.joblib`
- Report outputs: `reports/model_training_summary.md`, `reports/test_predictions.csv`, `reports/feature_importance.csv`, and HTML plots.

Important limitations:

- The checked-in demo dataset has only 12 rows and 8 compounds.
- Validation and test splits are 3 rows each, so rankings are unstable.
- Public-like rows and internal rows are mixed in random splits. Larger datasets should use grouped/source-aware splits by compound, method, source, and preferably time.
- Current uncertainty includes a split-conformal q90 residual proxy plus held-out applicability-domain flags. This is still a demo diagnostic, not a fully calibrated per-condition interval.
- `gradient_profile` exists upstream but is collapsed to start/end/duration/slope in the model matrix. Full gradients will matter for method optimization.

## Literature and Market Scan

### Retention time prediction

METLIN SMRT is still the most relevant public small-molecule LC-MS RT reference. The 2019 Nature Communications paper reports a large METLIN-derived retention-time dataset and a deep learning model for small molecules, with strong top-k identification utility in LC-MS metabolomics. Source: [Zhou et al., 2019, Nature Communications](https://www.nature.com/articles/s41467-019-13680-7).

RepoRT is a 2023 Nature Methods resource explicitly aimed at standardized reporting and public reuse of small-molecule RT records. It is important because it emphasizes chromatographic metadata, not just compound structures. Source: [Stanstrup et al., 2023, Nature Methods](https://www.nature.com/articles/s41592-023-02143-z); dataset/code links are at [the RepoRT GitHub organization](https://github.com/Report-workflow).

MCMRT is a newer multi-column metabolite chromatographic retention-time dataset and is relevant for expanding beyond single-method RT prediction toward cross-column transfer. Source: [Scientific Data search result / article family](https://www.nature.com/search?q=MCMRT%20metabolite%20chromatographic%20retention%20time).

ROASMI is a recent retention-order/application-domain approach for small molecule identification. It is useful for ChromaIntel because retention order can be more transferable than absolute RT across methods. Source: [ROASMI, Journal of Cheminformatics](https://link.springer.com/article/10.1186/s13321-025-00968-8).

Graph neural networks have been applied directly to LC retention time from molecular graphs. The 2021 ACS Analytical Chemistry paper "Prediction of Liquid Chromatographic Retention Time with Graph Neural Networks" is a primary GNN reference for this space. Source: [ACS Analytical Chemistry, 2021](https://pubs.acs.org/doi/10.1021/acs.analchem.1c02363).

Transfer learning with pretrained graph neural networks is attractive when a target lab has a small labeled dataset. A 2023 Analytical Chemistry paper trained from large METLIN-like data and adapted to small target RT datasets, which is close to ChromaIntel's future shape. Source: [ACS Analytical Chemistry, 2023](https://pubs.acs.org/doi/10.1021/acs.analchem.3c02185).

DeepLC-style transfer learning is best known in proteomics, but the lesson transfers: instrument/method-specific calibration can be more important than a universal model. Source: [DeepLC, Nature Methods 2026](https://www.nature.com/articles/s41592-025-02635-8). Treat this as a strategy reference, not a direct small-molecule model choice.

### Molecular foundation models

ChemBERTa and MolFormer-style encoders can produce structure embeddings that may help RT, quality, and ionization models once enough lab labels exist. ChemBERTa pretraining used large PubChem SMILES data for molecular property prediction. Source: [ChemBERTa arXiv](https://arxiv.org/abs/2010.09885). MolFormer was trained at very large scale on molecular strings and is a stronger candidate for frozen embeddings than immediate fine-tuning in this MVP. Source: [Large-scale chemical language representations, arXiv](https://arxiv.org/abs/2106.09553).

For ChromaIntel, these models are overkill until the project has hundreds to thousands of labeled internal rows per condition family, or a clean offline embedding workflow. A practical intermediate step is to add Morgan fingerprints and maybe frozen pretrained embeddings as extra tabular columns, then compare by grouped validation.

### Method optimization

LC method optimization is usually a closed-loop optimization problem, not just a one-shot RT prediction problem. Bayesian optimization has been used for chromatographic gradient optimization under small experiment budgets. Source: [Bayesian optimization of liquid chromatographic separations, Analytical Chemistry 2023](https://pubs.acs.org/doi/10.1021/acs.analchem.3c02944).

Recent operator-free HPLC optimization work formalizes objectives such as number of resolved peaks, last elution time, critical resolution, symmetry, and sensitivity. Source: [Closed-loop HPLC method optimization, RSC Analytical Methods 2024](https://pubs.rsc.org/en/content/articlelanding/2024/an/d4an00578h).

For an LC-MS/MS bioanalytical MVP, do not start with autonomous closed-loop optimization. Start with a constrained candidate generator, a forward model, uncertainty penalties, and lab-approved operating bounds. Move to Bayesian optimization only when ChromaIntel can ingest experiment results quickly and safely.

### Classical tabular model libraries

LightGBM, XGBoost, and CatBoost are the right near-term external libraries to evaluate once the dataset grows. All run on CPU and are proven for tabular regression. LightGBM is fast and supports categorical features. Source: [LightGBM documentation](https://lightgbm.readthedocs.io/en/stable/). XGBoost has mature histogram tree methods and categorical support. Source: [XGBoost documentation](https://xgboost.readthedocs.io/en/stable/). CatBoost is especially convenient for mixed numeric/categorical chemistry-method tables because it handles categorical features natively. Source: [CatBoost documentation](https://catboost.ai/docs/).

## Recommended Architecture Roadmap

### Implement next

1. Keep the current Ridge/RF/HGB CPU baseline as the demo benchmark. It is transparent and dependency-light.
2. Add source-aware and group-aware evaluation before adding heavier models. Suggested split keys: `inchikey`, `source_dataset`, `column_name`, `mobile_phase_system`, and later `instrument_platform`.
3. Preserve explicit quality labels through dataset assembly. Current quality metrics are not meaningful until this is fixed.
4. Keep the no-new-dependency `ExtraTreesRegressor` candidate in the model zoo. The current run includes it, but the tiny validation split does not justify product claims.
5. Add applicability-domain checks:
   - compound AD from descriptor/fingerprint nearest-neighbor distance
   - method AD from unseen column/mobile-phase/instrument categories
   - source AD from public vs internal dataset tags
   - prediction interval from conformal calibration once enough calibration rows exist
6. Add CatBoost first when external dependencies are acceptable and there are at least several hundred rows with categorical method metadata. Then compare LightGBM and XGBoost under the same grouped splits.

### Implement after data maturity

1. Multi-task model layer:
   - RT regression
   - peak quality regression/classification
   - success/failure classification
   - log peak area or intensity risk
   - ionization polarity/adduct/transition suitability where labels exist
2. Quantile or conformal intervals:
   - start with split conformal intervals on residuals
   - later condition intervals by source, matrix, column chemistry, and AD bin
3. Candidate method optimizer:
   - generate lab-safe candidate gradients/columns/mobile phases
   - score candidates by predicted RT window fit, peak quality, runtime, uncertainty, and AD penalty
   - require human approval and record outcomes for active learning

### Defer

- Fine-tuning ChemBERTa/MolFormer/GNN models. Use frozen embeddings or fingerprints first.
- End-to-end graph/method neural networks. They need far more data, stricter splits, and careful leakage control.
- Autonomous Bayesian optimization. It is valuable later, but only after instrument integration, experiment tracking, and safety bounds are solid.
- Claims about calibrated uncertainty from the current global residual proxy.

## Lightweight CPU Experiment

Command run as an inline Python script with the existing virtual environment:

```powershell
@'
# compares current trainer candidates against ExtraTreesRegressor
'@ | .\.venv\Scripts\python.exe -
```

Dataset and split:

- Matrix: `data/processed/model_matrix.csv`
- Rows: total 12, train 6, validation 3, test 3
- Features: 28 total, with 7 categorical and 21 numeric
- Split logic: same random-state train/validation/test split as `app.models.training.train_forward_models`

Results:

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| linear_ridge | 1.558 | 1.825 | -2.431 | 2.901 | 3.298 | -0.791 |
| random_forest | 1.703 | 1.943 | -2.889 | 2.168 | 2.589 | -0.104 |
| hist_gradient_boosting | 1.733 | 1.994 | -3.096 | 2.072 | 2.678 | -0.182 |
| extra_trees | 2.120 | 2.579 | -5.855 | 1.940 | 2.105 | 0.270 |

Interpretation: ExtraTrees improved the tiny test split but had the worst validation MAE. With only 3 validation rows and 3 test rows, this is a smoke test only. It supports adding ExtraTrees as another cheap sklearn candidate after evaluation is improved; it does not prove superiority.

## Practical Training Commands

Assemble the current demo matrix:

```powershell
.\.venv\Scripts\python.exe scripts\assemble_dataset.py
```

Train the current forward-model bundle:

```powershell
.\.venv\Scripts\python.exe scripts\train_models.py
```

Train with explicit paths:

```powershell
.\.venv\Scripts\python.exe scripts\train_models.py `
  --matrix data\processed\model_matrix.csv `
  --artifact data\processed\models\trained_forward_bundle.joblib `
  --report-dir reports `
  --plots-dir data\processed\plots
```

Recommended next training command after adding grouped evaluation and an ExtraTrees candidate should remain CPU-only and artifact-compatible:

```powershell
.\.venv\Scripts\python.exe scripts\train_models.py --matrix data\processed\model_matrix.csv
```

## Final Recommendation

The next implementation should not jump to deep learning. The highest-value model work is:

1. Preserve real quality labels and richer method fields.
2. Add grouped/source-aware validation and applicability-domain reporting.
3. Add ExtraTrees as a no-dependency sklearn candidate.
4. Add CatBoost as the first external tabular model once the dataset is large enough and dependency policy allows it.
5. Design the data schema now for multi-task RT, quality, success, and intensity-risk learning.

Deep molecular models and Bayesian closed-loop method optimization are credible future directions, but they should wait until ChromaIntel has enough internal, condition-rich, outcome-rich data to validate them honestly.
