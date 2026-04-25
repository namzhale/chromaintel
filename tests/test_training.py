import json

import pytest
import pandas as pd

from app.models.training import (
    _candidate_models,
    _group_kfold_scores,
    _grouped_train_validation_test_split,
    _groups_for_split,
    train_forward_models,
)
from app.schemas.method import GradientStep, MethodInput, MSSettingsInput
from app.services.predictor import ForwardPredictor


def _training_matrix(row_count: int = 18) -> pd.DataFrame:
    rows = []
    sources = ["internal_lab", "RepoRT", "METLIN_SMRT"]
    method_pairs = [
        ("BEH C18", "C18", "acn_formic_acid"),
        ("HSS T3", "T3", "methanol_formic_acid"),
        ("Phenyl Hexyl", "phenyl_hexyl", "acn_ammonium_formate"),
    ]
    for idx in range(row_count):
        source_idx = idx % len(sources)
        column_name, column_chemistry, mobile_phase_system = method_pairs[idx % len(method_pairs)]
        organic_end = 65 + (idx % 5) * 5
        gradient_duration = 4 + (idx % 4)
        rows.append(
            {
                "compound_name": f"Compound {idx % 6}",
                "canonical_smiles": "CCO",
                "inchikey": f"KEY{idx % 6}",
                "source_dataset": sources[source_idx],
                "molecular_weight": 120 + idx * 8,
                "logp": -0.5 + idx * 0.12,
                "tpsa": 20 + idx * 1.5,
                "hbond_donors": idx % 3,
                "hbond_acceptors": 2 + idx % 4,
                "rotatable_bonds": idx % 5,
                "aromatic_ring_count": idx % 2,
                "formal_charge": 0,
                "heavy_atom_count": 8 + idx,
                "fraction_csp3": 0.2 + (idx % 4) * 0.1,
                "ph": 3.0 + (idx % 4) * 0.5,
                "temperature_c": 35 + (idx % 3) * 5,
                "flow_ml_min": 0.25 + (idx % 3) * 0.05,
                "injection_ul": 1 + (idx % 3),
                "initial_organic_pct": 5,
                "final_organic_pct": organic_end,
                "gradient_duration_min": gradient_duration,
                "total_runtime_min": gradient_duration + 1.0,
                "gradient_slope_percent_b_min": (organic_end - 5) / gradient_duration,
                "column_name": column_name,
                "column_chemistry": column_chemistry,
                "stationary_phase_type": "reversed phase",
                "mobile_phase_a": "Water + 0.1% formic acid",
                "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
                "mobile_phase_system": mobile_phase_system,
                "ion_mode": "positive" if idx % 2 == 0 else "negative",
                "precursor_mz": 100 + idx * 10,
                "product_mz": 80 + idx * 4,
                "rt_min": 1.0 + idx * 0.35 + source_idx * 0.2,
                "quality_score": min(0.95, 0.62 + (idx % 7) * 0.04),
            }
        )
    return pd.DataFrame(rows)


def test_candidate_models_include_cpu_practical_extra_trees():
    models = _candidate_models(categorical=["ion_mode"], numeric=["molecular_weight"])

    assert "extra_trees" in models
    assert "xgboost" in models
    assert "catboost" in models


