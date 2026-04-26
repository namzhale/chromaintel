from __future__ import annotations

import argparse
import sys
import textwrap
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

INK = "#16212F"
MUTED = "#5C6672"
BLUE = "#246BBA"
TEAL = "#2A9D8F"
RED = "#B94A48"
AMBER = "#C9822B"
PANEL = "#F3F7FA"
GRID = "#D8E0E8"
ROW_ALT = "#F7FAFC"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    data = _load_dashboard_data()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(args.output, data)
    print(f"Wrote dashboard PDF: {args.output.resolve()}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the Russian ChromaIntel dashboard PDF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _load_dashboard_data() -> dict[str, object]:
    metadata: dict[str, Any] = {}
    if MODEL_BUNDLE.exists():
        bundle = joblib.load(MODEL_BUNDLE)
        metadata = bundle.get("metadata", {}) if isinstance(bundle, dict) else {}
    return {
        "master": _read_csv(PROCESSED_DIR / "master_dataset.csv"),
        "matrix": _read_csv(PROCESSED_DIR / "model_matrix.csv"),
        "cv": _read_csv(REPORTS_DIR / "cv_metrics.csv"),
        "benchmark": _read_csv(REPORTS_DIR / "model_benchmark_matrix.csv"),
        "source_holdout": _read_csv(REPORTS_DIR / "source_holdout_metrics.csv"),
        "method_holdout": _read_csv(REPORTS_DIR / "method_holdout_metrics.csv"),
        "column_holdout": _read_csv(REPORTS_DIR / "column_family_holdout_metrics.csv"),
        "importance": _read_csv(REPORTS_DIR / "feature_importance.csv"),
        "source_metrics": _read_csv(REPORTS_DIR / "source_metrics.csv"),
        "predictions": _read_csv(REPORTS_DIR / "test_predictions.csv"),
        "target_coverage": _read_csv(REPORTS_DIR / "target_coverage_matrix.csv"),
        "inverse_metrics": _read_csv(REPORTS_DIR / "inverse_model_metrics.csv"),
        "inverse_topk": _read_csv(REPORTS_DIR / "inverse_topk_evaluation.csv"),
        "metadata": metadata,
    }


def build_pdf(path: Path, data: dict[str, object]) -> None:
    """Build a compact Russian PDF dashboard from existing ChromaIntel reports."""

    _setup_matplotlib()
    with PdfPages(path) as pdf:
        for builder in (
            _page_dataset,
            _page_model_comparison,
            _page_transfer_validation,
            _page_feature_and_error_analysis,
            _page_target_inverse_models,
            _page_roadmap,
        ):
            fig = _new_page()
            builder(fig, data)
            pdf.savefig(fig)
            plt.close(fig)


def _setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.facecolor": "white",
            "axes.titlesize": 11,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
        }
    )


def _new_page() -> plt.Figure:
    return plt.figure(figsize=(11.69, 8.27), dpi=150)


