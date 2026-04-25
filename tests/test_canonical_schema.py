from app.schemas.canonical import (
    CANONICAL_REGISTRY_FIELDS,
    duplicate_key,
    method_hash,
    missing_required_fields,
    source_quality_score,
)


def _complete_record() -> dict[str, object]:
    return {
        "compound_name": "Caffeine",
        "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
        "inchikey": "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
        "source_dataset": "RepoRT",
        "source_record_id": "row-1",
        "column_name": " Waters BEH C18 ",
        "column_chemistry": "C18",
        "stationary_phase_type": "reversed phase",
        "mobile_phase_a": "Water + 0.1% formic acid",
        "mobile_phase_b": "Acetonitrile + 0.1% formic acid",
        "ph": 3.2,
        "gradient_profile": "0 min 5% B; 5 min 95% B",
        "initial_organic_pct": 5,
        "final_organic_pct": 95,
        "gradient_duration_min": 5,
        "total_runtime_min": 7,
        "temperature_c": 40,
        "flow_ml_min": 0.35,
        "ion_mode": "positive",
        "precursor_mz": 195.0877,
        "product_mz": 138.066,
        "matrix": "plasma",
        "rt_min": 1.42,
        "peak_area": 12345,
        "peak_height": 2345,
        "sn_ratio": 42,
        "tailing_factor": 1.1,
        "asymmetry": 1.05,
        "resolution": 2.0,
    }


def test_registry_field_groups_cover_required_sections():
    assert set(CANONICAL_REGISTRY_FIELDS) == {
        "compound",
        "lc_method",
        "ms_method",
        "sample_context",
        "observation",
        "peak_metrics",
        "provenance",
    }
    assert "canonical_smiles" in CANONICAL_REGISTRY_FIELDS["compound"]
    assert "gradient_profile" in CANONICAL_REGISTRY_FIELDS["lc_method"]
    assert "rt_min" in CANONICAL_REGISTRY_FIELDS["observation"]
    assert "source_dataset" in CANONICAL_REGISTRY_FIELDS["provenance"]


def test_method_hash_is_deterministic_after_normalization():
    record = _complete_record()
    equivalent = {
        **record,
        "column_name": "waters beh c18",
        "ph": "3.2000",
        "flow_ml_min": "0.35000",
        "temperature_c": "40.0",
        "total_runtime_min": "7.000",
    }

    assert method_hash(record) == method_hash(equivalent)


def test_duplicate_key_uses_identity_method_ms_sample_and_rounded_rt():
    record = _complete_record()

    assert duplicate_key(record) == (
        "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
        method_hash(record),
        "positive",
        195.0877,
        138.066,
        "plasma",
        1.42,
    )


def test_source_quality_score_increases_with_completeness():
    sparse = {
        "compound_name": "Caffeine",
        "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
        "rt_min": 1.42,
        "source_dataset": "RepoRT",
    }
    complete = _complete_record()

    assert 0 < source_quality_score(sparse) < source_quality_score(complete) <= 1


def test_missing_required_fields_reports_blank_values():
    record = _complete_record()
    record["source_dataset"] = " "
    record["rt_min"] = None

    assert missing_required_fields(record) == ["rt_min", "source_dataset"]
