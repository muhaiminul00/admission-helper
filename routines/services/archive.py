"""Routine Archive (Milestone 14, Phase 1).

Filesystem-backed archive of routine PDFs living directly in
media/routines/ - no database table, no upload interface. Discovery
is entirely filename-driven (`YYYY-MM.pdf`), so copying a new PDF into
the folder is the only "upload" step this app supports; the newest
filename automatically becomes the "current" routine.

Isolated here, not in the view, so a future storage backend (S3,
cloud storage, etc.) only requires replacing this module - the view
never touches the filesystem directly (Service-First Rule).
"""

import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})\.pdf$")


@dataclass(frozen=True)
class RoutineEntry:
    filename: str
    label: str


def _archive_dir() -> Path:
    return Path(settings.MEDIA_ROOT) / "routines"


def list_routines():
    """Every valid routine PDF in the archive folder, newest first.
    Non-PDF and non-conforming files are silently ignored (Phase 1:
    "Ignore every non-PDF file"). One `iterdir()` scan per call - the
    view calls this once per request, never in a loop (Performance:
    "avoid repeated filesystem scans during a single request")."""
    archive_dir = _archive_dir()
    if not archive_dir.is_dir():
        return []
    entries = []
    for path in archive_dir.iterdir():
        if not path.is_file():
            continue
        match = FILENAME_RE.match(path.name)
        if not match:
            continue
        entries.append(RoutineEntry(filename=path.name, label=f"{match.group(1)}-{match.group(2)}"))
    entries.sort(key=lambda entry: entry.label, reverse=True)
    return entries


def get_latest_routine():
    """The newest routine by filename, or None if the archive is
    empty - "Newest PDF becomes Current Routine"."""
    entries = list_routines()
    return entries[0] if entries else None


def resolve_routine_file(filename):
    """The absolute Path for `filename`, but only if it is a valid,
    existing routine PDF - otherwise None. Path traversal is rejected
    by construction: `filename` must fully match the strict
    `YYYY-MM.pdf` pattern before it is ever joined onto the archive
    directory, so no path separator, `..`, or absolute path can reach
    the filesystem lookup."""
    if not FILENAME_RE.match(filename):
        return None
    path = _archive_dir() / filename
    if not path.is_file():
        return None
    return path