def _page_dataset(fig: plt.Figure, data: dict[str, object]) -> None:
    master: pd.DataFrame = data["master"]  # type: ignore[assignment]
    matrix: pd.DataFrame = data["matrix"]  # type: ignore[assignment]

    _title(
        fig,
        "ChromaIntel LC-MS/MS: дашборд MVP",
        "Датасет, модели, переносимость между источниками/методами и дальнейшая дорожная карта",
    )

    source_counts = _value_counts(master, "source_dataset")
    family_counts = master["source_dataset"].astype(str).str.split(":").str[0].value_counts() if "source_dataset" in master else pd.Series(dtype=int)
    compound_count = _compound_count(master)
    cards = [
        ("Master rows", len(master), "строк после canonical merge"),
        ("Model rows", len(matrix), "строк в model matrix"),
        ("Compounds", compound_count, "уникальных соединений"),
        ("Sources", len(source_counts), f"{len(family_counts)} семейств"),
    ]
    _metric_cards(fig, cards)

    ax_sources = fig.add_axes([0.13, 0.35, 0.35, 0.38])
    _barh(
        ax_sources,
        source_counts.head(16).sort_values(),
        "Крупнейшие источники данных",
        "строк",
        BLUE,
        value_fmt="{:,.0f}",
    )

    ax_missing = fig.add_axes([0.56, 0.35, 0.37, 0.38])
    missing = master.isna().mean().sort_values(ascending=False).head(10) if not master.empty else pd.Series(dtype=float)
    _barh(ax_missing, missing.sort_values(), "Поля с наибольшей долей пропусков", "доля", TEAL, value_fmt="{:.2f}")

    ax_notes = fig.add_axes([0.055, 0.08, 0.88, 0.20])
    _panel(ax_notes)
    _panel_text(
        ax_notes,
        "Ключевые выводы",
        [
            "Основная supervised-цель: время удержания `rt_min`. Quality score пока является прозрачным surrogate, а не лабораторным acceptance label.",
            "Текущий expanded build объединяет ReTiNA, METLIN SMRT Figshare, MCMRT, RepoRT и mock/internal seed без добавления Kaggle descriptor sidecar как новых RT-таргетов.",
            "Большие CSV/joblib артефакты локальные и воспроизводимые; в git попадают код, отчеты и правила artifact policy.",
        ],
    )


def _page_model_comparison(fig: plt.Figure, data: dict[str, object]) -> None:
    cv: pd.DataFrame = data["cv"]  # type: ignore[assignment]
    benchmark: pd.DataFrame = data["benchmark"]  # type: ignore[assignment]
    metadata: dict[str, Any] = data["metadata"]  # type: ignore[assignment]

    _title(
        fig,
        "Сравнение моделей",
        "Random split не используется как единственное доказательство; главный sanity-check здесь GroupKFold по InChIKey и final grouped holdout.",
    )

    rt_cv = cv[cv["target"].eq("rt_min")].sort_values("mae_mean") if not cv.empty else pd.DataFrame()
    q_cv = cv[cv["target"].eq("quality_score")].sort_values("mae_mean") if not cv.empty else pd.DataFrame()
    final_rt = _benchmark_subset(benchmark, "final_grouped_holdout", "rt_min")

    ax_cv_mae = fig.add_axes([0.12, 0.56, 0.32, 0.28])
    if not rt_cv.empty:
        _barh(ax_cv_mae, rt_cv.set_index("model")["mae_mean"].sort_values(ascending=False), "RT GroupKFold MAE", "мин", BLUE, highlight_min=True)
    else:
        _empty(ax_cv_mae, "Нет cv_metrics.csv")

    ax_test_mae = fig.add_axes([0.56, 0.56, 0.38, 0.28])
    if not final_rt.empty:
        _barh(ax_test_mae, final_rt.set_index("model_family")["mae"].sort_values(ascending=False), "RT final holdout MAE", "мин", TEAL, highlight_min=True)
    else:
        _empty(ax_test_mae, "Нет final holdout")

    ax_rt_table = fig.add_axes([0.055, 0.31, 0.53, 0.18])
    _draw_table(
        ax_rt_table,
        ["RT model", "CV MAE", "CV RMSE", "CV R²", "Spearman"],
        _rows(rt_cv, ["model", "mae_mean", "rmse_mean", "r2_mean", "spearman_mean"], limit=6),
        [0.34, 0.15, 0.15, 0.13, 0.16],
    )

    ax_q_table = fig.add_axes([0.055, 0.11, 0.53, 0.15])
    _draw_table(
        ax_q_table,
        ["Quality surrogate", "CV MAE", "CV RMSE", "CV R²"],
        _rows(q_cv, ["model", "mae_mean", "rmse_mean", "r2_mean"], limit=6),
        [0.40, 0.17, 0.17, 0.17],
    )

    ax_summary = fig.add_axes([0.64, 0.11, 0.30, 0.34])
    _panel(ax_summary)
    selected_rt = metadata.get("best_rt_model", _first(rt_cv, "model"))
    selected_q = metadata.get("best_quality_model", _first(q_cv, "model"))
    uncertainty = metadata.get("uncertainty_metadata", {}).get("rt", {}) if isinstance(metadata.get("uncertainty_metadata"), dict) else {}
    lines = [
        f"Выбранная RT-модель: {selected_rt}",
        f"Quality surrogate: {selected_q}",
        f"q90 residual proxy: {_fmt(uncertainty.get('q90_min'))} мин",
        "CatBoost/XGBoost поддерживаются в full-запуске; quick-mode на expanded matrix оставляет CPU-практичный набор.",
        "Quality-метрики нельзя трактовать как реальное peak-shape качество без внутренних lab labels.",
    ]
    ax_summary.text(0.05, 0.90, "Интерпретация", fontsize=12, fontweight="bold", color=INK, transform=ax_summary.transAxes)
    ax_summary.text(0.05, 0.73, _wrap_bullets(lines, width=45), fontsize=8.2, color=INK, va="top", transform=ax_summary.transAxes)


