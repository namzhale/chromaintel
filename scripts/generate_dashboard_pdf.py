from __future__ import annotations

import argparse
import math
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "chromaintel_dashboard_report.pdf"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODEL_BUNDLE = PROCESSED_DIR / "models" / "trained_forward_bundle.joblib"


@dataclass(frozen=True)
class PdfStyle:
    page_width: int = 842
    page_height: int = 595
    margin: int = 42
    font: str = "F1"
    bold_font: str = "F2"


class SimplePdf:
    """Tiny dependency-free PDF writer for dashboard-style reports."""

    def __init__(self, style: PdfStyle | None = None):
        self.style = style or PdfStyle()
        self.pages: list[list[str]] = []
        self.current: list[str] = []
        self.new_page()

    def new_page(self) -> None:
        if self.current:
            self.pages.append(self.current)
        self.current = []

    def text(self, x: float, y: float, value: str, size: int = 10, bold: bool = False) -> None:
        font = self.style.bold_font if bold else self.style.font
        self.current.append(f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({_pdf_escape(value)}) Tj ET")

    def multiline(self, x: float, y: float, value: str, width_chars: int = 95, size: int = 9, leading: int = 12) -> float:
        line_y = y
        for line in textwrap.wrap(value, width=width_chars) or [""]:
            self.text(x, line_y, line, size=size)
            line_y -= leading
        return line_y

    def rect(self, x: float, y: float, w: float, h: float, color: tuple[float, float, float]) -> None:
        r, g, b = color
        self.current.append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f 0 0 0 rg")

    def line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.current.append(f"0.75 w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def table(self, x: float, y: float, headers: list[str], rows: list[list[str]], widths: list[float], size: int = 8) -> float:
        row_h = 17
        self.rect(x, y - row_h + 4, sum(widths), row_h, (0.90, 0.93, 0.96))
        cursor = x + 4
        for header, width in zip(headers, widths):
            self.text(cursor, y - 8, header, size=size, bold=True)
            cursor += width
        self.line(x, y - row_h + 2, x + sum(widths), y - row_h + 2)
        y -= row_h
        for idx, row in enumerate(rows):
            if idx % 2:
                self.rect(x, y - row_h + 4, sum(widths), row_h, (0.97, 0.98, 0.99))
            cursor = x + 4
            for cell, width in zip(row, widths):
                self.text(cursor, y - 8, str(cell)[: max(int(width / 4.4), 8)], size=size)
                cursor += width
            y -= row_h
        return y

    def bar_chart(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        labels: list[str],
        values: list[float],
        title: str,
        color: tuple[float, float, float] = (0.16, 0.42, 0.67),
        lower_is_better: bool = False,
    ) -> float:
        self.text(x, y, title, size=11, bold=True)
        chart_y = y - 18
        max_value = max(values) if values else 1.0
        max_value = max(max_value, 1e-9)
        bar_h = min(18, (height - 26) / max(len(values), 1))
        for idx, (label, value) in enumerate(zip(labels, values)):
            yy = chart_y - idx * (bar_h + 7)
            self.text(x, yy + 3, label[:22], size=8)
            bar_x = x + 118
            bar_w = (width - 180) * value / max_value
            fill = (0.70, 0.25, 0.25) if lower_is_better and value == max_value else color
            self.rect(bar_x, yy, bar_w, bar_h, fill)
            self.text(bar_x + bar_w + 5, yy + 3, f"{value:.3g}", size=8)
        return chart_y - len(values) * (bar_h + 7) - 8

    def write(self, path: Path) -> None:
        if self.current:
            self.pages.append(self.current)
            self.current = []
        objects: list[bytes] = []
        catalog_id = 1
        pages_id = 2
        font_id = 3
        bold_font_id = 4
        page_ids = []
        content_ids = []
        next_id = 5
        for _ in self.pages:
            page_ids.append(next_id)
            content_ids.append(next_id + 1)
            next_id += 2
        objects.append(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode())
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        for page_id, content_id, commands in zip(page_ids, content_ids, self.pages):
            page = (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {self.style.page_width} {self.style.page_height}] "
                f"/Resources << /Font << /F1 {font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
            stream = "\n".join(commands).encode("latin-1", errors="replace")
            content = b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
            objects.append(page.encode())
            objects.append(content)
        _write_pdf_objects(path, objects)


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
    master = _read_csv(PROCESSED_DIR / "master_dataset.csv")
    matrix = _read_csv(PROCESSED_DIR / "model_matrix.csv")
    source_metrics = _read_csv(REPORTS_DIR / "source_metrics.csv")
    importance = _read_csv(REPORTS_DIR / "feature_importance.csv")
    predictions = _read_csv(REPORTS_DIR / "test_predictions.csv")
    metadata = joblib.load(MODEL_BUNDLE)["metadata"] if MODEL_BUNDLE.exists() else {}
    return {
        "master": master,
        "matrix": matrix,
        "source_metrics": source_metrics,
        "importance": importance,
        "predictions": predictions,
        "metadata": metadata,
    }


def _build_pdf(path: Path, data: dict[str, object]) -> None:
    pdf = SimplePdf()
    _page_summary(pdf, data)
    pdf.new_page()
    _page_models(pdf, data)
    pdf.new_page()
    _page_parameters(pdf, data)
    pdf.new_page()
    _page_roadmap(pdf)
    pdf.write(path)


def _page_summary(pdf: SimplePdf, data: dict[str, object]) -> None:
    master: pd.DataFrame = data["master"]  # type: ignore[assignment]
    matrix: pd.DataFrame = data["matrix"]  # type: ignore[assignment]
    x = pdf.style.margin
    y = pdf.style.page_height - 42
    pdf.text(x, y, "ChromaIntel LC-MS/MS MVP Dashboard", size=20, bold=True)
    y -= 24
    pdf.text(x, y, "Dataset size, model comparison, parameter significance, and development roadmap", size=10)
    y -= 28
    cards = [
        ("Master rows", len(master)),
        ("Model rows", len(matrix)),
        ("Compounds", master["compound_name"].nunique() if "compound_name" in master else 0),
        ("Sources", master["source_dataset"].nunique() if "source_dataset" in master else 0),
    ]
    card_w = 170
    for idx, (label, value) in enumerate(cards):
        cx = x + idx * (card_w + 10)
        pdf.rect(cx, y - 64, card_w, 64, (0.93, 0.96, 0.98))
        pdf.text(cx + 12, y - 24, str(value), size=22, bold=True)
        pdf.text(cx + 12, y - 46, label, size=9)
    y -= 95
    source_counts = master["source_dataset"].value_counts().sort_values(ascending=False) if "source_dataset" in master else pd.Series(dtype=int)
    pdf.bar_chart(x, y, 350, 130, [str(k) for k in source_counts.index], [float(v) for v in source_counts.values], "Rows by source")
    missing = master.isna().mean().sort_values(ascending=False).head(8)
    pdf.bar_chart(x + 420, y, 330, 130, [str(k) for k in missing.index], [float(v) for v in missing.values], "Highest missingness fraction")
    y -= 170
    notes = [
        "Prediction targets: retention time in minutes (rt_min) and provisional peak quality score (quality_score).",
        "Current demo dataset is intentionally small and mixed-source; metrics are diagnostic, not production evidence.",
        "Internal bioanalytical runs with accepted and failed methods are the highest-value next data source.",
    ]
    pdf.text(x, y, "Executive Notes", size=13, bold=True)
    y -= 20
    for note in notes:
        y = pdf.multiline(x, y, f"- {note}", width_chars=115)
        y -= 3


def _page_models(pdf: SimplePdf, data: dict[str, object]) -> None:
    metadata: dict = data["metadata"]  # type: ignore[assignment]
    source_metrics: pd.DataFrame = data["source_metrics"]  # type: ignore[assignment]
    x = pdf.style.margin
    y = pdf.style.page_height - 42
    pdf.text(x, y, "Model Comparison", size=18, bold=True)
    y -= 26
    rt_metrics = pd.DataFrame(metadata.get("rt_metrics", {})).T.reset_index(names="model")
    quality_metrics = pd.DataFrame(metadata.get("quality_metrics", {})).T.reset_index(names="model")
    if not rt_metrics.empty:
        labels = rt_metrics["model"].astype(str).tolist()
        pdf.bar_chart(x, y, 360, 130, labels, rt_metrics["validation_mae"].astype(float).tolist(), "RT validation MAE (lower is better)", lower_is_better=True)
        pdf.bar_chart(x + 420, y, 340, 130, labels, rt_metrics["test_mae"].astype(float).tolist(), "RT test MAE (lower is better)", lower_is_better=True)
    y -= 165
    rows = _metric_rows(rt_metrics, ["model", "validation_mae", "test_mae", "test_r2"])
    y = pdf.table(x, y, ["RT model", "Val MAE", "Test MAE", "Test R2"], rows, [165, 95, 95, 95])
    y -= 20
    q_rows = _metric_rows(quality_metrics, ["model", "validation_mae", "test_mae", "test_r2"])
    y = pdf.table(x, y, ["Quality model", "Val MAE", "Test MAE", "Test R2"], q_rows, [165, 95, 95, 95])
    if not source_metrics.empty:
        pdf.text(x + 520, 235, "Source-wise RT error", size=12, bold=True)
        rows = _metric_rows(source_metrics, ["source_dataset", "n_test", "rt_mae", "mean_bias"])
        pdf.table(x + 520, 215, ["Source", "N", "MAE", "Bias"], rows, [105, 35, 60, 60])
    uncertainty = metadata.get("uncertainty_metadata", {}).get("rt", {})
    pdf.text(x, 70, f"Selected RT model: {metadata.get('best_rt_model', 'n/a')}; selected quality model: {metadata.get('best_quality_model', 'n/a')}", size=10, bold=True)
    pdf.text(x, 52, f"Uncertainty proxy: {uncertainty.get('method', 'n/a')} q90={float(uncertainty.get('q90_min', 0.0)):.3f} min", size=9)


def _page_parameters(pdf: SimplePdf, data: dict[str, object]) -> None:
    importance: pd.DataFrame = data["importance"]  # type: ignore[assignment]
    predictions: pd.DataFrame = data["predictions"]  # type: ignore[assignment]
    x = pdf.style.margin
    y = pdf.style.page_height - 42
    pdf.text(x, y, "Parameter Significance And Validation Detail", size=18, bold=True)
    y -= 28
    top = importance.head(10) if not importance.empty else pd.DataFrame()
    if not top.empty:
        pdf.bar_chart(x, y, 500, 230, top["feature"].astype(str).tolist(), top["importance_mean"].astype(float).tolist(), "Top RT permutation importance")
        rows = _metric_rows(top, ["feature", "feature_group", "importance_mean", "significance"])
        pdf.table(x + 520, y - 10, ["Feature", "Group", "Imp.", "Signal"], rows[:10], [88, 76, 45, 72], size=7)
    y -= 280
    pdf.text(x, y, "Held-out prediction diagnostics", size=13, bold=True)
    y -= 20
    if not predictions.empty:
        mae = predictions["abs_rt_error_min"].mean() if "abs_rt_error_min" in predictions else math.nan
        rmse = (predictions["rt_error_min"].pow(2).mean() ** 0.5) if "rt_error_min" in predictions else math.nan
        ad_flags = int(predictions["ad_flag"].sum()) if "ad_flag" in predictions else 0
        pdf.text(x, y, f"Test rows: {len(predictions)} | RT MAE: {mae:.3f} min | RT RMSE: {rmse:.3f} min | AD flags: {ad_flags}", size=10)
        y -= 22
        rows = _metric_rows(predictions.sort_values("abs_rt_error_min", ascending=False), ["compound_name", "source_dataset", "rt_min", "predicted_rt_min", "abs_rt_error_min"])
        pdf.table(x, y, ["Compound", "Source", "Actual RT", "Pred RT", "Abs Error"], rows, [130, 105, 75, 75, 75])


def _page_roadmap(pdf: SimplePdf) -> None:
    x = pdf.style.margin
    y = pdf.style.page_height - 42
    pdf.text(x, y, "Roadmap", size=18, bold=True)
    y -= 30
    phases = [
        (
            "0-2 weeks: data foundation",
            [
                "Import internal BE-style historical runs with accepted, failed, low-intensity, poor-resolution, and carryover cases.",
                "Expand reviewed public RT samples and preserve source/license/missingness provenance.",
                "Add import preview summaries for invalid rows, duplicate runs, and missing MS/LC fields.",
            ],
        ),
        (
            "2-4 weeks: stronger validation and models",
            [
                "Move from random split to grouped/source holdout by InChIKey, source, and method family.",
                "Evaluate Morgan fingerprints, ExtraTrees, CatBoost/LightGBM/XGBoost when enough rows exist.",
                "Persist applicability-domain ranges and penalize out-of-domain recommendations.",
            ],
        ),
        (
            "1-2 months: recommendation quality",
            [
                "Add score decomposition: RT fit, quality, runtime, confidence, AD penalty.",
                "Make LC search space configurable by lab-approved columns, solvents, pH, flow, temperature, and runtime.",
                "Collect outcome feedback from recommended methods for active learning.",
            ],
        ),
        (
            "2-4 months: SOTA research track",
            [
                "Pretrain or benchmark graph/Transformer structure encoders on METLIN/RepoRT/MCMRT-scale RT data.",
                "Use retention-order objectives where absolute RT does not transfer cleanly between methods.",
                "Add calibrated conformal intervals by matrix, source, column chemistry, and instrument platform.",
            ],
        ),
    ]
    for title, bullets in phases:
        pdf.text(x, y, title, size=12, bold=True)
        y -= 17
        for bullet in bullets:
            y = pdf.multiline(x + 12, y, f"- {bullet}", width_chars=115, size=9)
            y -= 2
        y -= 12
    pdf.text(x, 45, "Decision gate: do not claim production readiness until internal data volume, grouped validation, and lab acceptance criteria are in place.", size=9, bold=True)


def _metric_rows(frame: pd.DataFrame, columns: list[str]) -> list[list[str]]:
    if frame.empty:
        return []
    rows = []
    for _, row in frame.iterrows():
        cells = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                cells.append(f"{value:.3f}")
            else:
                cells.append(str(value))
        rows.append(cells)
    return rows


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _pdf_escape(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_pdf_objects(path: Path, objects: list[bytes]) -> None:
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode())
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    path.write_bytes(output)


if __name__ == "__main__":
    raise SystemExit(main())
