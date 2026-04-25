from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "chromaintel_dashboard_report.pdf"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODEL_BUNDLE = PROCESSED_DIR / "models" / "trained_forward_bundle.joblib"

BLUE = "#276FBF"
TEAL = "#2A9D8F"
RED = "#B94A48"
INK = "#17202A"
MUTED = "#5D6D7E"
PANEL = "#F3F7FA"
GRID = "#D6DEE6"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    data = _load_dashboard_data()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _build_pdf(args.output, data)
    print(f"Wrote dashboard PDF: {args.output.resolve()}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the ChromaIntel model/data dashboard PDF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _load_dashboard_data() -> dict[str, object]:
    metadata = joblib.load(MODEL_BUNDLE)["metadata"] if MODEL_BUNDLE.exists() else {}
    return {
        "master": _read_csv(PROCESSED_DIR / "master_dataset.csv"),
        "matrix": _read_csv(PROCESSED_DIR / "model_matrix.csv"),
        "source_metrics": _read_csv(REPORTS_DIR / "source_metrics.csv"),
        "source_holdout": _read_csv(REPORTS_DIR / "source_holdout_metrics.csv"),
        "cv_metrics": _read_csv(REPORTS_DIR / "cv_metrics.csv"),
        "importance": _read_csv(REPORTS_DIR / "feature_importance.csv"),
        "predictions": _read_csv(REPORTS_DIR / "test_predictions.csv"),
        "metadata": metadata,
    }


def _build_pdf(path: Path, data: dict[str, object]) -> None:
    _setup_matplotlib()
    with PdfPages(path) as pdf:
        for builder in [
            _page_summary,
            _page_models,
            _page_full_model_matrix,
            _page_validation,
            _page_parameters,
            _page_roadmap,
        ]:
            fig = _new_page()
            builder(fig, data)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def _setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 12,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.facecolor": "white",
        }
    )


def _new_page() -> plt.Figure:
    return plt.figure(figsize=(11.69, 8.27), dpi=150)


def _page_summary(fig: plt.Figure, data: dict[str, object]) -> None:
    master: pd.DataFrame = data["master"]  # type: ignore[assignment]
    matrix: pd.DataFrame = data["matrix"]  # type: ignore[assignment]

    fig.text(0.055, 0.94, "ChromaIntel LC-MS/MS: MVP-дашборд", fontsize=22, fontweight="bold", color=INK)
    fig.text(
        0.055,
        0.905,
        "Размер датасета, качество моделей, пропуски, переносимость между источниками и roadmap",
        fontsize=10,
        color=MUTED,
    )

    source_family_counts = (
        master["source_dataset"].astype(str).str.split(":").str[0].value_counts()
        if "source_dataset" in master
        else pd.Series(dtype=int)
    )
    cards = [
        ("Строк master", len(master)),
        ("Строк model matrix", len(matrix)),
        ("Соединений", master["compound_name"].nunique() if "compound_name" in master else 0),
        ("Семейств источников", len(source_family_counts)),
    ]
    for idx, (label, value) in enumerate(cards):
        _card(fig, 0.055 + idx * 0.225, 0.79, 0.19, 0.09, f"{value:,}".replace(",", " "), label)

    ax_sources = fig.add_axes([0.06, 0.35, 0.43, 0.34])
    source_counts = master["source_dataset"].value_counts().head(18) if "source_dataset" in master else pd.Series(dtype=int)
    _barh(ax_sources, source_counts.sort_values(), "Топ источников по числу строк", "строк", BLUE)

    ax_missing = fig.add_axes([0.57, 0.35, 0.36, 0.34])
    missing = master.isna().mean().sort_values(ascending=False).head(8)
    _barh(ax_missing, missing.sort_values(), "Наибольшая доля пропусков", "доля", TEAL, value_fmt="{:.2f}")

    ax_note = fig.add_axes([0.055, 0.08, 0.88, 0.19])
    ax_note.axis("off")
    _panel(ax_note)
    notes = [
        "Цели предсказания: retention time `rt_min` и временный surrogate `quality_score`.",
        "Основной RT-датасет теперь публичный и смешанный: RepoRT + MCMRT + mock/internal шаблоны.",
        "MCMRT добавляет 30 reversed-phase LC-методов и позволяет проверять перенос на новый источник.",
        "Quality-модель пока диагностическая: публичные RT-источники почти не содержат реальных peak-quality метрик.",
    ]
    ax_note.text(0.025, 0.78, "Ключевые выводы", fontsize=13, fontweight="bold", color=INK, transform=ax_note.transAxes)
    ax_note.text(0.025, 0.48, "\n".join(f"• {note}" for note in notes), fontsize=9.5, color=INK, va="top", transform=ax_note.transAxes)


