from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from app.schemas.dataset import CANONICAL_DATASET_COLUMNS, NUMERIC_CANONICAL_COLUMNS
from app.services.descriptors import DescriptorCalculator, InvalidStructureError


ALIASES = {
    "name": "compound_name",
    "compound": "compound_name",
    "compound name": "compound_name",
    "SMILES": "smiles",
    "canonicalsmiles": "canonical_smiles",
    "inchi_key": "inchikey",
    "InChIKey": "inchikey",
    "dataset_source": "source_dataset",
    "source": "source_dataset",
    "column": "column_name",
    "stationary_phase": "column_chemistry",
    "stationary phase": "column_chemistry",
    "phase_type": "stationary_phase_type",
    "pH": "ph",
    "temp": "temperature_c",
    "temperature": "temperature_c",
    "flow": "flow_ml_min",
    "flow_rate_ml_min": "flow_ml_min",
    "injection_volume_ul": "injection_ul",
    "runtime_min": "total_runtime_min",
    "initial_percent_b": "initial_organic_pct",
    "final_percent_b": "final_organic_pct",
    "ionization_mode": "ion_mode",
    "precursor": "precursor_mz",
    "product": "product_mz",
    "rt": "rt_min",
    "retention_time_min": "rt_min",
    "signal_to_noise": "sn_ratio",
}


