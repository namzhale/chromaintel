# LC-MS/MS Model Training Summary

## Datasets Used

- Rows used: 12
- Compounds: 8
- Source distribution: {'internal_lab': 5, 'RepoRT': 5, 'METLIN_SMRT': 2}

## Feature Set

The model uses RDKit compound descriptors, simplified LC gradient encodings, column/mobile-phase categories, and MS setting fields. Morgan fingerprints are available from the descriptor pipeline but are not enabled in the small demo training run to avoid overfitting tiny seed data.

## Models Tested

- Linear baseline: Ridge regression
- RandomForestRegressor
- HistGradientBoostingRegressor

## Best Models

- RT model: `linear_ridge`
- Peak quality surrogate: `linear_ridge`

## RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 1.558 | 1.825 | -2.431 | 2.901 | 3.298 | -0.791 |
| random_forest | 1.703 | 1.943 | -2.889 | 2.168 | 2.589 | -0.104 |
| hist_gradient_boosting | 1.733 | 1.994 | -3.096 | 2.072 | 2.678 | -0.182 |

## Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.034 | 0.041 | 0.616 | 0.069 | 0.076 | 0.386 |
| random_forest | 0.058 | 0.059 | 0.202 | 0.085 | 0.089 | 0.172 |
| hist_gradient_boosting | 0.068 | 0.069 | -0.063 | 0.099 | 0.102 | -0.095 |

## Source-wise Performance

| source_dataset | rt_mae |
| --- | --- |
| METLIN_SMRT | 5.006 |
| RepoRT | 2.454 |
| internal_lab | 1.242 |

## Recommendation Proxy Metrics

- Top-k success proxy: candidates are ranked by target RT fit, provisional quality, runtime penalty, and confidence bonus.
- Mean predicted quality score is reported in the GUI recommendation cards.
- Uncertainty proxy: RT residual standard deviation on the test split, currently 2.565 min.

## Current Limitations

- The checked-in dataset is a small mock/demo set, not yet a validated internal laboratory history.
- Public RT datasets often lack peak quality, matrix, sample preparation, and MS transition metadata.
- Peak quality is provisional. Quality score is provisional. It uses observed quality_score when present; otherwise it is a transparent proxy from S/N, resolution, asymmetry, and tailing.
- Source-aware validation is reported by source distribution and source-wise error; larger datasets should use source holdout splits.

## Next Steps

1. Import internal historical BE assay development runs using the internal template.
2. Calibrate RT and quality models on accepted lab methods by instrument platform and matrix.
3. Add explicit uncertainty calibration and applicability-domain checks.
4. Expand candidate search spaces to match available columns, solvents, and validated operating ranges.
