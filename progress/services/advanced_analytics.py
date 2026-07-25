""""Study advisor" insights layered on top of `analytics.py`'s basic
completion metrics (Milestone 8).

`analytics.py`/`dashboard.py` answer "how much have I completed?" -
this module answers "what should I study next?", "which subjects/
chapters/lectures need attention?", and "am I actually ready for the
next exam?". Nothing here is stored: every function recomputes from
`Progress`/`Chapter`/`Lecture`/`Exam` on demand, scoped to a single
`user`, exactly like the rest of the service layer.

This module is analytics-only, per this milestone's explicit scope: it
never schedules revisions or writes to any model (see Milestone 9 for
scheduling).
"""

from datetime import timedelta

from django.db.models import Count, F, Max, Q, Sum
from django.db.models.functions import ExtractWeekDay, TruncDate, TruncMonth
from django.utils import timezone

from lectures.models import LectureTopic
from routines.models import Exam, Lecture
from subjects.models import Chapter, Subject

from . import revision as revision_service
from .analytics import (
    READINESS_BADGE_CLASSES,
    READINESS_LABELS,
    _percentage,
    completed_case,
    get_chapter_analytics,
    get_lecture_analytics,
    get_lecture_completion_stats,
    get_subject_analytics,
    readiness_label,
)
from ..models import Progress

COMPLETED_TOPIC_FILTER = dict(
    class_done=True, notes_done=True, revision_done=True, practice_done=True
)

WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


# ---------------------------------------------------------------------
# Subject insights
# ---------------------------------------------------------------------

def get_subject_insights(user):
    """Strongest/weakest subject (ties broken by completed, then total
    topic count) plus a full ranked list, for `user`. One query
    (delegates to `get_subject_analytics`, already a single annotated
    query)."""
    rows = get_subject_analytics(user, sort="name")
    ranked = sorted(rows, key=lambda r: (-r["percentage"], -r["completed"], -r["total"]))
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i

    with_topics = [r for r in ranked if r["total"] > 0]
    return {
        "strongest": with_topics[0] if with_topics else None,
        "weakest": with_topics[-1] if with_topics else None,
        "ranking": ranked,
    }


def get_subject_completion_trend(user):
    """Per-subject topics completed today / last 7 days / last 30 days.

    Three `Sum(completed_case(..., since=X))` annotations computed in
    one query, rather than three separate queries per window.
    """
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)

    subjects = Subject.objects.annotate(
        today_count=Sum(completed_case(user, "lectures__topics__", since=today)),
        week_count=Sum(completed_case(user, "lectures__topics__", since=week_ago)),
        month_count=Sum(completed_case(user, "lectures__topics__", since=month_ago)),
    )
    return [
        {
            "subject": s,
            "today": s.today_count or 0,
            "last_7_days": s.week_count or 0,
            "last_30_days": s.month_count or 0,
        }
        for s in subjects
    ]


def get_average_completion_speed(user):
    """Average topics fully completed per active study day, for `user`.

    "Active day" = a calendar date on which at least one topic was
    completed - a user who studies in bursts isn't penalized for the
    days they didn't study at all. Two small queries (a count and a
    distinct-dates count over the user's own completed `Progress` rows
    only - bounded by that user's activity, not overall dataset size).
    """
    completed_qs = Progress.objects.filter(user=user, **COMPLETED_TOPIC_FILTER)
    total_completed = completed_qs.count()
    active_days = completed_qs.values("updated_at__date").distinct().count()
    if active_days == 0:
        return 0.0
    return round(total_completed / active_days, 2)


# ---------------------------------------------------------------------
# Chapter insights
# ---------------------------------------------------------------------

