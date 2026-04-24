from __future__ import annotations

from typing import Any

import pandas as pd

from app.schemas.method import MethodInput, MSSettingsInput
from app.services.descriptors import DescriptorCalculator
from app.services.feature_engineering import build_lc_condition_features, build_ms_features


CATEGORICAL_FEATURES = [
    "column",
    "stationary_phase",
    "mobile_phase_a",
    "mobile_phase_b",
    "ionization_mode",
]

NUMERIC_METHOD_FEATURES = [
    "ph",
    "temperature_c",
    "flow_rate_ml_min",
    "injection_volume_ul",
    "runtime_min",
    "initial_percent_b",
    "final_percent_b",
    "gradient_slope_percent_b_min",
    "precursor_mz",
]


def method_features(method: MethodInput, ms_settings: MSSettingsInput | None = None) -> dict[str, Any]:
    initial_b = method.gradient_steps[0].percent_b if method.gradient_steps else 0.0
    final_b = method.gradient_steps[-1].percent_b if method.gradient_steps else initial_b
    runtime = max(method.runtime_min, 0.01)
    return {
        "column": method.column,
        "stationary_phase": method.stationary_phase,
        "mobile_phase_a": method.mobile_phase_a,
        "mobile_phase_b": method.mobile_phase_b,
        "ph": method.ph or 7.0,
        "temperature_c": method.temperature_c or 35.0,
        "flow_rate_ml_min": method.flow_rate_ml_min or 0.3,
        "injection_volume_ul": method.injection_volume_ul or 2.0,
        "runtime_min": method.runtime_min,
        "initial_percent_b": initial_b,
        "final_percent_b": final_b,
        "gradient_slope_percent_b_min": (final_b - initial_b) / runtime,
        "ionization_mode": ms_settings.ionization_mode if ms_settings else "unknown",
        "precursor_mz": ms_settings.precursor_mz if ms_settings and ms_settings.precursor_mz else 0.0,
    }


def build_feature_row(
    compound: dict[str, Any],
    method: MethodInput,
    ms_settings: MSSettingsInput | None = None,
    descriptor_calculator: DescriptorCalculator | None = None,
) -> dict[str, Any]:
    calculator = descriptor_calculator or DescriptorCalculator()
    smiles = compound.get("smiles") or compound.get("canonical_smiles")
    descriptor_features = calculator.model_features(smiles) if smiles else {}
    legacy_method = method_features(method, ms_settings)
    canonical_row = {
        "column_name": method.column,
        "column_chemistry": _column_chemistry(method.column, method.stationary_phase),
        "stationary_phase_type": method.stationary_phase,
        "mobile_phase_a": method.mobile_phase_a,
        "mobile_phase_b": method.mobile_phase_b,
        "ph": method.ph,
        "temperature_c": method.temperature_c,
        "flow_ml_min": method.flow_rate_ml_min,
        "injection_ul": method.injection_volume_ul,
        "initial_organic_pct": legacy_method["initial_percent_b"],
        "final_organic_pct": legacy_method["final_percent_b"],
        "gradient_duration_min": method.gradient_steps[-2].time_min if len(method.gradient_steps) > 1 else method.runtime_min,
        "total_runtime_min": method.runtime_min,
        "ion_mode": ms_settings.ionization_mode if ms_settings else "unknown",
        "precursor_mz": ms_settings.precursor_mz if ms_settings and ms_settings.precursor_mz else 0.0,
        "product_mz": _product_mz(ms_settings),
    }
    canonical_features = {
        **build_lc_condition_features(canonical_row),
        **build_ms_features(canonical_row),
    }
    return {**descriptor_features, **legacy_method, **canonical_features}


def _column_chemistry(column: str, stationary_phase: str) -> str:
    text = f"{column} {stationary_phase}".upper()
    if "HILIC" in text or "AMIDE" in text:
        return "HILIC"
    if "PHENYL" in text:
        return "phenyl"
    if "C18" in text:
        return "C18"
    return stationary_phase


def _product_mz(ms_settings: MSSettingsInput | None) -> float:
    if not ms_settings or not ms_settings.transitions:
        return 0.0
    first = ms_settings.transitions[0]
    for key in ("product_mz", "fragment_mz", "q3"):
        if key in first and first[key]:
            return float(first[key])
    return 0.0


def as_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)
