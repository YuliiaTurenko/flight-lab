"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import os
import logging

from datetime import datetime
from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "260ADB165"
FIRST_NAME = "Yuliia"
LAST_NAME = "Turenko"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Flight database CLI"
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("-i", "--input", dest="i", metavar="FILE", help="input CSV file")
    source_group.add_argument("-d", "--directory", dest="d", metavar="FOLDER", help="directory containing CSV files")
    source_group.add_argument("-j", "--json", dest="j", metavar="FILE", help="JSON file containing queries")
    parser.add_argument("-a", metavar="FILE", help="airport list file (required with -i/-d)")
    parser.add_argument("-o", metavar="FILE", help="output JSON database")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="folder for the response file")

    return parser


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = create_parser()
    args = parser.parse_args(argv)
    if args.j is None and args.a is None:
        parser.error("-a is required with -i or -d")
    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")
    
    return args


def read_json(path: str):
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e.msg} (line {e.lineno}, column {e.colno})")


def load_database(path: str) -> list[dict]:
    data = read_json(path)
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError(f"{path} must contain a JSON array of objects")
    
    return data


def load_queries(path: str) -> dict | list:
    data = read_json(path)
    if not isinstance(data, (dict, list)):
        raise ValueError(f"{path} must contain a query object or an array of queries")
    
    return data


def csv_paths(args: argparse.Namespace) -> list[str]:
    if args.i is not None:
        return [args.i]
    if not os.path.isdir(args.d):
        raise FileNotFoundError(f"folder not found: {args.d}")
    names = sorted(
        n for n in os.listdir(args.d)
        if n.endswith(".csv") and os.path.isfile(os.path.join(args.d, n))
    )
    if not names:
        raise ValueError(f"no .csv files found in {args.d}")
   
    return [os.path.join(args.d, n) for n in names]


def make_log_handler(log_path: str) -> logging.Handler:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    
    return handler


def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    try:
        args = parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    logger = logging.getLogger("flight_parser")
    handler = None
    try:
        if args.j is not None:
            db = load_database(args.j)
        else:
            paths = csv_paths(args)
            airports = load_airports(args.a)

            out_path = args.o if args.o is not None else "db.json"
            log_path = os.path.join(os.path.dirname(out_path), "errors.log")
            handler = make_log_handler(log_path)

            db, errors = parse_files(paths, airports)
            for message in errors:
                logger.warning("%s", message)
            logger.info("Parsed %d valid rows, %d invalid rows", len(db), len(errors))

            write_json(out_path, db)
            print(f"{len(db)} valid, {len(errors)} invalid -> {out_path}")

        if args.q is not None:
            queries = load_queries(args.q)
            response = run_queries(db, queries)
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            write_json(os.path.join(args.r, name), response)
            print(f"{len(response)} queries -> {name}")

        return 0
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        if handler is not None:
            logger.error("%s", e)
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
