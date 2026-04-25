from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.dataset_assembly import assemble_master_dataset, normalize_source_frame
from app.services.feature_engineering import build_model_matrix
from app.services.internal_validation import write_internal_templates


DEFAULT_SOURCE = PROJECT_ROOT / "data" / "mock_training_records.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
DEFAULT_BULK_SOURCE = DEFAULT_OUTPUT_DIR / "external_report_bulk_5k.csv"


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


def assemble_dataset(
    source_path: str | Path = DEFAULT_SOURCE,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    templates_dir: str | Path = DEFAULT_TEMPLATES_DIR,
    additional_sources: list[str | Path] | None = None,
) -> AssemblyOutputs:
    """Build and persist the canonical master dataset plus model matrix."""

    source = Path(source_path)
    output = Path(output_dir)
    templates = Path(templates_dir)

    if not source.exists():
        raise FileNotFoundError(f"Source training records not found: {source}")

    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(source)
    normalized = normalize_source_frame(raw, source_dataset=source.stem)
    frames = [normalized]
    resolved_additional_sources = _default_additional_sources(output, additional_sources)
    for extra_source in resolved_additional_sources:
        extra_path = Path(extra_source)
        if not extra_path.exists():
            raise FileNotFoundError(f"Additional source not found: {extra_path}")
        extra = pd.read_csv(extra_path)
        source_label = (
            str(extra["source_dataset"].dropna().iloc[0])
            if "source_dataset" in extra and not extra["source_dataset"].dropna().empty
            else extra_path.stem
        )
        frames.append(normalize_source_frame(extra, source_dataset=source_label))
    master = assemble_master_dataset(frames)
    model_matrix = build_model_matrix(master)
    template_paths = {
        key: Path(path) for key, path in write_internal_templates(templates).items()
    }

    master_path = output / "master_dataset.csv"
    model_matrix_path = output / "model_matrix.csv"
    master.to_csv(master_path, index=False)
    model_matrix.to_csv(model_matrix_path, index=False)

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
        "--additional-source",
        type=Path,
        action="append",
        default=None,
        help="Additional normalized/canonical CSV source to merge into the master dataset.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    outputs = assemble_dataset(args.source, args.output_dir, args.templates_dir, args.additional_source)

    print("LC-MS/MS dataset assembly complete")
    print(f"Source CSV: {outputs.source_path.resolve()} ({outputs.source_rows} rows)")
    print(f"Additional source rows: {outputs.additional_source_rows}")
    print(f"Master dataset: {outputs.master_path.resolve()} ({outputs.master_rows} rows)")
    print(
        "Model matrix: "
        f"{outputs.model_matrix_path.resolve()} "
        f"({outputs.model_matrix_rows} rows x {outputs.model_matrix_columns} columns)"
    )
    for label, path in outputs.template_paths.items():
        print(f"Internal template {label}: {path.resolve()}")
    return 0


def _default_additional_sources(output_dir: Path, additional_sources: list[str | Path] | None) -> list[str | Path]:
    if additional_sources is not None:
        return additional_sources
    default_bulk = output_dir / DEFAULT_BULK_SOURCE.name
    return [default_bulk] if default_bulk.exists() else []


if __name__ == "__main__":
    raise SystemExit(main())
