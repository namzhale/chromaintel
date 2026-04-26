from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _matrix() -> pd.DataFrame:
    base_method = {
        "source_dataset": "cli_fixture",
        "column_name": "BEH C18",
        "mobile_phase_a": "water with 0.1% formic acid",
        "mobile_phase_b": "acetonitrile with 0.1% formic acid",
        "mobile_phase_system": "acn_formic_acid",
        "ph": 3.2,
        "flow_ml_min": 0.35,
        "temperature_c": 40.0,
        "total_runtime_min": 6.0,
        "quality_score": 0.8,
    }
    return pd.DataFrame(
        [
            {
                **base_method,
                "compound_name": "Caffeine",
                "canonical_smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "inchikey": "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
                "rt_min": 1.5,
            },
            {
                **base_method,
                "compound_name": "Aspirin",
                "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
                "rt_min": 4.2,
            },
            {
                **base_method,
                "compound_name": "Acetaminophen",
                "canonical_smiles": "CC(=O)Nc1ccc(O)cc1",
                "inchikey": "RZVAJINKPMORJF-UHFFFAOYSA-N",
                "rt_min": 2.1,
            },
        ]
    )


def _run_script(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, args)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_target_readiness_cli_writes_reports(tmp_path):
    matrix_path = tmp_path / "matrix.csv"
    report_dir = tmp_path / "reports"
    _matrix().to_csv(matrix_path, index=False)

    result = _run_script("scripts/analyze_target_readiness.py", "--input", matrix_path, "--report-dir", report_dir)

    assert "Coverage CSV" in result.stdout
    assert (report_dir / "target_coverage_matrix.csv").exists()
    assert (report_dir / "peak_metric_target_readiness.md").exists()


def test_prepare_dl_cli_writes_pairwise_and_inverse_manifests(tmp_path):
    matrix_path = tmp_path / "matrix.csv"
    output_dir = tmp_path / "dl"
    report_dir = tmp_path / "benchmarks"
    _matrix().to_csv(matrix_path, index=False)

    result = _run_script(
        "scripts/prepare_dl_datasets.py",
        "--input",
        matrix_path,
        "--output-dir",
        output_dir,
        "--reports-dir",
        report_dir,
        "--pair-delta-rt-min",
        "0.1",
    )

    assert "Pairwise manifest" in result.stdout
    assert (output_dir / "graph_manifest.csv").exists()
    assert (output_dir / "smiles_transformer_manifest.csv").exists()
    assert (output_dir / "pairwise_retention_order_manifest.csv").exists()
    assert (output_dir / "inverse_task_manifest.csv").exists()


def test_train_inverse_cli_writes_metrics_and_bundle(tmp_path):
    matrix_path = tmp_path / "matrix.csv"
    artifact_path = tmp_path / "models" / "inverse_bundle.joblib"
    report_dir = tmp_path / "reports"
    _matrix().to_csv(matrix_path, index=False)

    result = _run_script(
        "scripts/train_inverse_models.py",
        "--matrix",
        matrix_path,
        "--artifact",
        artifact_path,
        "--report-dir",
        report_dir,
        "--quick",
    )

    assert "Inverse model training complete" in result.stdout
    assert artifact_path.exists()
    assert (report_dir / "inverse_model_metrics.csv").exists()
    assert (report_dir / "inverse_topk_evaluation.csv").exists()
