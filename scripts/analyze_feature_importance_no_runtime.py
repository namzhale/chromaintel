from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.runtime_leakage import (  # noqa: E402
    RuntimeAblationConfig,
    run_no_runtime_feature_importance,
    write_no_runtime_feature_importance_outputs,
)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    matrix = pd.read_csv(args.model_matrix, low_memory=False)
    importance, metrics = run_no_runtime_feature_importance(
        matrix,
        RuntimeAblationConfig(
            sample_rows=args.sample_rows,
            random_state=args.random_state,
            n_estimators=args.n_estimators,
        ),
        n_repeats=args.n_repeats,
    )
    paths = write_no_runtime_feature_importance_outputs(importance, metrics, args.report_dir)
    print(importance.head(args.show_top).to_string(index=False))
    print(f"Report: {Path(paths['report']).resolve()}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train the no-runtime-proxy RT model and compute permutation feature importance."
    )
    parser.add_argument("--model-matrix", type=Path, default=PROJECT_ROOT / "data" / "processed" / "model_matrix.csv")
    parser.add_argument("--sample-rows", type=int, default=20000)
    parser.add_argument("--n-estimators", type=int, default=120)
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--report-dir", type=Path, default=PROJECT_ROOT / "reports")
    parser.add_argument("--show-top", type=int, default=25)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
