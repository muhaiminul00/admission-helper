"""Shared base class for all CSV importers.

Each importer subclass supplies `filename` and `required_columns`, and
implements `validate_row()` / `import_row()`. `run()` wires them
together: read -> validate header -> validate+import every row inside a
single transaction, so a single bad row rolls back the whole file's
changes rather than partially importing it.
"""

from django.db import transaction

from .utils import read_csv_rows
from .validators import ImportValidationError


class BaseImporter:
    filename = None
    required_columns = None

    def __init__(self, base_dir, stdout):
        self.base_dir = base_dir
        self.stdout = stdout
        self.imported_count = 0
        self.skipped = []  # list of (row_line, reason) - intentional, logged skips

    @property
    def path(self):
        return self.base_dir / self.filename

    def read(self):
        if not self.path.exists():
            raise ImportValidationError(
                self.filename, "-",
                "File is missing from the import directory.",
                Directory=str(self.base_dir),
            )
        return read_csv_rows(self.path)

    def validate_header(self, header):
        header_set = set(header)
        required_set = set(self.required_columns)
        missing = [c for c in self.required_columns if c not in header_set]
        unexpected = [c for c in header if c not in required_set]
        if missing or unexpected:
            details = {}
            if missing:
                details["Missing columns"] = ", ".join(missing)
            if unexpected:
                details["Unexpected columns"] = ", ".join(unexpected)
            raise ImportValidationError(
                self.filename, "header",
                "CSV header does not match the finalized schema.",
                **details,
            )

    def field(self, row, name):
        return row.get(name, "")

    def skip(self, line, reason):
        self.skipped.append((line, reason))
        self.log(f"  ⚠ Skipped row {line}: {reason}")

    def log(self, message):
        self.stdout.write(message)

    def validate_row(self, row):
        raise NotImplementedError

    def import_row(self, row):
        raise NotImplementedError

    def run(self):
        header, rows = self.read()
        self.validate_header(header)

        with transaction.atomic():
            for row in rows:
                self.validate_row(row)
                self.import_row(row)

        return self.imported_count

    def validate_only(self):
        """Milestone 10: read + validate every row, without calling
        `import_row()` and without a transaction (nothing is written,
        so nothing needs rolling back) - the "validate" half of
        `import_csv --preview`, reusing this class's own
        `validate_row()` logic exactly as `run()` does, rather than a
        second, separate validation pass.
        """
        header, rows = self.read()
        self.validate_header(header)
        for row in rows:
            self.validate_row(row)
        return len(rows)
