"""Validate the source CSV datasets before CSV import is implemented.

This command performs read-only, structural and cross-file consistency
checks against subjects.csv, chapters.csv, routine.csv,
lecture_topics.csv and exams.csv. It never modifies the datasets and
never touches the database - it only produces validation_report.md.

Validation targets the FINALIZED dataset design (see PROJECT_PROGRESS.md,
"Dataset Revision" entry), not the original 06_CSV_Import_Specification.md
draft:

- Subject codes are subject-level (P, C, M, B, E, BA), not paper-level.
- chapters.csv carries an explicit `paper` column (1st/2nd paper) since
  subject codes no longer encode the paper.
- lecture_topics.csv's chapter_no column intentionally holds a Bengali
  "<paper> পত্র অধ্যায়-<chapter>" reference, not a bare integer, for
  subjects that have papers (P, C, M, B). It is parsed and resolved
  against chapters.csv. Subjects without a chapter breakdown (E, BA) are
  exempt from chapter resolution.
- routine.csv's event_type values (CLASS, DAILY_EXAM, WEEKLY_EXAM,
  MONTHLY_EXAM) are finalized.
- exams.csv's column set (exam_code, exam_type, title, lecture_codes,
  exam_date, online_start, online_end) is finalized.
- Subjects with zero CLASS rows in routine.csv (English, Bangla in this
  dataset) are self-study subjects: their lecture codes are not expected
  to exist as routine.csv CLASS rows.
- Lecture/week number 06 is an intentional gap across every subject and
  must never be reported as a numbering gap.
"""

import csv
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

REQUIRED_FILES = [
    "subjects.csv",
    "chapters.csv",
    "routine.csv",
    "lecture_topics.csv",
    "exams.csv",
]

FINALIZED_HEADERS = {
    "subjects.csv": ["code", "name", "display_order"],
    "chapters.csv": ["subject_code", "paper", "chapter_no", "chapter_name", "display_order"],
    "routine.csv": [
        "date", "day", "event_type", "subject_code", "lecture_code",
        "title", "start_time", "end_time", "notes",
    ],
    "lecture_topics.csv": [
        "lecture_code", "subject_code", "chapter_no", "topic", "display_order",
    ],
    "exams.csv": [
        "exam_code", "exam_type", "title", "lecture_codes", "exam_date",
        "online_start", "online_end",
    ],
}

FINALIZED_EVENT_TYPES = {"CLASS", "DAILY_EXAM", "WEEKLY_EXAM", "MONTHLY_EXAM"}
LOCKED_EXAM_TYPES = {"WEEKLY", "MONTHLY", "SPECIAL"}
PAPER_VALUES = {"1", "2"}

# Subjects with no chapter breakdown in chapters.csv by design (English
# and Bangla topics are referenced by lesson/unit text, not chapter
# number). chapter_no resolution is skipped for these.
SUBJECTS_WITHOUT_CHAPTERS = {"E", "BA"}

# Lecture/week 06 is intentionally skipped across every subject in this
# dataset and must never be reported as a numbering gap.
ALLOWED_NUMBERING_GAPS = {6}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
LECTURE_CODE_RE = re.compile(r"^([A-Za-z]+)-(\d+)$")

BENGALI_DIGITS = "০১২৩৪৫৬৭৮৯"
BENGALI_DIGIT_MAP = {d: str(i) for i, d in enumerate(BENGALI_DIGITS)}

# Bengali "য়" (YYA) can appear as the single precomposed codepoint U+09DF,
# or as the decomposed sequence YA (U+09AF) + NUKTA (U+09BC). Both render
# identically but do not compare equal as Python strings, and this is not
# fixed by unicodedata.normalize() since U+09DF has no canonical
# decomposition to U+09AF U+09BC in the Unicode Character Database.
# Normalize to the precomposed form before matching/building patterns.
_DECOMPOSED_YYA = "য়"
_PRECOMPOSED_YYA = "য়"


def normalize_bengali(text):
    return text.replace(_DECOMPOSED_YYA, _PRECOMPOSED_YYA)


# Matches e.g. "১ম পত্র অধ্যায়-০২" (1st paper, chapter 2) or
# "২য় পত্র অধ্যায়-১০" (2nd paper, chapter 10). Built from explicit
# codepoints (rather than literal glyphs in source) so the encoding of
# this file can never silently drift from the precomposed form above.
_PROTHOM = "১ম"  # ১ম - "1st"
_DWITIYO = "২" + _PRECOMPOSED_YYA  # ২য় - "2nd"
_PORTRO = "পত্র"  # পত্র - "paper"
_ODHYAY = "অধ্যা" + _PRECOMPOSED_YYA  # অধ্যায় - "chapter"

