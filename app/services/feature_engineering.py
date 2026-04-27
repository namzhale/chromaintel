from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from app.services.descriptors import DescriptorCalculator, InvalidStructureError


COMPOUND_FEATURES = [
    "molecular_weight",
    "exact_mol_wt",
    "logp",
    "molar_refractivity",
    "tpsa",
    "labute_asa",
    "hbond_donors",
    "hbond_acceptors",
    "rotatable_bonds",
    "aromatic_ring_count",
    "formal_charge",
    "heavy_atom_count",
    "hetero_atom_count",
    "halogen_count",
    "valence_electron_count",
    "fraction_csp3",
    "ring_count",
    "aliphatic_ring_count",
    "saturated_ring_count",
    "bridgehead_atom_count",
    "spiro_atom_count",
    "aromatic_atom_fraction",
    "bertz_complexity",
    "carboxylic_acid_count",
    "phenol_count",
    "alcohol_count",
    "primary_amine_count",
    "secondary_amine_count",
    "tertiary_amine_count",
    "amine_count",
    "amide_count",
    "sulfonamide_count",
    "phosphate_count",
    "nitrile_count",
    "acidic_group_count",
    "basic_group_count",
    "strongest_acid_pka_proxy",
    "strongest_base_pka_proxy",
    "acid_ionized_fraction_ph3",
    "base_ionized_fraction_ph3",
    "estimated_net_charge_ph3",
    "estimated_logd_ph3",
    "acid_ionized_fraction_ph7",
    "base_ionized_fraction_ph7",
    "estimated_net_charge_ph7",
    "estimated_logd_ph7",
    "slogp_vsa_hydrophobic",
    "slogp_vsa_polar",
    "peoe_vsa_positive",
    "peoe_vsa_negative",
    "smr_vsa_total",
    "gasteiger_charge_min",
    "gasteiger_charge_max",
    "gasteiger_abs_charge_mean",
    "gasteiger_dipole_moment_proxy",
]

LC_NUMERIC_FEATURES = [
    "ph",
    "temperature_c",
    "flow_ml_min",
    "injection_ul",
    "initial_organic_pct",
    "final_organic_pct",
    "gradient_duration_min",
    "total_runtime_min",
    "gradient_slope_percent_b_min",
]

LC_CATEGORICAL_FEATURES = [
    "column_name",
    "column_chemistry",
    "stationary_phase_type",
    "mobile_phase_a",
    "mobile_phase_b",
]

MS_FEATURES = ["ion_mode", "precursor_mz", "product_mz"]
MORGAN_FINGERPRINT_BITS = 2048

TARGET_COLUMNS = [
    "rt_min",
    "quality_score",
    "asymmetry",
    "tailing_factor",
    "resolution",
    "peak_width_base_min",
    "peak_width_half_height_min",
    "peak_area",
    "peak_height",
    "sn_ratio",
]


@dataclass(frozen=True)
class FeatureGroups:
    """Named feature groups used by the training and explanation layers."""

    compound: list[str]
    fingerprints: list[str]
    lc_numeric: list[str]
    lc_categorical: list[str]
    ms: list[str]
    combined: list[str]


def build_model_matrix(master: pd.DataFrame, include_fingerprints: bool = False) -> pd.DataFrame:
    """Create model-ready rows from the canonical master dataset."""

    rows: list[dict[str, Any]] = []
    calc = DescriptorCalculator()
    descriptor_cache: dict[str, dict[str, Any]] = {}
    for _, source in master.iterrows():
        row = source.to_dict()
        smiles = row.get("canonical_smiles") or row.get("smiles")
        descriptor_values: dict[str, Any] = {}
        if pd.notna(smiles) and str(smiles).strip():
            cache_key = f"{smiles}|fp={include_fingerprints}"
            if cache_key not in descriptor_cache:
                descriptor_cache[cache_key] = _descriptor_values(calc, str(smiles), include_fingerprints)
            descriptor_values = descriptor_cache[cache_key]
        else:
            descriptor_values = {key: np.nan for key in COMPOUND_FEATURES}
            if include_fingerprints:
                descriptor_values.update(_empty_morgan_fingerprint())

        feature_row = {
            **_identity_fields(row),
            **descriptor_values,
            **build_lc_condition_features(row),
            **build_ms_features(row),
            **_target_fields(row),
        }
        feature_row["quality_score"] = _quality_score(feature_row)
        rows.append(feature_row)

    return pd.DataFrame(rows)


def _descriptor_values(
    calc: DescriptorCalculator,
    smiles: str,
    include_fingerprints: bool,
) -> dict[str, Any]:
    try:
        descriptors = calc.from_smiles(smiles)
        values = {key: descriptors[key] for key in COMPOUND_FEATURES}
        if include_fingerprints:
            values.update({f"morgan_{idx}": bit for idx, bit in enumerate(descriptors["morgan_fp"])})
        return values
    except InvalidStructureError:
        values = {key: np.nan for key in COMPOUND_FEATURES}
        if include_fingerprints:
            values.update(_empty_morgan_fingerprint())
        return values


