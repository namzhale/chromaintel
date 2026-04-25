from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.dataset import CANONICAL_DATASET_COLUMNS
from app.services.dataset_assembly import normalize_source_frame

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "public_sources"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PUBLIC_SOURCE_MANIFEST = PROJECT_ROOT / "data" / "public_source_manifest.json"

REPORT_BASE = "https://raw.githubusercontent.com/michaelwitting/RepoRT/master/processed_data"
REPORT_API_CONTENTS = "https://api.github.com/repos/michaelwitting/RepoRT/contents/processed_data"
REPORT_DATASET_ID = "0001"
MINIMAL_PUBLIC_RT_COLUMNS = {"compound_name", "rt_min"}
MCMRT_SUPPLEMENT_URL = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41597-024-03780-5/"
    "MediaObjects/41597_2024_3780_MOESM1_ESM.xlsx"
)
MCMRT_ARTICLE_URL = "https://www.nature.com/articles/s41597-024-03780-5"
MCMRT_DATASET_DOI = "https://doi.org/10.57760/sciencedb.15823"

REQUIRED_MANIFEST_FIELDS = {
    "source_name",
    "url",
    "license",
    "expected_fields",
    "adapter_status",
    "known_missingness",
    "ingestion_mode",
}

@dataclass(frozen=True)
class RepoRTFiles:
    metadata: pd.DataFrame
    rtdata: pd.DataFrame
    gradient: pd.DataFrame
    info: pd.DataFrame


def load_public_source_manifest(path: str | Path = PUBLIC_SOURCE_MANIFEST) -> list[dict[str, Any]]:
    """Load and validate the reviewed public-source manifest."""

    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = payload.get("sources", [])
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{manifest_path} must contain a non-empty 'sources' list")
    for index, source in enumerate(sources, start=1):
        missing = REQUIRED_MANIFEST_FIELDS - set(source)
        if missing:
            raise ValueError(f"Manifest source #{index} is missing fields: {sorted(missing)}")
        if not isinstance(source["expected_fields"], list) or not source["expected_fields"]:
            raise ValueError(f"Manifest source #{index} expected_fields must be a non-empty list")
        if not isinstance(source["known_missingness"], list):
            raise ValueError(f"Manifest source #{index} known_missingness must be a list")
    return sources


def fetch_report_sample(
    dataset_id: str = REPORT_DATASET_ID,
    rows: int = 10,
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
) -> Path:
    """Fetch a tiny RepoRT subset and normalize it into the MVP schema."""

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    files = _download_report_files(dataset_id, raw_dir)
    normalized = normalize_report(files, dataset_id, rows)
    output_path = processed_dir / f"external_report_{dataset_id}_sample.csv"
    normalized.to_csv(output_path, index=False)
    return output_path


