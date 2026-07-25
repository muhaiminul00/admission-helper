"""Imports routine.csv into Routine + Lecture.

Design decisions (see PROJECT_PROGRESS.md, Milestone 3):

- Only `CLASS` rows become `Lecture` records. The `Lecture` model (per
  02.1_Database_Model_Contract_v1.0.md) represents "one scheduled
  lecture" and has no field for event_type; `DAILY_EXAM`/`WEEKLY_EXAM`/
  `MONTHLY_EXAM` rows have no corresponding persisted model (the CSV
  Import Specification's Database Mapping table maps routine.csv only
  to Routine + Lecture). These rows are still read, validated
  (event_type must be one of the four finalized values, date must be
  valid) and counted, but produce no database row - nothing is silently
  dropped from the console/summary reporting, it's just not persisted
  as a separate entity, since no such entity exists in the schema.
- A single fixed-name `Routine` row is reused across every import run
  (get_or_create keyed by ROUTINE_NAME) so re-running the command is
  idempotent - Routine has no natural unique key of its own besides id.
- The orientation row (CLASS, blank subject_code AND blank lecture_code)
  is recognized as an intentional general session and skipped (logged,
  not an error) rather than rejected - Lecture requires both fields, so
  it cannot be represented as a Lecture, and inventing a subject/lecture
  code for it would misrepresent the data.
"""

from subjects.models import Subject

from .base_importer import BaseImporter
from .routine_helpers import get_or_create_routine
from .validators import (
    DuplicateTracker,
    ImportValidationError,
    parse_date,
    parse_time_optional,
    require,
    validate_choice,
)

FINALIZED_EVENT_TYPES = {"CLASS", "DAILY_EXAM", "WEEKLY_EXAM", "MONTHLY_EXAM"}


class RoutineImporter(BaseImporter):
    filename = "routine.csv"
    required_columns = [
        "date", "day", "event_type", "subject_code", "lecture_code",
        "title", "start_time", "end_time", "notes",
    ]

    def __init__(self, base_dir, stdout):
        super().__init__(base_dir, stdout)
        self._routine = None
        self._subject_cache = {}
        self._dup_lecture_code = DuplicateTracker(
            self.filename, "lecture_code",
            "Duplicate lecture_code '{key}' across multiple CLASS rows.",
        )
        self.event_type_counts = {}

    def _get_routine(self):
        if self._routine is None:
            self._routine = get_or_create_routine()
        return self._routine

    def _get_subject(self, code, line):
        if code not in self._subject_cache:
            try:
                self._subject_cache[code] = Subject.objects.get(code=code)
            except Subject.DoesNotExist:
                raise ImportValidationError(
                    self.filename, line,
                    f"Unknown subject code '{code}' (not present in the imported subjects).",
                    Column="subject_code",
                )
        return self._subject_cache[code]

    @staticmethod
    def _is_general_session(row):
        return (
            not row.get("subject_code", "").strip()
            and not row.get("lecture_code", "").strip()
        )

    def validate_row(self, row):
        line = row["_line"]

        parse_date(self.field(row, "date"), self.filename, line, "date")
        event_type = validate_choice(
            self.field(row, "event_type"), FINALIZED_EVENT_TYPES,
            self.filename, line, "event_type",
        )
        self.event_type_counts[event_type] = self.event_type_counts.get(event_type, 0) + 1

        if event_type != "CLASS":
            return

        if self._is_general_session(row):
            return  # orientation-style general session - valid, handled in import_row

        subject_code = self.field(row, "subject_code").strip()
        lecture_code = self.field(row, "lecture_code").strip()

        if not subject_code:
            raise ImportValidationError(
                self.filename, line,
                "subject_code is required for event_type CLASS when lecture_code is present.",
                Column="subject_code",
            )
        if not lecture_code:
            raise ImportValidationError(
                self.filename, line,
                "lecture_code is required for event_type CLASS when subject_code is present.",
                Column="lecture_code",
            )

        self._get_subject(subject_code, line)
        require(self.field(row, "title"), self.filename, line, "title")
        require(self.field(row, "day"), self.filename, line, "day")
        parse_time_optional(self.field(row, "start_time"), self.filename, line, "start_time")
        parse_time_optional(self.field(row, "end_time"), self.filename, line, "end_time")
        self._dup_lecture_code.check(lecture_code, line)

    def import_row(self, row):
        line = row["_line"]
        event_type = self.field(row, "event_type").strip()

        if event_type != "CLASS":
            return  # acknowledged/validated above; no model exists to persist into

        if self._is_general_session(row):
            self.skip(
                line,
                "General/orientation CLASS session with no subject_code or "
                "lecture_code (by design) - not represented as a Lecture.",
            )
            return

        from routines.models import Lecture

        routine = self._get_routine()
        subject = self._get_subject(self.field(row, "subject_code").strip(), line)
        lecture_code = self.field(row, "lecture_code").strip()
        title = self.field(row, "title").strip()
        date = parse_date(self.field(row, "date"), self.filename, line, "date")
        day = self.field(row, "day").strip()
        start_time = parse_time_optional(self.field(row, "start_time"), self.filename, line, "start_time")
        end_time = parse_time_optional(self.field(row, "end_time"), self.filename, line, "end_time")
        notes = self.field(row, "notes").strip()

        Lecture.objects.update_or_create(
            routine=routine,
            lecture_code=lecture_code,
            defaults={
                "subject": subject,
                "title": title,
                "lecture_date": date,
                "day": day,
                "start_time": start_time,
                "end_time": end_time,
                "notes": notes,
            },
        )
        self.imported_count += 1
