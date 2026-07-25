from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse, Http404
from django.views.generic import DetailView, TemplateView, View

from progress.services import revision as revision_service
from progress.services.analytics import READINESS_LABELS, get_exam_readiness
from subjects.models import Subject

from .models import DatasetVersion, Exam, ImportLog
from .services import archive as archive_service
from .services import timeline
from .services.dataset.comparison import COMPARISON_SECTIONS, compare_all, detect_duplicates
from .services.exam_coverage import get_exam_coverage

COMPLETED_PARAM_MAP = {"1": True, "0": False}


class _TimelineViewMixin:
    """Shared query-param parsing for the Routine/Exam timeline pages
    and their "load more" window endpoints (Milestone 10.5)."""

    def _subject_code(self):
        return self.request.GET.get("subject", "")

    def _completed_param(self):
        return self.request.GET.get("completed", "")

    def _completed(self):
        return COMPLETED_PARAM_MAP.get(self._completed_param())

    def _before_after(self):
        return self.request.GET.get("before") or None, self.request.GET.get("after") or None

    def _status(self):
        return self.request.GET.get("status", "")

    @staticmethod
    def _subject_options(subjects_qs):
        """(value, label) options for the shared select_field/filter_panel
        components - presentation-only reshaping of an already-fetched
        queryset, not a new query or calculation."""
        return [("", "All")] + [(s.code, s.name) for s in subjects_qs]