def _page_transfer_validation(fig: plt.Figure, data: dict[str, object]) -> None:
    source_holdout: pd.DataFrame = data["source_holdout"]  # type: ignore[assignment]
    method_holdout: pd.DataFrame = data["method_holdout"]  # type: ignore[assignment]
    column_holdout: pd.DataFrame = data["column_holdout"]  # type: ignore[assignment]
    source_metrics: pd.DataFrame = data["source_metrics"]  # type: ignore[assignment]

    _title(
        fig,
        "Переносимость: source / method / column holdout",
        "Эти проверки важнее случайного split: они отвечают, переносится ли модель на новые источники, методы и семейства колонок.",
    )

    ax_source = fig.add_axes([0.09, 0.56, 0.25, 0.28])
    _holdout_best_bar(ax_source, source_holdout, "holdout_family", "Source-family holdout", BLUE)

    ax_method = fig.add_axes([0.42, 0.56, 0.25, 0.28])
    _holdout_best_bar(ax_method, method_holdout, "holdout_method", "Method holdout", TEAL)

    ax_column = fig.add_axes([0.715, 0.56, 0.23, 0.28])
    _holdout_best_bar(ax_column, column_holdout, "holdout_column_family", "Column-family holdout", AMBER)

    ax_table = fig.add_axes([0.055, 0.28, 0.58, 0.20])
    transfer_rows = _combined_holdout_rows(source_holdout, method_holdout, column_holdout)
    _draw_table(
        ax_table,
        ["Scope", "Holdout", "Best model", "N", "MAE", "nMAE % runtime"],
        transfer_rows[:9],
        [0.17, 0.27, 0.21, 0.09, 0.10, 0.13],
        font_size=7.5,
    )

    ax_worst = fig.add_axes([0.69, 0.25, 0.25, 0.23])
    if not source_metrics.empty:
        worst = source_metrics.sort_values("rt_mae", ascending=False).head(8)
        _barh(ax_worst, worst.set_index("source_dataset")["rt_mae"].sort_values(), "Worst source-wise MAE", "мин", RED)
    else:
        _empty(ax_worst, "Нет source_metrics.csv")

    ax_note = fig.add_axes([0.055, 0.08, 0.88, 0.12])
    _panel(ax_note)
    _panel_text(
        ax_note,
        "Что это значит",
        [
            "Если holdout MAE резко хуже grouped holdout, модель запоминает локальные режимы метода/источника и нуждается в method-conditioned features или calibrants.",
            "Для bioanalytical BE-style применения главный следующий gate: internal time-based или new-method holdout на реальных лабораторных runs.",
        ],
        title_size=10.5,
        text_size=8.2,
    )


