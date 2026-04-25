# Optional SMILES Transformer Embeddings

Date: 2026-04-25

This module adds a frozen-embedding path for pretrained SMILES transformers without making neural dependencies mandatory.

## Runtime Contract

`app/models/transformer_embeddings.py` is intentionally standalone. The existing tabular training path in `app/models/training.py` is not required to import it. This keeps the MVP usable with the current `requirements.txt`, which has no `transformers` or `torch` dependency.

`scripts/prepare_dl_datasets.py` writes `data/processed/dl/smiles_transformer_manifest.csv` for frozen-embedding or later transformer experiments. The manifest contains canonical SMILES, method context, `rt_min`, deterministic or source-provided split labels, and encoder metadata. It does not tokenize, download, encode, fine-tune, or import neural dependencies.

## Supported Modes

| Mode | Status | Network behavior |
| --- | --- | --- |
| Cached embeddings | Implemented | No network. Loads CSV or JSON embedding caches. |
| ChemBERTa availability | Implemented | Checks local Hugging Face config only by default. |
| MolFormer availability | Implemented | Checks local Hugging Face config only by default. |
| Generic Hugging Face availability | Implemented | Requires caller-provided local model id. |
| Live encoding | Intentionally gated | Wrapper exists, but encoding is not enabled in offline tests. |
| Fine-tuning | Not implemented | Out of scope for MVP data volume and dependency policy. |

## Cache Format

The loader expects:

- A key column, default `canonical_smiles`.
- Numeric embedding columns prefixed with `tx_emb_`.
- Optional sidecar metadata at the same path with `.meta.json` suffix.

Example:

```csv
canonical_smiles,compound_name,tx_emb_0,tx_emb_1,tx_emb_2
CCO,Ethanol,0.1,0.2,0.3
```

## Feature Join

`join_embeddings_with_method_features` joins cached molecular embeddings onto method-feature rows by SMILES key. If a cache is unavailable, it returns the original frame with `status=skipped`. If some rows are missing from the cache, the default behavior fills embedding values with zeros and reports `status=partial`.

This keeps downstream tabular modeling explicit: transformer columns are additional molecular descriptors, not a replacement for LC method, column, gradient, or MS settings.

## DL Manifest Contract

The SMILES transformer manifest contains the shared DL base columns plus:

- `encoder_family`;
- `encoder_model_id`;
- `encoder_status`;
- `encoder_input`, currently equal to `canonical_smiles`.

The data-prep path filters invalid or missing SMILES with the existing descriptor utility and can cap smoke output with `--max-rows`. Split labels are preserved from `split`, `split_label`, or `data_split` when present; otherwise they are generated with a stable SHA-256 hash over compound identity and the configured seed.

## Provenance

Each joined payload carries metadata including embedding columns, missing count, skip/fill reason, and cache sidecar metadata. Real experiments should record model id, pooling, embedding dimension, source cache path, and model artifact provenance before using these features in validation reports.
