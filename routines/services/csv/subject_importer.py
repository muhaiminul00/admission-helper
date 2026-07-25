"""Imports subjects.csv into the Subject model."""

from subjects.models import Subject

from .base_importer import BaseImporter
from .validators import DuplicateTracker, parse_int, require


class SubjectImporter(BaseImporter):
    filename = "subjects.csv"
    required_columns = ["code", "name", "display_order"]

    def __init__(self, base_dir, stdout):
        super().__init__(base_dir, stdout)
        self._dup_code = DuplicateTracker(
            self.filename, "code", "Duplicate subject code '{key}' in subjects.csv."
        )

    def validate_row(self, row):
        line = row["_line"]
        code = require(self.field(row, "code"), self.filename, line, "code")
        require(self.field(row, "name"), self.filename, line, "name")
        parse_int(self.field(row, "display_order"), self.filename, line, "display_order")
        self._dup_code.check(code, line)

    def import_row(self, row):
        code = self.field(row, "code").strip()
        name = self.field(row, "name").strip()
        display_order = int(self.field(row, "display_order").strip())

        Subject.objects.update_or_create(
            code=code,
            defaults={"name": name, "display_order": display_order},
        )
        self.imported_count += 1