CHAPTER_REF_RE = re.compile(
    rf"^(?P<paper>{_PROTHOM}|{_DWITIYO})\s*{_PORTRO}\s*{_ODHYAY}-(?P<chapter>[০-৯]+)$"
)


def is_allowed_gap_lecture(lecture_code):
    """True if lecture_code's number is an intentionally-skipped gap (06).

    lecture_topics.csv / exams.csv may still reference a gap lecture (e.g.
    pre-prepared topic content for a live class that was skipped) even
    though routine.csv has no CLASS row for it - that is expected, not an
    orphan reference.
    """
    match = LECTURE_CODE_RE.match(lecture_code)
    return bool(match) and int(match.group(2)) in ALLOWED_NUMBERING_GAPS


def bengali_to_int(digits):
    return int("".join(BENGALI_DIGIT_MAP[d] for d in digits))


def parse_chapter_ref(value):
    """Parse a lecture_topics.csv chapter_no value like '১ম পত্র অধ্যায়-০২'.

    Returns (paper, chapter_no) as ("1"|"2", int), or None if the value
    doesn't match the finalized paper+chapter reference format.
    """
    match = CHAPTER_REF_RE.match(normalize_bengali(value.strip()))
    if not match:
        return None
    paper = "1" if match.group("paper") == _PROTHOM else "2"
    chapter_no = bengali_to_int(match.group("chapter"))
    return paper, chapter_no


class Command(BaseCommand):
    help = "Validate subjects/chapters/routine/lecture_topics/exams CSV datasets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            default=str(settings.BASE_DIR),
            help="Directory containing the CSV files (default: project root).",
        )
        parser.add_argument(
            "--out",
            default=str(Path(settings.BASE_DIR) / "validation_report.md"),
            help="Path to write validation_report.md to.",
        )

    def handle(self, *args, **options):
        base_dir = Path(options["dir"])
        out_path = Path(options["out"])

        result = ValidationResult()
        raw = load_all_files(base_dir, result)

        if raw is not None:
            validate_subjects(raw, result)
            validate_chapters(raw, result)
            validate_routine(raw, result)
            validate_lecture_topics(raw, result)
            validate_exams(raw, result)
            validate_cross_file(raw, result)

        report = render_report(base_dir, raw, result)
        out_path.write_text(report, encoding="utf-8")

        status = "INVALID" if result.errors else "VALID"
        summary = (
            f"Dataset {status}: {len(result.errors)} error(s), "
            f"{len(result.warnings)} warning(s). Report written to {out_path}"
        )
        self.stdout.write(summary)

        if result.errors:
            raise SystemExit(1)


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []
        self.quality = []
        self.stats = {}

    def error(self, file, row, column, message):
        self.errors.append(
            {"file": file, "row": row, "column": column, "message": message}
        )

    def warning(self, file, row, column, message):
        self.warnings.append(
            {"file": file, "row": row, "column": column, "message": message}
        )

    def note(self, message):
        self.notes.append(message)

    def quality_issue(self, file, message):
        self.quality.append({"file": file, "message": message})


def read_csv_rows(path):
    """Read a CSV file, returning (header, rows, bom, raw_bytes).

    Each row is a dict of column -> value, plus '_line' (1-indexed file
    line number of that row, header = line 1). Fully blank rows are
    skipped, per the CSV spec's "Blank rows are ignored" rule, and are
    not included in the returned rows.
    """
    with path.open("rb") as fh:
        raw_bytes = fh.read()

    bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    text = raw_bytes.decode("utf-8-sig")

    reader = csv.reader(text.splitlines())
    header = next(reader)

    rows = []
    for line_no, fields in enumerate(reader, start=2):
        if not fields or all(f.strip() == "" for f in fields):
            continue
        row = dict(zip(header, fields))
        row["_line"] = line_no
        row["_raw_fields"] = fields
        rows.append(row)

    return header, rows, bom, raw_bytes


def load_all_files(base_dir, result):
    raw = {}
    missing = []

    for filename in REQUIRED_FILES:
        path = base_dir / filename
        if not path.exists():
            missing.append(filename)
            continue

        header, rows, bom, raw_bytes = read_csv_rows(path)

        if bom:
            result.quality_issue(filename, "File starts with a UTF-8 BOM.")

        if len(header) != len(set(header)):
            dupes = [c for c, n in Counter(header).items() if n > 1]
            result.quality_issue(
                filename, f"Duplicate header column(s): {', '.join(dupes)}."
            )

        if b"\x00" in raw_bytes:
            result.quality_issue(filename, "File contains NUL bytes.")

        raw[filename] = {"header": header, "rows": rows}

    if missing:
        for filename in missing:
            result.error(filename, "-", "-", "File is missing from the dataset directory.")
        return None

    return raw


