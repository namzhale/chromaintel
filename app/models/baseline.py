from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.services.features import CATEGORICAL_FEATURES


TARGET_RT = "retention_time_min"
TARGET_QUALITY = "quality_score"


@dataclass
class TrainingResult:
    rt_mae: float
    rt_rmse: float
    quality_mae: float
    n_train: int
    n_validation: int
    artifact_path: Path


class BaselineModelBundle:
    """Two RandomForest regressors: RT and aggregate peak quality."""

    def __init__(self, rt_model: Pipeline, quality_model: Pipeline, feature_columns: list[str]):
        self.rt_model = rt_model
        self.quality_model = quality_model
        self.feature_columns = feature_columns

    def predict(self, feature_row: dict[str, Any]) -> dict[str, float]:
        frame = pd.DataFrame([{key: feature_row.get(key) for key in self.feature_columns}])
        rt = float(self.rt_model.predict(frame)[0])
        quality = float(np.clip(self.quality_model.predict(frame)[0], 0, 1))
        return {"predicted_rt_min": max(rt, 0.1), "quality_score": quality}

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "rt_model": self.rt_model,
                "quality_model": self.quality_model,
                "feature_columns": self.feature_columns,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> "BaselineModelBundle":
        payload = joblib.load(path)
        return cls(payload["rt_model"], payload["quality_model"], payload["feature_columns"])


def train_baseline_models(
    records: pd.DataFrame,
    artifact_path: str | Path = "data/processed/models/baseline_bundle.joblib",
) -> TrainingResult:
    usable = records.dropna(subset=[TARGET_RT, TARGET_QUALITY]).copy()
    if len(usable) < 4:
        raise ValueError("At least 4 records are required to train baseline models")

    feature_columns = [
        column
        for column in usable.columns
        if column
        not in {
            TARGET_RT,
            TARGET_QUALITY,
            "compound_name",
            "smiles",
            "dataset_source",
            "matrix",
        }
    ]
    categorical = [col for col in CATEGORICAL_FEATURES if col in feature_columns]
    numeric = [col for col in feature_columns if col not in categorical]

    x_train, x_val, y_rt_train, y_rt_val = train_test_split(
        usable[feature_columns],
        usable[TARGET_RT],
        test_size=0.3,
        random_state=42,
    )
    y_quality_train = usable.loc[x_train.index, TARGET_QUALITY]
    y_quality_val = usable.loc[x_val.index, TARGET_QUALITY]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", "passthrough", numeric),
        ]
    )
    rt_model = Pipeline(
        [
            ("prep", preprocessor),
            ("rf", RandomForestRegressor(n_estimators=120, random_state=42, min_samples_leaf=1)),
        ]
    )
    quality_model = Pipeline(
        [
            ("prep", preprocessor),
            ("rf", RandomForestRegressor(n_estimators=120, random_state=7, min_samples_leaf=1)),
        ]
    )

    rt_model.fit(x_train, y_rt_train)
    quality_model.fit(x_train, y_quality_train)
    rt_pred = rt_model.predict(x_val)
    quality_pred = quality_model.predict(x_val)

    bundle = BaselineModelBundle(rt_model, quality_model, feature_columns)
    artifact = Path(artifact_path)
    bundle.save(artifact)

    return TrainingResult(
        rt_mae=float(mean_absolute_error(y_rt_val, rt_pred)),
        rt_rmse=float(mean_squared_error(y_rt_val, rt_pred) ** 0.5),
        quality_mae=float(mean_absolute_error(y_quality_val, quality_pred)),
        n_train=len(x_train),
        n_validation=len(x_val),
        artifact_path=artifact,
    )