def _page_feature_and_error_analysis(fig: plt.Figure, data: dict[str, object]) -> None:
    importance: pd.DataFrame = data["importance"]  # type: ignore[assignment]
    predictions: pd.DataFrame = data["predictions"]  # type: ignore[assignment]

    _title(
        fig,
        "Значимость параметров и ошибки holdout",
        "Permutation importance показывает, какие признаки реально двигают RT-модель на текущем holdout.",
    )

    top = importance.head(10) if not importance.empty else pd.DataFrame()
    ax_imp = fig.add_axes([0.13, 0.50, 0.37, 0.34])
    if not top.empty:
        _barh(ax_imp, top.set_index("feature")["importance_mean"].sort_values(), "Top-10 факторов RT", "importance", BLUE)
    else:
        _empty(ax_imp, "Нет feature_importance.csv")

    ax_imp_table = fig.add_axes([0.56, 0.50, 0.38, 0.34])
    _draw_table(
        ax_imp_table,
        ["Feature", "Group", "Importance", "Signal"],
        _rows(top, ["feature", "feature_group", "importance_mean", "significance"], limit=10),
        [0.34, 0.27, 0.18, 0.15],
        font_size=7.3,
    )

    ax_pred = fig.add_axes([0.055, 0.09, 0.64, 0.31])
    if not predictions.empty:
        worst = predictions.sort_values("abs_rt_error_min", ascending=False).head(10)
        mae = predictions["abs_rt_error_min"].mean() if "abs_rt_error_min" in predictions else np.nan
        rmse = float(np.sqrt(np.mean(np.square(predictions["rt_error_min"])))) if "rt_error_min" in predictions else np.nan
        ax_pred.text(0.0, 1.03, f"Holdout: N={len(predictions):,} | MAE={mae:.3f} мин | RMSE={rmse:.3f} мин", fontsize=10, fontweight="bold", color=INK, transform=ax_pred.transAxes)
        _draw_table(
            ax_pred,
            ["Compound", "Source", "Actual RT", "Pred RT", "|Error|"],
            _rows(worst, ["compound_name", "source_dataset", "rt_min", "predicted_rt_min", "abs_rt_error_min"], limit=10),
            [0.28, 0.22, 0.14, 0.14, 0.13],
            font_size=7.2,
            top_margin=0.92,
        )
    else:
        _empty(ax_pred, "Нет test_predictions.csv")

    ax_ad = fig.add_axes([0.75, 0.09, 0.19, 0.31])
    _panel(ax_ad)
    ad_flags = int(predictions["ad_flag"].sum()) if "ad_flag" in predictions else 0
    ax_ad.text(0.08, 0.86, "Applicability domain", fontsize=10.5, fontweight="bold", color=INK, transform=ax_ad.transAxes)
    ax_ad.text(0.08, 0.70, f"AD flags: {ad_flags:,}", fontsize=15, fontweight="bold", color=RED if ad_flags else TEAL, transform=ax_ad.transAxes)
    ax_ad.text(
        0.08,
        0.50,
        _wrap_text("Низкий AD support должен понижать confidence и штрафовать inverse recommendation.", 31),
        fontsize=8,
        color=INK,
        va="top",
        transform=ax_ad.transAxes,
    )