def check_required_columns(filename, header, required, result):
    header_set = set(header)
    required_set = set(required)

    missing_cols = [c for c in required if c not in header_set]
    unexpected_cols = [c for c in header if c not in required_set]

    if missing_cols:
        result.error(
            filename, "header", ", ".join(missing_cols),
            "Required column(s) missing from header.",
        )
    if unexpected_cols:
        result.error(
            filename, "header", ", ".join(unexpected_cols),
            "Unexpected column(s) not part of the finalized schema.",
        )
    return missing_cols, unexpected_cols


# ---------------------------------------------------------------------
# subjects.csv
# ---------------------------------------------------------------------

def validate_subjects(raw, result):
    filename = "subjects.csv"
    header, rows = raw[filename]["header"], raw[filename]["rows"]

    check_required_columns(filename, header, FINALIZED_HEADERS[filename], result)

    codes = defaultdict(list)
    names = defaultdict(list)
    display_orders = defaultdict(list)

    for row in rows:
        line = row["_line"]
        code = row.get("code", "").strip()
        name = row.get("name", "").strip()
        display_order = row.get("display_order", "").strip()

        if not code:
            result.error(filename, line, "code", "Missing subject code.")
        if not name:
            result.error(filename, line, "name", "Missing subject name.")
        if not display_order:
            result.error(filename, line, "display_order", "Missing display_order.")
        elif not display_order.isdigit():
            result.error(
                filename, line, "display_order",
                f"display_order '{display_order}' is not a valid integer.",
            )

        if code:
            codes[code].append(line)
        if name:
            names[name].append(line)
        if display_order:
            display_orders[display_order].append(line)

    for code, lines in codes.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "code",
                f"Duplicate subject code '{code}'.",
            )

    for name, lines in names.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "name",
                f"Duplicate subject name '{name}'.",
            )

    for order, lines in display_orders.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "display_order",
                f"Duplicate display_order '{order}'.",
            )

    result.stats["subjects"] = len(rows)
    result.stats["subject_codes"] = set(codes.keys())


# ---------------------------------------------------------------------
# chapters.csv
# ---------------------------------------------------------------------

def validate_chapters(raw, result):
    filename = "chapters.csv"
    header, rows = raw[filename]["header"], raw[filename]["rows"]
    subject_codes = result.stats.get("subject_codes", set())

    check_required_columns(filename, header, FINALIZED_HEADERS[filename], result)

    combo_seen = defaultdict(list)
    order_per_subject_paper = defaultdict(list)
    chapter_index = defaultdict(set)

    for row in rows:
        line = row["_line"]
        subject_code = row.get("subject_code", "").strip()
        paper = row.get("paper", "").strip()
        chapter_no = row.get("chapter_no", "").strip()
        chapter_name = row.get("chapter_name", "").strip()
        display_order = row.get("display_order", "").strip()

        if not subject_code:
            result.error(filename, line, "subject_code", "Missing subject_code.")
        elif subject_code not in subject_codes:
            result.error(
                filename, line, "subject_code",
                f"Unknown subject code '{subject_code}' (not present in subjects.csv).",
            )

        if not paper:
            result.error(filename, line, "paper", "Missing paper.")
        elif paper not in PAPER_VALUES:
            result.error(
                filename, line, "paper",
                f"paper '{paper}' must be '1' or '2'.",
            )

        if not chapter_no:
            result.error(filename, line, "chapter_no", "Missing chapter_no.")
        elif not chapter_no.isdigit():
            result.error(
                filename, line, "chapter_no",
                f"chapter_no '{chapter_no}' is not a valid integer.",
            )

        if not chapter_name:
            result.error(filename, line, "chapter_name", "Missing chapter_name.")

        if not display_order:
            result.error(filename, line, "display_order", "Missing display_order.")
        elif not display_order.isdigit():
            result.error(
                filename, line, "display_order",
                f"display_order '{display_order}' is not a valid integer.",
            )

        if subject_code and paper and chapter_no:
            combo_seen[(subject_code, paper, chapter_no)].append(line)
            chapter_index[(subject_code, paper)].add(chapter_no)
        if subject_code and paper and display_order:
            order_per_subject_paper[(subject_code, paper, display_order)].append(line)

    for (subject_code, paper, chapter_no), lines in combo_seen.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "subject_code, paper, chapter_no",
                f"Duplicate (subject_code, paper, chapter_no) = "
                f"('{subject_code}', '{paper}', '{chapter_no}').",
            )

    for (subject_code, paper, order), lines in order_per_subject_paper.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "display_order",
                f"Duplicate display_order '{order}' within subject '{subject_code}' paper {paper}.",
            )

    result.stats["chapters"] = len(rows)
    result.stats["chapter_index"] = chapter_index


