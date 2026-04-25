# Canonical Registry Schema

ChromaIntel keeps the existing nullable training dataset schema in
`app/schemas/dataset.py`. The registry-level schema in
`app/schemas/canonical.py` formalizes how public and internal observations are
grouped before they are deduplicated, scored, or promoted into database-backed
entities.

## Registry Field Groups

| Group | Purpose | Fields |
| --- | --- | --- |
| compound | Compound identity and external identifiers | `compound_name`, `smiles`, `canonical_smiles`, `inchikey`, `pubchem_cid`, `chembl_id` |
| lc_method | Chromatography identity and LC conditions | `column_name`, `column_chemistry`, `stationary_phase_type`, `chromatography_mode`, `mobile_phase_a`, `mobile_phase_b`, `ph`, `gradient_profile`, `initial_organic_pct`, `final_organic_pct`, `gradient_duration_min`, `total_runtime_min`, `temperature_c`, `flow_ml_min`, `injection_ul` |
| ms_method | MS acquisition identity | `ion_mode`, `precursor_mz`, `product_mz`, `collision_energy`, `polarity`, `ms_platform` |
| sample_context | Biological or sample-preparation context | `matrix`, `sample_prep`, `species`, `biofluid`, `dilution_factor` |
| observation | Run-level measured outcome | `rt_min`, `success_flag`, `run_id`, `batch_id`, `replicate_id` |
| peak_metrics | Peak shape and signal quality | `peak_area`, `peak_height`, `sn_ratio`, `tailing_factor`, `asymmetry`, `resolution`, `quality_score` |
| provenance | Source traceability | `source_dataset`, `source_record_id`, `source_url`, `license`, `notes` |

Required registry fields are `canonical_smiles`, `column_name`,
`mobile_phase_a`, `mobile_phase_b`, `rt_min`, and `source_dataset`. The helper
`missing_required_fields(record)` reports absent, null, or blank values in this
stable order. `validate_registry_record(record)` adds lightweight range checks
for retention time, pH, and organic percentages.

## Method Hash

`method_hash(record)` creates a deterministic 16-character SHA-256 digest from
normalized LC method fields:

`column_name`, `column_chemistry`, `stationary_phase_type`,
`chromatography_mode`, `mobile_phase_a`, `mobile_phase_b`, `ph`,
`gradient_profile`, `initial_organic_pct`, `final_organic_pct`,
`gradient_duration_min`, `flow_ml_min`, `temperature_c`, and
`total_runtime_min`.

Text is stripped, whitespace-collapsed, and lowercased. Numeric strings and
numeric values normalize to rounded floats, so `3.2`, `3.200`, and `"3.2000"`
hash identically.

## Duplicate Key Policy

Registry duplicates are observations with the same:

1. Compound identity: `inchikey` when present, otherwise `canonical_smiles`.
2. LC method identity: `method_hash(record)`.
3. MS identity: normalized `ion_mode`, `precursor_mz`, and `product_mz`.
4. Sample context: normalized `matrix`.
5. Retention time: `rt_min` rounded to two decimals.

The helper `duplicate_key(record)` returns this tuple. The policy intentionally
keeps source provenance outside the duplicate key so independent sources can be
merged while their `source_dataset` and `source_record_id` values remain
available for traceability.

## Source Quality Score

`source_quality_score(record)` returns a 0 to 1 completeness score with these
weights:

| Component | Weight | Fields |
| --- | ---: | --- |
| structure | 0.25 | `canonical_smiles`, `inchikey` |
| retention time | 0.20 | `rt_min` |
| LC metadata | 0.20 | `column_name`, `mobile_phase_a`, `mobile_phase_b`, `gradient_profile` |
| MS metadata | 0.15 | `ion_mode`, `precursor_mz`, `product_mz` |
| sample context | 0.10 | `matrix` |
| peak metrics | 0.10 | `peak_area`, `peak_height`, `sn_ratio`, `tailing_factor`, `asymmetry`, `resolution` |

The score is monotonic with completeness: filling more weighted fields cannot
lower the score.

## Database Notes

The current SQLAlchemy schema already separates compounds, structures,
datasets, methods, gradient steps, MS settings, runs, peak metrics,
predictions, recommendations, and audit logs. This schema document does not add
tables or alter migrations. A future docs-only Alembic migration can describe
registry views once the database ingestion path consumes these helpers.