def test_train_forward_models_exports_sota_metadata_and_feature_importance(tmp_path):
    summary = train_forward_models(
        _training_matrix(),
        artifact_path=tmp_path / "models" / "bundle.joblib",
        report_dir=tmp_path / "reports",
        plots_dir=tmp_path / "plots",
    )

    assert "extra_trees" in summary.rt_metrics
    assert "xgboost" in summary.rt_metrics
    assert "catboost" in summary.rt_metrics
    assert summary.validation_metadata["split_strategy"] == "group_shuffle_holdout_with_group_kfold_model_selection"
    assert summary.validation_metadata["cv_strategy"] == "GroupKFold"
    assert summary.validation_metadata["source_counts"]["train"]["internal_lab"] > 0
    assert summary.validation_metadata["group_column"] == "inchikey"
    assert summary.validation_metadata["group_overlap_counts"] == {
        "train_validation": 0,
        "train_test": 0,
        "validation_test": 0,
    }
    assert len(summary.feature_columns) > 0
    assert summary.uncertainty_metadata["rt"]["method"] == "split_conformal_abs_residual_q90"
    assert summary.uncertainty_metadata["rt"]["q90_min"] >= 0
    assert (tmp_path / "reports" / "feature_importance.csv").exists()
    assert summary.feature_importance_path.endswith("feature_importance.csv")
    assert (tmp_path / "reports" / "sota_model_experiments.md").exists()
    assert (tmp_path / "reports" / "cv_metrics.csv").exists()
    assert (tmp_path / "reports" / "source_holdout_metrics.csv").exists()
    assert (tmp_path / "reports" / "evaluation_matrix.csv").exists()
    assert (tmp_path / "reports" / "evaluation_matrix.md").exists()
    assert (tmp_path / "reports" / "model_benchmark_matrix.csv").exists()
    assert (tmp_path / "reports" / "model_benchmark_matrix.md").exists()
    assert (tmp_path / "reports" / "model_benchmark_matrix.json").exists()
    assert (tmp_path / "reports" / "split_manifest.json").exists()
    assert (tmp_path / "reports" / "retention_order_metrics.csv").exists()

    cv_metrics = pd.read_csv(tmp_path / "reports" / "cv_metrics.csv")
    assert {"validation_scope", "target", "model", "mae_mean", "rmse_mean", "r2_mean", "spearman_mean", "n_folds"}.issubset(
        cv_metrics.columns
    )

    evaluation = pd.read_csv(tmp_path / "reports" / "evaluation_matrix.csv")
    assert {
        "validation_scope",
        "target",
        "model",
        "mae",
        "rmse",
        "r2",
        "spearman",
        "normalized_mae_runtime_pct",
    }.issubset(evaluation.columns)
    assert {"group_kfold", "final_grouped_holdout", "method_holdout", "column_family_holdout"}.issubset(
        set(evaluation["validation_scope"])
    )
    assert evaluation.loc[evaluation["target"].eq("rt_min"), "normalized_mae_runtime_pct"].notna().any()
    benchmark = pd.read_csv(tmp_path / "reports" / "model_benchmark_matrix.csv")
    assert {"model_family", "feature_set", "split", "normalized_mae_runtime_pct"}.issubset(benchmark.columns)
    assert not evaluation.duplicated(
        subset=["validation_scope", "target", "model", "split_name", "holdout_key"]
    ).any()

    split_manifest = json.loads((tmp_path / "reports" / "split_manifest.json").read_text(encoding="utf-8"))
    assert split_manifest["split_strategy"] == "group_shuffle_holdout_with_group_kfold_model_selection"
    assert split_manifest["group_column"] == "inchikey"
    assert split_manifest["group_overlap_counts"] == {
        "train_validation": 0,
        "train_test": 0,
        "validation_test": 0,
    }
    assert set(split_manifest["splits"]) == {"train", "validation", "test"}
    assert split_manifest["diagnostics"]["method_holdout"]["scope"] == "method_holdout"
    assert split_manifest["diagnostics"]["column_family_holdout"]["scope"] == "column_family_holdout"

    feature_importance = pd.read_csv(tmp_path / "reports" / "feature_importance.csv")
    assert {"feature_group", "significance", "importance_z"}.issubset(feature_importance.columns)
    assert set(feature_importance["significance"]).issubset(
        {"positive", "weak_positive", "neutral_or_unstable", "negative"}
    )

    source_metrics = pd.read_csv(tmp_path / "reports" / "source_metrics.csv")
    assert {"source_dataset", "n_test", "rt_mae", "rt_rmse", "mean_bias", "median_abs_error"}.issubset(
        source_metrics.columns
    )

    predictions = pd.read_csv(tmp_path / "reports" / "test_predictions.csv")
    assert {"rt_error_min", "abs_rt_error_min", "ad_flag", "ad_reason"}.issubset(predictions.columns)
    order_metrics = pd.read_csv(tmp_path / "reports" / "retention_order_metrics.csv")
    assert {"pairwise_order_accuracy", "spearman_rt", "n_pairs"}.issubset(order_metrics.columns)


