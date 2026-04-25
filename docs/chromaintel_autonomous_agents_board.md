# ChromaIntel Autonomous Agents Board

Date: 2026-04-25

## Current Slice Goal

Add public-data adapter contracts, canonical schema documentation, method-conditioned evaluation, benchmark reports, dashboard updates, and release verification without duplicating existing implementation.

## Global Rules For Agents

- Start with an existing-implementation audit.
- Do not stage, commit, push, create branches, edit remotes, or revert unrelated work.
- Use `.\.venv\Scripts\python.exe`.
- Keep scopes disjoint.
- Write a report to `docs/agent_reports/20260425_<agent_name>.md`.
- Add or update tests for every behavior change.

## Board

| Agent | Scope | Status | Primary Files |
| --- | --- | --- | --- |
| Agent 0 Orchestrator | Integration, plan, board, final report, verification | in progress | `docs/implementation_plan_next_slice.md`, `docs/chromaintel_autonomous_agents_board.md`, `docs/implementation_report_data_models.md` |
| Agent 1 Canonical Schema | Canonical registry schema, method hash, duplicate policy | completed | `app/schemas/canonical.py`, `docs/canonical_schema.md`, `tests/test_canonical_schema.py` |
| Agent 2 Public RT Adapters | PredRet/GMCRT/MultiConditionRT/METLIN manual fixture adapters | completed | `app/adapters/public_rt.py`, `tests/test_public_rt_adapters.py`, `docs/data_sources/`, `reports/ingestion/` |
| Agent 3 Enrichment | PubChem/ChEMBL/RDKit identity resolution, offline fixtures | completed | `app/services/compound_identity.py`, `tests/test_compound_identity.py`, `reports/enrichment/` |
| Agent 4 Evaluation | Method/column holdout, normalized MAE, benchmark matrix inputs | completed | `app/models/training.py`, `tests/test_training.py`, `reports/evaluation_matrix.*` |
| Agent 5 Reporting | Russian PDF/Streamlit benchmark and coverage panels | partially integrated | `reports/model_benchmark_matrix.*`, existing PDF/report paths |
| Agent 6 Optional Models | Graph/transformer/LightGBM dependency-gated status docs/stubs | completed | `docs/model_architectures/`, optional stubs/tests |
| Agent 7 Graph Models | GCN/GAT/MPNN/D-MPNN optional graph path | completed | `app/models/graph_optional.py`, `tests/test_graph_optional.py`, `reports/benchmarks/graph_models.csv` |
| Agent 8 Transformer Embeddings | ChemBERTa/MolFormer cached embedding path | completed | `app/models/transformer_embeddings.py`, `tests/test_transformer_embeddings.py`, `reports/benchmarks/transformer_embeddings.csv` |
| Agent 15 QA | Verification review and release risk checklist | pending final verification | `docs/agent_reports/20260425_qa_release.md` |

## Next Integration Checkpoint

1. Regenerate full training reports on the 15k matrix.
2. Regenerate the PDF dashboard.
3. Run full verification, commit, push.
