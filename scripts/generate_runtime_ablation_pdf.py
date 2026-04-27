from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_OUTPUT = REPORTS_DIR / "runtime_leakage_ablation_report.pdf"

INK = "#16212F"
MUTED = "#5C6672"
BLUE = "#246BBA"
TEAL = "#2A9D8F"
AMBER = "#C9822B"
PANEL = "#F3F7FA"
GRID = "#D8E0E8"
ROW_ALT = "#F7FAFC"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    data = _load_data(args.report_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(args.output, data)
    print(f"Wrote runtime ablation PDF: {args.output.resolve()}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Russian PDF for runtime/gradient ablation analysis.")
    parser.add_argument("--report-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _load_data(report_dir: Path) -> dict[str, Any]:
    metrics_path = report_dir / "runtime_ablation_metrics.csv"
    diagnostics_path = report_dir / "runtime_consequence_diagnostics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing runtime ablation metrics: {metrics_path}")
    if not diagnostics_path.exists():
        raise FileNotFoundError(f"Missing runtime diagnostics: {diagnostics_path}")
    return {
        "metrics": pd.read_csv(metrics_path),
        "diagnostics": json.loads(diagnostics_path.read_text(encoding="utf-8")),
    }


def build_pdf(path: Path, data: dict[str, Any]) -> None:
    """Build a concise Russian PDF report for runtime proxy ablation."""

    _setup_matplotlib()
    with PdfPages(path) as pdf:
        fig = _new_page()
        _page_summary(fig, data)
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
            "pdf.fonttype": 42,
        }
    )


def _new_page() -> plt.Figure:
    return plt.figure(figsize=(11.69, 8.27), dpi=150)


def _page_summary(fig: plt.Figure, data: dict[str, Any]) -> None:
    metrics: pd.DataFrame = data["metrics"]
    diagnostics: dict[str, Any] = data["diagnostics"]
    _title(
        fig,
        "Проверка runtime/gradient duration как proxy-признаков RT",
        "Мини-исследование на одинаковой 20k-подвыборке и grouped split по InChIKey",
    )

    cards = [
        ("Строк", diagnostics.get("sample_rows"), "в ablation-подвыборке"),
        ("Train/Test", f"{diagnostics.get('train_rows')}/{diagnostics.get('test_rows')}", "без compound overlap"),
        ("Spearman RT-runtime", _fmt(diagnostics.get("rt_total_runtime_spearman")), "умеренная связь"),
        ("Доля short-stop", _pct(diagnostics.get("target_like_runtime_margin_fraction")), "runtime заканчивается 0-2 мин после RT"),
    ]
    _metric_cards(fig, cards)

    ax_mae = fig.add_axes([0.09, 0.43, 0.40, 0.30])
    ordered = metrics.sort_values("mae", ascending=True)
    _barh(
        ax_mae,
        ordered.set_index("ablation")["mae"].sort_values(ascending=False),
        "RT MAE по ablation-режимам",
        "мин",
        BLUE,
    )

    ax_table = fig.add_axes([0.55, 0.43, 0.39, 0.30])
    table_rows = []
    for _, row in metrics.sort_values("mae").iterrows():
        table_rows.append(
            [
                _label(row["ablation"]),
                f"{row['mae']:.3f}",
                f"{row['rmse']:.3f}",
                f"{row['r2']:.3f}",
                f"{row['spearman']:.3f}",
            ]
        )
    _draw_table(ax_table, ["Режим", "MAE", "RMSE", "R2", "Spearman"], table_rows, [0.34, 0.13, 0.14, 0.12, 0.17])

    ax_diag = fig.add_axes([0.06, 0.08, 0.43, 0.27])
    _panel(ax_diag)
    diag_lines = [
        f"Медианный запас после пика: {_fmt(diagnostics.get('post_peak_margin_median_min'))} мин",
        f"Q10/Q90 запаса: {_fmt(diagnostics.get('post_peak_margin_q10_min'))} / {_fmt(diagnostics.get('post_peak_margin_q90_min'))} мин",
        f"Медиана RT/runtime: {_fmt(diagnostics.get('rt_runtime_fraction_median'))}",
        f"Method-групп проверено: {diagnostics.get('method_group_count')}",
        f"Runtime меняется внутри method key: {_pct(diagnostics.get('within_method_variable_runtime_group_fraction'))}",
    ]
    _panel_text(ax_diag, "Диагностика следствия", diag_lines)

    ax_conclusion = fig.add_axes([0.53, 0.08, 0.41, 0.27])
    _panel(ax_conclusion)
    conclusion_lines = [
        "Удаление обоих runtime-признаков ухудшает MAE с 1.614 до 1.657 мин: эффект есть, но модель не держится только на них.",
        "На публичной подвыборке нет сильного сигнала short-stop leakage: запас после пика обычно большой, а runtime редко меняется внутри похожего method key.",
        "Для внутренних targeted BE-assay данных риск остается: runtime мог быть выбран после scouting run или знания ожидаемого пика.",
        "Рекомендация: показывать full_method и no_runtime_proxy benchmark; в inverse recommendation трактовать runtime как constraint/penalty.",
    ]
    _panel_text(ax_conclusion, "Вывод", conclusion_lines)


