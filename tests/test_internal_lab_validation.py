from pathlib import Path

import pandas as pd

from app.services.internal_validation import validate_internal_lab_frame, write_internal_templates


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
