# AI-Assisted LC-MS/MS Method Development MVP

Practical local MVP for bioanalytical small-molecule LC-MS/MS method development. It supports forward retention-time and peak-quality prediction, constrained method recommendation, mock public/internal datasets, PostgreSQL schema, FastAPI routes, and a Streamlit GUI.

## What is included

- PostgreSQL schema for compounds, structures, datasets, methods, gradients, runs, peak metrics, MS settings, predictions, recommendations, and audit logs.
- RDKit descriptor pipeline: MW, logP, TPSA, HBD/HBA, rotatable bonds, aromatic rings, charge, heavy atoms, and Morgan fingerprints.
- Offline-first adapters for internal lab templates, METLIN SMRT, RepoRT, ChEMBL, MassBank, and MoNA.
- PubChem enrichment client for name or CID lookup.
- Multi-model CPU training for RT and provisional quality using Ridge, RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, and CatBoost.
- Heuristic fallback predictions so the GUI remains useful before model artifacts exist.
- Recommendation engine that generates candidate methods and ranks them by RT fit, quality, and runtime.
- Streamlit pages: Dashboard, Compound lookup, Forward prediction, Method recommendation, Dataset browser, Model evaluation, Admin/import.
- Literature and market review PDF: `docs/literature_market_review_ai_lcms_bioanalysis.pdf`.

## Local setup

```powershell
cd C:\study\cheminf\pract\lcms_method_mvp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Train the baseline model on mock data:

```powershell
python scripts/train_baselines.py
```

Build the unified canonical dataset and model matrix:

```powershell
python scripts/assemble_dataset.py
```

This writes:

- `data/processed/master_dataset.csv`
- `data/processed/model_matrix.csv`
- `data/templates/internal_lab_historical_runs_template.csv`
- `data/templates/internal_lab_data_dictionary.md`

Train the multi-model forward pipeline and generate evaluation outputs:

```powershell
python scripts/train_models.py
```

This trains Ridge, RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, and CatBoost models for RT and provisional peak quality. Model selection uses GroupKFold by compound identity, then writes:

- `data/processed/models/trained_forward_bundle.joblib`
- `reports/model_training_summary.md`
- `reports/test_predictions.csv`
- `reports/feature_importance.csv`
- `reports/source_metrics.csv`
- `reports/cv_metrics.csv`
- `reports/source_holdout_metrics.csv`
- `reports/sota_model_experiments.md`
- reproducible Plotly HTML plots under `data/processed/plots/`

Generate a compact PDF dashboard for presentation or review:

```powershell
python scripts/generate_dashboard_pdf.py
```

This writes `reports/chromaintel_dashboard_report.pdf` with dataset size, model comparison, source-wise errors, parameter significance, and the next roadmap.

Run the GUI:

```powershell
streamlit run app/gui/streamlit_app.py
```

The GUI includes Dataset Assembly and Training pages. Forward Prediction and Method Recommendation automatically use `data/processed/models/trained_forward_bundle.joblib` when present, then fall back to the older baseline or transparent heuristic.
Trained predictions also expose applicability-domain flags and reasons based on saved training feature ranges and categorical values.

Run the API:

```powershell
uvicorn app.api.main:app --reload
```

## Docker Compose

```powershell
docker compose up --build
```

- Streamlit GUI: http://localhost:8501
- FastAPI app service: http://localhost:8001/docs
- PostgreSQL: localhost:5432, database `lcms_method_dev`, user/password `lcms/lcms`

## Database

For quick local table creation:

```powershell
python -m app.db.init_db
python scripts/seed_db.py
```

For migration-managed databases:

```powershell
alembic upgrade head
```

## Data import approach

The MVP avoids blocking on private resources or scraping. Public and optional sources are represented as normalized offline CSV/JSON import modules:

- `app/adapters/metlin_smrt.py`
- `app/adapters/report.py`
- `app/adapters/pubchem.py`
- `app/adapters/chembl.py`
- `app/adapters/massbank.py`
- `app/adapters/mona.py`
- `app/adapters/internal_lab_template.py`

Internal lab files should map to the normalized record columns used in `data/mock_training_records.csv`. Raw exports can be staged in `data/raw/`; cleaned model-ready tables can go in `data/processed/`.

Normalize a reviewed local public export without scraping:

```powershell
python scripts/fetch_public_datasets.py --list-sources

python scripts/fetch_public_datasets.py --bulk-report --target-rows 5000 --max-datasets 80 --output-name report_bulk_5k

python scripts/fetch_public_datasets.py --mcmrt --output-name mcmrt_supplement

python scripts/assemble_dataset.py

python scripts/fetch_public_datasets.py `
  --local-export data\raw\public_sources\some_rt_export.tsv `
  --source-name RepoRT:reviewed `
  --source-url https://github.com/michaelwitting/RepoRT `
  --license-note CC-BY-SA-4.0
```

Extract conservative LC-MS/MS entities from reviewed text snippets:

```powershell
python scripts/extract_lcms_entities.py snippets.txt --source-name paper_batch_001
python scripts/extract_lcms_entities.py --stdin-text "Caffeine on C18 column, rt 2.4 min." --json
```

The literature parser is offline-first. The `--use-llm` flag is reserved for a future opt-in extractor and does not call an LLM in this MVP.

Current checked-in processed training matrix after RepoRT plus MCMRT expansion:

- `data/processed/external_mcmrt_supplement.csv`: 10,073 MCMRT RT rows from 30 reversed-phase methods
- `data/processed/master_dataset.csv`: 15,052 rows, 3,945 compounds
- `data/processed/model_matrix.csv`: 15,052 rows x 41 columns
- selected RT model after retraining: `extra_trees`
- validation: GroupKFold by `inchikey` plus source-family holdout for RepoRT and MCMRT

## Internal Lab Onboarding

Generate the practical CSV template and data dictionary:

```powershell
python scripts/assemble_dataset.py
```

Template files:

- `data/templates/internal_lab_historical_runs_template.csv`
- `data/templates/internal_lab_data_dictionary.md`

The Admin/import GUI page previews uploaded CSV files and validates required fields, numeric ranges, invalid SMILES, and duplicate run IDs.

## Model Evaluation

The generated report at `reports/model_training_summary.md` contains:

- datasets and row counts
- feature set summary
- tested model families
- best RT and quality models
- MAE, RMSE, and R2 metrics
- grouped cross-validation metrics
- source-family holdout metrics for new-source transfer checks
- source-wise performance
- split-conformal q90 RT uncertainty proxy
- applicability-domain flags for held-out predictions
- permutation importance with parameter significance labels
- limitations and next steps for internal fine-tuning

For a presentation-style summary, use `reports/chromaintel_dashboard_report.pdf`.

## Testing

```powershell
python -m pytest tests
```

Current tests cover:

- RDKit descriptor calculation and invalid SMILES handling.
- Dataset schema normalization and merge logic.
- Internal lab import validation.
- Training model zoo, uncertainty metadata, source metrics, and feature significance.
- Literature parser extraction into canonical fields.
- Recommendation candidate ranking and method runtime calculation.

## Notes for real lab integration

- Replace mock records with internal LC-MS/MS assay development runs, keeping source provenance in `datasets.source_type`.
- Keep audited recommendation inputs and outputs in `audit_log` and `recommendations`.
- Add matrix, sample preparation, protein precipitation/extraction, and instrument platform fields as metadata until the lab schema stabilizes.
- Treat METLIN SMRT and RepoRT as pretraining/benchmarking sources, then calibrate with internal accepted peak metrics.
