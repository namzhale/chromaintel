from pathlib import Path

import pandas as pd

from scripts.generate_dashboard_pdf import build_pdf


def test_dashboard_pdf_smoke_builds_russian_report(tmp_path):
    output = tmp_path / "dashboard.pdf"
    data = {
        "master": pd.DataFrame(
            [
                {"compound_name": "Caffeine", "source_dataset": "RepoRT:0001", "inchikey": "A"},
                {"compound_name": "Aspirin", "source_dataset": "MCMRT:CM 01", "inchikey": "B"},
            ]
        ),
        "matrix": pd.DataFrame([{"rt_min": 1.2}, {"rt_min": 2.3}]),
        "cv": pd.DataFrame(
            [
                {
                    "target": "rt_min",
                    "model": "extra_trees",
                    "mae_mean": 1.1,
                    "rmse_mean": 1.7,
                    "r2_mean": 0.8,
                    "spearman_mean": 0.9,
                },
                {
                    "target": "quality_score",
                    "model": "random_forest",
                    "mae_mean": 0.02,
                    "rmse_mean": 0.03,
                    "r2_mean": 0.7,
                },
            ]
        ),
        "benchmark": pd.DataFrame(
            [
                {
                    "split": "final_grouped_holdout",
                    "target": "rt_min",
                    "model_family": "extra_trees",
                    "mae": 1.0,
                    "rmse": 1.5,
                    "r2": 0.85,
                }
            ]
        ),
        "source_holdout": pd.DataFrame(
            [
                {
                    "target": "rt_min",
                    "holdout_family": "RepoRT",
                    "model": "extra_trees",
                    "n_holdout": 10,
                    "mae": 1.4,
                    "normalized_mae_runtime_pct": 7.0,
                }
            ]
        ),
        "method_holdout": pd.DataFrame(
            [
                {
                    "target": "rt_min",
                    "holdout_method": "C18 | acn_formic",
                    "model": "extra_trees",
                    "n_holdout": 8,
                    "mae": 1.6,
                    "normalized_mae_runtime_pct": 6.0,
                }
            ]
        ),
        "column_holdout": pd.DataFrame(
            [
                {
                    "target": "rt_min",
                    "holdout_column_family": "C18",
                    "model": "extra_trees",
                    "n_holdout": 8,
                    "mae": 1.7,
                    "normalized_mae_runtime_pct": 8.0,
                }
            ]
        ),
        "importance": pd.DataFrame(
            [
                {
                    "feature": "logp",
                    "feature_group": "compound_descriptor",
                    "importance_mean": 2.0,
                    "significance": "positive",
                }
            ]
        ),
        "source_metrics": pd.DataFrame(
            [{"source_dataset": "RepoRT:0001", "rt_mae": 2.1, "n_test": 2}]
        ),
        "predictions": pd.DataFrame(
            [
                {
                    "compound_name": "Caffeine",
                    "source_dataset": "RepoRT:0001",
                    "rt_min": 1.2,
                    "predicted_rt_min": 1.4,
                    "rt_error_min": 0.2,
                    "abs_rt_error_min": 0.2,
                    "ad_flag": False,
                }
            ]
        ),
        "target_coverage": pd.DataFrame(
            [
                {
                    "target": "rt_min",
                    "coverage_fraction": 1.0,
                    "label_source": "measured",
                    "readiness": "trainable",
                },
                {
                    "target": "peak_width_base_min",
                    "coverage_fraction": 0.0,
                    "label_source": "unavailable",
                    "readiness": "unavailable",
                },
            ]
        ),
        "inverse_metrics": pd.DataFrame(
            [{"model": "extra_trees", "roc_auc": 0.9, "pr_auc": 0.85, "brier_score": 0.12}]
        ),
        "inverse_topk": pd.DataFrame(
            [{"model": "extra_trees", "top_1_success": 0.5, "top_3_success": 0.8, "top_5_success": 0.9}]
        ),
        "metadata": {
            "best_rt_model": "extra_trees",
            "best_quality_model": "random_forest",
            "uncertainty_metadata": {"rt": {"q90_min": 2.5}},
        },
    }

    build_pdf(output, data)

    assert output.exists()
    assert output.stat().st_size > 1000


def test_dashboard_source_has_no_common_mojibake_markers():
    source = Path("scripts/generate_dashboard_pdf.py").read_text(encoding="utf-8")
    for marker in ["Рґ", "СЃ", "Рњ", "вЂў"]:
        assert marker not in source
