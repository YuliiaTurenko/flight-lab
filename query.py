"""Running queries against the flight database."""

import math
from validator import parse_datetime

RECORD_KEYS = ("flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price")
STRING_KEYS = {"flight_id", "origin", "destination"}
DATETIME_KEYS = {"departure_datetime", "arrival_datetime"}
NUMBER_KEYS = {"price", "min_price"}
ALLOWED_KEYS = STRING_KEYS | DATETIME_KEYS | NUMBER_KEYS | {"sort_by", "order", "limit"}


def is_valid_query(query) -> bool:
    if not isinstance(query, dict):
        return False

    for key, value in query.items():
        if key not in ALLOWED_KEYS:
            return False
        if key in STRING_KEYS:
            if not isinstance(value, str):
                return False
        elif key in DATETIME_KEYS:
            if not isinstance(value, str) or parse_datetime(value) is None:
                return False
        elif key in NUMBER_KEYS:
            if not is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return False

    if "order" in query and "sort_by" not in query:
        return False
    
    return True


def is_number(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    
    return isinstance(value, float) and math.isfinite(value)


def apply_filters(db: list[dict], query: dict) -> list[dict]:
    result = db

    for key in STRING_KEYS:
        if key in query:
            result = [r for r in result if r[key] == query[key]]

    if "departure_datetime" in query:
        result = [r for r in result if r["departure_datetime"] >= query["departure_datetime"]]
    
    if "arrival_datetime" in query:
        result = [r for r in result if r["arrival_datetime"] <= query["arrival_datetime"]]

    if "price" in query:
        result = [r for r in result if r["price"] <= query["price"]]
    
    if "min_price" in query:
        result = [r for r in result if r["price"] >= query["min_price"]]

    return list(result) 


def apply_sorting(records: list[dict], query: dict) -> list[dict]:
    if "sort_by" not in query:
        return records
    
    field = query["sort_by"]
    descending = query.get("order", "asc") == "desc"
    
    return sorted(records, key=lambda r: r[field], reverse=descending)


def apply_limit(records: list[dict], query: dict) -> list[dict]:
    if "limit" not in query:
        return records
    
    return records[: query["limit"]]


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = apply_filters(db, query)
    matches = apply_sorting(matches, query)
    matches = apply_limit(matches, query)

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]
