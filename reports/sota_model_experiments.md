# SOTA Model Experiments

This bounded experiment compares CPU-practical tabular regressors for the current demo RT matrix.

- Feature set: `core`
- Morgan fingerprint features: 0

## Grouped CV Metrics

| validation_scope | target | model | group_column | n_folds | n_rows | n_groups | mae_mean | mae_std | rmse_mean | rmse_std | r2_mean | r2_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| group_kfold | rt_min | linear_ridge | inchikey | 5 | 15052 | 2785 | 3.776 | 0.107 | 5.681 | 0.094 | 0.709 | 0.033 |
| group_kfold | rt_min | random_forest | inchikey | 5 | 15052 | 2785 | 1.983 | 0.046 | 3.346 | 0.194 | 0.898 | 0.019 |
| group_kfold | rt_min | extra_trees | inchikey | 5 | 15052 | 2785 | 1.849 | 0.075 | 3.163 | 0.156 | 0.909 | 0.017 |
| group_kfold | rt_min | hist_gradient_boosting | inchikey | 5 | 15052 | 2785 | 2.072 | 0.062 | 3.396 | 0.195 | 0.895 | 0.021 |
| group_kfold | rt_min | xgboost | inchikey | 5 | 15052 | 2785 | 2.03 | 0.061 | 3.32 | 0.205 | 0.9 | 0.018 |
| group_kfold | rt_min | catboost | inchikey | 5 | 15052 | 2785 | 2.164 | 0.079 | 3.363 | 0.187 | 0.897 | 0.021 |
| group_kfold | quality_score | linear_ridge | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.003 | 0.005 | 0.554 | 0.338 |
| group_kfold | quality_score | random_forest | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.001 | 0.95 | 0.027 |
| group_kfold | quality_score | extra_trees | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.901 | 0.065 |
| group_kfold | quality_score | hist_gradient_boosting | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.005 | 0.005 | 0.2 | 0.096 |
| group_kfold | quality_score | xgboost | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.897 | 0.038 |
| group_kfold | quality_score | catboost | inchikey | 5 | 15052 | 2785 | 0.0 | 0.0 | 0.001 | 0.002 | 0.919 | 0.003 |

## Final Grouped Holdout RT Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 3.653 | 5.479 | 0.717 | 3.891 | 5.737 | 0.737 |
| random_forest | 2.09 | 3.372 | 0.893 | 1.989 | 3.474 | 0.904 |
| extra_trees | 1.917 | 3.226 | 0.902 | 1.861 | 3.173 | 0.92 |
| hist_gradient_boosting | 2.056 | 3.171 | 0.905 | 2.095 | 3.463 | 0.904 |
| xgboost | 2.074 | 3.281 | 0.898 | 1.991 | 3.36 | 0.91 |
| catboost | 2.238 | 3.325 | 0.896 | 2.186 | 3.494 | 0.903 |

## Final Grouped Holdout Quality Metrics

| model | validation_mae | validation_rmse | validation_r2 | test_mae | test_rmse | test_r2 |
| --- | --- | --- | --- | --- | --- | --- |
| linear_ridge | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.85 |
| random_forest | 0.0 | 0.0 |  | 0.0 | 0.002 | 0.938 |
| extra_trees | 0.0 | 0.0 |  | 0.0 | 0.002 | 0.948 |
| hist_gradient_boosting | 0.0 | 0.001 |  | 0.0 | 0.005 | 0.69 |
| xgboost | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.908 |
| catboost | 0.0 | 0.0 |  | 0.0 | 0.003 | 0.912 |

Candidate models: linear_ridge, random_forest, extra_trees, hist_gradient_boosting, xgboost, catboost

## Retention-Order Diagnostic

