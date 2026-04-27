# Evaluation Matrix

Long-form diagnostics for grouped CV, final grouped holdout, source-family holdout, method holdout, and column-family holdout. `normalized_mae_runtime_pct` is reported for RT rows as MAE divided by mean runtime for the evaluated rows.

| validation_scope | target | model | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_grouped_holdout | rt_min | linear_ridge | test | 42533 | 2.077 | 3.099 | 0.746 | 0.803 | 9.46 |
| final_grouped_holdout | rt_min | random_forest | test | 42533 | 1.244 | 2.104 | 0.883 | 0.903 | 5.664 |
| final_grouped_holdout | rt_min | extra_trees | test | 42533 | 1.187 | 1.994 | 0.895 | 0.909 | 5.405 |
| final_grouped_holdout | rt_min | hist_gradient_boosting | test | 42533 | 1.575 | 2.322 | 0.857 | 0.863 | 7.17 |
| final_grouped_holdout | quality_score | linear_ridge | test | 42533 | 0.0 | 0.002 | 0.524 | 0.017 |  |
| final_grouped_holdout | quality_score | random_forest | test | 42533 | 0.0 | 0.001 | 0.904 | 1.0 |  |
| final_grouped_holdout | quality_score | extra_trees | test | 42533 | 0.0 | 0.001 | 0.868 | 1.0 |  |
| final_grouped_holdout | quality_score | hist_gradient_boosting | test | 42533 | 0.0 | 0.002 | 0.286 | 0.033 |  |
| group_kfold | rt_min | linear_ridge | GroupKFold | 17367 | 3.503 | 5.284 | 0.741 | 0.831 | 15.894 |
| group_kfold | rt_min | random_forest | GroupKFold | 17367 | 1.756 | 2.991 | 0.917 | 0.944 | 7.969 |
| group_kfold | rt_min | extra_trees | GroupKFold | 17367 | 1.639 | 2.874 | 0.923 | 0.949 | 7.439 |
| group_kfold | rt_min | hist_gradient_boosting | GroupKFold | 17367 | 1.912 | 3.049 | 0.914 | 0.936 | 8.675 |
| group_kfold | quality_score | linear_ridge | GroupKFold | 17367 | 0.0 | 0.003 | 0.759 | 0.045 |  |
| group_kfold | quality_score | random_forest | GroupKFold | 17367 | 0.0 | 0.002 | 0.947 | 1.0 |  |
| group_kfold | quality_score | extra_trees | GroupKFold | 17367 | 0.0 | 0.001 | 0.946 | 1.0 |  |
| group_kfold | quality_score | hist_gradient_boosting | GroupKFold | 17367 | 0.0 | 0.005 | 0.353 | 0.06 |  |
| source_family_holdout | rt_min | linear_ridge | MCMRT | 10073 | 4.047 | 5.671 | 0.683 | 0.764 | 12.573 |
| source_family_holdout | rt_min | random_forest | MCMRT | 10073 | 2.197 | 3.424 | 0.884 | 0.92 | 6.825 |
| source_family_holdout | rt_min | extra_trees | MCMRT | 10073 | 2.288 | 3.453 | 0.882 | 0.913 | 7.107 |
| source_family_holdout | rt_min | hist_gradient_boosting | MCMRT | 10073 | 2.223 | 3.306 | 0.892 | 0.917 | 6.904 |
| source_family_holdout | quality_score | linear_ridge | MCMRT | 10073 | 0.081 | 0.082 |  |  |  |
| source_family_holdout | quality_score | random_forest | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | extra_trees | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | MCMRT | 10073 | 0.041 | 0.055 |  |  |  |
| source_family_holdout | rt_min | linear_ridge | RepoRT | 4491 | 7.576 | 10.156 | 0.199 | 0.325 | 31.185 |
| source_family_holdout | rt_min | random_forest | RepoRT | 4491 | 4.305 | 6.628 | 0.659 | 0.649 | 17.722 |
| source_family_holdout | rt_min | extra_trees | RepoRT | 4491 | 4.217 | 6.503 | 0.672 | 0.679 | 17.358 |
| source_family_holdout | rt_min | hist_gradient_boosting | RepoRT | 4491 | 4.477 | 6.44 | 0.678 | 0.631 | 18.428 |
| source_family_holdout | quality_score | linear_ridge | RepoRT | 4491 | 0.336 | 0.373 | -2211.69 | -0.049 |  |
| source_family_holdout | quality_score | random_forest | RepoRT | 4491 | 0.057 | 0.063 | -62.511 | 0.058 |  |
| source_family_holdout | quality_score | extra_trees | RepoRT | 4491 | 0.086 | 0.096 | -145.45 | 0.058 |  |
| source_family_holdout | quality_score | hist_gradient_boosting | RepoRT | 4491 | 0.012 | 0.022 | -6.52 | 0.058 |  |
| source_family_holdout | rt_min | linear_ridge | ReTiNA | 2439 | 7.321 | 9.279 | -0.317 | 0.416 | 34.507 |
| source_family_holdout | rt_min | random_forest | ReTiNA | 2439 | 3.434 | 4.487 | 0.692 | 0.706 | 16.186 |
| source_family_holdout | rt_min | extra_trees | ReTiNA | 2439 | 3.081 | 3.788 | 0.781 | 0.748 | 14.521 |
| source_family_holdout | rt_min | hist_gradient_boosting | ReTiNA | 2439 | 3.447 | 4.482 | 0.693 | 0.706 | 16.247 |
| source_family_holdout | quality_score | linear_ridge | ReTiNA | 2439 | 0.005 | 0.006 |  |  |  |
| source_family_holdout | quality_score | random_forest | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | extra_trees | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | ReTiNA | 2439 | 0.011 | 0.028 |  |  |  |
| source_family_holdout | rt_min | linear_ridge | METLIN_SMRT_Figshare | 357 | 2.539 | 3.197 | 0.255 | 0.561 | 11.038 |
| source_family_holdout | rt_min | random_forest | METLIN_SMRT_Figshare | 357 | 2.319 | 3.045 | 0.324 | 0.611 | 10.081 |
| source_family_holdout | rt_min | extra_trees | METLIN_SMRT_Figshare | 357 | 2.579 | 3.219 | 0.245 | 0.61 | 11.214 |
| source_family_holdout | rt_min | hist_gradient_boosting | METLIN_SMRT_Figshare | 357 | 2.228 | 2.935 | 0.372 | 0.621 | 9.688 |
| source_family_holdout | quality_score | linear_ridge | METLIN_SMRT_Figshare | 357 | 0.015 | 0.015 |  |  |  |
| source_family_holdout | quality_score | random_forest | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | extra_trees | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 3.049 | 3.918 | 0.746 | 0.877 | 10.697 |
| method_holdout | rt_min | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.73 | 2.584 | 0.89 | 0.966 | 6.071 |
| method_holdout | rt_min | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.515 | 1.932 | 0.938 | 0.974 | 5.317 |
| method_holdout | rt_min | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.475 | 1.921 | 0.939 | 0.972 | 5.174 |
| method_holdout | quality_score | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.014 | 0.014 |  |  |  |
| method_holdout | quality_score | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.001 |  |  |  |
| method_holdout | rt_min | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 6.65 | 9.958 | 0.71 | 0.886 | 13.926 |
| method_holdout | rt_min | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.688 | 5.447 | 0.913 | 0.968 | 5.629 |
| method_holdout | rt_min | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.761 | 4.695 | 0.936 | 0.964 | 5.783 |
| method_holdout | rt_min | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.48 | 4.537 | 0.94 | 0.98 | 5.193 |
| method_holdout | quality_score | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 2.221 | 2.823 | 0.689 | 0.913 | 10.332 |
| method_holdout | rt_min | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.72 | 0.924 | 0.967 | 0.983 | 3.348 |
| method_holdout | rt_min | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.641 | 0.807 | 0.975 | 0.99 | 2.98 |
| method_holdout | rt_min | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.9 | 1.209 | 0.943 | 0.972 | 4.188 |
| method_holdout | quality_score | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.013 |  |  |  |
| method_holdout | quality_score | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.001 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | C18 | 13064 | 5.046 | 7.016 | 0.592 | 0.711 | 16.341 |
| column_family_holdout | rt_min | random_forest | C18 | 13064 | 2.92 | 4.722 | 0.815 | 0.86 | 9.456 |
| column_family_holdout | rt_min | extra_trees | C18 | 13064 | 2.879 | 4.616 | 0.823 | 0.873 | 9.322 |
| column_family_holdout | rt_min | hist_gradient_boosting | C18 | 13064 | 2.894 | 4.775 | 0.811 | 0.877 | 9.373 |
| column_family_holdout | quality_score | linear_ridge | C18 | 13064 | 0.046 | 0.05 |  |  |  |
| column_family_holdout | quality_score | random_forest | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | extra_trees | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | C18 | 13064 | 0.004 | 0.009 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | unknown | 4291 | 5.081 | 7.462 | -0.165 | 0.692 | 24.257 |
| column_family_holdout | rt_min | random_forest | unknown | 4291 | 2.424 | 3.348 | 0.766 | 0.807 | 11.573 |
| column_family_holdout | rt_min | extra_trees | unknown | 4291 | 2.448 | 3.287 | 0.774 | 0.812 | 11.685 |
| column_family_holdout | rt_min | hist_gradient_boosting | unknown | 4291 | 2.721 | 3.79 | 0.7 | 0.75 | 12.989 |
| column_family_holdout | quality_score | linear_ridge | unknown | 4291 | 0.009 | 0.012 |  |  |  |
| column_family_holdout | quality_score | random_forest | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | extra_trees | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | unknown | 4291 | 0.013 | 0.039 |  |  |  |
