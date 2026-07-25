from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from core.test_utils import build_sample_dataset, create_user
from progress.models import Progress


class LectureDetailViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_dated_lecture_renders(self):
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vectors intro")

    def test_undated_lecture_shows_not_scheduled_fallback(self):
        lecture = self.data["lectures"]["e01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Not scheduled")

    def test_unknown_lecture_code_404s(self):
        response = self.client.get(reverse("lecture-detail", args=["DOES-NOT-EXIST"]))
        self.assertEqual(response.status_code, 404)

    def test_distinct_chapters_deduplicated_and_none_skipped(self):
        lecture = self.data["lectures"]["p01"]  # 2 topics, 2 different chapters
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertEqual(len(response.context["chapters"]), 2)

    def test_chapterless_lecture_has_no_chapters_listed(self):
        lecture = self.data["lectures"]["e01"]  # topic has chapter=None
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertEqual(response.context["chapters"], [])

    def test_query_count_is_small_and_fixed(self):
        # Milestone 9 added the revision_schedules fetch and
        # is_lecture_exam_ready() (a completion check + a revision-level
        # lookup), both scoped to this one lecture - budget raised 6->12
        # to reflect that real, bounded addition (not a regression; see
        # PROJECT_PROGRESS.md's Query Count Summary).
        lecture = self.data["lectures"]["p01"]
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertLessEqual(len(ctx.captured_queries), 12)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_only_current_users_progress_is_shown(self):
        other = create_user("student2")
        topic1 = self.data["topics"]["t1"]  # self.data["user"]'s progress is COMPLETE
        Progress.objects.create(
            user=other, lecture_topic=topic1,
            class_done=False, notes_done=False, revision_done=False, practice_done=False,
        )
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        topics = {t.id: t for t in response.context["topics"]}
        self.assertTrue(topics[topic1.id].progress_obj.class_done)


class LectureDetailCrossNavigationTests(TestCase):
    """Milestone 12, Phase 10: Subject/Chapter/Previous-Next-Lecture/
    Upcoming-Exam links, all derived from data the view already had
    (no new calculations)."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_subject_link_present(self):
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertContains(response, reverse("subject-detail", args=[self.data["subject_p"].pk]))

    def test_chapter_links_present(self):
        lecture = self.data["lectures"]["p01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        chapter = self.data["chapters"]["p11"]
        self.assertContains(response, reverse("chapter-detail", args=[chapter.pk]))

    def test_previous_and_next_lecture_scoped_to_same_subject(self):
        # P-01 (today+1) and P-02 (today+8) are both Subject P, dated -
        # P-01 has no previous (nothing dated earlier in Subject P),
        # P-02's previous should be P-01.
        p01 = self.data["lectures"]["p01"]
        p02 = self.data["lectures"]["p02"]
        response = self.client.get(reverse("lecture-detail", args=[p02.lecture_code]))
        self.assertEqual(response.context["previous_lecture"], p01)
        self.assertIsNone(response.context["next_lecture"])

    def test_undated_lecture_has_no_previous_next(self):
        lecture = self.data["lectures"]["e01"]
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        self.assertIsNone(response.context["previous_lecture"])
        self.assertIsNone(response.context["next_lecture"])

    def test_covering_exam_listed_and_linked(self):
        lecture = self.data["lectures"]["p01"]  # covered by exam WE-01
        response = self.client.get(reverse("lecture-detail", args=[lecture.lecture_code]))
        exam = self.data["exams"]["we01"]
        self.assertIn(exam, response.context["covering_exams"])
        self.assertContains(response, reverse("exam-detail", args=[exam.pk]))
