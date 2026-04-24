import pandas as pd

from app.services.feature_engineering import build_model_matrix


def test_build_model_matrix_creates_feature_groups_and_proxy_quality():
    master = pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
                "column_chemistry": "C18",
                "stationary_phase_type": "reversed phase",
                "mobile_phase_a": "Water + 0.1% formic acid",
                "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
                "ph": 3.2,
                "temperature_c": 40,
                "flow_ml_min": 0.35,
                "injection_ul": 2,
                "initial_organic_pct": 5,
                "final_organic_pct": 95,
                "gradient_duration_min": 5,
                "total_runtime_min": 5.8,
                "ion_mode": "positive",
                "precursor_mz": 195.1,
                "rt_min": 1.35,
                "asymmetry": 1.05,
                "resolution": 2.1,
                "sn_ratio": 82,
                "source_dataset": "internal_lab",
            }
        ]
    )

    matrix = build_model_matrix(master)

    assert matrix.loc[0, "molecular_weight"] > 190
    assert matrix.loc[0, "fraction_csp3"] >= 0
    assert matrix.loc[0, "quality_score"] > 0.8
    assert matrix.loc[0, "gradient_slope_percent_b_min"] == 18


def test_build_model_matrix_preserves_explicit_quality_score():
    master = pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
                "column_chemistry": "C18",
                "stationary_phase_type": "reversed phase",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "rt_min": 1.35,
                "quality_score": 0.91,
            }
        ]
    )

    matrix = build_model_matrix(master)

    assert matrix.loc[0, "quality_score"] == 0.91
