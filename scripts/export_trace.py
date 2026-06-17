#!/usr/bin/env python3
"""Export a generation trace JSON to stdout or file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.core.security import validate_trace_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Spec2Vision trace JSON")
    parser.add_argument("trace_id", help="Task / trace id")
    parser.add_argument("-o", "--output", help="Optional output file")
    args = parser.parse_args()

    trace_id = validate_trace_id(args.trace_id)
    settings = get_settings()
    path = settings.traces_dir / f"{trace_id}.json"
    if not path.exists():
        print(f"Trace not found: {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
