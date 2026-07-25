"""Weekly Overview (Milestone 15, Phase 2).

Triggers on the first day of every Routine Week - never Saturday,
Sunday, or the ISO calendar week. `routines.services.timeline.
get_routine_week_map()` keys every week by the Monday that starts its
ISO span (see that module's own docstring), so "first day of a Routine
Week" is exactly "today is a Monday whose (iso_year, iso_week) is in
the map" - no second definition of "week boundary" is introduced here.
"""

from datetime import timedelta

from django.utils import timezone

from progress.models import RevisionSchedule
from routines.models import Exam
from routines.services import timeline

from ..models import ReminderLog
from .job import ReminderJob
from .preferences import get_preferences
from .targeting import target_users

ReminderType = ReminderLog.ReminderType
Status = RevisionSchedule.Status


def _day_by_day_schedule(monday, week_lectures, week_exams):
    days = []
    for offset in range(7):
        day = monday + timedelta(days=offset)
        days.append(
            {
                "date": day,
                "lectures": [lecture for lecture in week_lectures if lecture.lecture_date == day],
                "exams": [exam for exam in week_exams if exam.exam_date == day],
            }
        )
    return days


def generate(now=None, current_time=None, users=None):
    # current_time is accepted (unused) only so `engine.py` can call
    # every generator with the same signature - this reminder type has
    # no time-of-day gate, only a date one.
    today = now or timezone.localdate()
    if today.weekday() != 0:
        return []

    week_map = timeline.get_routine_week_map()
    week_number = week_map.get(today.isocalendar()[:2])
    if week_number is None:
        return []

    week = timeline.get_routine_week(week_number)
    monday = today
    sunday = monday + timedelta(days=6)
    week_exams = list(Exam.objects.filter(exam_date__gte=monday, exam_date__lte=sunday).order_by("exam_date"))
    days = _day_by_day_schedule(monday, week["lectures"], week_exams)

    jobs = []
    for user in target_users(users):
        prefs = get_preferences(user)
        if not prefs.weekly_overview_enabled:
            continue

        revision_count = (
            RevisionSchedule.objects.filter(user=user, due_date__gte=monday, due_date__lte=sunday)
            .exclude(status=Status.COMPLETED)
            .count()
        )

        jobs.append(
            ReminderJob(
                user=user,
                reminder_type=ReminderType.WEEKLY_OVERVIEW,
                reference_key=str(week_number),
                context={
                    "week_number": week_number,
                    "monday": monday,
                    "sunday": sunday,
                    "lecture_count": len(week["lectures"]),
                    "exam_count": len(week_exams),
                    "revision_count": revision_count,
                    "days": days,
                },
            )
        )
    return jobs
