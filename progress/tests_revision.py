"""Milestone 9 - Revision System tests.

Kept in a separate module (`tests_revision.py`, not appended to the
already-large `progress/tests.py`) - Django's default test discovery
(`DiscoverRunner`, pattern `test*.py`) picks this up automatically
alongside `tests.py`, no settings change needed.
"""

from datetime import date, timedelta

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from progress.models import Progress, RevisionHistory, RevisionSchedule
from progress.services import revision as rev


class IsLectureCompletedTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_lecture_with_all_topics_complete_is_completed(self):
        # P-02 has a single topic (t3), fully completed in the fixture.
        self.assertTrue(rev.is_lecture_completed(self.user, self.data["lectures"]["p02"]))

    def test_lecture_with_partial_topic_is_not_completed(self):
        # P-01 has 2 topics: t1 complete, t2 only partially done.
        self.assertFalse(rev.is_lecture_completed(self.user, self.data["lectures"]["p01"]))

    def test_lecture_with_no_progress_at_all_is_not_completed(self):
        self.assertFalse(rev.is_lecture_completed(self.user, self.data["lectures"]["p06"]))

    def test_second_user_sees_lecture_as_not_completed(self):
        other = create_user("student2")
        self.assertFalse(rev.is_lecture_completed(other, self.data["lectures"]["p02"]))


class EnsureRevisionScheduleTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]  # fully completed in the fixture

    def test_creates_three_stages_for_a_completed_lecture(self):
        created = rev.ensure_revision_schedule(self.user, self.lecture)
        self.assertTrue(created)
        schedules = RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture)
        self.assertEqual(schedules.count(), 3)
        self.assertEqual(
            set(schedules.values_list("revision_level", flat=True)),
            {1, 2, 3},
        )
        self.assertTrue(all(s.status == RevisionSchedule.Status.PENDING for s in schedules))

    def test_due_date_calculation(self):
        completion_date = date(2026, 1, 1)
        rev.ensure_revision_schedule(self.user, self.lecture, completion_date=completion_date)
        due_dates = dict(
            RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture)
            .values_list("revision_level", "due_date")
        )
        self.assertEqual(due_dates[1], date(2026, 1, 2))   # +1 day
        self.assertEqual(due_dates[2], date(2026, 1, 5))   # +1 +3 days
        self.assertEqual(due_dates[3], date(2026, 1, 12))  # +1 +3 +7 days

    def test_does_not_create_schedule_for_incomplete_lecture(self):
        incomplete_lecture = self.data["lectures"]["p01"]
        created = rev.ensure_revision_schedule(self.user, incomplete_lecture)
        self.assertFalse(created)
        self.assertFalse(
            RevisionSchedule.objects.filter(user=self.user, lecture=incomplete_lecture).exists()
        )

    def test_duplicate_prevention_on_second_call(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        created_again = rev.ensure_revision_schedule(self.user, self.lecture)
        self.assertFalse(created_again)
        self.assertEqual(
            RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture).count(), 3
        )

    def test_schedules_are_per_user_not_shared(self):
        other = create_user("student2")
        rev.ensure_revision_schedule(self.user, self.lecture)
        # other user hasn't completed the lecture themselves - no schedule.
        created = rev.ensure_revision_schedule(other, self.lecture)
        self.assertFalse(created)
        self.assertFalse(
            RevisionSchedule.objects.filter(user=other, lecture=self.lecture).exists()
        )


