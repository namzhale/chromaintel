from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.graph_optional import detect_graph_availability
from app.models.transformer_embeddings import detect_encoder_availability
from app.schemas.dataset import CANONICAL_DATASET_COLUMNS, NUMERIC_CANONICAL_COLUMNS
from app.services.dataset_assembly import ALIASES
from app.services.descriptors import DescriptorCalculator, InvalidStructureError
from app.services.target_readiness import target_label_sources_for_row


DEFAULT_INPUTS = [
    PROJECT_ROOT / "data" / "processed" / "master_dataset.csv",
]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "dl"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports" / "benchmarks"
SPLIT_COLUMNS = ("split", "split_label", "data_split")
SPLIT_LABELS = ("train", "validation", "test")
SPLIT_FRACTIONS = (0.8, 0.1, 0.1)

DL_BASE_COLUMNS = [
    "canonical_smiles",
    "inchikey",
    "source_dataset",
    "source_record_id",
    "compound_name",
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
    "matrix",
    "rt_min",
    "quality_score",
    "asymmetry",
    "tailing_factor",
    "resolution",
    "sn_ratio",
    "peak_area",
    "peak_height",
    "peak_width_base_min",
    "peak_width_half_height_min",
    "target_label_sources_json",
    "split",
]


@dataclass(frozen=True)
class DLDatasetOutputs:
    graph_manifest_path: Path
    transformer_manifest_path: Path
    pairwise_manifest_path: Path
    inverse_manifest_path: Path
    report_path: Path
    input_rows: int
    valid_rows: int
    filtered_invalid_smiles: int
    pairwise_pairs: int
    split_strategy: str
    max_rows: int | None
    input_paths: list[str]


