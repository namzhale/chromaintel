from pathlib import Path

import pandas as pd

from app.services.public_import_preview import discover_processed_imports, preview_processed_import


def test_discover_processed_imports_finds_external_and_literature_files(tmp_path):
    (tmp_path / "external_report_sample.csv").write_text("compound_name,rt_min\nA,1.2\n", encoding="utf-8")
    (tmp_path / "literature_extracted_smoke.csv").write_text("compound_name,rt_min\nB,2.3\n", encoding="utf-8")
    (tmp_path / "master_dataset.csv").write_text("compound_name,rt_min\nC,3.4\n", encoding="utf-8")

    files = discover_processed_imports(tmp_path)

    assert [path.name for path in files] == ["external_report_sample.csv", "literature_extracted_smoke.csv"]


def test_preview_processed_import_reports_canonical_coverage_and_missingness(tmp_path):
    path = tmp_path / "external_demo.csv"
    pd.DataFrame(
        [
            {
                "compound_name": "Caffeine",
                "canonical_smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
                "source_dataset": "RepoRT:test",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": "acetonitrile",
                "rt_min": 2.1,
            },
            {
                "compound_name": "Aspirin",
                "canonical_smiles": None,
                "source_dataset": "RepoRT:test",
                "column_name": "BEH C18",
                "mobile_phase_a": "water",
                "mobile_phase_b": None,
                "rt_min": 4.2,
            },
        ]
    ).to_csv(path, index=False)

    preview = preview_processed_import(path)

    assert preview.path == Path(path)
    assert preview.row_count == 2
    assert preview.column_count == 7
    assert preview.source_counts == {"RepoRT:test": 2}
    assert preview.canonical_coverage["compound_name"] == 1.0
    assert preview.canonical_coverage["canonical_smiles"] == 0.5
    assert preview.canonical_coverage["mobile_phase_b"] == 0.5
    assert preview.missingness[0]["field"] in {"canonical_smiles", "mobile_phase_b"}
