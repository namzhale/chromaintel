from pathlib import Path

import pandas as pd

from app.adapters.base import load_table


def load_massbank_reference(path: str | Path) -> pd.DataFrame:
    """Load optional MassBank MS reference metadata from local CSV/JSON."""

    return load_table(path)
