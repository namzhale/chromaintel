from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.services.descriptors import DescriptorCalculator


def load_training_records(path: str | Path = "data/mock_training_records.csv") -> pd.DataFrame:
    records = pd.read_csv(path)
    calculator = DescriptorCalculator()
    descriptor_rows = []
    for smiles in records["smiles"]:
        descriptor_rows.append(calculator.model_features(smiles))
    descriptors = pd.DataFrame(descriptor_rows)
    return pd.concat([records.reset_index(drop=True), descriptors.reset_index(drop=True)], axis=1)


def load_dataset_browser_records(path: str | Path = "data/mock_training_records.csv") -> pd.DataFrame:
    return pd.read_csv(path)