def prepare_dl_datasets(
    input_paths: Iterable[str | Path] | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    reports_dir: str | Path = DEFAULT_REPORTS_DIR,
    max_rows: int | None = None,
    split_seed: int = 42,
    encoder_family: str = "chemberta",
    pair_delta_rt_min: float = 0.05,
) -> DLDatasetOutputs:
    """Write dependency-light graph and SMILES-transformer dataset manifests."""

    paths = [Path(path) for path in (input_paths or DEFAULT_INPUTS)]
    existing_paths = [path for path in paths if path.exists()]
    if not existing_paths:
        raise FileNotFoundError("No DL dataset input CSVs were found")

    loaded = [_read_source(path) for path in existing_paths]
    combined = pd.concat(loaded, ignore_index=True) if loaded else pd.DataFrame()
    input_rows = int(len(combined))
    prepared, filtered_invalid = build_dl_manifest_frame(combined, max_rows=max_rows, split_seed=split_seed)

    output = Path(output_dir)
    reports = Path(reports_dir)
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    graph_manifest = _graph_manifest(prepared)
    transformer_manifest = _transformer_manifest(prepared, encoder_family=encoder_family)
    pairwise_manifest = _pairwise_retention_order_manifest(prepared, delta_rt_min=pair_delta_rt_min)
    inverse_manifest = _inverse_task_manifest(prepared)
    graph_path = output / "graph_manifest.csv"
    transformer_path = output / "smiles_transformer_manifest.csv"
    pairwise_path = output / "pairwise_retention_order_manifest.csv"
    inverse_path = output / "inverse_task_manifest.csv"
    report_path = reports / "dl_dataset_prep_report.json"

    graph_manifest.to_csv(graph_path, index=False)
    transformer_manifest.to_csv(transformer_path, index=False)
    pairwise_manifest.to_csv(pairwise_path, index=False)
    inverse_manifest.to_csv(inverse_path, index=False)
    split_strategy = _split_strategy(combined)
    report = {
        "status": "prepared",
        "input_paths": [str(path) for path in existing_paths],
        "input_rows": input_rows,
        "valid_rows": int(len(prepared)),
        "filtered_invalid_smiles": filtered_invalid,
        "max_rows": max_rows,
        "split_strategy": split_strategy,
        "split_counts": prepared["split"].value_counts(dropna=False).to_dict(),
        "graph_manifest_path": str(graph_path),
        "transformer_manifest_path": str(transformer_path),
        "pairwise_manifest_path": str(pairwise_path),
        "inverse_manifest_path": str(inverse_path),
        "pairwise_pairs": int(len(pairwise_manifest)),
        "inverse_rows": int(len(inverse_manifest)),
        "graph_availability": detect_graph_availability().backend_status,
        "encoder_availability": detect_encoder_availability(encoder_family).to_metadata(),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return DLDatasetOutputs(
        graph_manifest_path=graph_path,
        transformer_manifest_path=transformer_path,
        pairwise_manifest_path=pairwise_path,
        inverse_manifest_path=inverse_path,
        report_path=report_path,
        input_rows=input_rows,
        valid_rows=int(len(prepared)),
        filtered_invalid_smiles=filtered_invalid,
        pairwise_pairs=int(len(pairwise_manifest)),
        split_strategy=split_strategy,
        max_rows=max_rows,
        input_paths=[str(path) for path in existing_paths],
    )


def build_dl_manifest_frame(
    frame: pd.DataFrame,
    max_rows: int | None = None,
    split_seed: int = 42,
) -> tuple[pd.DataFrame, int]:
    """Normalize canonical fields, filter invalid SMILES, and assign splits."""

    if max_rows is not None and max_rows < 0:
        raise ValueError("max_rows must be non-negative")

    standardized = _standardize_columns(frame)
    if max_rows is not None:
        standardized = standardized.head(max_rows)
    valid_rows: list[dict[str, Any]] = []
    invalid_count = 0
    calc = DescriptorCalculator()
    for _, row in standardized.iterrows():
        record = row.to_dict()
        smiles = _first_text(record.get("canonical_smiles"), record.get("smiles"))
        if smiles is None:
            invalid_count += 1
            continue
        try:
            canonical_smiles, inchikey = calc.canonicalize(smiles)
        except InvalidStructureError:
            invalid_count += 1
            continue
        record["canonical_smiles"] = canonical_smiles
        if _first_text(record.get("inchikey")) is None:
            record["inchikey"] = inchikey
        valid_rows.append(record)

    manifest = pd.DataFrame(valid_rows)
    if manifest.empty:
        return pd.DataFrame(columns=DL_BASE_COLUMNS), invalid_count

    manifest = _assign_splits(manifest, split_seed=split_seed)
    manifest = _deduplicate_manifest(manifest)
    manifest = manifest.sort_values(["canonical_smiles", "source_dataset", "rt_min"], na_position="last")
    for column in DL_BASE_COLUMNS:
        if column not in manifest:
            manifest[column] = pd.NA
    manifest["target_label_sources_json"] = manifest.apply(
        lambda row: json.dumps(target_label_sources_for_row(row.to_dict()), sort_keys=True),
        axis=1,
    )
    return manifest[DL_BASE_COLUMNS].reset_index(drop=True), invalid_count


def _deduplicate_manifest(frame: pd.DataFrame) -> pd.DataFrame:
    key_columns = [
        "canonical_smiles",
        "source_dataset",
        "column_name",
        "mobile_phase_a",
        "mobile_phase_b",
        "gradient_profile",
        "total_runtime_min",
        "rt_min",
    ]
    available = [column for column in key_columns if column in frame.columns]
    return frame.drop_duplicates(subset=available, keep="first") if available else frame


def _read_source(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    if "source_dataset" not in frame:
        frame["source_dataset"] = path.stem
    return frame


def _standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(columns={col: ALIASES.get(col, ALIASES.get(str(col).strip(), col)) for col in frame.columns})
    standardized = renamed.copy()
    for column in [*CANONICAL_DATASET_COLUMNS, "split", "split_label", "data_split"]:
        if column not in standardized:
            standardized[column] = pd.NA
    for column in NUMERIC_CANONICAL_COLUMNS:
        if column in standardized:
            standardized[column] = pd.to_numeric(standardized[column], errors="coerce")
    return standardized


def _assign_splits(frame: pd.DataFrame, split_seed: int) -> pd.DataFrame:
    split_column = _available_split_column(frame)
    assigned = frame.copy()
    if split_column:
        assigned["split"] = assigned[split_column].map(_normalize_split_label)
        missing = assigned["split"].isna()
        if missing.any():
            assigned.loc[missing, "split"] = assigned.loc[missing].apply(
                lambda row: _hash_split(_split_key(row), split_seed),
                axis=1,
            )
        return assigned

    assigned["split"] = assigned.apply(lambda row: _hash_split(_split_key(row), split_seed), axis=1)
    return assigned


def _available_split_column(frame: pd.DataFrame) -> str | None:
    for column in SPLIT_COLUMNS:
        if column in frame and frame[column].notna().any():
            return column
    return None


def _split_strategy(frame: pd.DataFrame) -> str:
    split_column = _available_split_column(frame)
    return f"source_column:{split_column}" if split_column else "deterministic_hash"


def _normalize_split_label(value: object) -> str | None:
    text = _first_text(value)
    if text is None:
        return None
    normalized = text.lower().replace("val", "validation")
    if normalized in {"train", "training"}:
        return "train"
    if normalized in {"validation", "valid", "dev"}:
        return "validation"
    if normalized in {"test", "holdout"}:
        return "test"
    return normalized


def _hash_split(key: str, split_seed: int) -> str:
    digest = hashlib.sha256(f"{split_seed}:{key}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    if bucket < SPLIT_FRACTIONS[0]:
        return SPLIT_LABELS[0]
    if bucket < SPLIT_FRACTIONS[0] + SPLIT_FRACTIONS[1]:
        return SPLIT_LABELS[1]
    return SPLIT_LABELS[2]


def _split_key(row: pd.Series) -> str:
    return _first_text(row.get("inchikey"), row.get("canonical_smiles"), row.get("smiles")) or str(row.name)


def _graph_manifest(frame: pd.DataFrame) -> pd.DataFrame:
    manifest = frame.copy()
    availability = detect_graph_availability()
    manifest["graph_backend"] = "rdkit_numpy"
    manifest["graph_training_enabled"] = False
    manifest["graph_dependency_status"] = "rdkit_available" if availability.rdkit_available else "rdkit_missing"
    return manifest


def _transformer_manifest(frame: pd.DataFrame, encoder_family: str) -> pd.DataFrame:
    manifest = frame.copy()
    availability = detect_encoder_availability(encoder_family)
    manifest["encoder_family"] = availability.encoder_family
    manifest["encoder_model_id"] = availability.model_id
    manifest["encoder_status"] = availability.status
    manifest["encoder_input"] = manifest["canonical_smiles"]
    manifest["method_text"] = manifest.apply(_method_text, axis=1)
    return manifest


def _pairwise_retention_order_manifest(frame: pd.DataFrame, delta_rt_min: float = 0.05) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if frame.empty or "rt_min" not in frame:
        return pd.DataFrame(columns=["compound_i", "compound_j", "method_key", "rt_i", "rt_j", "delta_rt", "order_label", "source_dataset"])
    grouped = frame.dropna(subset=["rt_min"]).groupby(_method_key_columns(frame), dropna=False)
    for method_key, group in grouped:
        sorted_group = group.sort_values("rt_min").head(100)
        records = sorted_group.to_dict("records")
        for i, left in enumerate(records):
            for right in records[i + 1 :]:
                delta = float(right["rt_min"]) - float(left["rt_min"])
                if abs(delta) < delta_rt_min:
                    continue
                rows.append(
                    {
                        "compound_i": left.get("canonical_smiles"),
                        "compound_j": right.get("canonical_smiles"),
                        "inchikey_i": left.get("inchikey"),
                        "inchikey_j": right.get("inchikey"),
                        "method_key": "|".join(map(str, method_key if isinstance(method_key, tuple) else (method_key,))),
                        "rt_i": float(left["rt_min"]),
                        "rt_j": float(right["rt_min"]),
                        "delta_rt": abs(delta),
                        "order_label": 1,
                        "source_dataset": left.get("source_dataset"),
                    }
                )
                if len(rows) >= 50000:
                    return pd.DataFrame(rows)
    return pd.DataFrame(rows)


def _inverse_task_manifest(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in frame.dropna(subset=["rt_min"]).iterrows():
        record = row.to_dict()
        rows.append(
            {
                "compound_name": record.get("compound_name"),
                "canonical_smiles": record.get("canonical_smiles"),
                "inchikey": record.get("inchikey"),
                "source_dataset": record.get("source_dataset"),
                "target_rt_min": record.get("rt_min"),
                "desired_quality_min": 0.65,
                "max_runtime_min": record.get("total_runtime_min"),
                "candidate_column_name": record.get("column_name"),
                "candidate_method_text": _method_text(row),
                "observed_quality_score": record.get("quality_score"),
                "label_source": "observed_method_proxy",
            }
        )
    return pd.DataFrame(rows)


def _method_text(row: pd.Series) -> str:
    parts = [
        f"column={row.get('column_name', 'unknown')}",
        f"mobile_a={row.get('mobile_phase_a', 'unknown')}",
        f"mobile_b={row.get('mobile_phase_b', 'unknown')}",
        f"pH={row.get('ph', 'unknown')}",
        f"flow={row.get('flow_ml_min', 'unknown')} mL/min",
        f"temp={row.get('temperature_c', 'unknown')} C",
        f"runtime={row.get('total_runtime_min', 'unknown')} min",
    ]
    return "; ".join(parts)


def _method_key_columns(frame: pd.DataFrame) -> list[str]:
    candidates = ["source_dataset", "column_name", "mobile_phase_a", "mobile_phase_b", "total_runtime_min"]
    return [column for column in candidates if column in frame.columns]


def _first_text(*values: object) -> str | None:
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare dependency-light graph and SMILES-transformer manifests."
    )
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        default=None,
        help="Input canonical/model CSV. May be supplied multiple times. Defaults to known processed sources.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--encoder-family", default="chemberta")
    parser.add_argument("--pair-delta-rt-min", type=float, default=0.05)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    outputs = prepare_dl_datasets(
        input_paths=args.input,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        max_rows=args.max_rows,
        split_seed=args.split_seed,
        encoder_family=args.encoder_family,
        pair_delta_rt_min=args.pair_delta_rt_min,
    )
    print("DL dataset preparation complete")
    print(f"Input rows: {outputs.input_rows}")
    print(f"Valid rows: {outputs.valid_rows}")
    print(f"Filtered invalid/missing SMILES: {outputs.filtered_invalid_smiles}")
    print(f"Split strategy: {outputs.split_strategy}")
    print(f"Graph manifest: {outputs.graph_manifest_path.resolve()}")
    print(f"SMILES transformer manifest: {outputs.transformer_manifest_path.resolve()}")
    print(f"Pairwise manifest: {outputs.pairwise_manifest_path.resolve()} ({outputs.pairwise_pairs} pairs)")
    print(f"Inverse manifest: {outputs.inverse_manifest_path.resolve()}")
    print(f"Report: {outputs.report_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
