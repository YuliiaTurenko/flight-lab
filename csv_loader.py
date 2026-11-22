"""Reading CSV files into flight records and error messages."""

import csv
from pathlib import Path
from validator import to_record, validate_row

DUPLICATE_FLIGHT = "DUPLICATE_FLIGHT"

# Helpers
def is_skippable(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def format_error(file_name: str, line_no: int, code: str, text: str) -> str:
    return f"{file_name}:{line_no}: {code} | {text}"


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in paths:
        file_name = Path(path).name

        with open(path, encoding="utf-8-sig") as f:
            for line_no, raw in enumerate(f, start=1):
                if line_no == 1:
                    continue
                if is_skippable(raw):
                    continue

                line = raw.rstrip("\r\n")
                fields = next(csv.reader([line]))

                code = validate_row(fields, airports)
                if code is not None:
                    errors.append(format_error(file_name, line_no, code, line.strip()))
                    continue

                record = to_record(fields)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen:
                    errors.append(format_error(file_name, line_no, DUPLICATE_FLIGHT, line.strip()))
                    continue

                seen.add(key)
                records.append(record)

    return records, errors
