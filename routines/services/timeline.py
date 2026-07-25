"""Timeline navigation for the Routine and Exam pages (Milestone 10.5).

Replaces page-based Previous/Next navigation with a window that always
opens around the user's current study position: "Past <- Today ->
Future". The window is **event-based, not calendar-day based** - it
always holds a fixed *count* of events on each side of the anchor
(`PREVIOUS_EVENTS`/`NEXT_EVENTS` below), never a fixed number of
calendar days. A date is never split across a window boundary: once a
date's first event is pulled in, every event on that date comes with
it - so "load more" always adds/removes whole days, and a day with
many lectures doesn't blow the window budget while three empty days
never consume any of it (empty calendar days simply never appear,
since the window is built by querying event rows directly, never by
iterating calendar dates).

This module owns anchor resolution, windowing, and week/date grouping
only. It never computes completion/readiness itself - the `attach_*()`
helpers below bulk-merge that from the existing, unmodified
`progress/services/analytics.py` and `progress/services/revision.py`
so a lecture/exam card's progress is never calculated twice.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import groupby

from django.db.models import Count, F, Sum
from django.urls import reverse
from django.utils import timezone

from progress.services.analytics import completed_case, get_exam_readiness, get_lecture_completion_stats

from ..models import Exam, Lecture

# Configurable window sizes (Milestone 10.5 spec: "configuration
# constants for easy future adjustment").
PREVIOUS_EVENTS = 5
NEXT_EVENTS = 10

# Per-direction, per-source fetch ceiling. A fixed constant, not
# derived from table size, so a window query never scans/loads the
# full dataset - generous enough that no realistic per-day event
# density truncates a date's events mid-day (a window only ever needs
# enough raw candidates to assemble PREVIOUS_EVENTS/NEXT_EVENTS worth
# of *whole* dates, and real per-day density here is small - a handful
# of lectures at most).
FETCH_CEILING = max(PREVIOUS_EVENTS, NEXT_EVENTS) * 4 + 10


@dataclass
class TimelineEvent:
    date: object
    type: str  # "CLASS" or "EXAM"
    title: str
    subject: object
    url: str
    code: str
    obj: object
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------
# Source querysets
# ---------------------------------------------------------------------

def _lecture_queryset(subject_code="", completed=None, user=None):
    """Dated Lectures only (undated "virtual" lectures - self-study
    subjects, the lecture-06 gap - have no calendar slot, same
    exclusion `routines/services/events.py` already applied).

    `completed`/`user` (Milestone 10.5's Routine Timeline
    Completed/Incomplete filter) reuse `analytics.completed_case()`
    rather than re-deriving "is this lecture fully done" - the exact
    aggregation `analytics.get_lecture_analytics()` already uses.
    """
    qs = Lecture.objects.filter(lecture_date__isnull=False).select_related("subject")
    if subject_code:
        qs = qs.filter(subject__code=subject_code)
    if completed is not None and user is not None:
        qs = qs.annotate(
            _total_topics=Count("topics", distinct=True),
            _completed_topics=Sum(completed_case(user, "topics__")),
        )
        if completed:
            qs = qs.filter(_total_topics__gt=0, _completed_topics=F("_total_topics"))
        else:
            qs = qs.exclude(_total_topics__gt=0, _completed_topics=F("_total_topics"))
    return qs


def _exam_ids_for_subject(subject_code):
    """Exam ids whose `covered_lectures` includes at least one lecture
    code for `subject_code`. `covered_lectures` is a plain JSON list of
    code strings (not a FK - see `routines/models.py: Exam`), so this
    can't be a DB-level lookup; done as one bulk, Python-side pass over
    every Exam (the exam table is small and structurally bounded - one
    prep-year's worth of exams, unlike Lecture which grows over time -
    so this stays cheap regardless of how long the app has been used).
    """
    matching = []
    for exam_id, covered in Exam.objects.values_list("id", "covered_lectures"):
        prefixes = {code.split("-")[0] for code in covered}
        if subject_code in prefixes:
            matching.append(exam_id)
    return matching


def _exam_queryset(subject_code=""):
    qs = Exam.objects.all()
    if subject_code:
        qs = qs.filter(id__in=_exam_ids_for_subject(subject_code))
    return qs


def _lecture_to_event(lecture):
    return TimelineEvent(
        date=lecture.lecture_date,
        type="CLASS",
        title=lecture.title or lecture.lecture_code,
        subject=lecture.subject,
        url=reverse("lecture-detail", args=[lecture.lecture_code]),
        code=lecture.lecture_code,
        obj=lecture,
    )


def _exam_to_event(exam):
    return TimelineEvent(
        date=exam.exam_date,
        type="EXAM",
        title=exam.exam_name,
        subject=None,
        url=reverse("exam-detail", args=[exam.pk]),
        code=exam.exam_code,
        obj=exam,
    )


# ---------------------------------------------------------------------
# Generic event-based windowing (works over one source's queryset +
# date field at a time - Lecture/lecture_date or Exam/exam_date)
# ---------------------------------------------------------------------

def _fetch_side(qs, date_field, descending, limit):
    # Milestone 12, Phase 2: `id` as an explicit tie-breaker makes
    # ordering deterministic when multiple rows share the same date -
    # without one, the DB is free to return same-date rows in any
    # order it likes (SQLite has no guaranteed default), which reads
    # as "sometimes recentering differently" even though nothing about
    # the underlying data changed. Same direction as the date field so
    # "closest to the anchor first" stays consistent within a tied day.
    id_order = "-id" if descending else "id"
    ordering = (f"-{date_field}", id_order) if descending else (date_field, id_order)
    rows = list(qs.order_by(*ordering)[:limit])
    exhausted = len(rows) < limit
    return rows, exhausted


def _select_whole_dates(rows_closest_first, date_field, target_n):
    """Walks whole date-groups outward from the anchor (closest first),
    stopping once at least `target_n` rows are selected - never
    stopping mid-date. Returns (selected_rows, fully_consumed)."""
    selected = []
    for _date, group in groupby(rows_closest_first, key=lambda r: getattr(r, date_field)):
        selected.extend(group)
        if len(selected) >= target_n:
            break
    fully_consumed = len(selected) == len(rows_closest_first)
    return selected, fully_consumed


def _windowed_query(qs, date_field, previous_n, next_n, before=None, after=None):
    """Builds one timeline window. With `before`/`after` unset, resolves
    the smart anchor (today's rows if any, else nearest upcoming, else
    nearest past) and centers on it - 2 queries total. `before`
    (strictly-older) or `after` (strictly-newer) instead extend the
    window past that date, for "load more" - 1 query.
    """
    today = timezone.localdate()

    if before is not None:
        rows, exhausted = _fetch_side(qs.filter(**{f"{date_field}__lt": before}), date_field, True, FETCH_CEILING)
        window, fully_consumed = _select_whole_dates(rows, date_field, previous_n)
        return {"rows": list(reversed(window)), "has_more_previous": (not fully_consumed) or (not exhausted)}

    if after is not None:
        rows, exhausted = _fetch_side(qs.filter(**{f"{date_field}__gt": after}), date_field, False, FETCH_CEILING)
        window, fully_consumed = _select_whole_dates(rows, date_field, next_n)
        return {"rows": window, "has_more_next": (not fully_consumed) or (not exhausted)}

    prev_rows, prev_exhausted = _fetch_side(
        qs.filter(**{f"{date_field}__lt": today}), date_field, True, FETCH_CEILING
    )
    next_rows, next_exhausted = _fetch_side(
        qs.filter(**{f"{date_field}__gte": today}), date_field, False, FETCH_CEILING
    )

    if any(getattr(r, date_field) == today for r in next_rows):
        anchor = today
    elif next_rows:
        anchor = getattr(next_rows[0], date_field)
    elif prev_rows:
        anchor = getattr(prev_rows[0], date_field)
    else:
        anchor = today  # nothing exists at all - nothing to center on anyway

    on_anchor = [r for r in next_rows if getattr(r, date_field) == anchor]
    on_anchor += [r for r in prev_rows if getattr(r, date_field) == anchor]
    strictly_next = [r for r in next_rows if getattr(r, date_field) > anchor]
    strictly_prev = [r for r in prev_rows if getattr(r, date_field) < anchor]

    prev_window, prev_fully_consumed = _select_whole_dates(strictly_prev, date_field, previous_n)
    next_window, next_fully_consumed = _select_whole_dates(strictly_next, date_field, next_n)

    return {
        "anchor": anchor,
        "today": today,
        "rows": list(reversed(prev_window)) + on_anchor + next_window,
        "has_more_previous": (not prev_fully_consumed) or (not prev_exhausted),
        "has_more_next": (not next_fully_consumed) or (not next_exhausted),
    }


# ---------------------------------------------------------------------
# Public timeline builders
# ---------------------------------------------------------------------

def get_lecture_timeline(
    subject_code="", completed=None, user=None,
    previous_n=PREVIOUS_EVENTS, next_n=NEXT_EVENTS, before=None, after=None,
):
    """Routine Timeline window: dated Lectures only (Milestone 10.5 -
    Exams get their own dedicated timeline, see `get_exam_timeline()`).
    """
    qs = _lecture_queryset(subject_code, completed=completed, user=user)
    result = _windowed_query(qs, "lecture_date", previous_n, next_n, before, after)
    result["events"] = [_lecture_to_event(r) for r in result.pop("rows")]
    return result


def get_exam_timeline(subject_code="", previous_n=PREVIOUS_EVENTS, next_n=NEXT_EVENTS, before=None, after=None):
    """Exam Timeline window - same windowing algorithm as the Routine
    Timeline, over `Exam`/`exam_date` instead of `Lecture`/`lecture_date`.
    """
    qs = _exam_queryset(subject_code)
    result = _windowed_query(qs, "exam_date", previous_n, next_n, before, after)
    result["events"] = [_exam_to_event(r) for r in result.pop("rows")]
    return result


# ---------------------------------------------------------------------
# Progress/readiness integration (bulk - never one query per card)
# ---------------------------------------------------------------------

def attach_lecture_progress(events, user):
    """Bulk-attach completion stats to CLASS events' `.extra`, reusing
    `analytics.get_lecture_completion_stats()` - one query for the
    whole window, never one per card."""
    codes = [e.code for e in events]
    if not codes:
        return events
    stats = get_lecture_completion_stats(user, codes)
    for e in events:
        stat = stats.get(e.code, {})
        total = stat.get("total_topics") or 0
        completed = stat.get("completed_topics") or 0
        e.extra["total_topics"] = total
        e.extra["completed_topics"] = completed
        e.extra["percentage"] = round(completed / total * 100, 1) if total else 0.0
    return events


def attach_revision_status(events, user):
    """Bulk-attach exam-ready + pending-revision-count to CLASS events'
    `.extra`, reusing `revision.get_exam_ready_lecture_codes()` plus a
    new small bulk helper (`revision.get_pending_revision_counts()`) -
    never a per-card query."""
    from progress.services import revision as revision_service

    if not events:
        return events
    ready_codes = revision_service.get_exam_ready_lecture_codes(user)
    lecture_ids = [e.obj.id for e in events]
    pending_counts = revision_service.get_pending_revision_counts(user, lecture_ids)
    for e in events:
        e.extra["exam_ready"] = e.code in ready_codes
        e.extra["pending_revisions"] = pending_counts.get(e.obj.id, 0)
    return events


def attach_exam_readiness(events, user):
    """Bulk-attach readiness info to EXAM events' `.extra`, reusing
    `analytics.get_exam_readiness()` wholesale (computed once for every
    exam regardless of window size - never re-derived here)."""
    if not events:
        return events
    readiness_by_id = {row["exam"].pk: row for row in get_exam_readiness(user)}
    today = timezone.localdate()
    for e in events:
        row = readiness_by_id.get(e.obj.pk)
        if row:
            e.extra.update(row)
        e.extra["days_remaining"] = (e.obj.exam_date - today).days
    return events


# ---------------------------------------------------------------------
# Week/date grouping (view-layer presentation only - no calculations)
# ---------------------------------------------------------------------

def group_by_week(events):
    """[{iso_year, iso_week, days: [{date, events}]}], assuming `events`
    is already in chronological order (true of every window this module
    builds)."""
    weeks = []
    for (iso_year, iso_week), week_group in groupby(events, key=lambda e: e.date.isocalendar()[:2]):
        days = [
            {"date": day, "events": list(day_events)}
            for day, day_events in groupby(week_group, key=lambda e: e.date)
        ]
        weeks.append({"iso_year": iso_year, "iso_week": iso_week, "days": days})
    return weeks


def filter_by_readiness(events, label):
    """Keep only EXAM events whose already-attached readiness label
    (see `attach_exam_readiness()`) matches `label` (one of
    `analytics.READINESS_LABELS`' display values) - a presentation
    filter over data `analytics.get_exam_readiness()` already computed,
    not a second readiness calculation."""
    if not label:
        return events
    return [e for e in events if e.extra.get("readiness_label") == label]


def window_bounds(events):
    """(oldest_date, newest_date) among `events`, as ISO strings, for
    the "load previous"/"load next" HTMX endpoints' cursor params -
    `None` if the window is empty."""
    if not events:
        return None, None
    return events[0].date.isoformat(), events[-1].date.isoformat()


# ---------------------------------------------------------------------
# Routine Week numbering (Milestone 12, Phase 6; unified across Routine
# and Exam Timelines in Milestone 13, Phase 1) - sequential relative to
# this dataset's own imported schedule, not the ISO calendar week of
# the year (which would read as "Week 30" - meaningless to a student,
# and nothing routine.csv exposes anyway; there is no week number
# column anywhere in the imported dataset). "Routine Week 1" is this
# schedule's earliest dated week, "Routine Week 2" the next, and so on.
#
# The map spans every ISO week from the earliest to the latest dated
# Lecture or Exam, inclusive - not just weeks that happen to contain a
# lecture. Milestone 12 originally only numbered weeks with a lecture
# in them, which meant an exam falling in a lecture-free week had no
# number to show, so the Exam Timeline kept a separate, ISO-based
# label. Filling in every week in the span (whether or not a lecture
# lands in it) means both timelines resolve any date in range to the
# same number through this one function - "exactly one shared Routine
# Week implementation," per this milestone's own instruction - rather
# than two numbering schemes that happened to agree most of the time.
# ---------------------------------------------------------------------

def get_routine_week_map():
    """{(iso_year, iso_week): sequential_number} for every ISO week from
    the earliest to the latest dated Lecture/Exam, inclusive - two
    queries (Lecture dates, Exam dates), independent of any timeline
    window (Routine Week is a canonical page - Phase 4/5 - reachable
    regardless of where either timeline's own window currently is)."""
    lecture_dates = Lecture.objects.filter(lecture_date__isnull=False).values_list(
        "lecture_date", flat=True
    )
    exam_dates = Exam.objects.values_list("exam_date", flat=True)
    all_dates = sorted(set(lecture_dates) | set(exam_dates))
    if not all_dates:
        return {}

    first_monday = date.fromisocalendar(*all_dates[0].isocalendar()[:2], 1)
    last_monday = date.fromisocalendar(*all_dates[-1].isocalendar()[:2], 1)

    week_map = {}
    cursor = first_monday
    number = 1
    while cursor <= last_monday:
        week_map[cursor.isocalendar()[:2]] = number
        number += 1
        cursor += timedelta(weeks=1)
    return week_map


def attach_routine_week_numbers(weeks):
    """Mutates `group_by_week()`'s output in place, adding a
    `week_number` key to each entry - the only thing that changes is
    the label a template shows ("Routine Week N" instead of "Week
    {{ iso_week }}, {{ iso_year }}"); the grouping itself is untouched."""
    week_map = get_routine_week_map()
    for week in weeks:
        week["week_number"] = week_map.get((week["iso_year"], week["iso_week"]))
    return weeks


def get_routine_week(week_number):
    """All dated Lectures belonging to Routine Week `week_number`, plus
    the total week count (for Previous/Next navigation on the canonical
    Routine Week page) - `None` if no such week exists."""
    week_map = get_routine_week_map()
    matching_keys = {key for key, number in week_map.items() if number == week_number}
    if not matching_keys:
        return None
    lectures = [
        lecture for lecture in (
            Lecture.objects.filter(lecture_date__isnull=False)
            .select_related("subject")
            .order_by("lecture_date", "start_time")
        )
        if lecture.lecture_date.isocalendar()[:2] in matching_keys
    ]
    return {
        "week_number": week_number,
        "lectures": lectures,
        "total_weeks": len(week_map),
    }