# ---------------------------------------------------------------------
# routine.csv
# ---------------------------------------------------------------------

def validate_routine(raw, result):
    filename = "routine.csv"
    header, rows = raw[filename]["header"], raw[filename]["rows"]
    subject_codes = result.stats.get("subject_codes", set())

    check_required_columns(filename, header, FINALIZED_HEADERS[filename], result)

    class_lecture_lines = defaultdict(list)
    all_event_types = Counter()
    lecture_numbers_by_prefix = defaultdict(dict)
    class_lecture_codes = set()
    class_subject_counts = Counter()
    general_session_lines = []

    for row in rows:
        line = row["_line"]
        date = row.get("date", "").strip()
        event_type = row.get("event_type", "").strip()
        subject_code = row.get("subject_code", "").strip()
        lecture_code = row.get("lecture_code", "").strip()

        if not date:
            result.error(filename, line, "date", "Missing date.")
        elif not DATE_RE.match(date):
            result.error(
                filename, line, "date",
                f"Invalid date format '{date}'. Expected YYYY-MM-DD.",
            )
        else:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                result.error(filename, line, "date", f"'{date}' is not a real calendar date.")

        for field in ("start_time", "end_time"):
            value = row.get(field, "").strip()
            if value and not TIME_RE.match(value):
                result.error(
                    filename, line, field,
                    f"Invalid time format '{value}'. Expected HH:MM (24-hour).",
                )

        if not event_type:
            result.error(filename, line, "event_type", "Missing event_type.")
        else:
            all_event_types[event_type] += 1
            if event_type not in FINALIZED_EVENT_TYPES:
                result.error(
                    filename, line, "event_type",
                    f"event_type '{event_type}' is not one of the finalized values "
                    f"({', '.join(sorted(FINALIZED_EVENT_TYPES))}).",
                )

        if event_type == "CLASS":
            # Orientation-style general session: both subject_code and
            # lecture_code intentionally blank (not tied to any subject).
            # Only flagged as an error when exactly one of the two is
            # blank, which would be an inconsistent/partial row.
            if not subject_code and not lecture_code:
                general_session_lines.append(line)
            else:
                if not subject_code:
                    result.error(
                        filename, line, "subject_code",
                        "subject_code is required for event_type CLASS when "
                        "lecture_code is present.",
                    )
                elif subject_code not in subject_codes:
                    result.error(
                        filename, line, "subject_code",
                        f"Unknown subject code '{subject_code}' (not present in subjects.csv).",
                    )
                else:
                    class_subject_counts[subject_code] += 1

                if not lecture_code:
                    result.error(
                        filename, line, "lecture_code",
                        "lecture_code is required for event_type CLASS when "
                        "subject_code is present.",
                    )
                else:
                    class_lecture_lines[lecture_code].append(line)
                    class_lecture_codes.add(lecture_code)

                    match = LECTURE_CODE_RE.match(lecture_code)
                    if match:
                        prefix, number = match.group(1), int(match.group(2))
                        lecture_numbers_by_prefix[prefix][number] = line

    # Duplicate lecture codes: only flagged when the SAME lecture_code
    # appears on more than one CLASS row. The same lecture_code recurring
    # on a DAILY_EXAM/WEEKLY_EXAM/MONTHLY_EXAM row referencing that
    # lecture is expected dataset structure, not a duplicate Lecture.
    for lecture_code, lines in class_lecture_lines.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "lecture_code",
                f"Duplicate lecture_code '{lecture_code}' across multiple CLASS rows "
                "(duplicate lecture_code within a routine).",
            )

    # Duplicate routine order: the same lecture number (e.g. 05) reused
    # under the same subject prefix by a different lecture_code string.
    seen_numbers = defaultdict(lambda: defaultdict(list))
    for lecture_code, lines in class_lecture_lines.items():
        match = LECTURE_CODE_RE.match(lecture_code)
        if match:
            prefix, number = match.group(1), match.group(2)
            seen_numbers[prefix][number].append(lecture_code)

    for prefix, numbers in seen_numbers.items():
        for number, codes in numbers.items():
            if len(set(codes)) > 1:
                result.error(
                    filename, "-", "lecture_code",
                    f"Duplicate routine order: subject '{prefix}' lecture number "
                    f"'{number}' is used by multiple lecture codes: {', '.join(sorted(set(codes)))}.",
                )

    # Lecture numbering consistency (gaps), excluding the known/allowed
    # gap at number 6.
    for prefix, numbers in lecture_numbers_by_prefix.items():
        used = sorted(numbers.keys())
        if not used:
            continue
        expected = set(range(used[0], used[-1] + 1))
        missing = sorted(expected - set(used) - ALLOWED_NUMBERING_GAPS)
        if missing:
            result.warning(
                filename, "-", "lecture_code",
                f"Subject '{prefix}': lecture numbering gap(s) at "
                f"{', '.join(str(n) for n in missing)} (between "
                f"{prefix}-{used[0]:02d} and {prefix}-{used[-1]:02d}).",
            )

    if all_event_types:
        result.note(
            "routine.csv event_type values found (all finalized): "
            + ", ".join(f"{k} ({v})" for k, v in sorted(all_event_types.items()))
        )

    if general_session_lines:
        result.note(
            "routine.csv: general/orientation CLASS session(s) with no "
            "subject_code/lecture_code (by design, see Architectural "
            f"Decisions): row(s) {', '.join(map(str, general_session_lines))}."
        )

    # Subjects with zero CLASS rows in routine.csv are self-study subjects
    # (no scheduled live class in this routine) - their lecture codes are
    # not expected to resolve against routine.csv.
    self_study_subjects = {
        code for code in subject_codes if class_subject_counts.get(code, 0) == 0
    }
    if self_study_subjects:
        result.note(
            "Subject(s) with no CLASS rows in routine.csv, treated as "
            "self-study (their lecture codes are not required to exist as "
            "routine.csv CLASS rows): " + ", ".join(sorted(self_study_subjects))
        )

    result.stats["routine_rows"] = len(rows)
    result.stats["lectures"] = len(class_lecture_codes)
    result.stats["class_lecture_codes"] = class_lecture_codes
    result.stats["self_study_subjects"] = self_study_subjects


