"""Imports exams.csv into Exam.

Milestone 4.1: exam_code, online_start, online_end are now dedicated
Exam model fields (see routines/models.py) instead of being folded into
`notes` as labeled text - that Milestone 3 workaround is removed
entirely. `notes` is no longer written by this importer at all, since
the finalized exams.csv has no notes column - nothing to put there.

exam_code is now unique, so it is the update_or_create lookup key
(replacing the old synthetic (routine, exam_name, exam_date) key).

Every lecture_code in `lecture_codes` resolves via
get_or_create_lecture() (see lecture_topic_importer.py for the same
pattern) so `covered_lectures` entries are always linkable to a real
Lecture, even for self-study subjects or the lecture-06 gap. A
lecture_code whose subject prefix isn't a known Subject is a genuine
error, not an exemption case.
"""

from subjects.models import Subject

from .base_importer import BaseImporter
from .lecture_helpers import get_or_create_lecture
from .routine_helpers import get_or_create_routine
from .utils import LECTURE_CODE_RE
from .validators import (
    DuplicateTracker,
    ImportValidationError,
    parse_date,
    parse_date_optional,
    require,
    validate_choice,
)

EXAM_TYPE_MAP = {"WEEKLY": "Weekly", "MONTHLY": "Monthly", "SPECIAL": "Special"}


class ExamImporter(BaseImporter):
    filename = "exams.csv"
    required_columns = [
        "exam_code", "exam_type", "title", "lecture_codes", "exam_date",
        "online_start", "online_end",
    ]

    def __init__(self, base_dir, stdout):
        super().__init__(base_dir, stdout)
        self._subject_cache = {}
        self._dup_exam_code = DuplicateTracker(
            self.filename, "exam_code", "Duplicate exam_code '{key}' in exams.csv."
        )

    def _get_subject(self, code, line):
        if code not in self._subject_cache:
            try:
                self._subject_cache[code] = Subject.objects.get(code=code)
            except Subject.DoesNotExist:
                raise ImportValidationError(
                    self.filename, line,
                    f"Unknown subject code '{code}' (not present in the imported subjects).",
                    Column="lecture_codes",
                )
        return self._subject_cache[code]

    def _parse_lecture_codes(self, raw_value, line):
        codes = [c.strip() for c in raw_value.split(",")]
        empties = [i + 1 for i, c in enumerate(codes) if c == ""]
        if empties:
            raise ImportValidationError(
                self.filename, line,
                f"Empty lecture code entry at position(s) {empties} in '{raw_value}'.",
                Column="lecture_codes",
            )

        seen = set()
        for code in codes:
            if code in seen:
                raise ImportValidationError(
                    self.filename, line,
                    f"Duplicate lecture code reference within the same exam: '{code}'.",
                    Column="lecture_codes",
                )
            seen.add(code)

            match = LECTURE_CODE_RE.match(code)
            if not match:
                raise ImportValidationError(
                    self.filename, line,
                    f"lecture_code '{code}' is not in the expected '<PREFIX>-<number>' format.",
                    Column="lecture_codes",
                )
            self._get_subject(match.group(1), line)  # validates the subject prefix is known

        return codes

    def validate_row(self, row):
        line = row["_line"]
        exam_code = require(self.field(row, "exam_code"), self.filename, line, "exam_code")
        self._dup_exam_code.check(exam_code, line)

        exam_type = require(self.field(row, "exam_type"), self.filename, line, "exam_type")
        validate_choice(exam_type, set(EXAM_TYPE_MAP), self.filename, line, "exam_type")

        require(self.field(row, "title"), self.filename, line, "title")
        self._parse_lecture_codes(
            require(self.field(row, "lecture_codes"), self.filename, line, "lecture_codes"), line
        )
        parse_date(self.field(row, "exam_date"), self.filename, line, "exam_date")
        parse_date_optional(self.field(row, "online_start"), self.filename, line, "online_start")
        parse_date_optional(self.field(row, "online_end"), self.filename, line, "online_end")

    def import_row(self, row):
        line = row["_line"]
        exam_code = self.field(row, "exam_code").strip()
        exam_type = EXAM_TYPE_MAP[self.field(row, "exam_type").strip()]
        title = self.field(row, "title").strip()
        lecture_codes = self._parse_lecture_codes(
            self.field(row, "lecture_codes").strip(), line
        )
        exam_date = parse_date(self.field(row, "exam_date"), self.filename, line, "exam_date")
        online_start = parse_date_optional(
            self.field(row, "online_start"), self.filename, line, "online_start"
        )
        online_end = parse_date_optional(
            self.field(row, "online_end"), self.filename, line, "online_end"
        )

        for code in lecture_codes:
            match = LECTURE_CODE_RE.match(code)
            subject = self._get_subject(match.group(1), line)
            get_or_create_lecture(code, subject)

        from routines.models import Exam

        Exam.objects.update_or_create(
            exam_code=exam_code,
            defaults={
                "routine": get_or_create_routine(),
                "exam_name": title,
                "exam_type": exam_type,
                "exam_date": exam_date,
                "online_start": online_start,
                "online_end": online_end,
                "covered_lectures": lecture_codes,
            },
        )
        self.imported_count += 1
