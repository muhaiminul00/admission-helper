"""The Progress Service (Milestone 15.2, Parts 2-4) - the single
source of truth for multi-dimensional progress display.

Every study activity (`class_done`/`notes_done`/`revision_done`/
`practice_done`) counts independently and equally (25% each) instead
of requiring all four before any credit shows - a topic with just
`class_done=True` is 25% done here, not 0%. This is a **display/
aggregation concern only**. It does not change, and must never be used
to change, when a lecture counts as "complete" for revision-scheduling
purposes - `progress.services.revision.is_lecture_completed()` (and
therefore `ensure_revision_schedule()`) keeps using its own strict
all-four-required definition via `dashboard.COMPLETED_TOPIC_FILTER`,
completely independent of this module. The two are different
questions ("how much progress has been made so far, dimension by
dimension?" vs. "is this lecture fully done, so a revision schedule
should exist?") that happened to share one formula before; this
module deliberately does not touch that formula or anything built on
it (`analytics.py`, `dashboard.py`, `revision.py` are all unchanged).

Every scope (topic/chapter/lecture/subject/exam/overall) aggregates
from the same four `Progress` boolean columns, always in one query per
scope - and every *bulk* variant (`get_bulk_*`) answers "progress for
many X at once" in one query total, never one query per row, so list
pages (Subject/Chapter/Lecture Analytics) stay N+1-free (Part 17).
"""

from django.db.models import Case, Count, IntegerField, Sum, When

from lectures.models import LectureTopic
from routines.models import Lecture
from subjects.models import Subject

from ..models import Progress

DIMENSIONS = ("class_done", "notes_done", "revision_done", "practice_done")

# Fixed, permanent colors per Part 2's table - literal Tailwind class
# strings (not built at render time) so Tailwind's build-time scanner
# picks them up; see templates/components/progress_meter.html.
DIMENSION_META = {
    "class_done": {"label": "Class", "color_class": "bg-blue-500", "dark_color_class": "dark:bg-blue-500"},
    "notes_done": {"label": "Notes", "color_class": "bg-emerald-500", "dark_color_class": "dark:bg-emerald-500"},
    "revision_done": {"label": "Revision", "color_class": "bg-amber-400", "dark_color_class": "dark:bg-amber-400"},
    "practice_done": {"label": "Practice", "color_class": "bg-purple-500", "dark_color_class": "dark:bg-purple-500"},
}

EMPTY_SEGMENT_CLASS = "bg-gray-200 dark:bg-slate-700"


def _dimension_sum(user, dim, join_prefix=""):
    """A `Sum(Case(When(...)))` counting how many rows under
    `join_prefix` have `dim=True` for `user` - the same join-prefix
    aggregation technique `analytics.completed_case()` already uses,
    applied per-dimension instead of requiring all four at once."""
    def field(name):
        return f"{join_prefix}progress_records__{name}"

    return Sum(
        Case(
            When(**{field("user"): user, field(dim): True}, then=1),
            default=0, output_field=IntegerField(),
        )
    )


def _build_result(topic_count, dim_counts):
    total_units = topic_count * 4
    completed_units = sum(dim_counts.values())
    dimensions = {}
    segments = []
    for dim in DIMENSIONS:
        completed = dim_counts.get(dim) or 0
        meta = DIMENSION_META[dim]
        dimensions[dim] = {
            "label": meta["label"],
            "color_class": meta["color_class"],
            "dark_color_class": meta["dark_color_class"],
            "completed": completed,
            "total": topic_count,
            "percentage": round(completed / topic_count * 100, 1) if topic_count else 0.0,
        }
        segments.append(
            {
                "label": meta["label"], "color_class": meta["color_class"],
                "count": completed, "total": topic_count,
                "percentage": dimensions[dim]["percentage"],
            }
        )
    return {
        "topic_count": topic_count,
        "total_units": total_units,
        "completed_units": completed_units,
        "percentage": round(completed_units / total_units * 100, 1) if total_units else 0.0,
        "dimensions": dimensions,
        "segments": segments,
    }


def _empty_result():
    return _build_result(0, {})


def _aggregate_topics(user, topics_qs):
    result = topics_qs.aggregate(
        topic_count=Count("id", distinct=True),
        **{f"_{dim}": _dimension_sum(user, dim) for dim in DIMENSIONS},
    )
    topic_count = result["topic_count"] or 0
    dim_counts = {dim: result[f"_{dim}"] or 0 for dim in DIMENSIONS}
    return _build_result(topic_count, dim_counts)


# ---------------------------------------------------------------------
# Single-scope lookups (Topic -> Chapter -> Lecture -> Subject -> Exam
# -> overall/Dashboard) - one query each.
# ---------------------------------------------------------------------

def get_topic_progress(user, topic_id):
    row = Progress.objects.filter(user=user, lecture_topic_id=topic_id).values(*DIMENSIONS).first()
    dim_counts = {dim: (1 if row and row[dim] else 0) for dim in DIMENSIONS}
    return _build_result(1, dim_counts)


