from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from core.test_utils import build_sample_dataset, create_user


class DashboardViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_renders_with_stats_and_widgets(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_topics"], 5)
        self.assertEqual(response.context["completed_lectures"], 1)
        self.assertContains(response, "Refresh")

    def test_empty_database_does_not_crash(self):
        from lectures.models import LectureTopic
        from routines.models import Lecture, Exam
        from subjects.models import Subject, Chapter

        LectureTopic.objects.all().delete()
        Lecture.objects.all().delete()
        Exam.objects.all().delete()
        Chapter.objects.all().delete()
        Subject.objects.all().delete()

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No upcoming exam")

    def test_query_count_is_small_and_fixed(self):
        # Milestone 8 added 6 new "study advisor" widgets (budget raised
        # 20->30) and Milestone 9 added a Revision section
        # (get_revision_dashboard_stats() - a handful of small .count()
        # queries plus the exam-ready lookup; budget raised 30->40) -
        # each a real, bounded addition, not a regression. What matters
        # (and is what this test actually guards) is that the count
        # stays FIXED regardless of how much data exists - re-asserted
        # below against a larger dataset.
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("dashboard"))
        self.assertLessEqual(len(ctx.captured_queries), 40)

    def test_query_count_does_not_scale_with_extra_data(self):
        from lectures.models import LectureTopic

        with CaptureQueriesContext(connection) as ctx_before:
            self.client.get(reverse("dashboard"))
        before = len(ctx_before.captured_queries)

        # Add a lot more topics under the same lecture - if any dashboard
        # query scaled per-row instead of using annotate()/aggregate(),
        # this would increase the query count.
        lecture = self.data["lectures"]["p01"]
        chapter = self.data["chapters"]["p11"]
        for i in range(50):
            LectureTopic.objects.create(
                lecture=lecture, chapter=chapter, topic=f"Extra topic {i}", display_order=100 + i
            )

        with CaptureQueriesContext(connection) as ctx_after:
            self.client.get(reverse("dashboard"))
        self.assertEqual(len(ctx_after.captured_queries), before)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_statistics_are_user_specific(self):
        other = create_user("student2")
        self.client.force_login(other)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["completed_topics"], 0)


class DashboardWidgetsViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_htmx_refresh_returns_partial(self):
        response = self.client.get(reverse("dashboard-widgets"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")
        self.assertContains(response, "Overall Completion")

    def test_reflects_updated_progress_after_refresh(self):
        from progress.models import Progress

        topic = self.data["topics"]["t4"]
        Progress.objects.create(
            user=self.data["user"], lecture_topic=topic, class_done=True, notes_done=True,
            revision_done=True, practice_done=True,
        )
        response = self.client.get(reverse("dashboard-widgets"))
        self.assertEqual(response.context["completed_topics"], 3)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard-widgets"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
