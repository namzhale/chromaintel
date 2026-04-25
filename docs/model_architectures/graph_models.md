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

`scripts/prepare_dl_datasets.py` now provides the dependency-light data view for future graph experiments. It writes `data/processed/dl/graph_manifest.csv` with canonical structure identifiers, LC/MS method fields, `rt_min`, deterministic or source-provided split labels, and graph-readiness metadata. The manifest is intentionally a CSV contract, not a PyTorch/PyG/DGL dataset object.

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

## DL Manifest Contract

The graph manifest contains:

- compound identity: `canonical_smiles`, `inchikey`, `source_dataset`, `source_record_id`, `compound_name`;
- method context: column, mobile phase, gradient, temperature, flow, injection, ion mode, precursor/product m/z, matrix;
- label/split fields: `rt_min`, `split`;
- graph metadata: `graph_backend`, `graph_training_enabled`, `graph_dependency_status`.

SMILES validity is checked through the existing RDKit-backed descriptor utility. Invalid or missing SMILES rows are filtered before writing the manifest. `--max-rows` caps rows before canonicalization so smoke runs remain fast on large processed source files.

## Intentional Limits

No graph model training, grouped CV, checkpointing, GPU execution, or Chemprop CLI wrapping is implemented in this slice. These stubs exist so future graph work can report dependency readiness and featurization health without changing the current CPU-first tabular training path in `app/models/training.py`.

Before enabling training, add explicit dependency approval, grouped compound splits, source-family holdouts, retention-order diagnostics, uncertainty metadata, and applicability-domain reporting comparable to the existing tabular training reports.
