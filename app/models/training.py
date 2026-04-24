from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.feature_engineering import feature_groups


@dataclass(frozen=True)
class ModelMetrics:
    """Regression metrics for a single split."""

    mae: float
    rmse: float
    r2: float


@dataclass(frozen=True)
class TrainingSummary:
    """Serializable summary of the reproducible training run."""

    best_rt_model: str
    best_quality_model: str
    rt_metrics: dict[str, dict[str, float]]
    quality_metrics: dict[str, dict[str, float]]
    n_train: int
    n_validation: int
    n_test: int
    feature_columns: list[str]
    artifact_path: str
    report_path: str


class TrainedForwardModelBundle:
    """Persisted forward models for RT and provisional peak quality."""

    def __init__(
        self,
        rt_model: Pipeline,
        quality_model: Pipeline,
        feature_columns: list[str],
        categorical_features: list[str],
        numeric_features: list[str],
        metadata: dict[str, Any],
    ):
        self.rt_model = rt_model
        self.quality_model = quality_model
        self.feature_columns = feature_columns
        self.categorical_features = categorical_features
        self.numeric_features = numeric_features
        self.metadata = metadata

    def predict(self, feature_row: dict[str, Any]) -> dict[str, Any]:
        frame = pd.DataFrame([{column: feature_row.get(column) for column in self.feature_columns}])
        rt = float(self.rt_model.predict(frame)[0])
        quality = float(np.clip(self.quality_model.predict(frame)[0], 0, 1))
        residual_std = float(self.metadata.get("rt_residual_std", 1.0))
        confidence = float(np.clip(1.0 / (1.0 + residual_std / max(rt, 0.1)), 0.35, 0.92))
        return {
            "predicted_rt_min": max(rt, 0.1),
            "quality_score": quality,
            "confidence": confidence,
            "uncertainty_rt_min": residual_std,
            "model_name": self.metadata.get("best_rt_model", "trained forward model"),
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "rt_model": self.rt_model,
                "quality_model": self.quality_model,
                "feature_columns": self.feature_columns,
                "categorical_features": self.categorical_features,
                "numeric_features": self.numeric_features,
                "metadata": self.metadata,
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "TrainedForwardModelBundle":
        payload = joblib.load(path)
        return cls(
            payload["rt_model"],
            payload["quality_model"],
            payload["feature_columns"],
            payload["categorical_features"],
            payload["numeric_features"],
            payload["metadata"],
        )


def train_forward_models(
    model_matrix: pd.DataFrame,
    artifact_path: str | Path = "data/processed/models/trained_forward_bundle.joblib",
    report_dir: str | Path = "reports",
    plots_dir: str | Path = "data/processed/plots",
) -> TrainingSummary:
    """Train linear, RandomForest, and HistGradientBoosting models for RT and quality."""

    usable = model_matrix.dropna(subset=["rt_min"]).copy().replace({pd.NA: np.nan})
    usable["quality_score"] = usable["quality_score"].fillna(0.5)
    if len(usable) < 8:
        raise ValueError("At least 8 usable rows are required for train/validation/test splits")

    groups = feature_groups(usable)
    feature_columns = groups.combined
    categorical = groups.lc_categorical + ["ion_mode"]
    categorical = [col for col in categorical if col in feature_columns]
    numeric = [col for col in feature_columns if col not in categorical]

    train_val, test = train_test_split(usable, test_size=0.2, random_state=42)
    train, validation = train_test_split(train_val, test_size=0.25, random_state=42)
    models = _candidate_models(categorical, numeric)

    rt_results = _fit_and_score(models, train, validation, test, feature_columns, "rt_min")
    quality_results = _fit_and_score(models, train, validation, test, feature_columns, "quality_score")

    best_rt_name = min(rt_results, key=lambda name: rt_results[name]["validation"].mae)
    best_quality_name = min(quality_results, key=lambda name: quality_results[name]["validation"].mae)
    rt_model = rt_results[best_rt_name]["model"]
    quality_model = quality_results[best_quality_name]["model"]

    test_predictions = test[["compound_name", "source_dataset", "rt_min", "quality_score"]].copy()
    test_predictions["predicted_rt_min"] = rt_model.predict(test[feature_columns])
    test_predictions["predicted_quality_score"] = np.clip(quality_model.predict(test[feature_columns]), 0, 1)
    residual_std = float(np.std(test_predictions["predicted_rt_min"] - test_predictions["rt_min"]))
    feature_importance = _permutation_importance(rt_model, test, feature_columns)

    metadata = {
        "best_rt_model": best_rt_name,
        "best_quality_model": best_quality_name,
        "rt_residual_std": residual_std,
        "feature_importance": feature_importance.to_dict("records"),
        "rt_metrics": _metrics_payload(rt_results),
        "quality_metrics": _metrics_payload(quality_results),
        "provisional_quality_note": (
            "Quality score is provisional. It uses observed quality_score when present; "
            "otherwise it is a transparent proxy from S/N, resolution, asymmetry, and tailing."
        ),
    }
    bundle = TrainedForwardModelBundle(rt_model, quality_model, feature_columns, categorical, numeric, metadata)
    bundle.save(artifact_path)

    report_path = generate_training_outputs(
        model_matrix=usable,
        test_predictions=test_predictions,
        feature_importance=feature_importance,
        metadata=metadata,
        report_dir=report_dir,
        plots_dir=plots_dir,
    )

    return TrainingSummary(
        best_rt_model=best_rt_name,
        best_quality_model=best_quality_name,
        rt_metrics=_metrics_payload(rt_results),
        quality_metrics=_metrics_payload(quality_results),
        n_train=len(train),
        n_validation=len(validation),
        n_test=len(test),
        feature_columns=feature_columns,
        artifact_path=str(artifact_path),
        report_path=str(report_path),
    )


def generate_training_outputs(
    model_matrix: pd.DataFrame,
    test_predictions: pd.DataFrame,
    feature_importance: pd.DataFrame,
    metadata: dict[str, Any],
    report_dir: str | Path = "reports",
    plots_dir: str | Path = "data/processed/plots",
) -> Path:
    """Write demo-ready evaluation plots and markdown report."""

    report_dir = Path(report_dir)
    plots_dir = Path(plots_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    test_predictions = test_predictions.copy()
    test_predictions["rt_error_min"] = test_predictions["predicted_rt_min"] - test_predictions["rt_min"]
    px.scatter(
        test_predictions,
        x="rt_min",
        y="predicted_rt_min",
        color="source_dataset",
        hover_data=["compound_name"],
        title="Predicted vs Actual RT",
    ).write_html(plots_dir / "predicted_vs_actual_rt.html")
    px.histogram(
        test_predictions,
        x="rt_error_min",
        color="source_dataset",
        title="RT Error Distribution",
    ).write_html(plots_dir / "rt_error_distribution.html")
    source_perf = (
        test_predictions.assign(abs_error=lambda df: df["rt_error_min"].abs())
        .groupby("source_dataset", dropna=False)["abs_error"]
        .mean()
        .reset_index(name="rt_mae")
    )
    px.bar(source_perf, x="source_dataset", y="rt_mae", title="Source-wise RT MAE").write_html(
        plots_dir / "source_wise_performance.html"
    )
    px.bar(
        feature_importance.head(20),
        x="importance_mean",
        y="feature",
        orientation="h",
        title="Permutation Feature Importance",
    ).write_html(plots_dir / "feature_importance.html")

    report = report_dir / "model_training_summary.md"
    report.write_text(_report_markdown(model_matrix, metadata, source_perf), encoding="utf-8")
    test_predictions.to_csv(report_dir / "test_predictions.csv", index=False)
    feature_importance.to_csv(report_dir / "feature_importance.csv", index=False)
    return report


def _candidate_models(categorical: list[str], numeric: list[str]) -> dict[str, Pipeline]:
    return {
        "linear_ridge": Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric, scale_numeric=True)),
                ("model", Ridge(alpha=1.0)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                ("model", RandomForestRegressor(n_estimators=180, random_state=42, min_samples_leaf=1)),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                ("model", HistGradientBoostingRegressor(random_state=42, max_iter=120)),
            ]
        ),
    }


