"""Canonical training dataset schema for LC-MS/MS method development."""

from __future__ import annotations


CANONICAL_DATASET_COLUMNS = [
    "compound_name",
    "smiles",
    "canonical_smiles",
    "inchikey",
    "source_dataset",
    "source_record_id",
    "column_name",
    "column_chemistry",
    "stationary_phase_type",
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
    "ion_mode",
    "precursor_mz",
    "product_mz",
    "rt_min",
    "peak_area",
    "peak_height",
    "sn_ratio",
    "tailing_factor",
    "asymmetry",
    "resolution",
    "matrix",
    "success_flag",
    "quality_score",
    "notes",
    "missing_fields_count",
]


REQUIRED_INTERNAL_COLUMNS = [
    "run_id",
    "compound_name",
    "smiles",
    "column_name",
    "mobile_phase_a",
    "mobile_phase_b",
    "rt_min",
]


NUMERIC_CANONICAL_COLUMNS = [
    "ph",
    "initial_organic_pct",
    "final_organic_pct",
    "gradient_duration_min",
    "total_runtime_min",
    "temperature_c",
    "flow_ml_min",
    "injection_ul",
    "precursor_mz",
    "product_mz",
    "rt_min",
    "peak_area",
    "peak_height",
    "sn_ratio",
    "tailing_factor",
    "asymmetry",
    "resolution",
    "quality_score",
]
