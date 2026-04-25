from pathlib import Path

import pandas as pd
import pytest

from app.adapters.public_rt import (
    PUBLIC_RT_ADAPTERS,
    load_public_rt_records,
    summarize_public_rt_records,
    write_public_rt_report,
)
from app.schemas.dataset import CANONICAL_DATASET_COLUMNS


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_rt"


@pytest.mark.parametrize(
    ("source_name", "fixture_name", "expected_rows"),
    [
        ("PredRet", "predret_fixture.csv", 2),
        ("GMCRT", "gmcrt_fixture.tsv", 3),
        ("MultiConditionRT", "multiconditionrt_fixture.csv", 2),
    ],
)
def test_configured_public_rt_adapters_normalize_fixture_tables(source_name, fixture_name, expected_rows):
    records = load_public_rt_records(FIXTURE_DIR / fixture_name, source_name)

    assert list(records.columns) == CANONICAL_DATASET_COLUMNS
    assert len(records) == expected_rows
    assert set(records["source_dataset"]) == {source_name}
    assert records["compound_name"].notna().all()
    assert records["rt_min"].notna().all()
    assert records["missing_fields_count"].ge(0).all()
    assert source_name in records.loc[0, "notes"]


def test_public_rt_adapter_uses_source_defaults_and_column_aliases():
    records = load_public_rt_records(FIXTURE_DIR / "multiconditionrt_fixture.csv", "MultiConditionRT")

    assert records.loc[0, "source_record_id"] == "MC-01"
    assert records.loc[0, "initial_organic_pct"] == 10
    assert records.loc[1, "stationary_phase_type"] == "HILIC"
    assert records.loc[1, "column_chemistry"] == "HILIC"
    assert records["matrix"].eq("reference").all()
    assert records["success_flag"].eq(True).all()


def test_public_rt_summary_counts_missing_fields_and_duplicate_rows():
    records = load_public_rt_records(FIXTURE_DIR / "gmcrt_fixture.tsv", "GMCRT")
    summary = summarize_public_rt_records(records, PUBLIC_RT_ADAPTERS["GMCRT"])

    assert summary["source_name"] == "GMCRT"
    assert summary["rows"] == 3
    assert summary["duplicate_rows"] == 1
    assert summary["missing_by_column"]["precursor_mz"] == 3
    assert "compound_name|canonical_smiles|column_name|rt_min" in summary["duplicate_key"]


def test_public_rt_report_is_written_as_markdown(tmp_path):
    records = load_public_rt_records(FIXTURE_DIR / "gmcrt_fixture.tsv", "GMCRT")
    output = write_public_rt_report(records, PUBLIC_RT_ADAPTERS["GMCRT"], tmp_path / "gmcrt.md")

    text = output.read_text(encoding="utf-8")
    assert "# GMCRT fixture ingestion report" in text
    assert "- Rows: 3" in text
    assert "- Duplicate rows: 1" in text
    assert "| precursor_mz | 3 |" in text


def test_public_rt_adapter_rejects_unknown_source():
    with pytest.raises(ValueError, match="Unknown public RT source"):
        load_public_rt_records(FIXTURE_DIR / "predret_fixture.csv", "NopeRT")


def test_public_rt_adapter_requires_configured_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame([{"compound_name": "No RT"}]).to_csv(bad, index=False)

    with pytest.raises(ValueError, match="PredRet fixture is missing configured columns"):
        load_public_rt_records(bad, "PredRet")
