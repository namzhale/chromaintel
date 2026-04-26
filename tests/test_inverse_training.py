import pandas as pd

from app.models.inverse_training import (
    INVERSE_FEATURE_COLUMNS,
    build_inverse_training_table,
    train_inverse_models,
)


def _fixture_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "canonical_smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "inchikey": "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
                "source_dataset": "internal_lab",
                "column_name": "BEH C18",
                "mobile_phase_system": "acn_formic_acid",
                "ph": 3.2,
                "flow_ml_min": 0.35,
                "temperature_c": 40,
                "total_runtime_min": 6,
                "rt_min": 1.5,
                "quality_score": 0.9,
            },
            {
                "compound_name": "Aspirin",
                "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
                "source_dataset": "RepoRT:0001",
                "column_name": "BEH C18",
                "mobile_phase_system": "acn_formic_acid",
                "ph": 3.2,
                "flow_ml_min": 0.35,
                "temperature_c": 40,
                "total_runtime_min": 6,
                "rt_min": 4.2,
                "quality_score": 0.75,
            },
            {
                "compound_name": "Labetalol",
                "canonical_smiles": "CC(CCc1ccccc1)NCC(O)c1ccc(O)c(NC=O)c1",
                "inchikey": "SGUAFYLVXWIBPW-UHFFFAOYSA-N",
                "source_dataset": "MCMRT:CM 01",
                "column_name": "CSH Phenyl-Hexyl",
                "mobile_phase_system": "meoh_formic_acid",
                "ph": 4.8,
                "flow_ml_min": 0.4,
                "temperature_c": 45,
                "total_runtime_min": 8,
                "rt_min": 5.4,
                "quality_score": 0.68,
            },
        ]
    )


def test_build_inverse_training_table_creates_proxy_labels_and_features():
    table = build_inverse_training_table(_fixture_matrix(), negatives_per_row=1)

    assert len(table) == 6
    assert set(table["label_source"]) == {"synthetic_proxy"}
    assert set(table["suitable"]) == {0, 1}
    assert set(INVERSE_FEATURE_COLUMNS).issubset(table.columns)
    assert table.loc[table["suitable"].eq(1), "rt_fit_score"].min() >= 0.95
    assert table.loc[table["suitable"].eq(0), "constraint_violation_count"].max() >= 1


def test_train_inverse_models_writes_metrics_bundle_and_reports(tmp_path):
    matrix = _fixture_matrix()
    outputs = train_inverse_models(
        matrix,
        artifact_path=tmp_path / "inverse_bundle.joblib",
        report_dir=tmp_path / "reports",
        quick=True,
    )

    metrics = pd.read_csv(outputs.metrics_csv)
    topk = pd.read_csv(outputs.topk_csv)

    assert outputs.artifact_path.exists()
    assert outputs.training_rows >= 6
    assert {"model", "roc_auc", "pr_auc", "brier_score"}.issubset(metrics.columns)
    assert {"top_1_success", "top_3_success", "top_5_success"}.issubset(topk.columns)
    assert outputs.metrics_md.exists()