def _page_models(fig: plt.Figure, data: dict[str, object]) -> None:
    metadata: dict[str, Any] = data["metadata"]  # type: ignore[assignment]
    rt_metrics = pd.DataFrame(metadata.get("rt_metrics", {})).T.reset_index(names="model")
    quality_metrics = pd.DataFrame(metadata.get("quality_metrics", {})).T.reset_index(names="model")
    cv_metrics: pd.DataFrame = data["cv_metrics"]  # type: ignore[assignment]

    fig.text(0.055, 0.94, "Сравнение моделей", fontsize=22, fontweight="bold", color=INK)
    fig.text(0.055, 0.905, "Выбор модели теперь основан на GroupKFold по InChIKey, без утечки соединений между fold'ами.", fontsize=10, color=MUTED)

    rt_cv = cv_metrics[cv_metrics["target"].eq("rt_min")].sort_values("mae_mean") if not cv_metrics.empty else pd.DataFrame()
    if not rt_cv.empty:
        ax_cv = fig.add_axes([0.06, 0.56, 0.39, 0.27])
        _barh(
            ax_cv,
            rt_cv.set_index("model")["mae_mean"].sort_values(ascending=False),
            "RT GroupKFold MAE: ниже лучше",
            "мин",
            BLUE,
            highlight_min=True,
        )
        ax_rmse = fig.add_axes([0.55, 0.56, 0.39, 0.27])
        _barh(
            ax_rmse,
            rt_cv.set_index("model")["rmse_mean"].sort_values(ascending=False),
            "RT GroupKFold RMSE: ниже лучше",
            "мин",
            TEAL,
            highlight_min=True,
        )

    ax_table = fig.add_axes([0.055, 0.29, 0.89, 0.20])
    ax_table.axis("off")
    rt_rows = _table_rows(rt_cv, ["model", "mae_mean", "rmse_mean", "r2_mean"], limit=6)
    _draw_table(ax_table, ["Модель RT", "MAE CV", "RMSE CV", "R² CV"], rt_rows, [0.32, 0.20, 0.20, 0.20])

    ax_q = fig.add_axes([0.055, 0.09, 0.55, 0.15])
    ax_q.axis("off")
    q_rows = _table_rows(quality_metrics, ["model", "validation_mae", "test_mae", "test_r2"], limit=6)
    _draw_table(ax_q, ["Quality surrogate", "Val MAE", "Test MAE", "Test R²"], q_rows, [0.35, 0.20, 0.20, 0.20], font_size=8)

    selected_text = (
        f"Выбрано: RT = {metadata.get('best_rt_model', 'n/a')}; "
        f"quality = {metadata.get('best_quality_model', 'n/a')}"
    )
    uncertainty = metadata.get("uncertainty_metadata", {}).get("rt", {})
    fig.text(0.64, 0.20, selected_text, fontsize=11, fontweight="bold", color=INK)
    fig.text(
        0.64,
        0.16,
        f"q90 uncertainty proxy: {float(uncertainty.get('q90_min', 0.0)):.3f} мин",
        fontsize=9,
        color=MUTED,
    )
    fig.text(0.64, 0.11, "Примечание: quality_score пока proxy, не лабораторный acceptance label.", fontsize=8.5, color=RED)


