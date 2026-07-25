"""Subject/chapter/lecture/exam analytics calculations.

Calculated on demand (never cached), matching Milestone 4's "Do not
cache" precedent. A topic counts as complete when its Progress record
has all four study-stage booleans set - the same definition used
throughout the application.

Completion counts are computed with conditional aggregation
(annotate/Case/When) rather than per-row Python loops, so each page
issues a small, fixed number of queries regardless of dataset size.
"""

from django.db.models import Case, Count, IntegerField, Q, Sum, When

from routines.models import Exam, Lecture
from subjects.models import Chapter, Subject

READINESS_READY = "ready"
READINESS_GOOD = "good"
READINESS_NEEDS_WORK = "needs_work"
READINESS_HIGH_RISK = "high_risk"

READINESS_LABELS = {
    READINESS_READY: "Ready",
    READINESS_GOOD: "Good",
    READINESS_NEEDS_WORK: "Needs Work",
    READINESS_HIGH_RISK: "High Risk",
}

READINESS_BADGE_CLASSES = {
    READINESS_READY: "bg-emerald-100 text-emerald-800",
    READINESS_GOOD: "bg-blue-100 text-blue-800",
    READINESS_NEEDS_WORK: "bg-amber-100 text-amber-800",
    READINESS_HIGH_RISK: "bg-red-100 text-red-800",
}


def _percentage(completed, total):
    return round(completed / total * 100, 1) if total else 0.0


def completed_case(user, join_prefix="", since=None):
    """A Case/When that yields 1 for a topic fully completed BY `user`, else 0.

    `join_prefix` is the ORM path from the annotated model down to
    LectureTopic's reverse `progress_records` relation (e.g. "topics__"
    when annotating Lecture, "" when annotating LectureTopic itself).

    `since` (Milestone 8) optionally restricts to completions whose
    `Progress.updated_at` date is on or after that date - used for
    completion-trend calculations (today/7-day/30-day counts) without a
    second query per window: multiple `Sum(completed_case(..., since=X))`
    annotations, one per window, run in a single annotated query.

    Milestone 7: `progress_records` is no longer to-one (many users can
    each have a Progress row for the same topic), so the join can fan
    out to one row per user who has touched that topic. Filtering the
    When condition on `user` as well as the four booleans keeps the
    result correct regardless of that fan-out: every other user's
    joined row fails the `user` equality and contributes 0, and
    (user, lecture_topic) is unique so at most one row can ever satisfy
    the full condition per topic.
    """
    def field(name):
        return f"{join_prefix}progress_records__{name}"

    conditions = {
        field("user"): user,
        field("class_done"): True,
        field("notes_done"): True,
        field("revision_done"): True,
        field("practice_done"): True,
    }
    if since is not None:
        conditions[field("updated_at__date__gte")] = since

    return Case(
        When(**conditions, then=1),
        default=0,
        output_field=IntegerField(),
    )


def get_lecture_completion_stats(user, lecture_codes):
    """Bulk lecture-code -> {total_topics, completed_topics} for `user`.

    Shared by `get_exam_readiness()` here and
    `progress/services/advanced_analytics.py: get_exam_insights()` - one
    query regardless of how many lecture codes are passed, avoiding a
    query pair per exam/lookup (N+1).
    """
    return {
        row["lecture_code"]: row
        for row in Lecture.objects.filter(lecture_code__in=lecture_codes)
        .annotate(
            total_topics=Count("topics", distinct=True),
            completed_topics=Sum(completed_case(user, "topics__")),
        )
        .values("lecture_code", "total_topics", "completed_topics")
    }


def readiness_label(percentage):
    if percentage >= 90:
        return READINESS_READY
    if percentage >= 70:
        return READINESS_GOOD
    if percentage >= 40:
        return READINESS_NEEDS_WORK
    return READINESS_HIGH_RISK


