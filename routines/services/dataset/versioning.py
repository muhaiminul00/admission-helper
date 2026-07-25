"""Dataset version lifecycle: checksums, archiving, creation,
activation (Milestone 10).

`DatasetVersion.statistics` is a summary (counts), not a data
snapshot - what actually makes `rollback_dataset` able to restore a
previous version's real data is the archived copy of its source CSVs
(`archive_source_csvs()`), re-imported by
`routines/services/dataset/rollback.py` using the exact same
`IMPORT_STAGES` pipeline as a normal `import_csv` run.
"""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import transaction

from routines.models import DatasetVersion

DATASET_FILES = ["subjects.csv", "chapters.csv", "routine.csv", "lecture_topics.csv", "exams.csv"]


def _archive_root():
    """`settings.DATASET_ARCHIVE_ROOT` if set (tests override this to a
    temp directory via `override_settings`, so running the test suite
    never writes archive folders into the real project's `data/`
    directory), else `<BASE_DIR>/data/dataset_archive`."""
    configured = getattr(settings, "DATASET_ARCHIVE_ROOT", None)
    if configured is not None:
        return Path(configured)
    return Path(settings.BASE_DIR) / "data" / "dataset_archive"


def compute_checksum(base_dir):
    """SHA-256 over all five dataset CSVs, concatenated in a fixed
    order - a fingerprint used to detect "this exact dataset was
    already imported as version X" (see comparison.py)."""
    base_dir = Path(base_dir)
    digest = hashlib.sha256()
    for filename in DATASET_FILES:
        digest.update((base_dir / filename).read_bytes())
    return digest.hexdigest()


def archive_source_csvs(base_dir, version_name):
    """Copies the five source CSVs into
    `data/dataset_archive/<version_name>/` and returns that directory's
    path. Never touches `base_dir` itself - purely additive."""
    base_dir = Path(base_dir)
    target = _archive_root() / version_name
    target.mkdir(parents=True, exist_ok=True)
    for filename in DATASET_FILES:
        shutil.copy2(base_dir / filename, target / filename)
    return target


def next_version_name():
    existing = DatasetVersion.objects.count()
    return f"v{existing + 1}-{datetime.now():%Y%m%d%H%M%S}"


def create_dataset_version(base_dir, statistics, user=None, description="", version_name=None):
    """Archives the source CSVs and creates (but does not activate) a
    new `DatasetVersion` row. Call `activate_version()` separately once
    the caller is ready to make it the active dataset - kept as two
    steps so a caller can create the version, confirm the import
    actually succeeded, and only then flip it active.
    """
    base_dir = Path(base_dir)
    version_name = version_name or next_version_name()
    archive_path = archive_source_csvs(base_dir, version_name)
    checksum = compute_checksum(base_dir)

    return DatasetVersion.objects.create(
        version_name=version_name,
        source=str(archive_path),
        description=description,
        imported_by=user,
        checksum=checksum,
        statistics=statistics,
    )


def activate_version(version):
    """Makes `version` the sole active `DatasetVersion`, atomically -
    the partial `UniqueConstraint` on the model is the real guarantee;
    this just does the two-step "deactivate everything else, activate
    this one" safely in one transaction.
    """
    with transaction.atomic():
        DatasetVersion.objects.filter(is_active=True).exclude(pk=version.pk).update(is_active=False)
        version.is_active = True
        version.save(update_fields=["is_active"])
    return version


def get_active_version():
    return DatasetVersion.objects.filter(is_active=True).first()


def get_previous_version(current=None):
    """The `DatasetVersion` imported immediately before `current` (or
    before the currently active one, if not given) - the rollback
    target when no explicit version is named."""
    current = current if current is not None else get_active_version()
    qs = DatasetVersion.objects.all()
    if current is not None:
        qs = qs.exclude(pk=current.pk).filter(imported_at__lt=current.imported_at)
    return qs.order_by("-imported_at").first()
