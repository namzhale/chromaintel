"""Offline-first parser for LC-MS/MS method snippets from papers and abstracts.

The parser is deliberately conservative: it extracts only high-confidence method
entities from user-provided text/CSV snippets and maps them into the canonical
training schema. Optional LLM extraction can be layered on top later without
changing the normalized output contract.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from app.schemas.dataset import CANONICAL_DATASET_COLUMNS


TEXT_COLUMNS = ["title", "abstract", "snippet", "text", "methods", "description"]


def load_snippets(paths: Iterable[str | Path]) -> list[str]:
    """Load plain-text snippets or concatenate useful text columns from tables."""

    snippets: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.suffix.lower() in {".csv", ".tsv", ".tab"}:
            sep = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
            frame = pd.read_csv(path, sep=sep)
            columns = [column for column in TEXT_COLUMNS if column in frame.columns]
            if not columns:
                columns = list(frame.columns[: min(3, len(frame.columns))])
            for _, row in frame[columns].fillna("").iterrows():
                text = "\n".join(str(row[column]).strip() for column in columns if str(row[column]).strip())
                if text:
                    snippets.append(text)
        else:
            text = path.read_text(encoding="utf-8")
            if text.strip():
                snippets.append(text.strip())
    return snippets


def extract_lcms_records(snippets: Iterable[str], source_name: str) -> list[dict[str, Any]]:
    """Extract canonical LC-MS/MS fields from method text snippets."""

    records = []
    for index, snippet in enumerate(snippets, start=1):
        record = _empty_record(source_name, index)
        record.update(_extract_compound(snippet))
        record.update(_extract_column(snippet))
        record.update(_extract_mobile_phases(snippet))
        record.update(_extract_gradient(snippet))
        record.update(_extract_conditions(snippet))
        record.update(_extract_ms_transition(snippet))
        record.update(_extract_rt(snippet))
        record["notes"] = "offline regex parser; review before training use"
        records.append(record)
    return records


def normalize_literature_records(records: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Return literature extraction records as a canonical nullable dataframe."""

    frame = pd.DataFrame(records).reindex(columns=CANONICAL_DATASET_COLUMNS)
    if frame.empty:
        return frame
    frame["missing_fields_count"] = frame[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return frame


def _empty_record(source_name: str, index: int) -> dict[str, Any]:
    return {
        column: pd.NA for column in CANONICAL_DATASET_COLUMNS
    } | {
        "source_dataset": f"literature:{source_name}",
        "source_record_id": f"{source_name}:{index}",
        "matrix": "literature",
        "success_flag": True,
    }


def _extract_compound(text: str) -> dict[str, Any]:
    match = re.search(r"\b([A-Z][A-Za-z0-9\-]+)\s+(?:was|were|on|retention|RT\b)", text)
    if not match:
        match = re.search(r"\b([A-Z][A-Za-z0-9\-]+)\b.*?\bRT\b", text, flags=re.IGNORECASE)
    return {"compound_name": match.group(1) if match else pd.NA}


def _extract_column(text: str) -> dict[str, Any]:
    column_match = re.search(
        r"(?:on|using)\s+(?:a\s+)?([A-Za-z0-9\-\s]+?(?:C18|T3|Phenyl[-\s]?Hexyl|HILIC|Amide))\s+column",
        text,
        flags=re.IGNORECASE,
    )
    if not column_match:
        column_match = re.search(r"\bon\s+((?:C18|T3|HILIC|Amide|Phenyl[-\s]?Hexyl))\s+column", text, flags=re.IGNORECASE)
    column_name = _clean(column_match.group(1)) if column_match else pd.NA
    chemistry = pd.NA
    phase = pd.NA
    upper = str(column_name).upper()
    if "C18" in upper or "T3" in upper:
        chemistry = "C18"
        phase = "reversed phase"
    elif "PHENYL" in upper:
        chemistry = "phenyl"
        phase = "reversed phase"
    elif "HILIC" in upper or "AMIDE" in upper:
        chemistry = "HILIC"
        phase = "HILIC"
    return {
        "column_name": column_name,
        "column_chemistry": chemistry,
        "stationary_phase_type": phase,
    }


def _extract_mobile_phases(text: str) -> dict[str, Any]:
    a_match = re.search(
        r"mobile phase A (?:was|is)?\s*(.*?)(?:\s+and\s+mobile phase B|\s*,\s*B\b|$)",
        text,
        flags=re.IGNORECASE,
    )
    b_match = re.search(
        r"mobile phase B (?:was|is)?\s*(.*?)(?=(?:\.\s+(?:The|Gradient|Injection|ESI|MRM)\b)|$)",
        text,
        flags=re.IGNORECASE,
    )
    if not a_match:
        a_match = re.search(r"\bA\s+([^,.;]+)", text, flags=re.IGNORECASE)
    if not b_match:
        b_match = re.search(r"\bB\s+([^,.;]+)", text, flags=re.IGNORECASE)
    return {
        "mobile_phase_a": _clean(a_match.group(1)) if a_match else pd.NA,
        "mobile_phase_b": _clean(b_match.group(1)) if b_match else pd.NA,
    }


def _extract_gradient(text: str) -> dict[str, Any]:
    match = re.search(
        r"from\s+(\d+(?:\.\d+)?)\s*%\s*B\s+to\s+(\d+(?:\.\d+)?)\s*%\s*B\s+over\s+(\d+(?:\.\d+)?)\s*min",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return {}
    initial, final, duration = (float(match.group(i)) for i in range(1, 4))
    return {
        "initial_organic_pct": _int_if_whole(initial),
        "final_organic_pct": _int_if_whole(final),
        "gradient_duration_min": _int_if_whole(duration),
        "total_runtime_min": _int_if_whole(duration),
        "gradient_profile": f"0 min {initial:g}%B; {duration:g} min {final:g}%B",
    }


def _extract_conditions(text: str) -> dict[str, Any]:
    flow = _first_float(r"(\d+(?:\.\d+)?)\s*mL/min", text)
    temperature = _first_float(r"(\d+(?:\.\d+)?)\s*(?:C|deg C)\b", text)
    injection = _first_float(r"(\d+(?:\.\d+)?)\s*uL", text)
    ph = _first_float(r"\bpH\s*(\d+(?:\.\d+)?)", text)
    return {
        "flow_ml_min": flow if flow is not None else pd.NA,
        "temperature_c": _int_if_whole(temperature) if temperature is not None else pd.NA,
        "injection_ul": _int_if_whole(injection) if injection is not None else pd.NA,
        "ph": ph if ph is not None else pd.NA,
    }


def _extract_ms_transition(text: str) -> dict[str, Any]:
    mode = "positive" if re.search(r"(ESI\+|\bpositive\b)", text, flags=re.IGNORECASE) else pd.NA
    if pd.isna(mode) and re.search(r"(ESI-|\bnegative\b)", text, flags=re.IGNORECASE):
        mode = "negative"
    transition = re.search(r"(\d+(?:\.\d+)?)\s*(?:>|to)\s*(\d+(?:\.\d+)?)", text)
    return {
        "ion_mode": mode,
        "precursor_mz": float(transition.group(1)) if transition else pd.NA,
        "product_mz": float(transition.group(2)) if transition else pd.NA,
    }


def _extract_rt(text: str) -> dict[str, Any]:
    rt = _first_float(r"(?:retention time|RT|rt)\s*(?:was|=|:)?\s*(\d+(?:\.\d+)?)\s*min", text)
    return {"rt_min": rt if rt is not None else pd.NA}


def _first_float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" .,:;")


def _int_if_whole(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value
