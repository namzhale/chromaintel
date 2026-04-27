from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.models.training import _annotate_importance
from app.services.feature_engineering import feature_groups


RUNTIME_FEATURES = ("gradient_duration_min", "total_runtime_min")
METHOD_ID_COLUMNS = [
    "source_dataset",
    "column_name",
    "mobile_phase_system",
    "initial_organic_pct",
    "final_organic_pct",
    "flow_ml_min",
    "temperature_c",
]


@dataclass(frozen=True)
class RuntimeAblationConfig:
    """Configuration for a small runtime proxy ablation study."""

    sample_rows: int = 20000
    random_state: int = 42
    n_estimators: int = 120
    test_size: float = 0.2


def build_runtime_ablation_sets(base_features: list[str]) -> dict[str, list[str]]:
    """Return feature lists that isolate gradient duration and total runtime effects."""

    return {
        "with_both": list(base_features),
        "without_total_runtime": [feature for feature in base_features if feature != "total_runtime_min"],
        "without_gradient_duration": [feature for feature in base_features if feature != "gradient_duration_min"],
        "without_both": [feature for feature in base_features if feature not in set(RUNTIME_FEATURES)],
    }


def run_runtime_ablation_study(
    model_matrix: pd.DataFrame,
    config: RuntimeAblationConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Train identical small ExtraTrees models with/without duration proxy features."""

    cfg = config or RuntimeAblationConfig()
    usable = model_matrix.dropna(subset=["rt_min"]).copy().replace({pd.NA: np.nan})
    if len(usable) < 20:
        raise ValueError("At least 20 rows with rt_min are required for runtime ablation")
    sampled = _sample_for_ablation(usable, cfg.sample_rows, cfg.random_state)

    groups = feature_groups(sampled)
    base_features = groups.combined
    ablation_sets = build_runtime_ablation_sets(base_features)
    group_labels = _group_labels(sampled)
    splitter = GroupShuffleSplit(n_splits=1, test_size=cfg.test_size, random_state=cfg.random_state)
    train_idx, test_idx = next(splitter.split(sampled, groups=group_labels))
    train = sampled.iloc[train_idx].copy()
    test = sampled.iloc[test_idx].copy()

    rows: list[dict[str, Any]] = []
    for ablation_name, features in ablation_sets.items():
        categorical = [feature for feature in groups.lc_categorical + ["ion_mode"] if feature in features]
        numeric = [feature for feature in features if feature not in categorical]
        model = _model(categorical, numeric, cfg.n_estimators, cfg.random_state)
        model.fit(train[features], train["rt_min"])
        pred = model.predict(test[features])
        rows.append(
            {
                "ablation": ablation_name,
                "n_train": int(len(train)),
                "n_test": int(len(test)),
                "n_features": int(len(features)),
                "uses_gradient_duration_min": "gradient_duration_min" in features,
                "uses_total_runtime_min": "total_runtime_min" in features,
                "mae": float(mean_absolute_error(test["rt_min"], pred)),
                "rmse": float(mean_squared_error(test["rt_min"], pred) ** 0.5),
                "r2": _safe_r2(test["rt_min"], pred),
                "spearman": _safe_spearman(test["rt_min"], pred),
                "normalized_mae_runtime_pct": _normalized_mae_runtime_pct(test, pred),
            }
        )

    metrics = pd.DataFrame(rows).sort_values("mae").reset_index(drop=True)
    diagnostics = runtime_consequence_diagnostics(sampled)
    diagnostics.update(
        {
            "sample_rows": int(len(sampled)),
            "split_group_column": _group_column(sampled),
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "train_test_group_overlap": int(len(set(_group_labels(train)) & set(_group_labels(test)))),
        }
    )
    return metrics, diagnostics


def run_no_runtime_feature_importance(
    model_matrix: pd.DataFrame,
    config: RuntimeAblationConfig | None = None,
    n_repeats: int = 3,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Train the no-runtime-proxy RT model and return permutation feature importance."""

    cfg = config or RuntimeAblationConfig()
    usable = model_matrix.dropna(subset=["rt_min"]).copy().replace({pd.NA: np.nan})
    if len(usable) < 20:
        raise ValueError("At least 20 rows with rt_min are required for feature importance")
    sampled = _sample_for_ablation(usable, cfg.sample_rows, cfg.random_state)
    groups = feature_groups(sampled)
    features = build_runtime_ablation_sets(groups.combined)["without_both"]
    categorical = [feature for feature in groups.lc_categorical + ["ion_mode"] if feature in features]
    numeric = [feature for feature in features if feature not in categorical]

    group_labels = _group_labels(sampled)
    splitter = GroupShuffleSplit(n_splits=1, test_size=cfg.test_size, random_state=cfg.random_state)
    train_idx, test_idx = next(splitter.split(sampled, groups=group_labels))
    train = sampled.iloc[train_idx].copy()
    test = sampled.iloc[test_idx].copy()
    model = _model(categorical, numeric, cfg.n_estimators, cfg.random_state)
    model.fit(train[features], train["rt_min"])
    pred = model.predict(test[features])
    result = permutation_importance(
        model,
        test[features],
        test["rt_min"],
        n_repeats=n_repeats,
        random_state=cfg.random_state,
        scoring="neg_mean_absolute_error",
    )
    importance = pd.DataFrame(
        {
            "feature": features,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    ).sort_values("importance_mean", ascending=False).reset_index(drop=True)
    metrics = {
        "ablation": "without_both",
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "n_features": int(len(features)),
        "uses_gradient_duration_min": False,
        "uses_total_runtime_min": False,
        "mae": float(mean_absolute_error(test["rt_min"], pred)),
        "rmse": float(mean_squared_error(test["rt_min"], pred) ** 0.5),
        "r2": _safe_r2(test["rt_min"], pred),
        "spearman": _safe_spearman(test["rt_min"], pred),
        "normalized_mae_runtime_pct": _normalized_mae_runtime_pct(test, pred),
        "sample_rows": int(len(sampled)),
        "split_group_column": _group_column(sampled),
        "train_test_group_overlap": int(len(set(_group_labels(train)) & set(_group_labels(test)))),
    }
    return _annotate_importance(importance), metrics


def runtime_consequence_diagnostics(frame: pd.DataFrame) -> dict[str, Any]:
    """Measure whether runtime looks like an independent method setting or a target-derived margin."""

    usable = frame.dropna(subset=["rt_min"]).copy()
    margin = _numeric(usable, "total_runtime_min") - _numeric(usable, "rt_min")
    rt = _numeric(usable, "rt_min")
    total = _numeric(usable, "total_runtime_min")
    gradient = _numeric(usable, "gradient_duration_min")
    fraction = rt / total.replace(0, np.nan)
    method_group_stats = _method_group_runtime_stats(usable)
    target_like_margin = margin.between(0, 2.0, inclusive="both")

    return {
        "rt_total_runtime_pearson": _safe_corr(rt, total, method="pearson"),
        "rt_total_runtime_spearman": _safe_corr(rt, total, method="spearman"),
        "rt_gradient_duration_pearson": _safe_corr(rt, gradient, method="pearson"),
        "rt_gradient_duration_spearman": _safe_corr(rt, gradient, method="spearman"),
        "post_peak_margin_median_min": _safe_quantile(margin, 0.5),
        "post_peak_margin_q10_min": _safe_quantile(margin, 0.1),
        "post_peak_margin_q90_min": _safe_quantile(margin, 0.9),
        "rt_runtime_fraction_median": _safe_quantile(fraction, 0.5),
        "rt_runtime_fraction_q90": _safe_quantile(fraction, 0.9),
        "target_like_runtime_margin_fraction": float(target_like_margin.mean()) if len(target_like_margin) else 0.0,
        **method_group_stats,
    }


def write_runtime_ablation_outputs(
    metrics: pd.DataFrame,
    diagnostics: dict[str, Any],
    report_dir: str | Path = "reports",
) -> dict[str, str]:
    """Write CSV, JSON, and markdown outputs for the runtime leakage study."""

    out = Path(report_dir)
    out.mkdir(parents=True, exist_ok=True)
    metrics_path = out / "runtime_ablation_metrics.csv"
    diagnostics_path = out / "runtime_consequence_diagnostics.json"
    report_path = out / "runtime_leakage_ablation_report.md"
    metrics.to_csv(metrics_path, index=False)
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(_runtime_ablation_markdown(metrics, diagnostics), encoding="utf-8")
    return {
        "metrics": str(metrics_path),
        "diagnostics": str(diagnostics_path),
        "report": str(report_path),
    }


def write_no_runtime_feature_importance_outputs(
    importance: pd.DataFrame,
    metrics: dict[str, Any],
    report_dir: str | Path = "reports",
) -> dict[str, str]:
    """Write no-runtime feature importance outputs."""

    out = Path(report_dir)
    out.mkdir(parents=True, exist_ok=True)
    importance_path = out / "feature_importance_no_runtime.csv"
    metrics_path = out / "feature_importance_no_runtime_metrics.json"
    report_path = out / "feature_importance_no_runtime.md"
    importance.to_csv(importance_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(_no_runtime_importance_markdown(importance, metrics), encoding="utf-8")
    return {
        "importance": str(importance_path),
        "metrics": str(metrics_path),
        "report": str(report_path),
    }


def _no_runtime_importance_markdown(importance: pd.DataFrame, metrics: dict[str, Any]) -> str:
    top = importance.head(25).round(4)
    table = _markdown_table(top)
    return f"""# Feature Importance Without Runtime Proxy Features

This report recalculates RT permutation feature importance after excluding `gradient_duration_min` and `total_runtime_min`. The model still keeps LC composition, organic percentages, gradient slope, column/mobile-phase categories, MS mode, and molecular descriptors.

## Model Metrics

- Ablation mode: `{metrics.get('ablation')}`
- Sample rows: {metrics.get('sample_rows')}
- Train/test rows: {metrics.get('n_train')} / {metrics.get('n_test')}
- Split group column: `{metrics.get('split_group_column')}`
- Train/test group overlap: {metrics.get('train_test_group_overlap')}
- Features used: {metrics.get('n_features')}
- MAE: {_fmt(metrics.get('mae'))} min
- RMSE: {_fmt(metrics.get('rmse'))} min
- R2: {_fmt(metrics.get('r2'))}
- Spearman: {_fmt(metrics.get('spearman'))}

## Top Features

{table}

## Interpretation

After removing direct duration/runtime features, the model should be interpreted through remaining controllable LC conditions and chemistry: organic start/end percentage, gradient slope, column/mobile phase categories, hydrophobicity/logD, surface area, ionization proxies, flow, temperature, and MS polarity. This is the safer feature-importance view for transfer claims and inverse recommendation.
"""


def _runtime_ablation_markdown(metrics: pd.DataFrame, diagnostics: dict[str, Any]) -> str:
    table = _markdown_table(metrics.round(4))
    conclusion = _runtime_consequence_interpretation(diagnostics)
    return f"""# Проверка runtime/gradient duration как возможных proxy-признаков RT

Мини-исследование проверяет, ведут ли себя `gradient_duration_min` и `total_runtime_min` как честные параметры LC-метода или как proxy-признаки, частично следующие из ожидаемого/измеренного RT. Для всех вариантов используется одна и та же подвыборка, один и тот же grouped split по соединениям и одна ExtraTrees-модель.

## Сравнение ablation-режимов

{table}

## Диагностика “runtime как следствие RT”

- Строк в подвыборке: {diagnostics.get('sample_rows')}
- Split group column: `{diagnostics.get('split_group_column')}`
- Пересечение compound-групп train/test: {diagnostics.get('train_test_group_overlap')}
- Spearman(`rt_min`, `total_runtime_min`): {_fmt(diagnostics.get('rt_total_runtime_spearman'))}
- Spearman(`rt_min`, `gradient_duration_min`): {_fmt(diagnostics.get('rt_gradient_duration_spearman'))}
- Медианный запас после пика (`total_runtime_min - rt_min`): {_fmt(diagnostics.get('post_peak_margin_median_min'))} мин
- Q10/Q90 запаса после пика: {_fmt(diagnostics.get('post_peak_margin_q10_min'))} / {_fmt(diagnostics.get('post_peak_margin_q90_min'))} мин
- Медиана `rt_min / total_runtime_min`: {_fmt(diagnostics.get('rt_runtime_fraction_median'))}
- Доля строк, где метод заканчивается через 0-2 мин после RT: {_fmt(diagnostics.get('target_like_runtime_margin_fraction'))}
- Проверено method-групп: {diagnostics.get('method_group_count')}
- Доля method-групп, где runtime меняется внутри одного method key: {_fmt(diagnostics.get('within_method_variable_runtime_group_fraction'))}

## Интерпретация

{conclusion}

## Как понять, является ли runtime следствием

1. Если `total_runtime_min` меняется от аналита к аналиту внутри одной method-family и монотонно следует за `rt_min`, это похоже на operational choice, выбранный под ожидаемый пик.
2. Если `total_runtime_min - rt_min` мал и стабилен, runtime может кодировать правило “остановить метод вскоре после целевого пика”.
3. Если `total_runtime_min` одинаков для многих соединений в одном методе, это скорее независимый параметр метода, а не следствие конкретного RT.
4. Если удаление `total_runtime_min` резко ухудшает метрики, а удаление химических/method composition признаков нет, модель, вероятно, использует runtime как shortcut.
5. Самая сильная проверка для внутренних данных: сравнить дизайн метода до запуска с наблюдаемым RT после запуска. Параметр, выбранный после знания RT, нельзя использовать как causal predictor.

## Рекомендация

`full_method` можно использовать как практический operational predictor. Для научных выводов, transfer-валидации и inverse recommendation нужно отдельно показывать `no_runtime_proxy` benchmark, а runtime трактовать в основном как constraint/penalty, а не как свободный predictive feature.
"""


def _runtime_consequence_interpretation(diagnostics: dict[str, Any]) -> str:
    total_corr = float(diagnostics.get("rt_total_runtime_spearman") or 0.0)
    margin_fraction = float(diagnostics.get("target_like_runtime_margin_fraction") or 0.0)
    variable_fraction = float(diagnostics.get("within_method_variable_runtime_group_fraction") or 0.0)
    signals = []
    if total_corr >= 0.7:
        signals.append("высокая ранговая корреляция RT-runtime")
    if margin_fraction >= 0.5:
        signals.append("многие методы заканчиваются вскоре после наблюдаемого RT")
    if variable_fraction >= 0.2:
        signals.append("runtime заметно меняется внутри похожих method-групп")
    if not signals:
        return "На этой публичной подвыборке нет сильного простого сигнала, что `total_runtime_min` является следствием RT: корреляция умеренная, медианный запас после пика большой, а внутри одинаковых method-групп runtime почти не меняется. Но ablation всё равно нужно регулярно показывать, потому что во внутренних targeted bioanalytical assays runtime действительно может задаваться после знания ожидаемого пика."
    return (
        "Подвыборка показывает возможные признаки proxy-leakage: "
        + ", ".join(signals)
        + ". Для model-selection claims лучше считать `total_runtime_min` подозрительным и опираться на no-runtime ablations при оценке transfer/recommendation."
    )


def _sample_for_ablation(frame: pd.DataFrame, sample_rows: int, random_state: int) -> pd.DataFrame:
    if len(frame) <= sample_rows:
        return frame.reset_index(drop=True)
    if "source_dataset" not in frame:
        return frame.sample(sample_rows, random_state=random_state).reset_index(drop=True)
    source_count = max(int(frame["source_dataset"].nunique(dropna=False)), 1)
    per_source = max(sample_rows // source_count, 1)
    sampled = frame.groupby("source_dataset", group_keys=False, dropna=False).apply(
        lambda group: group.sample(min(len(group), per_source), random_state=random_state)
    )
    if len(sampled) < sample_rows:
        remainder = frame.drop(index=sampled.index, errors="ignore")
        extra = remainder.sample(min(len(remainder), sample_rows - len(sampled)), random_state=random_state)
        sampled = pd.concat([sampled, extra], axis=0)
    if len(sampled) > sample_rows:
        sampled = sampled.sample(sample_rows, random_state=random_state)
    return sampled.reset_index(drop=True)


def _model(categorical: list[str], numeric: list[str], n_estimators: int, random_state: int) -> Pipeline:
    preprocessor = ColumnTransformer(
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
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("preprocess", preprocessor),
            (
                "model",
                ExtraTreesRegressor(
                    n_estimators=n_estimators,
                    random_state=random_state,
                    n_jobs=-1,
                    min_samples_leaf=2,
                ),
            ),
        ]
    )


def _group_column(frame: pd.DataFrame) -> str:
    if "inchikey" in frame and frame["inchikey"].notna().sum() >= 2:
        return "inchikey"
    if "canonical_smiles" in frame and frame["canonical_smiles"].notna().sum() >= 2:
        return "canonical_smiles"
    return "compound_name"


def _group_labels(frame: pd.DataFrame) -> pd.Series:
    column = _group_column(frame)
    values = frame[column].astype("object") if column in frame else pd.Series(pd.NA, index=frame.index)
    return values.where(values.notna() & values.astype(str).str.strip().ne(""), "missing:" + frame.index.astype(str))


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def _safe_r2(y_true: pd.Series, y_pred: np.ndarray) -> float:
    true = pd.to_numeric(y_true, errors="coerce")
    if true.notna().sum() < 2 or float(true.std()) < 1e-8:
        return float("nan")
    return float(r2_score(y_true, y_pred))


def _safe_spearman(y_true: pd.Series, y_pred: np.ndarray) -> float:
    true = pd.to_numeric(y_true, errors="coerce")
    pred = pd.Series(y_pred, index=true.index)
    if true.notna().sum() < 2 or float(true.std()) < 1e-8 or float(pred.std()) < 1e-8:
        return float("nan")
    return float(true.corr(pred, method="spearman"))


def _normalized_mae_runtime_pct(test: pd.DataFrame, pred: np.ndarray) -> float:
    runtime = _numeric(test, "total_runtime_min").replace(0, np.nan)
    mean_runtime = float(runtime.mean()) if runtime.notna().any() else float("nan")
    if not np.isfinite(mean_runtime) or mean_runtime <= 0:
        return float("nan")
    return float(mean_absolute_error(test["rt_min"], pred) / mean_runtime * 100.0)


def _safe_corr(left: pd.Series, right: pd.Series, method: str) -> float:
    frame = pd.DataFrame({"left": left, "right": right}).dropna()
    if len(frame) < 2 or frame["left"].std() < 1e-8 or frame["right"].std() < 1e-8:
        return float("nan")
    return float(frame["left"].corr(frame["right"], method=method))


def _safe_quantile(values: pd.Series, q: float) -> float:
    finite = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if finite.empty:
        return float("nan")
    return float(finite.quantile(q))


def _method_group_runtime_stats(frame: pd.DataFrame) -> dict[str, Any]:
    keys = [column for column in METHOD_ID_COLUMNS if column in frame]
    if not keys or "total_runtime_min" not in frame:
        return {
            "method_group_count": 0,
            "within_method_variable_runtime_group_fraction": 0.0,
            "within_method_rt_runtime_spearman_median": float("nan"),
        }
    rows = []
    for _, group in frame.groupby(keys, dropna=False):
        if len(group) < 3:
            continue
        runtime_unique = int(_numeric(group, "total_runtime_min").nunique(dropna=True))
        corr = _safe_corr(_numeric(group, "rt_min"), _numeric(group, "total_runtime_min"), method="spearman")
        rows.append({"variable_runtime": runtime_unique > 1, "corr": corr})
    if not rows:
        return {
            "method_group_count": 0,
            "within_method_variable_runtime_group_fraction": 0.0,
            "within_method_rt_runtime_spearman_median": float("nan"),
        }
    stats = pd.DataFrame(rows)
    return {
        "method_group_count": int(len(stats)),
        "within_method_variable_runtime_group_fraction": float(stats["variable_runtime"].mean()),
        "within_method_rt_runtime_spearman_median": _safe_quantile(stats["corr"], 0.5),
    }


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    text = frame.fillna("").astype(str).apply(lambda col: col.str.replace("|", "\\|", regex=False))
    lines = [
        "| " + " | ".join(text.columns) + " |",
        "| " + " | ".join(["---"] * len(text.columns)) + " |",
    ]
    for _, row in text.iterrows():
        lines.append("| " + " | ".join(row[col] for col in text.columns) + " |")
    return "\n".join(lines)


def _fmt(value: object) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not np.isfinite(parsed):
        return "n/a"
    return f"{parsed:.3f}"
