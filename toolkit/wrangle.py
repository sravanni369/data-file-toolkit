"""Core CSV/JSON conversion and validation logic."""

import csv
import io
import json


def coerce(value):
    """Best-effort type coercion: int -> float -> stripped string -> None."""
    if value is None:
        return None
    v = str(value).strip()
    if v == "":
        return None
    for caster in (int, float):
        try:
            return caster(v)
        except ValueError:
            pass
    return v


def csv_to_rows(csv_text):
    """Parse CSV text into a list of dicts with coerced values."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return [
        {k.strip(): coerce(v) for k, v in raw.items() if k is not None}
        for raw in reader
    ]


def rows_to_json(rows):
    """Serialize rows to pretty JSON with stable key order."""
    return json.dumps(rows, indent=2, sort_keys=True)


def json_to_csv(json_text):
    """Convert a JSON array of flat objects to CSV text.

    Column order = keys of the first object, then any extra keys
    seen later (appended in first-seen order). Missing values -> "".
    """
    rows = json.loads(json_text)
    if not isinstance(rows, list):
        raise ValueError("expected a JSON array of objects")
    fields = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("expected every array item to be an object")
        for k in row:
            if k not in fields:
                fields.append(k)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fields, restval="", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in fields})
    return out.getvalue()


def validate(csv_text, required):
    """Check required fields are present and non-empty in every row.

    Returns (ok_count, errors) where errors are line-numbered messages.
    A bad row never raises — batch keeps going.
    """
    ok, errors = 0, []
    reader = csv.DictReader(io.StringIO(csv_text))
    header = [h.strip() for h in (reader.fieldnames or [])]
    missing_cols = [f for f in required if f not in header]
    if missing_cols:
        return 0, [f"header: missing column(s) {', '.join(missing_cols)}"]
    for lineno, raw in enumerate(reader, start=2):
        row = {k.strip(): coerce(v) for k, v in raw.items() if k is not None}
        empty = [f for f in required if row.get(f) is None]
        if empty:
            errors.append(f"line {lineno}: empty {', '.join(empty)}")
        else:
            ok += 1
    return ok, errors
