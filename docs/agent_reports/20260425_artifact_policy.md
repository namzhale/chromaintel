# Artifact Policy Agent - 2026-04-25

## Existing implementation audit

Already exists:
- `.gitignore` entries for several generated public-data and DL-prep outputs.
- README warnings that expanded datasets and trained bundles are large generated local artifacts.

Partially exists:
- No single artifact policy document explained what may be committed versus what should remain local.
- No manifest summarized the current local sizes and row counts for the expanded build.

Newly implemented:
- Added `docs/artifact_policy.md` with rebuild commands, do-not-commit rules, and future GitHub Releases/Git LFS/object-store options.
- Added `reports/local_artifact_manifest.md` documenting the current 213,941-row dataset, 43-column matrix, 188 MB model bundle, and DL manifests.
- Linked the policy and manifest from README.
- Updated `.PLAN` so the next slice moves on to PDF dashboard polish, Morgan comparison, and GUI/API smoke.

Intentionally skipped:
- Did not configure Git LFS automatically because that changes repository storage policy and quotas.
- Did not stage large generated artifacts.

Files reused:
- `README.md`
- `.PLAN`

Files modified:
- `README.md`
- `.PLAN`

Files created:
- `docs/artifact_policy.md`
- `reports/local_artifact_manifest.md`
- `docs/agent_reports/20260425_artifact_policy.md`
