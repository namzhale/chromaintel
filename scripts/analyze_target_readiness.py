from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.target_readiness import write_target_readiness_reports


DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "model_matrix.csv"
DEFAULT_REPORTS = PROJECT_ROOT / "reports"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write peak/direct target readiness reports.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORTS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Input matrix not found: {args.input}")
    frame = pd.read_csv(args.input, low_memory=False)
    paths = write_target_readiness_reports(frame, args.report_dir)
    print(f"Coverage CSV: {paths['coverage_csv'].resolve()}")
    print(f"Readiness report: {paths['readiness_md'].resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
