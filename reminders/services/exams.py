"""Exam Reminders (Milestone 15, Phase 5).

Weekly Exams: 1 day before, exam day morning.
Monthly Exams: 7/3/1 days before, exam day morning.

Readiness/coverage are both reused wholesale - `progress.services.
analytics.get_exam_readiness()` for the percentage/label,
`routines.services.exam_coverage.get_exam_coverage()` (the same
function `ExamDetailView` uses) for covered subjects/chapters/
lectures, and `progress.services.revision.get_exam_ready_lecture_codes()`
for which of those lectures are already exam-ready. Nothing here
recomputes any of those three calculations.
"""

from datetime import time, timedelta

from django.utils import timezone

from progress.services import revision as revision_service
from progress.services.analytics import get_exam_readiness
from routines.models import Exam
from routines.services.exam_coverage import get_exam_coverage

from ..models import ReminderLog
from .job import ReminderJob
from .preferences import get_preferences
from .targeting import target_users

ReminderType = ReminderLog.ReminderType

# Not user-configurable (unlike the Daily Agenda's delivery time, per
# Phase 7's preference list) - a fixed "morning" gate so an exam-day
# reminder never fires in the middle of the night for a scheduler that
# happens to run more than once a day.
EXAM_DAY_MORNING_TIME = time(8, 0)

WEEKLY_OFFSETS = (1, 0)
MONTHLY_OFFSETS = (7, 3, 1, 0)


def _offset_label(offset):
    return "day_of" if offset == 0 else f"{offset}d_before"


def _due_exams(exam_type, offsets, today):
    """[(exam, offset)] for every exam of `exam_type` whose date is
    exactly `offset` days from `today`, for each configured offset."""
    due = []
    for offset in offsets:
        exam_date = today + timedelta(days=offset)
        for exam in Exam.objects.filter(exam_type=exam_type, exam_date=exam_date):
            due.append((exam, offset))
    return due


def _generate(exam_type, offsets, reminder_type, pref_field, now, current_time, users):
    today = now or timezone.localdate()
    current_time = current_time if current_time is not None else timezone.localtime().time()

    due = _due_exams(exam_type, offsets, today)
    due = [(exam, offset) for exam, offset in due if offset != 0 or current_time >= EXAM_DAY_MORNING_TIME]
    if not due:
        return []

    jobs = []
    for user in target_users(users):
        prefs = get_preferences(user)
        if not getattr(prefs, pref_field):
            continue

        readiness_by_exam_id = {row["exam"].pk: row for row in get_exam_readiness(user)}
        ready_codes = revision_service.get_exam_ready_lecture_codes(user)

        for exam, offset in due:
            coverage = get_exam_coverage(exam)
            remaining_lectures = [
                row["lecture"]
                for row in coverage["covered_lecture_rows"]
                if row["lecture"] is not None and row["code"] not in ready_codes
            ]
            jobs.append(
                ReminderJob(
                    user=user,
                    reminder_type=reminder_type,
                    reference_key=f"{exam.pk}:{_offset_label(offset)}",
                    context={
                        "exam": exam,
                        "days_remaining": offset,
                        "readiness": readiness_by_exam_id.get(exam.pk),
                        "covered_subjects": coverage["covered_subjects"],
                        "covered_chapters": coverage["covered_chapters"],
                        "remaining_lectures": remaining_lectures,
                    },
                )
            )
    return jobs


def generate_weekly(now=None, current_time=None, users=None):
    return _generate(
        Exam.ExamType.WEEKLY, WEEKLY_OFFSETS, ReminderType.WEEKLY_EXAM,
        "weekly_exam_reminder_enabled", now, current_time, users,
    )


def generate_monthly(now=None, current_time=None, users=None):
    return _generate(
        Exam.ExamType.MONTHLY, MONTHLY_OFFSETS, ReminderType.MONTHLY_EXAM,
        "monthly_exam_reminder_enabled", now, current_time, users,
    )
