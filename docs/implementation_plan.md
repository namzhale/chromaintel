# ChromaIntel LC-MS/MS MVP Implementation Plan

> For agentic workers: implement this plan milestone by milestone. Keep each milestone independently testable, run the listed verification commands before committing that milestone, and avoid broad refactors unless a checklist item explicitly requires them.

**Goal:** Complete the ChromaIntel LC-MS/MS MVP from demo-ready scaffolding to an internally usable lab onboarding workflow with assembled datasets, trained/evaluated forward models, GUI dashboards, and documented release handoff.

**Architecture:** Keep the current offline-first FastAPI + Streamlit + SQLAlchemy application shape. Use normalized CSV/template imports and RDKit descriptors to produce `data/processed/master_dataset.csv` and `data/processed/model_matrix.csv`, then train persisted scikit-learn model bundles consumed by the predictor, recommendation engine, API, and GUI.

**Tech Stack:** Python 3.10, FastAPI, Streamlit, SQLAlchemy/Alembic, pandas, RDKit, scikit-learn, Plotly, pytest, joblib.

---

## 1. Current State Summary

- Repository root: `C:\study\cheminf\pract\lcms_method_mvp`.
- Existing app surface:
  - FastAPI routes in `app/api/main.py` for health, PubChem lookup, prediction, recommendation, and dataset browsing.
  - Streamlit GUI in `app/gui/streamlit_app.py` with Dashboard, Compound lookup, Forward prediction, Method recommendation, Dataset browser, Model evaluation, and Admin/import pages.
  - SQLAlchemy schema in `app/db/models.py`, initialization in `app/db/init_db.py`, and first Alembic migration in `alembic/versions/001_initial_schema.py`.
  - Offline adapters in `app/adapters/` for internal lab templates, METLIN SMRT, RepoRT, ChEMBL, MassBank, MoNA, and PubChem enrichment.
  - Descriptor and feature services in `app/services/descriptors.py`, `app/services/features.py`, and `app/services/feature_engineering.py`.
  - Recommendation and prediction services in `app/services/recommendation.py` and `app/services/predictor.py`.
- Dataset assembly work already exists:
  - `app/services/dataset_assembly.py` normalizes source frames into canonical columns, canonicalizes structures, derives gradient fields, and deduplicates by identity/method/RT.
  - `scripts/assemble_dataset.py` writes `data/processed/master_dataset.csv`, `data/processed/model_matrix.csv`, and internal lab template files.
  - `app/services/internal_validation.py` validates internal lab upload columns, ranges, duplicate run IDs, and SMILES.
- Training work already exists:
  - `app/models/baseline.py` and `scripts/train_baselines.py` provide legacy RandomForest baseline training.
  - `app/models/training.py` trains Ridge, RandomForest, and HistGradientBoosting forward models for RT and provisional quality; writes plots and reports.
  - `scripts/train_models.py` loads or creates the model matrix and writes `data/processed/models/trained_forward_bundle.joblib`.
  - `reports/model_training_summary.md` exists, but the checked-in demo report is based on only 12 rows and shows weak RT validation metrics; quality metrics are degenerate because the seed data has little quality variation.
- Current data/artifacts:
  - Mock CSVs exist in `data/`.
  - Processed outputs exist under `data/processed/`, including `master_dataset.csv`, `model_matrix.csv`, trained model bundles, and Plotly HTML plots.
  - Internal onboarding templates exist under `data/templates/`.
- Current tests:
  - Tests cover dataset normalization/deduplication, descriptor calculation, feature engineering, internal lab validation/template writing, and recommendation ranking.
  - Missing or incomplete coverage remains for full CLI assembly behavior, trained model pipeline behavior, predictor trained-bundle path, API persistence behavior, and GUI dashboard data/report integration.

---

## 2. Remaining Milestones

### Milestone 1: Lock Dataset Contracts And Internal Import Readiness

**Outcome:** Internal lab users can validate historical runs against a clear canonical schema before those runs enter training.