# ---------------------------------------------------------------------
# lecture_topics.csv
# ---------------------------------------------------------------------

def validate_lecture_topics(raw, result):
    filename = "lecture_topics.csv"
    header, rows = raw[filename]["header"], raw[filename]["rows"]
    subject_codes = result.stats.get("subject_codes", set())
    class_lecture_codes = result.stats.get("class_lecture_codes", set())
    self_study_subjects = result.stats.get("self_study_subjects", set())
    chapter_index = result.stats.get("chapter_index", {})

    check_required_columns(filename, header, FINALIZED_HEADERS[filename], result)

    display_order_per_lecture = defaultdict(list)
    topic_per_lecture = defaultdict(list)
    orphan_lecture_codes = set()

    for row in rows:
        line = row["_line"]
        lecture_code = row.get("lecture_code", "").strip()
        subject_code = row.get("subject_code", "").strip()
        chapter_no = row.get("chapter_no", "").strip()
        topic = row.get("topic", "").strip()
        display_order = row.get("display_order", "").strip()

        if not lecture_code:
            result.error(filename, line, "lecture_code", "Missing lecture_code.")
        elif lecture_code not in class_lecture_codes:
            match = LECTURE_CODE_RE.match(lecture_code)
            prefix = match.group(1) if match else None
            if prefix in self_study_subjects or subject_code in self_study_subjects:
                pass  # self-study subject: no CLASS row is expected to exist
            elif is_allowed_gap_lecture(lecture_code):
                pass  # intentional numbering gap (e.g. -06): class skipped, content still valid
            else:
                orphan_lecture_codes.add(lecture_code)
                result.error(
                    filename, line, "lecture_code",
                    f"lecture_code '{lecture_code}' does not exist as a CLASS row in routine.csv.",
                )

        if not subject_code:
            result.error(filename, line, "subject_code", "Missing subject_code.")
        elif subject_code not in subject_codes:
            result.error(
                filename, line, "subject_code",
                f"Unknown subject code '{subject_code}' (not present in subjects.csv).",
            )

        if not chapter_no:
            result.error(filename, line, "chapter_no", "Missing chapter_no.")
        elif subject_code in SUBJECTS_WITHOUT_CHAPTERS:
            pass  # free-text lesson reference; no chapter breakdown to resolve against
        else:
            parsed = parse_chapter_ref(chapter_no)
            if parsed is None:
                result.error(
                    filename, line, "chapter_no",
                    f"chapter_no '{chapter_no}' does not match the finalized "
                    "'<paper> পত্র অধ্যায়-<chapter>' reference format.",
                )
            else:
                paper, number = parsed
                key = (subject_code, paper)
                if key not in chapter_index:
                    result.error(
                        filename, line, "chapter_no",
                        f"No chapters exist for subject '{subject_code}' paper {paper} in chapters.csv.",
                    )
                elif str(number) not in chapter_index[key]:
                    result.error(
                        filename, line, "chapter_no",
                        f"Chapter {number} does not exist for subject '{subject_code}' "
                        f"paper {paper} in chapters.csv.",
                    )

        if not topic:
            result.error(filename, line, "topic", "Missing topic.")

        if not display_order:
            result.warning(filename, line, "display_order", "Missing display_order.")
        elif not display_order.isdigit():
            result.error(
                filename, line, "display_order",
                f"display_order '{display_order}' is not a valid integer.",
            )

        if lecture_code and display_order:
            display_order_per_lecture[(lecture_code, display_order)].append(line)
        if lecture_code and topic:
            topic_per_lecture[(lecture_code, topic)].append(line)

    for (lecture_code, order), lines in display_order_per_lecture.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "display_order",
                f"Duplicate display_order '{order}' within lecture '{lecture_code}'.",
            )

    for (lecture_code, topic), lines in topic_per_lecture.items():
        if len(lines) > 1:
            short = f"{topic[:60]}..." if len(topic) > 60 else topic
            result.error(
                filename, ", ".join(map(str, lines)), "topic",
                f"Duplicate topic within lecture '{lecture_code}': '{short}'",
            )

    result.stats["lecture_topics"] = len(rows)
    result.stats["orphan_lecture_topic_lecture_codes"] = orphan_lecture_codes


