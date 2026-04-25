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
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
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
    feature_importance_path: str
    validation_metadata: dict[str, Any]
    uncertainty_metadata: dict[str, Any]


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
        uncertainty = float(self.metadata.get("rt_conformal_q90_min", self.metadata.get("rt_residual_std", 1.0)))
        confidence = float(np.clip(1.0 / (1.0 + uncertainty / max(rt, 0.1)), 0.35, 0.92))
        return {
            "predicted_rt_min": max(rt, 0.1),
            "quality_score": quality,
            "confidence": confidence,
            "uncertainty_rt_min": uncertainty,
            "rt_interval_min": [max(rt - uncertainty, 0.1), rt + uncertainty],
            "uncertainty_method": self.metadata.get("rt_uncertainty_method", "residual_proxy"),
            "model_name": self.metadata.get("best_rt_model", "trained forward model"),
        }

    def applicability_domain_check(self, feature_row: dict[str, Any]) -> dict[str, Any]:
        """Check a prediction row against training-domain metadata."""

        domain = self.metadata.get("applicability_domain") or {}
        numeric_ranges = domain.get("numeric_ranges", {})
        categorical_values = domain.get("categorical_values", {})
        reasons: list[str] = []
        for feature, bounds in numeric_ranges.items():
            value = pd.to_numeric(feature_row.get(feature), errors="coerce")
            if pd.isna(value):
                continue
            lower = bounds.get("min")
            upper = bounds.get("max")
            if lower is not None and float(value) < float(lower):
                reasons.append(f"{feature} below training range ({float(value):.3g} < {float(lower):.3g})")
            if upper is not None and float(value) > float(upper):
                reasons.append(f"{feature} above training range ({float(value):.3g} > {float(upper):.3g})")
        for feature, allowed in categorical_values.items():
            value = feature_row.get(feature)
            if pd.notna(value) and str(value) not in set(allowed):
                reasons.append(f"{feature} unseen category ({value})")
        return {
            "out_of_domain": bool(reasons),
            "reasons": reasons,
            "method": domain.get("method", "training_feature_ranges"),
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
            compress=3,
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
    test_predictions["rt_error_min"] = test_predictions["predicted_rt_min"] - test_predictions["rt_min"]
    test_predictions["abs_rt_error_min"] = test_predictions["rt_error_min"].abs()
    test_predictions = _add_applicability_domain_flags(test_predictions, test, usable, numeric)
    residual_std = float(np.std(test_predictions["rt_error_min"]))
    validation_rt_error = rt_model.predict(validation[feature_columns]) - validation["rt_min"]
    uncertainty_metadata = {
        "rt": {
            "method": "split_conformal_abs_residual_q90",
            "q90_min": float(np.quantile(np.abs(validation_rt_error), 0.9)),
            "residual_std_min": residual_std,
        }
    }
    feature_importance = _permutation_importance(rt_model, test, feature_columns)
    applicability_domain = _applicability_domain_metadata(train, numeric, categorical)
    validation_metadata = {
        "split_strategy": "random_holdout_with_source_metadata",
        "source_counts": {
            "train": _source_counts(train),
            "validation": _source_counts(validation),
            "test": _source_counts(test),
        },
        "group_column": "inchikey" if "inchikey" in usable.columns else "compound_name",
    }
    validation_metadata["group_overlap_counts"] = _group_overlap_counts(
        train,
        validation,
        test,
        str(validation_metadata["group_column"]),
    )

    metadata = {
        "best_rt_model": best_rt_name,
        "best_quality_model": best_quality_name,
        "candidate_models": list(models.keys()),
        "rt_residual_std": residual_std,
        "rt_conformal_q90_min": uncertainty_metadata["rt"]["q90_min"],
        "rt_uncertainty_method": uncertainty_metadata["rt"]["method"],
        "validation_metadata": validation_metadata,
        "uncertainty_metadata": uncertainty_metadata,
        "applicability_domain": applicability_domain,
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
        feature_importance_path=str(Path(report_dir) / "feature_importance.csv"),
        validation_metadata=validation_metadata,
        uncertainty_metadata=uncertainty_metadata,
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
    if "rt_error_min" not in test_predictions:
        test_predictions["rt_error_min"] = test_predictions["predicted_rt_min"] - test_predictions["rt_min"]
    if "abs_rt_error_min" not in test_predictions:
        test_predictions["abs_rt_error_min"] = test_predictions["rt_error_min"].abs()
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
    source_perf = _source_metrics(test_predictions)
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
    source_perf.to_csv(report_dir / "source_metrics.csv", index=False)
    (report_dir / "sota_model_experiments.md").write_text(_sota_markdown(metadata), encoding="utf-8")
    return report


def _candidate_models(categorical: list[str], numeric: list[str]) -> dict[str, Pipeline]:
    models = {
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
        "extra_trees": Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                ("model", ExtraTreesRegressor(n_estimators=240, random_state=42, min_samples_leaf=1)),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                ("model", HistGradientBoostingRegressor(random_state=42, max_iter=120)),
            ]
        ),
    }
    models.update(_optional_boosting_models(categorical, numeric))
    return models