class RoutineTimelineView(_TimelineViewMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10.5: /routine/ - a scrollable timeline of dated
    Lectures centered on the user's current study position, replacing
    the old page-based `RoutineListView`. Exams get their own dedicated
    timeline (`ExamTimelineView`) rather than being merged in here -
    see PROJECT_PROGRESS.md, Milestone 10.5, for why.
    """

    template_name = "routine/timeline.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["routine/partials/_timeline.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self._subject_code()
        completed = self._completed()
        user = self.request.user

        window = timeline.get_lecture_timeline(subject_code=subject_code, completed=completed, user=user)
        events = window["events"]
        timeline.attach_lecture_progress(events, user)
        timeline.attach_revision_status(events, user)
        oldest_date, newest_date = timeline.window_bounds(events)

        subjects = Subject.objects.order_by("display_order")
        context.update(
            weeks=timeline.attach_routine_week_numbers(timeline.group_by_week(events)),
            anchor=window.get("anchor"),
            today=window.get("today"),
            has_more_previous=window["has_more_previous"],
            has_more_next=window["has_more_next"],
            oldest_date=oldest_date,
            newest_date=newest_date,
            subjects=subjects,
            selected_subject=subject_code,
            selected_completed=self._completed_param(),
            filter_fields=[
                {
                    "kind": "select", "name": "subject", "label": "Subject",
                    "options": self._subject_options(subjects), "selected": subject_code,
                },
                {
                    "kind": "select", "name": "completed", "label": "Status",
                    "options": [("", "All"), ("1", "Completed"), ("0", "Incomplete")],
                    "selected": self._completed_param(),
                },
            ],
        )
        return context


class RoutineTimelineWindowView(_TimelineViewMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10.5: `/routine/window/` - HTMX "load older"/"load
    newer" endpoint, hit when the sentinel div at either edge of the
    timeline scrolls into view (`hx-trigger="revealed"`)."""

    def get_template_names(self):
        direction = self.request.GET.get("direction")
        if direction == "previous":
            return ["routine/partials/_window_previous.html"]
        return ["routine/partials/_window_next.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self._subject_code()
        completed = self._completed()
        before, after = self._before_after()
        user = self.request.user

        window = timeline.get_lecture_timeline(
            subject_code=subject_code, completed=completed, user=user, before=before, after=after
        )
        events = window["events"]
        timeline.attach_lecture_progress(events, user)
        timeline.attach_revision_status(events, user)
        oldest_date, newest_date = timeline.window_bounds(events)

        context.update(
            weeks=timeline.attach_routine_week_numbers(timeline.group_by_week(events)),
            anchor=None,
            has_more_previous=window.get("has_more_previous", False),
            has_more_next=window.get("has_more_next", False),
            oldest_date=oldest_date,
            newest_date=newest_date,
            selected_subject=subject_code,
            selected_completed=self._completed_param(),
        )
        return context


class ExamTimelineView(_TimelineViewMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10.5: /routine/exams/ - a scrollable timeline of Exams
    centered on the current/next upcoming exam. No dedicated exam list
    page existed before this milestone (exams previously only surfaced
    as a filtered view of the routine list, or via the Analytics
    readiness page)."""

    template_name = "exams/timeline.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["exams/partials/_timeline.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self._subject_code()
        status = self._status()
        user = self.request.user

        window = timeline.get_exam_timeline(subject_code=subject_code)
        events = window["events"]
        timeline.attach_exam_readiness(events, user)
        oldest_date, newest_date = timeline.window_bounds(events)
        events = timeline.filter_by_readiness(events, status)

        subjects = Subject.objects.order_by("display_order")
        status_choices = list(READINESS_LABELS.values())
        context.update(
            # Milestone 13, Phase 1: the Exam Timeline now shares the
            # exact same Routine Week numbering as the Routine Timeline
            # (get_routine_week_map() spans every week from the earliest
            # to latest dated Lecture/Exam, so an exam date always
            # resolves to a number even in a lecture-free week) - one
            # shared implementation, not two numbering schemes.
            weeks=timeline.attach_routine_week_numbers(timeline.group_by_week(events)),
            anchor=window.get("anchor"),
            today=window.get("today"),
            has_more_previous=window["has_more_previous"],
            has_more_next=window["has_more_next"],
            oldest_date=oldest_date,
            newest_date=newest_date,
            subjects=subjects,
            selected_subject=subject_code,
            selected_status=status,
            status_choices=status_choices,
            filter_fields=[
                {
                    "kind": "select", "name": "subject", "label": "Subject",
                    "options": self._subject_options(subjects), "selected": subject_code,
                },
                {
                    "kind": "select", "name": "status", "label": "Readiness",
                    "options": [("", "All")] + [(label, label) for label in status_choices],
                    "selected": status,
                },
            ],
        )
        return context


class ExamTimelineWindowView(_TimelineViewMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10.5: `/routine/exams/window/` - "load older"/"load
    newer" endpoint for the Exam Timeline."""

    def get_template_names(self):
        direction = self.request.GET.get("direction")
        if direction == "previous":
            return ["exams/partials/_window_previous.html"]
        return ["exams/partials/_window_next.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_code = self._subject_code()
        status = self._status()
        before, after = self._before_after()
        user = self.request.user

        window = timeline.get_exam_timeline(subject_code=subject_code, before=before, after=after)
        events = window["events"]
        timeline.attach_exam_readiness(events, user)
        oldest_date, newest_date = timeline.window_bounds(events)
        events = timeline.filter_by_readiness(events, status)

        context.update(
            weeks=timeline.attach_routine_week_numbers(timeline.group_by_week(events)),
            anchor=None,
            has_more_previous=window.get("has_more_previous", False),
            has_more_next=window.get("has_more_next", False),
            oldest_date=oldest_date,
            newest_date=newest_date,
            selected_subject=subject_code,
            selected_status=status,
        )
        return context


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    context_object_name = "exam"
    template_name = "exams/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        user = self.request.user

        # Milestone 12, Phase 10 - cross-navigation: covered Subjects/
        # Chapters/Lectures resolved by the shared `get_exam_coverage()`
        # (extracted in Milestone 15 so the exam reminder emails reuse
        # the exact same resolution instead of a second copy);
        # readiness and revision status reused wholesale from the
        # existing Milestone 5/9 functions rather than recalculated here.
        coverage = get_exam_coverage(exam)
        context["covered_lecture_rows"] = coverage["covered_lecture_rows"]

        readiness_row = next(
            (row for row in get_exam_readiness(user) if row["exam"].pk == exam.pk), None
        )
        exam_ready_codes = revision_service.get_exam_ready_lecture_codes(user)
        for row in context["covered_lecture_rows"]:
            row["exam_ready"] = row["code"] in exam_ready_codes

        context.update(
            covered_subjects=coverage["covered_subjects"],
            covered_chapters=coverage["covered_chapters"],
            readiness_row=readiness_row,
        )
        return context


class RoutineWeekView(LoginRequiredMixin, TemplateView):
    """Milestone 12: /routine/week/<n>/ - the canonical page for one
    "Routine Week" (Phase 4/6 - sequential relative to this dataset's
    own schedule, not the ISO calendar week of the year; see
    `timeline.get_routine_week()`/`get_routine_week_map()`)."""

    template_name = "routine/week_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_number = kwargs["week_number"]
        week = timeline.get_routine_week(week_number)
        if week is None:
            raise Http404("No such Routine Week.")

        lecture_codes = [lecture.lecture_code for lecture in week["lectures"]]
        user = self.request.user
        exam_ready_codes = revision_service.get_exam_ready_lecture_codes(user)
        lecture_rows = [
            {"lecture": lecture, "exam_ready": lecture.lecture_code in exam_ready_codes}
            for lecture in week["lectures"]
        ]

        context.update(
            week_number=week_number,
            lecture_rows=lecture_rows,
            total_weeks=week["total_weeks"],
            has_previous=week_number > 1,
            has_next=week_number < week["total_weeks"],
        )
        return context


class RoutineResourcesView(LoginRequiredMixin, TemplateView):
    """Milestone 14, Phase 1: the Routine Archive - a fully automatic,
    filesystem-backed viewer over `media/routines/*.pdf` (see
    `routines.services.archive`). Replaces Milestone 12's placeholder
    "nothing has been uploaded" page now that the archive is real.
    `?routine=<filename>` selects which entry the viewer shows; HTMX
    requests re-render only the viewer partial so switching routines
    never reloads the page."""

    template_name = "routine/resources.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["routine/partials/_resources_viewer.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        archive = archive_service.list_routines()
        requested = self.request.GET.get("routine", "")
        selected = next((entry for entry in archive if entry.filename == requested), None)
        if selected is None and archive:
            selected = archive[0]
        context.update(
            archive=archive,
            selected=selected,
            latest=archive[0] if archive else None,
        )
        return context


class RoutineArchiveFileView(LoginRequiredMixin, View):
    """Milestone 14, Phase 1: serves one routine PDF by filename.
    `resolve_routine_file()` is the only thing that turns `filename`
    into a filesystem path, and it rejects anything that isn't an
    exact `YYYY-MM.pdf` match before ever touching the filesystem - so
    this view can never be tricked into serving an arbitrary file
    (Security: "Reject path traversal", "Ignore every other file").
    `?download=1` serves as an attachment for the Download button;
    plain requests serve inline for the iframe viewer."""

    def get(self, request, filename):
        path = archive_service.resolve_routine_file(filename)
        if path is None:
            raise Http404("No such routine document.")
        as_attachment = request.GET.get("download") == "1"
        return FileResponse(
            open(path, "rb"), content_type="application/pdf",
            as_attachment=as_attachment, filename=filename,
        )


class _StaffOnlyMixin(UserPassesTestMixin):
    """Milestone 12, Phase 9: dataset management is administrative, not
    student-facing (students get Routine Resources instead - see
    `RoutineResourcesView`/`templates/base.html`'s nav). Reuses Django's
    existing `is_staff` flag (this project's only admin/user
    distinction since Milestone 1 - no custom roles were ever added,
    per the Database Model Contract's Version 1 Constraints) rather
    than introducing a new permission system. A non-staff user hitting
    these URLs directly gets a 403, not just a hidden nav link - the
    nav change alone would be security-by-obscurity."""

    def test_func(self):
        return self.request.user.is_staff


class DatasetHistoryView(_StaffOnlyMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10: /datasets/ - read-only dataset version + import
    history. No editing, no import triggered from here - this is
    strictly a viewer onto what `import_csv`/`rollback_dataset` have
    already done."""

    template_name = "datasets/history.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["datasets/partials/_history.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            active_version=DatasetVersion.objects.filter(is_active=True).first(),
            versions=DatasetVersion.objects.select_related("imported_by").all(),
            import_logs=ImportLog.objects.select_related("dataset_version", "user").all()[:50],
        )
        return context


class DatasetCompareView(_StaffOnlyMixin, LoginRequiredMixin, TemplateView):
    """Milestone 10: /datasets/compare/ - side-by-side comparison of
    the CSVs currently sitting in the project root against the
    current database state (the same "what would importing right now
    change?" question `import_csv --preview`/`compare_dataset` answer
    from the CLI - this page calls the exact same `compare_all()`).
    Read-only: no editing, no import triggered from here.
    """

    template_name = "datasets/compare.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["datasets/partials/_compare.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_filter = self.request.GET.get("entity", "")
        change_filter = self.request.GET.get("change", "")

        diff = compare_all(settings.BASE_DIR)
        duplicates = detect_duplicates(settings.BASE_DIR)

        sections = []
        for key, label, _fn in COMPARISON_SECTIONS:
            if entity_filter and entity_filter != key:
                continue
            section = dict(diff[key])
            if change_filter:
                section = {change_filter: section.get(change_filter, [])}
            sections.append({"key": key, "label": label, "data": section})

        entity_choices = [(key, label) for key, label, _fn in COMPARISON_SECTIONS]
        change_choices = [("added", "Added"), ("modified", "Modified"), ("removed", "Removed"), ("unchanged", "Unchanged")]
        context.update(
            sections=sections,
            routine_events=diff["routine_events"],
            duplicates=duplicates,
            has_duplicates=any(duplicates.values()),
            entity_choices=entity_choices,
            selected_entity=entity_filter,
            selected_change=change_filter,
            filter_fields=[
                {
                    "kind": "select", "name": "entity", "label": "Entity",
                    "options": [("", "All")] + entity_choices, "selected": entity_filter,
                },
                {
                    "kind": "select", "name": "change", "label": "Change Type",
                    "options": [("", "All")] + change_choices, "selected": change_filter,
                },
            ],
        )
        return context
