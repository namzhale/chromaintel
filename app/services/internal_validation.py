from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.schemas.dataset import REQUIRED_INTERNAL_COLUMNS
from app.services.descriptors import DescriptorCalculator, InvalidStructureError


@dataclass(frozen=True)
class ValidationIssue:
    """A single internal lab import validation issue."""

    row: int | None
    column: str | None
    severity: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Validation result for an uploaded internal LC-MS/MS history file."""

    is_valid: bool
    issues: list[ValidationIssue]


INTERNAL_TEMPLATE_COLUMNS = [
    "run_id",
    "compound_name",
    "smiles",
    "pubchem_cid",
    "inchikey",
    "matrix",
    "sample_prep",
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
    "collision_energy_v",
    "rt_min",
    "peak_area",
    "peak_height",
    "sn_ratio",
    "tailing_factor",
    "asymmetry",
    "resolution",
    "success_flag",
    "notes",
]


DATA_DICTIONARY = {
    "run_id": "Unique analytical run or result identifier. Required.",
    "compound_name": "Analyte or internal standard name. Required.",
    "smiles": "Structure SMILES used for RDKit normalization. Required for model training.",
    "pubchem_cid": "Optional PubChem compound identifier.",
    "inchikey": "Optional source InChIKey; recalculated when SMILES is valid.",
    "matrix": "Biological matrix, e.g. plasma, serum, urine, whole blood.",
    "sample_prep": "Sample preparation summary, e.g. PPT, LLE, SPE.",
    "column_name": "Column brand/chemistry/dimensions. Required.",
    "column_chemistry": "Controlled chemistry label, e.g. C18, phenyl, HILIC.",
    "stationary_phase_type": "Reversed phase, HILIC, ion exchange, etc.",
    "mobile_phase_a": "A solvent/buffer composition. Required.",
    "mobile_phase_b": "B solvent/buffer composition. Required.",
    "ph": "Mobile phase pH; valid range 0-14.",
    "gradient_profile": "Human-readable gradient or JSON profile.",
    "initial_organic_pct": "Initial organic percent, usually percent B.",
    "final_organic_pct": "Final organic percent, usually percent B.",
    "gradient_duration_min": "Gradient ramp duration in minutes.",
    "total_runtime_min": "Total method runtime in minutes.",
    "temperature_c": "Column temperature in Celsius.",
    "flow_ml_min": "LC flow in mL/min; must be positive.",
    "injection_ul": "Injection volume in microliters.",
    "ion_mode": "positive, negative, both, or unknown.",
    "precursor_mz": "MRM/Q1 precursor m/z.",
    "product_mz": "MRM/Q3 product m/z.",
    "collision_energy_v": "Collision energy in volts/eV as recorded.",
    "rt_min": "Observed retention time in minutes. Required.",
    "peak_area": "Integrated peak area.",
    "peak_height": "Peak height.",
    "sn_ratio": "Signal-to-noise ratio.",
    "tailing_factor": "USP tailing factor where available.",
    "asymmetry": "Peak asymmetry factor where available.",
    "resolution": "Resolution to nearest critical neighbor.",
    "success_flag": "Whether the run/method met acceptance expectations.",
    "notes": "Free text comments and caveats.",
}


def validate_internal_lab_frame(frame: pd.DataFrame) -> ValidationResult:
    """Validate a realistic internal bioanalytical LC-MS/MS import frame."""

    issues: list[ValidationIssue] = []
    missing_columns = [column for column in REQUIRED_INTERNAL_COLUMNS if column not in frame.columns]
    for column in missing_columns:
        issues.append(ValidationIssue(None, column, "error", f"missing required field: {column}"))

    if "run_id" in frame.columns:
        duplicate_mask = frame["run_id"].astype("string").duplicated(keep=False)
        for idx in frame.index[duplicate_mask]:
            issues.append(ValidationIssue(int(idx), "run_id", "error", "duplicate run_id"))

    for idx, row in frame.iterrows():
        for column in REQUIRED_INTERNAL_COLUMNS:
            if column in frame.columns and pd.isna(row.get(column)):
                issues.append(ValidationIssue(int(idx), column, "error", f"missing required value: {column}"))
        _validate_numeric_range(issues, row, int(idx), "ph", 0, 14)
        _validate_numeric_range(issues, row, int(idx), "flow_ml_min", 0.001, 5)
        _validate_numeric_range(issues, row, int(idx), "temperature_c", 0, 120)
        _validate_numeric_range(issues, row, int(idx), "injection_ul", 0, 100)
        _validate_numeric_range(issues, row, int(idx), "rt_min", 0, 120)
        smiles = row.get("smiles") if "smiles" in frame.columns else None
        if pd.isna(smiles) or not str(smiles).strip():
            issues.append(ValidationIssue(int(idx), "smiles", "error", "missing SMILES"))
        else:
            try:
                DescriptorCalculator().canonicalize(str(smiles))
            except InvalidStructureError:
                issues.append(ValidationIssue(int(idx), "smiles", "error", "invalid SMILES"))

    return ValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )


def write_internal_templates(output_dir: str | Path = "data/templates") -> dict[str, str]:
    """Create an internal historical-runs CSV template and data dictionary."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    template_csv = output / "internal_lab_historical_runs_template.csv"
    dictionary = output / "internal_lab_data_dictionary.md"

    pd.DataFrame(
        [
            {
                "run_id": "RUN-EXAMPLE-001",
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "matrix": "plasma",
                "sample_prep": "protein precipitation",
                "column_name": "BEH C18 50x2.1 mm 1.7um",
                "column_chemistry": "C18",
                "stationary_phase_type": "reversed phase",
                "mobile_phase_a": "Water + 0.1% formic acid",
                "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
                "ph": 3.2,
                "gradient_profile": "5-95%B over 5.0 min, hold 0.8 min",
                "initial_organic_pct": 5,
                "final_organic_pct": 95,
                "gradient_duration_min": 5.0,
                "total_runtime_min": 5.8,
                "temperature_c": 40,
                "flow_ml_min": 0.35,
                "injection_ul": 2,
                "ion_mode": "positive",
                "precursor_mz": 195.1,
                "product_mz": 138.1,
                "collision_energy_v": 20,
                "rt_min": 1.35,
                "peak_area": 212000,
                "peak_height": 54000,
                "sn_ratio": 82,
                "tailing_factor": 1.1,
                "asymmetry": 1.05,
                "resolution": 2.1,
                "success_flag": True,
                "notes": "Example row; replace with historical lab data.",
            }
        ],
        columns=INTERNAL_TEMPLATE_COLUMNS,
    ).to_csv(template_csv, index=False)

    lines = ["# Internal Lab Historical Runs Data Dictionary", ""]
    for column in INTERNAL_TEMPLATE_COLUMNS:
        lines.append(f"- `{column}`: {DATA_DICTIONARY[column]}")
    dictionary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"template_csv": str(template_csv), "data_dictionary": str(dictionary)}


def _validate_numeric_range(
    issues: list[ValidationIssue],
    row: pd.Series,
    idx: int,
    column: str,
    low: float,
    high: float,
) -> None:
    if column not in row.index or pd.isna(row.get(column)):
        return
    value = pd.to_numeric(row.get(column), errors="coerce")
    if pd.isna(value) or not low <= float(value) <= high:
        issues.append(
            ValidationIssue(idx, column, "error", f"{column} outside valid range {low}-{high}")
        )

