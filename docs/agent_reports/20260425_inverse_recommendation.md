# Inverse Recommendation Agent Report

## Existing Implementation Audit

- `app/services/recommendation.py` is the only recommendation engine module found. No duplicate inverse recommendation implementation was added.
- `RecommendationEngine` already enumerated constrained candidate methods, called the injected `ForwardPredictor`, ranked by RT fit, quality, runtime, confidence, and AD penalty, and returned score components.
- `config/recommendation_search_space.json` already drove the bounded search space for columns, solvent systems, pH, flow, temperature, gradient end times, and max runtime.
- `tests/test_recommendation.py` already covered ranking stability, score decomposition keys, AD penalty behavior, checked-in config parsing, and method runtime calculation.
- `app/services/predictor.py` already prefers `trained_forward_bundle.joblib` over the legacy baseline and heuristic fallback. The trained path already exposes confidence, uncertainty, feature summary, and applicability-domain metadata, but recommendation output did not preserve most of those details.
- No nearest/known-method hook existed. Future BO/active-learning status was only documented elsewhere, not represented in recommendation config.

## Changed Files

- `app/schemas/prediction.py`
  - Added recommendation output fields for `constraints`, `reason_codes`, `forward_prediction`, and `nearest_known_methods`.
- `app/services/recommendation.py`
  - Preserves applied inverse constraints on each recommendation.
  - Expands score decomposition with weighted contribution terms.
  - Adds reason codes for model source, RT match, quality, runtime, AD/OOD status, constraints, and nearest-method availability.
  - Surfaces forward-predictor metadata including model note, uncertainty, AD method, feature summary, and risks.
  - Adds optional `known_methods` input and lightweight nearest-known-method similarity hooks without new dependencies.
  - Adds config-backed roadmap hooks for Bayesian optimization and active learning.
- `config/recommendation_search_space.json`
  - Added disabled `optimization_hooks` entries for Bayesian optimization and active learning.
- `tests/test_recommendation.py`
  - Added tests for constraints/reason codes/forward metadata, nearest-known-method hooks, and optimization hook config parsing.

## Verification Results

Red check before implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_recommendation.py -q
```

Result: `3 failed, 4 passed in 1.82s`.

Expected failures:

- Missing `RecommendationCandidate.constraints`.
- `RecommendationEngine.__init__()` did not accept `known_methods`.
- Missing `CandidateSearchSpace.optimization_hooks`.

Green targeted test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_recommendation.py -q
```

Result: `7 passed in 1.38s`.

Compile check:

```powershell
.\.venv\Scripts\python.exe -m py_compile app\services\recommendation.py app\schemas\prediction.py tests\test_recommendation.py
```

Result: exit 0, no output.

Diff whitespace check:

```powershell
git diff --check
```

Result: exit 0. Git emitted CRLF conversion warnings for existing dirty files and the touched files; no whitespace errors were reported.

## Known Limitations

- Nearest-known-method support is an in-memory hook for later retrieval/database wiring. It does not yet query historical runs.
- BO and active-learning hooks are roadmap/config placeholders only; no optimizer dependency or acquisition loop was added.
- Recommendation API request schema still exposes only the existing public constraint fields. Direct engine calls can use pH/flow/temperature/runtime constraints already present in `RecommendationEngine`.
- Full test suite and model retraining were not run because this slice was scoped to recommendation tests and the workspace contains unrelated active data/DL-prep changes.

## Git Safety

- No staging, commit, push, branch, remote, or revert operations were performed.
- Existing unrelated dirty files were left untouched.
