from pathlib import Path

import pandas as pd

from app.adapters.base import load_table, validate_records


def load_internal_lab_file(path: str | Path) -> pd.DataFrame:
    """Load the lab CSV template for BE-style small molecule assay records."""

    return validate_records(load_table(path), "internal_lab")


def template_columns() -> list[str]:
    return [
        "compound_name",
        "smiles",
        "pubchem_cid",
        "matrix",
        "column",
        "stationary_phase",
        "mobile_phase_a",
        "mobile_phase_b",
        "ph",
        "temperature_c",
        "flow_rate_ml_min",
        "injection_volume_ul",
        "runtime_min",
        "initial_percent_b",
        "final_percent_b",
        "ionization_mode",
        "precursor_mz",
        "transition_quantifier",
        "retention_time_min",
        "peak_area",
        "asymmetry",
        "resolution",
        "signal_to_noise",
        "quality_score",
        "dataset_source",
    ]
