from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_RECORD_COLUMNS = {
    "compound_name",
    "smiles",
    "dataset_source",
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
    "retention_time_min",
    "quality_score",
}


def load_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)


def validate_records(frame: pd.DataFrame, source_name: str) -> pd.DataFrame:
    missing = REQUIRED_RECORD_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{source_name} import is missing columns: {sorted(missing)}")
    frame = frame.copy()
    frame["dataset_source"] = frame["dataset_source"].fillna(source_name)
    return frame
