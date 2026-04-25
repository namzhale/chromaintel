import pandas as pd

from app.services.dataset_assembly import (
    assemble_master_dataset,
    normalize_source_frame,
    resolve_external_sources,
)
from scripts.assemble_dataset import assemble_dataset


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
                "width_at_base": 0.24,
                "width_at_half_height": 0.11,
            }
        ]
    )

    normalized = normalize_source_frame(raw, source_dataset="RepoRT")

    assert list(normalized["source_dataset"]) == ["RepoRT"]
    assert normalized.loc[0, "compound_name"] == "caffeine"
    assert normalized.loc[0, "canonical_smiles"] == "Cn1c(=O)c2c(ncn2C)n(C)c1=O"
    assert normalized.loc[0, "inchikey"]
    assert normalized.loc[0, "rt_min"] == 1.42
    assert normalized.loc[0, "peak_width_base_min"] == 0.24
    assert normalized.loc[0, "peak_width_half_height_min"] == 0.11
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


def test_expanded_ml_profile_selects_canonical_sources_and_sidecars(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    for name in [
        "external_retina_hf_full.csv",
        "external_metlin_smrt_figshare.csv",
        "external_kaggle_metlin_descriptors.csv",
        "external_kaggle_metlin_descriptors_descriptors.csv",
        "external_report_bulk_5k.csv",
        "external_mcmrt_supplement.csv",
    ]:
        (processed / name).write_text("compound_name,rt_min\nExample,1.0\n", encoding="utf-8")

    selection = resolve_external_sources(processed, profile="expanded_ml")

    included_names = [source.path.name for source in selection.included]
    excluded_names = [source.path.name for source in selection.excluded]
    sidecar_names = [source.path.name for source in selection.sidecars]
    assert included_names == [
        "external_retina_hf_full.csv",
        "external_mcmrt_supplement.csv",
        "external_report_bulk_5k.csv",
        "external_metlin_smrt_figshare.csv",
    ]
    assert "external_kaggle_metlin_descriptors.csv" in excluded_names
    assert "external_kaggle_metlin_descriptors_descriptors.csv" in sidecar_names
    assert any("sidecar metadata" in note for note in selection.policy_notes)


def test_assemble_dataset_explicit_sources_excludes_kaggle_sidecar_and_reports(tmp_path):
    source = tmp_path / "mock_training_records.csv"
    processed = tmp_path / "processed"
    templates = tmp_path / "templates"
    reports = tmp_path / "reports"
    processed.mkdir()
    source.write_text(
        "compound_name,smiles,dataset_source,column_name,mobile_phase_a,mobile_phase_b,rt_min\n"
        "Caffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C,mock_training_records,BEH C18,Water,Acetonitrile,1.40\n",
        encoding="utf-8",
    )
    figshare = processed / "external_metlin_smrt_figshare.csv"
    figshare.write_text(
        "compound_name,smiles,source_dataset,column_name,mobile_phase_a,mobile_phase_b,rt_min\n"
        "Caffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C,METLIN_SMRT_Figshare,BEH C18,Water,Acetonitrile,1.40\n",
        encoding="utf-8",
    )
    kaggle = processed / "external_kaggle_metlin_descriptors.csv"
    kaggle.write_text(
        "compound_name,smiles,source_dataset,column_name,mobile_phase_a,mobile_phase_b,rt_min\n"
        "Caffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C,Kaggle_METLIN_SMRT,BEH C18,Water,Acetonitrile,1.40\n",
        encoding="utf-8",
    )

    outputs = assemble_dataset(
        source_path=source,
        output_dir=processed,
        templates_dir=templates,
        reports_dir=reports,
        source_profile="explicit",
        additional_sources=[figshare, kaggle],
    )

    assert outputs.additional_source_rows == 1
    assert outputs.excluded_source_rows == 1
    assert outputs.master_rows == 1
    report = outputs.summary_report_path.read_text(encoding="utf-8")
    assert "METLIN Figshare" in report
    assert "Kaggle descriptor-aligned canonical export" in report
    assert "Excluded duplicate/sidecar policy" in report
