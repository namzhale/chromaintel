from pathlib import Path

import pandas as pd

from app.adapters.base import load_table, validate_records


def load_metlin_smrt_records(path: str | Path) -> pd.DataFrame:
    """Load METLIN SMRT records from an authorized offline export."""

    return validate_records(load_table(path), "METLIN_SMRT")
