from __future__ import annotations

import importlib.util
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_ENCODERS = {
    "chemberta": ("ChemBERTa", "seyonec/ChemBERTa-zinc-base-v1"),
    "molformer": ("MolFormer", "ibm/MoLFormer-XL-both-10pct"),
    "generic_hf": ("generic_hf", None),
    "generic": ("generic_hf", None),
}


@dataclass(frozen=True)
class EncoderAvailability:
    """Serializable status for an optional SMILES transformer encoder."""

    encoder_family: str
    model_id: str | None
    available: bool
    status: str
    reason: str
    local_files_only: bool
    download_attempted: bool
    dependency_available: bool

    def to_metadata(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CachedEmbeddingStore:
    """Offline table of precomputed molecular transformer embeddings."""

    frame: pd.DataFrame
    key_column: str
    embedding_columns: list[str]
    metadata: dict[str, Any]


class SmilesTransformerEncoder:
    """Thin optional wrapper around a local Hugging Face SMILES encoder.

    This class never downloads by default. It is intended for explicit local-cache
    experiments; production tests should use cached embeddings instead.
    """

    def __init__(self, encoder_family: str, model_id: str | None = None, local_files_only: bool = True):
        availability = detect_encoder_availability(
            encoder_family,
            model_id=model_id,
            local_files_only=local_files_only,
        )
        if not availability.available:
            raise RuntimeError(availability.reason)
        self.availability = availability

    def encode(self, smiles: list[str]) -> pd.DataFrame:
        raise NotImplementedError(
            "Live transformer encoding is dependency-gated. Use cached embeddings for offline runs."
        )


def detect_encoder_availability(
    encoder_family: str,
    model_id: str | None = None,
    local_files_only: bool = True,
) -> EncoderAvailability:
    """Check whether a requested Hugging Face encoder can be loaded locally."""

    family, resolved_model_id = _resolve_encoder(encoder_family, model_id)
    has_transformers = importlib.util.find_spec("transformers") is not None
    if not has_transformers:
        return EncoderAvailability(
            encoder_family=family,
            model_id=resolved_model_id,
            available=False,
            status="unavailable",
            reason="transformers_not_installed",
            local_files_only=local_files_only,
            download_attempted=False,
            dependency_available=False,
        )
    if not resolved_model_id:
        return EncoderAvailability(
            encoder_family=family,
            model_id=resolved_model_id,
            available=False,
            status="unavailable",
            reason="model_id_required_for_generic_hf",
            local_files_only=local_files_only,
            download_attempted=False,
            dependency_available=True,
        )

    try:
        from transformers import AutoConfig

        AutoConfig.from_pretrained(resolved_model_id, local_files_only=local_files_only)
    except Exception as exc:
        return EncoderAvailability(
            encoder_family=family,
            model_id=resolved_model_id,
            available=False,
            status="unavailable",
            reason=f"local_model_unavailable: {exc.__class__.__name__}",
            local_files_only=local_files_only,
            download_attempted=not local_files_only,
            dependency_available=True,
        )
    return EncoderAvailability(
        encoder_family=family,
        model_id=resolved_model_id,
        available=True,
        status="available",
        reason="local_transformers_config_available",
        local_files_only=local_files_only,
        download_attempted=not local_files_only,
        dependency_available=True,
    )


def load_cached_embeddings(
    path: str | Path,
    key_column: str = "canonical_smiles",
    embedding_prefix: str = "tx_emb_",
) -> CachedEmbeddingStore:
    """Load precomputed embeddings from CSV/JSON without requiring transformers."""

    cache_path = Path(path)
    if not cache_path.exists():
        raise FileNotFoundError(f"Embedding cache not found: {cache_path}")

    if cache_path.suffix.lower() == ".csv":
        frame = pd.read_csv(cache_path)
    elif cache_path.suffix.lower() == ".json":
        frame = pd.read_json(cache_path)
    else:
        raise ValueError("Embedding cache must be a CSV or JSON file")

    if key_column not in frame.columns:
        raise ValueError(f"Embedding cache is missing key column: {key_column}")
    embedding_columns = [col for col in frame.columns if str(col).startswith(embedding_prefix)]
    if not embedding_columns:
        raise ValueError(f"Embedding cache has no columns with prefix {embedding_prefix!r}")

    normalized = frame.copy()
    normalized[key_column] = normalized[key_column].astype(str)
    for column in embedding_columns:
        normalized[column] = pd.to_numeric(normalized[column], errors="raise")
    normalized = normalized.set_index(key_column, drop=False)

    metadata = _read_sidecar_metadata(cache_path)
    metadata.setdefault("source_path", str(cache_path))
    metadata.setdefault("embedding_dim", len(embedding_columns))
    metadata.setdefault("status", "cached")
    return CachedEmbeddingStore(
        frame=normalized,
        key_column=key_column,
        embedding_columns=embedding_columns,
        metadata=metadata,
    )


def join_embeddings_with_method_features(
    method_features: pd.DataFrame,
    embedding_store: CachedEmbeddingStore | None,
    smiles_column: str = "canonical_smiles",
    missing: str = "zeros",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Join cached molecular embeddings to LC/MS method features."""

    if embedding_store is None:
        return method_features.copy(), {
            "status": "skipped",
            "skip_reason": "embedding_store_unavailable",
            "embedding_columns": [],
            "missing_embedding_count": int(len(method_features)),
        }
    if smiles_column not in method_features.columns:
        return method_features.copy(), {
            "status": "skipped",
            "skip_reason": f"missing_smiles_column:{smiles_column}",
            "embedding_columns": embedding_store.embedding_columns,
            "missing_embedding_count": int(len(method_features)),
        }

    joined = method_features.copy()
    keys = joined[smiles_column].astype(str)
    embeddings = embedding_store.frame.reindex(keys)[embedding_store.embedding_columns].reset_index(drop=True)
    missing_mask = embeddings.isna().all(axis=1)
    missing_count = int(missing_mask.sum())
    if missing_count:
        if missing != "zeros":
            return method_features.copy(), {
                "status": "skipped",
                "skip_reason": "missing_cached_embeddings",
                "embedding_columns": embedding_store.embedding_columns,
                "missing_embedding_count": missing_count,
            }
        embeddings = embeddings.fillna(0.0)
    joined = pd.concat([joined.reset_index(drop=True), embeddings.astype(float)], axis=1)

    status = "partial" if missing_count else "joined"
    skip_reason = "missing_cached_embeddings_filled_with_zeros" if missing_count else None
    metadata = {
        "status": status,
        "skip_reason": skip_reason,
        "embedding_columns": embedding_store.embedding_columns,
        "missing_embedding_count": missing_count,
        "encoder_metadata": embedding_store.metadata,
    }
    return joined, metadata


def _resolve_encoder(encoder_family: str, model_id: str | None) -> tuple[str, str | None]:
    key = str(encoder_family).strip().lower().replace("-", "_")
    family, default_model_id = DEFAULT_ENCODERS.get(key, (encoder_family, None))
    return family, model_id or default_model_id


def _read_sidecar_metadata(cache_path: Path) -> dict[str, Any]:
    sidecar = cache_path.with_suffix(".meta.json")
    if not sidecar.exists():
        return {}
    return json.loads(sidecar.read_text(encoding="utf-8"))
