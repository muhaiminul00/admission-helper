"""Weekly Progress Summary (Milestone 15, Phase 6).

Triggers the day a completed Routine Week hands off to the next one -
the same Monday `weekly.generate()` fires the *next* week's overview
on, summarizing the week that just ended (`today - 7 days`'s Monday)
instead. Completion/readiness numbers are all reused: lecture
completion via `progress.services.analytics.get_lecture_completion_stats()`,
overall progress via `progress.services.dashboard.get_completion_stats()`.
"""

from datetime import timedelta

from django.utils import timezone

from progress.models import RevisionSchedule
from progress.services.analytics import get_lecture_completion_stats
from progress.services.dashboard import get_completion_stats
from routines.models import Exam
from routines.services import timeline

from ..models import ReminderLog
from .job import ReminderJob
from .preferences import get_preferences
from .targeting import target_users

ReminderType = ReminderLog.ReminderType
Status = RevisionSchedule.Status


def generate(now=None, current_time=None, users=None):
    # current_time is accepted (unused) only for a uniform generator
    # signature - see weekly.generate()'s comment.
    today = now or timezone.localdate()
    if today.weekday() != 0:
        return []

    week_map = timeline.get_routine_week_map()
    prev_monday = today - timedelta(days=7)
    prev_week_number = week_map.get(prev_monday.isocalendar()[:2])
    if prev_week_number is None:
        return []
    prev_sunday = prev_monday + timedelta(days=6)

    prev_week = timeline.get_routine_week(prev_week_number)
    lecture_codes = [lecture.lecture_code for lecture in prev_week["lectures"]]
    exams_prev_week_count = Exam.objects.filter(
        exam_date__gte=prev_monday, exam_date__lte=prev_sunday
    ).count()

    next_week_number = week_map.get(today.isocalendar()[:2])
    next_week = timeline.get_routine_week(next_week_number) if next_week_number else None
    next_week_exam_count = (
        Exam.objects.filter(exam_date__gte=today, exam_date__lte=today + timedelta(days=6)).count()
        if next_week
        else 0
    )

    jobs = []
    for user in target_users(users):
        prefs = get_preferences(user)
        if not prefs.weekly_progress_enabled:
            continue

        stats_by_code = get_lecture_completion_stats(user, lecture_codes)
        completed_lectures = sum(
            1
            for code in lecture_codes
            if stats_by_code.get(code, {}).get("total_topics")
            and stats_by_code[code]["total_topics"] == stats_by_code[code]["completed_topics"]
        )
        completed_revisions = RevisionSchedule.objects.filter(
            user=user,
            lecture__lecture_code__in=lecture_codes,
            status=Status.COMPLETED,
            completed_at__date__gte=prev_monday,
            completed_at__date__lte=prev_sunday,
        ).count()
        overall_percentage = get_completion_stats(user)["completion_percentage"]

        jobs.append(
            ReminderJob(
                user=user,
                reminder_type=ReminderType.WEEKLY_PROGRESS,
                reference_key=str(prev_week_number),
                context={
                    "week_number": prev_week_number,
                    "monday": prev_monday,
                    "sunday": prev_sunday,
                    "total_lectures": len(lecture_codes),
                    "completed_lectures": completed_lectures,
                    "completed_revisions": completed_revisions,
                    "exams_completed_count": exams_prev_week_count,
                    "overall_percentage": overall_percentage,
                    "next_week_number": next_week_number,
                    "next_week_lecture_count": len(next_week["lectures"]) if next_week else 0,
                    "next_week_exam_count": next_week_exam_count,
                },
            )
        )
    return jobs