**Files to modify or create:**
- Modify: `app/schemas/dataset.py`
- Modify: `app/services/internal_validation.py`
- Modify: `app/services/dataset_assembly.py`
- Modify: `app/adapters/internal_lab_template.py`
- Modify: `scripts/assemble_dataset.py`
- Modify: `data/templates/internal_lab_historical_runs_template.csv`
- Modify: `data/templates/internal_lab_data_dictionary.md`
- Modify: `tests/test_internal_lab_validation.py`
- Modify: `tests/test_dataset_assembly.py`
- Create if needed: `tests/test_assemble_dataset_cli.py`

**Checklist:**
- [ ] Confirm the canonical dataset columns include all MVP fields needed for lab onboarding: run ID/provenance, compound identity, matrix, sample prep, LC conditions, gradient summary, MS transition settings, RT, peak quality metrics, success flag, notes, and missing-field count.
- [ ] Ensure `REQUIRED_INTERNAL_COLUMNS` requires all fields needed for minimum viable model training: `run_id`, `compound_name`, `smiles`, `column_name`, `mobile_phase_a`, `mobile_phase_b`, `rt_min`, plus any required method provenance fields the lab wants to enforce.
- [ ] Extend internal validation to emit actionable issue messages for missing required fields, invalid SMILES, duplicate run IDs, impossible ranges, unsupported ion modes, invalid organic percentages, and final organic below initial organic when the row claims a gradient ramp.
- [ ] Ensure `normalize_source_frame` preserves `run_id` or maps it to `source_record_id` so imported internal data remains traceable.
- [ ] Ensure assembly reports row counts for raw, normalized, dropped invalid, deduplicated, and model-matrix rows.
- [ ] Keep internal templates aligned with the exact validation schema and data dictionary text.
- [ ] Add focused tests for a valid internal template row, an invalid row with multiple issues, run ID provenance mapping, and CLI assembly output paths.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_internal_lab_validation.py tests/test_dataset_assembly.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_assemble_dataset_cli.py -v
.\.venv\Scripts\python.exe scripts/assemble_dataset.py --source data/mock_training_records.csv --output-dir data/processed --templates-dir data/templates
```

Expected result: all tests pass; assembly prints source/master/model-matrix row counts and template paths; `data/processed/master_dataset.csv`, `data/processed/model_matrix.csv`, and `data/templates/*` are regenerated consistently.

### Milestone 2: Harden Feature Engineering And Model Matrix Generation

**Outcome:** Model features are stable, explainable, and robust to realistic sparse public/internal LC-MS/MS records.

**Files to modify or create:**
- Modify: `app/services/feature_engineering.py`
- Modify: `app/services/features.py`
- Modify: `app/services/descriptors.py`
- Modify: `app/services/dataset_assembly.py`
- Modify: `tests/test_feature_engineering.py`
- Modify: `tests/test_descriptors.py`
- Create if needed: `tests/test_model_matrix_contract.py`

**Checklist:**
- [ ] Freeze a model matrix contract: identity columns, numeric descriptor columns, LC numeric features, LC categorical features, MS features, target columns, and derived quality score.
- [ ] Add a single exported helper that returns the expected feature column groups and target columns used by both training and evaluation.
- [ ] Make quality score derivation explicit for rows with `sn_ratio`, `resolution`, `asymmetry`, and `tailing_factor`; preserve provided `quality_score` when present.
- [ ] Ensure invalid or missing SMILES do not crash assembly; they should create nullable descriptor values and retain notes/provenance.
- [ ] Decide whether Morgan fingerprints are enabled for the MVP. Keep them disabled by default for small demo data, and document the flag in tests if retained.
- [ ] Add tests that assert stable column order, numeric coercion, quality-score behavior, invalid SMILES behavior, and categorical defaults.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py tests/test_descriptors.py tests/test_model_matrix_contract.py -v
.\.venv\Scripts\python.exe scripts/assemble_dataset.py
```

Expected result: all tests pass; model matrix has deterministic columns and can be regenerated from the mock data without errors.

### Milestone 3: Finish Reproducible Training, Evaluation, And Reports

**Outcome:** A single command trains the forward models, writes a loadable artifact, and produces evaluation reports that the GUI and lab team can trust as MVP diagnostics.

**Files to modify or create:**
- Modify: `app/models/training.py`
- Modify: `app/models/baseline.py`
- Modify: `app/services/predictor.py`
- Modify: `scripts/train_models.py`
- Modify: `scripts/train_baselines.py`
- Modify: `reports/model_training_summary.md`
- Modify: `reports/test_predictions.csv`
- Modify: `reports/feature_importance.csv`
- Modify: `data/processed/models/trained_forward_bundle.joblib`
- Modify: `data/processed/plots/predicted_vs_actual_rt.html`
- Modify: `data/processed/plots/rt_error_distribution.html`
- Modify: `data/processed/plots/source_wise_performance.html`
- Modify: `data/processed/plots/feature_importance.html`
- Create if needed: `tests/test_training_pipeline.py`
- Create if needed: `tests/test_predictor_trained_bundle.py`

**Checklist:**
- [ ] Add tests that train on a small deterministic fixture and confirm the saved bundle can be loaded and used by `ForwardPredictor`.
- [ ] Ensure `scripts/train_models.py` fails clearly when the model matrix is too small, malformed, or missing required target columns.
- [ ] Keep train/validation/test split seeds fixed and include split sizes in the report.
- [ ] Add source-aware evaluation outputs where data volume permits: source distribution, source-wise MAE, and explicit warning when source holdout is not statistically meaningful.
- [ ] Add applicability-domain metadata to the trained bundle: observed ranges for pH, flow, runtime, logP, TPSA, and column/mobile-phase categories.
- [ ] Use trained bundle metadata in `ForwardPredictor._out_of_domain` when available; keep heuristic bounds as fallback.
- [ ] Ensure `reports/model_training_summary.md` distinguishes demo/mock limitations from real internal calibration requirements.
- [ ] Re-run training after dataset work and commit regenerated report/model artifacts only when they are intentional release artifacts.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_training_pipeline.py tests/test_predictor_trained_bundle.py -v
.\.venv\Scripts\python.exe scripts/train_models.py --matrix data/processed/model_matrix.csv --artifact data/processed/models/trained_forward_bundle.joblib --report-dir reports --plots-dir data/processed/plots
.\.venv\Scripts\python.exe -m pytest tests -v
```

Expected result: tests pass; training prints train/validation/test counts, best RT model, best quality model, artifact path, report path, and feature count; artifact reload works through the predictor.

### Milestone 4: Complete API And Persistence Workflows

**Outcome:** Prediction, recommendation, dataset browsing, and import-oriented workflows are API-testable and audit-friendly.

**Files to modify or create:**
- Modify: `app/api/main.py`
- Modify: `app/db/models.py`
- Modify: `app/db/init_db.py`
- Modify: `app/db/session.py`
- Modify: `alembic/env.py`
- Modify or create: `alembic/versions/*.py`
- Modify: `app/schemas/method.py`
- Modify: `app/schemas/prediction.py`
- Create if needed: `tests/test_api_prediction.py`
- Create if needed: `tests/test_api_dataset_browser.py`
- Create if needed: `tests/test_db_schema.py`

**Checklist:**
- [ ] Add API tests for `/health`, `/predict`, `/recommend`, and `/datasets/browser`.
- [ ] Confirm prediction and recommendation audit rows are created without requiring an external PostgreSQL server in tests; use SQLite test sessions or dependency overrides.
- [ ] Align dataset browser response fields with GUI expectations and canonical dataset naming.
- [ ] Add import validation endpoint only if it is needed for the MVP GUI; otherwise keep import validation in Streamlit to avoid unused API surface.
- [ ] Ensure Alembic migration state matches SQLAlchemy models after any schema changes.
- [ ] Make external PubChem lookup failures non-fatal and user-readable in both API and GUI.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api_prediction.py tests/test_api_dataset_browser.py tests/test_db_schema.py -v
.\.venv\Scripts\python.exe -m app.db.init_db
.\.venv\Scripts\python.exe scripts/seed_db.py
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001
```

Expected result: API tests pass; local DB initialization and seeding complete; the FastAPI app starts and `/health` returns `{"status":"ok"}`.

### Milestone 5: Upgrade Streamlit GUI Dashboards For Lab Onboarding

**Outcome:** The GUI is useful for internal lab review: it shows dataset readiness, model evaluation, prediction explanations, recommendation tradeoffs, and import validation feedback.

**Files to modify or create:**
- Modify: `app/gui/streamlit_app.py`
- Modify: `app/services/data_loader.py`
- Modify: `app/services/internal_validation.py`
- Modify: `app/services/predictor.py`
- Modify: `app/services/recommendation.py`
- Create if needed: `tests/test_gui_data_loaders.py`

**Checklist:**
- [ ] Dashboard page: show record counts, compound counts, source distribution, matrix distribution, missing-field summary, and RT/quality scatter using the processed master dataset when present.
- [ ] Dataset browser page: read canonical processed data first, then fall back to mock browser records; support filters for source, matrix, compound, column chemistry, ion mode, and success flag.
- [ ] Model evaluation page: surface `reports/model_training_summary.md`, `reports/test_predictions.csv`, `reports/feature_importance.csv`, and Plotly HTML plot links or embedded charts.
- [ ] Admin/import page: validate uploaded internal CSV with `validate_internal_lab_frame`, show blocking errors and warnings, and display the generated template/data dictionary paths.
- [ ] Forward prediction page: clearly display model name, confidence, uncertainty, out-of-domain status, and risk components from the trained model path.
- [ ] Recommendation page: show ranked candidates, target RT delta, predicted quality, runtime, confidence, and explanation; handle the case where quality filtering removes all candidates.
- [ ] Add data-loader tests for processed-data fallback behavior and report loading behavior.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_gui_data_loaders.py tests/test_recommendation.py -v
.\.venv\Scripts\python.exe scripts/assemble_dataset.py
.\.venv\Scripts\python.exe scripts/train_models.py
.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501
```

Expected result: tests pass; the GUI starts on port 8501; every page loads with processed artifacts present; uploaded invalid internal CSV rows produce readable validation feedback.

### Milestone 6: Internal Lab Onboarding Package And Documentation

**Outcome:** A lab scientist or internal developer can onboard historical LC-MS/MS runs, retrain models, inspect results, and run the MVP locally.

**Files to modify or create:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `data/templates/internal_lab_historical_runs_template.csv`
- Modify: `data/templates/internal_lab_data_dictionary.md`
- Modify: `docs/implementation_plan.md` only if the plan changes after implementation
- Create if needed: `docs/internal_lab_onboarding.md`
- Create if needed: `docs/model_evaluation_notes.md`
- Create if needed: `docs/screenshots/*.png`

**Checklist:**
- [ ] Add an internal lab onboarding guide with the exact CSV template, validation rules, import command, training command, GUI command, and expected outputs.
- [ ] Document which columns are required for MVP training versus optional metadata for future modeling.
- [ ] Document demo-data limitations and the minimum internal data volume needed before interpreting model metrics as decision-support evidence.
- [ ] Add screenshots for Dashboard, Forward prediction, Method recommendation, Dataset browser, Model evaluation, and Admin/import after GUI polish.
- [ ] Update README setup commands to consistently use `.\.venv\Scripts\python.exe` on Windows.
- [ ] Document artifact paths and how to regenerate them.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe scripts/assemble_dataset.py --source data/mock_training_records.csv
.\.venv\Scripts\python.exe scripts/train_models.py
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001
```

Expected result: onboarding commands reproduce the processed dataset, model artifact, reports, GUI, and API from a clean local checkout with dependencies installed.

### Milestone 7: Final Release Verification And Integration

**Outcome:** The MVP is ready for the user's requested major commits and final push by the main integrating agent.

**Files to modify or create:**
- Modify only files intentionally changed by previous milestones.
- Do not include incidental cache files, virtualenv files, local databases, or unreviewed generated artifacts.

**Checklist:**
- [ ] Run the full test suite.
- [ ] Regenerate dataset, models, reports, and plots intentionally.
- [ ] Start API and GUI once from the virtualenv and smoke-test the main workflows.
- [ ] Review generated reports for demo-data caveats and internal-data next steps.
- [ ] Review changed files before each commit and exclude incidental local output.
- [ ] Prepare a release summary with dataset, model, GUI, API, docs, risks, and verification evidence.

**Verification commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe scripts/assemble_dataset.py
.\.venv\Scripts\python.exe scripts/train_models.py
.\.venv\Scripts\python.exe -m app.db.init_db
.\.venv\Scripts\python.exe scripts/seed_db.py
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001
.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501
```

Expected result: all tests pass; dataset/training commands complete; API and GUI start successfully; dashboards and prediction/recommendation flows work against the trained artifact.

---

## 3. File-Level Task Checklist

Use this checklist as the implementation work queue. Keep each item scoped and verify it with the milestone commands above.

### Dataset And Import

- [ ] `app/schemas/dataset.py`: finalize canonical columns, required internal columns, and numeric canonical columns.
- [ ] `app/services/internal_validation.py`: harden validation for required fields, value ranges, ion modes, organic percentages, duplicates, SMILES, and issue serialization.
- [ ] `app/services/dataset_assembly.py`: preserve provenance, normalize aliases, handle invalid structures, deduplicate deterministically, and report missing fields.
- [ ] `app/adapters/internal_lab_template.py`: align adapter output with canonical schema and internal template columns.
- [ ] `scripts/assemble_dataset.py`: expose useful CLI args, print row-count diagnostics, and write deterministic processed outputs.
- [ ] `data/templates/internal_lab_historical_runs_template.csv`: keep sample row valid and representative.
- [ ] `data/templates/internal_lab_data_dictionary.md`: document every template column and accepted values.
- [ ] `tests/test_internal_lab_validation.py`: cover valid and invalid internal imports.
- [ ] `tests/test_dataset_assembly.py`: cover aliasing, provenance, invalid SMILES notes, and deduplication.
- [ ] `tests/test_assemble_dataset_cli.py`: cover CLI output paths and counts.

### Feature Engineering

- [ ] `app/services/descriptors.py`: keep RDKit descriptors deterministic and invalid-SMILES errors explicit.
- [ ] `app/services/features.py`: align prediction-time feature construction with training-time feature names.
- [ ] `app/services/feature_engineering.py`: freeze model matrix columns, quality proxy logic, feature groups, and fingerprint default behavior.
- [ ] `tests/test_descriptors.py`: cover canonicalization, descriptor ranges, and invalid structures.
- [ ] `tests/test_feature_engineering.py`: cover model-matrix fields and quality proxy.
- [ ] `tests/test_model_matrix_contract.py`: assert stable columns and training/prediction feature compatibility.

### Modeling And Evaluation

- [ ] `app/models/baseline.py`: keep legacy baseline loadable until trained bundle fully replaces it.
- [ ] `app/models/training.py`: add robust validation, applicability-domain metadata, evaluation outputs, and reproducible reports.
- [ ] `app/services/predictor.py`: load trained bundle first, use metadata for out-of-domain checks, and keep baseline/heuristic fallbacks.
- [ ] `scripts/train_baselines.py`: keep baseline command functional or document it as legacy.
- [ ] `scripts/train_models.py`: make the primary training command deterministic and failure-readable.
- [ ] `tests/test_training_pipeline.py`: train on a small fixture and assert metrics/report/artifact outputs.
- [ ] `tests/test_predictor_trained_bundle.py`: assert predictor loads the trained artifact and returns RT, quality, confidence, uncertainty, and model metadata.
- [ ] `reports/model_training_summary.md`: regenerate after final training and include limitations.
- [ ] `reports/test_predictions.csv`: regenerate after final training.
- [ ] `reports/feature_importance.csv`: regenerate after final training.
- [ ] `data/processed/models/trained_forward_bundle.joblib`: regenerate intentionally after final training.
- [ ] `data/processed/plots/*.html`: regenerate intentionally after final training.

### API And Database

- [ ] `app/api/main.py`: align response payloads, error handling, audit logging, and dataset browser filters.
- [ ] `app/db/models.py`: update schema only where needed for import provenance, auditability, or model outputs.
- [ ] `app/db/init_db.py`: keep local initialization reliable.
- [ ] `app/db/session.py`: support dependency overrides in tests.
- [ ] `alembic/env.py`: keep migration configuration aligned.
- [ ] `alembic/versions/*.py`: add migration if schema changes.
- [ ] `app/schemas/method.py`: keep request schemas consistent with GUI and API needs.
- [ ] `app/schemas/prediction.py`: include uncertainty, confidence, out-of-domain, risks, explanations, and recommendation fields.
- [ ] `tests/test_api_prediction.py`: cover prediction and audit persistence.
- [ ] `tests/test_api_dataset_browser.py`: cover filters and response shape.
- [ ] `tests/test_db_schema.py`: cover schema initialization or migration assumptions.

### GUI And Onboarding

- [ ] `app/gui/streamlit_app.py`: upgrade dashboards, model evaluation, import validation, and recommendation/prediction displays.
- [ ] `app/services/data_loader.py`: load processed datasets/reports first and mock data as fallback.
- [ ] `tests/test_gui_data_loaders.py`: cover processed-data and fallback-loading behavior.
- [ ] `README.md`: update local setup, commands, artifact regeneration, and internal onboarding entry points.
- [ ] `docs/internal_lab_onboarding.md`: create lab-facing import/train/evaluate/run guide.
- [ ] `docs/model_evaluation_notes.md`: create model caveats and interpretation notes.
- [ ] `docs/screenshots/*.png`: add final GUI screenshots if requested by the release owner.

---

## 4. Verification Command Matrix

Use `.\.venv\Scripts\python.exe` for all Python entry points.

| Milestone | Commands |
| --- | --- |
| Dataset contracts/import | `.\.venv\Scripts\python.exe -m pytest tests/test_internal_lab_validation.py tests/test_dataset_assembly.py -v`<br>`.\.venv\Scripts\python.exe -m pytest tests/test_assemble_dataset_cli.py -v`<br>`.\.venv\Scripts\python.exe scripts/assemble_dataset.py --source data/mock_training_records.csv --output-dir data/processed --templates-dir data/templates` |
| Feature engineering | `.\.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py tests/test_descriptors.py tests/test_model_matrix_contract.py -v`<br>`.\.venv\Scripts\python.exe scripts/assemble_dataset.py` |
| Training/evaluation | `.\.venv\Scripts\python.exe -m pytest tests/test_training_pipeline.py tests/test_predictor_trained_bundle.py -v`<br>`.\.venv\Scripts\python.exe scripts/train_models.py --matrix data/processed/model_matrix.csv --artifact data/processed/models/trained_forward_bundle.joblib --report-dir reports --plots-dir data/processed/plots`<br>`.\.venv\Scripts\python.exe -m pytest tests -v` |
| API/database | `.\.venv\Scripts\python.exe -m pytest tests/test_api_prediction.py tests/test_api_dataset_browser.py tests/test_db_schema.py -v`<br>`.\.venv\Scripts\python.exe -m app.db.init_db`<br>`.\.venv\Scripts\python.exe scripts/seed_db.py`<br>`.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001` |
| GUI/dashboard | `.\.venv\Scripts\python.exe -m pytest tests/test_gui_data_loaders.py tests/test_recommendation.py -v`<br>`.\.venv\Scripts\python.exe scripts/assemble_dataset.py`<br>`.\.venv\Scripts\python.exe scripts/train_models.py`<br>`.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501` |
| Onboarding/docs | `.\.venv\Scripts\python.exe scripts/assemble_dataset.py --source data/mock_training_records.csv`<br>`.\.venv\Scripts\python.exe scripts/train_models.py`<br>`.\.venv\Scripts\python.exe -m pytest tests -v`<br>`.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501`<br>`.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001` |
| Final release | `.\.venv\Scripts\python.exe -m pytest tests -v`<br>`.\.venv\Scripts\python.exe scripts/assemble_dataset.py`<br>`.\.venv\Scripts\python.exe scripts/train_models.py`<br>`.\.venv\Scripts\python.exe -m app.db.init_db`<br>`.\.venv\Scripts\python.exe scripts/seed_db.py`<br>`.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001`<br>`.\.venv\Scripts\python.exe -m streamlit run app/gui/streamlit_app.py --server.headless true --server.port 8501` |

When a listed test file does not exist yet, create it as part of the corresponding milestone before running that command.

---

## 5. Commit And Push Policy

This section is policy for the main integrating agent. Do not perform git operations from planning-only or subagent-only tasks unless explicitly authorized by the main agent.

- No staging, committing, branch creation, remote changes, or pushing should happen during planning-only work.
- Commit only after a milestone's tests and command-line verification pass.
- Use small milestone commits so failures can be bisected:
  - `feat: harden internal dataset import`
  - `feat: stabilize model matrix generation`
  - `feat: train and evaluate forward models`
  - `feat: add api workflow coverage`
  - `feat: upgrade streamlit lab dashboards`
  - `docs: add internal lab onboarding guide`
- Before each commit, review changed files and exclude virtualenv files, caches, local databases, accidental logs, and unrequested generated artifacts.
- Include generated artifacts only when they are intentional MVP deliverables: processed demo CSVs, model bundle, report CSVs/markdown, and Plotly evaluation HTML.
- Push only after the final release verification commands pass and the release owner confirms that generated artifacts should be included.
- If the repository has unrelated user changes, leave them untouched. Coordinate with the main agent before editing a file that already contains unrelated work.

---

## 6. Risks And Blockers

- **Small demo dataset:** Current checked-in training report uses 12 rows, so RT metrics are unstable and quality metrics are not meaningful. Real internal historical runs are required before treating the model as decision-support.
- **Public dataset sparsity:** Public RT datasets often lack matrix, sample prep, peak shape, S/N, MS transition, and instrument metadata. The plan should preserve missingness and provenance rather than pretending these fields are known.
- **Quality target validity:** `quality_score` is currently a proxy when explicit values are absent. Internal acceptance rules should define the production quality target.
- **Domain shift:** Models trained on public or mock data may not transfer to a specific lab's instruments, columns, matrices, and sample-prep protocols. Source-aware validation and internal calibration are required.
- **Applicability-domain limits:** Current predictor fallback uses broad heuristic bounds. Trained model metadata should drive out-of-domain warnings once enough data exists.
- **Artifact churn:** Training artifacts and Plotly HTML files can change when data or scikit-learn versions change. Regenerate and commit them only intentionally.
- **Database dependency:** API audit workflows depend on database configuration. Tests should use dependency overrides or isolated local databases so CI/local verification is reliable.
- **GUI smoke testing:** Streamlit pages need manual or browser smoke checks after data-loader changes because many failures appear only when pages render with real artifacts.
- **External services:** PubChem network lookups can fail or be unavailable. Lookup failures must remain non-fatal.
- **Regulatory/lab governance:** This MVP should be framed as method-development decision support, not validated regulated software, until internal validation, audit, and change-control procedures exist.

