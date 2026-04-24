import pandas as pd

from app.services.dataset_assembly import assemble_master_dataset, normalize_source_frame


def test_normalize_source_frame_canonicalizes_identity_and_columns():
    raw = pd.DataFrame(
        [
            {
                "name": " caffeine ",
                "SMILES": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "column": "BEH C18",
                "stationary_phase": "C18",
                "mobile_phase_a": "Water + 0.1% formic acid",
                "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
                "rt": 1.42,
                "pH": 3.2,
                "flow": 0.35,
                "temp": 40,
                "ionization_mode": "ESI+",
            }
        ]
    )

    normalized = normalize_source_frame(raw, source_dataset="RepoRT")

    assert list(normalized["source_dataset"]) == ["RepoRT"]
    assert normalized.loc[0, "compound_name"] == "caffeine"
    assert normalized.loc[0, "canonical_smiles"] == "Cn1c(=O)c2c(ncn2C)n(C)c1=O"
    assert normalized.loc[0, "inchikey"]
    assert normalized.loc[0, "rt_min"] == 1.42
    assert normalized.loc[0, "ion_mode"] == "positive"
    assert "notes" in normalized.columns


def test_assemble_master_dataset_deduplicates_by_identity_method_and_rt():
    source_a = pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "source_dataset": "METLIN_SMRT",
                "column_name": "BEH C18",
                "mobile_phase_a": "Water",
                "mobile_phase_b": "Acetonitrile",
                "ph": 3.2,
                "rt_min": 1.4,
            }
        ]
    )
    source_b = source_a.copy()
    source_b["source_dataset"] = "RepoRT"

    master = assemble_master_dataset([source_a, source_b])

    assert len(master) == 1
    assert master.loc[0, "source_dataset"] == "METLIN_SMRT;RepoRT"
    assert master.loc[0, "missing_fields_count"] > 0