def build_lc_condition_features(row: dict[str, Any]) -> dict[str, Any]:
    """Build simplified LC condition encodings including gradient summary."""

    duration = _num(row.get("gradient_duration_min"), default=_num(row.get("total_runtime_min"), 0.0))
    initial = _num(row.get("initial_organic_pct"), default=0.0)
    final = _num(row.get("final_organic_pct"), default=initial)
    slope = (final - initial) / duration if duration else 0.0
    return {
        "column_name": row.get("column_name"),
        "column_chemistry": row.get("column_chemistry"),
        "stationary_phase_type": row.get("stationary_phase_type"),
        "mobile_phase_a": row.get("mobile_phase_a"),
        "mobile_phase_b": row.get("mobile_phase_b"),
        "mobile_phase_system": mobile_phase_system(row.get("mobile_phase_a"), row.get("mobile_phase_b")),
        "ph": _num(row.get("ph"), default=7.0),
        "temperature_c": _num(row.get("temperature_c"), default=35.0),
        "flow_ml_min": _num(row.get("flow_ml_min"), default=0.3),
        "injection_ul": _num(row.get("injection_ul"), default=2.0),
        "initial_organic_pct": initial,
        "final_organic_pct": final,
        "gradient_duration_min": duration,
        "total_runtime_min": _num(row.get("total_runtime_min"), default=duration),
        "gradient_slope_percent_b_min": slope,
    }


def build_ms_features(row: dict[str, Any]) -> dict[str, Any]:
    """Build MS setting features with explicit unknown categories."""

    return {
        "ion_mode": row.get("ion_mode") or "unknown",
        "precursor_mz": _num(row.get("precursor_mz"), default=0.0),
        "product_mz": _num(row.get("product_mz"), default=0.0),
    }


def feature_groups(frame: pd.DataFrame) -> FeatureGroups:
    """Return feature group names that are present in a model matrix."""

    compound = [col for col in COMPOUND_FEATURES if col in frame.columns]
    fingerprints = morgan_feature_columns(frame)
    lc_numeric = [col for col in LC_NUMERIC_FEATURES if col in frame.columns]
    lc_categorical = [col for col in [*LC_CATEGORICAL_FEATURES, "mobile_phase_system"] if col in frame.columns]
    ms = [col for col in MS_FEATURES if col in frame.columns]
    combined = compound + fingerprints + lc_numeric + lc_categorical + ms
    return FeatureGroups(compound, fingerprints, lc_numeric, lc_categorical, ms, combined)


def morgan_feature_columns(frame: pd.DataFrame) -> list[str]:
    """Return Morgan fingerprint feature columns in stable bit-index order."""

    return sorted(
        [col for col in frame.columns if str(col).startswith("morgan_")],
        key=lambda col: int(str(col).split("_", 1)[1]),
    )


def mobile_phase_system(a_phase: object, b_phase: object) -> str:
    """Map detailed mobile phases to a compact controlled vocabulary."""

    text = f"{a_phase or ''} {b_phase or ''}".lower()
    organic = "acn" if "acetonitrile" in text else "meoh" if "methanol" in text else "other"
    modifier = "formic_acid" if "formic" in text else "ammonium" if "ammonium" in text else "unbuffered"
    return f"{organic}_{modifier}"


def _quality_score(row: dict[str, Any]) -> float:
    explicit = row.get("quality_score")
    if pd.notna(explicit):
        return float(np.clip(explicit, 0.0, 1.0))
    score = 0.55
    if pd.notna(row.get("sn_ratio")):
        score += min(float(row["sn_ratio"]) / 100.0, 0.25)
    if pd.notna(row.get("resolution")):
        score += min(float(row["resolution"]) / 10.0, 0.2)
    asymmetry = row.get("asymmetry")
    tailing = row.get("tailing_factor")
    shape = asymmetry if pd.notna(asymmetry) else tailing
    if pd.notna(shape):
        score += max(0.0, 0.15 - abs(float(shape) - 1.1) * 0.15)
    return float(np.clip(score, 0.0, 1.0))


def _identity_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "compound_name": row.get("compound_name"),
        "canonical_smiles": row.get("canonical_smiles"),
        "inchikey": row.get("inchikey"),
        "source_dataset": row.get("source_dataset"),
        "matrix": row.get("matrix"),
    }


def _target_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {column: row.get(column, np.nan) for column in TARGET_COLUMNS}


def _num(value: object, default: float | None = np.nan) -> float:
    parsed = pd.to_numeric(value, errors="coerce")
    if pd.isna(parsed):
        return float(default) if default is not None and pd.notna(default) else np.nan
    return float(parsed)


def _empty_morgan_fingerprint() -> dict[str, int]:
    return {f"morgan_{idx}": 0 for idx in range(MORGAN_FINGERPRINT_BITS)}
