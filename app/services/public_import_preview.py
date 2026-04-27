from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROCESSED_IMPORT_PATTERNS = ("external_*.csv", "literature_extracted*.csv")
CANONICAL_PREVIEW_FIELDS = [
    "compound_name",
    "canonical_smiles",
    "inchikey",
    "source_dataset",
    "column_name",
    "column_chemistry",
    "stationary_phase_type",
    "mobile_phase_a",
    "mobile_phase_b",
    "ph",
    "gradient_profile",
    "initial_organic_pct",
    "final_organic_pct",
    "gradient_duration_min",
    "total_runtime_min",
    "temperature_c",
    "flow_ml_min",
    "injection_ul",
    "ion_mode",
    "precursor_mz",
    "product_mz",
    "rt_min",
    "matrix",
]


@dataclass(frozen=True)
class ProcessedImportPreview:
    """Small, GUI-safe summary for processed public/literature import CSVs."""

    path: Path
    row_count: int
    column_count: int
    source_counts: dict[str, int]
    canonical_coverage: dict[str, float]
    missingness: list[dict[str, Any]]
    example_rows: pd.DataFrame


def discover_processed_imports(processed_dir: str | Path) -> list[Path]:
    """Return processed public/literature import CSV files in stable display order."""

    root = Path(processed_dir)
    paths: list[Path] = []
    for pattern in PROCESSED_IMPORT_PATTERNS:
        paths.extend(root.glob(pattern))
    excluded = {"external_kaggle_metlin_descriptors_descriptors.csv"}
    unique = {path.resolve(): path for path in paths if path.is_file() and path.name not in excluded}
    return sorted(unique.values(), key=lambda path: (0 if path.name.startswith("external_") else 1, path.name))


def preview_processed_import(path: str | Path, sample_rows: int = 25) -> ProcessedImportPreview:
    """Read a processed import CSV and summarize provenance, canonical coverage, and missingness."""

    csv_path = Path(path)
    frame = pd.read_csv(csv_path, low_memory=False)
    source_counts = _source_counts(frame)
    canonical_coverage = {
        field: _coverage(frame, field)
        for field in CANONICAL_PREVIEW_FIELDS
        if field in frame.columns
    }
    missingness = _missingness(frame)
    return ProcessedImportPreview(
        path=csv_path,
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        source_counts=source_counts,
        canonical_coverage=canonical_coverage,
        missingness=missingness,
        example_rows=frame.head(sample_rows).copy(),
    )


def _source_counts(frame: pd.DataFrame) -> dict[str, int]:
    for column in ("source_dataset", "dataset_source", "source_name", "source"):
        if column in frame.columns:
            return {str(source): int(count) for source, count in frame[column].value_counts(dropna=False).items()}
    return {}


def _coverage(frame: pd.DataFrame, field: str) -> float:
    if field not in frame.columns or frame.empty:
        return 0.0
    return float(frame[field].notna().mean())


def _missingness(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for field in frame.columns:
        missing_count = int(frame[field].isna().sum())
        rows.append(
            {
                "field": field,
                "missing_count": missing_count,
                "missing_fraction": round(missing_count / max(len(frame), 1), 3),
            }
        )
    return sorted(rows, key=lambda row: (-int(row["missing_count"]), str(row["field"])))