def get_chapter_progress(user, chapter_id):
    return _aggregate_topics(user, LectureTopic.objects.filter(chapter_id=chapter_id))


def get_lecture_progress(user, lecture_id):
    return _aggregate_topics(user, LectureTopic.objects.filter(lecture_id=lecture_id))


def get_subject_progress(user, subject_code):
    return _aggregate_topics(user, LectureTopic.objects.filter(lecture__subject__code=subject_code))


def get_overall_progress(user):
    """Dashboard/overall scope - every topic in the dataset."""
    return _aggregate_topics(user, LectureTopic.objects.all())


# ---------------------------------------------------------------------
# Bulk lookups - one query for many rows, never one query per row.
# ---------------------------------------------------------------------

def get_bulk_chapter_progress(user, chapters_qs):
    """{chapter_id: progress_dict} for every chapter in `chapters_qs`."""
    rows = chapters_qs.annotate(
        _topic_count=Count("lecture_topics", distinct=True),
        **{f"_{dim}": _dimension_sum(user, dim, "lecture_topics__") for dim in DIMENSIONS},
    ).values("id", "_topic_count", *[f"_{dim}" for dim in DIMENSIONS])
    return {
        row["id"]: _build_result(row["_topic_count"], {dim: row[f"_{dim}"] or 0 for dim in DIMENSIONS})
        for row in rows
    }


def get_bulk_lecture_progress(user, lectures_qs):
    """{lecture_id: progress_dict} for every lecture in `lectures_qs`."""
    rows = lectures_qs.annotate(
        _topic_count=Count("topics", distinct=True),
        **{f"_{dim}": _dimension_sum(user, dim, "topics__") for dim in DIMENSIONS},
    ).values("id", "_topic_count", *[f"_{dim}" for dim in DIMENSIONS])
    return {
        row["id"]: _build_result(row["_topic_count"], {dim: row[f"_{dim}"] or 0 for dim in DIMENSIONS})
        for row in rows
    }


def get_bulk_subject_progress(user, subjects_qs=None):
    """{subject_id: progress_dict} for every subject in `subjects_qs`
    (default: all subjects) - lecture->subject, not chapter->subject,
    matching `analytics.get_subject_analytics()`'s own reasoning (a
    subject with no chapter breakdown, e.g. self-study English/Bangla,
    is still counted correctly this way)."""
    rows = (subjects_qs or Subject.objects.all()).annotate(
        _topic_count=Count("lectures__topics", distinct=True),
        **{f"_{dim}": _dimension_sum(user, dim, "lectures__topics__") for dim in DIMENSIONS},
    ).values("id", "_topic_count", *[f"_{dim}" for dim in DIMENSIONS])
    return {
        row["id"]: _build_result(row["_topic_count"], {dim: row[f"_{dim}"] or 0 for dim in DIMENSIONS})
        for row in rows
    }


def get_bulk_lecture_progress_by_code(user, lecture_codes):
    """{lecture_code: progress_dict} for the given codes - the
    building block `get_bulk_exam_progress()` uses, since `Exam.
    covered_lectures` is a plain JSON list of codes, not a FK (see
    `routines/models.py`), mirroring `analytics.
    get_lecture_completion_stats()`'s own by-code bulk pattern."""
    rows = Lecture.objects.filter(lecture_code__in=lecture_codes).annotate(
        _topic_count=Count("topics", distinct=True),
        **{f"_{dim}": _dimension_sum(user, dim, "topics__") for dim in DIMENSIONS},
    ).values("lecture_code", "_topic_count", *[f"_{dim}" for dim in DIMENSIONS])
    return {
        row["lecture_code"]: _build_result(row["_topic_count"], {dim: row[f"_{dim}"] or 0 for dim in DIMENSIONS})
        for row in rows
    }


def get_bulk_exam_progress(user, exams):
    """{exam_id: progress_dict}, merging the per-dimension counts of
    every lecture an exam covers - one query for every exam's covered
    lectures combined (via `get_bulk_lecture_progress_by_code()`),
    regardless of how many exams are passed in."""
    all_codes = set()
    for exam in exams:
        all_codes.update(exam.covered_lectures)
    by_code = get_bulk_lecture_progress_by_code(user, all_codes)

    results = {}
    for exam in exams:
        topic_count = 0
        dim_counts = {dim: 0 for dim in DIMENSIONS}
        for code in exam.covered_lectures:
            row = by_code.get(code)
            if not row:
                continue
            topic_count += row["topic_count"]
            for dim in DIMENSIONS:
                dim_counts[dim] += row["dimensions"][dim]["completed"]
        results[exam.id] = _build_result(topic_count, dim_counts)
    return results


def get_exam_progress(user, exam):
    return get_bulk_exam_progress(user, [exam])[exam.id]
