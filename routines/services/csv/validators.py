"""Shared validation helpers for the CSV import system.

Every function here either returns a cleaned/parsed value or raises
ImportValidationError with enough context (file, row, reason, plus any
extra labeled details) to build an actionable error message.
"""

import re
from datetime import datetime

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class ImportValidationError(Exception):
    """Raised by validators/importers when a row cannot be imported.

    `details` is an ordered mapping of label -> value rendered under the
    file/row/reason in the console error report (e.g. Column, Subject,
    Paper, Chapter).
    """

    def __init__(self, file, row, reason, **details):
        self.file = file
        self.row = row
        self.reason = reason
        self.details = details
        super().__init__(f"{file} row {row}: {reason}")


def require(value, file, row, column):
    """Return the stripped value, or raise if blank."""
    cleaned = (value or "").strip()
    if not cleaned:
        raise ImportValidationError(
            file, row, "Missing required value.", Column=column
        )
    return cleaned


def parse_int(value, file, row, column):
    cleaned = require(value, file, row, column)
    if not cleaned.isdigit():
        raise ImportValidationError(
            file, row, f"'{cleaned}' is not a valid integer.", Column=column
        )
    return int(cleaned)


def parse_date(value, file, row, column):
    cleaned = require(value, file, row, column)
    if not DATE_RE.match(cleaned):
        raise ImportValidationError(
            file, row,
            f"Invalid date format '{cleaned}'. Expected YYYY-MM-DD.",
            Column=column,
        )
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        raise ImportValidationError(
            file, row, f"'{cleaned}' is not a real calendar date.", Column=column
        )


def parse_date_optional(value, file, row, column):
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return parse_date(cleaned, file, row, column)


def parse_time(value, file, row, column):
    cleaned = require(value, file, row, column)
    if not TIME_RE.match(cleaned):
        raise ImportValidationError(
            file, row,
            f"Invalid time format '{cleaned}'. Expected HH:MM (24-hour).",
            Column=column,
        )
    return datetime.strptime(cleaned, "%H:%M").time()


def parse_time_optional(value, file, row, column):
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return parse_time(cleaned, file, row, column)


def parse_paper(value, file, row, column="paper"):
    cleaned = require(value, file, row, column)
    if cleaned not in ("1", "2"):
        raise ImportValidationError(
            file, row, f"paper '{cleaned}' must be '1' or '2'.", Column=column
        )
    return int(cleaned)


def validate_choice(value, choices, file, row, column):
    cleaned = require(value, file, row, column)
    if cleaned not in choices:
        raise ImportValidationError(
            file, row,
            f"'{cleaned}' is not one of the allowed values: "
            f"{', '.join(sorted(choices))}.",
            Column=column,
        )
    return cleaned


class DuplicateTracker:
    """Raises ImportValidationError the second time the same key is seen.

    Defense-in-depth: the dataset was already validated (0 errors) before
    this milestone, but the importer must not silently trust that and
    should never persist duplicate rows even if the source file changes.
    """

    def __init__(self, file, column, message):
        self.file = file
        self.column = column
        self.message = message
        self._seen = {}

    def check(self, key, row):
        if key in self._seen:
            raise ImportValidationError(
                self.file, row, self.message.format(key=key),
                Column=self.column,
                **{"First seen at row": self._seen[key]},
            )
        self._seen[key] = row
