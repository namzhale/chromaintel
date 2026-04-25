from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.dataset_assembly import (
    SOURCE_PROFILES,
    assemble_master_dataset,
    resolve_external_sources,
    write_dataset_assembly_report,
)
from app.services.feature_engineering import build_model_matrix
from app.services.internal_validation import write_internal_templates


DEFAULT_SOURCE = PROJECT_ROOT / "data" / "mock_training_records.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_BULK_SOURCE = DEFAULT_OUTPUT_DIR / "external_report_bulk_5k.csv"
DEFAULT_MCMRT_SOURCE = DEFAULT_OUTPUT_DIR / "external_mcmrt_supplement.csv"


@dataclass(frozen=True)
class AssemblyOutputs:
    source_path: Path
    master_path: Path
    model_matrix_path: Path
    template_paths: dict[str, Path]
    source_rows: int
    master_rows: int
    model_matrix_rows: int
    model_matrix_columns: int
    additional_source_rows: int
    excluded_source_rows: int
    summary_report_path: Path
    selected_sources: list[str]
    excluded_sources: list[str]
    sidecar_sources: list[str]
    source_row_counts: dict[str, int]


def assemble_dataset(
    source_path: str | Path = DEFAULT_SOURCE,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    templates_dir: str | Path = DEFAULT_TEMPLATES_DIR,
    reports_dir: str | Path = DEFAULT_REPORTS_DIR,
    additional_sources: list[str | Path] | None = None,
    source_profile: str = "default",
) -> AssemblyOutputs:
    """Build and persist the canonical master dataset plus model matrix."""

    source = Path(source_path)
    output = Path(output_dir)
    templates = Path(templates_dir)
    reports = Path(reports_dir)

    if not source.exists():
        raise FileNotFoundError(f"Source training records not found: {source}")

    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(source)
    primary = raw.copy()
    if not _has_source_dataset_input(primary):
        primary["source_dataset"] = source.stem
    frames = [primary]
    selection = resolve_external_sources(
        output,
        profile=source_profile,
        explicit_sources=additional_sources,
    )
    row_counts: dict[str, int] = {source.stem: len(raw)}
    for selected_source in selection.included:
        extra_path = selected_source.path
        extra = pd.read_csv(extra_path)
        row_counts[selected_source.key] = len(extra)
        source_label = (
            str(extra["source_dataset"].dropna().iloc[0])
            if "source_dataset" in extra and not extra["source_dataset"].dropna().empty
            else extra_path.stem
        )
        if not _has_source_dataset_input(extra):
            extra["source_dataset"] = source_label
        frames.append(extra)
    for excluded_source in [*selection.excluded, *selection.sidecars]:
        row_counts[excluded_source.key] = _csv_row_count(excluded_source.path)
    master = assemble_master_dataset(frames)
    model_matrix = build_model_matrix(master)
    template_paths = {
        key: Path(path) for key, path in write_internal_templates(templates).items()
    }

    master_path = output / "master_dataset.csv"
    model_matrix_path = output / "model_matrix.csv"
    summary_report_path = reports / "dataset_assembly_summary.md"
    master.to_csv(master_path, index=False)
    model_matrix.to_csv(model_matrix_path, index=False)
    write_dataset_assembly_report(
        summary_report_path,
        selection,
        row_counts,
        primary_source_label=source.stem,
        primary_source_path=source,
        primary_source_rows=len(raw),
        master_rows=len(master),
        model_matrix_rows=len(model_matrix),
        model_matrix_columns=len(model_matrix.columns),
    )

    return AssemblyOutputs(
        source_path=source,
        master_path=master_path,
        model_matrix_path=model_matrix_path,
        template_paths=template_paths,
        source_rows=len(raw),
        master_rows=len(master),
        model_matrix_rows=len(model_matrix),
        model_matrix_columns=len(model_matrix.columns),
        additional_source_rows=sum(len(frame) for frame in frames[1:]),
        excluded_source_rows=sum(row_counts.get(source.key, 0) for source in selection.excluded),
        summary_report_path=summary_report_path,
        selected_sources=[str(source.path) for source in selection.included],
        excluded_sources=[str(source.path) for source in selection.excluded],
        sidecar_sources=[str(source.path) for source in selection.sidecars],
        source_row_counts=row_counts,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assemble the LC-MS/MS master dataset and model matrix."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Input CSV of training records.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for master_dataset.csv and model_matrix.csv.",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=DEFAULT_TEMPLATES_DIR,
        help="Directory for generated internal lab template files.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help="Directory for dataset assembly summary reports.",
    )
    parser.add_argument(
        "--source-profile",
        choices=sorted(SOURCE_PROFILES),
        default="default",
        help=(
            "External source profile. Use default for existing RepoRT/MCMRT behavior, "
            "expanded_ml for ReTiNA + MCMRT + RepoRT + METLIN Figshare, or explicit "
            "with --additional-source."
        ),
    )
    parser.add_argument(
        "--additional-source",
        type=Path,
        action="append",
        default=None,
        help="Additional normalized/canonical CSV source to merge into the master dataset.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_profile = "explicit" if args.additional_source else args.source_profile
    outputs = assemble_dataset(
        args.source,
        args.output_dir,
        args.templates_dir,
        args.reports_dir,
        args.additional_source,
        source_profile,
    )

    print("LC-MS/MS dataset assembly complete")
    print(f"Source CSV: {outputs.source_path.resolve()} ({outputs.source_rows} rows)")
    print(f"Source profile: {source_profile}")
    print(f"Additional source rows: {outputs.additional_source_rows}")
    print(f"Excluded duplicate/sidecar rows: {outputs.excluded_source_rows}")
    print(f"Master dataset: {outputs.master_path.resolve()} ({outputs.master_rows} rows)")
    print(
        "Model matrix: "
        f"{outputs.model_matrix_path.resolve()} "
        f"({outputs.model_matrix_rows} rows x {outputs.model_matrix_columns} columns)"
    )
    print(f"Dataset assembly report: {outputs.summary_report_path.resolve()}")
    for label, path in outputs.template_paths.items():
        print(f"Internal template {label}: {path.resolve()}")
    return 0


def _default_additional_sources(output_dir: Path, additional_sources: list[str | Path] | None) -> list[str | Path]:
    if additional_sources is not None:
        return additional_sources
    defaults = []
    for candidate in [output_dir / DEFAULT_BULK_SOURCE.name, output_dir / DEFAULT_MCMRT_SOURCE.name]:
        if candidate.exists():
            defaults.append(candidate)
    return defaults


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def _has_source_dataset_input(frame: pd.DataFrame) -> bool:
    source_columns = {"source_dataset", "dataset_source", "source"}
    return any(column in frame.columns for column in source_columns)


if __name__ == "__main__":
    raise SystemExit(main())