| source_dataset | column_name | mobile_phase_system | n_rows | n_pairs | pairwise_order_accuracy | spearman_rt |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | ALL | 3247 | 104519 | 0.855 | 0.95 |
| MCMRT:CM 01 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 73 | 2619 | 0.866 | 0.901 |
| MCMRT:CM 02 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2625 | 0.867 | 0.9 |
| MCMRT:CM 03 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2624 | 0.861 | 0.892 |
| MCMRT:CM 04 | Thermo Hypersil GOLD | meoh_formic_acid | 73 | 2627 | 0.868 | 0.9 |
| MCMRT:CM 05 | ACQUITY BEH C18 | meoh_formic_acid | 73 | 2625 | 0.87 | 0.904 |
| MCMRT:CM 06 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 73 | 2628 | 0.861 | 0.895 |
| MCMRT:CM 07 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2624 | 0.861 | 0.892 |
| MCMRT:CM 08 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2628 | 0.86 | 0.888 |
| MCMRT:CM 09 | Thermo Hypersil GOLD | meoh_formic_acid | 73 | 2626 | 0.866 | 0.898 |
| MCMRT:CM 10 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2624 | 0.862 | 0.893 |
| MCMRT:CM 11 | ACQUITY BEH C18 | meoh_formic_acid | 73 | 2627 | 0.872 | 0.905 |
| MCMRT:CM 12 | Acclaim RSLC 120 C18 | meoh_formic_acid | 73 | 2628 | 0.865 | 0.899 |
| MCMRT:CM 13 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 73 | 2627 | 0.866 | 0.9 |
| MCMRT:CM 14 | ACQUITY UPLC HSS T3 | meoh_formic_acid | 73 | 2626 | 0.865 | 0.895 |
| MCMRT:CM 15 | Acclaim 120 C18 | meoh_formic_acid | 73 | 2627 | 0.874 | 0.909 |
| MCMRT:CM 16 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_formic_acid | 73 | 2627 | 0.869 | 0.905 |
| MCMRT:CM 17 | Thermo Hypersil GOLD | meoh_formic_acid | 73 | 2625 | 0.86 | 0.892 |
| MCMRT:CM 18 | Thermo Hypersil GOLD | meoh_formic_acid | 73 | 2626 | 0.863 | 0.896 |
| MCMRT:CM 19 | Acclaim RSLC 120 C18 | acn_formic_acid | 73 | 2628 | 0.857 | 0.888 |
| MCMRT:CM 20 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 70 | 2409 | 0.848 | 0.879 |
| MCMRT:CM 21 | Thermo Hypersil GOLD | acn_formic_acid | 70 | 2412 | 0.853 | 0.88 |
| MCMRT:CM 22 | ACQUITY PRIMER HSS T3 with VanGuard | acn_formic_acid | 70 | 2413 | 0.85 | 0.878 |
| MCMRT:CM 23 | ACQUITY UPLC HSS T3 | acn_formic_acid | 70 | 2412 | 0.855 | 0.884 |
| MCMRT:CM 24 | Acclaim 120 C18 | acn_formic_acid | 70 | 2414 | 0.854 | 0.888 |
| MCMRT:CM 25 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 75 | 2769 | 0.872 | 0.904 |
| MCMRT:CM 26 | ACQUITY UPLC HSS T3 | meoh_ammonium | 75 | 2772 | 0.874 | 0.908 |
| MCMRT:CM 27 | ACQUITY PRIMER HSS T3 with VanGuard | meoh_ammonium | 75 | 2771 | 0.868 | 0.902 |
| MCMRT:CM 28 | ACQUITY UPLC HSS T3 | meoh_ammonium | 75 | 2773 | 0.872 | 0.906 |
| MCMRT:CM 29 | Acclaim 120 C18 | meoh_ammonium | 75 | 2772 | 0.873 | 0.909 |
| MCMRT:CM 30 | Acclaim RSLC 120 C18 | meoh_ammonium | 75 | 2774 | 0.871 | 0.902 |
| RepoRT:0001 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 12 | 66 | 0.864 | 0.895 |
| RepoRT:0002 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 88 | 3821 | 0.903 | 0.919 |
| RepoRT:0003 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 13 | 78 | 0.897 | 0.926 |
| RepoRT:0004 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 43 | 872 | 0.807 | 0.816 |
| RepoRT:0005 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 19 | 171 | 0.766 | 0.777 |
| RepoRT:0006 | Hichrom Alltima HP C18 | acn_formic_acid | 3 | 3 | 1.0 | 1.0 |
| RepoRT:0007 | Merck SeQuant ZIC-pHILIC | acn_unbuffered | 32 | 493 | 0.761 | 0.708 |
| RepoRT:0008 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 5 | 10 | 0.8 | 0.8 |
| RepoRT:0009 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 90 | 3933 | 0.817 | 0.789 |
| RepoRT:0010 | Merck Supelco Ascentis Express C18 | acn_formic_acid | 14 | 91 | 0.923 | 0.95 |
| RepoRT:0013 |  | acn_formic_acid | 7 | 20 | 0.35 | -0.411 |
| RepoRT:0014 |  | acn_formic_acid | 2 | 1 | 1.0 | 1.0 |
| RepoRT:0015 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 18 | 153 | 0.752 | 0.708 |
| RepoRT:0016 | Waters ACQUITY UPLC BEH C18 | acn_formic_acid | 5 | 10 | 0.5 | -0.1 |
| RepoRT:0017 | Phenomenex Kinetex C18 | meoh_formic_acid | 44 | 941 | 0.807 | 0.81 |
| RepoRT:0018 | Waters Atlantis T3 | acn_formic_acid | 28 | 378 | 0.783 | 0.783 |
| RepoRT:0019 | Waters XBridge C18 | meoh_formic_acid | 62 | 1877 | 0.832 | 0.835 |
| RepoRT:0020 | Merck SeQuant ZIC-pHILIC | other_unbuffered | 21 | 210 | 0.79 | 0.752 |
| RepoRT:0021 | Waters Symmetry C18 | acn_formic_acid | 11 | 55 | 0.855 | 0.845 |
| RepoRT:0023 | Thermo Scientific Hypersil GOLD | acn_formic_acid | 12 | 66 | 0.818 | 0.748 |
| RepoRT:0024 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 93 | 4182 | 0.852 | 0.845 |
| RepoRT:0025 | Waters ACQUITY UPLC HSS T3 | meoh_formic_acid | 10 | 43 | 0.744 | 0.772 |
| RepoRT:0026 | Thermo Scientific Hypersil GOLD PFP | acn_formic_acid | 2 | 1 | 1.0 | 1.0 |
| RepoRT:0027 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 61 | 1830 | 0.775 | 0.72 |
| RepoRT:0028 | Phenomenex Synergi Hydro-RP | acn_formic_acid | 13 | 78 | 0.91 | 0.929 |
| RepoRT:0029 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 13 | 78 | 0.923 | 0.951 |
| RepoRT:0030 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 12 | 66 | 0.939 | 0.958 |
| RepoRT:0031 | Phenomenex Luna Omega Polar C18 | acn_formic_acid | 11 | 55 | 0.836 | 0.791 |
| RepoRT:0032 | Phenomenex Luna C18 | acn_formic_acid | 14 | 91 | 0.923 | 0.943 |
| RepoRT:0033 |  | acn_formic_acid | 13 | 78 | 0.872 | 0.896 |
| RepoRT:0034 |  | acn_formic_acid | 10 | 45 | 0.733 | 0.552 |
| RepoRT:0036 | Merck Supelco SUPELCOSIL LC-C18 | acn_unbuffered | 10 | 45 | 0.933 | 0.96 |
| RepoRT:0037 | Phenomenex Kinetex PFP | acn_unbuffered | 7 | 21 | 0.667 | 0.393 |
| RepoRT:0038 | Waters Atlantis T3 | acn_unbuffered | 10 | 45 | 0.889 | 0.924 |
| RepoRT:0039 | Merck LiChrospher RP-18 | acn_formic_acid | 14 | 91 | 0.824 | 0.82 |
| RepoRT:0040 | Waters ACQUITY UPLC BEH Shield RP18 | acn_formic_acid | 24 | 276 | 0.87 | 0.898 |
| RepoRT:0041 | Waters ACQUITY UPLC HSS T3 | acn_formic_acid | 23 | 253 | 0.735 | 0.651 |
| RepoRT:0042 | Phenomenex Kinetex EVO C18 | acn_formic_acid | 12 | 66 | 0.894 | 0.916 |
| RepoRT:0043 | Waters ACQUITY UPLC HSS T3 | acn_unbuffered | 10 | 45 | 0.933 | 0.952 |
| RepoRT:0044 | Merck SeQuant ZIC-HILIC | acn_formic_acid | 140 | 5000 | 0.792 | 0.764 |
| RepoRT:0045 | Waters ACQUITY UPLC BEH C18 | meoh_formic_acid | 25 | 299 | 0.856 | 0.864 |

Tree ensembles, XGBoost, and CatBoost are trained on one-hot encoded LC/MS condition categories plus numeric RDKit/method descriptors. When enabled, Morgan fingerprints are included as sparse binary compound features. Model selection uses GroupKFold by compound identity; source-family holdouts and retention-order metrics are diagnostic transfer checks.
