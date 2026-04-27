# Feature Importance Without Runtime Proxy Features

This report recalculates RT permutation feature importance after excluding `gradient_duration_min` and `total_runtime_min`. The model still keeps LC composition, organic percentages, gradient slope, column/mobile-phase categories, MS mode, and molecular descriptors.

## Model Metrics

- Ablation mode: `without_both`
- Sample rows: 20000
- Train/test rows: 16215 / 3785
- Split group column: `inchikey`
- Train/test group overlap: 0
- Features used: 71
- MAE: 1.657 min
- RMSE: 2.918 min
- R2: 0.899
- Spearman: 0.935

## Top Features

| feature | importance_mean | importance_std | feature_group | importance_z | significance |
| --- | --- | --- | --- | --- | --- |
| gradient_slope_percent_b_min | 2.5809 | 0.0754 | lc_numeric | 34.2412 | positive |
| initial_organic_pct | 1.5063 | 0.019 | lc_numeric | 79.3058 | positive |
| column_name | 0.8157 | 0.0139 | lc_categorical | 58.4834 | positive |
| estimated_logd_ph3 | 0.6808 | 0.0091 | compound_descriptor | 74.9286 | positive |
| estimated_logd_ph7 | 0.615 | 0.0093 | compound_descriptor | 66.3911 | positive |
| logp | 0.6115 | 0.0043 | compound_descriptor | 143.1556 | positive |
| final_organic_pct | 0.3998 | 0.0118 | lc_numeric | 33.9659 | positive |
| mobile_phase_system | 0.3151 | 0.0099 | lc_categorical | 31.729 | positive |
| mobile_phase_b | 0.2924 | 0.0044 | lc_categorical | 66.031 | positive |
| mobile_phase_a | 0.2363 | 0.0026 | lc_categorical | 89.2441 | positive |
| temperature_c | 0.1499 | 0.0042 | lc_numeric | 35.603 | positive |
| flow_ml_min | 0.1099 | 0.007 | lc_numeric | 15.6943 | positive |
| hbond_donors | 0.1034 | 0.0074 | compound_descriptor | 13.8932 | positive |
| peoe_vsa_positive | 0.044 | 0.0023 | compound_descriptor | 19.2204 | positive |
| slogp_vsa_hydrophobic | 0.0417 | 0.0004 | compound_descriptor | 113.9904 | positive |
| exact_mol_wt | 0.0408 | 0.0031 | compound_descriptor | 13.2361 | positive |
| labute_asa | 0.0403 | 0.0044 | compound_descriptor | 9.1509 | positive |
| bertz_complexity | 0.0397 | 0.0034 | compound_descriptor | 11.8048 | positive |
| molar_refractivity | 0.0344 | 0.0045 | compound_descriptor | 7.5943 | positive |
| smr_vsa_total | 0.0291 | 0.0027 | compound_descriptor | 10.778 | positive |
| sulfonamide_count | 0.0251 | 0.0013 | compound_descriptor | 19.454 | positive |
| molecular_weight | 0.0248 | 0.0019 | compound_descriptor | 12.8315 | positive |
| rotatable_bonds | 0.0238 | 0.0012 | compound_descriptor | 19.1912 | positive |
| gasteiger_charge_max | 0.0234 | 0.0038 | compound_descriptor | 6.1423 | positive |
| heavy_atom_count | 0.0217 | 0.0031 | compound_descriptor | 6.9377 | positive |

## Interpretation

After removing direct duration/runtime features, the model should be interpreted through remaining controllable LC conditions and chemistry: organic start/end percentage, gradient slope, column/mobile phase categories, hydrophobicity/logD, surface area, ionization proxies, flow, temperature, and MS polarity. This is the safer feature-importance view for transfer claims and inverse recommendation.
