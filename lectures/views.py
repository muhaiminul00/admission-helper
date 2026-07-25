from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from progress.models import Progress
from progress.services import revision as revision_service
from routines.models import Exam, Lecture


class LectureDetailView(LoginRequiredMixin, DetailView):
    model = Lecture
    slug_field = "lecture_code"
    slug_url_kwarg = "lecture_code"
    context_object_name = "lecture"
    template_name = "lectures/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecture = self.object
        user = self.request.user

        topics = list(
            lecture.topics.select_related("chapter", "chapter__subject")
            .order_by("display_order")
        )
        progress_by_topic = {
            progress.lecture_topic_id: progress
            for progress in Progress.objects.filter(
                user=user, lecture_topic__in=topics
            )
        }
        for topic in topics:
            topic.progress_obj = progress_by_topic.get(topic.id)

        chapters = []
        seen_chapter_ids = set()
        for topic in topics:
            if topic.chapter_id is not None and topic.chapter_id not in seen_chapter_ids:
                seen_chapter_ids.add(topic.chapter_id)
                chapters.append(topic.chapter)

        revision_schedules = list(
            lecture.revision_schedules.filter(user=user).order_by("revision_level")
        )

        # Milestone 12, Phase 10 - cross-navigation. Previous/Next
        # Lecture scoped to the same subject (comparing across subjects
        # wouldn't mean anything to a student navigating "what's next
        # in this course"), ordered the same way the Routine Timeline
        # already orders lectures. Upcoming Exam: the nearest exam
        # (by date) whose covered_lectures includes this lecture's code.
        previous_lecture = next_lecture = None
        if lecture.lecture_date:
            previous_lecture = (
                Lecture.objects.filter(
                    subject=lecture.subject, lecture_date__lt=lecture.lecture_date
                )
                .order_by("-lecture_date", "-start_time")
                .first()
            )
            next_lecture = (
                Lecture.objects.filter(
                    subject=lecture.subject, lecture_date__gt=lecture.lecture_date
                )
                .order_by("lecture_date", "start_time")
                .first()
            )

        covering_exams = sorted(
            (
                exam for exam in Exam.objects.all()
                if lecture.lecture_code in exam.covered_lectures
            ),
            key=lambda exam: exam.exam_date,
        )

        context.update(
            topics=topics,
            chapters=chapters,
            revision_schedules=revision_schedules,
            is_exam_ready=revision_service.is_lecture_exam_ready(user, lecture),
            previous_lecture=previous_lecture,
            next_lecture=next_lecture,
            covering_exams=covering_exams,
        )
        return context
