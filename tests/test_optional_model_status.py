from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_optional_model_status_matches_dependency_gates():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    status = (ROOT / "docs" / "model_architectures" / "optional_models_status.md").read_text(
        encoding="utf-8"
    )

    assert "XGBoost | Active when import succeeds" in status
    assert "CatBoost | Active when import succeeds" in status
    assert "LightGBM | Not implemented" in status
    assert "GCN | Roadmap only" in status
    assert "GAT | Roadmap only" in status
    assert "MPNN | Roadmap only" in status
    assert "D-MPNN / Chemprop | Roadmap only" in status
    assert "ChemBERTa | Roadmap only" in status
    assert "MolFormer | Roadmap only" in status
    assert "Mixture of Experts (MoE) | Design stub only" in status
    assert "Bayesian optimization / active learning | Stub only" in status

    assert "xgboost==" in requirements
    assert "catboost==" in requirements
    assert "lightgbm" not in requirements
    assert "chemprop" not in requirements
    assert "transformers" not in requirements
    assert "torch" not in requirements
    assert "botorch" not in requirements
    assert "optuna" not in requirements
    assert "scikit-optimize" not in requirements
