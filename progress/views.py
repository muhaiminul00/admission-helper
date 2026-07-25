from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView

from lectures.models import LectureTopic
from routines.models import Lecture
from subjects.models import Chapter, Subject

from .models import Progress, RevisionSchedule
from .services import (
    get_chapter_analytics,
    get_completion_stats,
    get_exam_readiness,
    get_lecture_analytics,
    get_subject_analytics,
)
from .services import advanced_analytics as insights
from .services import progress_service
from .services import revision as revision_service

TOGGLEABLE_FIELDS = {"class_done", "notes_done", "revision_done", "practice_done"}
ANALYTICS_PAGE_SIZE = 20


class ProgressToggleView(LoginRequiredMixin, View):
    """HTMX endpoint: flip one Progress boolean and return the updated row.

    Always operates on `request.user`'s own Progress row -
    get_or_create(user=request.user, lecture_topic=topic) both scopes
    every read/write to the logged-in user and (via the
    (user, lecture_topic) UniqueConstraint) guarantees exactly one
    Progress row per user per topic - never a duplicate, and never
    another user's row. Saving updates `updated_at` automatically
    (auto_now=True).

    Milestone 9: after saving, checks whether this toggle just made the
    topic's lecture fully completed and, if so, creates that lecture's
    revision schedule (`ensure_revision_schedule()` is itself a no-op
    if the lecture isn't fully done yet or already has a schedule, so
    this is safe to call unconditionally on every toggle rather than
    only on the specific field flip that happens to complete it).
    """

    def post(self, request, topic_id, field):
        if field not in TOGGLEABLE_FIELDS:
            raise Http404(f"Unknown progress field '{field}'.")

        topic = get_object_or_404(LectureTopic, pk=topic_id)
        progress, _ = Progress.objects.get_or_create(user=request.user, lecture_topic=topic)
        setattr(progress, field, not getattr(progress, field))
        progress.save()

        revision_service.ensure_revision_schedule(request.user, topic.lecture)

        topic.progress_obj = progress
        return render(request, "lectures/_topic_row.html", {"topic": topic})


class ProgressOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "progress/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_completion_stats(user))
        context["subject_rows"] = get_subject_analytics(user)

        # Milestone 15.2, Parts 2-6: the multi-dimensional progress
        # meter alongside the (unchanged) completed/remaining/percentage
        # numbers above - one bulk query for every subject row's meter,
        # not one query per row (Part 17).
        overall_progress = progress_service.get_overall_progress(user)
        subject_progress_by_id = progress_service.get_bulk_subject_progress(user)
        for row in context["subject_rows"]:
            row["progress"] = subject_progress_by_id.get(row["subject"].pk)

        context["overall_progress"] = overall_progress
        return context


class AnalyticsSubjectsView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/subjects.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["analytics/partials/_subjects_table.html"]
        return [self.template_name]

    SORT_OPTIONS = [("name", "Name"), ("completion", "Completion %"), ("remaining", "Remaining Topics")]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        sort = self.request.GET.get("sort", "name")
        rows = get_subject_analytics(user, sort=sort)

        # Milestone 15.2, Parts 2-6: one bulk query for every row's
        # progress meter (Part 17 - never one query per row).
        progress_by_id = progress_service.get_bulk_subject_progress(user)
        for row in rows:
            row["progress"] = progress_by_id.get(row["subject"].pk)

        context.update(
            rows=rows,
            sort=sort,
            filter_fields=[
                {"kind": "select", "name": "sort", "label": "Sort by", "options": self.SORT_OPTIONS, "selected": sort},
            ],
        )
        return context


