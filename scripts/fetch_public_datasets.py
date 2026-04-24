from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.dataset import CANONICAL_DATASET_COLUMNS

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "public_sources"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REPORT_BASE = "https://raw.githubusercontent.com/michaelwitting/RepoRT/master/processed_data"
REPORT_DATASET_ID = "0001"

@dataclass(frozen=True)
class RepoRTFiles:
    metadata: pd.DataFrame
    rtdata: pd.DataFrame
    gradient: pd.DataFrame
    info: pd.DataFrame


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


def _fetch_text(url: str) -> str:
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


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
    text = f"{column_name or ''} {usp_code or ''}".upper()
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
    return parser


def main() -> int:
    args = _parser().parse_args()
    output = fetch_report_sample(args.report_id, args.rows)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