# ---------------------------------------------------------------------
# exams.csv
# ---------------------------------------------------------------------

def validate_exams(raw, result):
    filename = "exams.csv"
    header, rows = raw[filename]["header"], raw[filename]["rows"]
    class_lecture_codes = result.stats.get("class_lecture_codes", set())
    self_study_subjects = result.stats.get("self_study_subjects", set())

    check_required_columns(filename, header, FINALIZED_HEADERS[filename], result)

    exam_code_lines = defaultdict(list)
    exam_number_by_prefix = defaultdict(dict)
    orphan_lecture_refs = set()

    prev_date = None
    prev_row_desc = None

    for row in rows:
        line = row["_line"]
        exam_type = row.get("exam_type", "").strip()
        exam_code = row.get("exam_code", "").strip()
        date_value = row.get("exam_date", "").strip()
        online_start = row.get("online_start", "").strip()
        online_end = row.get("online_end", "").strip()

        if not row.get("title", "").strip():
            result.error(filename, line, "title", "Missing title.")

        if exam_type and exam_type not in LOCKED_EXAM_TYPES:
            result.warning(
                filename, line, "exam_type",
                f"exam_type '{exam_type}' is not one of the recognized values "
                f"({', '.join(sorted(LOCKED_EXAM_TYPES))}).",
            )
        elif not exam_type:
            result.error(filename, line, "exam_type", "Missing exam_type.")

        if not exam_code:
            result.error(filename, line, "exam_code", "Missing exam_code.")
        else:
            exam_code_lines[exam_code].append(line)
            match = LECTURE_CODE_RE.match(exam_code)
            if match:
                prefix, number = match.group(1), int(match.group(2))
                exam_number_by_prefix[prefix][number] = line

        exam_date_parsed = None
        if not date_value:
            result.error(filename, line, "exam_date", "Missing exam date.")
        elif not DATE_RE.match(date_value):
            result.error(
                filename, line, "exam_date",
                f"Invalid date format '{date_value}'. Expected YYYY-MM-DD.",
            )
        else:
            try:
                exam_date_parsed = datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                result.error(filename, line, "exam_date", f"'{date_value}' is not a real calendar date.")
            else:
                if prev_date is not None and exam_date_parsed < prev_date:
                    result.warning(
                        filename, line, "exam_date",
                        f"Exam date '{date_value}' is out of chronological order "
                        f"(follows '{prev_row_desc}').",
                    )
                prev_date = exam_date_parsed
                prev_row_desc = date_value

        for field, value in (("online_start", online_start), ("online_end", online_end)):
            if value and not DATE_RE.match(value):
                result.error(
                    filename, line, field,
                    f"Invalid date format '{value}'. Expected YYYY-MM-DD.",
                )

        if online_start and online_end and DATE_RE.match(online_start) and DATE_RE.match(online_end):
            if online_start > online_end:
                result.error(
                    filename, line, "online_start, online_end",
                    f"online_start '{online_start}' is after online_end '{online_end}'.",
                )

        raw_codes = row.get("lecture_codes", "").strip()
        if not raw_codes:
            result.warning(filename, line, "lecture_codes", "No covered lectures listed.")
        else:
            codes = [c.strip() for c in raw_codes.split(",")]
            empties = [i + 1 for i, c in enumerate(codes) if c == ""]
            if empties:
                result.error(
                    filename, line, "lecture_codes",
                    f"Empty lecture code entry at position(s) {empties} in '{raw_codes}'.",
                )

            non_empty = [c for c in codes if c]
            dupes = [c for c, n in Counter(non_empty).items() if n > 1]
            if dupes:
                result.error(
                    filename, line, "lecture_codes",
                    f"Duplicate lecture code reference(s) within the same exam: {', '.join(dupes)}.",
                )

            for code in non_empty:
                if code in class_lecture_codes:
                    continue
                match = LECTURE_CODE_RE.match(code)
                prefix = match.group(1) if match else None
                if prefix in self_study_subjects:
                    continue  # self-study subject: no CLASS row expected
                if is_allowed_gap_lecture(code):
                    continue  # intentional numbering gap (e.g. -06)
                orphan_lecture_refs.add(code)
                result.error(
                    filename, line, "lecture_codes",
                    f"lecture_code '{code}' does not exist as a CLASS row in routine.csv.",
                )

    for exam_code, lines in exam_code_lines.items():
        if len(lines) > 1:
            result.error(
                filename, ", ".join(map(str, lines)), "exam_code",
                f"Duplicate exam_code '{exam_code}'.",
            )

    for prefix, numbers in exam_number_by_prefix.items():
        used = sorted(numbers.keys())
        if not used:
            continue
        expected = set(range(used[0], used[-1] + 1))
        missing = sorted(expected - set(used) - ALLOWED_NUMBERING_GAPS)
        if missing:
            result.warning(
                filename, "-", "exam_code",
                f"Exam series '{prefix}': numbering gap(s) at "
                f"{', '.join(str(n) for n in missing)}.",
            )

    result.stats["exams"] = len(rows)
    result.stats["orphan_exam_lecture_refs"] = orphan_lecture_refs


