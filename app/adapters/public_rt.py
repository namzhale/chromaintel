from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app.schemas.dataset import CANONICAL_DATASET_COLUMNS
from app.services.dataset_assembly import normalize_source_frame


DEFAULT_DUPLICATE_KEY = (
    "compound_name",
    "canonical_smiles",
    "column_name",
    "rt_min",
)


@dataclass(frozen=True)
class PublicRTAdapterConfig:
    source_name: str
    column_map: dict[str, str]
    required_columns: tuple[str, ...]
    provenance_url: str
    license_note: str
    missingness_notes: tuple[str, ...]
    defaults: dict[str, Any] = field(default_factory=dict)
    duplicate_key: tuple[str, ...] = DEFAULT_DUPLICATE_KEY


PUBLIC_RT_ADAPTERS: dict[str, PublicRTAdapterConfig] = {
    "PredRet": PublicRTAdapterConfig(
        source_name="PredRet",
        column_map={
            "Name": "compound_name",
            "SMILES": "smiles",
            "InChIKey": "inchikey",
            "RT": "rt_min",
            "Column": "column_name",
            "Stationary Phase": "column_chemistry",
            "Mobile A": "mobile_phase_a",
            "Mobile B": "mobile_phase_b",
            "pH": "ph",
            "Gradient": "gradient_profile",
            "Initial B": "initial_organic_pct",
            "Final B": "final_organic_pct",
            "Runtime": "total_runtime_min",
            "Temperature": "temperature_c",
            "Flow": "flow_ml_min",
            "Source ID": "source_record_id",
        },
        required_columns=("Name", "RT"),
        provenance_url="https://predret.org/",
        license_note="Use reviewed local exports only; verify redistribution terms before publishing raw data.",
        missingness_notes=("MS transitions", "peak quality metrics", "sample matrix"),
        defaults={"matrix": "reference", "success_flag": True, "ion_mode": "unknown"},
    ),
    "GMCRT": PublicRTAdapterConfig(
        source_name="GMCRT",
        column_map={
            "compound_name": "compound_name",
            "smiles": "smiles",
            "retention_time_min": "rt_min",
            "column_name": "column_name",
            "mobile_phase_a": "mobile_phase_a",
            "mobile_phase_b": "mobile_phase_b",
            "gradient_profile": "gradient_profile",
            "method_id": "source_record_id",
        },
        required_columns=("compound_name", "retention_time_min"),
        provenance_url="manual_reviewed_export:GMCRT",
        license_note="Manual fixture adapter only; verify original dataset license and citation before ingestion.",
        missingness_notes=("InChIKey", "full method metadata", "MS transitions", "peak quality metrics"),
        defaults={"matrix": "reference", "success_flag": True, "ion_mode": "unknown"},
    ),
    "MultiConditionRT": PublicRTAdapterConfig(
        source_name="MultiConditionRT",
        column_map={
            "compound": "compound_name",
            "canonical_smiles": "canonical_smiles",
            "rt_min": "rt_min",
            "column": "column_name",
            "phase_type": "stationary_phase_type",
            "organic_start": "initial_organic_pct",
            "organic_end": "final_organic_pct",
            "total_runtime_min": "total_runtime_min",
            "temperature_c": "temperature_c",
            "flow_rate_ml_min": "flow_ml_min",
            "condition_id": "source_record_id",
        },
        required_columns=("compound", "rt_min", "condition_id"),
        provenance_url="manual_reviewed_export:MultiConditionRT",
        license_note="Manual fixture adapter only; ingest local reviewed tables, not bulk live downloads.",
        missingness_notes=("InChIKey", "mobile phase composition", "MS transitions", "peak quality metrics"),
        defaults={"matrix": "reference", "success_flag": True, "ion_mode": "unknown"},
    ),
}


def load_public_rt_records(path: str | Path, source_name: str) -> pd.DataFrame:
    """Load a reviewed local public RT fixture/export into the canonical schema."""

    config = _adapter_config(source_name)
    raw = _read_table(Path(path))
    missing = [column for column in config.required_columns if column not in raw.columns]
    if missing:
        raise ValueError(f"{source_name} fixture is missing configured columns: {missing}")

    prepared = raw.rename(columns=config.column_map).copy()
    for column, value in config.defaults.items():
        if column not in prepared:
            prepared[column] = value
        else:
            prepared[column] = prepared[column].fillna(value)
    prepared["source_dataset"] = source_name
    prepared["notes"] = prepared.get("notes", pd.Series([pd.NA] * len(prepared))).map(
        lambda note: _append_note(
            note,
            (
                f"{source_name} local fixture import; provenance={config.provenance_url}; "
                f"license_note={config.license_note}"
            ),
        )
    )

    normalized = normalize_source_frame(prepared, source_dataset=source_name)
    normalized["missing_fields_count"] = normalized[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return normalized


def summarize_public_rt_records(
    records: pd.DataFrame,
    config: PublicRTAdapterConfig,
) -> dict[str, Any]:
    """Summarize fixture missingness and duplicate rows for audit reports."""

    canonical = records.reindex(columns=CANONICAL_DATASET_COLUMNS)
    duplicate_key = [column for column in config.duplicate_key if column in canonical.columns]
    duplicates = int(canonical.duplicated(subset=duplicate_key, keep="first").sum()) if duplicate_key else 0
    return {
        "source_name": config.source_name,
        "rows": int(len(canonical)),
        "duplicate_rows": duplicates,
        "duplicate_key": "|".join(duplicate_key),
        "missing_by_column": {
            column: int(canonical[column].isna().sum())
            for column in CANONICAL_DATASET_COLUMNS
            if int(canonical[column].isna().sum()) > 0
        },
        "known_missingness": list(config.missingness_notes),
        "provenance_url": config.provenance_url,
        "license_note": config.license_note,
    }


def write_public_rt_report(
    records: pd.DataFrame,
    config: PublicRTAdapterConfig,
    output_path: str | Path,
) -> Path:
    """Write a compact Markdown ingestion report for a fixture/local export."""

    summary = summarize_public_rt_records(records, config)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {config.source_name} fixture ingestion report",
        "",
        f"- Rows: {summary['rows']}",
        f"- Duplicate rows: {summary['duplicate_rows']}",
        f"- Duplicate key: {summary['duplicate_key']}",
        f"- Provenance: {summary['provenance_url']}",
        f"- License note: {summary['license_note']}",
        "",
        "## Known source missingness",
        "",
    ]
    lines.extend(f"- {note}" for note in summary["known_missingness"])
    lines.extend(["", "## Missingness by canonical column", "", "| Column | Missing rows |", "| --- | ---: |"])
    lines.extend(
        f"| {column} | {missing} |"
        for column, missing in sorted(summary["missing_by_column"].items())
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _adapter_config(source_name: str) -> PublicRTAdapterConfig:
    try:
        return PUBLIC_RT_ADAPTERS[source_name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown public RT source {source_name!r}. Available: {sorted(PUBLIC_RT_ADAPTERS)}"
        ) from exc


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".tsv", ".tab"}:
        return pd.read_csv(path, sep="\t")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)


def _append_note(existing: Any, note: str) -> str:
    text = "" if pd.isna(existing) else str(existing).strip()
    return f"{text}; {note}" if text else note
