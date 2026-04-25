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


@dataclass(frozen=True)
class ImportPreview:
    """Compact preview summary for internal lab onboarding before import."""

    row_count: int
    valid_row_count: int
    invalid_row_count: int
    duplicate_run_id_count: int
    missingness_by_column: dict[str, int]
    issues: list[ValidationIssue]


ION_MODE_VALUES = {"positive", "negative", "both", "unknown"}
MATRIX_VALUES = {
    "plasma",
    "serum",
    "urine",
    "whole blood",
    "blood",
    "saliva",
    "csf",
    "tissue",
    "unknown",
}


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
    "peak_width_base_min",
    "peak_width_half_height_min",
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
    "peak_width_base_min": "Peak width at baseline in minutes where available.",
    "peak_width_half_height_min": "Peak width at half height in minutes where available.",
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
        _validate_vocabulary(issues, row, int(idx), "ion_mode", ION_MODE_VALUES)
        _validate_vocabulary(issues, row, int(idx), "matrix", MATRIX_VALUES)
        _validate_gradient_consistency(issues, row, int(idx))
        _validate_transition_requirements(issues, row, int(idx))
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


def preview_internal_lab_import(frame: pd.DataFrame) -> ImportPreview:
    """Summarize validity, missingness, and duplicate rows before database import."""

    result = validate_internal_lab_frame(frame)
    invalid_rows = {issue.row for issue in result.issues if issue.severity == "error" and issue.row is not None}
    duplicate_count = 0
    if "run_id" in frame.columns:
        duplicate_count = int(frame["run_id"].astype("string").duplicated(keep=False).sum())
    missingness = {
        column: int(frame[column].isna().sum())
        for column in frame.columns
    }
    return ImportPreview(
        row_count=len(frame),
        valid_row_count=max(len(frame) - len(invalid_rows), 0),
        invalid_row_count=len(invalid_rows),
        duplicate_run_id_count=duplicate_count,
        missingness_by_column=missingness,
        issues=result.issues,
    )


def write_internal_templates(output_dir: str | Path = "data/templates") -> dict[str, str]:
    """Create an internal historical-runs CSV template and data dictionary."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    template_csv = output / "internal_lab_historical_runs_template.csv"
    dictionary = output / "internal_lab_data_dictionary.md"

    pd.DataFrame(_template_example_rows(), columns=INTERNAL_TEMPLATE_COLUMNS).to_csv(template_csv, index=False)

    lines = ["# Internal Lab Historical Runs Data Dictionary", ""]
    for column in INTERNAL_TEMPLATE_COLUMNS:
        lines.append(f"- `{column}`: {DATA_DICTIONARY[column]}")
    dictionary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"template_csv": str(template_csv), "data_dictionary": str(dictionary)}


def _template_example_rows() -> list[dict[str, object]]:
    """Return realistic accepted and failed BE-style internal-history examples."""

    base = {
        "compound_name": "Caffeine",
        "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        "pubchem_cid": 2519,
        "inchikey": "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
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
    }
    examples = [
        {
            **base,
            "run_id": "RUN-ACCEPTED-001",
            "notes": "accepted; clean peak shape and adequate response",
        },
        {
            **base,
            "run_id": "RUN-FAILED-001",
            "rt_min": 0.18,
            "peak_area": 18000,
            "peak_height": 5200,
            "sn_ratio": 14,
            "tailing_factor": 2.6,
            "asymmetry": 2.2,
            "resolution": 0.6,
            "success_flag": False,
            "notes": "failed; near-void elution and poor resolution from matrix front",
        },
        {
            **base,
            "run_id": "RUN-LOW-INTENSITY-001",
            "peak_area": 4200,
            "peak_height": 900,
            "sn_ratio": 5,
            "success_flag": False,
            "notes": "low_intensity; response below lower calibration acceptance expectation",
        },
        {
            **base,
            "run_id": "RUN-POOR-RESOLUTION-001",
            "rt_min": 1.02,
            "resolution": 0.8,
            "success_flag": False,
            "notes": "poor_resolution; coelution with endogenous interference",
        },
        {
            **base,
            "run_id": "RUN-CARRYOVER-001",
            "peak_area": 65000,
            "peak_height": 16000,
            "sn_ratio": 35,
            "success_flag": False,
            "notes": "carryover; post-ULOQ blank retained measurable analyte signal",
        },
    ]
    return examples


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


def _validate_vocabulary(
    issues: list[ValidationIssue],
    row: pd.Series,
    idx: int,
    column: str,
    allowed: set[str],
) -> None:
    if column not in row.index or pd.isna(row.get(column)):
        return
    value = str(row.get(column)).strip().lower()
    if value and value not in allowed:
        issues.append(
            ValidationIssue(idx, column, "error", f"{column} must be one of {sorted(allowed)}")
        )


def _validate_gradient_consistency(issues: list[ValidationIssue], row: pd.Series, idx: int) -> None:
    initial = pd.to_numeric(row.get("initial_organic_pct"), errors="coerce")
    final = pd.to_numeric(row.get("final_organic_pct"), errors="coerce")
    duration = pd.to_numeric(row.get("gradient_duration_min"), errors="coerce")
    runtime = pd.to_numeric(row.get("total_runtime_min"), errors="coerce")

    for column, value in [("initial_organic_pct", initial), ("final_organic_pct", final)]:
        if pd.notna(value) and not 0 <= float(value) <= 100:
            issues.append(ValidationIssue(idx, column, "error", f"{column} must be within 0-100"))
    if pd.notna(initial) and pd.notna(final) and float(final) < float(initial):
        issues.append(
            ValidationIssue(idx, "final_organic_pct", "warning", "final organic percent is below initial percent")
        )
    if pd.notna(duration) and float(duration) <= 0:
        issues.append(ValidationIssue(idx, "gradient_duration_min", "error", "gradient duration must be positive"))
    if pd.notna(duration) and pd.notna(runtime) and float(duration) > float(runtime):
        issues.append(
            ValidationIssue(idx, "gradient_duration_min", "error", "gradient duration exceeds total runtime")
        )


def _validate_transition_requirements(issues: list[ValidationIssue], row: pd.Series, idx: int) -> None:
    ion_mode = str(row.get("ion_mode", "unknown")).strip().lower()
    if ion_mode not in {"positive", "negative", "both"}:
        return
    for column in ["precursor_mz", "product_mz", "collision_energy_v"]:
        if column not in row.index or pd.isna(row.get(column)) or str(row.get(column)).strip() == "":
            issues.append(
                ValidationIssue(idx, column, "error", f"{column} is required when ion_mode is known")
            )