SUBJECT_SORT_KEYS = {
    "name": (lambda row: row["subject"].name.lower(), False),
    "completion": (lambda row: row["percentage"], True),
    "remaining": (lambda row: row["remaining"], True),
}


def get_subject_analytics(user, sort="name"):
    """Per-subject topic totals/completion for `user`, using
    lecture->subject (not chapter->subject) so subjects with no chapter
    breakdown (e.g. English, Bangla self-study topics) are still
    counted correctly.
    """
    subjects = Subject.objects.annotate(
        total_topics=Count("lectures__topics", distinct=True),
        completed_topics=Sum(completed_case(user, "lectures__topics__")),
    )

    rows = []
    for subject in subjects:
        total = subject.total_topics
        completed = subject.completed_topics or 0
        rows.append(
            {
                "subject": subject,
                "total": total,
                "completed": completed,
                "remaining": total - completed,
                "percentage": _percentage(completed, total),
            }
        )

    key, reverse = SUBJECT_SORT_KEYS.get(sort, SUBJECT_SORT_KEYS["name"])
    rows.sort(key=key, reverse=reverse)
    return rows


def get_chapter_analytics(user, subject_code=None):
    chapters = Chapter.objects.select_related("subject").annotate(
        total_topics=Count("lecture_topics", distinct=True),
        completed_topics=Sum(completed_case(user, "lecture_topics__")),
    )
    if subject_code:
        chapters = chapters.filter(subject__code=subject_code)

    rows = []
    for chapter in chapters:
        total = chapter.total_topics
        completed = chapter.completed_topics or 0
        rows.append(
            {
                "chapter": chapter,
                "total": total,
                "completed": completed,
                "remaining": total - completed,
                "percentage": _percentage(completed, total),
            }
        )
    return rows


def get_lecture_analytics(user, subject_code=None, search=None):
    lectures = Lecture.objects.select_related("subject").annotate(
        total_topics=Count("topics", distinct=True),
        completed_topics=Sum(completed_case(user, "topics__")),
    )
    if subject_code:
        lectures = lectures.filter(subject__code=subject_code)
    if search:
        lectures = lectures.filter(
            Q(lecture_code__icontains=search) | Q(title__icontains=search)
        )

    rows = []
    for lecture in lectures:
        total = lecture.total_topics
        completed = lecture.completed_topics or 0
        rows.append(
            {
                "lecture": lecture,
                "total": total,
                "completed": completed,
                "remaining": total - completed,
                "percentage": _percentage(completed, total),
            }
        )
    return rows


def get_exam_readiness(user):
    """Readiness per exam for `user`, resolved from `covered_lectures` codes.

    `covered_lectures` is a plain JSON list of lecture codes (not a
    FK), so lecture/topic completion for every exam is pre-fetched in
    one bulk query (`get_lecture_completion_stats()`) up front and then
    looked up per exam in Python - avoiding one query pair per exam (N+1).
    """
    exams = list(Exam.objects.all())

    all_codes = set()
    for exam in exams:
        all_codes.update(exam.covered_lectures)

    stats_by_code = get_lecture_completion_stats(user, all_codes)

    rows = []
    for exam in exams:
        total = 0
        completed = 0
        covered_lecture_count = 0
        for code in exam.covered_lectures:
            stat = stats_by_code.get(code)
            if stat is None:
                continue
            covered_lecture_count += 1
            total += stat["total_topics"] or 0
            completed += stat["completed_topics"] or 0

        percentage = _percentage(completed, total)
        label = readiness_label(percentage)
        rows.append(
            {
                "exam": exam,
                "covered_lecture_count": covered_lecture_count,
                "total_topics": total,
                "completed_topics": completed,
                "remaining_topics": total - completed,
                "percentage": percentage,
                "readiness_label": READINESS_LABELS[label],
                "readiness_badge_class": READINESS_BADGE_CLASSES[label],
            }
        )
    return rows