def _page_validation(fig: plt.Figure, data: dict[str, object]) -> None:
    metadata: dict[str, Any] = data["metadata"]  # type: ignore[assignment]
    source_holdout: pd.DataFrame = data["source_holdout"]  # type: ignore[assignment]
    source_metrics: pd.DataFrame = data["source_metrics"]  # type: ignore[assignment]

    fig.text(0.055, 0.94, "Валидация и переносимость", fontsize=22, fontweight="bold", color=INK)
    validation = metadata.get("validation_metadata", {})
    overlap = validation.get("group_overlap_counts", {})
    fig.text(
        0.055,
        0.905,
        f"Split: {validation.get('split_strategy', 'n/a')} | group = {validation.get('group_column', 'n/a')} | overlap train/val/test = {overlap}",
        fontsize=8.8,
        color=MUTED,
    )

    rt_holdout = source_holdout[source_holdout["target"].eq("rt_min")] if not source_holdout.empty else pd.DataFrame()
    for idx, family in enumerate(["MCMRT", "RepoRT"]):
        ax = fig.add_axes([0.06 + idx * 0.49, 0.53, 0.40, 0.30])
        subset = rt_holdout[rt_holdout["holdout_family"].eq(family)].sort_values("mae", ascending=False)
        if subset.empty:
            ax.axis("off")
            continue
        _barh(
            ax,
            subset.set_index("model")["mae"],
            f"Holdout {family}: train без {family}",
            "MAE, мин",
            BLUE if family == "MCMRT" else TEAL,
            highlight_min=True,
        )

    ax_holdout_table = fig.add_axes([0.055, 0.29, 0.50, 0.17])
    ax_holdout_table.axis("off")
    rows = _table_rows(rt_holdout.sort_values(["holdout_family", "mae"]), ["holdout_family", "model", "n_holdout", "mae", "rmse", "r2"], limit=8)
    _draw_table(ax_holdout_table, ["Источник", "Модель", "N", "MAE", "RMSE", "R²"], rows, [0.18, 0.25, 0.10, 0.13, 0.13, 0.12], font_size=7.5)

    ax_source = fig.add_axes([0.62, 0.17, 0.32, 0.29])
    if not source_metrics.empty:
        worst = source_metrics.sort_values("rt_mae", ascending=False).head(10)
        _barh(ax_source, worst.set_index("source_dataset")["rt_mae"].sort_values(), "Наихудшие source-wise ошибки", "MAE, мин", RED)

    ax_explain = fig.add_axes([0.055, 0.08, 0.50, 0.12])
    ax_explain.axis("off")
    _panel(ax_explain)
    ax_explain.text(0.025, 0.72, "Как читать эту страницу", fontsize=11, fontweight="bold", color=INK, transform=ax_explain.transAxes)
    ax_explain.text(
        0.025,
        0.42,
        _wrap_text(
            "Source-family holdout показывает перенос: модель обучается без всего семейства источника "
            "и тестируется на нём. Это строже random split и ближе к вопросу: "
            "«сработает ли на новом наборе методик?»",
            width=92,
        ),
        fontsize=8.5,
        color=INK,
        va="top",
        wrap=True,
        transform=ax_explain.transAxes,
    )


