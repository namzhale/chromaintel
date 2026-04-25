from __future__ import annotations

import importlib.util
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


GRAPH_MODEL_FAMILIES = ("gcn", "gat", "mpnn", "d_mpnn", "chemprop_style")


@dataclass(frozen=True)
class GraphAvailability:
    """Optional dependency status for molecular graph experiments."""

    rdkit_available: bool
    torch_available: bool
    pyg_available: bool
    dgl_available: bool
    chemprop_available: bool

    @property
    def backend_status(self) -> dict[str, bool]:
        return {
            "rdkit": self.rdkit_available,
            "torch": self.torch_available,
            "torch_geometric": self.pyg_available,
            "dgl": self.dgl_available,
            "chemprop": self.chemprop_available,
        }


@dataclass(frozen=True)
class GraphModelConfig:
    """Configuration recorded for dependency-gated graph model stubs."""

    model_family: str
    hidden_dim: int = 64
    num_layers: int = 3
    dropout: float = 0.1
    readout: str = "mean"
    lr: float = 0.001
    epochs: int = 50
    batch_size: int = 32
    random_state: int = 42

    def __post_init__(self) -> None:
        if self.model_family not in GRAPH_MODEL_FAMILIES:
            raise ValueError(f"Unsupported graph model family: {self.model_family}")
        if self.hidden_dim <= 0:
            raise ValueError("hidden_dim must be positive")
        if self.num_layers <= 0:
            raise ValueError("num_layers must be positive")
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")


@dataclass(frozen=True)
class MoleculeGraph:
    """Numpy representation of an RDKit molecule graph."""

    smiles: str
    atom_features: np.ndarray
    edge_index: np.ndarray
    edge_features: np.ndarray

    @property
    def num_atoms(self) -> int:
        return int(self.atom_features.shape[0])

    @property
    def num_directed_edges(self) -> int:
        return int(self.edge_index.shape[1])


@dataclass(frozen=True)
class GraphModelSpec:
    """Dependency-gated graph model family metadata."""

    family: str
    display_name: str
    required_backends: tuple[str, ...]
    status: str
    missing_backends: tuple[str, ...]
    training_enabled: bool = False


def detect_graph_availability() -> GraphAvailability:
    """Detect graph-model dependencies without importing optional stacks."""

    return GraphAvailability(
        rdkit_available=importlib.util.find_spec("rdkit") is not None,
        torch_available=importlib.util.find_spec("torch") is not None,
        pyg_available=importlib.util.find_spec("torch_geometric") is not None,
        dgl_available=importlib.util.find_spec("dgl") is not None,
        chemprop_available=importlib.util.find_spec("chemprop") is not None,
    )


def featurize_molecule_graph(smiles: str) -> MoleculeGraph:
    """Convert a SMILES string to a small RDKit-backed graph smoke fixture."""

    try:
        from rdkit import Chem
    except Exception as exc:  # pragma: no cover - exercised only when RDKit is absent
        raise RuntimeError("RDKit is required for molecule graph featurization") from exc

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES for graph featurization: {smiles}")

    atom_features = np.asarray([_atom_features(atom) for atom in mol.GetAtoms()], dtype=np.float32)
    edge_pairs: list[tuple[int, int]] = []
    edge_features: list[list[float]] = []
    for bond in mol.GetBonds():
        begin = int(bond.GetBeginAtomIdx())
        end = int(bond.GetEndAtomIdx())
        features = _bond_features(bond)
        edge_pairs.extend([(begin, end), (end, begin)])
        edge_features.extend([features, features])

    if edge_pairs:
        edge_index = np.asarray(edge_pairs, dtype=np.int64).T
        edge_feature_array = np.asarray(edge_features, dtype=np.float32)
    else:
        edge_index = np.empty((2, 0), dtype=np.int64)
        edge_feature_array = np.empty((0, 6), dtype=np.float32)

    return MoleculeGraph(
        smiles=smiles,
        atom_features=atom_features,
        edge_index=edge_index,
        edge_features=edge_feature_array,
    )


def graph_model_specs(availability: GraphAvailability | None = None) -> dict[str, GraphModelSpec]:
    """Return dependency-gated metadata for supported graph model families."""

    availability = availability or detect_graph_availability()
    backend_status = availability.backend_status
    specs = {
        "gcn": ("GCN", ("rdkit", "torch", "torch_geometric")),
        "gat": ("GAT", ("rdkit", "torch", "torch_geometric")),
        "mpnn": ("MPNN", ("rdkit", "torch")),
        "d_mpnn": ("D-MPNN", ("rdkit", "torch", "chemprop")),
        "chemprop_style": ("Chemprop-style D-MPNN", ("rdkit", "torch", "chemprop")),
    }
    return {
        family: _spec_from_requirements(family, display_name, required, backend_status)
        for family, (display_name, required) in specs.items()
    }


def graph_skip_report(config: GraphModelConfig, availability: GraphAvailability | None = None) -> dict[str, Any]:
    """Return a serializable report explaining why graph training is skipped."""

    spec = graph_model_specs(availability)[config.model_family]
    return {
        "model_family": config.model_family,
        "display_name": spec.display_name,
        "status": spec.status,
        "training_enabled": False,
        "required_backends": list(spec.required_backends),
        "missing_backends": list(spec.missing_backends),
        "config": asdict(config),
        "reason": (
            "No full graph training is run by this optional stub. "
            "Install and approve the required graph backend stack, then add a dedicated grouped-CV training path."
        ),
    }


def tiny_torch_cpu_smoke() -> dict[str, Any]:
    """Run a one-layer CPU forward pass only when PyTorch is installed."""

    if importlib.util.find_spec("torch") is None:
        return {"status": "torch_missing", "device": "cpu", "trained": False}

    import torch

    with torch.no_grad():
        layer = torch.nn.Linear(2, 1)
        output = layer(torch.zeros((1, 2), dtype=torch.float32, device="cpu"))
    return {
        "status": "ok",
        "device": "cpu",
        "trained": False,
        "output_shape": list(output.shape),
    }


def _spec_from_requirements(
    family: str,
    display_name: str,
    required_backends: tuple[str, ...],
    backend_status: dict[str, bool],
) -> GraphModelSpec:
    missing = tuple(backend for backend in required_backends if not backend_status.get(backend, False))
    return GraphModelSpec(
        family=family,
        display_name=display_name,
        required_backends=required_backends,
        missing_backends=missing,
        status="skipped_missing_dependency" if missing else "available_stub",
        training_enabled=False,
    )


def _atom_features(atom: Any) -> list[float]:
    hybridization = str(atom.GetHybridization())
    return [
        float(atom.GetAtomicNum()),
        float(atom.GetTotalDegree()),
        float(atom.GetFormalCharge()),
        float(atom.GetTotalNumHs()),
        float(atom.GetIsAromatic()),
        float(atom.IsInRing()),
        float(hybridization == "SP"),
        float(hybridization == "SP2"),
        float(hybridization == "SP3"),
    ]


def _bond_features(bond: Any) -> list[float]:
    bond_type = str(bond.GetBondType())
    return [
        float(bond_type == "SINGLE"),
        float(bond_type == "DOUBLE"),
        float(bond_type == "TRIPLE"),
        float(bond_type == "AROMATIC"),
        float(bond.GetIsConjugated()),
        float(bond.IsInRing()),
    ]