def _page_target_inverse_models(fig: plt.Figure, data: dict[str, object]) -> None:
    coverage: pd.DataFrame = data["target_coverage"]  # type: ignore[assignment]
    inverse_metrics: pd.DataFrame = data["inverse_metrics"]  # type: ignore[assignment]
    inverse_topk: pd.DataFrame = data["inverse_topk"]  # type: ignore[assignment]

    _title(
        fig,
        "Peak targets и ML-модель обратной задачи",
        "Эта страница отделяет измеренные peak labels от proxy targets и показывает baseline для inverse ranking.",
    )

    ax_cov = fig.add_axes([0.055, 0.50, 0.45, 0.34])
    if not coverage.empty:
        cov = coverage.head(12).copy()
        _barh(
            ax_cov,
            cov.set_index("target")["coverage_fraction"].sort_values(),
            "Target coverage",
            "доля строк",
            TEAL,
            value_fmt="{:.2f}",
        )
    else:
        _empty(ax_cov, "Нет target_coverage_matrix.csv")

    ax_cov_table = fig.add_axes([0.56, 0.50, 0.38, 0.34])
    _draw_table(
        ax_cov_table,
        ["Target", "Coverage", "Label", "Readiness"],
        _rows(coverage, ["target", "coverage_fraction", "label_source", "readiness"], limit=11),
        [0.35, 0.16, 0.22, 0.22],
        font_size=7.2,
    )

    ax_inv = fig.add_axes([0.055, 0.17, 0.43, 0.23])
    if not inverse_metrics.empty and "pr_auc" in inverse_metrics:
        best = inverse_metrics.sort_values("pr_auc", ascending=True).tail(8)
        _barh(ax_inv, best.set_index("model")["pr_auc"], "Inverse PR-AUC", "PR-AUC", BLUE, highlight_min=False)
    else:
        _empty(ax_inv, "Нет inverse_model_metrics.csv")

    ax_inv_table = fig.add_axes([0.55, 0.17, 0.39, 0.23])
    if not inverse_metrics.empty and not inverse_topk.empty:
        merge_keys = ["model", "label_source"] if "label_source" in inverse_metrics and "label_source" in inverse_topk else ["model"]
        merged = inverse_metrics.merge(inverse_topk, on=merge_keys, how="left")
    else:
        merged = inverse_metrics
    _draw_table(
        ax_inv_table,
        ["Model", "ROC-AUC", "PR-AUC", "Brier", "Top-3"],
        _rows(merged.sort_values("pr_auc", ascending=False) if "pr_auc" in merged else merged, ["model", "roc_auc", "pr_auc", "brier_score", "top_3_success"], limit=8),
        [0.34, 0.16, 0.16, 0.16, 0.14],
        font_size=7.2,
    )

    ax_note = fig.add_axes([0.055, 0.06, 0.89, 0.08])
    _panel(ax_note, face="#FFF9EC", edge="#E6D5AA")
    ax_note.text(
        0.025,
        0.62,
        _wrap_text(
            "Inverse labels сейчас synthetic_proxy: они проверяют ранжирование candidate methods, но не заменяют реальные accepted/failed lab outcomes.",
            130,
        ),
        fontsize=8.6,
        fontweight="bold",
        color=AMBER,
        va="center",
        transform=ax_note.transAxes,
    )


def _page_roadmap(fig: plt.Figure, data: dict[str, object]) -> None:
    _title(
        fig,
        "Roadmap: от MVP к лабораторной платформе",
        "Следующий рост качества зависит не только от архитектуры, а прежде всего от внутренних peak-quality и assay outcome labels.",
    )

    cards = [
        (
            "1. Данные и lab feedback",
            [
                "Подключить реальные BE-style historical runs: accepted, failed, low intensity, poor resolution, carryover.",
                "Разделить labels: measured peak quality, derived surrogate, weak label, unknown.",
                "Добавить time-based internal holdout и source-quality score.",
            ],
        ),
        (
            "2. Модели",
            [
                "Сравнить core vs Morgan/full на expanded matrix.",
                "Запустить XGBoost/CatBoost full run и dependency-gated graph/SMILES-transformer embeddings.",
                "Добавить quantile/conformal intervals по source/method/column-family.",
            ],
        ),
        (
            "3. Inverse recommendation",
            [
                "Расширить YAML/JSON method templates под доступные колонки и растворители лаборатории.",
                "Ранжировать по RT fit, quality, runtime, uncertainty, AD penalty, order score и transition support.",
                "Сохранять каждую рекомендацию в audit trail для последующего active learning.",
            ],
        ),
        (
            "4. Дашборды и release",
            [
                "Добавить в Streamlit source/method/column holdout panels и import preview для local-public CSV.",
                "Smoke-test FastAPI и Streamlit перед release.",
                "Определить artifact/LFS policy для передачи больших trained bundles.",
            ],
        ),
    ]

    positions = [(0.055, 0.55), (0.53, 0.55), (0.055, 0.22), (0.53, 0.22)]
    for (title, bullets), (x, y) in zip(cards, positions):
        ax = fig.add_axes([x, y, 0.415, 0.25])
        _panel(ax)
        ax.text(0.045, 0.84, title, fontsize=12, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.045, 0.66, _wrap_bullets(bullets, width=58), fontsize=8.0, color=INK, va="top", transform=ax.transAxes)

    ax_gate = fig.add_axes([0.055, 0.08, 0.89, 0.08])
    _panel(ax_gate, face="#FFF5F2", edge="#E6B8AA")
    ax_gate.text(
        0.025,
        0.62,
        _wrap_text(
            "Decision gate: не заявлять production readiness, пока нет внутреннего validation split, "
            "реальных peak-shape labels и проверенной переносимости на новые методы.",
            112,
        ),
        fontsize=8.8,
        fontweight="bold",
        color=RED,
        va="center",
        transform=ax_gate.transAxes,
    )


