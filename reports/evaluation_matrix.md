# Evaluation Matrix

Long-form diagnostics for grouped CV, final grouped holdout, source-family holdout, method holdout, and column-family holdout. `normalized_mae_runtime_pct` is reported for RT rows as MAE divided by mean runtime for the evaluated rows.

| validation_scope | target | model | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_grouped_holdout | rt_min | linear_ridge | test | 42533 | 2.253 | 3.296 | 0.712 | 0.758 | 10.261 |
| final_grouped_holdout | rt_min | random_forest | test | 42533 | 1.464 | 2.375 | 0.851 | 0.861 | 6.666 |
| final_grouped_holdout | rt_min | extra_trees | test | 42533 | 1.429 | 2.313 | 0.858 | 0.867 | 6.507 |
| final_grouped_holdout | rt_min | hist_gradient_boosting | test | 42533 | 1.785 | 2.607 | 0.82 | 0.817 | 8.126 |
| final_grouped_holdout | quality_score | linear_ridge | test | 42533 | 0.0 | 0.002 | 0.524 | 0.017 |  |
| final_grouped_holdout | quality_score | random_forest | test | 42533 | 0.0 | 0.001 | 0.904 | 1.0 |  |
| final_grouped_holdout | quality_score | extra_trees | test | 42533 | 0.0 | 0.001 | 0.836 | 1.0 |  |
| final_grouped_holdout | quality_score | hist_gradient_boosting | test | 42533 | 0.0 | 0.002 | 0.391 | 0.04 |  |
| group_kfold | rt_min | linear_ridge | GroupKFold | 17367 | 3.602 | 5.456 | 0.724 | 0.818 | 16.342 |
| group_kfold | rt_min | random_forest | GroupKFold | 17367 | 1.94 | 3.302 | 0.899 | 0.933 | 8.803 |
| group_kfold | rt_min | extra_trees | GroupKFold | 17367 | 1.85 | 3.14 | 0.908 | 0.94 | 8.396 |
| group_kfold | rt_min | hist_gradient_boosting | GroupKFold | 17367 | 2.156 | 3.4 | 0.893 | 0.923 | 9.782 |
| group_kfold | quality_score | linear_ridge | GroupKFold | 17367 | 0.0 | 0.003 | 0.759 | 0.045 |  |
| group_kfold | quality_score | random_forest | GroupKFold | 17367 | 0.0 | 0.001 | 0.955 | 1.0 |  |
| group_kfold | quality_score | extra_trees | GroupKFold | 17367 | 0.0 | 0.001 | 0.966 | 1.0 |  |
| group_kfold | quality_score | hist_gradient_boosting | GroupKFold | 17367 | 0.0 | 0.005 | 0.437 | 0.063 |  |
| source_family_holdout | rt_min | linear_ridge | MCMRT | 10073 | 4.207 | 5.889 | 0.658 | 0.741 | 13.067 |
| source_family_holdout | rt_min | random_forest | MCMRT | 10073 | 2.255 | 3.534 | 0.877 | 0.913 | 7.006 |
| source_family_holdout | rt_min | extra_trees | MCMRT | 10073 | 2.422 | 3.742 | 0.862 | 0.901 | 7.523 |
| source_family_holdout | rt_min | hist_gradient_boosting | MCMRT | 10073 | 2.375 | 3.537 | 0.877 | 0.907 | 7.379 |
| source_family_holdout | quality_score | linear_ridge | MCMRT | 10073 | 0.082 | 0.082 |  |  |  |
| source_family_holdout | quality_score | random_forest | MCMRT | 10073 | 0.002 | 0.002 |  |  |  |
| source_family_holdout | quality_score | extra_trees | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | MCMRT | 10073 | 0.038 | 0.057 |  |  |  |
| source_family_holdout | rt_min | linear_ridge | RepoRT | 4491 | 7.895 | 10.621 | 0.124 | 0.354 | 32.499 |
| source_family_holdout | rt_min | random_forest | RepoRT | 4491 | 4.364 | 6.606 | 0.661 | 0.628 | 17.962 |
| source_family_holdout | rt_min | extra_trees | RepoRT | 4491 | 4.239 | 6.543 | 0.668 | 0.662 | 17.447 |
| source_family_holdout | rt_min | hist_gradient_boosting | RepoRT | 4491 | 4.651 | 6.564 | 0.665 | 0.639 | 19.144 |
| source_family_holdout | quality_score | linear_ridge | RepoRT | 4491 | 0.336 | 0.373 | -2210.296 | -0.049 |  |
| source_family_holdout | quality_score | random_forest | RepoRT | 4491 | 0.059 | 0.066 | -68.858 | 0.058 |  |
| source_family_holdout | quality_score | extra_trees | RepoRT | 4491 | 0.072 | 0.081 | -103.86 | 0.058 |  |
| source_family_holdout | quality_score | hist_gradient_boosting | RepoRT | 4491 | 0.011 | 0.021 | -5.747 | 0.058 |  |
| source_family_holdout | rt_min | linear_ridge | ReTiNA | 2439 | 7.414 | 9.451 | -0.366 | 0.438 | 34.945 |
| source_family_holdout | rt_min | random_forest | ReTiNA | 2439 | 3.63 | 4.691 | 0.664 | 0.676 | 17.11 |
| source_family_holdout | rt_min | extra_trees | ReTiNA | 2439 | 3.075 | 3.757 | 0.784 | 0.777 | 14.495 |
| source_family_holdout | rt_min | hist_gradient_boosting | ReTiNA | 2439 | 3.448 | 4.387 | 0.706 | 0.744 | 16.25 |
| source_family_holdout | quality_score | linear_ridge | ReTiNA | 2439 | 0.005 | 0.006 |  |  |  |
| source_family_holdout | quality_score | random_forest | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | extra_trees | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | ReTiNA | 2439 | 0.012 | 0.031 |  |  |  |
| source_family_holdout | rt_min | linear_ridge | METLIN_SMRT_Figshare | 357 | 2.67 | 3.382 | 0.167 | 0.445 | 11.61 |
| source_family_holdout | rt_min | random_forest | METLIN_SMRT_Figshare | 357 | 2.347 | 3.155 | 0.274 | 0.595 | 10.203 |
| source_family_holdout | rt_min | extra_trees | METLIN_SMRT_Figshare | 357 | 2.395 | 3.087 | 0.306 | 0.539 | 10.414 |
| source_family_holdout | rt_min | hist_gradient_boosting | METLIN_SMRT_Figshare | 357 | 2.373 | 3.185 | 0.261 | 0.512 | 10.317 |
| source_family_holdout | quality_score | linear_ridge | METLIN_SMRT_Figshare | 357 | 0.015 | 0.015 |  |  |  |
| source_family_holdout | quality_score | random_forest | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | extra_trees | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 3.369 | 4.337 | 0.689 | 0.842 | 11.823 |
| method_holdout | rt_min | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.674 | 2.457 | 0.9 | 0.966 | 5.873 |
| method_holdout | rt_min | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.56 | 2.057 | 0.93 | 0.974 | 5.474 |
| method_holdout | rt_min | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.624 | 2.16 | 0.923 | 0.964 | 5.699 |
| method_holdout | quality_score | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.014 | 0.014 |  |  |  |
| method_holdout | quality_score | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.001 |  |  |  |
| method_holdout | rt_min | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 6.912 | 10.33 | 0.688 | 0.87 | 14.475 |
| method_holdout | rt_min | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.884 | 5.832 | 0.901 | 0.955 | 6.04 |
| method_holdout | rt_min | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.716 | 4.724 | 0.935 | 0.959 | 5.689 |
| method_holdout | rt_min | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.993 | 5.245 | 0.92 | 0.968 | 6.269 |
| method_holdout | quality_score | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 2.254 | 2.914 | 0.668 | 0.877 | 10.482 |
| method_holdout | rt_min | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.764 | 1.0 | 0.961 | 0.977 | 3.554 |
| method_holdout | rt_min | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.631 | 0.817 | 0.974 | 0.989 | 2.935 |
| method_holdout | rt_min | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 1.014 | 1.372 | 0.926 | 0.959 | 4.718 |
| method_holdout | quality_score | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.013 |  |  |  |
| method_holdout | quality_score | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.001 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | C18 | 13064 | 5.188 | 7.142 | 0.577 | 0.693 | 16.8 |
| column_family_holdout | rt_min | random_forest | C18 | 13064 | 2.978 | 4.849 | 0.805 | 0.854 | 9.643 |
| column_family_holdout | rt_min | extra_trees | C18 | 13064 | 3.023 | 4.899 | 0.801 | 0.862 | 9.79 |
| column_family_holdout | rt_min | hist_gradient_boosting | C18 | 13064 | 3.034 | 4.966 | 0.796 | 0.861 | 9.825 |
| column_family_holdout | quality_score | linear_ridge | C18 | 13064 | 0.046 | 0.05 |  |  |  |
| column_family_holdout | quality_score | random_forest | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | extra_trees | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | C18 | 13064 | 0.003 | 0.008 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | unknown | 4291 | 5.176 | 7.684 | -0.235 | 0.693 | 24.709 |
| column_family_holdout | rt_min | random_forest | unknown | 4291 | 2.51 | 3.497 | 0.744 | 0.792 | 11.983 |
| column_family_holdout | rt_min | extra_trees | unknown | 4291 | 2.396 | 3.194 | 0.787 | 0.832 | 11.438 |
| column_family_holdout | rt_min | hist_gradient_boosting | unknown | 4291 | 2.677 | 3.685 | 0.716 | 0.768 | 12.777 |
| column_family_holdout | quality_score | linear_ridge | unknown | 4291 | 0.009 | 0.012 |  |  |  |
| column_family_holdout | quality_score | random_forest | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | extra_trees | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | unknown | 4291 | 0.012 | 0.032 |  |  |  |
