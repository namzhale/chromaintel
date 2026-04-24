from pathlib import Path

import pandas as pd

from app.adapters.base import load_table, validate_records


def load_report_records(path: str | Path) -> pd.DataFrame:
    """Load RepoRT-style normalized RT records with chromatographic metadata."""

    return validate_records(load_table(path), "RepoRT")