def fetch_report_bulk(
    target_rows: int = 5000,
    max_datasets: int = 80,
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    output_name: str = "report_bulk",
) -> Path:
    """Fetch enough reviewed RepoRT processed datasets to reach a row target."""

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    failures: list[str] = []
    total_rows = 0
    for dataset_id in list_report_dataset_ids()[:max_datasets]:
        if total_rows >= target_rows:
            break
        try:
            files = _download_report_files(dataset_id, raw_dir)
            remaining = max(target_rows - total_rows, 0)
            normalized = normalize_report(files, dataset_id, rows=remaining)
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError, pd.errors.ParserError) as exc:
            failures.append(f"{dataset_id}:{type(exc).__name__}")
            continue
        if normalized.empty:
            continue
        frames.append(normalized)
        total_rows += len(normalized)

    if not frames:
        raise RuntimeError("No RepoRT datasets could be fetched for the bulk import")

    bulk = pd.concat(frames, ignore_index=True)
    bulk["notes"] = bulk["notes"].map(
        lambda note: _append_note(
            note,
            f"bulk RepoRT import target_rows={target_rows}; skipped={','.join(failures[:20]) or 'none'}",
        )
    )
    bulk["missing_fields_count"] = bulk[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    output_path = processed_dir / f"external_{output_name}.csv"
    bulk.to_csv(output_path, index=False)
    print(
        f"Fetched {len(frames)} RepoRT datasets, {len(bulk)} rows. "
        f"Skipped {len(failures)} datasets."
    )
    if failures:
        print(f"Skipped sample: {', '.join(failures[:10])}")
    return output_path


def list_report_dataset_ids() -> list[str]:
    """List RepoRT processed dataset identifiers from the public GitHub API."""

    with urlopen(REPORT_API_CONTENTS, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    dataset_ids = [
        item["name"]
        for item in payload
        if item.get("type") == "dir" and str(item.get("name", "")).isdigit()
    ]
    return sorted(dataset_ids)


def import_local_public_export(
    path: str | Path,
    source_name: str,
    source_url: str,
    license_note: str,
    rows: int | None = None,
    processed_dir: Path = PROCESSED_DIR,
    output_name: str | None = None,
) -> Path:
    """Normalize a small, user-approved public RT/MS export into the canonical schema.

    This is intentionally local-file based so sources with mixed licenses or bulky raw
    downloads can be reviewed before ingestion.
    """

    processed_dir.mkdir(parents=True, exist_ok=True)
    source_path = Path(path)
    raw = _read_public_table(source_path)
    if rows is not None:
        raw = raw.head(rows)

    normalization_input = _with_normalizer_placeholders(raw)
    normalized = normalize_source_frame(normalization_input, source_dataset=source_name)
    for placeholder_column in ["column_name", "column_chemistry", "stationary_phase_type"]:
        normalized[placeholder_column] = normalized[placeholder_column].mask(
            normalized[placeholder_column].eq(""), pd.NA
        )
    _validate_minimal_public_rt(normalized, source_path)
    normalized["notes"] = normalized["notes"].map(
        lambda note: _append_note(
            note,
            (
                "local public export import; "
                f"source_url={source_url}; license={license_note}; "
                f"source_file={source_path.name}"
            ),
        )
    )
    normalized["missing_fields_count"] = normalized[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)

    safe_name = output_name or _safe_source_name(source_name)
    output_path = processed_dir / f"external_{safe_name}_sample.csv"
    normalized.to_csv(output_path, index=False)
    return output_path


def fetch_mcmrt_supplement(
    rows: int | None = None,
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    output_name: str = "mcmrt_supplement",
    local_xlsx: str | Path | None = None,
) -> Path:
    """Fetch or load the MCMRT supplementary workbook and normalize its 30-method RT matrix."""

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = Path(local_xlsx) if local_xlsx else raw_dir / "mcmrt_supplement.xlsx"
    if local_xlsx is None or not workbook_path.exists():
        content = urlopen(MCMRT_SUPPLEMENT_URL, timeout=60).read()
        workbook_path.write_bytes(content)

    normalized = normalize_mcmrt_workbook(workbook_path, rows=rows)
    output_path = processed_dir / f"external_{output_name}.csv"
    normalized.to_csv(output_path, index=False)
    print(f"Normalized MCMRT supplement to {len(normalized)} rows from {workbook_path}")
    return output_path


def normalize_mcmrt_workbook(path: str | Path, rows: int | None = None) -> pd.DataFrame:
    """Melt the MCMRT supplementary XLSX into the canonical nullable schema."""

    workbook = Path(path)
    compounds = pd.read_excel(workbook, sheet_name="S3")
    methods_raw = pd.read_excel(workbook, sheet_name="S2", header=None)
    rt_matrix = pd.read_excel(workbook, sheet_name="S4")
    method_metadata = _mcmrt_method_metadata(methods_raw)

    compound_columns = {
        _clean_header(column): column for column in compounds.columns
    }
    compounds = compounds.rename(
        columns={
            compound_columns.get("MCMRT Number", "MCMRT\nNumber"): "mcmrt_number",
            compound_columns.get("Compound Name", "Compound \nName"): "compound_name",
            compound_columns.get("Isomeric SMILES", "Isomeric SMILES"): "smiles",
            compound_columns.get("InChI", "InChI"): "inchi",
            compound_columns.get("ESI polarity", "ESI polarity"): "ion_mode",
        }
    )
    rt_matrix = rt_matrix.rename(columns={"Number": "mcmrt_number", "Compound Name": "compound_name"})

    rows_out: list[dict[str, Any]] = []
    rt_columns = [column for column in rt_matrix.columns if str(column).startswith("CM ")]
    for _, rt_row in rt_matrix.iterrows():
        compound = compounds.loc[compounds["mcmrt_number"].eq(rt_row["mcmrt_number"])]
        if compound.empty:
            continue
        compound_row = compound.iloc[0]
        for column in rt_columns:
            rt_value = pd.to_numeric(rt_row[column], errors="coerce")
            if pd.isna(rt_value):
                continue
            method_code, method_name = _mcmrt_method_parts(str(column))
            method = method_metadata.get(method_code, {})
            rows_out.append(
                {
                    "compound_name": compound_row.get("compound_name", rt_row["compound_name"]),
                    "smiles": _clean_text(compound_row.get("smiles")),
                    "canonical_smiles": _clean_text(compound_row.get("smiles")),
                    "inchikey": pd.NA,
                    "source_dataset": f"MCMRT:{method_code}",
                    "source_record_id": f"{int(rt_row['mcmrt_number'])}:{method_code}",
                    "column_name": method.get("column_name"),
                    "column_chemistry": _column_chemistry(method.get("column_name"), pd.NA),
                    "stationary_phase_type": "reversed phase",
                    "mobile_phase_a": method.get("mobile_phase_a"),
                    "mobile_phase_b": method.get("mobile_phase_b"),
                    "ph": pd.NA,
                    "gradient_profile": method.get("gradient_profile"),
                    "initial_organic_pct": method.get("initial_organic_pct"),
                    "final_organic_pct": method.get("final_organic_pct"),
                    "gradient_duration_min": method.get("gradient_duration_min"),
                    "total_runtime_min": method.get("total_runtime_min"),
                    "temperature_c": method.get("temperature_c"),
                    "flow_ml_min": method.get("flow_ml_min"),
                    "injection_ul": pd.NA,
                    "ion_mode": compound_row.get("ion_mode", "unknown"),
                    "precursor_mz": pd.NA,
                    "product_mz": pd.NA,
                    "rt_min": rt_value,
                    "peak_area": pd.NA,
                    "peak_height": pd.NA,
                    "sn_ratio": pd.NA,
                    "tailing_factor": pd.NA,
                    "asymmetry": pd.NA,
                    "resolution": pd.NA,
                    "matrix": "reference",
                    "success_flag": True,
                    "quality_score": pd.NA,
                    "notes": (
                        "MCMRT supplementary workbook import; "
                        f"article={MCMRT_ARTICLE_URL}; dataset={MCMRT_DATASET_DOI}; "
                        f"supplement={MCMRT_SUPPLEMENT_URL}; method={method_code}; "
                        f"lc_method_name={method.get('lc_method_name', method_name)}; "
                        "public source, peak quality/MS transitions not provided"
                    ),
                }
            )

    frame = pd.DataFrame(rows_out).head(rows) if rows is not None else pd.DataFrame(rows_out)
    frame = frame.reindex(columns=CANONICAL_DATASET_COLUMNS)
    frame = normalize_source_frame(frame, source_dataset="MCMRT")
    frame["missing_fields_count"] = frame[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return frame


def normalize_report(files: RepoRTFiles, dataset_id: str, rows: int) -> pd.DataFrame:
    metadata = files.metadata.iloc[0]
    info = files.info.iloc[0]
    rtdata = files.rtdata.head(rows).copy()

    gradient_profile = _gradient_profile(files.gradient)
    gradient_duration = _gradient_duration(files.gradient)
    total_runtime = pd.to_numeric(files.gradient["t [min]"], errors="coerce").max()
    mobile_phase_a = _phase_label(metadata, "A")
    mobile_phase_b = _phase_label(metadata, "B")
    initial_organic = _organic_pct(metadata, "gradient.start")
    final_organic = _organic_pct(metadata, "gradient.end")

    frame = pd.DataFrame(
        {
            "compound_name": rtdata["name"],
            "smiles": rtdata["smiles.std"],
            "canonical_smiles": rtdata["smiles.std"],
            "inchikey": rtdata["inchikey.std"],
            "source_dataset": f"RepoRT:{dataset_id}",
            "source_record_id": rtdata["id"],
            "column_name": metadata.get("column.name"),
            "column_chemistry": _column_chemistry(metadata.get("column.name"), metadata.get("column.usp.code")),
            "stationary_phase_type": "reversed phase" if str(info.get("method.type", "")).upper() == "RP" else pd.NA,
            "mobile_phase_a": mobile_phase_a,
            "mobile_phase_b": mobile_phase_b,
            "ph": _first_numeric(metadata.get("eluent.A.pH"), metadata.get("eluent.B.pH")),
            "gradient_profile": gradient_profile,
            "initial_organic_pct": initial_organic,
            "final_organic_pct": final_organic,
            "gradient_duration_min": gradient_duration,
            "total_runtime_min": total_runtime,
            "temperature_c": metadata.get("column.temperature"),
            "flow_ml_min": metadata.get("column.flowrate"),
            "injection_ul": pd.NA,
            "ion_mode": "unknown",
            "precursor_mz": pd.NA,
            "product_mz": pd.NA,
            "rt_min": rtdata["rt"],
            "peak_area": pd.NA,
            "peak_height": pd.NA,
            "sn_ratio": pd.NA,
            "tailing_factor": pd.NA,
            "asymmetry": pd.NA,
            "resolution": pd.NA,
            "matrix": "reference",
            "success_flag": True,
            "quality_score": pd.NA,
            "notes": (
                "RepoRT processed_data import; license CC-BY-SA-4.0; "
                f"source={info.get('source')}; url={info.get('url')}; "
                "missing MS transitions and peak quality metrics"
            ),
        }
    )

    frame = frame.reindex(columns=CANONICAL_DATASET_COLUMNS)
    frame["missing_fields_count"] = frame[CANONICAL_DATASET_COLUMNS[:-1]].isna().sum(axis=1)
    return frame


def _mcmrt_method_metadata(methods_raw: pd.DataFrame) -> dict[str, dict[str, Any]]:
    methods: dict[str, dict[str, Any]] = {}
    method_columns = [
        column
        for column in range(1, methods_raw.shape[1])
        if str(methods_raw.iat[0, column]).strip().startswith("CM ")
    ]
    for column in method_columns:
        method_code = str(methods_raw.iat[0, column]).strip()
        gradient = _mcmrt_gradient(methods_raw, column)
        methods[method_code] = {
            "lc_method_name": _clean_text(methods_raw.iat[1, column]),
            "column_name": _clean_text(methods_raw.iat[6, column]),
            "temperature_c": _num(methods_raw.iat[9, column]) or pd.NA,
            "mobile_phase_a": _clean_text(methods_raw.iat[11, column]),
            "mobile_phase_b": _clean_text(methods_raw.iat[12, column]),
            "flow_ml_min": gradient.get("flow_ml_min"),
            "gradient_profile": gradient.get("gradient_profile"),
            "initial_organic_pct": gradient.get("initial_organic_pct"),
            "final_organic_pct": gradient.get("final_organic_pct"),
            "gradient_duration_min": gradient.get("gradient_duration_min"),
            "total_runtime_min": gradient.get("total_runtime_min"),
        }
    return methods


def _mcmrt_gradient(methods_raw: pd.DataFrame, column: int) -> dict[str, Any]:
    steps = []
    for row_index in range(14, min(21, len(methods_raw))):
        time_min = pd.to_numeric(methods_raw.iat[row_index, column], errors="coerce")
        flow = pd.to_numeric(methods_raw.iat[row_index, column + 1], errors="coerce") if column + 1 < methods_raw.shape[1] else pd.NA
        percent_b = pd.to_numeric(methods_raw.iat[row_index, column + 2], errors="coerce") if column + 2 < methods_raw.shape[1] else pd.NA
        if pd.isna(time_min) or pd.isna(percent_b):
            continue
        steps.append({"time": float(time_min), "flow": float(flow) if pd.notna(flow) else pd.NA, "b": float(percent_b)})
    if not steps:
        return {}

    b_values = [step["b"] for step in steps]
    max_b = max(b_values)
    max_b_time = next(step["time"] for step in steps if step["b"] == max_b)
    flow_values = [step["flow"] for step in steps if pd.notna(step["flow"])]
    return {
        "gradient_profile": "; ".join(
            f"{step['time']:g}min B{step['b']:g} flow{step['flow'] if pd.notna(step['flow']) else 'NA'}"
            for step in steps
        ),
        "flow_ml_min": float(flow_values[0]) if flow_values else pd.NA,
        "initial_organic_pct": float(b_values[0]),
        "final_organic_pct": float(max_b),
        "gradient_duration_min": float(max_b_time),
        "total_runtime_min": float(max(step["time"] for step in steps)),
    }


def _mcmrt_method_parts(header: str) -> tuple[str, str]:
    parts = []
    for part in header.split("\n"):
        cleaned = _clean_text(part)
        if pd.notna(cleaned):
            parts.append(str(cleaned))
    method_code = parts[0] if parts else header.strip()
    method_name = parts[1] if len(parts) > 1 else method_code
    return method_code, method_name


def _clean_header(value: object) -> str:
    return " ".join(str(value).replace("\n", " ").split())


def _clean_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = " ".join(str(value).replace("\xa0", " ").replace("\n", " ").split())
    return text if text else pd.NA


def _download_report_files(dataset_id: str, raw_dir: Path) -> RepoRTFiles:
    names = {
        "metadata": f"{dataset_id}_metadata.tsv",
        "rtdata": f"{dataset_id}_rtdata_canonical_success.tsv",
        "gradient": f"{dataset_id}_gradient.tsv",
        "info": f"{dataset_id}_info.tsv",
    }
    frames = {}
    for key, name in names.items():
        url = f"{REPORT_BASE}/{dataset_id}/{name}"
        text = _fetch_text(url)
        (raw_dir / f"report_{name}").write_text(text, encoding="utf-8")
        frames[key] = pd.read_csv(StringIO(text), sep="\t")
    return RepoRTFiles(**frames)


def _read_public_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl", ".ndjson"}:
        try:
            return pd.read_json(path, lines=suffix in {".jsonl", ".ndjson"})
        except ValueError:
            return pd.read_json(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".tsv", ".tab"}:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path, sep=None, engine="python")


def _with_normalizer_placeholders(frame: pd.DataFrame) -> pd.DataFrame:
    prepared = frame.copy()
    if "column_name" not in prepared and "column" not in prepared:
        prepared["column_name"] = pd.NA
    for column in ["column_chemistry", "stationary_phase_type"]:
        if column not in prepared:
            prepared[column] = pd.NA
    return prepared


def _validate_minimal_public_rt(frame: pd.DataFrame, path: Path) -> None:
    missing = {
        column
        for column in MINIMAL_PUBLIC_RT_COLUMNS
        if column not in frame or frame[column].isna().all()
    }
    if missing:
        raise ValueError(
            f"{path} does not contain usable public RT rows after normalization; "
            f"missing populated columns: {sorted(missing)}"
        )


def _fetch_text(url: str) -> str:
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def _append_note(existing: Any, note: str) -> str:
    text = "" if pd.isna(existing) else str(existing).strip()
    return f"{text}; {note}" if text else note


def _safe_source_name(source_name: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "_" for char in source_name)
    return "_".join(part for part in safe.split("_") if part) or "public_export"


def _phase_label(metadata: pd.Series, phase: str) -> str:
    solvents = {
        "h2o": "water",
        "meoh": "methanol",
        "acn": "acetonitrile",
        "iproh": "isopropanol",
        "acetone": "acetone",
        "hex": "hexane",
        "chcl3": "chloroform",
        "ch2cl2": "dichloromethane",
        "hept": "heptane",
    }
    parts: list[str] = []
    for column, label in solvents.items():
        value = _num(metadata.get(f"eluent.{phase}.{column}"))
        if value:
            parts.append(f"{value:g}% {label}")

    modifiers = []
    for modifier in [
        "formic",
        "acetic",
        "trifluoroacetic",
        "phosphor",
        "nh4ac",
        "nh4form",
        "nh4carb",
        "nh4bicarb",
        "nh4f",
        "nh4oh",
    ]:
        amount = _num(metadata.get(f"eluent.{phase}.{modifier}"))
        if amount:
            unit = metadata.get(f"eluent.{phase}.{modifier}.unit")
            modifiers.append(f"{amount:g}{unit or ''} {modifier}")
    ph = metadata.get(f"eluent.{phase}.pH")
    if pd.notna(ph) and str(ph).strip():
        modifiers.append(f"pH {ph}")
    if modifiers:
        parts.append(" + ".join(modifiers))
    return " + ".join(parts) if parts else pd.NA


def _organic_pct(metadata: pd.Series, prefix: str) -> float:
    total = 0.0
    for phase in ["A", "B", "C", "D"]:
        phase_pct = _num(metadata.get(f"{prefix}.{phase}"))
        organic_fraction = sum(
            _num(metadata.get(f"eluent.{phase}.{solvent}"))
            for solvent in ["meoh", "acn", "iproh", "acetone", "hex", "chcl3", "ch2cl2", "hept"]
        ) / 100.0
        total += phase_pct * organic_fraction
    return total


def _gradient_profile(gradient: pd.DataFrame) -> str:
    return "; ".join(
        f"{row['t [min]']}min A{row['A [%]']} B{row['B [%]']} C{row['C [%]']} D{row['D [%]']} flow{row['flow rate [ml/min]']}"
        for _, row in gradient.iterrows()
    )


def _gradient_duration(gradient: pd.DataFrame) -> float:
    b_values = pd.to_numeric(gradient["B [%]"], errors="coerce")
    times = pd.to_numeric(gradient["t [min]"], errors="coerce")
    max_b = b_values.max()
    max_time = times[b_values == max_b].min()
    return float(max_time) if pd.notna(max_time) else float(times.max())


def _column_chemistry(column_name: object, usp_code: object) -> object:
    column_text = "" if pd.isna(column_name) else str(column_name)
    usp_text = "" if pd.isna(usp_code) else str(usp_code)
    text = f"{column_text} {usp_text}".upper()
    if "T3" in text or "C18" in text or "L1" in text:
        return "C18"
    if "HILIC" in text or "AMIDE" in text:
        return "HILIC"
    if "PHENYL" in text:
        return "phenyl"
    return pd.NA


def _first_numeric(*values: object) -> object:
    for value in values:
        number = _num(value)
        if number:
            return number
    return pd.NA


def _num(value: object) -> float:
    parsed = pd.to_numeric(value, errors="coerce")
    if pd.isna(parsed):
        return 0.0
    return float(parsed)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch tiny public LC-MS RT datasets for offline MVP samples.")
    parser.add_argument("--report-id", default=REPORT_DATASET_ID, help="RepoRT processed_data dataset id.")
    parser.add_argument("--rows", type=int, default=10, help="Number of RT rows to normalize.")
    parser.add_argument("--bulk-report", action="store_true", help="Fetch multiple RepoRT processed datasets.")
    parser.add_argument("--target-rows", type=int, default=5000, help="Target rows for --bulk-report.")
    parser.add_argument("--max-datasets", type=int, default=80, help="Maximum RepoRT datasets to attempt for --bulk-report.")
    parser.add_argument("--mcmrt", action="store_true", help="Fetch and normalize the MCMRT supplementary RT matrix.")
    parser.add_argument("--mcmrt-local-xlsx", type=Path, help="Use a local MCMRT supplementary XLSX instead of downloading.")
    parser.add_argument("--mcmrt-rows", type=int, help="Optional row limit for the normalized MCMRT matrix.")
    parser.add_argument(
        "--local-export",
        type=Path,
        help="Small, already-authorized public CSV/TSV/JSON/XLSX export to normalize instead of downloading RepoRT.",
    )
    parser.add_argument("--source-name", default="public_export", help="Source label for --local-export rows.")
    parser.add_argument("--source-url", default="", help="Original public source URL for provenance notes.")
    parser.add_argument("--license-note", default="reviewed before local import", help="License/provenance note.")
    parser.add_argument("--output-name", help="Optional processed filename stem after external_.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PUBLIC_SOURCE_MANIFEST,
        help="Reviewed public-source manifest to print when --list-sources is used.",
    )
    parser.add_argument("--list-sources", action="store_true", help="Print reviewed public source manifest and exit.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.list_sources:
        sources = load_public_source_manifest(args.manifest)
        for source in sources:
            print(
                f"{source['source_name']}: {source['adapter_status']} | "
                f"{source['ingestion_mode']} | {source['url']}"
            )
        return 0
    if args.mcmrt or args.mcmrt_local_xlsx:
        output = fetch_mcmrt_supplement(
            rows=args.mcmrt_rows,
            output_name=args.output_name or "mcmrt_supplement",
            local_xlsx=args.mcmrt_local_xlsx,
        )
    elif args.bulk_report:
        output = fetch_report_bulk(
            target_rows=args.target_rows,
            max_datasets=args.max_datasets,
            output_name=args.output_name or "report_bulk",
        )
    elif args.local_export:
        output = import_local_public_export(
            args.local_export,
            source_name=args.source_name,
            source_url=args.source_url,
            license_note=args.license_note,
            rows=args.rows,
            output_name=args.output_name,
        )
    else:
        output = fetch_report_sample(args.report_id, args.rows)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