def _page_full_model_matrix(fig: plt.Figure, data: dict[str, object]) -> None:
    metadata: dict[str, Any] = data["metadata"]  # type: ignore[assignment]
    cv_metrics: pd.DataFrame = data["cv_metrics"]  # type: ignore[assignment]
    source_holdout: pd.DataFrame = data["source_holdout"]  # type: ignore[assignment]
    rt_metrics = pd.DataFrame(metadata.get("rt_metrics", {})).T.reset_index(names="model")
    quality_metrics = pd.DataFrame(metadata.get("quality_metrics", {})).T.reset_index(names="model")

    fig.text(0.055, 0.94, "Полная матрица сравнения моделей", fontsize=22, fontweight="bold", color=INK)
    fig.text(
        0.055,
        0.905,
        "Проверенные модели: Ridge, RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, CatBoost.",
        fontsize=10,
        color=MUTED,
    )

    rt_cv = cv_metrics[cv_metrics["target"].eq("rt_min")].sort_values("mae_mean") if not cv_metrics.empty else pd.DataFrame()
    q_cv = cv_metrics[cv_metrics["target"].eq("quality_score")].sort_values("mae_mean") if not cv_metrics.empty else pd.DataFrame()
    rt_holdout = source_holdout[source_holdout["target"].eq("rt_min")] if not source_holdout.empty else pd.DataFrame()

    ax_rt_cv = fig.add_axes([0.055, 0.59, 0.42, 0.25])
    ax_rt_cv.axis("off")
    _draw_table(
        ax_rt_cv,
        ["RT GroupKFold", "MAE", "RMSE", "R2"],
        _table_rows(rt_cv, ["model", "mae_mean", "rmse_mean", "r2_mean"], limit=8),
        [0.38, 0.18, 0.18, 0.18],
        font_size=8,
    )

    ax_rt_final = fig.add_axes([0.525, 0.59, 0.42, 0.25])
    ax_rt_final.axis("off")
    _draw_table(
        ax_rt_final,
        ["RT final holdout", "Val MAE", "Test MAE", "Test R2"],
        _table_rows(rt_metrics.sort_values("test_mae"), ["model", "validation_mae", "test_mae", "test_r2"], limit=8),
        [0.38, 0.18, 0.18, 0.18],
        font_size=8,
    )

    ax_q_cv = fig.add_axes([0.055, 0.30, 0.42, 0.22])
    ax_q_cv.axis("off")
    _draw_table(
        ax_q_cv,
        ["Quality GroupKFold", "MAE", "RMSE", "R2"],
        _table_rows(q_cv, ["model", "mae_mean", "rmse_mean", "r2_mean"], limit=8),
        [0.38, 0.18, 0.18, 0.18],
        font_size=8,
    )

    ax_q_final = fig.add_axes([0.525, 0.30, 0.42, 0.22])
    ax_q_final.axis("off")
    _draw_table(
        ax_q_final,
        ["Quality final holdout", "Val MAE", "Test MAE", "Test R2"],
        _table_rows(quality_metrics.sort_values("test_mae"), ["model", "validation_mae", "test_mae", "test_r2"], limit=8),
        [0.38, 0.18, 0.18, 0.18],
        font_size=8,
    )

    ax_transfer = fig.add_axes([0.055, 0.075, 0.89, 0.16])
    ax_transfer.axis("off")
    transfer = rt_holdout.sort_values(["holdout_family", "mae"]) if not rt_holdout.empty else pd.DataFrame()
    _draw_table(
        ax_transfer,
        ["Transfer holdout", "Модель", "N", "MAE", "RMSE", "R2"],
        _table_rows(transfer, ["holdout_family", "model", "n_holdout", "mae", "rmse", "r2"], limit=10),
        [0.18, 0.27, 0.09, 0.12, 0.12, 0.12],
        font_size=7.5,
    )


