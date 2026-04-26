from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


INVERSE_FEATURE_COLUMNS = [
    "rt_fit_score",
    "predicted_quality_score",
    "runtime_penalty",
    "confidence_score",
    "ad_penalty",
    "constraint_violation_count",
    "target_rt_min",
    "candidate_runtime_min",
    "candidate_ph",
    "candidate_flow_ml_min",
    "candidate_temperature_c",
    "column_name",
    "mobile_phase_system",
]

NUMERIC_INVERSE_FEATURES = [
    "rt_fit_score",
    "predicted_quality_score",
    "runtime_penalty",
    "confidence_score",
    "ad_penalty",
    "constraint_violation_count",
    "target_rt_min",
    "candidate_runtime_min",
    "candidate_ph",
    "candidate_flow_ml_min",
    "candidate_temperature_c",
]

CATEGORICAL_INVERSE_FEATURES = ["column_name", "mobile_phase_system"]
DEFAULT_ARTIFACT = Path("data/processed/models/inverse_recommendation_bundle.joblib")
DEFAULT_REPORT_DIR = Path("reports")


@dataclass(frozen=True)
class InverseTrainingOutputs:
    artifact_path: Path
    metrics_csv: Path
    metrics_md: Path
    topk_csv: Path
    training_table_path: Path
    training_rows: int
    best_model: str


class InverseRecommendationBundle:
    """Persisted inverse ranker for optional recommendation reranking."""

    def __init__(
        self,
        model: Pipeline,
        model_name: str,
        feature_columns: list[str],
        label_source: str = "synthetic_proxy",
        metadata: dict[str, Any] | None = None,
    ):
        self.model = model
        self.model_name = model_name
        self.feature_columns = feature_columns
        self.label_source = label_source
        self.metadata = metadata or {}

    def score_candidate(
        self,
        compound: dict[str, Any],
        method: Any,
        prediction: dict[str, Any],
        target_rt_min: float,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = candidate_features_from_prediction(method, prediction, target_rt_min, constraints or {})
        frame = pd.DataFrame([row])
        score = _predict_score(self.model, frame[self.feature_columns])[0]
        return {
            "score": float(np.clip(score, 0.0, 1.0)),
            "label_source": self.label_source,
            "model_name": self.model_name,
        }


def build_inverse_training_table(
    model_matrix: pd.DataFrame,
    negatives_per_row: int = 1,
    target_window_min: float = 0.75,
    quality_threshold: float = 0.65,
) -> pd.DataFrame:
    """Build a transparent synthetic/proxy table for inverse method suitability."""

    usable = model_matrix.dropna(subset=["rt_min"]).copy()
    rows: list[dict[str, Any]] = []
    for _, source in usable.iterrows():
        base = _base_candidate_row(source, target_rt_min=float(source["rt_min"]))
        base.update(
            {
                "predicted_rt_min": float(source["rt_min"]),
                "rt_fit_score": 1.0,
                "predicted_quality_score": float(_num(source.get("quality_score"), 0.55)),
                "confidence_score": 0.85,
                "ad_penalty": 0.0,
                "constraint_violation_count": 0,
                "suitable": 1,
                "label_source": "synthetic_proxy",
            }
        )
        rows.append(_finalize_inverse_row(base, target_window_min, quality_threshold, force_label=1))
        for idx in range(negatives_per_row):
            shift = target_window_min * (2.5 + idx)
            negative = _base_candidate_row(source, target_rt_min=float(source["rt_min"]))
            negative.update(
                {
                    "predicted_rt_min": float(source["rt_min"]) + shift,
                    "rt_fit_score": max(0.0, 1.0 - shift / max(float(source["rt_min"]), 1.0)),
                    "predicted_quality_score": max(0.05, float(_num(source.get("quality_score"), 0.55)) - 0.25),
                    "confidence_score": 0.55,
                    "ad_penalty": 0.2,
                    "constraint_violation_count": 1 + idx,
                    "suitable": 0,
                    "label_source": "synthetic_proxy",
                }
            )
            rows.append(_finalize_inverse_row(negative, target_window_min, quality_threshold, force_label=0))
    table = pd.DataFrame(rows)
    for column in INVERSE_FEATURE_COLUMNS:
        if column not in table:
            table[column] = np.nan
    return table


def train_inverse_models(
    model_matrix: pd.DataFrame,
    artifact_path: str | Path = DEFAULT_ARTIFACT,
    report_dir: str | Path = DEFAULT_REPORT_DIR,
    quick: bool = False,
) -> InverseTrainingOutputs:
    """Train CPU-friendly inverse suitability classifiers and write reports."""

    max_rows = 5000 if quick else None
    matrix = model_matrix.head(max_rows).copy() if max_rows else model_matrix.copy()
    table = build_inverse_training_table(matrix, negatives_per_row=1 if quick else 2)
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)

    train_table_path = reports / "inverse_training_table_sample.csv"
    table.head(1000).to_csv(train_table_path, index=False)

    x = table[INVERSE_FEATURE_COLUMNS]
    y = table["suitable"].astype(int)
    groups = table.get("inchikey", pd.Series(range(len(table)))).fillna(table["compound_name"]).astype(str)
    train_idx, test_idx = _train_test_indices(table, groups)
    models = _candidate_models(quick=quick)
    metrics: list[dict[str, Any]] = []
    topk_rows: list[dict[str, Any]] = []
    fitted: dict[str, Pipeline] = {}
    for name, model in models.items():
        model.fit(x.iloc[train_idx], y.iloc[train_idx])
        fitted[name] = model
        scores = _predict_score(model, x.iloc[test_idx])
        preds = (scores >= 0.5).astype(int)
        metrics.append(_classification_metrics(name, y.iloc[test_idx], preds, scores))
        topk_rows.append(_topk_metrics(name, table.iloc[test_idx].assign(_score=scores)))

    metrics_frame = pd.DataFrame(metrics).sort_values(["pr_auc", "roc_auc"], ascending=False)
    best_name = str(metrics_frame.iloc[0]["model"])
    bundle = InverseRecommendationBundle(
        fitted[best_name],
        model_name=best_name,
        feature_columns=INVERSE_FEATURE_COLUMNS,
        metadata={"label_source": "synthetic_proxy", "quick": quick, "training_rows": int(len(table))},
    )
    joblib.dump(bundle, artifact)

    metrics_csv = reports / "inverse_model_metrics.csv"
    metrics_md = reports / "inverse_model_metrics.md"
    topk_csv = reports / "inverse_topk_evaluation.csv"
    metrics_frame.to_csv(metrics_csv, index=False)
    pd.DataFrame(topk_rows).to_csv(topk_csv, index=False)
    metrics_md.write_text(_metrics_markdown(metrics_frame, pd.DataFrame(topk_rows), best_name, len(table)), encoding="utf-8")
    return InverseTrainingOutputs(
        artifact_path=artifact,
        metrics_csv=metrics_csv,
        metrics_md=metrics_md,
        topk_csv=topk_csv,
        training_table_path=train_table_path,
        training_rows=int(len(table)),
        best_model=best_name,
    )


