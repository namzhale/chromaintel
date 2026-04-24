from pathlib import Path

import pandas as pd

from app.adapters.base import load_table


def load_chembl_annotations(path: str | Path) -> pd.DataFrame:
    """Load optional ChEMBL annotations exported as CSV/JSON.

    Live ChEMBL enrichment can be added later; the MVP keeps this offline-first.
    """

    return load_table(path)