def _page_parameters(fig: plt.Figure, data: dict[str, object]) -> None:
    importance: pd.DataFrame = data["importance"]  # type: ignore[assignment]
    predictions: pd.DataFrame = data["predictions"]  # type: ignore[assignment]

    fig.text(0.055, 0.94, "Значимость параметров и диагностика ошибок", fontsize=22, fontweight="bold", color=INK)
    fig.text(0.055, 0.905, "Permutation importance рассчитан для выбранной RT-модели на holdout-наборе.", fontsize=10, color=MUTED)

    top = importance.head(10) if not importance.empty else pd.DataFrame()
    if not top.empty:
        ax_imp = fig.add_axes([0.06, 0.51, 0.45, 0.32])
        _barh(ax_imp, top.set_index("feature")["importance_mean"].sort_values(), "Top-10 факторов RT", "важность", BLUE)

        ax_table = fig.add_axes([0.59, 0.51, 0.35, 0.32])
        ax_table.axis("off")
        rows = _table_rows(top, ["feature", "feature_group", "importance_mean", "significance"], limit=10)
        _draw_table(ax_table, ["Фича", "Группа", "Imp.", "Сигнал"], rows, [0.31, 0.28, 0.16, 0.20], font_size=7)

    ax_diag = fig.add_axes([0.055, 0.09, 0.89, 0.33])
    ax_diag.axis("off")
    if not predictions.empty:
        mae = predictions["abs_rt_error_min"].mean() if "abs_rt_error_min" in predictions else np.nan
        rmse = (predictions["rt_error_min"].pow(2).mean() ** 0.5) if "rt_error_min" in predictions else np.nan
        ad_flags = int(predictions["ad_flag"].sum()) if "ad_flag" in predictions else 0
        ax_diag.text(
            0,
            1.05,
            f"Holdout diagnostics: N={len(predictions)} | RT MAE={mae:.3f} мин | RT RMSE={rmse:.3f} мин | AD flags={ad_flags}",
            fontsize=10,
            fontweight="bold",
            color=INK,
            transform=ax_diag.transAxes,
        )
        worst = predictions.sort_values("abs_rt_error_min", ascending=False).head(9)
        rows = _table_rows(worst, ["compound_name", "source_dataset", "rt_min", "predicted_rt_min", "abs_rt_error_min"], limit=9)
        _draw_table(ax_diag, ["Соединение", "Источник", "Факт RT", "Прогноз RT", "|Ошибка|"], rows, [0.27, 0.20, 0.14, 0.16, 0.14], font_size=7.5)


def _page_roadmap(fig: plt.Figure, data: dict[str, object]) -> None:
    fig.text(0.055, 0.94, "Roadmap развития", fontsize=22, fontweight="bold", color=INK)
    fig.text(0.055, 0.905, "Что делать дальше, чтобы MVP стал лабораторно полезным, а не только публичным benchmark.", fontsize=10, color=MUTED)

    phases = [
        (
            "0-2 недели: данные лаборатории",
            [
                "Загрузить исторические BE-style разработки: accepted, failed, low intensity, poor resolution, carryover.",
                "Стабилизировать словари matrix, ion mode, column family, solvent system, instrument platform.",
                "Добавить import preview: пропуски, недопустимые диапазоны, дубликаты runs, ошибки SMILES.",
            ],
        ),
        (
            "2-4 недели: честная оценка качества",
            [
                "Держать GroupKFold по InChIKey как baseline validation.",
                "Добавить holdout по method family/column family и отдельную проверку на internal-only split.",
                "Калибровать conformal intervals по source/matrix/column chemistry.",
            ],
        ),
        (
            "1-2 месяца: рекомендации методик",
            [
                "Разложить recommendation score на RT fit, quality, runtime, confidence и AD penalty.",
                "Ограничить search space утверждёнными колонками, растворителями, pH, flow, temperature и runtime.",
                "Собирать feedback от химиков и использовать его для active learning.",
            ],
        ),
        (
            "2-4 месяца: SOTA track",
            [
                "Сравнить descriptor+GBM с Morgan fingerprints, graph encoders и structure Transformer embeddings.",
                "Для межметодного переноса добавить retention-order/ranking objective, а не только absolute RT.",
                "Отдельно обучать/калибровать модели под bioanalytical matrix и instrument platform.",
            ],
        ),
    ]
    for idx, (title, bullets) in enumerate(phases):
        x = 0.06 if idx % 2 == 0 else 0.53
        y = 0.58 if idx < 2 else 0.27
        ax = fig.add_axes([x, y, 0.40, 0.25])
        ax.axis("off")
        _panel(ax)
        ax.text(0.04, 0.84, title, fontsize=12, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.04, 0.66, _wrap_bullets(bullets), fontsize=8.0, color=INK, va="top", transform=ax.transAxes)

    fig.text(
        0.055,
        0.07,
        "Decision gate: не заявлять production readiness, пока нет внутреннего лабораторного датасета, source/method holdout и критериев acceptance от аналитиков.",
        fontsize=9.5,
        fontweight="bold",
        color=RED,
    )