def candidate_features_from_prediction(
    method: Any,
    prediction: dict[str, Any],
    target_rt_min: float,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    predicted_rt = float(prediction.get("predicted_rt_min", target_rt_min))
    runtime = float(getattr(method, "runtime_min", 0.0) or 0.0)
    rt_fit = 1.0 - min(abs(predicted_rt - target_rt_min) / max(target_rt_min, 0.1), 1.0)
    return {
        "rt_fit_score": rt_fit,
        "predicted_quality_score": float(prediction.get("quality_score", 0.5)),
        "runtime_penalty": min(runtime / max(float(constraints.get("max_runtime_min", 12.0) or 12.0), 0.1), 1.0),
        "confidence_score": float(prediction.get("confidence", 0.5)),
        "ad_penalty": 1.0 if prediction.get("out_of_domain") else 0.0,
        "constraint_violation_count": 0,
        "target_rt_min": float(target_rt_min),
        "candidate_runtime_min": runtime,
        "candidate_ph": float(getattr(method, "ph", 7.0) or 7.0),
        "candidate_flow_ml_min": float(getattr(method, "flow_rate_ml_min", 0.3) or 0.3),
        "candidate_temperature_c": float(getattr(method, "temperature_c", 35.0) or 35.0),
        "column_name": getattr(method, "column", "unknown") or "unknown",
        "mobile_phase_system": _mobile_phase_system(
            getattr(method, "mobile_phase_a", ""),
            getattr(method, "mobile_phase_b", ""),
        ),
    }


def _candidate_models(quick: bool) -> dict[str, Pipeline]:
    n_estimators = 40 if quick else 120
    models: dict[str, Any] = {
        "logistic_regression": LogisticRegression(max_iter=500, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=n_estimators, random_state=17, class_weight="balanced"),
        "extra_trees": ExtraTreesClassifier(n_estimators=n_estimators, random_state=17, class_weight="balanced"),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=40 if quick else 120, random_state=17),
    }
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=30 if quick else 100,
            max_depth=3,
            learning_rate=0.08,
            eval_metric="logloss",
            random_state=17,
        )
    except Exception:
        pass
    try:
        from catboost import CatBoostClassifier

        models["catboost"] = CatBoostClassifier(
            iterations=30 if quick else 100,
            depth=4,
            learning_rate=0.08,
            verbose=False,
            random_seed=17,
        )
    except Exception:
        pass
    return {name: _pipeline(model) for name, model in models.items()}


def _pipeline(model: Any) -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                NUMERIC_INVERSE_FEATURES,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                CATEGORICAL_INVERSE_FEATURES,
            ),
        ]
    )
    return Pipeline([("preprocess", preprocessor), ("model", model)])


