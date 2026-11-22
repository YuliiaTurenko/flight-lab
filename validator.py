"""Row validation: airport list loading, single-row checks, record building."""

import math
import re
from datetime import datetime

# Error codes
WRONG_FIELD_COUNT = "WRONG_FIELD_COUNT"
MISSING_FIELD = "MISSING_FIELD"
INVALID_FLIGHT_ID = "INVALID_FLIGHT_ID"
INVALID_ORIGIN = "INVALID_ORIGIN"
INVALID_DESTINATION = "INVALID_DESTINATION"
SAME_ORIGIN_DESTINATION = "SAME_ORIGIN_DESTINATION"
INVALID_DEPARTURE = "INVALID_DEPARTURE"
INVALID_ARRIVAL = "INVALID_ARRIVAL"
ARRIVAL_NOT_AFTER_DEPARTURE = "ARRIVAL_NOT_AFTER_DEPARTURE"
INVALID_PRICE = "INVALID_PRICE"
NON_POSITIVE_PRICE = "NON_POSITIVE_PRICE"

EXPECTED_FIELDS = 6
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT_CODE_RE = re.compile(r"[A-Z]{3}")
DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", re.ASCII)

# Helpers
def clean_airport_line(line: str) -> str | None:
    code = line.strip()
    if not code or code.startswith("#"):
        return None
    return code

def parse_datetime(value: str) -> datetime | None:
    if not isinstance(value, str):
        return None

    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"

    if not re.fullmatch(pattern, value):
        return None
    
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def parse_price(value: str) -> float | None:
    try:
        price = float(value)
    except ValueError:
        return None
    return price if math.isfinite(price) else None


def is_valid_airport(code: str, airports: set[str]) -> bool:
    return bool(AIRPORT_CODE_RE.fullmatch(code)) and code in airports


# Required API
def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports: set[str] = set()
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            code = clean_airport_line(line)
            if code is not None:
                airports.add(code)

    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != EXPECTED_FIELDS:
        return WRONG_FIELD_COUNT

    flight_id, origin, destination, departure, arrival, price = (f.strip() for f in fields)

    if not all((flight_id, origin, destination, departure, arrival, price)):
        return MISSING_FIELD

    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return INVALID_FLIGHT_ID

    if not is_valid_airport(origin, airports):
        return INVALID_ORIGIN
    
    if not is_valid_airport(destination, airports):
        return INVALID_DESTINATION

    if origin == destination:
        return SAME_ORIGIN_DESTINATION

    dep_dt = parse_datetime(departure)
    if dep_dt is None:
        return INVALID_DEPARTURE
    
    arr_dt = parse_datetime(arrival)
    if arr_dt is None:
        return INVALID_ARRIVAL

    if arr_dt <= dep_dt:
        return ARRIVAL_NOT_AFTER_DEPARTURE

    value = parse_price(price)
    if value is None:
        return INVALID_PRICE
    if value <= 0:
        return NON_POSITIVE_PRICE

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, departure, arrival, price = (f.strip() for f in fields)

    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": departure,
        "arrival_datetime": arrival,
        "price": float(price),
    }
