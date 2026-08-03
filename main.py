"""Entry point.

Usage:
  python main.py                          -> interactive mode
  python main.py --csv in.csv --out out.csv -> batch mode
"""
from __future__ import annotations

import argparse
import sys

from nomenclature.cli import run_interactive
from nomenclature.csv_batch import process_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Modular T cell nomenclature generator")
    parser.add_argument("--csv", help="Input CSV path (batch mode)")
    parser.add_argument("--out", help="Output CSV path (batch mode; required with --csv)")
    args = parser.parse_args()

    if args.csv:
        if not args.out:
            parser.error("--out is required when --csv is given")
        n = process_csv(args.csv, args.out)
        print(f"Processed {n} row(s). Wrote {args.out}")
        return

    run_interactive()


if __name__ == "__main__":
    sys.exit(main() or 0)
