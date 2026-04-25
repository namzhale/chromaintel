# Internal Lab Data Onboarding

This guide describes how a bioanalytical LC-MS/MS laboratory should prepare historical method-development runs for ChromaIntel training and evaluation.

## Goal

Internal data should teach the model what public RT datasets usually cannot:

- matrix effects in plasma, serum, urine, whole blood, tissue homogenate, and buffer;
- accepted and failed BE-style assay development attempts;
- MRM transitions, source conditions, and practical sensitivity limits;
- chromatographic failure modes such as carryover, low intensity, poor resolution, peak tailing, and unstable retention time.

Use public datasets such as RepoRT and MCMRT for pretraining and benchmarking. Use internal data for calibration and real laboratory decision support.

## File To Use

Start from:

```text
data/templates/internal_lab_historical_runs_template.csv
```

The data dictionary is:

```text
data/templates/internal_lab_data_dictionary.md
```

Keep one row per analyte result, transition, or method-development observation. If a single run measures multiple analytes, add one row per analyte so compound structure, transition, RT, and peak quality remain explicit.

## Minimum Required Columns

Every row intended for training should include:

- `run_id`
- `compound_name`
- `smiles`
- `matrix`
- `column_name`
- `mobile_phase_a`
- `mobile_phase_b`
- `ion_mode`
- `rt_min`
- `success_flag`

For LC-MS/MS MRM data, also include whenever available:

- `precursor_mz`
- `product_mz`
- `collision_energy_v`
- `peak_area`
- `peak_height`
- `sn_ratio`
- `tailing_factor`
- `asymmetry`
- `resolution`

Rows without SMILES can still be previewed, but they are weaker for model training because RDKit descriptors and compound identity grouping cannot be computed reliably.

## Recommended Controlled Vocabulary

Use consistent values so categorical encoders learn chemistry rather than spelling differences.

### Matrix

Recommended values:

- `plasma`
- `serum`
- `urine`
- `whole_blood`
- `tissue_homogenate`
- `buffer`
- `solvent_standard`

### Sample Preparation

Recommended values:

- `protein_precipitation`
- `liquid_liquid_extraction`
- `solid_phase_extraction`
- `dilute_and_shoot`
- `derivatization`
- `standard_solution`

### Ion Mode

Allowed values:

- `positive`
- `negative`
- `both`
- `unknown`

### Column Chemistry

Recommended values:

- `C18`
- `C8`
- `phenyl`
- `biphenyl`
- `HILIC`
- `amide`
- `mixed_mode`
- `ion_exchange`

## What Counts As A Useful Row

Do not upload only successful final methods. Failed and borderline development attempts are valuable because they teach the recommendation engine what to avoid.

Include rows like:

- accepted method: clean peak, acceptable RT, adequate sensitivity, no critical interference;
- low intensity: weak area/height or low S/N even when RT is acceptable;
- poor resolution: coelution, matrix interference, internal standard overlap, or critical pair not separated;
- carryover: unacceptable blank response after high standard;
- bad peak shape: tailing/asymmetry, shoulder peak, broad peak, split peak;
- unstable RT: drift across injections, batches, or matrices;
- impractical method: runtime too long, pressure too high, solvent/pH outside lab-approved range.

Set `success_flag=False` for failed attempts and describe the reason in `notes`.

## Numeric Range Checks

Before import, review these practical ranges:

- `ph`: 0 to 14
- `flow_ml_min`: greater than 0
- `injection_ul`: greater than 0
- `temperature_c`: usually 15 to 90 for LC columns
- `initial_organic_pct`: 0 to 100
- `final_organic_pct`: 0 to 100
- `gradient_duration_min`: greater than 0 for gradient methods
- `total_runtime_min`: greater than or equal to `gradient_duration_min`
- `rt_min`: greater than 0 and less than or equal to `total_runtime_min` when runtime is known
- `sn_ratio`: non-negative
- `tailing_factor`: positive when reported
- `asymmetry`: positive when reported
- `resolution`: non-negative

Rows outside these ranges should be fixed, excluded, or explicitly justified in `notes`.

## Gradient Guidance

Prefer structured gradient fields in addition to free text:

- `initial_organic_pct`
- `final_organic_pct`
- `gradient_duration_min`
- `total_runtime_min`

Use `gradient_profile` for the human-readable method, for example:

```text
5-95%B over 5.0 min, hold 0.8 min, re-equilibrate to 5%B by 5.8 min
```

If the gradient has multiple ramps or isocratic segments, keep the full profile in `gradient_profile`; the MVP will still use the simplified fields for first-pass modeling.

## Duplicate Handling

Duplicate rows are not always bad. Replicates are useful when they represent real repeated injections or batches.

Use unique `run_id` values. If the same compound/method appears multiple times:

- keep replicates when they are separate injections, batches, matrices, or instruments;
- remove accidental spreadsheet duplicates;
- note batch, instrument, analyst, or study identifiers in `notes` until dedicated fields are added.

## Import And Preview Workflow

1. Copy the template CSV.
2. Fill a small pilot batch first, for example 50 to 200 rows.
3. Open the Streamlit Admin/import page and preview the file.
4. Fix invalid SMILES, missing required fields, invalid numeric ranges, and duplicate run IDs.
5. Import a larger historical batch.
6. Retrain and compare:
   - public-only performance;
   - public plus internal performance;
   - internal holdout performance;
   - matrix-specific and column-family performance.

## Privacy And Audit Notes

Do not include patient identifiers, subject IDs, accession numbers, or confidential study labels in training exports. Use anonymized study or batch labels only when needed for validation grouping.

Keep recommendation inputs and outputs auditable. For any future production use, store:

- original user input;
- model artifact version;
- training dataset version;
- recommendation search constraints;
- top candidates and score decomposition;
- analyst decision and outcome.

## First Internal Data Target

For the next model iteration, aim for:

- at least 1,000 internal rows;
- at least 100 unique analytes;
- multiple matrices, especially plasma and serum;
- both positive and negative ionization;
- accepted and failed development attempts;
- at least one consistent platform or instrument family;
- explicit peak quality fields for a subset of rows.

This is enough to start calibrating public RT models toward real bioanalytical method-development behavior.
