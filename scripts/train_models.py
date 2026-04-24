from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.assemble_dataset import DEFAULT_OUTPUT_DIR, assemble_dataset


DEFAULT_MATRIX = DEFAULT_OUTPUT_DIR / "model_matrix.csv"
DEFAULT_ARTIFACT = DEFAULT_OUTPUT_DIR / "models" / "trained_forward_bundle.joblib"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"
DEFAULT_PLOTS_DIR = DEFAULT_OUTPUT_DIR / "plots"


def _load_trainer() -> Callable[..., object]:
    try:
        from app.models.training import train_forward_models
    except Exception as exc:  # pragma: no cover - defensive CLI reporting
        raise RuntimeError(
            "Could not import app.models.training.train_forward_models: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if not callable(train_forward_models):
        raise RuntimeError(
            "app.models.training.train_forward_models is not callable; "
            f"got {type(train_forward_models).__name__}"
        )
    return train_forward_models


def _ensure_model_matrix(matrix_path: Path) -> pd.DataFrame:
    if matrix_path.exists():
        print(f"Using existing model matrix: {matrix_path.resolve()}")
    else:
        print(f"Model matrix not found at {matrix_path.resolve()}; running assembly first.")
        outputs = assemble_dataset(output_dir=matrix_path.parent)
        print(
            "Assembly produced model matrix: "
            f"{outputs.model_matrix_path.resolve()} "
            f"({outputs.model_matrix_rows} rows x {outputs.model_matrix_columns} columns)"
        )
    return pd.read_csv(matrix_path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train LC-MS/MS forward models from the assembled model matrix."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX,
        help="Input model matrix CSV. Assembly runs first when this file is missing.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Output path for the trained model bundle.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Directory for training markdown and CSV reports.",
    )
    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=DEFAULT_PLOTS_DIR,
        help="Directory for generated training plots.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    matrix = _ensure_model_matrix(args.matrix)
    print(
        f"Loaded model matrix: {args.matrix.resolve()} "
        f"({len(matrix)} rows x {len(matrix.columns)} columns)"
    )

    try:
        train_forward_models = _load_trainer()
        summary = train_forward_models(
            matrix,
            artifact_path=args.artifact,
            report_dir=args.report_dir,
            plots_dir=args.plots_dir,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = asdict(summary) if hasattr(summary, "__dataclass_fields__") else {}
    print("LC-MS/MS model training complete")
    print(f"Rows: train={payload.get('n_train')}, validation={payload.get('n_validation')}, test={payload.get('n_test')}")
    print(f"Best RT model: {payload.get('best_rt_model')}")
    print(f"Best quality model: {payload.get('best_quality_model')}")
    print(f"Artifact: {Path(payload.get('artifact_path', args.artifact)).resolve()}")
    print(f"Report: {Path(payload.get('report_path', args.report_dir)).resolve()}")
    print(f"Feature count: {len(payload.get('feature_columns', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
