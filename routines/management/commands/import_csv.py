"""Import the finalized CSV dataset (subjects, chapters, routine,
lecture_topics, exams) into the database, in dependency order.

Usage:
    python manage.py import_csv [--dir DIR] [--user USERNAME]
    python manage.py import_csv --preview [--dir DIR]
    python manage.py import_csv --dry-run [--dir DIR]

Each stage runs inside its own transaction (see BaseImporter.run()) - a
single bad row rolls back that file's changes and stops the command
before any later stage runs. Safe to run repeatedly: every importer uses
update_or_create() keyed on each model's natural identity, so re-running
does not create duplicate data.

Milestone 10 additions (dataset lifecycle management - see
PROJECT_PROGRESS.md): every real import now also creates a
`DatasetVersion` (statistics + an archived copy of the source CSVs,
activated as the current dataset) and an `ImportLog` audit record.
`--preview` validates and compares the new CSVs against the database
without writing anything; `--dry-run` runs the real import inside an
outer transaction that is always rolled back afterward. The five-stage
import loop itself (`run_import_stages()`) is unchanged from before
this milestone - only what wraps around it is new.
"""

import sys
import time
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from routines.models import ImportLog
from routines.services.csv.chapter_importer import ChapterImporter
from routines.services.csv.exam_importer import ExamImporter
from routines.services.csv.lecture_topic_importer import LectureTopicImporter
from routines.services.csv.routine_importer import RoutineImporter
from routines.services.csv.subject_importer import SubjectImporter
from routines.services.csv.validators import ImportValidationError
from routines.services.dataset import versioning
from routines.services.dataset.comparison import COMPARISON_SECTIONS, compare_all, detect_duplicates
from routines.services.dataset.statistics import collect_statistics

IMPORTER_VERSION = "1.0"

# (importer class, human label for "Importing ...", unit label for the count)
IMPORT_STAGES = [
    (SubjectImporter, "subjects", "subjects"),
    (ChapterImporter, "chapters", "chapters"),
    (RoutineImporter, "routines", "routine events"),
    (LectureTopicImporter, "lecture topics", "lecture topics"),
    (ExamImporter, "exams", "exams"),
]


class _DryRunRollback(Exception):
    """Raised deliberately inside a `transaction.atomic()` block to
    force a clean rollback at the end of a successful dry run - never
    surfaced to the user as an error."""


def format_error(exc: ImportValidationError) -> str:
    lines = [
        "ERROR",
        "",
        "File:",
        exc.file,
        "",
        "Row:",
        str(exc.row),
        "",
        "Reason:",
        exc.reason,
    ]
    for label, value in exc.details.items():
        lines += ["", f"{label}:", str(value)]
    return "\n".join(lines)


def run_import_stages(base_dir, stdout, style):
    """Runs every `IMPORT_STAGES` importer against `base_dir`, in
    order - this is the exact same loop `import_csv` ran before
    Milestone 10, extracted verbatim so it can be reused unchanged by
    a real import, a `--dry-run` (wrapped in an outer transaction that
    gets rolled back), and `rollback_dataset` (re-importing an
    archived previous version). Raises `ImportValidationError` on the
    first invalid row, exactly as before; returns
    (imported_counts, skipped_counts) dicts keyed by stage label on
    success.
    """
    imported_counts = {}
    skipped_counts = {}
    for importer_class, label, unit in IMPORT_STAGES:
        stdout.write(f"Importing {label}...")
        importer = importer_class(base_dir, stdout)
        count = importer.run()
        imported_counts[label] = count
        skipped_counts[label] = len(importer.skipped)
        stdout.write(style.SUCCESS(f"✓ Imported {count} {unit}"))
        stdout.write("")
    return imported_counts, skipped_counts