def _optional_boosting_models(categorical: list[str], numeric: list[str]) -> dict[str, Pipeline]:
    """Return optional CPU gradient-boosting candidates when dependencies exist."""

    models: dict[str, Pipeline] = {}
    try:
        from xgboost import XGBRegressor
    except Exception:
        XGBRegressor = None
    if XGBRegressor is not None:
        models["xgboost"] = Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                (
                    "model",
                    XGBRegressor(
                        objective="reg:squarederror",
                        n_estimators=350,
                        max_depth=6,
                        learning_rate=0.05,
                        subsample=0.9,
                        colsample_bytree=0.85,
                        tree_method="hist",
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        )
    try:
        from catboost import CatBoostRegressor
    except Exception:
        CatBoostRegressor = None
    if CatBoostRegressor is not None:
        models["catboost"] = Pipeline(
            [
                ("prep", _preprocessor(categorical, numeric)),
                (
                    "model",
                    CatBoostRegressor(
                        loss_function="RMSE",
                        iterations=350,
                        depth=6,
                        learning_rate=0.05,
                        random_seed=42,
                        thread_count=1,
                        verbose=False,
                        allow_writing_files=False,
                    ),
                ),
            ]
        )
    return models


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
        frame = pd.DataFrame({"feature": feature_columns, "importance_mean": 0.0, "importance_std": 0.0})
        return _annotate_importance(frame)
    result = permutation_importance(
        model,
        test[feature_columns],
        test["rt_min"],
        n_repeats=8,
        random_state=42,
        scoring="neg_mean_absolute_error",
    )
    importance = (
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
    return _annotate_importance(importance)


def _annotate_importance(importance: pd.DataFrame) -> pd.DataFrame:
    annotated = importance.copy()
    annotated["feature_group"] = annotated["feature"].map(_feature_group)
    annotated["importance_z"] = annotated.apply(
        lambda row: float(row["importance_mean"] / row["importance_std"])
        if row["importance_std"]
        else 0.0,
        axis=1,
    )
    annotated["significance"] = annotated.apply(_importance_significance, axis=1)
    return annotated


def _feature_group(feature: str) -> str:
    descriptor_features = {
        "molecular_weight",
        "logp",
        "tpsa",
        "hbond_donors",
        "hbond_acceptors",
        "rotatable_bonds",
        "aromatic_ring_count",
        "formal_charge",
        "heavy_atom_count",
        "fraction_csp3",
    }
    lc_numeric = {
        "ph",
        "temperature_c",
        "flow_ml_min",
        "injection_ul",
        "initial_organic_pct",
        "final_organic_pct",
        "gradient_duration_min",
        "total_runtime_min",
        "gradient_slope_percent_b_min",
    }
    lc_categorical = {
        "column_name",
        "column_chemistry",
        "stationary_phase_type",
        "mobile_phase_a",
        "mobile_phase_b",
        "mobile_phase_system",
    }
    ms_features = {"ion_mode", "precursor_mz", "product_mz"}
    if feature in descriptor_features:
        return "compound_descriptor"
    if feature in lc_numeric:
        return "lc_numeric"
    if feature in lc_categorical:
        return "lc_categorical"
    if feature in ms_features:
        return "ms_setting"
    return "other"


def _importance_significance(row: pd.Series) -> str:
    mean = float(row["importance_mean"])
    std = float(row["importance_std"])
    z_score = float(row["importance_z"])
    if mean < 0:
        return "negative"
    if mean > 0 and (std == 0 or z_score >= 2):
        return "positive"
    if mean > 0 and z_score >= 1:
        return "weak_positive"
    return "neutral_or_unstable"


def _source_counts(frame: pd.DataFrame) -> dict[str, int]:
    if "source_dataset" not in frame:
        return {}
    return {str(source): int(count) for source, count in frame["source_dataset"].value_counts(dropna=False).items()}


def _group_overlap_counts(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    group_column: str,
) -> dict[str, int]:
    if group_column not in train or group_column not in validation or group_column not in test:
        return {"train_validation": 0, "train_test": 0, "validation_test": 0}
    train_groups = {str(value) for value in train[group_column].dropna().unique()}
    validation_groups = {str(value) for value in validation[group_column].dropna().unique()}
    test_groups = {str(value) for value in test[group_column].dropna().unique()}
    return {
        "train_validation": len(train_groups & validation_groups),
        "train_test": len(train_groups & test_groups),
        "validation_test": len(validation_groups & test_groups),
    }


def _source_metrics(test_predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, group in test_predictions.groupby("source_dataset", dropna=False):
        errors = group["rt_error_min"]
        abs_errors = errors.abs()
        rows.append(
            {
                "source_dataset": source,
                "n_test": int(len(group)),
                "rt_mae": float(abs_errors.mean()),
                "rt_rmse": float((errors.pow(2).mean()) ** 0.5),
                "mean_bias": float(errors.mean()),
                "median_abs_error": float(abs_errors.median()),
                "ad_flagged": int(group["ad_flag"].sum()) if "ad_flag" in group else 0,
            }
        )
    return pd.DataFrame(rows).sort_values(["rt_mae", "source_dataset"], ascending=[False, True]).reset_index(drop=True)


def _add_applicability_domain_flags(
    predictions: pd.DataFrame,
    test: pd.DataFrame,
    reference: pd.DataFrame,
    numeric_features: list[str],
) -> pd.DataFrame:
    flagged = predictions.copy()
    numeric_ranges = {
        feature: (reference[feature].min(), reference[feature].max())
        for feature in numeric_features
        if feature in reference and pd.api.types.is_numeric_dtype(reference[feature])
    }
    ad_flags = []
    ad_reasons = []
    for _, row in test.iterrows():
        reasons = []
        for feature, (lower, upper) in numeric_ranges.items():
            value = row.get(feature)
            if pd.notna(value) and (value < lower or value > upper):
                reasons.append(f"{feature} outside training range")
        ad_flags.append(bool(reasons))
        ad_reasons.append("; ".join(reasons) if reasons else "inside_training_range")
    flagged["ad_flag"] = ad_flags
    flagged["ad_reason"] = ad_reasons
    return flagged


def _applicability_domain_metadata(
    train: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
) -> dict[str, Any]:
    """Build training-domain metadata for prediction-time out-of-domain checks."""

    numeric_ranges: dict[str, dict[str, float | None]] = {}
    for feature in numeric_features:
        if feature not in train:
            continue
        values = pd.to_numeric(train[feature], errors="coerce")
        numeric_ranges[feature] = {
            "min": float(values.min()) if values.notna().any() else None,
            "max": float(values.max()) if values.notna().any() else None,
        }
    categorical_values = {
        feature: sorted(str(value) for value in train[feature].dropna().unique())
        for feature in categorical_features
        if feature in train
    }
    return {
        "method": "training_feature_ranges",
        "numeric_ranges": numeric_ranges,
        "categorical_values": categorical_values,
    }


def _sota_markdown(metadata: dict[str, Any]) -> str:
    rt_metrics = _markdown_table(pd.DataFrame(metadata["rt_metrics"]).T.round(3).reset_index(names="model"))
    quality_metrics = _markdown_table(pd.DataFrame(metadata["quality_metrics"]).T.round(3).reset_index(names="model"))
    return f"""# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

## RT Metrics

{rt_metrics}

## Quality Metrics

{quality_metrics}

Candidate models: {', '.join(metadata.get('candidate_models', []))}

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. Treat public-source performance as diagnostic until source/group holdout validation is added.
"""


def _report_markdown(model_matrix: pd.DataFrame, metadata: dict[str, Any], source_perf: pd.DataFrame) -> str:
    source_counts = model_matrix["source_dataset"].value_counts(dropna=False).to_dict()
    rt_metrics = _markdown_table(pd.DataFrame(metadata["rt_metrics"]).T.round(3).reset_index(names="model"))
    quality_metrics = _markdown_table(pd.DataFrame(metadata["quality_metrics"]).T.round(3).reset_index(names="model"))
    source_table = _markdown_table(source_perf.round(3))
    model_lines = "\n".join(f"- {name}" for name in metadata.get("candidate_models", []))
    return f"""# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: {len(model_matrix)}
- Compounds: {model_matrix['compound_name'].nunique()}
- Source distribution: {source_counts}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Models Tested

{model_lines}

## Best Models

- RT model: `{metadata['best_rt_model']}`
- Peak quality surrogate: `{metadata['best_quality_model']}`

## RT Metrics

{rt_metrics}

## Quality Metrics

{quality_metrics}

## Source-wise Performance

{source_table}

## Parameter Significance

`reports/feature_importance.csv` contains permutation importance for the selected RT model with feature groups, z-like stability scores, and significance labels: `positive`, `weak_positive`, `neutral_or_unstable`, and `negative`. These labels are diagnostic only on the current small held-out split.

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently {metadata['rt_residual_std']:.3f} min.
- Split-conformal q90 absolute RT residual: {metadata['uncertainty_metadata']['rt']['q90_min']:.3f} min.

## Current Limitations

- The checked-in dataset is a small mock/demo set, not yet a validated internal laboratory history.
- Public RT datasets often lack peak quality, matrix, sample preparation, and MS transition metadata.
- {metadata['provisional_quality_note']}
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
