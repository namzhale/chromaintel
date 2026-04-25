from pathlib import Path

import pandas as pd

from app.adapters.literature_parser import (
    extract_lcms_records,
    load_snippets,
    normalize_literature_records,
)


def test_extract_lcms_records_maps_text_to_canonical_fields():
    text = (
        "Caffeine was analyzed on a Waters BEH C18 column. "
        "Mobile phase A was water with 0.1% formic acid and mobile phase B was "
        "acetonitrile with 0.1% formic acid. The gradient ran from 5% B to 95% B "
        "over 8 min at 0.3 mL/min and 40 C. Injection volume was 2 uL. "
        "ESI+ MRM transition 195.1 > 138.1 gave retention time 2.4 min."
    )

    records = extract_lcms_records([text], source_name="abstract:test")

    assert len(records) == 1
    record = records[0]
    assert record["compound_name"] == "Caffeine"
    assert record["source_dataset"] == "literature:abstract:test"
    assert record["column_name"] == "Waters BEH C18"
    assert record["column_chemistry"] == "C18"
    assert record["stationary_phase_type"] == "reversed phase"
    assert record["mobile_phase_a"] == "water with 0.1% formic acid"
    assert record["mobile_phase_b"] == "acetonitrile with 0.1% formic acid"
    assert record["initial_organic_pct"] == 5
    assert record["final_organic_pct"] == 95
    assert record["gradient_duration_min"] == 8
    assert record["total_runtime_min"] == 8
    assert record["temperature_c"] == 40
    assert record["flow_ml_min"] == 0.3
    assert record["injection_ul"] == 2
    assert record["ion_mode"] == "positive"
    assert record["precursor_mz"] == 195.1
    assert record["product_mz"] == 138.1
    assert record["rt_min"] == 2.4
    assert "offline regex parser" in record["notes"]


def test_load_snippets_reads_text_and_csv_columns(tmp_path):
    text_path = tmp_path / "abstract.txt"
    text_path.write_text("Metformin retention time was 1.1 min.", encoding="utf-8")
    csv_path = tmp_path / "snippets.csv"
    pd.DataFrame({"title": ["paper"], "abstract": ["Aspirin RT 3.2 min by LC-MS."]}).to_csv(
        csv_path, index=False
    )

    snippets = load_snippets([text_path, csv_path])

    assert snippets == [
        "Metformin retention time was 1.1 min.",
        "paper\nAspirin RT 3.2 min by LC-MS.",
    ]


def test_normalize_literature_records_returns_canonical_dataframe():
    records = extract_lcms_records(
        ["Aspirin on C18 column, mobile phase A water, B methanol, rt 3.2 min."],
        source_name="dry-run",
    )

    frame = normalize_literature_records(records)

    assert "missing_fields_count" in frame.columns
    assert frame.loc[0, "source_dataset"] == "literature:dry-run"
    assert frame.loc[0, "rt_min"] == 3.2
    assert frame.loc[0, "column_name"] == "C18"
    assert frame.loc[0, "mobile_phase_a"] == "water"
    assert frame.loc[0, "mobile_phase_b"] == "methanol"
