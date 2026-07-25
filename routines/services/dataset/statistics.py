"""Post-import dataset statistics (Milestone 10).

Stored on `DatasetVersion.statistics` right after a successful import,
so "how big was this dataset" never needs re-querying the (possibly
since-changed) database to answer for a past version.
"""

from pathlib import Path

from lectures.models import LectureTopic
from routines.models import Exam, Lecture
from subjects.models import Chapter, Subject

from ..csv.utils import read_csv_rows


def collect_statistics(base_dir):
    """Current DB counts for the five imported models, plus a raw
    `routine.csv` row count (`routine_event_count`) - the only one of
    these six numbers with no persisted model of its own (only `CLASS`
    rows become `Lecture` rows - see PROJECT_PROGRESS.md, Milestone 3),
    so it's read directly from the CSV via the importer's own
    `read_csv_rows()` rather than a second parser.
    """
    base_dir = Path(base_dir)
    _, routine_rows = read_csv_rows(base_dir / "routine.csv")
    return {
        "subject_count": Subject.objects.count(),
        "chapter_count": Chapter.objects.count(),
        "lecture_count": Lecture.objects.count(),
        "lecture_topic_count": LectureTopic.objects.count(),
        "exam_count": Exam.objects.count(),
        "routine_event_count": len(routine_rows),
    }
