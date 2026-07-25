"""Daily Study Agenda (Milestone 15, Phase 3).

One reminder per active user per calendar day, once their configured
delivery time has passed. Reuses `progress.services.revision.
get_revision_queue()` for today's/overdue revisions rather than
re-deriving due-date buckets, and plain model queries for today's
Lectures/Exams (the same kind of direct query the Routine/Exam
Timeline modules already do - no completion/readiness calculation
happens here).
"""

from django.utils import timezone

from progress.services import revision as revision_service
from routines.models import Exam, Lecture

from ..models import ReminderLog
from .job import ReminderJob
from .preferences import get_preferences
from .targeting import target_users

ReminderType = ReminderLog.ReminderType


def generate(now=None, current_time=None, users=None):
    today = now or timezone.localdate()
    current_time = current_time if current_time is not None else timezone.localtime().time()

    jobs = []
    for user in target_users(users):
        prefs = get_preferences(user)
        if not prefs.daily_agenda_enabled:
            continue
        if current_time < prefs.daily_agenda_time:
            continue

        lectures = list(
            Lecture.objects.filter(lecture_date=today).select_related("subject").order_by("start_time")
        )
        exams_today = list(Exam.objects.filter(exam_date=today))
        queue = revision_service.get_revision_queue(user)
        revisions_today = queue["due_today"]
        overdue_revisions = queue["overdue"]
        has_activity = bool(lectures or exams_today or revisions_today)

        jobs.append(
            ReminderJob(
                user=user,
                reminder_type=ReminderType.DAILY_AGENDA,
                reference_key=today.isoformat(),
                context={
                    "today": today,
                    "lectures": lectures,
                    "exams": exams_today,
                    "revisions": revisions_today,
                    "overdue_revisions": overdue_revisions,
                    "has_activity": has_activity,
                    "study_load": len(lectures) + len(revisions_today) + len(exams_today),
                },
            )
        )
    return jobs
