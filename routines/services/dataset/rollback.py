"""Rollback to a previous DatasetVersion (Milestone 10).

Reuses the exact same import pipeline (`import_csv`'s
`run_import_stages()`) a normal import runs - rollback re-imports the
target version's archived CSVs rather than attempting to reconstruct
rows from `DatasetVersion.statistics` (a summary, not a snapshot).
Wrapped in one `transaction.atomic()` so a failure partway through
(e.g. an archived CSV was hand-edited and no longer validates) leaves
the database exactly as it was before the rollback was attempted -
never a half-restored dataset.
"""

import io
import time
from pathlib import Path

from django.core.management.color import no_style
from django.db import transaction
from django.utils import timezone

from routines.models import ImportLog

from . import versioning


class RollbackError(Exception):
    """Raised when a rollback cannot proceed (no previous version, or
    its archived CSVs are missing)."""


def rollback_to(target_version, user=None, stdout=None):
    """Re-imports `target_version`'s archived CSVs and makes it active
    again. Returns `target_version`. Raises `RollbackError` if the
    archive is missing, or `ImportValidationError` (re-raised
    unchanged) if the archived CSVs themselves fail validation -
    either way, nothing is left half-applied since everything runs
    inside one transaction.
    """
    # Imported here, not at module level, to avoid a circular import
    # (import_csv.py -> routines.services.dataset -> this module).
    from routines.management.commands.import_csv import IMPORTER_VERSION, run_import_stages

    if stdout is None:
        stdout = io.StringIO()
    style = no_style()

    archive_path = Path(target_version.source)
    if not archive_path.exists():
        raise RollbackError(
            f"Archived source CSVs for '{target_version.version_name}' are missing "
            f"(expected at {archive_path}). Rollback cannot proceed."
        )

    started_at = timezone.now()
    start = time.monotonic()

    with transaction.atomic():
        imported_counts, skipped_counts = run_import_stages(archive_path, stdout, style)
        versioning.activate_version(target_version)

    duration = time.monotonic() - start
    ImportLog.objects.create(
        dataset_version=target_version, importer_version=IMPORTER_VERSION, user=user,
        started_at=started_at, duration_seconds=duration, status=ImportLog.Status.ROLLBACK,
        imported_counts=imported_counts, skipped_counts=skipped_counts,
    )

    return target_version
