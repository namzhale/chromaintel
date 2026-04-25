# Evaluation Matrix

Long-form diagnostics for grouped CV, final grouped holdout, source-family holdout, method holdout, and column-family holdout. `normalized_mae_runtime_pct` is reported for RT rows as MAE divided by mean runtime for the evaluated rows.

| validation_scope | target | model | holdout_key | n_rows | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_grouped_holdout | rt_min | linear_ridge | test | 3247 | 3.891 | 5.737 | 0.737 | 0.819 | 13.137 |
| final_grouped_holdout | rt_min | random_forest | test | 3247 | 1.989 | 3.474 | 0.904 | 0.942 | 6.717 |
| final_grouped_holdout | rt_min | extra_trees | test | 3247 | 1.861 | 3.173 | 0.92 | 0.95 | 6.285 |
| final_grouped_holdout | rt_min | hist_gradient_boosting | test | 3247 | 2.095 | 3.463 | 0.904 | 0.941 | 7.074 |
| final_grouped_holdout | rt_min | xgboost | test | 3247 | 1.991 | 3.36 | 0.91 | 0.946 | 6.724 |
| final_grouped_holdout | rt_min | catboost | test | 3247 | 2.186 | 3.494 | 0.903 | 0.935 | 7.381 |
| final_grouped_holdout | quality_score | linear_ridge | test | 3247 | 0.0 | 0.003 | 0.85 | 0.053 |  |
| final_grouped_holdout | quality_score | random_forest | test | 3247 | 0.0 | 0.002 | 0.938 | 1.0 |  |
| final_grouped_holdout | quality_score | extra_trees | test | 3247 | 0.0 | 0.002 | 0.948 | 1.0 |  |
| final_grouped_holdout | quality_score | hist_gradient_boosting | test | 3247 | 0.0 | 0.005 | 0.69 | 0.057 |  |
| final_grouped_holdout | quality_score | xgboost | test | 3247 | 0.0 | 0.003 | 0.908 | 1.0 |  |
| final_grouped_holdout | quality_score | catboost | test | 3247 | 0.0 | 0.003 | 0.912 | 0.053 |  |
| group_kfold | rt_min | linear_ridge | GroupKFold | 15052 | 3.776 | 5.681 | 0.709 | 0.797 | 12.832 |
| group_kfold | rt_min | random_forest | GroupKFold | 15052 | 1.983 | 3.346 | 0.898 | 0.93 | 6.74 |
| group_kfold | rt_min | extra_trees | GroupKFold | 15052 | 1.849 | 3.163 | 0.909 | 0.94 | 6.285 |
| group_kfold | rt_min | hist_gradient_boosting | GroupKFold | 15052 | 2.072 | 3.396 | 0.895 | 0.928 | 7.042 |
| group_kfold | rt_min | xgboost | GroupKFold | 15052 | 2.03 | 3.32 | 0.9 | 0.931 | 6.9 |
| group_kfold | rt_min | catboost | GroupKFold | 15052 | 2.164 | 3.363 | 0.897 | 0.923 | 7.355 |
| group_kfold | quality_score | linear_ridge | GroupKFold | 15052 | 0.0 | 0.003 | 0.554 | 0.075 |  |
| group_kfold | quality_score | random_forest | GroupKFold | 15052 | 0.0 | 0.001 | 0.95 | 1.0 |  |
| group_kfold | quality_score | extra_trees | GroupKFold | 15052 | 0.0 | 0.001 | 0.901 | 1.0 |  |
| group_kfold | quality_score | hist_gradient_boosting | GroupKFold | 15052 | 0.0 | 0.005 | 0.2 | 0.227 |  |
| group_kfold | quality_score | xgboost | GroupKFold | 15052 | 0.0 | 0.001 | 0.897 | 1.0 |  |
| group_kfold | quality_score | catboost | GroupKFold | 15052 | 0.0 | 0.001 | 0.919 | 0.075 |  |
| source_family_holdout | rt_min | linear_ridge | MCMRT | 10073 | 5.335 | 6.998 | 0.517 | 0.754 | 16.571 |
| source_family_holdout | rt_min | random_forest | MCMRT | 10073 | 3.625 | 4.858 | 0.767 | 0.825 | 11.261 |
| source_family_holdout | rt_min | extra_trees | MCMRT | 10073 | 4.016 | 5.464 | 0.705 | 0.818 | 12.476 |
| source_family_holdout | rt_min | hist_gradient_boosting | MCMRT | 10073 | 3.585 | 4.904 | 0.763 | 0.829 | 11.136 |
| source_family_holdout | rt_min | xgboost | MCMRT | 10073 | 3.666 | 5.007 | 0.753 | 0.798 | 11.389 |
| source_family_holdout | rt_min | catboost | MCMRT | 10073 | 4.172 | 5.852 | 0.662 | 0.816 | 12.96 |
| source_family_holdout | quality_score | linear_ridge | MCMRT | 10073 | 0.096 | 0.096 |  |  |  |
| source_family_holdout | quality_score | random_forest | MCMRT | 10073 | 0.063 | 0.064 |  |  |  |
| source_family_holdout | quality_score | extra_trees | MCMRT | 10073 | 0.129 | 0.13 |  |  |  |
| source_family_holdout | quality_score | hist_gradient_boosting | MCMRT | 10073 | 0.009 | 0.024 |  |  |  |
| source_family_holdout | quality_score | xgboost | MCMRT | 10073 | 0.023 | 0.025 |  |  |  |
| source_family_holdout | quality_score | catboost | MCMRT | 10073 | 0.035 | 0.037 |  |  |  |
| source_family_holdout | rt_min | linear_ridge | RepoRT | 4972 | 49.538 | 64.865 | -33.162 | -0.048 | 207.726 |
| source_family_holdout | rt_min | random_forest | RepoRT | 4972 | 8.679 | 13.822 | -0.551 | 0.533 | 36.394 |
| source_family_holdout | rt_min | extra_trees | RepoRT | 4972 | 5.254 | 7.765 | 0.51 | 0.565 | 22.03 |
| source_family_holdout | rt_min | hist_gradient_boosting | RepoRT | 4972 | 5.184 | 8.075 | 0.471 | 0.523 | 21.737 |
| source_family_holdout | rt_min | xgboost | RepoRT | 4972 | 5.528 | 8.445 | 0.421 | 0.505 | 23.18 |
| source_family_holdout | rt_min | catboost | RepoRT | 4972 | 5.187 | 7.76 | 0.511 | 0.6 | 21.749 |
| source_family_holdout | quality_score | linear_ridge | RepoRT | 4972 | 0.343 | 0.377 | -2493.717 | -0.047 |  |
| source_family_holdout | quality_score | random_forest | RepoRT | 4972 | 0.078 | 0.085 | -124.719 | 0.055 |  |
| source_family_holdout | quality_score | extra_trees | RepoRT | 4972 | 0.076 | 0.082 | -117.018 | 0.055 |  |
| source_family_holdout | quality_score | hist_gradient_boosting | RepoRT | 4972 | 0.004 | 0.009 | -0.583 | 0.047 |  |
| source_family_holdout | quality_score | xgboost | RepoRT | 4972 | 0.005 | 0.005 | 0.485 | 0.056 |  |
| source_family_holdout | quality_score | catboost | RepoRT | 4972 | 0.062 | 0.069 | -83.609 | 0.055 |  |
| method_holdout | rt_min | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 3.677 | 4.671 | 0.639 | 0.84 | 12.902 |
| method_holdout | rt_min | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.409 | 1.799 | 0.946 | 0.971 | 4.942 |
| method_holdout | rt_min | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.5 | 1.802 | 0.946 | 0.978 | 5.262 |
| method_holdout | rt_min | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.226 | 1.567 | 0.959 | 0.976 | 4.3 |
| method_holdout | rt_min | xgboost | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.656 | 2.564 | 0.891 | 0.969 | 5.811 |
| method_holdout | rt_min | catboost | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 1.786 | 2.368 | 0.907 | 0.952 | 6.266 |
| method_holdout | quality_score | linear_ridge | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.015 | 0.015 |  |  |  |
| method_holdout | quality_score | random_forest | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.003 | 0.008 |  |  |  |
| method_holdout | quality_score | xgboost | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | catboost | Acclaim RSLC 120 C18 \| meoh_formic_acid | 2010 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 6.908 | 10.315 | 0.689 | 0.871 | 14.466 |
| method_holdout | rt_min | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 3.413 | 5.873 | 0.899 | 0.959 | 7.147 |
| method_holdout | rt_min | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 4.151 | 7.28 | 0.845 | 0.969 | 8.694 |
| method_holdout | rt_min | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 2.822 | 4.881 | 0.93 | 0.979 | 5.909 |
| method_holdout | rt_min | xgboost | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 3.897 | 7.112 | 0.852 | 0.981 | 8.16 |
| method_holdout | rt_min | catboost | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 5.416 | 9.147 | 0.756 | 0.962 | 11.343 |
| method_holdout | quality_score | linear_ridge | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | random_forest | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.008 | 0.016 |  |  |  |
| method_holdout | quality_score | xgboost | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | catboost | ACQUITY PRIMER HSS T3 with VanGuard \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | rt_min | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 2.441 | 3.119 | 0.62 | 0.881 | 11.354 |
| method_holdout | rt_min | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 1.136 | 1.648 | 0.894 | 0.919 | 5.286 |
| method_holdout | rt_min | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.83 | 1.031 | 0.958 | 0.98 | 3.86 |
| method_holdout | rt_min | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.962 | 1.25 | 0.939 | 0.96 | 4.475 |
| method_holdout | rt_min | xgboost | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.856 | 1.158 | 0.948 | 0.968 | 3.983 |
| method_holdout | rt_min | catboost | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.995 | 1.397 | 0.924 | 0.959 | 4.627 |
| method_holdout | quality_score | linear_ridge | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.009 | 0.012 |  |  |  |
| method_holdout | quality_score | random_forest | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | extra_trees | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | hist_gradient_boosting | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.001 | 0.001 |  |  |  |
| method_holdout | quality_score | xgboost | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| method_holdout | quality_score | catboost | Thermo Hypersil GOLD \| meoh_formic_acid | 1340 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | C18 | 13188 | 5.376 | 7.624 | 0.525 | 0.69 | 17.521 |
| column_family_holdout | rt_min | random_forest | C18 | 13188 | 4.693 | 8.612 | 0.394 | 0.793 | 15.295 |
| column_family_holdout | rt_min | extra_trees | C18 | 13188 | 4.664 | 8.817 | 0.364 | 0.815 | 15.201 |
| column_family_holdout | rt_min | hist_gradient_boosting | C18 | 13188 | 4.591 | 8.696 | 0.382 | 0.801 | 14.963 |
| column_family_holdout | rt_min | xgboost | C18 | 13188 | 4.946 | 8.982 | 0.34 | 0.805 | 16.119 |
| column_family_holdout | rt_min | catboost | C18 | 13188 | 4.822 | 8.952 | 0.345 | 0.814 | 15.714 |
| column_family_holdout | quality_score | linear_ridge | C18 | 13188 | 0.116 | 0.177 |  |  |  |
| column_family_holdout | quality_score | random_forest | C18 | 13188 | 0.001 | 0.001 |  |  |  |
| column_family_holdout | quality_score | extra_trees | C18 | 13188 | 0.0 | 0.002 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | C18 | 13188 | 0.093 | 0.099 |  |  |  |
| column_family_holdout | quality_score | xgboost | C18 | 13188 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | catboost | C18 | 13188 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | rt_min | linear_ridge | unknown | 1852 | 2.753 | 3.68 | 0.432 | 0.786 | 13.365 |
| column_family_holdout | rt_min | random_forest | unknown | 1852 | 1.354 | 2.044 | 0.825 | 0.911 | 6.576 |
| column_family_holdout | rt_min | extra_trees | unknown | 1852 | 1.162 | 1.697 | 0.879 | 0.947 | 5.641 |
| column_family_holdout | rt_min | hist_gradient_boosting | unknown | 1852 | 1.354 | 2.005 | 0.831 | 0.924 | 6.577 |
| column_family_holdout | rt_min | xgboost | unknown | 1852 | 1.253 | 1.934 | 0.843 | 0.925 | 6.086 |
| column_family_holdout | rt_min | catboost | unknown | 1852 | 1.449 | 2.103 | 0.815 | 0.916 | 7.034 |
| column_family_holdout | quality_score | linear_ridge | unknown | 1852 | 0.015 | 0.017 |  |  |  |
| column_family_holdout | quality_score | random_forest | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | extra_trees | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | hist_gradient_boosting | unknown | 1852 | 0.005 | 0.016 |  |  |  |
| column_family_holdout | quality_score | xgboost | unknown | 1852 | 0.0 | 0.0 |  |  |  |
| column_family_holdout | quality_score | catboost | unknown | 1852 | 0.0 | 0.0 |  |  |  |
