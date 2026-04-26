import pandas as pd

from app.services.target_readiness import (
    DIRECT_TARGETS,
    build_target_coverage_matrix,
    write_target_readiness_reports,
)


def test_target_coverage_marks_measured_proxy_and_unavailable_targets(tmp_path):
    frame = pd.DataFrame(
        [
            {"rt_min": 1.2, "quality_score": 0.8, "asymmetry": 1.1},
            {"rt_min": 2.4, "quality_score": None, "asymmetry": None},
        ]
    )

    coverage = build_target_coverage_matrix(frame)
    by_target = coverage.set_index("target")

    assert set(DIRECT_TARGETS).issubset(set(coverage["target"]))
    assert by_target.loc["rt_min", "label_source"] == "measured"
    assert by_target.loc["quality_score", "label_source"] == "derived_proxy"
    assert by_target.loc["asymmetry", "readiness"] == "sparse"
    assert by_target.loc["peak_width_base_min", "label_source"] == "unavailable"
    assert by_target.loc["broad_peak_risk", "label_source"] == "derived_proxy"
    assert by_target.loc["broad_peak_risk", "readiness"] == "proxy_only"

    paths = write_target_readiness_reports(frame, tmp_path)
    assert paths["coverage_csv"].exists()
    assert paths["readiness_md"].exists()
    assert "peak_width_half_height_min" in paths["readiness_md"].read_text(encoding="utf-8")
