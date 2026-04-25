import importlib.util

import pytest

from app.models.graph_optional import (
    GRAPH_MODEL_FAMILIES,
    GraphModelConfig,
    detect_graph_availability,
    featurize_molecule_graph,
    graph_model_specs,
    graph_skip_report,
    tiny_torch_cpu_smoke,
)


def test_graph_availability_detection_does_not_require_optional_graph_stacks():
    availability = detect_graph_availability()

    assert availability.rdkit_available is True
    assert availability.torch_available == (importlib.util.find_spec("torch") is not None)
    assert availability.pyg_available == (importlib.util.find_spec("torch_geometric") is not None)
    assert availability.dgl_available == (importlib.util.find_spec("dgl") is not None)
    assert availability.chemprop_available == (importlib.util.find_spec("chemprop") is not None)
    assert set(availability.backend_status) == {"rdkit", "torch", "torch_geometric", "dgl", "chemprop"}


def test_rdkit_molecule_graph_featurization_smoke_path_for_ethanol():
    graph = featurize_molecule_graph("CCO")

    assert graph.atom_features.shape[0] == 3
    assert graph.atom_features.shape[1] >= 6
    assert graph.edge_index.shape == (2, 4)
    assert graph.edge_features.shape[0] == 4
    assert graph.num_atoms == 3
    assert graph.num_directed_edges == 4
    assert graph.smiles == "CCO"


def test_graph_model_specs_are_dependency_gated_stubs():
    specs = graph_model_specs()

    assert set(specs) == set(GRAPH_MODEL_FAMILIES)
    assert specs["gcn"].required_backends == ("rdkit", "torch", "torch_geometric")
    assert specs["gat"].required_backends == ("rdkit", "torch", "torch_geometric")
    assert specs["mpnn"].required_backends == ("rdkit", "torch")
    assert specs["d_mpnn"].required_backends == ("rdkit", "torch", "chemprop")
    assert specs["chemprop_style"].required_backends == ("rdkit", "torch", "chemprop")
    assert all(spec.status in {"available_stub", "skipped_missing_dependency"} for spec in specs.values())


def test_graph_config_and_skip_report_explain_missing_training_runtime():
    config = GraphModelConfig(model_family="gcn", hidden_dim=16, num_layers=2, epochs=1)
    report = graph_skip_report(config)

    assert report["model_family"] == "gcn"
    assert report["status"] in {"available_stub", "skipped_missing_dependency"}
    assert report["training_enabled"] is False
    assert "No full graph training is run by this optional stub" in report["reason"]
    assert report["config"]["hidden_dim"] == 16
    assert "required_backends" in report


def test_invalid_smiles_raise_value_error():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        featurize_molecule_graph("not-a-smiles")


def test_tiny_torch_cpu_smoke_is_optional_and_never_trains():
    result = tiny_torch_cpu_smoke()

    assert result["device"] == "cpu"
    assert result["trained"] is False
    assert result["status"] in {"torch_missing", "ok"}
    if result["status"] == "ok":
        assert result["output_shape"] == [1, 1]
