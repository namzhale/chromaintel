from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DIRECT_TARGETS = [
    "rt_min",
    "quality_score",
    "asymmetry",
    "tailing_factor",
    "peak_width_base_min",
    "peak_width_half_height_min",
    "resolution",
    "sn_ratio",
    "peak_area",
    "peak_height",
]

DERIVED_RISK_TARGETS = [
    "low_intensity_risk",
    "poor_resolution_risk",
    "asymmetry_risk",
    "broad_peak_risk",
    "void_or_unretained_risk",
    "late_elution_risk",
]

MEASURED_TARGETS = {"rt_min"}
PROXY_TARGETS = {"quality_score", *DERIVED_RISK_TARGETS}


def build_target_coverage_matrix(frame: pd.DataFrame, sparse_threshold: int = 10) -> pd.DataFrame:
    """Summarize label coverage and training readiness for direct and proxy targets."""

    total_rows = int(len(frame))
    rows: list[dict[str, Any]] = []
    for target in [*DIRECT_TARGETS, *DERIVED_RISK_TARGETS]:
        available = int(frame[target].notna().sum()) if target in frame else 0
        if target in MEASURED_TARGETS and available:
            label_source = "measured"
        elif target in PROXY_TARGETS:
            label_source = "derived_proxy"
        elif available:
            label_source = "measured"
        else:
            label_source = "unavailable"

        if target in DERIVED_RISK_TARGETS:
            readiness = "proxy_only"
            train_action = "derive transparent risk proxy; do not claim measured peak label"
        elif available >= sparse_threshold:
            readiness = "trainable"
            train_action = "train supervised baseline"
        elif available > 0:
            readiness = "sparse"
            train_action = "report coverage; skip full model until more labels exist"
        else:
            readiness = "unavailable"
            train_action = "skip; collect internal lab labels"

        rows.append(
            {
                "target": target,
                "available_rows": available,
                "total_rows": total_rows,
                "coverage_fraction": available / total_rows if total_rows else 0.0,
                "label_source": label_source,
                "readiness": readiness,
                "train_action": train_action,
            }
        )
    return pd.DataFrame(rows)


def write_target_readiness_reports(
    frame: pd.DataFrame,
    report_dir: str | Path,
) -> dict[str, Path]:
    """Write target coverage CSV and a concise markdown readiness report."""

    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    coverage = build_target_coverage_matrix(frame)
    coverage_csv = reports / "target_coverage_matrix.csv"
    readiness_md = reports / "peak_metric_target_readiness.md"
    coverage.to_csv(coverage_csv, index=False)
    readiness_md.write_text(_readiness_markdown(coverage), encoding="utf-8")
    return {"coverage_csv": coverage_csv, "readiness_md": readiness_md}


def target_label_sources_for_row(row: dict[str, Any]) -> dict[str, str]:
    """Return per-target label-source metadata for DL/inverse manifests."""

    label_sources: dict[str, str] = {}
    for target in DIRECT_TARGETS:
        value = row.get(target)
        if pd.notna(value):
            label_sources[target] = "derived_proxy" if target == "quality_score" else "measured"
        else:
            label_sources[target] = "unavailable"
    for target in DERIVED_RISK_TARGETS:
        label_sources[target] = "derived_proxy"
    return label_sources


def _readiness_markdown(coverage: pd.DataFrame) -> str:
    lines = [
        "# Peak Metric Target Readiness",
        "",
        "This report separates measured labels from provisional or derived proxy targets.",
        "",
        "| Target | Available rows | Coverage | Label source | Readiness | Action |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for _, row in coverage.iterrows():
        lines.append(
            "| {target} | {available_rows} | {coverage:.3f} | {label_source} | {readiness} | {action} |".format(
                target=row["target"],
                available_rows=int(row["available_rows"]),
                coverage=float(row["coverage_fraction"]),
                label_source=row["label_source"],
                readiness=row["readiness"],
                action=row["train_action"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `rt_min` is the primary supervised target.",
            "- Public RT datasets usually lack measured asymmetry, width, resolution, S/N, and intensity labels.",
            "- Derived risk targets are useful for MVP ranking but must be shown as provisional until internal lab outcomes are available.",
        ]
    )
    return "\n".join(lines) + "\n"