def _card(fig: plt.Figure, x: float, y: float, w: float, h: float, value: str, label: str) -> None:
    ax = fig.add_axes([x, y, w, h])
    ax.axis("off")
    box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.018,rounding_size=0.04", linewidth=0, facecolor=PANEL)
    ax.add_patch(box)
    ax.text(0.07, 0.58, value, fontsize=20, fontweight="bold", color=INK, transform=ax.transAxes)
    ax.text(0.07, 0.24, label, fontsize=9, color=MUTED, transform=ax.transAxes)


def _panel(ax: plt.Axes) -> None:
    box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.014,rounding_size=0.03", linewidth=0.8, edgecolor=GRID, facecolor=PANEL)
    ax.add_patch(box)


def _barh(
    ax: plt.Axes,
    series: pd.Series,
    title: str,
    xlabel: str,
    color: str,
    value_fmt: str = "{:.2f}",
    highlight_min: bool = False,
) -> None:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = [str(label).replace("_", " ")[:28] for label in values.index]
    colors = [color] * len(values)
    if highlight_min and len(values):
        colors[int(np.argmin(values.to_numpy()))] = RED
    ax.barh(labels, values.to_numpy(), color=colors, height=0.64)
    ax.set_title(title, loc="left", fontweight="bold", color=INK, pad=8)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0, pad=4)
    max_value = float(values.max()) if len(values) else 0.0
    for idx, value in enumerate(values.to_numpy()):
        ax.text(value + max_value * 0.015, idx, value_fmt.format(value), va="center", fontsize=7.5, color=INK)
    ax.margins(x=0.15)


def _draw_table(ax: plt.Axes, headers: list[str], rows: list[list[str]], widths: list[float], font_size: float = 8) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    row_count = max(len(rows), 1) + 1
    row_h = min(0.12, 0.94 / row_count)
    y = 0.98
    x_positions = np.cumsum([0] + widths)
    for idx, header in enumerate(headers):
        ax.add_patch(plt.Rectangle((x_positions[idx], y - row_h), widths[idx], row_h, color="#E7EEF5", ec="white"))
        ax.text(x_positions[idx] + 0.01, y - row_h * 0.65, header, fontsize=font_size, fontweight="bold", color=INK)
    y -= row_h
    for row_idx, row in enumerate(rows):
        fill = "#FFFFFF" if row_idx % 2 == 0 else "#F6F8FA"
        for col_idx, cell in enumerate(row):
            ax.add_patch(plt.Rectangle((x_positions[col_idx], y - row_h), widths[col_idx], row_h, color=fill, ec="white"))
            ax.text(x_positions[col_idx] + 0.01, y - row_h * 0.65, _clip(cell, widths[col_idx]), fontsize=font_size, color=INK)
        y -= row_h


def _table_rows(frame: pd.DataFrame, columns: list[str], limit: int = 10) -> list[list[str]]:
    rows = []
    if frame.empty:
        return rows
    for _, row in frame.head(limit).iterrows():
        cells = []
        for column in columns:
            value = row.get(column, "")
            if pd.isna(value):
                cells.append("н/д")
            elif isinstance(value, (float, np.floating)):
                cells.append(f"{float(value):.3f}")
            elif isinstance(value, (int, np.integer)):
                cells.append(str(int(value)))
            else:
                cells.append(str(value))
        rows.append(cells)
    return rows


def _clip(value: str, width: float) -> str:
    max_chars = max(5, int(width * 52))
    return value if len(value) <= max_chars else value[: max_chars - 1] + "…"


def _wrap_bullets(bullets: list[str], width: int = 72) -> str:
    lines: list[str] = []
    for bullet in bullets:
        wrapped = _wrap_text(bullet, width).splitlines() or [""]
        lines.append(f"• {wrapped[0]}")
        lines.extend(f"  {line}" for line in wrapped[1:])
    return "\n".join(lines)


def _wrap_text(text: str, width: int = 80) -> str:
    import textwrap

    return "\n".join(textwrap.wrap(text, width=width))


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


if __name__ == "__main__":
    raise SystemExit(main())