class ProgressToggleCreatesScheduleTests(TestCase):
    """Regression-style integration test: completing a lecture via the
    real HTMX toggle endpoint (not calling the service directly) must
    trigger schedule creation - this is the actual trigger path used
    in production, per Milestone 9's "Automatic Schedule Creation"."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.client.force_login(self.user)

    def test_completing_last_field_creates_schedule(self):
        topic = self.data["topics"]["t2"]  # P-01's second topic, PARTIAL (class_done=True only)
        lecture = self.data["lectures"]["p01"]
        self.assertFalse(RevisionSchedule.objects.filter(user=self.user, lecture=lecture).exists())

        for field in ("notes_done", "revision_done", "practice_done"):
            self.client.post(reverse("progress-toggle", args=[topic.id, field]))

        self.assertTrue(rev.is_lecture_completed(self.user, lecture))
        self.assertEqual(
            RevisionSchedule.objects.filter(user=self.user, lecture=lecture).count(), 3
        )

    def test_toggling_an_already_completed_lecture_does_not_duplicate(self):
        lecture = self.data["lectures"]["p02"]
        topic = self.data["topics"]["t3"]
        rev.ensure_revision_schedule(self.user, lecture)  # pre-existing schedule

        # Toggle class_done off then back on - lecture briefly incomplete,
        # then complete again; must not create a second schedule set.
        self.client.post(reverse("progress-toggle", args=[topic.id, "class_done"]))
        self.client.post(reverse("progress-toggle", args=[topic.id, "class_done"]))

        self.assertEqual(
            RevisionSchedule.objects.filter(user=self.user, lecture=lecture).count(), 3
        )


class ExamReadyTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.schedules = list(
            RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture)
            .order_by("revision_level")
        )

    def test_not_exam_ready_before_any_revision_completed(self):
        self.assertFalse(rev.is_lecture_exam_ready(self.user, self.lecture))
        self.assertEqual(rev.get_exam_ready_lecture_codes(self.user), set())

    def test_not_exam_ready_with_only_some_revisions_completed(self):
        rev.complete_revision(self.user, self.schedules[0].id)
        rev.complete_revision(self.user, self.schedules[1].id)
        self.assertFalse(rev.is_lecture_exam_ready(self.user, self.lecture))

    def test_exam_ready_once_all_three_revisions_completed(self):
        for s in self.schedules:
            rev.complete_revision(self.user, s.id)
        self.assertTrue(rev.is_lecture_exam_ready(self.user, self.lecture))
        self.assertEqual(rev.get_exam_ready_lecture_codes(self.user), {"P-02"})

    def test_exam_ready_is_isolated_per_user(self):
        other = create_user("student2")
        for s in self.schedules:
            rev.complete_revision(self.user, s.id)
        self.assertFalse(rev.is_lecture_exam_ready(other, self.lecture))
        self.assertEqual(rev.get_exam_ready_lecture_codes(other), set())


class RevisionQueueServiceTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]

    def test_buckets_by_due_date_and_status(self):
        today = timezone.localdate()
        rev.ensure_revision_schedule(self.user, self.lecture, completion_date=today - timedelta(days=20))
        schedules = list(
            RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture).order_by("revision_level")
        )
        # completion - 20 days -> level1 due -19d (overdue), level2 due -16d (overdue), level3 due -9d (overdue)
        # force one into "due today" and one into "upcoming" for a clean bucket test instead:
        schedules[0].due_date = today
        schedules[0].save()
        schedules[1].due_date = today + timedelta(days=5)
        schedules[1].save()
        # schedules[2] stays overdue

        queue = rev.get_revision_queue(self.user)
        self.assertIn(schedules[0], queue["due_today"])
        self.assertIn(schedules[1], queue["upcoming"])
        self.assertIn(schedules[2], queue["overdue"])

    def test_completed_bucket(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        rev.complete_revision(self.user, schedule.id)

        queue = rev.get_revision_queue(self.user)
        self.assertIn(schedule, queue["completed"])
        self.assertNotIn(schedule, queue["overdue"])
        self.assertNotIn(schedule, queue["due_today"])
        self.assertNotIn(schedule, queue["upcoming"])

    def test_filter_by_subject(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        queue = rev.get_revision_queue(self.user, subject_code="P")
        self.assertTrue(len(queue["all"]) > 0)
        queue_other = rev.get_revision_queue(self.user, subject_code="E")
        self.assertEqual(queue_other["all"], [])

    def test_filter_by_status(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        rev.complete_revision(self.user, schedule.id)

        completed_only = rev.get_revision_queue(self.user, status="completed")
        self.assertEqual(len(completed_only["all"]), 1)
        pending_only = rev.get_revision_queue(self.user, status="pending")
        self.assertEqual(len(pending_only["all"]), 2)

    def test_filter_by_level(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        level2_only = rev.get_revision_queue(self.user, level=2)
        self.assertEqual(len(level2_only["all"]), 1)
        self.assertEqual(level2_only["all"][0].revision_level, 2)

    def test_isolated_per_user(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        other = create_user("student2")
        queue_other = rev.get_revision_queue(other)
        self.assertEqual(queue_other["all"], [])

    def test_query_count_is_fixed(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        with CaptureQueriesContext(connection) as ctx:
            rev.get_revision_queue(self.user)
        self.assertEqual(len(ctx.captured_queries), 1)


class CompleteRevisionTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()

    def test_completing_updates_status_and_completed_at(self):
        result = rev.complete_revision(self.user, self.schedule.id)
        self.assertEqual(result.status, RevisionSchedule.Status.COMPLETED)
        self.assertIsNotNone(result.completed_at)

    def test_completing_creates_history_entry(self):
        rev.complete_revision(self.user, self.schedule.id, notes="Reviewed vectors again")
        history = RevisionHistory.objects.filter(revision_schedule=self.schedule)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().notes, "Reviewed vectors again")

    def test_completing_again_is_a_no_op_not_a_second_history_entry(self):
        rev.complete_revision(self.user, self.schedule.id)
        rev.complete_revision(self.user, self.schedule.id)
        self.assertEqual(RevisionHistory.objects.filter(revision_schedule=self.schedule).count(), 1)

    def test_completed_revision_is_not_deleted(self):
        rev.complete_revision(self.user, self.schedule.id)
        self.assertTrue(RevisionSchedule.objects.filter(pk=self.schedule.id).exists())

    def test_cannot_complete_another_users_schedule(self):
        other = create_user("student2")
        result = rev.complete_revision(other, self.schedule.id)
        self.assertIsNone(result)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.status, RevisionSchedule.Status.PENDING)

    def test_unknown_schedule_id_returns_none(self):
        self.assertIsNone(rev.complete_revision(self.user, 999999))


class RevisionDashboardStatsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]

    def test_stats_with_no_revisions(self):
        stats = rev.get_revision_dashboard_stats(self.user)
        self.assertEqual(stats["revision_due_today"], 0)
        self.assertEqual(stats["revision_overdue"], 0)
        self.assertEqual(stats["revision_completion_percentage"], 0.0)
        self.assertEqual(stats["exam_ready_count"], 0)

    def test_stats_reflect_due_today_overdue_upcoming(self):
        today = timezone.localdate()
        rev.ensure_revision_schedule(self.user, self.lecture, completion_date=today - timedelta(days=20))
        stats = rev.get_revision_dashboard_stats(self.user)
        self.assertEqual(stats["revision_overdue"], 3)  # all 3 stages due in the past

    def test_stats_reflect_completed_this_week(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        rev.complete_revision(self.user, schedule.id)
        stats = rev.get_revision_dashboard_stats(self.user)
        self.assertEqual(stats["revision_completed_this_week"], 1)
        self.assertAlmostEqual(stats["revision_completion_percentage"], 33.3, places=1)

    def test_stats_isolated_per_user(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        other = create_user("student2")
        stats = rev.get_revision_dashboard_stats(other)
        self.assertEqual(stats["revision_overdue"], 0)
        self.assertEqual(stats["revision_completion_percentage"], 0.0)


class RevisionAnalyticsExtrasTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]

    def test_average_revision_delay_negative_when_completed_early(self):
        rev.ensure_revision_schedule(
            self.user, self.lecture, completion_date=timezone.localdate() + timedelta(days=29)
        )
        schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        rev.complete_revision(self.user, schedule.id)
        delay = rev.get_average_revision_delay(self.user)
        self.assertLess(delay, 0)

    def test_average_revision_delay_zero_when_nothing_completed(self):
        self.assertEqual(rev.get_average_revision_delay(self.user), 0.0)

    def test_revision_workload_and_upcoming_load(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.assertEqual(rev.get_revision_workload(self.user), 3)
        self.assertGreaterEqual(rev.get_upcoming_revision_load(self.user, days=30), 1)

    def test_overdue_revision_count(self):
        today = timezone.localdate()
        rev.ensure_revision_schedule(self.user, self.lecture, completion_date=today - timedelta(days=20))
        self.assertEqual(rev.get_overdue_revision_count(self.user), 3)

    def test_revision_streak_single_day(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        for s in RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture):
            rev.complete_revision(self.user, s.id)
        streak = rev.get_revision_streak(self.user)
        self.assertEqual(streak["current_streak"], 1)
        self.assertEqual(streak["longest_streak"], 1)

    def test_revision_streak_zero_when_nothing_completed(self):
        streak = rev.get_revision_streak(self.user)
        self.assertEqual(streak, {"current_streak": 0, "longest_streak": 0})


class RevisionQueueViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.client.force_login(self.user)

    def test_full_page_response(self):
        response = self.client.get(reverse("revision-queue"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "P-02")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("revision-queue"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")

    def test_filter_by_subject(self):
        response = self.client.get(reverse("revision-queue"), {"subject": "E"})
        self.assertEqual(response.context["all"], [])

    def test_filter_by_status(self):
        response = self.client.get(reverse("revision-queue"), {"status": "completed"})
        self.assertEqual(response.context["all"], [])

    def test_filter_by_level(self):
        response = self.client.get(reverse("revision-queue"), {"level": "2"})
        self.assertEqual(len(response.context["all"]), 1)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("revision-queue"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_query_count_within_budget(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("revision-queue"))
        self.assertLessEqual(len(ctx.captured_queries), 15)


class RevisionDetailViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        self.client.force_login(self.user)

    def test_full_page_response_shows_topics_and_history(self):
        response = self.client.get(reverse("revision-detail", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Electricity intro")
        self.assertContains(response, "First Revision")

    def test_unknown_schedule_404s(self):
        response = self.client.get(reverse("revision-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_view_another_users_schedule(self):
        other = create_user("student2")
        self.client.force_login(other)
        response = self.client.get(reverse("revision-detail", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("revision-detail", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class RevisionCompleteViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        rev.ensure_revision_schedule(self.user, self.lecture)
        self.schedule = RevisionSchedule.objects.filter(
            user=self.user, lecture=self.lecture, revision_level=1
        ).get()
        self.client.force_login(self.user)

    def test_marks_complete_and_returns_partial(self):
        response = self.client.post(reverse("revision-complete", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.status, RevisionSchedule.Status.COMPLETED)

    def test_get_not_allowed(self):
        response = self.client.get(reverse("revision-complete", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 405)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.post(reverse("revision-complete", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_cannot_complete_another_users_schedule_via_view(self):
        other = create_user("student2")
        self.client.force_login(other)
        response = self.client.post(reverse("revision-complete", args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 404)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.status, RevisionSchedule.Status.PENDING)


class LectureDetailRevisionIntegrationTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        self.client.force_login(self.user)

    def test_lecture_page_shows_revision_schedule_once_created(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        response = self.client.get(reverse("lecture-detail", args=[self.lecture.lecture_code]))
        self.assertContains(response, "Revision Schedule")
        self.assertContains(response, "First Revision")

    def test_lecture_page_shows_exam_ready_badge_once_all_revisions_done(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        for s in RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture):
            rev.complete_revision(self.user, s.id)
        response = self.client.get(reverse("lecture-detail", args=[self.lecture.lecture_code]))
        self.assertTrue(response.context["is_exam_ready"])
        self.assertContains(response, "Exam Ready")

    def test_lecture_page_no_revision_section_before_completion(self):
        incomplete_lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[incomplete_lecture.lecture_code]))
        self.assertNotContains(response, "Revision Schedule")


class DashboardRevisionIntegrationTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]
        self.client.force_login(self.user)

    def test_dashboard_shows_revision_section(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revision")
        self.assertEqual(response.context["revision_completion_percentage"], 0.0)

    def test_dashboard_widgets_endpoint_reflects_completed_revision(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        schedule = RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture, revision_level=1).get()
        rev.complete_revision(self.user, schedule.id)

        response = self.client.get(reverse("dashboard-widgets"))
        self.assertAlmostEqual(response.context["revision_completion_percentage"], 33.3, places=1)

    def test_dashboard_is_isolated_per_user(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        other = create_user("student2")
        self.client.force_login(other)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["revision_overdue"], 0)


class ExamAnalyticsRevisionIntegrationTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]  # covered by WE-01
        self.client.force_login(self.user)

    def test_exams_page_shows_exam_ready_lecture_count(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        for s in RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture):
            rev.complete_revision(self.user, s.id)

        response = self.client.get(reverse("analytics-exams"))
        rows = {row["exam"].exam_code: row for row in response.context["rows"]}
        self.assertEqual(rows["WE-01"]["exam_ready_lecture_count"], 1)

    def test_insights_page_shows_revision_insights(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        response = self.client.get(reverse("analytics-insights"))
        self.assertContains(response, "Revision Insights")
        self.assertIn("revision_insights", response.context)
        self.assertEqual(response.context["revision_insights"]["workload"], 3)

    def test_insights_exam_ready_count_matches_revision_service(self):
        rev.ensure_revision_schedule(self.user, self.lecture)
        for s in RevisionSchedule.objects.filter(user=self.user, lecture=self.lecture):
            rev.complete_revision(self.user, s.id)
        response = self.client.get(reverse("analytics-insights"))
        rows = {row["exam"].exam_code: row for row in response.context["exam_insights"]}
        self.assertEqual(rows["WE-01"]["exam_ready_lecture_count"], 1)
