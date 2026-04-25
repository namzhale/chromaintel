from __future__ import annotations

import json

import pandas as pd

from app.models.transformer_embeddings import (
    detect_encoder_availability,
    join_embeddings_with_method_features,
    load_cached_embeddings,
)


def test_load_cached_embeddings_from_csv_fixture():
    store = load_cached_embeddings("tests/fixtures/embeddings/mock_chemberta_embeddings.csv")

    assert store.metadata["encoder_family"] == "ChemBERTa"
    assert store.key_column == "canonical_smiles"
    assert store.embedding_columns == ["tx_emb_0", "tx_emb_1", "tx_emb_2"]
    assert store.frame.loc["CCO", "tx_emb_1"] == 0.2


def test_join_embeddings_with_method_features_fills_missing_rows_offline():
    method_features = pd.DataFrame(
        [
            {"canonical_smiles": "CCO", "column_chemistry": "C18", "flow_ml_min": 0.3},
            {"canonical_smiles": "missing", "column_chemistry": "T3", "flow_ml_min": 0.4},
        ]
    )
    store = load_cached_embeddings("tests/fixtures/embeddings/mock_chemberta_embeddings.csv")

    joined, metadata = join_embeddings_with_method_features(method_features, store)

    assert list(joined.columns) == [
        "canonical_smiles",
        "column_chemistry",
        "flow_ml_min",
        "tx_emb_0",
        "tx_emb_1",
        "tx_emb_2",
    ]
    assert joined.loc[0, "tx_emb_0"] == 0.1
    assert joined.loc[1, ["tx_emb_0", "tx_emb_1", "tx_emb_2"]].tolist() == [0.0, 0.0, 0.0]
    assert metadata["status"] == "partial"
    assert metadata["missing_embedding_count"] == 1
    assert metadata["skip_reason"] == "missing_cached_embeddings_filled_with_zeros"


def test_join_embeddings_can_skip_when_cache_is_unavailable():
    method_features = pd.DataFrame([{"canonical_smiles": "CCO", "flow_ml_min": 0.3}])

    joined, metadata = join_embeddings_with_method_features(method_features, embedding_store=None)

    assert joined.equals(method_features)
    assert metadata["status"] == "skipped"
    assert metadata["skip_reason"] == "embedding_store_unavailable"
    assert metadata["embedding_columns"] == []


def test_detect_encoder_availability_never_downloads_when_dependency_missing():
    availability = detect_encoder_availability("ChemBERTa", local_files_only=True)

    assert availability.encoder_family == "ChemBERTa"
    assert availability.model_id == "seyonec/ChemBERTa-zinc-base-v1"
    assert availability.local_files_only is True
    assert availability.download_attempted is False
    assert isinstance(availability.available, bool)
    assert availability.status in {"available", "unavailable"}
    json.dumps(availability.to_metadata())


def test_detect_encoder_availability_accepts_generic_hf_model_id_without_download():
    availability = detect_encoder_availability(
        "generic_hf",
        model_id="local/mock-smiles-transformer",
        local_files_only=True,
    )

    assert availability.encoder_family == "generic_hf"
    assert availability.model_id == "local/mock-smiles-transformer"
    assert availability.download_attempted is False
