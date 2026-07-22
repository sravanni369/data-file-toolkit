"""CLI entry point: python -m toolkit <command> ..."""

import argparse
import sys
from pathlib import Path

from .wrangle import csv_to_rows, rows_to_json, json_to_csv, validate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="toolkit", description="CSV/JSON convert + validate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("csv2json", help="convert CSV file to JSON file")
    p1.add_argument("src"), p1.add_argument("dst")

    p2 = sub.add_parser("json2csv", help="convert JSON array file to CSV file")
    p2.add_argument("src"), p2.add_argument("dst")

    p3 = sub.add_parser("validate", help="check required columns are filled")
    p3.add_argument("src")
    p3.add_argument("--require", nargs="+", required=True, metavar="COL")

    args = parser.parse_args(argv)

    try:
        text = Path(args.src).read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: cannot read {args.src}: {e}", file=sys.stderr)
        return 2

    if args.cmd == "csv2json":
        Path(args.dst).write_text(rows_to_json(csv_to_rows(text)), encoding="utf-8")
        print(f"wrote {args.dst}")
    elif args.cmd == "json2csv":
        try:
            Path(args.dst).write_text(json_to_csv(text), encoding="utf-8")
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(f"wrote {args.dst}")
    elif args.cmd == "validate":
        ok, errors = validate(text, args.require)
        print(f"ok rows: {ok}")
        for e in errors:
            print("REJECT:", e)
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
