"""Revision workflow: Lecture -> Progress -> Revision Queue -> Revision
History -> Exam Ready (Milestone 9).

Deterministic scheduling only - no AI, no randomness. Every due date is
computed from fixed, centralized interval constants (`REVISION_INTERVALS`)
so the whole schedule for a lecture is reproducible from its completion
date alone. This module owns every revision-specific calculation
(schedule creation, due-date math, exam-readiness, queue fetching,
completion, dashboard/analytics numbers) - views stay thin and call
into it, exactly like `analytics.py`/`dashboard.py` before it.

Explicitly out of scope for this milestone (see PROJECT_PROGRESS.md):
no notifications/reminders, no background jobs - schedules are created
synchronously, inline, the moment a lecture becomes fully completed.
"""

from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone

from lectures.models import LectureTopic
from routines.models import Lecture

from .dashboard import COMPLETED_TOPIC_FILTER
from ..models import Progress, RevisionHistory, RevisionSchedule

Level = RevisionSchedule.Level
Status = RevisionSchedule.Status

# Centralized, deterministic scheduling intervals (Milestone 9 spec):
# Level 1 due `FIRST` after the lecture's completion date; Level 2 due
# `SECOND` after Level 1's due date; Level 3 due `FINAL` after Level 2's
# due date. Change these to retune the whole app's revision cadence.
REVISION_INTERVALS = {
    Level.FIRST: timedelta(days=1),
    Level.SECOND: timedelta(days=3),
    Level.FINAL: timedelta(days=7),
}

ALL_LEVELS = (Level.FIRST, Level.SECOND, Level.FINAL)


def _calculate_due_dates(completion_date):
    """{level: due_date} for all three revision stages, computed
    cumulatively from `completion_date` per `REVISION_INTERVALS`."""
    due_dates = {}
    cursor = completion_date
    for level in ALL_LEVELS:
        cursor = cursor + REVISION_INTERVALS[level]
        due_dates[level] = cursor
    return due_dates


def is_lecture_completed(user, lecture):
    """A lecture is "completed" only when it has at least one topic and
    every one of its topics is fully completed by `user`. Two small
    queries, scoped to a single lecture - not a table scan."""
    total = LectureTopic.objects.filter(lecture=lecture).count()
    if total == 0:
        return False
    completed = Progress.objects.filter(
        user=user, lecture_topic__lecture=lecture, **COMPLETED_TOPIC_FILTER
    ).count()
    return completed == total


def ensure_revision_schedule(user, lecture, completion_date=None):
    """Create all three revision stages for (user, lecture) if the
    lecture is fully completed and no schedule already exists for it.

    Returns True if a schedule was created, False otherwise (lecture
    not yet fully completed, or a schedule already exists - including
    the race where a concurrent request created it first, caught via
    the (user, lecture, revision_level) UniqueConstraint rather than a
    second existence check after the fact).
    """
    if not is_lecture_completed(user, lecture):
        return False
    if RevisionSchedule.objects.filter(user=user, lecture=lecture).exists():
        return False

    completion_date = completion_date or timezone.localdate()
    due_dates = _calculate_due_dates(completion_date)
    try:
        with transaction.atomic():
            RevisionSchedule.objects.bulk_create(
                [
                    RevisionSchedule(user=user, lecture=lecture, revision_level=level, due_date=due)
                    for level, due in due_dates.items()
                ]
            )
    except IntegrityError:
        return False
    return True


def get_exam_ready_lecture_codes(user):
    """Lecture codes that are fully "Exam Ready" for `user`: the lecture
    itself is complete AND all three revision levels are completed.

    Since a `RevisionSchedule` row only exists once a lecture is fully
    completed (see `ensure_revision_schedule()`), "all 3 distinct
    revision levels completed" already implies lecture completion -
    one annotated query, then one small lookup to resolve ids to codes.
    """
    ready_lecture_ids = (
        RevisionSchedule.objects.filter(user=user, status=Status.COMPLETED)
        .values("lecture_id")
        .annotate(completed_levels=Count("revision_level", distinct=True))
        .filter(completed_levels=len(ALL_LEVELS))
        .values_list("lecture_id", flat=True)
    )
    return set(
        Lecture.objects.filter(id__in=ready_lecture_ids).values_list("lecture_code", flat=True)
    )


def is_lecture_exam_ready(user, lecture):
    """Single-lecture exam-ready check, for the Lecture Detail page."""
    if not is_lecture_completed(user, lecture):
        return False
    completed_levels = set(
        RevisionSchedule.objects.filter(
            user=user, lecture=lecture, status=Status.COMPLETED
        ).values_list("revision_level", flat=True)
    )
    return completed_levels == set(ALL_LEVELS)


# ---------------------------------------------------------------------
# Revision Queue
# ---------------------------------------------------------------------

def get_revision_queue(user, subject_code=None, status=None, level=None):
    """All of `user`'s revision schedules, filtered and bucketed into
    Due Today / Overdue / Upcoming / Completed - one query regardless
    of how many revisions exist."""
    today = timezone.localdate()

    qs = RevisionSchedule.objects.filter(user=user).select_related("lecture", "lecture__subject")
    if subject_code:
        qs = qs.filter(lecture__subject__code=subject_code)
    if level:
        qs = qs.filter(revision_level=level)
    if status:
        qs = qs.filter(status=status)

    rows = list(qs)

    due_today, overdue, upcoming, completed = [], [], [], []
    for row in rows:
        if row.status == Status.COMPLETED:
            completed.append(row)
        elif row.due_date < today:
            overdue.append(row)
        elif row.due_date == today:
            due_today.append(row)
        else:
            upcoming.append(row)

    completed.sort(key=lambda r: r.completed_at or timezone.now(), reverse=True)

    return {
        "due_today": due_today,
        "overdue": overdue,
        "upcoming": upcoming,
        "completed": completed,
        "all": rows,
    }


