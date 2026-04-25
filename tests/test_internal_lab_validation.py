from pathlib import Path

import pandas as pd

from app.services.internal_validation import (
    preview_internal_lab_import,
    validate_internal_lab_frame,
    write_internal_templates,
)


def test_internal_lab_validation_flags_missing_ranges_smiles_and_duplicates(tmp_path):
    frame = pd.DataFrame(
        [
            {
                "run_id": "RUN-1",
                "compound_name": "Bad",
                "smiles": "not-smiles",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "ph": 15,
                "flow_ml_min": -0.1,
                "rt_min": 2.1,
            },
            {
                "run_id": "RUN-1",
                "compound_name": "Bad duplicate",
                "smiles": "",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "ph": 3.2,
                "flow_ml_min": 0.35,
                "rt_min": 2.2,
            },
        ]
    )

    result = validate_internal_lab_frame(frame)

    assert not result.is_valid
    assert any("invalid SMILES" in issue.message for issue in result.issues)
    assert any("duplicate run_id" in issue.message for issue in result.issues)
    assert any("ph outside" in issue.message for issue in result.issues)


def test_write_internal_templates_creates_csv_and_dictionary(tmp_path):
    outputs = write_internal_templates(tmp_path)

    assert Path(outputs["template_csv"]).exists()
    assert Path(outputs["data_dictionary"]).exists()


def test_internal_lab_validation_flags_gradient_vocab_and_transition_gaps():
    frame = pd.DataFrame(
        [
            {
                "run_id": "RUN-2",
                "compound_name": "Aspirin",
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "matrix": "bloodish",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "ph": 3.2,
                "flow_ml_min": 0.35,
                "rt_min": 2.1,
                "ion_mode": "positive",
                "initial_organic_pct": 95,
                "final_organic_pct": 5,
                "gradient_duration_min": 8,
                "total_runtime_min": 6,
            }
        ]
    )

    result = validate_internal_lab_frame(frame)
    messages = [issue.message for issue in result.issues]

    assert not result.is_valid
    assert any("matrix must be one of" in message for message in messages)
    assert any("gradient duration exceeds total runtime" in message for message in messages)
    assert any("precursor_mz is required" in message for message in messages)
    assert any("product_mz is required" in message for message in messages)
    assert any("collision_energy_v is required" in message for message in messages)


def test_internal_lab_preview_summarizes_missing_invalid_and_duplicates():
    frame = pd.DataFrame(
        [
            {
                "run_id": "RUN-3",
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "rt_min": 1.3,
            },
            {
                "run_id": "RUN-3",
                "compound_name": None,
                "smiles": "not-smiles",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "rt_min": 2.2,
            },
        ]
    )

    preview = preview_internal_lab_import(frame)

    assert preview.row_count == 2
    assert preview.invalid_row_count == 2
    assert preview.duplicate_run_id_count == 2
    assert preview.missingness_by_column["compound_name"] == 1
    assert any(issue.message == "duplicate run_id" for issue in preview.issues)
