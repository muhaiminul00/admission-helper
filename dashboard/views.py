from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from progress.services.advanced_analytics import get_advanced_dashboard_widgets
from progress.services.dashboard import get_dashboard_stats, get_dashboard_widgets
from progress.services.progress_service import get_overall_progress
from progress.services.revision import get_revision_dashboard_stats
from routines.models import Exam, Lecture


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        today_lectures = Lecture.objects.filter(lecture_date=today).select_related("subject")
        today_exams = Exam.objects.filter(exam_date=today)

        context.update(
            today=today,
            today_lectures=today_lectures,
            today_exams=today_exams,
            has_today_routine=today_lectures.exists() or today_exams.exists(),
            upcoming_lecture=(
                Lecture.objects.filter(lecture_date__gt=today)
                .select_related("subject")
                .order_by("lecture_date", "start_time")
                .first()
            ),
            upcoming_exam=(
                Exam.objects.filter(exam_date__gt=today).order_by("exam_date").first()
            ),
        )
        context.update(get_dashboard_stats(self.request.user))
        context.update(get_dashboard_widgets(self.request.user))
        context.update(get_advanced_dashboard_widgets(self.request.user))
        context.update(get_revision_dashboard_stats(self.request.user))
        # Milestone 15.2, Parts 2-6: the multi-dimensional progress
        # meter for the "Overall Completion" widget below.
        context["overall_progress"] = get_overall_progress(self.request.user)
        return context


class DashboardWidgetsView(LoginRequiredMixin, TemplateView):
    """HTMX partial: refreshes the widgets section without a full page reload."""

    template_name = "dashboard/_widgets.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_dashboard_stats(self.request.user))
        context.update(get_dashboard_widgets(self.request.user))
        context.update(get_advanced_dashboard_widgets(self.request.user))
        context.update(get_revision_dashboard_stats(self.request.user))
        # Milestone 15.2, Parts 2-6: the multi-dimensional progress
        # meter for the "Overall Completion" widget below.
        context["overall_progress"] = get_overall_progress(self.request.user)
        return context
