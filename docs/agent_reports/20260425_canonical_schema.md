# Agent 1 Canonical Schema Report

## Existing implementation audit

Audited `app/schemas/dataset.py`, `app/schemas/method.py`,
`app/db/models.py`, `app/services/dataset_assembly.py`,
`tests/test_dataset_assembly.py`, and existing docs under `docs/`.

## already exists

- Flat nullable training dataset columns in `app/schemas/dataset.py`.
- Pydantic method input schemas in `app/schemas/method.py`.
- SQLAlchemy entities for compounds, structures, datasets, methods, gradient
  steps, MS settings, runs, peak metrics, predictions, recommendations, and
  audit logs in `app/db/models.py`.
- Dataset assembly deduplication by compound identity, LC method fields, and
  rounded retention time in `app/services/dataset_assembly.py`.
- Tests covering normalization and existing master-dataset deduplication in
  `tests/test_dataset_assembly.py`.

## partially exists

- Canonical schema concepts existed as flat dataset columns, but not as
  registry-level field groups.
- Duplicate handling existed in dataset assembly, but there was no reusable
  registry duplicate key helper.
- `quality_score` existed as a column, but there was no source completeness
  score helper.

## newly implemented

- Added grouped registry fields for compound, LC method, MS method, sample
  context, observation, peak metrics, and provenance.
- Added required-field and lightweight registry validation helpers.
- Added deterministic `method_hash()` over normalized LC method fields.
- Added `duplicate_key()` for registry duplicate policy.
- Added `source_quality_score()` with weighted completeness scoring.
- Added focused tests for field groups, method hash determinism, duplicate-key
  composition, quality-score monotonicity, and blank required values.
- Added canonical schema and duplicate policy documentation.

## intentionally skipped

- No Alembic migration was added because this slice adds docs and pure schema
  helpers only; no database tables, views, or columns were changed.
- No training, adapter, GUI, remote, branch, staging, commit, or push work was
  performed.

## files reused

- `app/schemas/dataset.py`
- `app/schemas/method.py`
- `app/db/models.py`
- `app/services/dataset_assembly.py`
- `tests/test_dataset_assembly.py`
- `docs/implementation_plan_next_slice.md`

## files modified

- None of the pre-existing scoped files were modified.

## files created

- `app/schemas/canonical.py`
- `docs/canonical_schema.md`
- `tests/test_canonical_schema.py`
- `docs/agent_reports/20260425_canonical_schema.md`

## verification

- Red test run before implementation:
  `.\.venv\Scripts\python.exe -m pytest tests\test_canonical_schema.py -q`
  failed with `ModuleNotFoundError: No module named 'app.schemas.canonical'`.
- Focused test run after implementation:
  `.\.venv\Scripts\python.exe -m pytest tests\test_canonical_schema.py -q`
  passed with `5 passed in 0.02s`.
- Compile check:
  `.\.venv\Scripts\python.exe -m py_compile app\schemas\canonical.py tests\test_canonical_schema.py`
  exited 0.
- Whitespace check:
  `git diff --check -- app/schemas/canonical.py docs/canonical_schema.md tests/test_canonical_schema.py docs/agent_reports/20260425_canonical_schema.md`
  exited 0.
- Full suite sanity check:
  `.\.venv\Scripts\python.exe -m pytest tests -q` failed during collection
  with `ModuleNotFoundError: No module named 'app.services.compound_identity'`
  from `tests/test_compound_identity.py`, which is outside this agent scope.
