# Agent 7 Graph Model Agent Report

Date: 2026-04-25

## Existing implementation audit

- `requirements.txt` pins RDKit, scikit-learn, XGBoost, and CatBoost. It does not include `torch`, `torch-geometric`, `dgl`, or `chemprop`.
- `app/models/training.py` already owns the active CPU tabular training path and uses local imports for optional XGBoost/CatBoost candidates.
- `docs/model_architectures/optional_models_status.md` previously listed GCN, GAT, MPNN, and D-MPNN/Chemprop as roadmap-only dependency-gated work.
- Existing tests cover descriptors, feature engineering, training, optional model status documentation, and recommendation behavior. No graph optional test module existed.

## Already exists

- RDKit dependency and descriptor smoke coverage.
- CPU-first tabular model training with grouped CV, holdout diagnostics, and report generation.
- Documentation policy that optional neural/graph dependencies must not be added implicitly.

## Partially exists

- Optional model dependency gating existed for XGBoost and CatBoost in `app/models/training.py`.
- Graph model families were documented as roadmap items, but had no import-safe runtime detection or featurization smoke path.

## Newly implemented

- Added `app/models/graph_optional.py` with import-safe availability detection for RDKit, PyTorch, PyG, DGL, and Chemprop.
- Added RDKit molecule graph featurization returning atom features, directed edge indices, and bond features.
- Added `GraphModelConfig`, `GraphModelSpec`, graph family metadata, and serializable skip reports.
- Added optional `tiny_torch_cpu_smoke()` that runs only a one-layer CPU forward pass when PyTorch is already installed.
- Added tests that pass without PyTorch, PyG, DGL, or Chemprop.
- Added graph model architecture documentation and a skipped benchmark/status CSV.

## Intentionally skipped

- No PyTorch, PyG, DGL, or Chemprop dependency was added to `requirements.txt`.
- No graph model training, GPU execution, checkpointing, Chemprop CLI wrapper, or full benchmark was run.
- No edits were made to `app/models/training.py`; the active training path remains tabular and CPU-first.
- No staging, commit, push, branch creation, remote edits, or unrelated reverts were performed.

## Files reused

- `requirements.txt`
- `app/models/training.py`
- `docs/model_architectures/optional_models_status.md`
- Existing `tests/` layout and pytest conventions

## Files modified

- None of the audited existing files were modified for this slice.

## Files created

- `app/models/graph_optional.py`
- `tests/test_graph_optional.py`
- `docs/model_architectures/graph_models.md`
- `docs/agent_reports/20260425_graph_models.md`
- `reports/benchmarks/graph_models.csv`

## Verification

Commands run:

```powershell
Get-ChildItem -Force
Get-Content -Path requirements.txt
Get-Content -Path app\models\training.py
Get-Content -Path docs\model_architectures\optional_models_status.md
rg --files tests app\models docs reports
Get-ChildItem -Recurse -File tests,app\models,docs,reports | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -File tests | Select-Object -ExpandProperty FullName
Get-ChildItem -Path app\models -Force
git status --short
Get-Content -Path tests\test_optional_model_status.py
Get-Content -Path tests\test_descriptors.py
Get-Content -Path tests\test_training.py -TotalCount 220
Get-Content -Path app\models\__init__.py
Get-Content -Path app\services\feature_engineering.py -TotalCount 220
.\.venv\Scripts\python.exe -m pytest tests\test_graph_optional.py
.\.venv\Scripts\python.exe -
.\.venv\Scripts\python.exe -m pytest tests\test_graph_optional.py tests\test_optional_model_status.py
.\.venv\Scripts\python.exe -m pytest
```

Verification results:

- `rg --files tests app\models docs reports` failed because `rg.exe` was access-denied in this workspace; PowerShell file enumeration was used instead.
- Initial graph test run failed with `ModuleNotFoundError: No module named 'app.models.graph_optional'`, as expected for the red TDD step.
- Final focused graph test run: `6 passed`.
- Focused graph plus optional-status regression run: `7 passed`.
- Full project test run: `63 passed, 1 warning in 69.59s`.
- Runtime graph availability in `.venv`: RDKit available; PyTorch, PyG, DGL, and Chemprop missing.
- Ethanol graph smoke path: 3 atoms, 4 directed edges.
- Tiny PyTorch smoke path: skipped with `torch_missing`; no training run.
