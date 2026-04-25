from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.adapters.literature_parser import (  # noqa: E402
    extract_lcms_records,
    load_snippets,
    normalize_literature_records,
)


DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "literature_extracted_records.csv"
DEFAULT_ENV_PATH = Path(r"C:\Users\namzh\Documents\Retell\.env")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract LC-MS/MS method entities from reviewed literature snippets."
    )
    parser.add_argument("inputs", nargs="*", type=Path, help="Text/CSV/TSV files with reviewed snippets.")
    parser.add_argument("--stdin-text", help="Single reviewed snippet supplied directly on the command line.")
    parser.add_argument("--source-name", default="manual_review", help="Source label stored in provenance fields.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Canonical output CSV path.")
    parser.add_argument("--json", action="store_true", help="Print extracted canonical records as JSON.")
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help=(
            "Reserved opt-in flag for future LLM extraction. The current MVP loads key "
            "presence only and keeps extraction offline."
        ),
    )
    parser.add_argument("--use-openai", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    use_llm = bool(args.use_llm or args.use_openai)
    if use_llm:
        key_present = _load_openai_key_presence(DEFAULT_ENV_PATH)
        if key_present:
            print("LLM requested and API key loaded; scaffold currently keeps extraction offline", file=sys.stderr)
        else:
            print("LLM requested but OPENAI_API_KEY was not found; using offline regex parser", file=sys.stderr)
    else:
        print("LLM disabled; using offline regex parser", file=sys.stderr)

    snippets = []
    if args.stdin_text:
        snippets.append(args.stdin_text)
    snippets.extend(load_snippets(args.inputs))
    if not snippets:
        print("No snippets supplied. Provide files or --stdin-text.", file=sys.stderr)
        return 2

    records = extract_lcms_records(snippets, source_name=args.source_name)
    frame = normalize_literature_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Extracted {len(frame)} record(s)")
    print(f"Wrote {len(frame)} literature-derived canonical rows to {args.output.resolve()}")
    if args.json:
        print(json.dumps(_json_records(frame), ensure_ascii=False, indent=2))
    return 0


def _load_openai_key_presence(env_path: Path) -> bool:
    if os.getenv("OPENAI_API_KEY"):
        return True
    if not env_path.exists():
        return False
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("OPENAI_API_KEY="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                os.environ["OPENAI_API_KEY"] = value
                return True
    return False


def _json_records(frame):
    records = frame.where(frame.notna(), None).to_dict("records")
    return records


if __name__ == "__main__":
    raise SystemExit(main())