def test_train_forward_models_records_morgan_feature_counts(tmp_path):
    matrix = _training_matrix()
    matrix["morgan_0"] = [idx % 2 for idx in range(len(matrix))]
    matrix["morgan_1"] = [(idx + 1) % 2 for idx in range(len(matrix))]

    summary = train_forward_models(
        matrix,
        artifact_path=tmp_path / "models" / "bundle.joblib",
        report_dir=tmp_path / "reports",
        plots_dir=tmp_path / "plots",
        feature_set="morgan",
    )

    assert "morgan_0" in summary.feature_columns
    report_text = (tmp_path / "reports" / "model_training_summary.md").read_text(encoding="utf-8")
    assert "Feature set: `morgan`" in report_text
    assert "'fingerprints': 2" in report_text


def test_grouped_split_has_no_inchikey_overlap():
    frame = _training_matrix(row_count=30)
    train, validation, test = _grouped_train_validation_test_split(frame, "inchikey")

    train_groups = set(_groups_for_split(train, "inchikey"))
    validation_groups = set(_groups_for_split(validation, "inchikey"))
    test_groups = set(_groups_for_split(test, "inchikey"))

    assert train_groups.isdisjoint(validation_groups)
    assert train_groups.isdisjoint(test_groups)
    assert validation_groups.isdisjoint(test_groups)


def test_group_kfold_falls_back_to_available_group_count():
    frame = _training_matrix(row_count=12)
    frame["inchikey"] = [f"KEY{idx % 3}" for idx in range(len(frame))]
    models = _candidate_models(categorical=["ion_mode"], numeric=["molecular_weight"])

    scores = _group_kfold_scores(models, frame, ["ion_mode", "molecular_weight"], "rt_min", "inchikey", n_splits=5)

    assert scores["extra_trees"]["n_folds"] == 3


def test_group_kfold_requires_two_groups():
    frame = _training_matrix(row_count=8)
    frame["inchikey"] = "ONE_GROUP"
    models = _candidate_models(categorical=["ion_mode"], numeric=["molecular_weight"])

    with pytest.raises(ValueError, match="At least two unique"):
        _group_kfold_scores(models, frame, ["ion_mode", "molecular_weight"], "rt_min", "inchikey")


def test_trained_predictor_uses_bundle_applicability_domain(tmp_path):
    model_dir = tmp_path / "models"
    train_forward_models(
        _training_matrix(),
        artifact_path=model_dir / "trained_forward_bundle.joblib",
        report_dir=tmp_path / "reports",
        plots_dir=tmp_path / "plots",
    )
    predictor = ForwardPredictor(artifact_path=model_dir)
    method = MethodInput(
        column="Novel Biphenyl 50x2.1 mm",
        stationary_phase="reversed phase",
        mobile_phase_a="Water + 0.1% formic acid",
        mobile_phase_b="Acetonitrile + 0.1% formic acid",
        ph=3.2,
        temperature_c=40.0,
        flow_rate_ml_min=0.3,
        injection_volume_ul=2.0,
        gradient_steps=[
            GradientStep(time_min=0.0, percent_b=5.0),
            GradientStep(time_min=5.0, percent_b=95.0),
        ],
    )

    result = predictor.predict(
        {"smiles": "CCO", "name": "ethanol"},
        method,
        MSSettingsInput(ionization_mode="positive", precursor_mz=101.0),
    )

    assert result["out_of_domain"] is True
    assert result["out_of_domain_method"] == "training_feature_ranges"
    assert any("unseen category" in reason for reason in result["out_of_domain_reasons"])
    assert result["peak_metrics"]["label_source"] == "provisional_estimate"
    assert result["peak_metrics"]["peak_width_base_min"] > result["peak_metrics"]["peak_width_half_height_min"]
