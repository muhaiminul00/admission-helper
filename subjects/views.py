from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from progress.models import Progress
from progress.services import progress_service
from progress.services.analytics import get_chapter_analytics, get_lecture_analytics, get_subject_analytics
from routines.models import Exam, Lecture

from .models import Chapter, Subject


class SubjectDetailView(LoginRequiredMixin, DetailView):
    """Milestone 12: /subjects/<pk>/ - the single canonical page for a
    Subject (Phase 4/5's "Architectural Rule - Single Canonical
    Entity"). Reuses `analytics.py`'s existing bulk functions rather
    than recalculating completion here - each already computes every
    subject/chapter/lecture's numbers in one query regardless of how
    many rows exist (Milestone 5/8's design), so picking this subject's
    row out of that existing result set costs nothing extra per page.
    """

    model = Subject
    context_object_name = "subject"
    template_name = "subjects/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.object
        user = self.request.user

        subject_row = next(
            (row for row in get_subject_analytics(user) if row["subject"].pk == subject.pk),
            None,
        )
        chapter_rows = get_chapter_analytics(user, subject_code=subject.code)
        lecture_rows = get_lecture_analytics(user, subject_code=subject.code)

        # Milestone 15.2, Parts 2-6: the multi-dimensional progress
        # meter alongside the (unchanged) analytics.py completion
        # numbers above - one bulk query each for the chapter/lecture
        # rows, not one query per row (Part 17).
        subject_progress = progress_service.get_subject_progress(user, subject.code)
        chapter_progress_by_id = progress_service.get_bulk_chapter_progress(
            user, Chapter.objects.filter(subject=subject)
        )
        lecture_progress_by_id = progress_service.get_bulk_lecture_progress(
            user, Lecture.objects.filter(subject=subject)
        )
        for row in chapter_rows:
            row["progress"] = chapter_progress_by_id.get(row["chapter"].pk)
        for row in lecture_rows:
            row["progress"] = lecture_progress_by_id.get(row["lecture"].pk)

        # Exam.covered_lectures is a JSON list of lecture codes, not a
        # FK (Milestone 3) - the same "prefix before the dash" matching
        # `timeline.py: _exam_ids_for_subject()` already uses.
        covering_exams = [
            exam for exam in Exam.objects.all()
            if any(code.split("-")[0] == subject.code for code in exam.covered_lectures)
        ]

        context.update(
            subject_row=subject_row,
            subject_progress=subject_progress,
            chapter_rows=chapter_rows,
            lecture_rows=lecture_rows,
            covering_exams=covering_exams,
        )
        return context


class ChapterDetailView(LoginRequiredMixin, DetailView):
    """Milestone 12: /chapters/<pk>/ - the single canonical page for a
    Chapter. Reuses `analytics.get_chapter_analytics()` for the
    chapter-level completion number (never recalculated here) and
    follows `LectureDetailView`'s exact bulk-Progress-lookup pattern
    (Milestone 4) for the per-topic checklist, rather than introducing
    a second way to compute "is this topic done"."""

    model = Chapter
    context_object_name = "chapter"
    template_name = "subjects/chapter_detail.html"
    queryset = Chapter.objects.select_related("subject")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        user = self.request.user

        chapter_row = next(
            (
                row for row in get_chapter_analytics(user, subject_code=chapter.subject.code)
                if row["chapter"].pk == chapter.pk
            ),
            None,
        )
        chapter_progress = progress_service.get_chapter_progress(user, chapter.pk)

        topics = list(
            chapter.lecture_topics.select_related("lecture", "lecture__subject")
            .order_by("lecture__lecture_date", "display_order")
        )
        progress_by_topic = {
            progress.lecture_topic_id: progress
            for progress in Progress.objects.filter(user=user, lecture_topic__in=topics)
        }
        for topic in topics:
            topic.progress_obj = progress_by_topic.get(topic.id)

        lectures = []
        seen_lecture_ids = set()
        for topic in topics:
            if topic.lecture_id not in seen_lecture_ids:
                seen_lecture_ids.add(topic.lecture_id)
                lectures.append(topic.lecture)

        context.update(
            chapter_row=chapter_row,
            chapter_progress=chapter_progress,
            topics=topics,
            lectures=lectures,
        )
        return context
