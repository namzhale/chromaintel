import json

import pandas as pd
import pytest

from scripts.fetch_public_datasets import (
    REQUIRED_MANIFEST_FIELDS,
    import_local_public_export,
    load_public_source_manifest,
)


def test_public_source_manifest_has_required_contract():
    sources = load_public_source_manifest()

    assert {source["source_name"] for source in sources} >= {"RepoRT", "METLIN_SMRT", "Internal_Lab_Historical_Runs"}
    for source in sources:
        assert REQUIRED_MANIFEST_FIELDS.issubset(source)
        assert source["expected_fields"]
        assert isinstance(source["known_missingness"], list)


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
