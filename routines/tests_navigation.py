"""Navigation & Study Workspace tests (Milestone 12): Routine Week
canonical page, anchor determinism, admin-vs-student dataset
permissions, and Exam Detail cross-navigation. Kept separate from
`routines/tests_timeline.py` (Milestone 10.5's windowing/anchor tests)
and `routines/tests_dataset.py`, matching this project's one-file-per-
feature test layout.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from lectures.models import LectureTopic
from routines.models import Exam, Lecture, Routine
from routines.services import timeline
from subjects.models import Subject


def _make_lecture(routine, subject, code, date, topic_count=1, chapter=None):
    lecture = Lecture.objects.create(
        routine=routine, lecture_code=code, subject=subject, title=code, lecture_date=date, day="Mon",
    )
    for i in range(topic_count):
        LectureTopic.objects.create(lecture=lecture, chapter=chapter, topic=f"{code} topic {i}", display_order=i)
    return lecture


class RoutineWeekNumberingTests(TestCase):
    """Milestone 12, Phase 6: "Routine Week N" is sequential relative to
    this dataset's own schedule, never the ISO calendar week of the
    year - routine.csv has no week-number column at all."""

    def setUp(self):
        self.user = create_user()
        self.today = timezone.localdate()
        self.routine = Routine.objects.create(name="Nav Test Routine", active=True)
        self.subject = Subject.objects.create(code="P", name="Physics", display_order=1)

    def test_weeks_numbered_sequentially_and_span_every_week_in_range(self):
        # Milestone 13, Phase 1: the map is continuous across the whole
        # span (including weeks with no lecture in them), not sparse -
        # this is what lets an exam date in an otherwise lecture-free
        # week still resolve to a number.
        monday_1 = self.today - timedelta(days=self.today.weekday())
        _make_lecture(self.routine, self.subject, "P-01", monday_1)
        _make_lecture(self.routine, self.subject, "P-02", monday_1 + timedelta(days=14))  # 2 ISO weeks later
        _make_lecture(self.routine, self.subject, "P-03", monday_1 + timedelta(days=28))  # 4 ISO weeks later

        week_map = timeline.get_routine_week_map()
        self.assertEqual(len(week_map), 5)  # weeks 0,1,2,3,4 relative to monday_1
        self.assertEqual(sorted(week_map.values()), [1, 2, 3, 4, 5])
        # The chronologically-first week must be numbered 1, regardless
        # of what its real ISO calendar week number is.
        first_key = monday_1.isocalendar()[:2]
        self.assertEqual(week_map[first_key], 1)

    def test_get_routine_week_returns_correct_lectures(self):
        monday_1 = self.today - timedelta(days=self.today.weekday())
        lecture1 = _make_lecture(self.routine, self.subject, "P-01", monday_1)
        _make_lecture(self.routine, self.subject, "P-02", monday_1 + timedelta(days=14))

        week = timeline.get_routine_week(1)
        self.assertEqual([lecture.lecture_code for lecture in week["lectures"]], [lecture1.lecture_code])
        self.assertEqual(week["total_weeks"], 3)  # week 1 (P-01), week 2 (empty), week 3 (P-02)

    def test_empty_week_between_lectures_has_no_lectures_but_is_a_valid_week(self):
        monday_1 = self.today - timedelta(days=self.today.weekday())
        _make_lecture(self.routine, self.subject, "P-01", monday_1)
        _make_lecture(self.routine, self.subject, "P-02", monday_1 + timedelta(days=14))

        week = timeline.get_routine_week(2)
        self.assertIsNotNone(week)
        self.assertEqual(week["lectures"], [])

    def test_get_routine_week_returns_none_for_unknown_week(self):
        _make_lecture(self.routine, self.subject, "P-01", self.today)
        self.assertIsNone(timeline.get_routine_week(99))

    def test_multiple_lectures_same_week_grouped_together(self):
        monday_1 = self.today - timedelta(days=self.today.weekday())
        _make_lecture(self.routine, self.subject, "P-01", monday_1)
        _make_lecture(self.routine, self.subject, "P-02", monday_1 + timedelta(days=2))
        week_map = timeline.get_routine_week_map()
        self.assertEqual(len(week_map), 1)

    def test_exam_only_week_still_gets_a_number(self):
        # Milestone 13, Phase 1's actual requirement: an exam falling in
        # a week with no lecture must still resolve to a Routine Week
        # number, since the Exam Timeline now uses this same map.
        monday_1 = self.today - timedelta(days=self.today.weekday())
        _make_lecture(self.routine, self.subject, "P-01", monday_1)
        Exam.objects.create(
            routine=self.routine, exam_code="WE-01", exam_name="Weekly Exam 1",
            exam_type=Exam.ExamType.WEEKLY, exam_date=monday_1 + timedelta(days=14),
        )
        week_map = timeline.get_routine_week_map()
        exam_week_key = (monday_1 + timedelta(days=14)).isocalendar()[:2]
        self.assertIn(exam_week_key, week_map)
        self.assertEqual(week_map[exam_week_key], 3)


class RoutineWeekViewTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)
        self.today = timezone.localdate()
        self.routine = Routine.objects.create(name="Nav Test Routine", active=True)
        self.subject = Subject.objects.create(code="P", name="Physics", display_order=1)
        monday_1 = self.today - timedelta(days=self.today.weekday())
        self.lecture1 = _make_lecture(self.routine, self.subject, "P-01", monday_1)
        self.lecture2 = _make_lecture(self.routine, self.subject, "P-02", monday_1 + timedelta(days=14))

    def test_week_page_renders_its_lectures(self):
        response = self.client.get(reverse("routine-week", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Routine Week 1")
        self.assertContains(response, "P-01")
        self.assertNotContains(response, "P-02")

    def test_unknown_week_404s(self):
        response = self.client.get(reverse("routine-week", args=[99]))
        self.assertEqual(response.status_code, 404)

    def test_next_previous_navigation_links(self):
        # lecture1 is week 1, lecture2 (14 days later) is week 3 - week 2
        # is the empty week in between (still a valid, navigable week).
        response = self.client.get(reverse("routine-week", args=[1]))
        self.assertNotContains(response, "Previous Week")
        self.assertContains(response, "Next Week")

        response = self.client.get(reverse("routine-week", args=[3]))
        self.assertContains(response, "Previous Week")
        self.assertNotContains(response, "Next Week")

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("routine-week", args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_routine_timeline_week_header_links_to_routine_week_page(self):
        response = self.client.get(reverse("routine-list"))
        self.assertContains(response, reverse("routine-week", args=[1]))

    def test_exam_timeline_uses_the_same_routine_week_numbering(self):
        # Milestone 13, Phase 1: exactly one shared Routine Week
        # implementation - the Exam Timeline must show "Routine Week N"
        # too, not a separate ISO-based label.
        Exam.objects.create(
            routine=self.routine, exam_code="WE-01", exam_name="Weekly Exam 1",
            exam_type=Exam.ExamType.WEEKLY, exam_date=self.lecture1.lecture_date,
        )
        response = self.client.get(reverse("exam-timeline"))
        self.assertContains(response, "Routine Week 1")
        self.assertContains(response, reverse("routine-week", args=[1]))


# Milestone 12's RoutineResourcesViewTests (honest-empty-state
# placeholder coverage) was removed here in Milestone 14 - the
# placeholder page it tested no longer exists. `RoutineResourcesView`
# is now the real, filesystem-backed Routine Archive; its full test
# coverage (empty state, latest-selection, login requirement, HTMX
# partial, path-traversal safety, etc.) lives in
# `routines/tests_archive.py`.


class AdminVsStudentNavigationTests(TestCase):
    """Milestone 12, Phase 9: dataset management is staff-only - a
    non-staff user is blocked at the view (403), not just hidden from
    the nav (which would be security-by-obscurity only)."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.staff_user = create_user(username="staff_member")
        self.staff_user.is_staff = True
        self.staff_user.save()

    def test_non_staff_user_gets_403_on_dataset_history(self):
        self.client.force_login(self.data["user"])
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 403)

    def test_non_staff_user_gets_403_on_dataset_compare(self):
        self.client.force_login(self.data["user"])
        response = self.client.get(reverse("dataset-compare"))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_access_dataset_history(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected_to_login_not_403(self):
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_nav_shows_datasets_link_for_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, reverse("dataset-history"))
        self.assertNotContains(response, "Routine Resources")

    def test_nav_shows_routine_resources_for_non_staff(self):
        self.client.force_login(self.data["user"])
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Routine Resources")
        self.assertNotContains(response, reverse("dataset-history"))


class ExamDetailCrossNavigationTests(TestCase):
    """Milestone 12, Phase 10: Exam Detail exposes covered
    Subjects/Chapters/Lectures, readiness, and per-lecture revision
    (exam-ready) status - all reused from existing services."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_covered_subjects_and_chapters_listed_and_linked(self):
        exam = self.data["exams"]["we01"]  # covers P-01, P-02, E-01
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertContains(response, reverse("subject-detail", args=[self.data["subject_p"].pk]))
        chapter = self.data["chapters"]["p11"]
        self.assertContains(response, reverse("chapter-detail", args=[chapter.pk]))

    def test_readiness_row_present(self):
        exam = self.data["exams"]["we01"]
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertIsNotNone(response.context["readiness_row"])
        self.assertContains(response, "Readiness")

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        exam = self.data["exams"]["we01"]
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertEqual(response.status_code, 302)