def normalize_source_frame(frame: pd.DataFrame, source_dataset: str) -> pd.DataFrame:
    """Map an arbitrary supported source export into the canonical nullable schema."""

    normalized = frame.rename(columns={col: ALIASES.get(col, ALIASES.get(str(col).strip(), col)) for col in frame.columns})
    normalized = normalized.copy()
    if "source_dataset" not in normalized:
        normalized["source_dataset"] = source_dataset
    normalized["source_dataset"] = normalized["source_dataset"].fillna(source_dataset).astype(str)

    for column in CANONICAL_DATASET_COLUMNS:
        if column not in normalized:
            normalized[column] = pd.NA

    for column in NUMERIC_CANONICAL_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized["compound_name"] = normalized["compound_name"].astype("string").str.strip()
    normalized["ion_mode"] = normalized["ion_mode"].map(_normalize_ion_mode).fillna("unknown")
    normalized["column_chemistry"] = normalized.apply(_infer_column_chemistry, axis=1)
    normalized["stationary_phase_type"] = normalized.apply(_infer_stationary_phase_type, axis=1)
    normalized = _derive_gradient_fields(normalized)
    normalized = _canonicalize_compounds(normalized)
    normalized["success_flag"] = normalized["success_flag"].where(
        normalized["success_flag"].notna(), True
    )
    normalized["missing_fields_count"] = normalized[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return normalized[CANONICAL_DATASET_COLUMNS]


def assemble_master_dataset(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Combine normalized source frames, deduplicate, and preserve provenance."""

    normalized_frames = []
    for idx, frame in enumerate(frames):
        if frame.empty:
            continue
        source = str(frame.get("source_dataset", pd.Series([f"source_{idx}"])).iloc[0])
        normalized_frames.append(normalize_source_frame(frame, source))
    if not normalized_frames:
        return pd.DataFrame(columns=CANONICAL_DATASET_COLUMNS)

    combined = pd.concat(normalized_frames, ignore_index=True)
    combined["_dedupe_key"] = combined.apply(_dedupe_key, axis=1)
    rows = []
    for _, group in combined.groupby("_dedupe_key", dropna=False, sort=False):
        base = group.iloc[0].copy()
        for column in CANONICAL_DATASET_COLUMNS:
            non_null = group[column].dropna()
            if not non_null.empty:
                base[column] = non_null.iloc[0]
        base["source_dataset"] = ";".join(sorted(set(group["source_dataset"].dropna().astype(str))))
        notes = sorted(set(group["notes"].dropna().astype(str)) - {""})
        if len(group) > 1:
            notes.append(f"deduplicated {len(group)} source rows")
        base["notes"] = "; ".join(notes) if notes else pd.NA
        rows.append(base[CANONICAL_DATASET_COLUMNS])

    master = pd.DataFrame(rows).reset_index(drop=True)
    master["missing_fields_count"] = master[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return master


def assemble_from_paths(source_paths: dict[str, str | Path], output_dir: str | Path = "data/processed") -> pd.DataFrame:
    """Load supported CSV/JSON files, save cleaned intermediates, and return master data."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frames = []
    for source, path in source_paths.items():
        if not path or not Path(path).exists():
            continue
        frame = pd.read_json(path) if Path(path).suffix.lower() == ".json" else pd.read_csv(path)
        clean = normalize_source_frame(frame, source)
        clean.to_csv(output / f"{source.lower()}_cleaned.csv", index=False)
        frames.append(clean)
    master = assemble_master_dataset(frames)
    master.to_csv(output / "master_dataset.csv", index=False)
    return master


def _canonicalize_compounds(frame: pd.DataFrame) -> pd.DataFrame:
    calc = DescriptorCalculator()
    canonical = []
    inchikeys = []
    notes = []
    for _, row in frame.iterrows():
        smiles = row.get("smiles") if pd.notna(row.get("smiles")) else row.get("canonical_smiles")
        note = row.get("notes") if pd.notna(row.get("notes")) else ""
        if pd.isna(smiles) or not str(smiles).strip():
            canonical.append(row.get("canonical_smiles"))
            inchikeys.append(row.get("inchikey"))
            notes.append(_append_note(note, "missing SMILES"))
            continue
        try:
            can, key = calc.canonicalize(str(smiles))
            canonical.append(can)
            inchikeys.append(row.get("inchikey") if pd.notna(row.get("inchikey")) else key)
        except InvalidStructureError:
            canonical.append(row.get("canonical_smiles"))
            inchikeys.append(row.get("inchikey"))
            note = _append_note(note, f"invalid SMILES: {smiles}")
        notes.append(note)
    frame["canonical_smiles"] = canonical
    frame["inchikey"] = inchikeys
    frame["notes"] = notes
    return frame


def _derive_gradient_fields(frame: pd.DataFrame) -> pd.DataFrame:
    if "gradient_profile" in frame:
        frame["gradient_profile"] = frame["gradient_profile"].astype("string")
    duration = frame["gradient_duration_min"].fillna(frame["total_runtime_min"])
    frame["gradient_duration_min"] = duration
    missing_runtime = frame["total_runtime_min"].isna()
    frame.loc[missing_runtime, "total_runtime_min"] = frame.loc[missing_runtime, "gradient_duration_min"]
    return frame


def _normalize_ion_mode(value: object) -> str:
    if pd.isna(value):
        return "unknown"
    text = str(value).strip().lower()
    if text in {"positive", "pos", "+", "esi+", "apci+"}:
        return "positive"
    if text in {"negative", "neg", "-", "esi-", "apci-"}:
        return "negative"
    if text in {"both", "mixed"}:
        return "both"
    return "unknown"


def _infer_column_chemistry(row: pd.Series) -> object:
    existing = row.get("column_chemistry")
    if pd.notna(existing):
        return existing
    column_value = row.get("column_name")
    column = "" if pd.isna(column_value) else str(column_value).upper()
    if "C18" in column:
        return "C18"
    if "PHENYL" in column:
        return "phenyl"
    if "HILIC" in column or "AMIDE" in column:
        return "HILIC"
    return pd.NA


def _infer_stationary_phase_type(row: pd.Series) -> object:
    existing = row.get("stationary_phase_type")
    if pd.notna(existing):
        return existing
    chemistry_value = row.get("column_chemistry")
    chemistry = "" if pd.isna(chemistry_value) else str(chemistry_value).upper()
    if "HILIC" in chemistry:
        return "HILIC"
    if chemistry:
        return "reversed phase"
    return pd.NA


def _dedupe_key(row: pd.Series) -> tuple:
    identity = row.get("inchikey") if pd.notna(row.get("inchikey")) else row.get("canonical_smiles")
    rt = round(float(row["rt_min"]), 2) if pd.notna(row.get("rt_min")) else None
    return (
        identity,
        row.get("column_name"),
        row.get("mobile_phase_a"),
        row.get("mobile_phase_b"),
        row.get("ph"),
        rt,
    )


def _append_note(existing: object, note: str) -> str:
    text = "" if pd.isna(existing) else str(existing)
    return f"{text}; {note}".strip("; ") if text else note
