from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.inverse_training import DEFAULT_ARTIFACT, DEFAULT_REPORT_DIR, train_inverse_models


DEFAULT_MATRIX = PROJECT_ROOT / "data" / "processed" / "model_matrix.csv"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train inverse recommendation ML baselines.")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--artifact", type=Path, default=PROJECT_ROOT / DEFAULT_ARTIFACT)
    parser.add_argument("--report-dir", type=Path, default=PROJECT_ROOT / DEFAULT_REPORT_DIR)
    parser.add_argument("--quick", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.matrix.exists():
        raise FileNotFoundError(f"Model matrix not found: {args.matrix}")
    matrix = pd.read_csv(args.matrix, low_memory=False)
    outputs = train_inverse_models(
        matrix,
        artifact_path=args.artifact,
        report_dir=args.report_dir,
        quick=args.quick,
    )
    print("Inverse model training complete")
    print(f"Training rows: {outputs.training_rows}")
    print(f"Best model: {outputs.best_model}")
    print(f"Artifact: {outputs.artifact_path.resolve()}")
    print(f"Metrics: {outputs.metrics_csv.resolve()}")
    print(f"Top-k report: {outputs.topk_csv.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
