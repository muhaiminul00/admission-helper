"""Timeline navigation tests (Milestone 10.5): anchor resolution, event-
based windowing, week grouping, HTMX lazy loading, progress/readiness
integration, and the Routine/Exam Timeline views. Kept separate from
`routines/tests.py` (importer tests) and `routines/tests_dataset.py`
(dataset-management tests), matching this project's one-file-per-
feature test layout.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from lectures.models import LectureTopic
from progress.models import Progress
from progress.services import revision as revision_service
from routines.models import Exam, Lecture, Routine
from routines.services import timeline
from subjects.models import Subject

COMPLETE = dict(class_done=True, notes_done=True, revision_done=True, practice_done=True)


def _make_lecture(routine, subject, code, date, topic_count=1):
    lecture = Lecture.objects.create(
        routine=routine, lecture_code=code, subject=subject, title=code, lecture_date=date, day="Mon",
    )
    for i in range(topic_count):
        LectureTopic.objects.create(lecture=lecture, chapter=None, topic=f"{code} topic {i}", display_order=i)
    return lecture


class TimelineFixture(TestCase):
    """A hand-built, date-controlled fixture (relative to `today`, so
    the suite never depends on the wall-clock date it runs on) - richer
    than `build_sample_dataset()` in date coverage, since anchor-
    resolution tests need explicit past/today/future lectures."""

    def setUp(self):
        self.user = create_user()
        self.today = timezone.localdate()
        self.routine = Routine.objects.create(name="Timeline Test Routine", active=True)
        self.subject_p = Subject.objects.create(code="P", name="Physics", display_order=1)
        self.subject_c = Subject.objects.create(code="C", name="Chemistry", display_order=2)


class AnchorResolutionTests(TimelineFixture):
    def test_anchor_is_today_when_today_has_a_lecture(self):
        _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=3))
        _make_lecture(self.routine, self.subject_p, "P-02", self.today)
        _make_lecture(self.routine, self.subject_p, "P-03", self.today + timedelta(days=4))

        window = timeline.get_lecture_timeline()
        self.assertEqual(window["anchor"], self.today)

    def test_anchor_is_nearest_upcoming_when_today_is_before_schedule(self):
        _make_lecture(self.routine, self.subject_p, "P-01", self.today + timedelta(days=2))
        _make_lecture(self.routine, self.subject_p, "P-02", self.today + timedelta(days=9))

        window = timeline.get_lecture_timeline()
        self.assertEqual(window["anchor"], self.today + timedelta(days=2))

    def test_anchor_is_nearest_past_when_today_is_after_schedule(self):
        _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=10))
        _make_lecture(self.routine, self.subject_p, "P-02", self.today - timedelta(days=3))

        window = timeline.get_lecture_timeline()
        self.assertEqual(window["anchor"], self.today - timedelta(days=3))

    def test_anchor_defaults_to_today_when_nothing_exists(self):
        window = timeline.get_lecture_timeline()
        self.assertEqual(window["anchor"], self.today)
        self.assertEqual(window["events"], [])

    def test_exam_anchor_is_next_upcoming_exam(self):
        Exam.objects.create(
            routine=self.routine, exam_code="WE-01", exam_name="Past Exam",
            exam_type=Exam.ExamType.WEEKLY, exam_date=self.today - timedelta(days=5),
        )
        Exam.objects.create(
            routine=self.routine, exam_code="WE-02", exam_name="Next Exam",
            exam_type=Exam.ExamType.WEEKLY, exam_date=self.today + timedelta(days=6),
        )
        window = timeline.get_exam_timeline()
        self.assertEqual(window["anchor"], self.today + timedelta(days=6))


class EventBasedWindowingTests(TimelineFixture):
    """Confirms the window is event-count based, not calendar-day
    based: a date with many events still only counts as one "step"
    toward the budget, and no date is ever split across the boundary.
    """

    def test_window_never_splits_a_date(self):
        # One date with 3 lectures, right at the previous-window boundary.
        busy_date = self.today - timedelta(days=1)
        for i in range(3):
            _make_lecture(self.routine, self.subject_p, f"P-0{i}", busy_date)
        _make_lecture(self.routine, self.subject_p, "P-99", self.today + timedelta(days=1))

        window = timeline.get_lecture_timeline(previous_n=1, next_n=10)
        dates_before_anchor = [e.date for e in window["events"] if e.date < window["anchor"]]
        # All 3 same-date lectures included together, not truncated to 1.
        self.assertEqual(len(dates_before_anchor), 3)

    def test_empty_days_never_consume_window_budget(self):
        # Lectures on only 2 real dates, several empty calendar days apart -
        # the window should still show both dates worth of events.
        _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=20))
        _make_lecture(self.routine, self.subject_p, "P-02", self.today + timedelta(days=1))

        window = timeline.get_lecture_timeline(previous_n=5, next_n=5)
        codes = {e.code for e in window["events"]}
        self.assertEqual(codes, {"P-01", "P-02"})

    def test_has_more_previous_and_next_flags(self):
        for i in range(8):
            _make_lecture(self.routine, self.subject_p, f"P-past-{i}", self.today - timedelta(days=20 - i))
        for i in range(8):
            _make_lecture(self.routine, self.subject_p, f"P-future-{i}", self.today + timedelta(days=i + 1))

        window = timeline.get_lecture_timeline(previous_n=2, next_n=2)
        self.assertTrue(window["has_more_previous"])
        self.assertTrue(window["has_more_next"])

    def test_no_more_flags_when_schedule_is_small(self):
        _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=1))
        _make_lecture(self.routine, self.subject_p, "P-02", self.today + timedelta(days=1))

        window = timeline.get_lecture_timeline(previous_n=5, next_n=10)
        self.assertFalse(window["has_more_previous"])
        self.assertFalse(window["has_more_next"])


class DeterministicOrderingTests(TimelineFixture):
    """Milestone 12, Phase 2: same-date events must sort identically
    every time - without an explicit tie-breaker, the DB is free to
    return same-date rows in any order, which would make the anchor's
    contents (and which lecture appears "first" on a busy day) look
    random across repeated requests even though nothing changed."""

    def test_same_date_events_order_identically_across_repeated_calls(self):
        busy_date = self.today
        for i in range(5):
            _make_lecture(self.routine, self.subject_p, f"P-{i}", busy_date)

        first_call = [e.code for e in timeline.get_lecture_timeline()["events"]]
        second_call = [e.code for e in timeline.get_lecture_timeline()["events"]]
        third_call = [e.code for e in timeline.get_lecture_timeline()["events"]]
        self.assertEqual(first_call, second_call)
        self.assertEqual(second_call, third_call)

    def test_same_date_events_ordered_by_id_ascending(self):
        busy_date = self.today
        codes_in_creation_order = [f"P-{i}" for i in range(4)]
        for code in codes_in_creation_order:
            _make_lecture(self.routine, self.subject_p, code, busy_date)

        events = timeline.get_lecture_timeline()["events"]
        self.assertEqual([e.code for e in events], codes_in_creation_order)


class LazyLoadingTests(TimelineFixture):
    def test_before_cursor_loads_strictly_older_events_without_duplication(self):
        dates = [self.today - timedelta(days=n) for n in range(1, 6)]
        for i, d in enumerate(dates):
            _make_lecture(self.routine, self.subject_p, f"P-{i}", d)

        initial = timeline.get_lecture_timeline(previous_n=2, next_n=10)
        oldest, _ = timeline.window_bounds(initial["events"])

        older = timeline.get_lecture_timeline(previous_n=2, before=oldest)
        older_dates = {e.date for e in older["events"]}
        initial_dates = {e.date for e in initial["events"]}
        self.assertTrue(all(d < initial["anchor"] for d in older_dates))
        self.assertEqual(older_dates & initial_dates, set())

    def test_after_cursor_loads_strictly_newer_events_without_duplication(self):
        dates = [self.today + timedelta(days=n) for n in range(1, 6)]
        for i, d in enumerate(dates):
            _make_lecture(self.routine, self.subject_p, f"P-{i}", d)

        initial = timeline.get_lecture_timeline(previous_n=5, next_n=2)
        _, newest = timeline.window_bounds(initial["events"])

        newer = timeline.get_lecture_timeline(next_n=2, after=newest)
        newer_dates = {e.date for e in newer["events"]}
        initial_dates = {e.date for e in initial["events"]}
        self.assertEqual(newer_dates & initial_dates, set())


class WeekGroupingTests(TimelineFixture):
    def test_groups_by_iso_week_and_date(self):
        monday = self.today - timedelta(days=self.today.weekday())
        _make_lecture(self.routine, self.subject_p, "P-01", monday)
        _make_lecture(self.routine, self.subject_p, "P-02", monday + timedelta(days=1))
        _make_lecture(self.routine, self.subject_p, "P-03", monday + timedelta(days=8))  # next iso week

        window = timeline.get_lecture_timeline(previous_n=5, next_n=5)
        weeks = timeline.group_by_week(window["events"])
        self.assertEqual(len(weeks), 2)
        self.assertEqual(len(weeks[0]["days"]), 2)
        self.assertEqual(len(weeks[1]["days"]), 1)


class ProgressIntegrationTests(TimelineFixture):
    def test_attach_lecture_progress_is_bulk_and_correct(self):
        lecture = _make_lecture(self.routine, self.subject_p, "P-01", self.today, topic_count=2)
        Progress.objects.create(user=self.user, lecture_topic=lecture.topics.first(), **COMPLETE)

        window = timeline.get_lecture_timeline()
        events = timeline.attach_lecture_progress(window["events"], self.user)
        event = next(e for e in events if e.code == "P-01")
        self.assertEqual(event.extra["completed_topics"], 1)
        self.assertEqual(event.extra["total_topics"], 2)
        self.assertEqual(event.extra["percentage"], 50.0)

    def test_progress_is_isolated_per_user(self):
        lecture = _make_lecture(self.routine, self.subject_p, "P-01", self.today, topic_count=1)
        other_user = create_user(username="other_student")
        Progress.objects.create(user=other_user, lecture_topic=lecture.topics.first(), **COMPLETE)

        window = timeline.get_lecture_timeline()
        events = timeline.attach_lecture_progress(window["events"], self.user)
        event = next(e for e in events if e.code == "P-01")
        self.assertEqual(event.extra["completed_topics"], 0)

    def test_completed_filter_reuses_analytics_completion_definition(self):
        done = _make_lecture(self.routine, self.subject_p, "P-done", self.today - timedelta(days=1))
        Progress.objects.create(user=self.user, lecture_topic=done.topics.first(), **COMPLETE)
        _make_lecture(self.routine, self.subject_p, "P-todo", self.today + timedelta(days=1))

        completed_window = timeline.get_lecture_timeline(completed=True, user=self.user, previous_n=5, next_n=5)
        incomplete_window = timeline.get_lecture_timeline(completed=False, user=self.user, previous_n=5, next_n=5)
        self.assertEqual({e.code for e in completed_window["events"]}, {"P-done"})
        self.assertEqual({e.code for e in incomplete_window["events"]}, {"P-todo"})


class RevisionStatusIntegrationTests(TimelineFixture):
    def test_attach_revision_status_bulk_and_correct(self):
        lecture = _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=2))
        topic = lecture.topics.first()
        Progress.objects.create(user=self.user, lecture_topic=topic, **COMPLETE)
        revision_service.ensure_revision_schedule(self.user, lecture)

        window = timeline.get_lecture_timeline()
        events = timeline.attach_revision_status(window["events"], self.user)
        event = next(e for e in events if e.code == "P-01")
        self.assertEqual(event.extra["pending_revisions"], 3)
        self.assertFalse(event.extra["exam_ready"])


class ExamReadinessIntegrationTests(TimelineFixture):
    def test_attach_exam_readiness_reuses_analytics_and_adds_countdown(self):
        lecture = _make_lecture(self.routine, self.subject_p, "P-01", self.today - timedelta(days=5), topic_count=2)
        Progress.objects.create(user=self.user, lecture_topic=lecture.topics.first(), **COMPLETE)
        Exam.objects.create(
            routine=self.routine, exam_code="WE-01", exam_name="Weekly Exam 1",
            exam_type=Exam.ExamType.WEEKLY, exam_date=self.today + timedelta(days=5),
            covered_lectures=["P-01"],
        )

        window = timeline.get_exam_timeline()
        events = timeline.attach_exam_readiness(window["events"], self.user)
        event = events[0]
        self.assertEqual(event.extra["days_remaining"], 5)
        self.assertEqual(event.extra["percentage"], 50.0)
        self.assertIn("readiness_label", event.extra)


class RoutineTimelineViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("routine-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "today-marker")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("routine-list"), HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "timeline-list")

    def test_subject_filter(self):
        response = self.client.get(reverse("routine-list"), {"subject": "P"})
        events = [e for week in response.context["weeks"] for day in week["days"] for e in day["events"]]
        self.assertTrue(all(e.subject.code == "P" for e in events))

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("routine-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_query_count_within_budget(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("routine-list"))
        self.assertLessEqual(len(ctx.captured_queries), 10)

    def test_window_endpoint_returns_partial(self):
        response = self.client.get(
            reverse("routine-timeline-window"), {"direction": "next", "after": str(self.data["today"])}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")

    def test_window_endpoint_query_count_within_budget(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(
                reverse("routine-timeline-window"), {"direction": "next", "after": str(self.data["today"])}
            )
        self.assertLessEqual(len(ctx.captured_queries), 10)


class ExamTimelineViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("exam-timeline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("exam-timeline"), HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "<html")

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("exam-timeline"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_query_count_within_budget(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("exam-timeline"))
        self.assertLessEqual(len(ctx.captured_queries), 10)

    def test_status_filter_uses_readiness_label(self):
        response = self.client.get(reverse("exam-timeline"), {"status": "High Risk"})
        events = [e for week in response.context["weeks"] for day in week["days"] for e in day["events"]]
        self.assertTrue(all(e.extra["readiness_label"] == "High Risk" for e in events))


class RevisionTimelineUXTests(TestCase):
    """The Revision Queue already had no pagination (Milestone 9) - this
    only verifies the Milestone 10.5 additions: a Today anchor marker
    and the shared Jump-to-Today control."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_today_marker_and_jump_fab_present(self):
        response = self.client.get(reverse("revision-queue"))
        self.assertContains(response, "today-marker")
        self.assertContains(response, "jump-today-fab")