def complete_revision(user, schedule_id, notes=""):
    """Mark one of `user`'s own revision schedules complete - a
    one-way action (see `RevisionHistory`'s docstring): completing an
    already-completed schedule is a no-op, not an error and not a
    second history entry.

    Returns the `RevisionSchedule`, or `None` if no such schedule
    exists for this user (never another user's - `user=user` is part
    of the lookup, not applied after the fact).
    """
    try:
        schedule = RevisionSchedule.objects.get(pk=schedule_id, user=user)
    except RevisionSchedule.DoesNotExist:
        return None

    if schedule.status == Status.COMPLETED:
        return schedule

    now = timezone.now()
    schedule.status = Status.COMPLETED
    schedule.completed_at = now
    schedule.save()
    RevisionHistory.objects.create(revision_schedule=schedule, completed_at=now, notes=notes)
    return schedule


# ---------------------------------------------------------------------
# Dashboard statistics
# ---------------------------------------------------------------------

def get_revision_dashboard_stats(user):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)

    qs = RevisionSchedule.objects.filter(user=user)
    total = qs.count()
    completed_total = qs.filter(status=Status.COMPLETED).count()
    due_today = qs.filter(status=Status.PENDING, due_date=today).count()
    overdue = qs.filter(status=Status.PENDING, due_date__lt=today).count()
    upcoming = qs.filter(status=Status.PENDING, due_date__gt=today).count()
    completed_this_week = qs.filter(
        status=Status.COMPLETED, completed_at__date__gte=week_ago
    ).count()
    exam_ready_count = len(get_exam_ready_lecture_codes(user))
    completion_percentage = round(completed_total / total * 100, 1) if total else 0.0

    return {
        "revision_due_today": due_today,
        "revision_overdue": overdue,
        "revision_upcoming": upcoming,
        "revision_completed_this_week": completed_this_week,
        "revision_completion_percentage": completion_percentage,
        "exam_ready_count": exam_ready_count,
    }


# ---------------------------------------------------------------------
# Analytics extras (surfaced on the Insights page - see
# progress/services/advanced_analytics.py: get_exam_insights(), which
# calls get_exam_ready_lecture_codes() above to annotate exam rows)
# ---------------------------------------------------------------------

def get_revision_completion_percentage(user):
    qs = RevisionSchedule.objects.filter(user=user)
    total = qs.count()
    if not total:
        return 0.0
    completed = qs.filter(status=Status.COMPLETED).count()
    return round(completed / total * 100, 1)


def get_overdue_revision_count(user):
    today = timezone.localdate()
    return RevisionSchedule.objects.filter(
        user=user, status=Status.PENDING, due_date__lt=today
    ).count()


def get_revision_workload(user):
    """Total pending (not-yet-completed) revisions for `user`."""
    return RevisionSchedule.objects.filter(user=user, status=Status.PENDING).count()


def get_upcoming_revision_load(user, days=7):
    """Pending revisions due within the next `days` days (inclusive of
    today, exclusive of already-overdue ones)."""
    today = timezone.localdate()
    horizon = today + timedelta(days=days)
    return RevisionSchedule.objects.filter(
        user=user, status=Status.PENDING, due_date__gte=today, due_date__lte=horizon
    ).count()


def get_exam_ready_count(user):
    return len(get_exam_ready_lecture_codes(user))


def get_pending_revision_counts(user, lecture_ids):
    """Bulk lecture_id -> pending revision count for `user` (Milestone
    10.5: Routine Timeline cards show revision status without a query
    per card)."""
    counts = (
        RevisionSchedule.objects.filter(user=user, lecture_id__in=lecture_ids, status=Status.PENDING)
        .values("lecture_id")
        .annotate(pending=Count("id"))
    )
    return {row["lecture_id"]: row["pending"] for row in counts}


def get_average_revision_delay(user):
    """Average (completed_at date - due_date) in days across all of
    `user`'s completed revisions - positive means completed late on
    average, negative means early, 0.0 if nothing completed yet."""
    completed = RevisionSchedule.objects.filter(
        user=user, status=Status.COMPLETED, completed_at__isnull=False
    ).values_list("due_date", "completed_at")
    if not completed:
        return 0.0
    delays = [(completed_at.date() - due_date).days for due_date, completed_at in completed]
    return round(sum(delays) / len(delays), 1)


def get_revision_streak(user):
    """Current/longest consecutive-day streaks of completing at least
    one revision, from distinct `RevisionHistory.completed_at` dates -
    the revision-workflow counterpart to
    `advanced_analytics.get_study_streak()` (which tracks topic
    completions, a different event stream)."""
    dates = sorted(
        set(
            RevisionHistory.objects.filter(revision_schedule__user=user).values_list(
                "completed_at__date", flat=True
            )
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
        current_streak = 0
    else:
        current_streak = 1
        for prev, curr in zip(reversed(dates[:-1]), reversed(dates[1:])):
            if (curr - prev).days == 1:
                current_streak += 1
            else:
                break

    return {"current_streak": current_streak, "longest_streak": longest}
