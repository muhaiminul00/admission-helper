from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.test_utils import build_sample_dataset, create_user


class SubjectDetailViewTests(TestCase):
    """Milestone 12: /subjects/<pk>/ - the canonical Subject page."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_renders_with_reused_analytics_numbers(self):
        subject = self.data["subject_p"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Physics")
        # 2/4 topics complete for Subject P: P-01 (t1 done, t2 partial),
        # P-02 (t3 done), P-06 (t4 untouched) = 4 topics, 2 complete.
        self.assertEqual(response.context["subject_row"]["completed"], 2)
        self.assertEqual(response.context["subject_row"]["total"], 4)

    def test_links_to_chapter_and_lecture_canonical_pages(self):
        subject = self.data["subject_p"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        chapter = self.data["chapters"]["p11"]
        lecture = self.data["lectures"]["p01"]
        self.assertContains(response, reverse("chapter-detail", args=[chapter.pk]))
        self.assertContains(response, reverse("lecture-detail", args=[lecture.lecture_code]))

    def test_covering_exams_listed(self):
        subject = self.data["subject_p"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        exam = self.data["exams"]["we01"]
        self.assertContains(response, reverse("exam-detail", args=[exam.pk]))

    def test_subject_with_no_chapters_does_not_crash(self):
        # Subject E is deliberately chapter-less (self-study) in the fixture.
        subject = self.data["subject_e"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        subject = self.data["subject_p"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_progress_is_isolated_per_user(self):
        other_user = create_user(username="other_student")
        self.client.force_login(other_user)
        subject = self.data["subject_p"]
        response = self.client.get(reverse("subject-detail", args=[subject.pk]))
        self.assertEqual(response.context["subject_row"]["completed"], 0)

    def test_query_count_is_small_and_fixed(self):
        subject = self.data["subject_p"]
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("subject-detail", args=[subject.pk]))
        self.assertLessEqual(len(ctx.captured_queries), 12)


class ChapterDetailViewTests(TestCase):
    """Milestone 12: /chapters/<pk>/ - the canonical Chapter page."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_renders_with_topics_and_completion(self):
        chapter = self.data["chapters"]["p11"]
        response = self.client.get(reverse("chapter-detail", args=[chapter.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vector")
        self.assertContains(response, "Vectors intro")

    def test_links_to_lecture_and_subject(self):
        chapter = self.data["chapters"]["p11"]
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("chapter-detail", args=[chapter.pk]))
        self.assertContains(response, reverse("lecture-detail", args=[lecture.lecture_code]))

    def test_topic_status_reflects_progress(self):
        # topic1 (Vectors intro, chapter p11) is fully completed in the fixture.
        chapter = self.data["chapters"]["p11"]
        response = self.client.get(reverse("chapter-detail", args=[chapter.pk]))
        self.assertContains(response, "Done")

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        chapter = self.data["chapters"]["p11"]
        response = self.client.get(reverse("chapter-detail", args=[chapter.pk]))
        self.assertEqual(response.status_code, 302)

    def test_query_count_is_small_and_fixed(self):
        chapter = self.data["chapters"]["p11"]
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("chapter-detail", args=[chapter.pk]))
        self.assertLessEqual(len(ctx.captured_queries), 12)
