"""Shared, format-level utilities for the CSV import system.

Pure parsing/reading helpers with no Django ORM access and no
per-file business rules - those live in validators.py and the
individual importers.
"""

import csv
import re
from pathlib import Path

LECTURE_CODE_RE = re.compile(r"^([A-Za-z]+)-(\d+)$")

# Bengali digits 0-9 (U+09E6..U+09EF), in order.
BENGALI_DIGITS = "".join(chr(0x09E6 + i) for i in range(10))
BENGALI_DIGIT_MAP = {d: str(i) for i, d in enumerate(BENGALI_DIGITS)}

# Bengali "য়" (YYA) has two valid Unicode representations: the single
# precomposed codepoint U+09DF, and the decomposed sequence YA (U+09AF) +
# NUKTA (U+09BC). They render identically but do not compare equal as
# Python strings, and unicodedata.normalize() does not convert between
# them (U+09DF has no canonical decomposition to U+09AF U+09BC in the
# Unicode Character Database). The dataset consistently uses the
# precomposed form. Built from explicit \uXXXX escapes (never literal
# glyphs in source) so this file's encoding can never silently drift
# between the two representations - typing the literal glyph in an
# editor/tool has previously produced the wrong (decomposed) form here.
_DECOMPOSED_YYA = "য়"  # YA + NUKTA
_PRECOMPOSED_YYA = "য়"  # YYA


def normalize_bengali(text):
    return text.replace(_DECOMPOSED_YYA, _PRECOMPOSED_YYA)


_PROTHOM = "১ম"  # "1st"
_DWITIYO = "২য়"  # "2nd"
_PORTRO = "পত্র"  # "paper"
_ODHYAY = "অধ্যায়"  # "chapter"

CHAPTER_REF_RE = re.compile(
    rf"^(?P<paper>{_PROTHOM}|{_DWITIYO})\s*{_PORTRO}\s*{_ODHYAY}-(?P<chapter>[{BENGALI_DIGITS[0]}-{BENGALI_DIGITS[9]}]+)$"
)


def bengali_to_int(digits):
    return int("".join(BENGALI_DIGIT_MAP[d] for d in digits))


def parse_chapter_ref(value):
    """Parse a lecture_topics.csv chapter_no value like '1st-paper chapter-2'
    (Bengali "<paper> পত্র অধ্যায়-<digits>" reference).

    Returns (paper, chapter_no) as (int, int), or None if the value
    doesn't match the finalized paper+chapter reference format.
    """
    match = CHAPTER_REF_RE.match(normalize_bengali(value.strip()))
    if not match:
        return None
    paper = 1 if match.group("paper") == _PROTHOM else 2
    chapter_no = bengali_to_int(match.group("chapter"))
    return paper, chapter_no


def read_csv_rows(path: Path):
    """Read a CSV file, returning (header, rows).

    UTF-8/BOM-safe (decodes with utf-8-sig, so a leading BOM is stripped
    rather than becoming part of the first header name). Each row is a
    dict of column -> value, plus '_line' (1-indexed file line number,
    header = line 1). Fully blank rows are skipped, per the CSV
    specification's "blank rows are ignored" rule.
    """
    with path.open("rb") as fh:
        raw_bytes = fh.read()

    text = raw_bytes.decode("utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = next(reader)

    rows = []
    for line_no, fields in enumerate(reader, start=2):
        if not fields or all(f.strip() == "" for f in fields):
            continue
        row = dict(zip(header, fields))
        row["_line"] = line_no
        rows.append(row)

    return header, rows
