from __future__ import annotations

import pandas as pd

from scripts.prepare_dl_datasets import (
    DL_BASE_COLUMNS,
    prepare_dl_datasets,
)


def test_prepare_dl_datasets_filters_invalid_smiles_and_writes_manifests(tmp_path):
    source = tmp_path / "source.csv"
    pd.DataFrame(
        [
            {
                "compound_name": "ethanol",
                "smiles": "CCO",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "rt_min": 1.2,
            },
            {
                "compound_name": "bad",
                "smiles": "not-a-smiles",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "rt_min": 3.4,
            },
        ]
    ).to_csv(source, index=False)

    outputs = prepare_dl_datasets(
        input_paths=[source],
        output_dir=tmp_path / "dl",
        reports_dir=tmp_path / "reports",
        split_seed=7,
    )

    graph = pd.read_csv(outputs.graph_manifest_path)
    transformer = pd.read_csv(outputs.transformer_manifest_path)

    assert outputs.input_rows == 2
    assert outputs.valid_rows == 1
    assert outputs.filtered_invalid_smiles == 1
    assert graph["canonical_smiles"].tolist() == ["CCO"]
    assert transformer["canonical_smiles"].tolist() == ["CCO"]
    assert "not-a-smiles" not in graph.to_string()
    assert list(graph.columns[: len(DL_BASE_COLUMNS)]) == DL_BASE_COLUMNS
    assert list(transformer.columns[: len(DL_BASE_COLUMNS)]) == DL_BASE_COLUMNS
    assert "graph_backend" in graph.columns
    assert "encoder_family" in transformer.columns
    assert "peak_width_base_min" in graph.columns
    assert "target_label_sources_json" in graph.columns
    assert "method_text" in transformer.columns


def test_prepare_dl_datasets_preserves_available_split_labels(tmp_path):
    source = tmp_path / "source.csv"
    pd.DataFrame(
        [
            {"canonical_smiles": "CCO", "inchikey": "", "source_dataset": "a", "rt_min": 1.0, "split": "train"},
            {"canonical_smiles": "CCN", "inchikey": "", "source_dataset": "a", "rt_min": 2.0, "split": "test"},
        ]
    ).to_csv(source, index=False)

    outputs = prepare_dl_datasets(
        input_paths=[source],
        output_dir=tmp_path / "dl",
        reports_dir=tmp_path / "reports",
    )

    manifest = pd.read_csv(outputs.graph_manifest_path).set_index("canonical_smiles")

    assert manifest["split"].to_dict() == {"CCN": "test", "CCO": "train"}
    assert outputs.split_strategy == "source_column:split"


def test_prepare_dl_datasets_generates_reproducible_splits(tmp_path):
    rows = [
        {"canonical_smiles": smiles, "source_dataset": "fixture", "rt_min": index + 0.5}
        for index, smiles in enumerate(["CCO", "CCN", "CCC", "CCCC", "c1ccccc1", "CCCl", "CCBr", "CC(=O)O"])
    ]
    source_a = tmp_path / "source_a.csv"
    source_b = tmp_path / "source_b.csv"
    pd.DataFrame(rows).to_csv(source_a, index=False)
    pd.DataFrame(list(reversed(rows))).to_csv(source_b, index=False)

    first = prepare_dl_datasets(
        input_paths=[source_a],
        output_dir=tmp_path / "first_dl",
        reports_dir=tmp_path / "first_reports",
        split_seed=123,
    )
    second = prepare_dl_datasets(
        input_paths=[source_b],
        output_dir=tmp_path / "second_dl",
        reports_dir=tmp_path / "second_reports",
        split_seed=123,
    )

    first_manifest = pd.read_csv(first.graph_manifest_path).set_index("canonical_smiles")
    second_manifest = pd.read_csv(second.graph_manifest_path).set_index("canonical_smiles")

    assert first.split_strategy == "deterministic_hash"
    assert second.split_strategy == "deterministic_hash"
    assert first_manifest["split"].to_dict() == second_manifest["split"].to_dict()


def test_prepare_dl_datasets_deduplicates_same_molecule_method_rt(tmp_path):
    source = tmp_path / "source.csv"
    pd.DataFrame(
        [
            {
                "canonical_smiles": "CCO",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "gradient_profile": "0 min 5% B; 5 min 95% B",
                "total_runtime_min": 5,
                "rt_min": 1.2,
            },
            {
                "canonical_smiles": "CCO",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "gradient_profile": "0 min 5% B; 5 min 95% B",
                "total_runtime_min": 5,
                "rt_min": 1.2,
            },
        ]
    ).to_csv(source, index=False)

    outputs = prepare_dl_datasets(input_paths=[source], output_dir=tmp_path / "dl", reports_dir=tmp_path / "reports")
    manifest = pd.read_csv(outputs.graph_manifest_path)

    assert outputs.input_rows == 2
    assert outputs.valid_rows == 1
    assert len(manifest) == 1


def test_prepare_dl_datasets_writes_pairwise_and_inverse_manifests(tmp_path):
    source = tmp_path / "source.csv"
    pd.DataFrame(
        [
            {
                "canonical_smiles": "CCO",
                "inchikey": "IK1",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "total_runtime_min": 6,
                "rt_min": 1.0,
                "quality_score": 0.8,
            },
            {
                "canonical_smiles": "CCN",
                "inchikey": "IK2",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "total_runtime_min": 6,
                "rt_min": 3.0,
                "quality_score": 0.7,
            },
            {
                "canonical_smiles": "CCC",
                "inchikey": "IK3",
                "source_dataset": "fixture",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "total_runtime_min": 6,
                "rt_min": 3.05,
                "quality_score": 0.7,
            },
        ]
    ).to_csv(source, index=False)

    outputs = prepare_dl_datasets(
        input_paths=[source],
        output_dir=tmp_path / "dl",
        reports_dir=tmp_path / "reports",
        pair_delta_rt_min=0.2,
    )

    pairwise = pd.read_csv(outputs.pairwise_manifest_path)
    inverse = pd.read_csv(outputs.inverse_manifest_path)

    assert outputs.pairwise_pairs == 2
    assert {"compound_i", "compound_j", "order_label", "delta_rt"}.issubset(pairwise.columns)
    assert pairwise["delta_rt"].min() >= 0.2
    assert {"target_rt_min", "candidate_method_text", "label_source"}.issubset(inverse.columns)
    assert set(inverse["label_source"]) == {"observed_method_proxy"}