# ---------------------------------------------------------------------
# Cross-file validation
# ---------------------------------------------------------------------

def validate_cross_file(raw, result):
    subject_codes = result.stats.get("subject_codes", set())
    class_lecture_codes = result.stats.get("class_lecture_codes", set())

    referenced_subjects = set()
    for row in raw["chapters.csv"]["rows"]:
        code = row.get("subject_code", "").strip()
        if code:
            referenced_subjects.add(code)
    for row in raw["routine.csv"]["rows"]:
        code = row.get("subject_code", "").strip()
        if code:
            referenced_subjects.add(code)
    for row in raw["lecture_topics.csv"]["rows"]:
        code = row.get("subject_code", "").strip()
        if code:
            referenced_subjects.add(code)

    orphan_subjects = subject_codes - referenced_subjects
    if orphan_subjects:
        result.note(
            "Subject(s) defined in subjects.csv but never referenced by "
            "chapters.csv, routine.csv or lecture_topics.csv: "
            + ", ".join(sorted(orphan_subjects))
        )

    orphan_lecture_topic_refs = result.stats.get("orphan_lecture_topic_lecture_codes", set())
    orphan_exam_refs = result.stats.get("orphan_exam_lecture_refs", set())
    all_orphan_lecture_refs = orphan_lecture_topic_refs | orphan_exam_refs
    if all_orphan_lecture_refs:
        result.note(
            "Lecture code(s) referenced by lecture_topics.csv and/or exams.csv "
            "but absent from routine.csv (CLASS rows) and not a self-study "
            "subject: " + ", ".join(sorted(all_orphan_lecture_refs))
        )

    referenced_lectures_without_topics = class_lecture_codes - {
        row.get("lecture_code", "").strip() for row in raw["lecture_topics.csv"]["rows"]
    }
    if referenced_lectures_without_topics:
        result.note(
            "Lecture(s) in routine.csv with no matching row in lecture_topics.csv: "
            + ", ".join(sorted(referenced_lectures_without_topics))
        )


QUOTED_RE = re.compile(r"'[^']*'")


