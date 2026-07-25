"""Dashboard-level aggregate stats and widgets.

Calculated on demand (never cached), per Milestone 4's "Do not cache"
precedent. Every function that touches `Progress` is scoped to a
single `user` (Milestone 7: Progress became per-user) - no function
here ever computes another user's progress.
"""

from django.db.models import Count, F, Sum
from django.utils import timezone

from lectures.models import LectureTopic
from routines.models import Exam, Lecture

from ..models import Progress
from .analytics import completed_case, get_subject_analytics

COMPLETED_TOPIC_FILTER = dict(
    class_done=True, notes_done=True, revision_done=True, practice_done=True
)


def get_completion_stats(user):
    total_topics = LectureTopic.objects.count()
    completed_topics = Progress.objects.filter(
        user=user, **COMPLETED_TOPIC_FILTER
    ).count()
    remaining_topics = total_topics - completed_topics
    completion_percentage = (
        round(completed_topics / total_topics * 100, 1) if total_topics else 0
    )
    return {
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "remaining_topics": remaining_topics,
        "completion_percentage": completion_percentage,
    }


def get_lecture_stats(user):
    total_lectures = Lecture.objects.count()
    completed_lectures = (
        Lecture.objects.annotate(
            total_topics=Count("topics", distinct=True),
            completed_topics=Sum(completed_case(user, "topics__")),
        )
        .filter(total_topics__gt=0, completed_topics=F("total_topics"))
        .count()
    )
    return {"total_lectures": total_lectures, "completed_lectures": completed_lectures}


def get_exam_stats():
    """Exam existence/scheduling is global, not user-owned data - every
    user sees the same upcoming exams/next exam."""
    today = timezone.localdate()
    upcoming_exams_qs = Exam.objects.filter(exam_date__gte=today).order_by("exam_date")
    next_exam = upcoming_exams_qs.first()
    return {
        "total_exams": Exam.objects.count(),
        "upcoming_exams": upcoming_exams_qs.count(),
        "days_remaining": (next_exam.exam_date - today).days if next_exam else None,
        "next_exam": next_exam,
    }


def get_dashboard_stats(user):
    stats = {}
    stats.update(get_completion_stats(user))
    stats.update(get_lecture_stats(user))
    stats.update(get_exam_stats())
    return stats


def get_recent_activity(user, limit=10):
    return (
        Progress.objects.filter(user=user, **COMPLETED_TOPIC_FILTER)
        .select_related(
            "lecture_topic__lecture__subject", "lecture_topic__chapter"
        )
        .order_by("-updated_at")[:limit]
    )


def get_upcoming_exams_widget(limit=5):
    today = timezone.localdate()
    return Exam.objects.filter(exam_date__gte=today).order_by("exam_date")[:limit]


def get_subject_extremes(user):
    """(most completed, least completed) subject rows for `user`,
    ignoring subjects with zero topics (nothing meaningful to rank)."""
    rows = [row for row in get_subject_analytics(user, sort="name") if row["total"] > 0]
    if not rows:
        return {"most_completed": None, "least_completed": None}
    return {
        "most_completed": max(rows, key=lambda row: row["percentage"]),
        "least_completed": min(rows, key=lambda row: row["percentage"]),
    }


def get_daily_progress_count(user):
    today = timezone.localdate()
    return Progress.objects.filter(
        user=user, updated_at__date=today, **COMPLETED_TOPIC_FILTER
    ).count()


def get_dashboard_widgets(user):
    widgets = {
        "recent_activity": get_recent_activity(user),
        "upcoming_exams_list": get_upcoming_exams_widget(),
    }
    widgets.update(get_subject_extremes(user))
    widgets["daily_progress_count"] = get_daily_progress_count(user)
    return widgets