def _title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.055, 0.94, title, fontsize=21, fontweight="bold", color=INK)
    fig.text(0.055, 0.905, subtitle, fontsize=9.5, color=MUTED)


def _metric_cards(fig: plt.Figure, cards: list[tuple[str, int, str]]) -> None:
    for idx, (label, value, hint) in enumerate(cards):
        ax = fig.add_axes([0.055 + idx * 0.225, 0.78, 0.19, 0.10])
        _panel(ax, face="#EAF2F8", edge="#EAF2F8")
        ax.text(0.07, 0.58, f"{value:,}".replace(",", " "), fontsize=18, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.07, 0.31, label, fontsize=8.5, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.07, 0.13, hint, fontsize=7.2, color=MUTED, transform=ax.transAxes)


def _panel(ax: plt.Axes, face: str = PANEL, edge: str = GRID) -> None:
    ax.axis("off")
    box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01,rounding_size=0.025", linewidth=0.8, edgecolor=edge, facecolor=face)
    ax.add_patch(box)


def _panel_text(ax: plt.Axes, title: str, bullets: list[str], title_size: float = 12, text_size: float = 8.6) -> None:
    ax.text(0.025, 0.76, title, fontsize=title_size, fontweight="bold", color=INK, transform=ax.transAxes)
    ax.text(0.025, 0.54, _wrap_bullets(bullets, width=145), fontsize=text_size, color=INK, va="top", transform=ax.transAxes)


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
    labels = [_short_label(label) for label in values.index]
    colors = [color] * len(values)
    if highlight_min and len(values):
        colors[int(np.argmin(values.to_numpy()))] = RED
    ax.barh(labels, values.to_numpy(), color=colors, height=0.62)
    ax.set_title(title, loc="left", fontweight="bold", color=INK, pad=7)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0, pad=3)
    max_value = float(values.max()) if len(values) else 0.0
    offset = max(max_value * 0.015, 0.01)
    for idx, value in enumerate(values.to_numpy()):
        ax.text(value + offset, idx, value_fmt.format(value), va="center", fontsize=7, color=INK)
    ax.margins(x=0.18)


def _draw_table(
    ax: plt.Axes,
    headers: list[str],
    rows: list[list[str]],
    widths: list[float],
    font_size: float = 8,
    top_margin: float = 0.98,
) -> None:
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    widths = _normalize_widths(widths)
    row_count = max(len(rows), 1) + 1
    row_h = min(0.105, (top_margin - 0.02) / row_count)
    y = top_margin
    x_positions = np.cumsum([0] + widths)
    for idx, header in enumerate(headers):
        ax.add_patch(plt.Rectangle((x_positions[idx], y - row_h), widths[idx], row_h, color="#E6EEF6", ec="white"))
        ax.text(x_positions[idx] + 0.006, y - row_h * 0.65, header, fontsize=font_size, fontweight="bold", color=INK)
    y -= row_h
    if not rows:
        rows = [["н/д"] + [""] * (len(headers) - 1)]
    for row_idx, row in enumerate(rows):
        fill = "white" if row_idx % 2 == 0 else ROW_ALT
        for col_idx, cell in enumerate(row[: len(headers)]):
            ax.add_patch(plt.Rectangle((x_positions[col_idx], y - row_h), widths[col_idx], row_h, color=fill, ec="white"))
            ax.text(x_positions[col_idx] + 0.006, y - row_h * 0.65, _clip(str(cell), widths[col_idx]), fontsize=font_size, color=INK)
        y -= row_h