class Command(BaseCommand):
    help = "Import subjects/chapters/routine/lecture_topics/exams CSVs into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            default=str(settings.BASE_DIR),
            help="Directory containing the CSV files (default: project root).",
        )
        parser.add_argument(
            "--preview", action="store_true",
            help="Validate and compare the CSVs against the current database. Writes nothing.",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Run the full import inside a transaction, then roll it back. For testing.",
        )
        parser.add_argument(
            "--user", default=None,
            help="Username to record as the importer in ImportLog/DatasetVersion (optional).",
        )

    def handle(self, *args, **options):
        # Windows consoles often default to a codepage (e.g. cp1252) that
        # cannot encode the checkmark/warning symbols used below.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        base_dir = Path(options["dir"])
        user = self._resolve_user(options.get("user"))

        if options["preview"]:
            self._run_preview(base_dir, user)
        elif options["dry_run"]:
            self._run_dry_run(base_dir, user)
        else:
            self._run_real_import(base_dir, user)

    @staticmethod
    def _resolve_user(username):
        if not username:
            return None
        return get_user_model().objects.filter(username=username).first()

    # -- real import ----------------------------------------------------

    def _run_real_import(self, base_dir, user):
        started_at = timezone.now()
        start = time.monotonic()

        try:
            imported_counts, skipped_counts = run_import_stages(base_dir, self.stdout, self.style)
        except ImportValidationError as exc:
            duration = time.monotonic() - start
            self.stdout.write("")
            self.stdout.write(format_error(exc))
            self.stdout.write("")
            self.stdout.write(self.style.ERROR(
                f"Import aborted while processing {exc.file}. "
                f"No changes from this stage were saved; earlier stages are unaffected."
            ))
            ImportLog.objects.create(
                importer_version=IMPORTER_VERSION, user=user, started_at=started_at,
                duration_seconds=duration, status=ImportLog.Status.FAILED,
                errors=str(exc),
            )
            raise SystemExit(1)

        duration = time.monotonic() - start
        self.stdout.write("-" * 32)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import completed successfully."))

        statistics = collect_statistics(base_dir)
        version = versioning.create_dataset_version(base_dir, statistics, user=user)
        versioning.activate_version(version)

        ImportLog.objects.create(
            dataset_version=version, importer_version=IMPORTER_VERSION, user=user,
            started_at=started_at, duration_seconds=duration, status=ImportLog.Status.SUCCESS,
            imported_counts=imported_counts, skipped_counts=skipped_counts,
        )
        self.stdout.write(f"Dataset version '{version.version_name}' created and activated.")

    # -- dry run ----------------------------------------------------------

    def _run_dry_run(self, base_dir, user):
        self.stdout.write(self.style.WARNING("DRY RUN - no changes will be saved."))
        self.stdout.write("")
        started_at = timezone.now()
        start = time.monotonic()
        imported_counts, skipped_counts = {}, {}
        failure = None

        try:
            with transaction.atomic():
                imported_counts, skipped_counts = run_import_stages(base_dir, self.stdout, self.style)
                self.stdout.write("-" * 32)
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS(
                    "Dry run completed successfully - rolling back now."
                ))
                raise _DryRunRollback()
        except _DryRunRollback:
            pass
        except ImportValidationError as exc:
            failure = exc
            self.stdout.write("")
            self.stdout.write(format_error(exc))
            self.stdout.write("")
            self.stdout.write(self.style.ERROR(
                "Dry run failed validation - nothing was saved (as always)."
            ))

        duration = time.monotonic() - start
        ImportLog.objects.create(
            importer_version=IMPORTER_VERSION, user=user, started_at=started_at,
            duration_seconds=duration, status=ImportLog.Status.DRY_RUN,
            imported_counts=imported_counts, skipped_counts=skipped_counts,
            errors=str(failure) if failure else "",
        )

        if failure:
            raise SystemExit(1)
        self.stdout.write(self.style.WARNING("All changes rolled back. Database is unchanged."))

    # -- preview ----------------------------------------------------------

    def _run_preview(self, base_dir, user):
        self.stdout.write(self.style.WARNING(
            "PREVIEW - validating and comparing only. No changes will be saved."
        ))
        self.stdout.write("")
        started_at = timezone.now()
        start = time.monotonic()

        duplicates = detect_duplicates(base_dir)
        if any(duplicates.values()):
            self.stdout.write(self.style.WARNING("Duplicate keys found in the new dataset:"))
            for entity, keys in duplicates.items():
                if keys:
                    self.stdout.write(f"  {entity}: {keys}")
            self.stdout.write("")

        for importer_class, label, _unit in IMPORT_STAGES:
            importer = importer_class(base_dir, self.stdout)
            try:
                count = importer.validate_only()
            except ImportValidationError as exc:
                self.stdout.write(format_error(exc))
                self.stdout.write("")
                self.stdout.write(self.style.ERROR(
                    f"Preview validation failed while processing {exc.file}."
                ))
                duration = time.monotonic() - start
                ImportLog.objects.create(
                    importer_version=IMPORTER_VERSION, user=user, started_at=started_at,
                    duration_seconds=duration, status=ImportLog.Status.PREVIEW,
                    errors=str(exc),
                )
                raise SystemExit(1)
            self.stdout.write(self.style.SUCCESS(f"✓ {label}: {count} rows valid"))
        self.stdout.write("")

        diff = compare_all(base_dir)
        self._print_comparison(diff)

        duration = time.monotonic() - start
        ImportLog.objects.create(
            importer_version=IMPORTER_VERSION, user=user, started_at=started_at,
            duration_seconds=duration, status=ImportLog.Status.PREVIEW,
        )

    def _print_comparison(self, diff):
        for key, label, _fn in COMPARISON_SECTIONS:
            section = diff[key]
            self.stdout.write(
                f"{label}: {len(section['added'])} added, {len(section['modified'])} modified, "
                f"{len(section['removed'])} removed, {len(section['unchanged'])} unchanged"
            )
        events = diff["routine_events"]
        self.stdout.write(
            f"Routine Events: {events['total_rows']} rows "
            f"({', '.join(f'{v} {k}' for k, v in events['by_event_type'].items())})"
        )
        self.stdout.write("")
