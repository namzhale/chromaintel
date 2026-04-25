# Model Benchmark Matrix

Unified tabular benchmark exported from `reports/evaluation_matrix.csv`. Lower MAE/RMSE and lower normalized MAE are better; higher R2/Spearman is better. Optional graph and transformer branches are documented separately under `reports/benchmarks/` until full training dependencies are installed.

| model_family | feature_set | target | split | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_forest | core | quality_score | column_family_holdout | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | column_family_holdout | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| xgboost | core | quality_score | column_family_holdout | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| catboost | core | quality_score | column_family_holdout | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| catboost | core | quality_score | column_family_holdout | C18 | 13188 | 0.0 | 0.0 |  |  |  |
| xgboost | core | quality_score | column_family_holdout | C18 | 13188 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | column_family_holdout | C18 | 13188 | 0.0 | 0.002 |  |  |  |
| random_forest | core | quality_score | column_family_holdout | C18 | 13188 | 0.001 | 0.001 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | unknown | 1852 | 0.005 | 0.016 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | unknown | 1852 | 0.015 | 0.017 |  |  |  |
| hist_gradient_boosting | core | quality_score | column_family_holdout | C18 | 13188 | 0.093 | 0.099 |  |  |  |
| linear_ridge | core | quality_score | column_family_holdout | C18 | 13188 | 0.116 | 0.177 |  |  |  |
| extra_trees | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.002 | 0.948 | 1.0 |  |
| random_forest | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.002 | 0.938 | 1.0 |  |
| catboost | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.003 | 0.912 | 0.053 |  |
| xgboost | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.003 | 0.908 | 1.0 |  |
| linear_ridge | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.003 | 0.85 | 0.053 |  |
| hist_gradient_boosting | core | quality_score | final_grouped_holdout | test | 3247 | 0.0 | 0.005 | 0.69 | 0.057 |  |
| random_forest | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.001 | 0.95 | 1.0 |  |
| catboost | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.001 | 0.919 | 0.075 |  |
| extra_trees | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.001 | 0.901 | 1.0 |  |
| xgboost | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.001 | 0.897 | 1.0 |  |
| linear_ridge | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.003 | 0.554 | 0.075 |  |
| hist_gradient_boosting | core | quality_score | group_kfold | GroupKFold | 15052 | 0.0 | 0.005 | 0.2 | 0.227 |  |
| random_forest | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| random_forest | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| extra_trees | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| catboost | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| catboost | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| xgboost | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| xgboost | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| xgboost | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| catboost | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.001 | 0.001 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.003 | 0.008 |  |  |  |
| hist_gradient_boosting | core | quality_score | method_holdout | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.008 | 0.016 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.012 |  |  |  |
| linear_ridge | core | quality_score | method_holdout | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.015 | 0.015 |  |  |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.004 | 0.009 | -0.583 | 0.047 |  |
| xgboost | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.005 | 0.005 | 0.485 | 0.056 |  |
| hist_gradient_boosting | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.009 | 0.024 |  |  |  |
| xgboost | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.023 | 0.025 |  |  |  |
| catboost | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.035 | 0.037 |  |  |  |
| catboost | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.062 | 0.069 | -83.609 | 0.055 |  |
| random_forest | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.063 | 0.064 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.076 | 0.082 | -117.018 | 0.055 |  |
| random_forest | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.078 | 0.085 | -124.719 | 0.055 |  |
| linear_ridge | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.096 | 0.096 |  |  |  |
| extra_trees | core | quality_score | source_family_holdout | MCMRT | 10073 | 0.129 | 0.13 |  |  |  |
| linear_ridge | core | quality_score | source_family_holdout | RepoRT | 4972 | 0.343 | 0.377 | -2493.717 | -0.047 |  |
| extra_trees | core | rt_min | column_family_holdout | unknown | 1852 | 1.162 | 1.697 | 0.879 | 0.947 | 5.641 |
| xgboost | core | rt_min | column_family_holdout | unknown | 1852 | 1.253 | 1.934 | 0.843 | 0.925 | 6.086 |
| random_forest | core | rt_min | column_family_holdout | unknown | 1852 | 1.354 | 2.044 | 0.825 | 0.911 | 6.576 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | unknown | 1852 | 1.354 | 2.005 | 0.831 | 0.924 | 6.577 |
| catboost | core | rt_min | column_family_holdout | unknown | 1852 | 1.449 | 2.103 | 0.815 | 0.916 | 7.034 |
| linear_ridge | core | rt_min | column_family_holdout | unknown | 1852 | 2.753 | 3.68 | 0.432 | 0.786 | 13.365 |
| hist_gradient_boosting | core | rt_min | column_family_holdout | C18 | 13188 | 4.591 | 8.696 | 0.382 | 0.801 | 14.963 |
| extra_trees | core | rt_min | column_family_holdout | C18 | 13188 | 4.664 | 8.817 | 0.364 | 0.815 | 15.201 |
| random_forest | core | rt_min | column_family_holdout | C18 | 13188 | 4.693 | 8.612 | 0.394 | 0.793 | 15.295 |
| catboost | core | rt_min | column_family_holdout | C18 | 13188 | 4.822 | 8.952 | 0.345 | 0.814 | 15.714 |
| xgboost | core | rt_min | column_family_holdout | C18 | 13188 | 4.946 | 8.982 | 0.34 | 0.805 | 16.119 |
| linear_ridge | core | rt_min | column_family_holdout | C18 | 13188 | 5.376 | 7.624 | 0.525 | 0.69 | 17.521 |
| extra_trees | core | rt_min | final_grouped_holdout | test | 3247 | 1.861 | 3.173 | 0.92 | 0.95 | 6.285 |
| random_forest | core | rt_min | final_grouped_holdout | test | 3247 | 1.989 | 3.474 | 0.904 | 0.942 | 6.717 |
| xgboost | core | rt_min | final_grouped_holdout | test | 3247 | 1.991 | 3.36 | 0.91 | 0.946 | 6.724 |
| hist_gradient_boosting | core | rt_min | final_grouped_holdout | test | 3247 | 2.095 | 3.463 | 0.904 | 0.941 | 7.074 |
| catboost | core | rt_min | final_grouped_holdout | test | 3247 | 2.186 | 3.494 | 0.903 | 0.935 | 7.381 |
| linear_ridge | core | rt_min | final_grouped_holdout | test | 3247 | 3.891 | 5.737 | 0.737 | 0.819 | 13.137 |
| extra_trees | core | rt_min | group_kfold | GroupKFold | 15052 | 1.849 | 3.163 | 0.909 | 0.94 | 6.285 |
| random_forest | core | rt_min | group_kfold | GroupKFold | 15052 | 1.983 | 3.346 | 0.898 | 0.93 | 6.74 |
| xgboost | core | rt_min | group_kfold | GroupKFold | 15052 | 2.03 | 3.32 | 0.9 | 0.931 | 6.9 |
| hist_gradient_boosting | core | rt_min | group_kfold | GroupKFold | 15052 | 2.072 | 3.396 | 0.895 | 0.928 | 7.042 |
| catboost | core | rt_min | group_kfold | GroupKFold | 15052 | 2.164 | 3.363 | 0.897 | 0.923 | 7.355 |
| linear_ridge | core | rt_min | group_kfold | GroupKFold | 15052 | 3.776 | 5.681 | 0.709 | 0.797 | 12.832 |
| extra_trees | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.83 | 1.031 | 0.958 | 0.98 | 3.86 |
| xgboost | core | rt_min | method_holdout | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.856 | 1.158 | 0.948 | 0.968 | 3.983 |
