# Next Data And Method-Conditioned Benchmark Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend ChromaIntel with stronger public-data ingestion contracts, canonical schema documentation, method/source/column evaluation, benchmark reporting, and analyst-facing dashboard updates while preserving the current MVP interfaces.

**Architecture:** Reuse the existing `app/`, `scripts/`, `tests/`, `reports/`, and `data/processed/` architecture. New capabilities should extend existing CLIs and services before adding wrappers. Optional deep-learning and private/bulk data paths must be dependency-gated or manual-ingestion stubs.

**Tech Stack:** Python, pandas, RDKit, scikit-learn, XGBoost/CatBoost when available, FastAPI/Streamlit, matplotlib/PDF reporting, SQLAlchemy/Alembic for database migration documentation.

---

## Guardrails

- Search existing implementation before adding files.
- Do not duplicate adapters, reports, schema concepts, model wrappers, or CLIs.
- Do not require network downloads during tests.
- Do not make GPU/deep-learning dependencies mandatory.
- Every agent writes `docs/agent_reports/20260425_<agent_name>.md` with an "Existing implementation audit" section.
- Subagents must not stage, commit, push, create branches, edit remotes, or revert unrelated work.

## Task 1: Canonical Schema And Duplicate Policy

**Files:**
- Create: `docs/canonical_schema.md`
- Create: `app/schemas/canonical.py`
- Create: `tests/test_canonical_schema.py`
- Optionally create migration: `alembic/versions/*_canonical_registry_views.py`

Steps:

- [ ] Audit existing SQLAlchemy, Pydantic, and dataset schema files.
- [ ] Add typed canonical registry field lists and validation helpers for compound, LC method, MS method, sample context, observation, and peak metrics.
- [ ] Add `method_hash()` using column, solvents, pH, gradient summary, flow, temperature, runtime, and chromatography mode.
- [ ] Add `source_quality_score()` weighted by structure, RT, LC metadata, MS metadata, sample context, and peak metrics completeness.
- [ ] Test method hash determinism, duplicate-key composition, and quality score monotonicity.
- [ ] Document duplicate policy and schema in `docs/canonical_schema.md`.

## Task 2: Public RT Adapter Contracts

**Files:**
- Create or extend: `app/adapters/public_rt.py`
- Extend: `scripts/fetch_public_datasets.py`
- Create fixtures under: `tests/fixtures/public_rt/`
- Create: `tests/test_public_rt_adapters.py`
- Create docs under: `docs/data_sources/`
- Create reports under: `reports/ingestion/`

Steps:

- [ ] Audit existing RepoRT, MCMRT, METLIN, and local-public ingestion code.
- [ ] Add config-first tabular adapter for PredRet, GMCRT-like, and MultiConditionRT-style CSV/XLSX fixtures.
- [ ] Add METLIN SMRT manual-ingestion path and docs without live bulk download.
- [ ] Generate missingness and duplicate reports for fixture imports.
- [ ] Keep output compatible with existing canonical nullable schema.

## Task 3: Enrichment And Structure Standardization

**Files:**
- Extend: `app/adapters/pubchem.py`, `app/adapters/chembl.py`
- Create or extend: `app/services/compound_identity.py`
- Create fixtures under: `tests/fixtures/enrichment/`
- Create: `tests/test_compound_identity.py`
- Create docs/report under: `reports/enrichment/`

Steps:

- [ ] Audit existing PubChem/ChEMBL clients and RDKit descriptor standardization.
- [ ] Add offline-safe cache loader and mocked fixture resolver.
- [ ] Add identity confidence labels: exact InChIKey, first-block match, PubChem CID, ChEMBL ID, name-only low confidence.
- [ ] Reject ambiguous name-only mappings by default.
- [ ] Write unresolved/ambiguous report fixtures.

## Task 4: Method-Conditioned Evaluation Matrix

**Files:**
- Extend: `app/models/training.py`
- Extend: `tests/test_training.py`
- Create: `reports/evaluation_matrix.csv`, `reports/evaluation_matrix.md`, `reports/split_manifest.json`

Steps:

- [ ] Audit current GroupKFold, source holdout, and retention-order diagnostics.
- [ ] Add method-holdout and column-family-holdout diagnostics using existing model zoo.
- [ ] Add normalized MAE as percent of runtime and Spearman metrics.
- [ ] Persist evaluation matrix and split manifest.
- [ ] Keep current `scripts/train_models.py` behavior backward compatible.

## Task 5: Benchmark Matrix And Dashboard

**Files:**
- Extend: `scripts/generate_dashboard_pdf.py`
- Extend: `app/gui/streamlit_app.py`
- Create: `reports/model_benchmark_matrix.csv`
- Create: `reports/model_benchmark_matrix.md`
- Create: `reports/model_benchmark_matrix.json`

Steps:

- [ ] Audit existing PDF and Streamlit evaluation pages.
- [ ] Add benchmark matrix from CV, holdout, method-holdout, column-family holdout, and retention-order outputs.
- [ ] Add Russian PDF panels for dataset coverage, benchmark matrix, retention-order, and next roadmap.
- [ ] Add Streamlit views that degrade gracefully when optional reports are missing.

## Task 6: Optional Model Families And Stubs

**Files:**
- Create docs under: `docs/model_architectures/`
- Optionally create stubs under: `app/models/optional/`
- Create tests for graceful skip.

Steps:

- [ ] Audit existing XGBoost/CatBoost/ExtraTrees/RandomForest/HGB support.
- [ ] Document graph and transformer status as optional dependency-gated branches.
- [ ] Add no-download smoke stubs for graph/transformer benchmarks if no dependencies exist.
- [ ] Ensure benchmark matrix marks skipped optional models explicitly.

## Task 7: Verification And Release

**Files:**
- Update: `README.md`
- Create: `docs/implementation_report_data_models.md`

Steps:

- [ ] Run `.\.venv\Scripts\python.exe -m pytest tests -q`.
- [ ] Run `.\.venv\Scripts\python.exe -m py_compile app\models\training.py app\gui\streamlit_app.py app\adapters\literature_parser.py scripts\fetch_public_datasets.py scripts\extract_lcms_entities.py scripts\train_models.py`.
- [ ] Run `git diff --check`.
- [ ] Run feasible training/report smoke.
- [ ] Commit and push after checks pass.
