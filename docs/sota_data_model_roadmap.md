# ChromaIntel SOTA Data And Modeling Roadmap

## Goal

Move ChromaIntel from a useful CPU-first MVP toward a method-conditioned RT and risk platform without breaking the existing FastAPI, Streamlit, SQLAlchemy, and training pipeline.

The near-term target is not a single giant model. The production path is a stacked forward ensemble plus constrained inverse optimization:

- Tabular LC/MS model: CatBoost, XGBoost, ExtraTrees, HistGradientBoosting, Ridge baseline.
- Molecular side model: Morgan fingerprints now; graph/D-MPNN later when data volume and dependencies justify it.
- Ranking side task: retention-order proxy for pairs measured under the same method.
- Uncertainty layer: grouped validation, source/method holdout, split conformal intervals, applicability-domain penalties.
- Inverse recommendation: generate allowed method templates, predict RT/risk/uncertainty, then rerank.

## Autonomous Agent Workstreams

Every agent must follow `.AGENTS` and `.IMPLEMENT`: no staging, commits, pushes, branch creation, remote edits, unrelated rewrites, or destructive git commands.

### Data Agent

Scope:

- `app/adapters/*`
- `scripts/fetch_public_datasets.py`
- `data/public_source_manifest.json`
- `data/processed/external_*.csv`
- `reports/*data*`

Deliverables:

- Reviewed public data source inventory with license notes.
- One new normalized source only when bulk access is open and reproducible.
- Canonical mapping notes for compound identity, method fields, RT units, and provenance.

Priority sources:

- METLIN SMRT Figshare reviewed local export: high-value next source for large RP-LC RT pretraining and benchmarking, imported through the offline `--local-export` path after license/provenance review.
- PredRet/RT repository exports when downloadable as tabular data.
- GNPS/MassIVE or Metabolomics Workbench studies only when RT and method metadata can be mapped without scraping private pages.
- PMC/Europe PMC literature-mined examples as weakly labeled rows, stored separately from trusted repository rows.

### Modeling Agent

Scope:

- `app/models/training.py`
- `app/services/feature_engineering.py`
- `scripts/train_models.py`
- `tests/test_training.py`
- `reports/*model*`

Deliverables:

- Descriptor-only vs descriptor+Morgan fingerprint comparison.
- Grouped CV plus source/method-family holdout for all model families.
- Retention-order ranking proxy metrics.
- Conformal interval reporting by source family when enough calibration rows exist.

### Evaluation Agent

Scope:

- `scripts/generate_dashboard_pdf.py`
- `reports/chromaintel_dashboard_report.pdf`
- `reports/*.csv`
- `reports/*.md`

Deliverables:

- Russian PDF dashboard with no overlapping layout.
- Full checked model comparison table: validation, grouped CV, test, source-family holdout.
- Dataset coverage: sources, compounds, method families, missingness.
- Roadmap slide/page with next experiments and blockers.

### Validation Agent

Scope:

- `app/services/internal_validation.py`
- `tests/test_internal_lab_validation.py`
- `app/services/recommendation.py`
- `tests/test_recommendation.py`

Deliverables:

- Internal import preview: missingness, invalid rows, duplicates, issue table.
- Controlled vocabulary validation for ion mode and matrix.
- Gradient consistency checks.
- Required MRM transition checks when ion mode is known.
- Recommendation score decomposition and AD penalty tests.

## Implementation Phases

### Phase 1: Data Backbone

- Keep raw, processed, and canonical rows separate.
- Add source-quality and completeness metadata before adding weakly mined literature rows to training.
- Hash LC methods using column, solvents, pH, gradient summary, flow, temperature, and runtime.
- Keep `source_dataset` provenance for every row.

### Phase 2: CPU SOTA Baseline

- Add `--include-fingerprints` training path.
- Compare descriptor-only vs descriptor+Morgan models.
- Keep XGBoost and CatBoost optional but enabled in the current venv.
- Select best RT model by grouped CV, not random split.
- Report normalized MAE as percent of runtime.

### Phase 3: Ranking And Uncertainty

- Add same-method retention-order pair generation.
- Report pairwise accuracy, Spearman, and Kendall-style proxy where feasible.
- Add source-family conformal summaries.
- Penalize low-support/out-of-domain candidates in recommendation ranking.

### Phase 4: Bioanalytical Enrichment

- Keep provisional peak quality transparent until internal labels exist.
- Add internal success/failure, low-intensity, poor-resolution, carryover, and matrix-effect examples to templates.
- Add retrieval panels for nearest compounds and nearest successful methods.

### Phase 5: Medium-Term Architecture

When internal data volume grows enough, evaluate:

- Chemprop/D-MPNN compound encoder with LC tabular side features.
- Method encoder with gradient vector, solvent/additive tokens, pH, column family, dimensions, runtime, temperature, flow, polarity, instrument, matrix, and sample prep.
- Fusion with FiLM-style conditioning or cross-attention.
- Multitask heads for RT mean, RT quantiles, retention order, success/failure, peak risk, peak width, tailing, and matrix-effect risk.
- Mixture-of-experts by column family, source family, and assay family.

## Verification Gate

Before any milestone commit:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m py_compile app\models\training.py app\gui\streamlit_app.py app\adapters\literature_parser.py scripts\fetch_public_datasets.py scripts\extract_lcms_entities.py scripts\train_models.py
git diff --check
```

Training and report refresh:

```powershell
.\.venv\Scripts\python.exe scripts\assemble_dataset.py
.\.venv\Scripts\python.exe scripts\train_models.py
.\.venv\Scripts\python.exe scripts\generate_dashboard_pdf.py
```