def _preprocessor(categorical: list[str], numeric: list[str], scale_numeric: bool = False) -> ColumnTransformer:
    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    return ColumnTransformer(
        transformers=[
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
            ("num", Pipeline(numeric_steps), numeric),
        ],
        verbose_feature_names_out=False,
    )


def _fit_and_score(
    models: dict[str, Pipeline],
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    feature_columns: list[str],
    target: str,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for name, model in models.items():
        fitted = copy.deepcopy(model)
        fitted.fit(train[feature_columns], train[target])
        results[name] = {
            "model": fitted,
            "validation": _metrics(validation[target], fitted.predict(validation[feature_columns])),
            "test": _metrics(test[target], fitted.predict(test[feature_columns])),
        }
    return results


def _metrics(y_true: pd.Series, y_pred: np.ndarray) -> ModelMetrics:
    return ModelMetrics(
        mae=float(mean_absolute_error(y_true, y_pred)),
        rmse=float(mean_squared_error(y_true, y_pred) ** 0.5),
        r2=float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
    )


def _metrics_payload(results: dict[str, dict[str, Any]]) -> dict[str, dict[str, float]]:
    return {
        name: {
            "validation_mae": payload["validation"].mae,
            "validation_rmse": payload["validation"].rmse,
            "validation_r2": payload["validation"].r2,
            "test_mae": payload["test"].mae,
            "test_rmse": payload["test"].rmse,
            "test_r2": payload["test"].r2,
        }
        for name, payload in results.items()
    }


def _permutation_importance(model: Pipeline, test: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    if len(test) < 2:
        return pd.DataFrame({"feature": feature_columns, "importance_mean": 0.0, "importance_std": 0.0})
    result = permutation_importance(
        model,
        test[feature_columns],
        test["rt_min"],
        n_repeats=8,
        random_state=42,
        scoring="neg_mean_absolute_error",
    )
    return (
        pd.DataFrame(
            {
                "feature": feature_columns,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )


def _report_markdown(model_matrix: pd.DataFrame, metadata: dict[str, Any], source_perf: pd.DataFrame) -> str:
    source_counts = model_matrix["source_dataset"].value_counts(dropna=False).to_dict()
    rt_metrics = _markdown_table(pd.DataFrame(metadata["rt_metrics"]).T.round(3).reset_index(names="model"))
    quality_metrics = _markdown_table(pd.DataFrame(metadata["quality_metrics"]).T.round(3).reset_index(names="model"))
    source_table = _markdown_table(source_perf.round(3))
    return f"""# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: {len(model_matrix)}
- Compounds: {model_matrix['compound_name'].nunique()}
- Source distribution: {source_counts}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Models Tested

- Linear baseline: Ridge regression
- RandomForestRegressor
- HistGradientBoostingRegressor

## Best Models

- RT model: `{metadata['best_rt_model']}`
- Peak quality surrogate: `{metadata['best_quality_model']}`

## RT Metrics

{rt_metrics}

## Quality Metrics

{quality_metrics}

## Source-wise Performance

{source_table}

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently {metadata['rt_residual_std']:.3f} min.

## Current Limitations

- The checked-in dataset is a small mock/demo set, not yet a validated internal laboratory history.
- Public RT datasets often lack peak quality, matrix, sample preparation, and MS transition metadata.
- Peak quality is provisional. {metadata['provisional_quality_note']}
- Source-aware validation is reported by source distribution and source-wise error; larger datasets should use source holdout splits.

## Next Steps

1. Import internal historical BE assay development runs using the internal template.
2. Calibrate RT and quality models on accepted lab methods by instrument platform and matrix.
3. Add explicit uncertainty calibration and applicability-domain checks.
4. Expand candidate search spaces to match available columns, solvents, and validated operating ranges.
"""


def _markdown_table(frame: pd.DataFrame) -> str:
    """Render a small markdown table without pandas' optional tabulate dependency."""

    if frame.empty:
        return "_No rows._"
    text_frame = frame.fillna("").astype(str)
    headers = list(text_frame.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in text_frame.iterrows():
        lines.append("| " + " | ".join(row[col] for col in headers) + " |")
    return "\n".join(lines)