def _title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.055, 0.94, title, fontsize=18, fontweight="bold", color=INK)
    fig.text(0.055, 0.905, subtitle, fontsize=9, color=MUTED)


def _metric_cards(fig: plt.Figure, cards: list[tuple[str, object, str]]) -> None:
    left = 0.055
    width = 0.205
    for idx, (title, value, note) in enumerate(cards):
        ax = fig.add_axes([left + idx * (width + 0.018), 0.76, width, 0.10])
        ax.axis("off")
        ax.add_patch(
            FancyBboxPatch(
                (0, 0),
                1,
                1,
                boxstyle="round,pad=0.018,rounding_size=0.03",
                linewidth=0,
                facecolor=PANEL,
                transform=ax.transAxes,
            )
        )
        ax.text(0.07, 0.62, str(value), fontsize=17, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.07, 0.34, title, fontsize=8, color=INK, transform=ax.transAxes)
        ax.text(0.07, 0.13, note, fontsize=6.8, color=MUTED, transform=ax.transAxes)


def _barh(ax: plt.Axes, series: pd.Series, title: str, xlabel: str, color: str) -> None:
    ax.barh(range(len(series)), series.values, color=color, height=0.58)
    ax.set_yticks(range(len(series)))
    ax.set_yticklabels([_label(str(value)) for value in series.index])
    ax.set_title(title, loc="left", fontweight="bold", color=INK)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for idx, value in enumerate(series.values):
        ax.text(value + max(series.values) * 0.015, idx, f"{value:.3f}", va="center", fontsize=7, color=INK)


def _draw_table(ax: plt.Axes, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    ax.axis("off")
    y = 0.94
    row_h = 0.14
    x = 0.0
    for header, width in zip(headers, widths):
        ax.add_patch(plt.Rectangle((x, y - row_h), width, row_h, facecolor="#E7EEF5", edgecolor="white"))
        ax.text(x + 0.01, y - row_h / 2, header, va="center", fontsize=7.5, fontweight="bold", color=INK)
        x += width
    y -= row_h
    for idx, row in enumerate(rows):
        x = 0.0
        face = ROW_ALT if idx % 2 else "white"
        for cell, width in zip(row, widths):
            ax.add_patch(plt.Rectangle((x, y - row_h), width, row_h, facecolor=face, edgecolor="white"))
            ax.text(x + 0.01, y - row_h / 2, str(cell), va="center", fontsize=7.2, color=INK)
            x += width
        y -= row_h


def _panel(ax: plt.Axes) -> None:
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0, 0),
            1,
            1,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            linewidth=0,
            facecolor=PANEL,
            transform=ax.transAxes,
        )
    )


def _panel_text(ax: plt.Axes, title: str, lines: list[str]) -> None:
    ax.text(0.045, 0.88, title, fontsize=11, fontweight="bold", color=INK, transform=ax.transAxes)
    wrapped = []
    for line in lines:
        wrapped.append("• " + textwrap.fill(line, width=65, subsequent_indent="  "))
    ax.text(0.045, 0.74, "\n".join(wrapped), fontsize=7.7, color=INK, va="top", transform=ax.transAxes)


def _label(value: str) -> str:
    return {
        "with_both": "оба признака",
        "without_total_runtime": "без total runtime",
        "without_gradient_duration": "без gradient duration",
        "without_both": "без обоих",
    }.get(value, value)


def _fmt(value: object) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "n/a"


def _pct(value: object) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "n/a"


if __name__ == "__main__":
    raise SystemExit(main())
