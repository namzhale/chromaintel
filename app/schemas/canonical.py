"""Registry-level canonical LC-MS/MS schema helpers."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping


CANONICAL_REGISTRY_FIELDS: dict[str, tuple[str, ...]] = {
    "compound": (
        "compound_name",
        "smiles",
        "canonical_smiles",
        "inchikey",
        "pubchem_cid",
        "chembl_id",
    ),
    "lc_method": (
        "column_name",
        "column_chemistry",
        "stationary_phase_type",
        "chromatography_mode",
        "mobile_phase_a",
        "mobile_phase_b",
        "ph",
        "gradient_profile",
        "initial_organic_pct",
        "final_organic_pct",
        "gradient_duration_min",
        "total_runtime_min",
        "temperature_c",
        "flow_ml_min",
        "injection_ul",
    ),
    "ms_method": (
        "ion_mode",
        "precursor_mz",
        "product_mz",
        "collision_energy",
        "polarity",
        "ms_platform",
    ),
    "sample_context": (
        "matrix",
        "sample_prep",
        "species",
        "biofluid",
        "dilution_factor",
    ),
    "observation": (
        "rt_min",
        "success_flag",
        "run_id",
        "batch_id",
        "replicate_id",
    ),
    "peak_metrics": (
        "peak_area",
        "peak_height",
        "sn_ratio",
        "tailing_factor",
        "asymmetry",
        "resolution",
        "peak_width_base_min",
        "peak_width_half_height_min",
        "quality_score",
    ),
    "provenance": (
        "source_dataset",
        "source_record_id",
        "source_url",
        "license",
        "notes",
    ),
}

REQUIRED_REGISTRY_FIELDS: tuple[str, ...] = (
    "canonical_smiles",
    "column_name",
    "mobile_phase_a",
    "mobile_phase_b",
    "rt_min",
    "source_dataset",
)

METHOD_HASH_FIELDS: tuple[str, ...] = (
    "column_name",
    "column_chemistry",
    "stationary_phase_type",
    "chromatography_mode",
    "mobile_phase_a",
    "mobile_phase_b",
    "ph",
    "gradient_profile",
    "initial_organic_pct",
    "final_organic_pct",
    "gradient_duration_min",
    "flow_ml_min",
    "temperature_c",
    "total_runtime_min",
)

SOURCE_QUALITY_WEIGHTS: dict[str, tuple[float, tuple[str, ...]]] = {
    "structure": (0.25, ("canonical_smiles", "inchikey")),
    "rt": (0.20, ("rt_min",)),
    "lc_metadata": (0.20, ("column_name", "mobile_phase_a", "mobile_phase_b", "gradient_profile")),
    "ms_metadata": (0.15, ("ion_mode", "precursor_mz", "product_mz")),
    "sample_context": (0.10, ("matrix",)),
    "peak_metrics": (
        0.10,
        (
            "peak_area",
            "peak_height",
            "sn_ratio",
            "tailing_factor",
            "asymmetry",
            "resolution",
            "peak_width_base_min",
            "peak_width_half_height_min",
        ),
    ),
}


def all_registry_fields() -> tuple[str, ...]:
    """Return registry fields in stable group order without duplicates."""

    fields: list[str] = []
    for group in CANONICAL_REGISTRY_FIELDS.values():
        for field in group:
            if field not in fields:
                fields.append(field)
    return tuple(fields)


def missing_required_fields(record: Mapping[str, object]) -> list[str]:
    """Return required registry fields that are absent, null, or blank."""

    return [field for field in REQUIRED_REGISTRY_FIELDS if _is_blank(record.get(field))]


def validate_registry_record(record: Mapping[str, object]) -> list[str]:
    """Return human-readable validation issues for a canonical registry row."""

    issues = [f"missing required field: {field}" for field in missing_required_fields(record)]
    rt = _to_float(record.get("rt_min"))
    if rt is not None and rt < 0:
        issues.append("rt_min must be non-negative")
    ph = _to_float(record.get("ph"))
    if ph is not None and not 0 <= ph <= 14:
        issues.append("ph must be between 0 and 14")
    for field in ("initial_organic_pct", "final_organic_pct"):
        value = _to_float(record.get(field))
        if value is not None and not 0 <= value <= 100:
            issues.append(f"{field} must be between 0 and 100")
    return issues


def method_hash(record: Mapping[str, object]) -> str:
    """Hash normalized LC method identity fields for registry-level grouping."""

    payload = {field: _normalize_value(record.get(field)) for field in METHOD_HASH_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()[:16]


def duplicate_key(record: Mapping[str, object]) -> tuple[object, ...]:
    """Return the duplicate-policy key for a compound-method observation."""

    identity = record.get("inchikey") if not _is_blank(record.get("inchikey")) else record.get("canonical_smiles")
    return (
        _normalize_identity(identity),
        method_hash(record),
        _normalize_text(record.get("ion_mode")),
        _rounded_float(record.get("precursor_mz"), 4),
        _rounded_float(record.get("product_mz"), 4),
        _normalize_text(record.get("matrix")),
        _rounded_float(record.get("rt_min"), 2),
    )


def source_quality_score(record: Mapping[str, object]) -> float:
    """Score source completeness from 0 to 1 using registry-level weighted groups."""

    score = 0.0
    for weight, fields in SOURCE_QUALITY_WEIGHTS.values():
        present = sum(0 if _is_blank(record.get(field)) else 1 for field in fields)
        score += weight * (present / len(fields))
    return round(min(score, 1.0), 4)


def _normalize_value(value: object) -> object:
    number = _to_float(value)
    if number is not None:
        return round(number, 6)
    return _normalize_text(value)


def _normalize_text(value: object) -> str | None:
    if _is_blank(value):
        return None
    return " ".join(str(value).strip().lower().split())


def _normalize_identity(value: object) -> str | None:
    if _is_blank(value):
        return None
    return " ".join(str(value).strip().split())


def _rounded_float(value: object, digits: int) -> float | None:
    number = _to_float(value)
    if number is None:
        return None
    return round(number, digits)


def _to_float(value: object) -> float | None:
    if _is_blank(value):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())
