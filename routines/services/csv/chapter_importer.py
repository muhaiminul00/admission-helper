"""Imports chapters.csv into the Chapter model.

Resolves each row using (subject_code, paper, chapter_no) - the Chapter
model's natural key since the Milestone 3.0 schema revision. Paper is
read directly from the CSV column; it is never inferred.
"""

from subjects.models import Chapter, Subject

from .base_importer import BaseImporter
from .validators import DuplicateTracker, ImportValidationError, parse_int, parse_paper, require


class ChapterImporter(BaseImporter):
    filename = "chapters.csv"
    required_columns = ["subject_code", "paper", "chapter_no", "chapter_name", "display_order"]

    def __init__(self, base_dir, stdout):
        super().__init__(base_dir, stdout)
        self._subject_cache = {}
        self._dup_key = DuplicateTracker(
            self.filename, "subject_code, paper, chapter_no",
            "Duplicate chapter key {key} in chapters.csv.",
        )

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

    def validate_row(self, row):
        line = row["_line"]
        subject_code = require(self.field(row, "subject_code"), self.filename, line, "subject_code")
        self._get_subject(subject_code, line)
        paper = parse_paper(self.field(row, "paper"), self.filename, line, "paper")
        chapter_no = parse_int(self.field(row, "chapter_no"), self.filename, line, "chapter_no")
        require(self.field(row, "chapter_name"), self.filename, line, "chapter_name")
        parse_int(self.field(row, "display_order"), self.filename, line, "display_order")
        self._dup_key.check((subject_code, paper, chapter_no), line)

    def import_row(self, row):
        line = row["_line"]
        subject = self._get_subject(self.field(row, "subject_code").strip(), line)
        paper = int(self.field(row, "paper").strip())
        chapter_no = int(self.field(row, "chapter_no").strip())
        chapter_name = self.field(row, "chapter_name").strip()
        display_order = int(self.field(row, "display_order").strip())

        Chapter.objects.update_or_create(
            subject=subject,
            paper=paper,
            chapter_no=chapter_no,
            defaults={"name": chapter_name, "display_order": display_order},
        )
        self.imported_count += 1