def get_priority_chapters(user, limit=10, rows=None):
    """Chapters ranked highest-priority-first: unfinished topics that
    also appear in an upcoming exam's coverage rank above equally-sized
    backlogs that don't. Three queries total (chapter stats, upcoming
    exams' covered codes, chapter ids reachable from those codes) -
    fixed regardless of how many chapters/exams exist. Pass `rows=`
    (already-fetched `get_chapter_analytics()` output) to skip the
    first query when a caller (e.g. the Insights page) already has it,
    avoiding a redundant re-fetch.
    """
    today = timezone.localdate()
    rows = get_chapter_analytics(user) if rows is None else list(rows)  # 1 query (or 0, if reused)

    upcoming_codes = set()
    for codes in Exam.objects.filter(exam_date__gte=today).values_list(
        "covered_lectures", flat=True
    ):  # 1 query
        upcoming_codes.update(codes)

    upcoming_chapter_ids = set(
        LectureTopic.objects.filter(
            lecture__lecture_code__in=upcoming_codes, chapter__isnull=False
        ).values_list("chapter_id", flat=True).distinct()
    )  # 1 query

    EXAM_COVERAGE_WEIGHT = 5
    for row in rows:
        in_upcoming_exam = row["chapter"].id in upcoming_chapter_ids
        row["in_upcoming_exam"] = in_upcoming_exam
        row["priority_score"] = row["remaining"] + (EXAM_COVERAGE_WEIGHT if in_upcoming_exam else 0)

    rows = [r for r in rows if r["remaining"] > 0]
    rows.sort(key=lambda r: (-r["priority_score"], -r["remaining"]))
    return rows[:limit]


def get_neglected_chapters(user, stale_days=14, limit=10):
    """Chapters with unfinished topics AND no activity (of any kind,
    not just completions) in the last `stale_days` - one annotated
    query (a filtered `Max()` for last-activity alongside the usual
    total/completed `Count`/`Sum`)."""
    cutoff = timezone.now() - timedelta(days=stale_days)

    chapters = Chapter.objects.select_related("subject").annotate(
        total_topics=Count("lecture_topics", distinct=True),
        completed_topics=Sum(completed_case(user, "lecture_topics__")),
        last_activity=Max(
            "lecture_topics__progress_records__updated_at",
            filter=Q(lecture_topics__progress_records__user=user),
        ),
    )

    rows = []
    for chapter in chapters:
        total = chapter.total_topics
        completed = chapter.completed_topics or 0
        remaining = total - completed
        if remaining <= 0:
            continue
        if chapter.last_activity is not None and chapter.last_activity >= cutoff:
            continue  # recently touched - not neglected
        rows.append(
            {
                "chapter": chapter,
                "total": total,
                "completed": completed,
                "remaining": remaining,
                "percentage": _percentage(completed, total),
                "last_activity": chapter.last_activity,
            }
        )

    rows.sort(key=lambda r: -r["remaining"])
    return rows[:limit]


def get_most_unfinished_chapters(user, limit=10, rows=None):
    rows = get_chapter_analytics(user) if rows is None else rows
    rows = [r for r in rows if r["remaining"] > 0]
    rows.sort(key=lambda r: -r["remaining"])
    return rows[:limit]


def get_most_completed_chapters(user, limit=10, rows=None):
    rows = get_chapter_analytics(user) if rows is None else rows
    rows = [r for r in rows if r["total"] > 0]
    rows.sort(key=lambda r: -r["percentage"])
    return rows[:limit]


# ---------------------------------------------------------------------
# Lecture insights
# ---------------------------------------------------------------------

def get_longest_untouched_lectures(user, limit=10, rows=None):
    """Lectures with zero completed topics, oldest-scheduled first (the
    class that happened longest ago with nothing done is most
    concerning). Undated lectures (self-study/gap - see Milestone 4.1)
    have no time reference for "how long", so they sort after every
    dated one rather than being conflated with a real overdue class.
    Pass `rows=` (already-fetched `get_lecture_analytics()` output) to
    avoid a redundant re-fetch."""
    rows = get_lecture_analytics(user) if rows is None else rows
    rows = [r for r in rows if r["total"] > 0 and r["completed"] == 0]
    rows.sort(
        key=lambda r: (
            r["lecture"].lecture_date is None,
            r["lecture"].lecture_date or timezone.localdate(),
        )
    )
    return rows[:limit]