def _holdout_best_bar(ax: plt.Axes, frame: pd.DataFrame, key_column: str, title: str, color: str) -> None:
    if frame.empty or key_column not in frame or "target" not in frame:
        _empty(ax, "Нет данных")
        return
    rt = frame[frame["target"].eq("rt_min")].copy()
    if rt.empty:
        _empty(ax, "Нет RT holdout")
        return
    best = rt.sort_values("mae").groupby(key_column, as_index=False).first().sort_values("mae", ascending=False).head(7)
    _barh(ax, best.set_index(key_column)["mae"], title, "best MAE, мин", color, highlight_min=True)


def _combined_holdout_rows(source: pd.DataFrame, method: pd.DataFrame, column: pd.DataFrame) -> list[list[str]]:
    configs = [
        ("source", source, "holdout_family"),
        ("method", method, "holdout_method"),
        ("column", column, "holdout_column_family"),
    ]
    rows: list[list[str]] = []
    for scope, frame, key in configs:
        if frame.empty or key not in frame:
            continue
        rt = frame[frame["target"].eq("rt_min")].copy() if "target" in frame else frame.copy()
        if rt.empty:
            continue
        best = rt.sort_values("mae").groupby(key, as_index=False).first().sort_values("mae").head(4)
        for _, row in best.iterrows():
            rows.append(
                [
                    scope,
                    str(row.get(key, "")),
                    str(row.get("model", "")),
                    _fmt(row.get("n_holdout"), decimals=0),
                    _fmt(row.get("mae")),
                    _fmt(row.get("normalized_mae_runtime_pct")),
                ]
            )
    return rows


def _benchmark_subset(frame: pd.DataFrame, split: str, target: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    subset = frame[frame["split"].eq(split) & frame["target"].eq(target)].copy()
    return subset.sort_values("mae") if "mae" in subset else subset


def _rows(frame: pd.DataFrame, columns: list[str], limit: int = 10) -> list[list[str]]:
    if frame.empty:
        return []
    rows: list[list[str]] = []
    for _, row in frame.head(limit).iterrows():
        rows.append([_fmt_cell(row.get(column)) for column in columns])
    return rows


def _fmt_cell(value: Any) -> str:
    if pd.isna(value):
        return "н/д"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.3f}"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return str(value)


def _fmt(value: Any, decimals: int = 3) -> str:
    if value is None or pd.isna(value):
        return "н/д"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if decimals == 0:
        return f"{int(round(number))}"
    return f"{number:.{decimals}f}"


def _clip(value: str, width: float) -> str:
    max_chars = max(5, int(width * 60))
    return value if len(value) <= max_chars else value[: max_chars - 1] + "…"


def _short_label(value: object, max_len: int = 30) -> str:
    label = str(value).replace("_", " ")
    return label if len(label) <= max_len else label[: max_len - 1] + "…"


def _wrap_text(text: str, width: int = 80) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def _wrap_bullets(bullets: list[str], width: int = 80) -> str:
    lines: list[str] = []
    for bullet in bullets:
        wrapped = textwrap.wrap(bullet, width=width) or [""]
        lines.append(f"• {wrapped[0]}")
        lines.extend(f"  {line}" for line in wrapped[1:])
    return "\n".join(lines)


def _normalize_widths(widths: list[float]) -> list[float]:
    total = sum(widths)
    return [width / total for width in widths] if total else widths


def _value_counts(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame[column].astype(str).value_counts() if column in frame else pd.Series(dtype=int)


def _compound_count(master: pd.DataFrame) -> int:
    counts = []
    for column in ("inchikey", "canonical_smiles", "compound_name"):
        if column in master:
            counts.append(int(master[column].dropna().nunique()))
    return max(counts) if counts else 0


def _first(frame: pd.DataFrame, column: str) -> str:
    if frame.empty or column not in frame:
        return "н/д"
    return str(frame.iloc[0][column])


def _empty(ax: plt.Axes, message: str) -> None:
    ax.axis("off")
    _panel(ax)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=9, color=MUTED, transform=ax.transAxes)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False) if path.exists() else pd.DataFrame()


if __name__ == "__main__":
    raise SystemExit(main())
