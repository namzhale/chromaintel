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
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
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

    group_column = _group_column(usable)
    train, validation, test = _grouped_train_validation_test_split(usable, group_column)
    models = _candidate_models(categorical, numeric)

    rt_results = _fit_and_score(models, train, validation, test, feature_columns, "rt_min")
    quality_results = _fit_and_score(models, train, validation, test, feature_columns, "quality_score")
    rt_cv_results = _group_kfold_scores(models, usable, feature_columns, "rt_min", group_column)
    quality_cv_results = _group_kfold_scores(models, usable, feature_columns, "quality_score", group_column)

    best_rt_name = min(rt_cv_results, key=lambda name: rt_cv_results[name]["mae_mean"])
    best_quality_name = min(quality_cv_results, key=lambda name: quality_cv_results[name]["mae_mean"])
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
    cv_metrics = _cv_metrics_frame({"rt_min": rt_cv_results, "quality_score": quality_cv_results}, group_column, usable)
    source_holdout_metrics = _source_family_holdout_metrics(models, usable, feature_columns, ["rt_min", "quality_score"], group_column)
    validation_metadata = {
        "split_strategy": "group_shuffle_holdout_with_group_kfold_model_selection",
        "cv_strategy": "GroupKFold",
        "n_cv_splits": int(cv_metrics["n_folds"].max()) if not cv_metrics.empty else 0,
        "source_counts": {
            "train": _source_counts(train),
            "validation": _source_counts(validation),
            "test": _source_counts(test),
        },
        "group_column": group_column,
        "group_counts": {
            "all": int(_groups_for_split(usable, group_column).nunique()),
            "train": int(_groups_for_split(train, group_column).nunique()),
            "validation": int(_groups_for_split(validation, group_column).nunique()),
            "test": int(_groups_for_split(test, group_column).nunique()),
        },
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
        "rt_cv_metrics": _cv_metrics_payload(rt_cv_results),
        "quality_cv_metrics": _cv_metrics_payload(quality_cv_results),
        "cv_metrics": cv_metrics.to_dict("records"),
        "source_holdout_metrics": source_holdout_metrics.to_dict("records"),
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
        cv_metrics=cv_metrics,
        source_holdout_metrics=source_holdout_metrics,
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


def _group_column(frame: pd.DataFrame) -> str:
    """Choose the strongest available compound identity column for leakage-aware splits."""

    if "inchikey" in frame and frame["inchikey"].notna().sum() >= 2:
        return "inchikey"
    if "canonical_smiles" in frame and frame["canonical_smiles"].notna().sum() >= 2:
        return "canonical_smiles"
    return "compound_name"


def _groups_for_split(frame: pd.DataFrame, group_column: str) -> pd.Series:
    """Return stable group labels, keeping missing identities row-unique."""

    if group_column not in frame:
        base = pd.Series(pd.NA, index=frame.index, dtype="object")
    else:
        base = frame[group_column].astype("object")
    labels = []
    for index, value in base.items():
        if pd.isna(value) or not str(value).strip():
            labels.append(f"missing:{index}")
        else:
            labels.append(str(value))
    return pd.Series(labels, index=frame.index, dtype="object")


def _grouped_train_validation_test_split(
    usable: pd.DataFrame,
    group_column: str,
    test_size: float = 0.2,
    validation_size: float = 0.25,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split rows without sharing compound groups across train, validation, and test."""

    groups = _groups_for_split(usable, group_column)
    if groups.nunique() < 3:
        raise ValueError("At least three unique compound groups are required for grouped train/validation/test splits")

    first_split = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_val_idx, test_idx = next(first_split.split(usable, groups=groups))
    train_val = usable.iloc[train_val_idx].copy()
    test = usable.iloc[test_idx].copy()

    train_val_groups = _groups_for_split(train_val, group_column)
    second_split = GroupShuffleSplit(n_splits=1, test_size=validation_size, random_state=random_state + 1)
    train_idx, validation_idx = next(second_split.split(train_val, groups=train_val_groups))
    train = train_val.iloc[train_idx].copy()
    validation = train_val.iloc[validation_idx].copy()
    return train, validation, test


def _group_kfold_scores(
    models: dict[str, Pipeline],
    frame: pd.DataFrame,
    feature_columns: list[str],
    target: str,
    group_column: str,
    n_splits: int = 5,
) -> dict[str, dict[str, Any]]:
    """Evaluate candidate models with GroupKFold so compounds do not leak across folds."""

    groups = _groups_for_split(frame, group_column)
    split_count = min(n_splits, int(groups.nunique()))
    if split_count < 2:
        raise ValueError("At least two unique compound groups are required for GroupKFold")

    splitter = GroupKFold(n_splits=split_count)
    results: dict[str, dict[str, Any]] = {}
    for name, model in models.items():
        fold_metrics = []
        for train_idx, test_idx in splitter.split(frame, groups=groups):
            train = frame.iloc[train_idx]
            test = frame.iloc[test_idx]
            fitted = copy.deepcopy(model)
            fitted.fit(train[feature_columns], train[target])
            fold_metrics.append(_metrics(test[target], fitted.predict(test[feature_columns])))
        results[name] = _aggregate_fold_metrics(fold_metrics, split_count)
    return results


def _aggregate_fold_metrics(fold_metrics: list[ModelMetrics], n_folds: int) -> dict[str, Any]:
    values = {
        "mae": np.array([metric.mae for metric in fold_metrics], dtype=float),
        "rmse": np.array([metric.rmse for metric in fold_metrics], dtype=float),
        "r2": np.array([metric.r2 for metric in fold_metrics], dtype=float),
    }
    return {
        "n_folds": n_folds,
        "folds": [metric.__dict__ for metric in fold_metrics],
        "mae_mean": float(np.nanmean(values["mae"])),
        "mae_std": float(np.nanstd(values["mae"])),
        "rmse_mean": float(np.nanmean(values["rmse"])),
        "rmse_std": float(np.nanstd(values["rmse"])),
        "r2_mean": float(np.nanmean(values["r2"])),
        "r2_std": float(np.nanstd(values["r2"])),
    }


def _cv_metrics_payload(cv_results: dict[str, dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Serialize grouped CV metrics by model."""

    return {
        name: {
            "cv_mae_mean": payload["mae_mean"],
            "cv_mae_std": payload["mae_std"],
            "cv_rmse_mean": payload["rmse_mean"],
            "cv_rmse_std": payload["rmse_std"],
            "cv_r2_mean": payload["r2_mean"],
            "cv_r2_std": payload["r2_std"],
            "n_folds": float(payload["n_folds"]),
        }
        for name, payload in cv_results.items()
    }


def _cv_metrics_frame(
    target_results: dict[str, dict[str, dict[str, Any]]],
    group_column: str,
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Build a normalized table of grouped cross-validation results."""

    rows = []
    n_groups = int(_groups_for_split(frame, group_column).nunique())
    for target, results in target_results.items():
        for model, payload in results.items():
            rows.append(
                {
                    "validation_scope": "group_kfold",
                    "target": target,
                    "model": model,
                    "group_column": group_column,
                    "n_folds": int(payload["n_folds"]),
                    "n_rows": int(len(frame)),
                    "n_groups": n_groups,
                    "mae_mean": payload["mae_mean"],
                    "mae_std": payload["mae_std"],
                    "rmse_mean": payload["rmse_mean"],
                    "rmse_std": payload["rmse_std"],
                    "r2_mean": payload["r2_mean"],
                    "r2_std": payload["r2_std"],
                }
            )
    return pd.DataFrame(rows)


def _source_family_holdout_metrics(
    models: dict[str, Pipeline],
    frame: pd.DataFrame,
    feature_columns: list[str],
    targets: list[str],
    group_column: str,
    min_holdout_rows: int = 50,
    min_train_rows: int = 50,
) -> pd.DataFrame:
    """Train without each source family and evaluate transfer to that held-out family."""

    if "source_dataset" not in frame:
        return pd.DataFrame()

    families = frame["source_dataset"].map(_source_family)
    rows = []
    for family, holdout_idx in families.groupby(families).groups.items():
        holdout = frame.loc[holdout_idx]
        train = frame.loc[~frame.index.isin(holdout.index)]
        if len(holdout) < min_holdout_rows or len(train) < min_train_rows:
            continue
        train_groups = _groups_for_split(train, group_column)
        holdout_groups = _groups_for_split(holdout, group_column)
        for target in targets:
            for model_name, model in models.items():
                fitted = copy.deepcopy(model)
                fitted.fit(train[feature_columns], train[target])
                predictions = fitted.predict(holdout[feature_columns])
                errors = pd.Series(predictions - holdout[target].to_numpy(), index=holdout.index)
                metrics = _metrics(holdout[target], predictions)
                rows.append(
                    {
                        "validation_scope": "source_family_holdout",
                        "holdout_family": family,
                        "target": target,
                        "model": model_name,
                        "n_train": int(len(train)),
                        "n_holdout": int(len(holdout)),
                        "n_train_sources": int(train["source_dataset"].nunique()),
                        "n_train_groups": int(train_groups.nunique()),
                        "n_holdout_groups": int(holdout_groups.nunique()),
                        "mae": metrics.mae,
                        "rmse": metrics.rmse,
                        "r2": metrics.r2,
                        "mean_bias": float(errors.mean()),
                        "median_abs_error": float(errors.abs().median()),
                    }
                )
    return pd.DataFrame(rows)


def _source_family(source_dataset: object) -> str:
    text = "unknown" if pd.isna(source_dataset) else str(source_dataset)
    return text.split(":", 1)[0]


def generate_training_outputs(
    model_matrix: pd.DataFrame,
    test_predictions: pd.DataFrame,
    feature_importance: pd.DataFrame,
    metadata: dict[str, Any],
    cv_metrics: pd.DataFrame | None = None,
    source_holdout_metrics: pd.DataFrame | None = None,
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
    cv_metrics = pd.DataFrame() if cv_metrics is None else cv_metrics
    source_holdout_metrics = pd.DataFrame() if source_holdout_metrics is None else source_holdout_metrics
    if not source_holdout_metrics.empty:
        px.bar(
            source_holdout_metrics[source_holdout_metrics["target"].eq("rt_min")],
            x="holdout_family",
            y="mae",
            color="model",
            barmode="group",
            title="Source-family Holdout RT MAE",
        ).write_html(plots_dir / "source_holdout_performance.html")
    report.write_text(_report_markdown(model_matrix, metadata, source_perf, cv_metrics, source_holdout_metrics), encoding="utf-8")
    test_predictions.to_csv(report_dir / "test_predictions.csv", index=False)
    feature_importance.to_csv(report_dir / "feature_importance.csv", index=False)
    source_perf.to_csv(report_dir / "source_metrics.csv", index=False)
    cv_metrics.to_csv(report_dir / "cv_metrics.csv", index=False)
    source_holdout_metrics.to_csv(report_dir / "source_holdout_metrics.csv", index=False)
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
    true_values = pd.to_numeric(y_true, errors="coerce").to_numpy(dtype=float)
    finite_values = true_values[np.isfinite(true_values)]
    r2 = float("nan")
    if len(finite_values) > 1 and float(np.nanstd(finite_values)) > 1e-8:
        r2 = float(r2_score(y_true, y_pred))
    return ModelMetrics(
        mae=float(mean_absolute_error(y_true, y_pred)),
        rmse=float(mean_squared_error(y_true, y_pred) ** 0.5),
        r2=r2,
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
    cv_metrics = _markdown_table(pd.DataFrame(metadata.get("cv_metrics", [])).round(3))
    return f"""# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

## Grouped CV Metrics

{cv_metrics}

## Final Grouped Holdout RT Metrics

{rt_metrics}

## Final Grouped Holdout Quality Metrics

{quality_metrics}

Candidate models: {', '.join(metadata.get('candidate_models', []))}

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. Model selection uses GroupKFold by compound identity; source-family holdouts are diagnostic transfer checks.
"""


def _report_markdown(
    model_matrix: pd.DataFrame,
    metadata: dict[str, Any],
    source_perf: pd.DataFrame,
    cv_metrics: pd.DataFrame,
    source_holdout_metrics: pd.DataFrame,
) -> str:
    source_counts = model_matrix["source_dataset"].value_counts(dropna=False).to_dict()
    rt_metrics = _markdown_table(pd.DataFrame(metadata["rt_metrics"]).T.round(3).reset_index(names="model"))
    quality_metrics = _markdown_table(pd.DataFrame(metadata["quality_metrics"]).T.round(3).reset_index(names="model"))
    source_table = _markdown_table(source_perf.round(3))
    cv_table = _markdown_table(cv_metrics.round(3))
    holdout_table = _markdown_table(source_holdout_metrics.round(3))
    model_lines = "\n".join(f"- {name}" for name in metadata.get("candidate_models", []))
    return f"""# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: {len(model_matrix)}
- Compounds: {model_matrix['compound_name'].nunique()}
- Source distribution: {source_counts}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Validation Design

- Model selection: GroupKFold by `{metadata['validation_metadata']['group_column']}`.
- Final holdout: group-aware train/validation/test split with no compound identity overlap between splits.
- Source-family holdout: train without each large source family and test on that held-out family.

## Models Tested

{model_lines}

## Best Models

- RT model: `{metadata['best_rt_model']}`
- Peak quality surrogate: `{metadata['best_quality_model']}`

## Grouped CV Metrics

{cv_table}

## Final Grouped Holdout RT Metrics

{rt_metrics}

## Final Grouped Holdout Quality Metrics

{quality_metrics}

## Source-wise Performance

{source_table}

## Source-Family Holdout Metrics

{holdout_table}

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
- Source-family holdout is now reported, but it is still public-to-public transfer rather than internal lab validation.

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
