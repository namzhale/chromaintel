# Dataset Assembly Summary

- Source profile: `explicit`
- Primary source: `primary` (1 rows)
- Master rows after canonical merge/deduplication: 2
- Model matrix shape: 2 rows x 43 columns

## Row Counts By Source

| Status | Source | Rows | Path | Policy |
| --- | --- | ---: | --- | --- |
| included | primary | 1 | `C:\Users\namzh\AppData\Local\Temp\pytest-of-namzh\pytest-97\test_assemble_dataset_accepts_0\primary.csv` | primary training records |
| included | external | 1 | `C:\Users\namzh\AppData\Local\Temp\pytest-of-namzh\pytest-97\test_assemble_dataset_accepts_0\external.csv` | target rows |

## Excluded duplicate/sidecar policy

- No duplicate/sidecar exclusions were applied.
- The expanded ML profile uses ReTiNA, MCMRT, RepoRT, and METLIN Figshare canonical rows while leaving Kaggle METLIN descriptor exports out of target-row assembly.
