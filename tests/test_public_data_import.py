import json

import pandas as pd
import pytest

from scripts.fetch_public_datasets import (
    REQUIRED_MANIFEST_FIELDS,
    import_local_public_export,
    list_report_dataset_ids,
    load_public_source_manifest,
    normalize_mcmrt_workbook,
)
from scripts.assemble_dataset import assemble_dataset


def test_public_source_manifest_has_required_contract():
    sources = load_public_source_manifest()

    assert {source["source_name"] for source in sources} >= {"RepoRT", "METLIN_SMRT", "Internal_Lab_Historical_Runs"}
    for source in sources:
        assert REQUIRED_MANIFEST_FIELDS.issubset(source)
        assert source["expected_fields"]
        assert isinstance(source["known_missingness"], list)
    mcmrt = next(source for source in sources if source["source_name"] == "MCMRT")
    assert mcmrt["adapter_status"] == "implemented_supplement_xlsx_normalizer"


@pytest.mark.parametrize("suffix", [".csv", ".tsv", ".jsonl"])
def test_import_local_public_export_normalizes_common_formats(tmp_path, suffix):
    source = pd.DataFrame(
        [
            {
                "compound": "Caffeine",
                "SMILES": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "column": "BEH C18",
                "mobile_phase_a": "Water + 0.1% formic acid",
                "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
                "rt": 1.42,
            }
        ]
    )
    input_path = tmp_path / f"public_export{suffix}"
    if suffix == ".tsv":
        source.to_csv(input_path, sep="\t", index=False)
    elif suffix == ".jsonl":
        input_path.write_text("\n".join(json.dumps(row) for row in source.to_dict("records")), encoding="utf-8")
    else:
        source.to_csv(input_path, index=False)

    output = import_local_public_export(
        input_path,
        source_name="UnitPublic",
        source_url="https://example.test/public",
        license_note="test license",
        processed_dir=tmp_path,
        output_name=f"unit_{suffix.strip('.')}",
    )

    normalized = pd.read_csv(output)
    assert normalized.loc[0, "compound_name"] == "Caffeine"
    assert normalized.loc[0, "source_dataset"] == "UnitPublic"
    assert normalized.loc[0, "rt_min"] == 1.42
    assert normalized.loc[0, "column_chemistry"] == "C18"
    assert "source_url=https://example.test/public" in normalized.loc[0, "notes"]
    assert "license=test license" in normalized.loc[0, "notes"]


def test_import_local_public_export_rejects_files_without_rt(tmp_path):
    input_path = tmp_path / "bad.csv"
    pd.DataFrame([{"compound_name": "No RT", "smiles": "CCO"}]).to_csv(input_path, index=False)

    with pytest.raises(ValueError, match="rt_min"):
        import_local_public_export(
            input_path,
            source_name="BadPublic",
            source_url="https://example.test/bad",
            license_note="test license",
            processed_dir=tmp_path,
        )


def test_normalize_mcmrt_workbook_melts_rt_matrix(tmp_path):
    workbook = tmp_path / "mcmrt_unit.xlsx"
    s2 = pd.DataFrame([[pd.NA] * 4 for _ in range(21)])
    s2.iloc[0, 0] = "#Number"
    s2.iloc[0, 1] = "CM 01"
    s2.iloc[1, 0] = "LC method name"
    s2.iloc[1, 1] = "C1_A1B1_10min"
    s2.iloc[6, 0] = "Analytical column"
    s2.iloc[6, 1] = "ACQUITY BEH C18"
    s2.iloc[9, 0] = "Column temperature (C)"
    s2.iloc[9, 1] = 40
    s2.iloc[11, 0] = "Mobile phase A"
    s2.iloc[11, 1] = "Water with 0.1% formic acid"
    s2.iloc[12, 0] = "Mobile phase B"
    s2.iloc[12, 1] = "Acetonitrile with 0.1% formic acid"
    s2.iloc[14, 1] = 0
    s2.iloc[14, 2] = 0.3
    s2.iloc[14, 3] = 5
    s2.iloc[15, 1] = 5
    s2.iloc[15, 2] = 0.3
    s2.iloc[15, 3] = 95

    s3 = pd.DataFrame(
        [
            {
                "MCMRT\nNumber": 1,
                "Compound \nName": "Caffeine",
                "Isomeric SMILES": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "InChI": "InChI=1S/C8H10N4O2",
                "ESI polarity": "Positive",
            },
            {
                "MCMRT\nNumber": 2,
                "Compound \nName": "Aspirin",
                "Isomeric SMILES": "CC(=O)Oc1ccccc1C(=O)O",
                "InChI": "InChI=1S/C9H8O4",
                "ESI polarity": "Negative",
            },
        ]
    )
    s4 = pd.DataFrame(
        [
            {"Number": 1, "Compound Name": "Caffeine", "CM 01\nC1_A1B1_10min": 1.25},
            {"Number": 2, "Compound Name": "Aspirin", "CM 01\nC1_A1B1_10min": 3.45},
        ]
    )
    with pd.ExcelWriter(workbook) as writer:
        pd.DataFrame().to_excel(writer, sheet_name="S1", index=False)
        s2.to_excel(writer, sheet_name="S2", index=False, header=False)
        s3.to_excel(writer, sheet_name="S3", index=False)
        s4.to_excel(writer, sheet_name="S4", index=False)

    normalized = normalize_mcmrt_workbook(workbook)

    assert len(normalized) == 2
    assert set(normalized["source_dataset"]) == {"MCMRT:CM 01"}
    assert normalized.loc[0, "column_chemistry"] == "C18"
    assert normalized.loc[0, "initial_organic_pct"] == 5
    assert normalized.loc[0, "final_organic_pct"] == 95
    assert "dataset=https://doi.org/10.57760/sciencedb.15823" in normalized.loc[0, "notes"]


def test_assemble_dataset_accepts_additional_processed_source(tmp_path):
    primary = tmp_path / "primary.csv"
    pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "rt_min": 1.4,
            }
        ]
    ).to_csv(primary, index=False)
    extra = tmp_path / "external.csv"
    pd.DataFrame(
        [
            {
                "compound_name": "Aspirin",
                "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                "source_dataset": "RepoRT:unit",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "rt_min": 3.2,
            }
        ]
    ).to_csv(extra, index=False)

    outputs = assemble_dataset(
        source_path=primary,
        output_dir=tmp_path / "processed",
        templates_dir=tmp_path / "templates",
        additional_sources=[extra],
    )
    master = pd.read_csv(outputs.master_path)

    assert outputs.source_rows == 1
    assert outputs.additional_source_rows == 1
    assert outputs.master_rows == 2
    assert set(master["source_dataset"]) == {"primary", "RepoRT:unit"}


def test_list_report_dataset_ids_can_parse_github_payload(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                [
                    {"name": "0002", "type": "dir"},
                    {"name": "README.md", "type": "file"},
                    {"name": "0001", "type": "dir"},
                ]
            ).encode()

    monkeypatch.setattr("scripts.fetch_public_datasets.urlopen", lambda *_args, **_kwargs: FakeResponse())

    assert list_report_dataset_ids() == ["0001", "0002"]