class AnalyticsChaptersView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/chapters.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["analytics/partials/_chapters_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self.request.GET.get("subject", "")
        rows = get_chapter_analytics(self.request.user, subject_code=subject_code or None)
        paginator = Paginator(rows, ANALYTICS_PAGE_SIZE)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        subjects = Subject.objects.order_by("display_order")

        # Milestone 15.2, Parts 2-6: bulk progress only for the current
        # page's chapters (Part 17 - never one query per row, and never
        # for the whole dataset when only one page is shown).
        progress_by_id = progress_service.get_bulk_chapter_progress(
            self.request.user, Chapter.objects.filter(id__in=[row["chapter"].pk for row in page_obj])
        )
        for row in page_obj:
            row["progress"] = progress_by_id.get(row["chapter"].pk)

        context.update(
            page_obj=page_obj,
            subjects=subjects,
            selected_subject=subject_code,
            filter_fields=[
                {
                    "kind": "select", "name": "subject", "label": "Subject",
                    "options": [("", "All")] + [(s.code, s.name) for s in subjects],
                    "selected": subject_code,
                },
            ],
        )
        return context


class AnalyticsLecturesView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/lectures.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["analytics/partials/_lectures_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self.request.GET.get("subject", "")
        search = self.request.GET.get("q", "")
        rows = get_lecture_analytics(
            self.request.user, subject_code=subject_code or None, search=search or None
        )
        paginator = Paginator(rows, ANALYTICS_PAGE_SIZE)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        subjects = Subject.objects.order_by("display_order")

        # Milestone 15.2, Parts 2-6: bulk progress only for the current
        # page's lectures (Part 17).
        progress_by_id = progress_service.get_bulk_lecture_progress(
            self.request.user, Lecture.objects.filter(id__in=[row["lecture"].pk for row in page_obj])
        )
        for row in page_obj:
            row["progress"] = progress_by_id.get(row["lecture"].pk)

        context.update(
            page_obj=page_obj,
            subjects=subjects,
            selected_subject=subject_code,
            search=search,
            filter_fields=[
                {"kind": "text", "name": "q", "label": "Search", "value": search, "placeholder": "Lecture code or title"},
                {
                    "kind": "select", "name": "subject", "label": "Subject",
                    "options": [("", "All")] + [(s.code, s.name) for s in subjects],
                    "selected": subject_code,
                },
            ],
        )
        return context


class AnalyticsExamsView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/exams.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["analytics/partials/_exams_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        rows = get_exam_readiness(user)

        exam_ready_codes = revision_service.get_exam_ready_lecture_codes(user)
        for row in rows:
            row["exam_ready_lecture_count"] = sum(
                1 for code in row["exam"].covered_lectures if code in exam_ready_codes
            )

        context["rows"] = rows
        return context


HEATMAP_LEVEL_THRESHOLDS = (0, 1, 3)  # count -> level 0/1/2/3 (0, 1, 2, 3+)


def _heatmap_level(count):
    if count <= 0:
        return 0
    if count < HEATMAP_LEVEL_THRESHOLDS[1] + 1:
        return 1
    if count < HEATMAP_LEVEL_THRESHOLDS[2] + 1:
        return 2
    return 3


def _scale_to_percent(rows, key):
    """Presentational only: adds `<key>_pct` (bar height relative to
    the max value in `rows`) for CSS-only bar charts - no analytics
    calculation happens here, just display scaling."""
    peak = max((r[key] for r in rows), default=0) or 1
    for row in rows:
        row[f"{key}_pct"] = round(row[key] / peak * 100)
    return rows


class AnalyticsInsightsView(LoginRequiredMixin, TemplateView):
    """Milestone 8: the "study advisor" page - what to study next, which
    subjects/chapters/lectures need attention, and exam readiness beyond
    plain completion %. Analytics-only: nothing here schedules anything
    or writes to any model.
    """

    template_name = "analytics/insights.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["analytics/partials/_insights.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetched once, reused by multiple insight functions (rows=...)
        # to avoid re-querying the same chapter/lecture completion data.
        chapter_rows = get_chapter_analytics(user)
        lecture_rows = get_lecture_analytics(user)

        subject_insights = insights.get_subject_insights(user)

        context.update(
            subject_insights=subject_insights,
            subject_trend=insights.get_subject_completion_trend(user),
            average_speed=insights.get_average_completion_speed(user),
            priority_chapters=insights.get_priority_chapters(user, limit=5, rows=chapter_rows),
            neglected_chapters=insights.get_neglected_chapters(user, limit=5),
            most_unfinished_chapters=insights.get_most_unfinished_chapters(
                user, limit=5, rows=chapter_rows
            ),
            most_completed_chapters=insights.get_most_completed_chapters(
                user, limit=5, rows=chapter_rows
            ),
            longest_untouched_lectures=insights.get_longest_untouched_lectures(
                user, limit=5, rows=lecture_rows
            ),
            recently_completed_lectures=insights.get_recently_completed_lectures(user, limit=5),
            backlog_lectures=insights.get_backlog_lectures(user, limit=5, rows=lecture_rows),
            study_streak=insights.get_study_streak(user),
            daily_trend=self._daily_trend_with_levels(insights.get_daily_completion_trend(user, days=35)),
            weekly_distribution=_scale_to_percent(insights.get_weekly_distribution(user), "count"),
            monthly_timeline=_scale_to_percent(insights.get_monthly_completion_timeline(user), "count"),
            exam_insights=insights.get_exam_insights(user),
            revision_insights={
                "completion_percentage": revision_service.get_revision_completion_percentage(user),
                "overdue_count": revision_service.get_overdue_revision_count(user),
                "workload": revision_service.get_revision_workload(user),
                "upcoming_load": revision_service.get_upcoming_revision_load(user),
                "exam_ready_count": revision_service.get_exam_ready_count(user),
                "average_delay": revision_service.get_average_revision_delay(user),
                "streak": revision_service.get_revision_streak(user),
            },
        )
        return context

    @staticmethod
    def _daily_trend_with_levels(days):
        for day in days:
            day["level"] = _heatmap_level(day["count"])
        return days


class RevisionQueueView(LoginRequiredMixin, TemplateView):
    """Milestone 9: /revision/ - Due Today / Overdue / Upcoming /
    Completed, filterable by subject/status/revision level."""

    template_name = "revision/queue.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["revision/partials/_queue.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        subject_code = self.request.GET.get("subject", "")
        status = self.request.GET.get("status", "")
        level = self.request.GET.get("level", "")

        queue = revision_service.get_revision_queue(
            user,
            subject_code=subject_code or None,
            status=status or None,
            level=int(level) if level else None,
        )
        context.update(queue)
        context.update(revision_service.get_revision_dashboard_stats(user))
        subjects = Subject.objects.order_by("display_order")
        levels = RevisionSchedule.Level.choices
        context.update(
            subjects=subjects,
            levels=levels,
            selected_subject=subject_code,
            selected_status=status,
            selected_level=level,
            filter_fields=[
                {
                    "kind": "select", "name": "subject", "label": "Subject",
                    "options": [("", "All")] + [(s.code, s.name) for s in subjects],
                    "selected": subject_code,
                },
                {
                    "kind": "select", "name": "status", "label": "Status",
                    "options": [("", "All"), ("pending", "Pending"), ("completed", "Completed")],
                    "selected": status,
                },
                {
                    "kind": "select", "name": "level", "label": "Revision Level",
                    "options": [("", "All")] + [(str(value), label) for value, label in levels],
                    "selected": level,
                },
            ],
        )
        return context


class RevisionDetailView(LoginRequiredMixin, TemplateView):
    template_name = "revision/detail.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["revision/partials/_detail_content.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = get_object_or_404(
            RevisionSchedule.objects.select_related("lecture", "lecture__subject"),
            pk=kwargs["pk"], user=self.request.user,
        )
        topics = list(
            schedule.lecture.topics.select_related("chapter").order_by("display_order")
        )
        context.update(
            schedule=schedule,
            topics=topics,
            history=list(schedule.history.all()),
            is_exam_ready=revision_service.is_lecture_exam_ready(self.request.user, schedule.lecture),
        )
        return context


class RevisionCompleteView(LoginRequiredMixin, View):
    """HTMX endpoint: mark one of the user's own revision schedules
    complete and return the refreshed detail fragment."""

    def post(self, request, pk):
        schedule = revision_service.complete_revision(request.user, pk)
        if schedule is None:
            raise Http404("Revision schedule not found.")

        topics = list(
            schedule.lecture.topics.select_related("chapter").order_by("display_order")
        )
        context = {
            "schedule": schedule,
            "topics": topics,
            "history": list(schedule.history.all()),
            "is_exam_ready": revision_service.is_lecture_exam_ready(request.user, schedule.lecture),
        }
        return render(request, "revision/partials/_detail_content.html", context)