def _classification_metrics(model: str, y_true: pd.Series, y_pred: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    has_two_classes = y_true.nunique() > 1
    return {
        "model": model,
        "roc_auc": float(roc_auc_score(y_true, scores)) if has_two_classes else np.nan,
        "pr_auc": float(average_precision_score(y_true, scores)) if has_two_classes else np.nan,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)) if has_two_classes else np.nan,
        "brier_score": float(brier_score_loss(y_true, np.clip(scores, 0, 1))),
        "n_test": int(len(y_true)),
        "label_source": "synthetic_proxy",
    }


def _topk_metrics(model: str, scored: pd.DataFrame) -> dict[str, Any]:
    group_cols = ["compound_name", "target_rt_min"]
    grouped = scored.sort_values("_score", ascending=False).groupby(group_cols, dropna=False)
    rows = []
    for _, group in grouped:
        suitable_positions = np.flatnonzero(group["suitable"].to_numpy() == 1)
        first_rank = int(suitable_positions[0] + 1) if len(suitable_positions) else 999
        rows.append(first_rank)
    ranks = np.array(rows) if rows else np.array([999])
    return {
        "model": model,
        "top_1_success": float(np.mean(ranks <= 1)),
        "top_3_success": float(np.mean(ranks <= 3)),
        "top_5_success": float(np.mean(ranks <= 5)),
        "mean_first_suitable_rank": float(np.mean(ranks)),
        "label_source": "synthetic_proxy",
    }


def _predict_score(model: Pipeline, frame: pd.DataFrame) -> np.ndarray:
    estimator = model.named_steps["model"] if isinstance(model, Pipeline) else model
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(frame)
        return proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
    if hasattr(model, "decision_function"):
        decision = model.decision_function(frame)
        return 1.0 / (1.0 + np.exp(-decision))
    return model.predict(frame)


def _train_test_indices(table: pd.DataFrame, groups: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    if len(table) < 20 or groups.nunique() < 3:
        idx = np.arange(len(table))
        return idx, idx
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=17)
    return next(splitter.split(table, table["suitable"], groups))


def _base_candidate_row(source: pd.Series, target_rt_min: float) -> dict[str, Any]:
    return {
        "compound_name": source.get("compound_name"),
        "inchikey": source.get("inchikey"),
        "source_dataset": source.get("source_dataset"),
        "target_rt_min": target_rt_min,
        "candidate_runtime_min": float(_num(source.get("total_runtime_min"), max(target_rt_min + 1.0, 5.0))),
        "candidate_ph": float(_num(source.get("ph"), 7.0)),
        "candidate_flow_ml_min": float(_num(source.get("flow_ml_min"), 0.3)),
        "candidate_temperature_c": float(_num(source.get("temperature_c"), 35.0)),
        "column_name": source.get("column_name") or "unknown",
        "mobile_phase_system": source.get("mobile_phase_system") or _mobile_phase_system(source.get("mobile_phase_a"), source.get("mobile_phase_b")),
    }


def _finalize_inverse_row(
    row: dict[str, Any],
    target_window_min: float,
    quality_threshold: float,
    force_label: int | None = None,
) -> dict[str, Any]:
    row["runtime_penalty"] = min(float(row["candidate_runtime_min"]) / 12.0, 1.0)
    if force_label is None:
        row["suitable"] = int(
            abs(float(row["predicted_rt_min"]) - float(row["target_rt_min"])) <= target_window_min
            and float(row["predicted_quality_score"]) >= quality_threshold
            and int(row["constraint_violation_count"]) == 0
        )
    else:
        row["suitable"] = int(force_label)
    return row


def _mobile_phase_system(a_phase: object, b_phase: object) -> str:
    text = f"{a_phase or ''} {b_phase or ''}".lower()
    organic = "acn" if "acetonitrile" in text else "meoh" if "methanol" in text else "other"
    modifier = "formic_acid" if "formic" in text else "ammonium" if "ammonium" in text else "unbuffered"
    return f"{organic}_{modifier}"


def _num(value: object, default: float) -> float:
    parsed = pd.to_numeric(value, errors="coerce")
    return float(default) if pd.isna(parsed) else float(parsed)


def _metrics_markdown(metrics: pd.DataFrame, topk: pd.DataFrame, best_model: str, training_rows: int) -> str:
    return "\n".join(
        [
            "# Inverse Recommendation Model Metrics",
            "",
            f"- Training rows: {training_rows}",
            "- Label source: `synthetic_proxy`",
            f"- Best model: `{best_model}`",
            "",
            "## Classification Metrics",
            "",
            _markdown_table(metrics.round(3)),
            "",
            "## Top-k Suitability Proxy",
            "",
            _markdown_table(topk.round(3)),
            "",
            "## Limitations",
            "",
            "- Labels are generated from forward-model style suitability rules, not accepted laboratory outcomes.",
            "- Treat this as an inverse ranking baseline until internal assay development results are connected.",
        ]
    ) + "\n"


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)
