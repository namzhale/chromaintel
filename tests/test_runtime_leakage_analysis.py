import pandas as pd

from app.models.runtime_leakage import (
    build_runtime_ablation_sets,
    runtime_consequence_diagnostics,
)


def test_runtime_ablation_sets_compare_each_duration_proxy():
    base = [
        "logp",
        "gradient_duration_min",
        "total_runtime_min",
        "gradient_slope_percent_b_min",
        "column_name",
    ]

    sets = build_runtime_ablation_sets(base)

    assert sets["with_both"] == base
    assert "total_runtime_min" not in sets["without_total_runtime"]
    assert "gradient_duration_min" in sets["without_total_runtime"]
    assert "gradient_duration_min" not in sets["without_gradient_duration"]
    assert "total_runtime_min" in sets["without_gradient_duration"]
    assert "gradient_duration_min" not in sets["without_both"]
    assert "total_runtime_min" not in sets["without_both"]
    assert "gradient_slope_percent_b_min" in sets["without_both"]


def test_runtime_consequence_diagnostics_flags_target_like_runtime_margin():
    frame = pd.DataFrame(
        {
            "rt_min": [1.0, 2.0, 3.0, 4.0],
            "total_runtime_min": [1.5, 2.5, 3.5, 4.5],
            "gradient_duration_min": [1.0, 2.0, 3.0, 4.0],
            "column_name": ["C18"] * 4,
            "mobile_phase_system": ["acn_formic_acid"] * 4,
            "initial_organic_pct": [5.0] * 4,
            "final_organic_pct": [95.0] * 4,
            "flow_ml_min": [0.3] * 4,
            "temperature_c": [40.0] * 4,
            "source_dataset": ["internal"] * 4,
        }
    )

    diagnostics = runtime_consequence_diagnostics(frame)

    assert diagnostics["rt_total_runtime_spearman"] == 1.0
    assert diagnostics["post_peak_margin_median_min"] == 0.5
    assert diagnostics["target_like_runtime_margin_fraction"] == 1.0
    assert diagnostics["within_method_variable_runtime_group_fraction"] == 1.0
