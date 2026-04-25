# Dependency-Gated Graph Models

Date: 2026-04-25

This note documents optional molecular graph model support for ChromaIntel. The implementation is intentionally a set of dependency-gated stubs, not a training runtime. It keeps graph neural network dependencies out of the mandatory install while preserving a tested smoke path for RDKit molecule graph featurization.

## Runtime Contract

`app/models/graph_optional.py` exposes:

- `detect_graph_availability()` for optional backend detection without importing PyTorch, PyG, DGL, or Chemprop.
- `featurize_molecule_graph(smiles)` for RDKit-backed atom and bond graph features.
- `GraphModelConfig` for recording graph experiment intent.
- `graph_model_specs()` for GCN, GAT, MPNN, D-MPNN, and Chemprop-style dependency requirements.
- `graph_skip_report(config)` for serializable graceful-skip metadata.
- `tiny_torch_cpu_smoke()` for a one-layer CPU forward pass only when PyTorch is already installed.

## Current Backend Status

Observed in the local `.venv` on 2026-04-25:

| Backend | Status |
| --- | --- |
| RDKit | available |
| PyTorch | missing |
| PyTorch Geometric | missing |
| DGL | missing |
| Chemprop | missing |

## Model Families

| Family | Required backends | Current status | Training enabled |
| --- | --- | --- | --- |
| GCN | RDKit, PyTorch, PyTorch Geometric | skipped_missing_dependency | no |
| GAT | RDKit, PyTorch, PyTorch Geometric | skipped_missing_dependency | no |
| MPNN | RDKit, PyTorch | skipped_missing_dependency | no |
| D-MPNN | RDKit, PyTorch, Chemprop | skipped_missing_dependency | no |
| Chemprop-style D-MPNN | RDKit, PyTorch, Chemprop | skipped_missing_dependency | no |

## Featurization Smoke Path

The RDKit featurizer converts a molecule into:

- `atom_features`: numeric atom descriptors including atomic number, degree, charge, hydrogens, aromaticity, ring membership, and simple hybridization flags.
- `edge_index`: directed bond pairs with shape `(2, n_directed_edges)`.
- `edge_features`: bond descriptors including single/double/triple/aromatic flags, conjugation, and ring membership.

For ethanol (`CCO`), the smoke path produces 3 atoms and 4 directed edges.

## Intentional Limits

No graph model training, grouped CV, checkpointing, GPU execution, or Chemprop CLI wrapping is implemented in this slice. These stubs exist so future graph work can report dependency readiness and featurization health without changing the current CPU-first tabular training path in `app/models/training.py`.

Before enabling training, add explicit dependency approval, grouped compound splits, source-family holdouts, retention-order diagnostics, uncertainty metadata, and applicability-domain reporting comparable to the existing tabular training reports.
