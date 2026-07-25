"""Revision Reminder (Milestone 15, Phase 4).

Notifies a user the moment one of their `RevisionSchedule` rows
becomes due today - one reminder per lecture per due occurrence,
enforced by using the `RevisionSchedule` row's own id as the
idempotency `reference_key` (each of a lecture's three revision
levels is its own row/occurrence, so this naturally covers "per
lecture per due occurrence" without any extra bookkeeping).
"""

from django.utils import timezone

from progress.models import RevisionSchedule

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

    jobs = []
    for user in target_users(users):
        prefs = get_preferences(user)
        if not prefs.revision_reminder_enabled:
            continue

        schedules = (
            RevisionSchedule.objects.filter(user=user, status=Status.PENDING, due_date=today)
            .select_related("lecture", "lecture__subject")
        )
        for schedule in schedules:
            lecture = schedule.lecture
            days_since_last_study = (today - lecture.lecture_date).days if lecture.lecture_date else None
            chapters = sorted(
                {topic.chapter for topic in lecture.topics.select_related("chapter") if topic.chapter},
                key=lambda chapter: (chapter.paper, chapter.chapter_no),
            )
            jobs.append(
                ReminderJob(
                    user=user,
                    reminder_type=ReminderType.REVISION_DUE,
                    reference_key=str(schedule.id),
                    context={
                        "schedule": schedule,
                        "lecture": lecture,
                        "subject": lecture.subject,
                        "chapters": chapters,
                        "days_since_last_study": days_since_last_study,
                    },
                )
            )
    return jobs