def render_issue_group(issues, individual_threshold=5):
    """Render a list of issues, grouping repeats of the same kind together.

    Issues sharing the same file/column and the same message with quoted
    values blanked out (e.g. "Unknown subject code 'M'." and "... 'P'.")
    are treated as one group. Groups of individual_threshold or fewer are
    rendered in full, one block per row (matching the
    file/row/column/message example format from the CSV Import
    Specification). Larger groups are rendered as a single summary line
    listing every affected row and every distinct value, so the report
    stays readable without dropping any information.
    """
    grouped = defaultdict(list)
    order = []
    for issue in issues:
        key = (issue["file"], issue["column"], QUOTED_RE.sub("'…'", issue["message"]))
        if key not in grouped:
            order.append(key)
        grouped[key].append(issue)

    lines = []
    for key in order:
        file, column, template = key
        members = grouped[key]

        if len(members) <= individual_threshold:
            for issue in members:
                lines.append(f"**{file}**")
                lines.append(f"Row {issue['row']}")
                lines.append(f"Column: {column}")
                lines.append("")
                lines.append(issue["message"])
                lines.append("")
            continue

        rows = [str(m["row"]) for m in members]
        values = []
        seen_values = set()
        for m in members:
            for v in QUOTED_RE.findall(m["message"]):
                if v not in seen_values:
                    seen_values.add(v)
                    values.append(v)

        lines.append(f"**{file}**")
        lines.append(f"Column: {column}")
        lines.append("")
        lines.append(f"{template} — {len(members)} occurrences")
        lines.append(f"Rows: {', '.join(rows)}")
        if values:
            lines.append(f"Values involved: {', '.join(values)}")
        lines.append("")

    return lines


# ---------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------

def render_report(base_dir, raw, result):
    lines = []
    lines.append("# CSV Dataset Validation Report")
    lines.append("")
    lines.append(f"**Directory:** `{base_dir}`")
    lines.append("")

    if raw is None:
        lines.append("## Summary")
        lines.append("")
        lines.append("❌ **Dataset INVALID** - one or more required files are missing.")
        lines.append("")
        lines.append("## Errors")
        lines.append("")
        for e in result.errors:
            lines.append(f"- `{e['file']}` — {e['message']}")
        return "\n".join(lines) + "\n"

    status = "✅ Dataset valid" if not result.errors else "❌ Dataset INVALID"
    lines.append("## Summary")
    lines.append("")
    lines.append(f"{status} — {len(result.errors)} error(s), {len(result.warnings)} warning(s).")
    lines.append("")

    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- Subjects: {result.stats.get('subjects', 0)}")
    lines.append(f"- Chapters: {result.stats.get('chapters', 0)}")
    lines.append(f"- Lectures (CLASS rows in routine.csv): {result.stats.get('lectures', 0)}")
    lines.append(f"- Routine rows (all event types): {result.stats.get('routine_rows', 0)}")
    lines.append(f"- Lecture Topics: {result.stats.get('lecture_topics', 0)}")
    lines.append(f"- Exams: {result.stats.get('exams', 0)}")
    lines.append("")

    lines.append("## Dataset Design Notes")
    lines.append("")
    lines.append(
        "This validator targets the finalized dataset design (subject-level "
        "codes P/C/M/B/E/BA, chapters.csv with an explicit `paper` column, "
        "Bengali paper+chapter references in lecture_topics.csv, the "
        "finalized event_type enum, and the finalized exams.csv schema) "
        "rather than the original 06_CSV_Import_Specification.md draft — "
        "see PROJECT_PROGRESS.md, \"Dataset Revision\" entry, for the full "
        "rationale."
    )
    lines.append("")
    if result.notes:
        for n in result.notes:
            lines.append(f"- {n}")
    else:
        lines.append("- No additional notes.")
    lines.append("")

    lines.append("## Errors")
    lines.append("")
    if result.errors:
        lines.extend(render_issue_group(result.errors))
    else:
        lines.append("✓ No errors found.")
        lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if result.warnings:
        lines.extend(render_issue_group(result.warnings))
    else:
        lines.append("✓ No warnings.")
        lines.append("")

    lines.append("## CSV Quality Checks")
    lines.append("")
    if result.quality:
        for q in result.quality:
            lines.append(f"- `{q['file']}`: {q['message']}")
    else:
        lines.append(
            "- ✓ All files are UTF-8 encoded, no BOM, no duplicate headers, "
            "no cell-level trailing/leading whitespace, no NUL bytes. "
            "Blank separator rows in `lecture_topics.csv` were detected and "
            "ignored per the \"blank rows are ignored\" rule."
        )
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    if result.errors:
        lines.append(
            "❌ **Dataset is NOT ready for import.** The errors above must be "
            "resolved before the CSV import system (Milestone 3) is "
            "implemented."
        )
    else:
        lines.append(
            "✅ **Dataset is valid and ready for import.** All cross-file "
            "foreign keys resolve successfully against the finalized "
            "dataset design."
        )
    lines.append("")

    return "\n".join(lines) + "\n"