def get_recently_completed_lectures(user, limit=10):
    """Fully-completed lectures, most recently finished first. One
    annotated query: `last_completed_at` is a `Max()` filtered to this
    user's fully-completed `Progress` rows for that lecture's topics."""
    lectures = (
        Lecture.objects.select_related("subject")
        .annotate(
            total_topics=Count("topics", distinct=True),
            completed_topics=Sum(completed_case(user, "topics__")),
            last_completed_at=Max(
                "topics__progress_records__updated_at",
                filter=Q(topics__progress_records__user=user, **{
                    f"topics__progress_records__{k}": v
                    for k, v in COMPLETED_TOPIC_FILTER.items()
                }),
            ),
        )
        .filter(total_topics__gt=0, completed_topics=F("total_topics"))
        .order_by("-last_completed_at")[:limit]
    )
    return [
        {
            "lecture": lecture,
            "total": lecture.total_topics,
            "completed": lecture.completed_topics,
            "completed_at": lecture.last_completed_at,
        }
        for lecture in lectures
    ]


def get_backlog_lectures(user, limit=10, rows=None):
    """Lectures with the largest unfinished-topic backlog, regardless
    of recency (contrast with `get_longest_untouched_lectures()`, which
    is about dormancy/time, not volume)."""
    rows = get_lecture_analytics(user) if rows is None else rows
    rows = [r for r in rows if r["remaining"] > 0]
    rows.sort(key=lambda r: -r["remaining"])
    return rows[:limit]


def get_study_streak(user):
    """Current and longest consecutive-day study streaks for `user`,
    based on distinct calendar dates with at least one fully-completed
    topic. One query - the distinct-date list is bounded by how many
    days the user has ever studied, never by total topic/dataset size.
    """
    dates = sorted(
        set(
            Progress.objects.filter(user=user, **COMPLETED_TOPIC_FILTER)
            .values_list("updated_at__date", flat=True)
        )
    )
    if not dates:
        return {"current_streak": 0, "longest_streak": 0}

    longest = current_run = 1
    for prev, curr in zip(dates, dates[1:]):
        if (curr - prev).days == 1:
            current_run += 1
        else:
            current_run = 1
        longest = max(longest, current_run)

    today = timezone.localdate()
    if dates[-1] not in (today, today - timedelta(days=1)):
        current_streak = 0  # streak broken - last activity wasn't today or yesterday
    else:
        current_streak = 1
        for prev, curr in zip(reversed(dates[:-1]), reversed(dates[1:])):
            if (curr - prev).days == 1:
                current_streak += 1
            else:
                break

    return {"current_streak": current_streak, "longest_streak": longest}


# ---------------------------------------------------------------------
# Trend / visualization data sources (CSS-only rendering, no JS charts)
# ---------------------------------------------------------------------

def get_daily_completion_trend(user, days=35):
    """Topics completed per day for the last `days` days, zero-filled
    for days with no activity - the data source for the calendar
    heatmap. One query."""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)

    counts = {
        row["day"]: row["count"]
        for row in (
            Progress.objects.filter(user=user, updated_at__date__gte=start, **COMPLETED_TOPIC_FILTER)
            .annotate(day=TruncDate("updated_at"))
            .values("day")
            .annotate(count=Count("id"))
        )
    }
    return [
        {"date": start + timedelta(days=i), "count": counts.get(start + timedelta(days=i), 0)}
        for i in range(days)
    ]


def get_weekly_distribution(user, days=90):
    """Topics completed per weekday (Sunday..Saturday) over the last
    `days` days - one query using `ExtractWeekDay`."""
    start = timezone.localdate() - timedelta(days=days - 1)
    counts = {
        row["weekday"]: row["count"]
        for row in (
            Progress.objects.filter(user=user, updated_at__date__gte=start, **COMPLETED_TOPIC_FILTER)
            .annotate(weekday=ExtractWeekDay("updated_at"))
            .values("weekday")
            .annotate(count=Count("id"))
        )
    }
    # Django's ExtractWeekDay: Sunday=1 .. Saturday=7.
    return [
        {"weekday": WEEKDAY_NAMES[i], "count": counts.get(i + 1, 0)}
        for i in range(7)
    ]


def _first_of_month(d):
    return d.replace(day=1)


def _add_month(d):
    return d.replace(year=d.year + 1, month=1) if d.month == 12 else d.replace(month=d.month + 1)


