# Extended Molecular Descriptors Retraining

## Existing Implementation Audit

- Already exists: RDKit descriptor calculator, canonical model matrix builder, tabular RT/quality training pipeline, permutation feature importance, grouped holdout/CV reports, PDF dashboard generator.
- Partially exists: descriptor set covered core physicochemical fields only; pKa, charge, VSA/surface, functional-group counts, and richer shape descriptors were absent from model features.
- Newly implemented: expanded descriptor calculation, feature matrix inclusion, tests for descriptor behavior and importance grouping.
- Intentionally skipped: true quantum dipole moments and experimental pKa prediction. The current implementation uses transparent RDKit/Gasteiger/SMARTS proxies that run locally without GPU or proprietary tools.
- Files reused: `app/services/descriptors.py`, `app/services/feature_engineering.py`, `app/models/training.py`, existing training/report scripts.
- Files modified: descriptor service, feature engineering service, training feature-group annotation, descriptor/feature/training tests.
- Files created: this report.

## Descriptor Additions

The compound feature group now includes 55 molecular descriptors. New fields include:

- Surface and polarity: `labute_asa`, `slogp_vsa_hydrophobic`, `slogp_vsa_polar`, `peoe_vsa_positive`, `peoe_vsa_negative`, `smr_vsa_total`.
- Ionization and pKa proxies: `strongest_acid_pka_proxy`, `strongest_base_pka_proxy`, `acid_ionized_fraction_ph3/ph7`, `base_ionized_fraction_ph3/ph7`, `estimated_net_charge_ph3/ph7`, `estimated_logd_ph3/ph7`.
- Functional groups: carboxylic acid, phenol, alcohol, primary/secondary/tertiary amine, amide, sulfonamide, phosphate, nitrile, acidic/basic group counts.
- Charge and dipole proxies: Gasteiger min/max/mean absolute charge and a 2D charge-displacement dipole proxy.
- Shape and complexity: exact mass, molar refractivity, hetero atom count, halogen count, valence electrons, ring counts, aromatic atom fraction, Bertz complexity, bridgehead/spiro atoms.

## Retraining Summary

Command:

```powershell
.\.venv\Scripts\python.exe scripts\train_models.py --feature-set core --quick
```

Rows used: 213,941.

Model matrix: 88 columns, 73 model features, 55 compound descriptors.

Best RT model: `extra_trees`.

Final grouped holdout RT metrics:

| Model | MAE min | RMSE min | R2 | Spearman | Normalized MAE % runtime |
| --- | ---: | ---: | ---: | ---: | ---: |
| extra_trees | 1.187 | 1.994 | 0.895 | 0.909 | 5.405 |
| random_forest | 1.244 | 2.104 | 0.883 | 0.903 | 5.664 |
| hist_gradient_boosting | 1.575 | 2.322 | 0.857 | 0.863 | 7.170 |
| linear_ridge | 2.077 | 3.099 | 0.746 | 0.803 | 9.460 |

## Feature Importance Selection

Top useful molecular descriptors by permutation importance:

| Feature | Importance | Interpretation |
| --- | ---: | --- |
| `estimated_logd_ph3` | 0.845 | pH-adjusted hydrophobicity proxy under acidic LC/MS conditions |
| `estimated_logd_ph7` | 0.777 | neutral/physiological ionization-adjusted hydrophobicity proxy |
| `logp` | 0.638 | baseline hydrophobicity |
| `slogp_vsa_hydrophobic` | 0.128 | hydrophobic surface area |
| `hbond_donors` | 0.082 | hydrogen-bonding effect on retention/selectivity |
| `bertz_complexity` | 0.064 | molecular complexity/shape proxy |
| `strongest_base_pka_proxy` | 0.052 | basic functional-group ionization proxy |
| `gasteiger_charge_max` | 0.051 | partial-charge distribution |
| `molar_refractivity` | 0.046 | polarizability/volume proxy |
| `peoe_vsa_negative` | 0.044 | negative partial-charge surface area |

Retention remains dominated by LC method features (`gradient_duration_min`, `total_runtime_min`, organic %, column/mobile phase), which is expected for method-conditioned RT prediction.

## Label Readiness

Measured labels are available for `rt_min`. Peak-shape targets (`asymmetry`, `tailing_factor`, `peak_width_base_min`, `peak_width_half_height_min`, `resolution`, `sn_ratio`, `peak_area`, `peak_height`) remain at 0 measured rows in the current public dataset. They should not be claimed as supervised measured models until internal lab exports provide those columns.

## Verification

- Descriptor and feature engineering tests: passed.
- Training tests: passed.
- Dashboard PDF regenerated: `reports/chromaintel_dashboard_report.pdf`.
