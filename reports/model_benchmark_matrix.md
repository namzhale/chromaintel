# Model Benchmark Matrix

Unified tabular benchmark exported from `reports/evaluation_matrix.csv`. Lower MAE/RMSE and lower normalized MAE are better; higher R2/Spearman is better. Optional graph and transformer branches are documented separately under `reports/benchmarks/` until full training dependencies are installed.

| model_family | feature_set | target | split | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| extra_trees | core | quality_score | column_family_holdout | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | column_family_holdout | C18 | 13064 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | column_family_holdout | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | column_family_holdout | unknown | 4291 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | C18 | 13064 | 0.003 | 0.008 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | unknown | 4291 | 0.009 | 0.012 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | unknown | 4291 | 0.012 | 0.032 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | C18 | 13064 | 0.046 | 0.05 |  |  |  |
| random_forest | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.001 | 0.904 | 1.0 |  |
| extra_trees | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.001 | 0.836 | 1.0 |  |
| linear_ridge | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.002 | 0.524 | 0.017 |  |
| hist_gradient_boosting | core | quality_score | final_grouped_holdout | test | 42533 | 0.0 | 0.002 | 0.391 | 0.04 |  |
| extra_trees | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.001 | 0.966 | 1.0 |  |
| random_forest | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.001 | 0.955 | 1.0 |  |
| linear_ridge | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.003 | 0.759 | 0.045 |  |
| hist_gradient_boosting | core | quality_score | group_kfold | GroupKFold | 17367 | 0.0 | 0.005 | 0.437 | 0.063 |  |
| random_forest | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.001 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.001 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.013 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.014 | 0.014 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.002 | 0.002 |  |  |  |
| linear_ridge | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.005 | 0.006 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.011 | 0.021 | -5.747 | 0.058 |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | ReTiNA | 2439 | 0.012 | 0.031 |  |  |  |
| linear_ridge | core | quality_score | source_family_holdout | METLIN_SMRT_Figshare | 357 | 0.015 | 0.015 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.038 | 0.057 |  |  |  |
| random_forest | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.059 | 0.066 | -68.858 | 0.058 |  |
| extra_trees | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.072 | 0.081 | -103.86 | 0.058 |  |
| linear_ridge | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.082 | 0.082 |  |  |  |
| linear_ridge | core | quality_score | source_family_holdout | RepoRT | 4491 | 0.336 | 0.373 | -2210.296 | -0.049 |  |
| extra_trees | core | rt_min | column_family_holdout | unknown | 4291 | 2.396 | 3.194 | 0.787 | 0.832 | 11.438 |
| random_forest | core | rt_min | column_family_holdout | unknown | 4291 | 2.51 | 3.497 | 0.744 | 0.792 | 11.983 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | unknown | 4291 | 2.677 | 3.685 | 0.716 | 0.768 | 12.777 |
| random_forest | core | rt_min | column_family_holdout | C18 | 13064 | 2.978 | 4.849 | 0.805 | 0.854 | 9.643 |
| extra_trees | core | rt_min | column_family_holdout | C18 | 13064 | 3.023 | 4.899 | 0.801 | 0.862 | 9.79 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | C18 | 13064 | 3.034 | 4.966 | 0.796 | 0.861 | 9.825 |
| linear_ridge | core | rt_min | column_family_holdout | unknown | 4291 | 5.176 | 7.684 | -0.235 | 0.693 | 24.709 |
| linear_ridge | core | rt_min | column_family_holdout | C18 | 13064 | 5.188 | 7.142 | 0.577 | 0.693 | 16.8 |
| extra_trees | core | rt_min | final_grouped_holdout | test | 42533 | 1.429 | 2.313 | 0.858 | 0.867 | 6.507 |
| random_forest | core | rt_min | final_grouped_holdout | test | 42533 | 1.464 | 2.375 | 0.851 | 0.861 | 6.666 |
| hist_gradient_boosting | core | rt_min | final_grouped_holdout | test | 42533 | 1.785 | 2.607 | 0.82 | 0.817 | 8.126 |
| linear_ridge | core | rt_min | final_grouped_holdout | test | 42533 | 2.253 | 3.296 | 0.712 | 0.758 | 10.261 |
| extra_trees | core | rt_min | group_kfold | GroupKFold | 17367 | 1.85 | 3.14 | 0.908 | 0.94 | 8.396 |
| random_forest | core | rt_min | group_kfold | GroupKFold | 17367 | 1.94 | 3.302 | 0.899 | 0.933 | 8.803 |
| hist_gradient_boosting | core | rt_min | group_kfold | GroupKFold | 17367 | 2.156 | 3.4 | 0.893 | 0.923 | 9.782 |
| linear_ridge | core | rt_min | group_kfold | GroupKFold | 17367 | 3.602 | 5.456 | 0.724 | 0.818 | 16.342 |
| extra_trees | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.631 | 0.817 | 0.974 | 0.989 | 2.935 |
| random_forest | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.764 | 1.0 | 0.961 | 0.977 | 3.554 |
| hist_gradient_boosting | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 1.014 | 1.372 | 0.926 | 0.959 | 4.718 |
| extra_trees | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.56 | 2.057 | 0.93 | 0.974 | 5.474 |
| hist_gradient_boosting | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.624 | 2.16 | 0.923 | 0.964 | 5.699 |
| random_forest | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.674 | 2.457 | 0.9 | 0.966 | 5.873 |
| linear_ridge | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 2.254 | 2.914 | 0.668 | 0.877 | 10.482 |
| extra_trees | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.716 | 4.724 | 0.935 | 0.959 | 5.689 |
| random_forest | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.884 | 5.832 | 0.901 | 0.955 | 6.04 |
| hist_gradient_boosting | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.993 | 5.245 | 0.92 | 0.968 | 6.269 |
| linear_ridge | core | rt_min | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 3.369 | 4.337 | 0.689 | 0.842 | 11.823 |
| linear_ridge | core | rt_min | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 6.912 | 10.33 | 0.688 | 0.87 | 14.475 |
| random_forest | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.255 | 3.534 | 0.877 | 0.913 | 7.006 |
| random_forest | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.347 | 3.155 | 0.274 | 0.595 | 10.203 |
| hist_gradient_boosting | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.373 | 3.185 | 0.261 | 0.512 | 10.317 |
| hist_gradient_boosting | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.375 | 3.537 | 0.877 | 0.907 | 7.379 |
| extra_trees | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.395 | 3.087 | 0.306 | 0.539 | 10.414 |
| extra_trees | core | rt_min | source_family_holdout | MCMRT | 10073 | 2.422 | 3.742 | 0.862 | 0.901 | 7.523 |
| linear_ridge | core | rt_min | source_family_holdout | METLIN_SMRT_Figshare | 357 | 2.67 | 3.382 | 0.167 | 0.445 | 11.61 |
| extra_trees | core | rt_min | source_family_holdout | ReTiNA | 2439 | 3.075 | 3.757 | 0.784 | 0.777 | 14.495 |