def get_monthly_completion_timeline(user, months=6):
    """Topics completed per calendar month for the last `months`
    months (oldest first) - one query using `TruncMonth`."""
    this_month = _first_of_month(timezone.localdate())
    start = this_month
    for _ in range(months - 1):
        start = _first_of_month(start - timedelta(days=1))

    counts = {}
    for row in (
        Progress.objects.filter(user=user, updated_at__date__gte=start, **COMPLETED_TOPIC_FILTER)
        .annotate(month=TruncMonth("updated_at"))
        .values("month")
        .annotate(count=Count("id"))
    ):
        month_dt = row["month"]
        counts[(month_dt.year, month_dt.month)] = row["count"]

    result = []
    cursor = start
    for _ in range(months):
        result.append({"month": cursor, "count": counts.get((cursor.year, cursor.month), 0)})
        cursor = _add_month(cursor)
    return result


# ---------------------------------------------------------------------
# Exam insights (extends analytics.py's get_exam_readiness())
# ---------------------------------------------------------------------

def get_exam_insights(user):
    """Extended exam readiness: adds a blended readiness score (topic
    completion + lecture completion), a coverage gap, remaining
    workload, and a confidence label - on top of the same fields
    `get_exam_readiness()` already returns. Reuses
    `get_lecture_completion_stats()` (the same helper `analytics.py`'s
    `get_exam_readiness()` uses) for a single bulk lookup rather than
    querying per exam.
    """
    exams = list(Exam.objects.all())

    all_codes = set()
    for exam in exams:
        all_codes.update(exam.covered_lectures)
    stats_by_code = get_lecture_completion_stats(user, all_codes)
    exam_ready_codes = revision_service.get_exam_ready_lecture_codes(user)

    rows = []
    for exam in exams:
        total_topics = completed_topics = 0
        covered_lecture_count = completed_lecture_count = exam_ready_lecture_count = 0
        for code in exam.covered_lectures:
            stat = stats_by_code.get(code)
            if stat is None:
                continue
            covered_lecture_count += 1
            lt = stat["total_topics"] or 0
            lc = stat["completed_topics"] or 0
            total_topics += lt
            completed_topics += lc
            if lt > 0 and lc == lt:
                completed_lecture_count += 1
            if code in exam_ready_codes:
                exam_ready_lecture_count += 1

        topic_pct = _percentage(completed_topics, total_topics)
        lecture_pct = _percentage(completed_lecture_count, covered_lecture_count)
        readiness_score = round(0.6 * topic_pct + 0.4 * lecture_pct, 1)
        label = readiness_label(readiness_score)

        rows.append(
            {
                "exam": exam,
                "covered_lecture_count": covered_lecture_count,
                "completed_lecture_count": completed_lecture_count,
                "exam_ready_lecture_count": exam_ready_lecture_count,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "remaining_topics": total_topics - completed_topics,
                "topic_completion_percentage": topic_pct,
                "lecture_completion_percentage": lecture_pct,
                "readiness_score": readiness_score,
                "missing_percentage": round(100 - topic_pct, 1),
                "confidence_label": READINESS_LABELS[label],
                "confidence_badge_class": READINESS_BADGE_CLASSES[label],
            }
        )

    rows.sort(key=lambda r: r["exam"].exam_date)
    return rows


def get_next_exam_insight(user):
    """The single nearest upcoming exam's insight row, for the
    dashboard's "Ready For Exam" widget - `None` if no exam is
    upcoming."""
    today = timezone.localdate()
    upcoming = [r for r in get_exam_insights(user) if r["exam"].exam_date >= today]
    return upcoming[0] if upcoming else None


# ---------------------------------------------------------------------
# Dashboard widgets (additive - see progress/services/dashboard.py for
# the pre-existing basic widgets, unchanged by this milestone)
# ---------------------------------------------------------------------

def get_advanced_dashboard_widgets(user):
    subject_insights = get_subject_insights(user)
    priority_chapters = get_priority_chapters(user, limit=1)
    untouched_lectures = get_longest_untouched_lectures(user, limit=1)

    return {
        "strongest_subject": subject_insights["strongest"],
        "weakest_subject": subject_insights["weakest"],
        "priority_chapter": priority_chapters[0] if priority_chapters else None,
        "longest_untouched_lecture": untouched_lectures[0] if untouched_lectures else None,
        "study_streak": get_study_streak(user),
        "ready_for_exam": get_next_exam_insight(user),
    }
