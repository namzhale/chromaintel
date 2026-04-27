# Model Benchmark Matrix

Unified tabular benchmark exported from `reports/evaluation_matrix.csv`. Lower MAE/RMSE and lower normalized MAE are better; higher R2/Spearman is better. Optional graph and transformer branches are documented separately under `reports/benchmarks/` until full training dependencies are installed.

| model_family | feature_set | target | split | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| extra_trees | core | quality_score | column_family_holdout | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | column_family_holdout | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | column_family_holdout | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | column_family_holdout | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | C18 | 13064 | 0.004 | 0.009 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | unknown | 4291 | 0.009 | 0.012 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | unknown | 4291 | 0.013 | 0.039 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | C18 | 13064 | 0.046 | 0.05 |  |  |  |
| random_forest | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.001 | 0.904 | 1.0 |  |
| extra_trees | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.001 | 0.868 | 1.0 |  |
| linear_ridge | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.002 | 0.524 | 0.017 |  |
| hist_gradient_boosting | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.002 | 0.286 | 0.033 |  |
| extra_trees | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.001 | 0.946 | 1.0 |  |
| random_forest | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.002 | 0.947 | 1.0 |  |
| linear_ridge | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.003 | 0.759 | 0.045 |  |
| hist_gradient_boosting | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.005 | 0.353 | 0.06 |  |
| random_forest | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.001 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.001 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.013 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.014 | 0.014 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| linear_ridge | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.005 | 0.006 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.011 | 0.028 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.012 | 0.022 | -6.52 | 0.058 |  |
| linear_ridge | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.015 | 0.015 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.041 | 0.055 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.057 | 0.063 | -62.511 | 0.058 |  |
| linear_ridge | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.081 | 0.082 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.086 | 0.096 | -145.45 | 0.058 |  |
| linear_ridge | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.336 | 0.373 | -2211.69 | -0.049 |  |
| random_forest | core | rt_min | column_family_holdout | unknown | 4291 | 2.424 | 3.348 | 0.766 | 0.807 | 11.573 |
| extra_trees | core | rt_min | column_family_holdout | unknown | 4291 | 2.448 | 3.287 | 0.774 | 0.812 | 11.685 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | unknown | 4291 | 2.721 | 3.79 | 0.7 | 0.75 | 12.989 |
| extra_trees | core | rt_min | column_family_holdout | C18 | 13064 | 2.879 | 4.616 | 0.823 | 0.873 | 9.322 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | C18 | 13064 | 2.894 | 4.775 | 0.811 | 0.877 | 9.373 |
| random_forest | core | rt_min | column_family_holdout | C18 | 13064 | 2.92 | 4.722 | 0.815 | 0.86 | 9.456 |
| linear_ridge | core | rt_min | column_family_holdout | C18 | 13064 | 5.046 | 7.016 | 0.592 | 0.711 | 16.341 |
| linear_ridge | core | rt_min | column_family_holdout | unknown | 4291 | 5.081 | 7.462 | -0.165 | 0.692 | 24.257 |
| extra_trees | core | rt_min | final_grouped_holdout | test | 42533 | 1.187 | 1.994 | 0.895 | 0.909 | 5.405 |
| random_forest | core | rt_min | final_grouped_holdout | test | 42533 | 1.244 | 2.104 | 0.883 | 0.903 | 5.664 |
| hist_gradient_boosting | core | rt_min | final_grouped_holdout | test | 42533 | 1.575 | 2.322 | 0.857 | 0.863 | 7.17 |
| linear_ridge | core | rt_min | final_grouped_holdout | test | 42533 | 2.077 | 3.099 | 0.746 | 0.803 | 9.46 |
| extra_trees | core | rt_min | group_kfold | GroupKFold | 17367 | 1.639 | 2.874 | 0.923 | 0.949 | 7.439 |
| random_forest | core | rt_min | group_kfold | GroupKFold | 17367 | 1.756 | 2.991 | 0.917 | 0.944 | 7.969 |
| hist_gradient_boosting | core | rt_min | group_kfold | GroupKFold | 17367 | 1.912 | 3.049 | 0.914 | 0.936 | 8.675 |
| linear_ridge | core | rt_min | group_kfold | GroupKFold | 17367 | 3.503 | 5.284 | 0.741 | 0.831 | 15.894 |
| extra_trees | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.641 | 0.807 | 0.975 | 0.99 | 2.98 |
| random_forest | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.72 | 0.924 | 0.967 | 0.983 | 3.348 |
| hist_gradient_boosting | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.9 | 1.209 | 0.943 | 0.972 | 4.188 |
| hist_gradient_boosting | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.475 | 1.921 | 0.939 | 0.972 | 5.174 |
| extra_trees | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.515 | 1.932 | 0.938 | 0.974 | 5.317 |
| random_forest | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.73 | 2.584 | 0.89 | 0.966 | 6.071 |
| linear_ridge | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 2.221 | 2.823 | 0.689 | 0.913 | 10.332 |
| hist_gradient_boosting | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.48 | 4.537 | 0.94 | 0.98 | 5.193 |
| random_forest | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.688 | 5.447 | 0.913 | 0.968 | 5.629 |
| extra_trees | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.761 | 4.695 | 0.936 | 0.964 | 5.783 |
| linear_ridge | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 3.049 | 3.918 | 0.746 | 0.877 | 10.697 |
| linear_ridge | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 6.65 | 9.958 | 0.71 | 0.886 | 13.926 |
| random_forest | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.197 | 3.424 | 0.884 | 0.92 | 6.825 |
| hist_gradient_boosting | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.223 | 3.306 | 0.892 | 0.917 | 6.904 |
| hist_gradient_boosting | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.228 | 2.935 | 0.372 | 0.621 | 9.688 |
| extra_trees | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.288 | 3.453 | 0.882 | 0.913 | 7.107 |
| random_forest | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.319 | 3.045 | 0.324 | 0.611 | 10.081 |
| linear_ridge | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.539 | 3.197 | 0.255 | 0.561 | 11.038 |
| extra_trees | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.579 | 3.219 | 0.245 | 0.61 | 11.214 |
| extra_trees | core | rt_min | source_family_holdout | ReTiNA | 2439 | 3.081 | 3.788 | 0.781 | 0.748 | 14.521 |
