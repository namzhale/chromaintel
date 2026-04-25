from pathlib import Path

import pandas as pd
import pytest

from app.services.compound_identity import (
    CompoundIdentityResolver,
    clear_identity_cache,
    load_identity_cache,
    write_identity_resolution_report,
)


FIXTURE = Path(__file__).parent / "fixtures" / "enrichment" / "compound_identity_cache.csv"


def test_load_identity_cache_reuses_cached_fixture_rows():
    clear_identity_cache()

    first = load_identity_cache(FIXTURE)
    second = load_identity_cache(FIXTURE)

    assert first is second
    assert len(first) == 4
    assert first[0]["normalized_names"] == {"caffeine", "1,3,7-trimethylxanthine", "guaranine"}


def test_resolver_assigns_ranked_confidence_labels_without_live_api_calls(monkeypatch):
    def fail_live_call(*_args, **_kwargs):
        raise AssertionError("identity resolver must not call live PubChem in tests")

    monkeypatch.setattr("app.adapters.pubchem.requests.get", fail_live_call)
    resolver = CompoundIdentityResolver(FIXTURE)

    exact = resolver.resolve({"inchikey": "RYYVLZVUVIJVGH-UHFFFAOYSA-N"})
    first_block = resolver.resolve({"inchikey": "RYYVLZVUVIJVGH-NOTREALSA-N"})
    cid = resolver.resolve({"pubchem_cid": 2244})
    chembl = resolver.resolve({"chembl_id": "chembl25"})
    name_only = resolver.resolve({"name": "Guaranine"})

    assert exact.status == "resolved"
    assert exact.confidence == "exact_inchikey"
    assert exact.candidate["name"] == "Caffeine"
    assert first_block.confidence == "inchikey_first_block"
    assert cid.confidence == "pubchem_cid"
    assert chembl.confidence == "chembl_id"
    assert name_only.confidence == "name_low"


def test_resolver_rejects_ambiguous_name_only_mapping_by_default():
    resolver = CompoundIdentityResolver(FIXTURE)

    result = resolver.resolve({"name": "Shared Name"})

    assert result.status == "ambiguous"
    assert result.confidence == "ambiguous_name"
    assert result.candidate is None
    assert {candidate["pubchem_cid"] for candidate in result.candidates} == {702, 6341}


def test_resolver_can_use_smiles_to_raise_name_match_confidence():
    resolver = CompoundIdentityResolver(FIXTURE)

    result = resolver.resolve({"name": "Caffeine", "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C"})

    assert result.status == "resolved"
    assert result.confidence == "exact_inchikey"
    assert result.candidate["pubchem_cid"] == 2519


def test_write_identity_resolution_report_separates_unresolved_and_ambiguous(tmp_path):
    resolver = CompoundIdentityResolver(FIXTURE)
    results = [
        resolver.resolve({"name": "Caffeine"}),
        resolver.resolve({"name": "Unknown analyte"}),
        resolver.resolve({"name": "Shared Name"}),
    ]

    paths = write_identity_resolution_report(results, tmp_path, stem="unit_identity")

    unresolved = pd.read_csv(paths["unresolved_csv"])
    ambiguous = pd.read_csv(paths["ambiguous_csv"])
    summary = paths["summary_md"].read_text(encoding="utf-8")
    assert unresolved.loc[0, "query_name"] == "Unknown analyte"
    assert ambiguous.loc[0, "candidate_count"] == 2
    assert "resolved: 1" in summary
    assert "ambiguous: 1" in summary
