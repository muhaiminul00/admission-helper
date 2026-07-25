from datetime import timedelta

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from progress.models import Progress
from progress.services import advanced_analytics as insights
from progress.services.analytics import (
    get_chapter_analytics,
    get_exam_readiness,
    get_lecture_analytics,
    get_subject_analytics,
    readiness_label,
)
from progress.services.dashboard import (
    get_completion_stats,
    get_dashboard_stats,
    get_dashboard_widgets,
    get_daily_progress_count,
)


class SubjectAnalyticsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_totals_and_percentage_per_subject(self):
        rows = {row["subject"].code: row for row in get_subject_analytics(self.user)}

        # Subject P: 4 topics (t1..t4), 2 completed (t1, t3).
        self.assertEqual(rows["P"]["total"], 4)
        self.assertEqual(rows["P"]["completed"], 2)
        self.assertEqual(rows["P"]["remaining"], 2)
        self.assertEqual(rows["P"]["percentage"], 50.0)

        # Subject E: 1 topic (t5, chapterless), 0 completed - must still
        # be counted (regression coverage for the chapter__subject bug
        # fixed in Milestone 5).
        self.assertEqual(rows["E"]["total"], 1)
        self.assertEqual(rows["E"]["completed"], 0)
        self.assertEqual(rows["E"]["percentage"], 0.0)

    def test_sort_by_completion_descending(self):
        rows = get_subject_analytics(self.user, sort="completion")
        percentages = [row["percentage"] for row in rows]
        self.assertEqual(percentages, sorted(percentages, reverse=True))

    def test_sort_by_remaining_descending(self):
        rows = get_subject_analytics(self.user, sort="remaining")
        remaining = [row["remaining"] for row in rows]
        self.assertEqual(remaining, sorted(remaining, reverse=True))

    def test_sort_by_name_ascending(self):
        rows = get_subject_analytics(self.user, sort="name")
        names = [row["subject"].name for row in rows]
        self.assertEqual(names, sorted(names))

    def test_query_count_is_fixed(self):
        with CaptureQueriesContext(connection) as ctx:
            get_subject_analytics(self.user)
        self.assertEqual(len(ctx.captured_queries), 1)

    def test_no_subjects_returns_empty_list(self):
        Progress.objects.all().delete()
        from lectures.models import LectureTopic
        from routines.models import Lecture, Exam
        from subjects.models import Subject, Chapter

        LectureTopic.objects.all().delete()
        Lecture.objects.all().delete()
        Exam.objects.all().delete()
        Chapter.objects.all().delete()
        Subject.objects.all().delete()

        self.assertEqual(get_subject_analytics(self.user), [])

    def test_second_user_sees_only_their_own_progress(self):
        other = create_user("student2")
        rows = {row["subject"].code: row for row in get_subject_analytics(other)}
        # Same curriculum totals, but zero completions - other never
        # touched any Progress row.
        self.assertEqual(rows["P"]["total"], 4)
        self.assertEqual(rows["P"]["completed"], 0)
        self.assertEqual(rows["E"]["completed"], 0)


class ChapterAnalyticsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_totals_per_chapter(self):
        rows = {
            (row["chapter"].paper, row["chapter"].chapter_no): row
            for row in get_chapter_analytics(self.user)
        }
        # P/1/1 covered by t1 (completed) and t4 (not) -> 2 total, 1 done.
        self.assertEqual(rows[(1, 1)]["total"], 2)
        self.assertEqual(rows[(1, 1)]["completed"], 1)
        self.assertEqual(rows[(1, 1)]["percentage"], 50.0)
        # P/1/2 covered by t2 only (partial, not fully done).
        self.assertEqual(rows[(1, 2)]["total"], 1)
        self.assertEqual(rows[(1, 2)]["completed"], 0)
        # P/2/1 covered by t3 only (fully done).
        self.assertEqual(rows[(2, 1)]["total"], 1)
        self.assertEqual(rows[(2, 1)]["completed"], 1)
        self.assertEqual(rows[(2, 1)]["percentage"], 100.0)

    def test_filter_by_subject_code(self):
        rows = get_chapter_analytics(self.user, subject_code="P")
        self.assertEqual(len(rows), 3)
        rows_other = get_chapter_analytics(self.user, subject_code="E")
        self.assertEqual(rows_other, [])

    def test_query_count_is_fixed(self):
        with CaptureQueriesContext(connection) as ctx:
            get_chapter_analytics(self.user)
        self.assertEqual(len(ctx.captured_queries), 1)

    def test_second_user_sees_zero_completion(self):
        other = create_user("student2")
        rows = {
            (row["chapter"].paper, row["chapter"].chapter_no): row
            for row in get_chapter_analytics(other)
        }
        self.assertEqual(rows[(1, 1)]["completed"], 0)
        self.assertEqual(rows[(2, 1)]["completed"], 0)


class LectureAnalyticsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_totals_per_lecture(self):
        rows = {row["lecture"].lecture_code: row for row in get_lecture_analytics(self.user)}
        self.assertEqual(rows["P-01"]["total"], 2)
        self.assertEqual(rows["P-01"]["completed"], 1)
        self.assertEqual(rows["P-01"]["percentage"], 50.0)
        self.assertEqual(rows["P-02"]["total"], 1)
        self.assertEqual(rows["P-02"]["completed"], 1)
        self.assertEqual(rows["P-02"]["percentage"], 100.0)
        self.assertEqual(rows["P-06"]["completed"], 0)
        self.assertEqual(rows["E-01"]["completed"], 0)

    def test_filter_by_subject(self):
        rows = get_lecture_analytics(self.user, subject_code="E")
        self.assertEqual([r["lecture"].lecture_code for r in rows], ["E-01"])

    def test_search_by_code(self):
        rows = get_lecture_analytics(self.user, search="P-02")
        self.assertEqual([r["lecture"].lecture_code for r in rows], ["P-02"])

    def test_search_by_title(self):
        rows = get_lecture_analytics(self.user, search="Physics 1")
        self.assertEqual([r["lecture"].lecture_code for r in rows], ["P-01"])

    def test_search_no_match_returns_empty(self):
        self.assertEqual(get_lecture_analytics(self.user, search="NoSuchThing"), [])

    def test_query_count_is_fixed(self):
        with CaptureQueriesContext(connection) as ctx:
            get_lecture_analytics(self.user)
        self.assertEqual(len(ctx.captured_queries), 1)

    def test_second_user_sees_zero_completion(self):
        other = create_user("student2")
        rows = {row["lecture"].lecture_code: row for row in get_lecture_analytics(other)}
        self.assertEqual(rows["P-01"]["completed"], 0)
        self.assertEqual(rows["P-02"]["completed"], 0)


class ExamReadinessTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_readiness_percentage_and_counts(self):
        rows = {row["exam"].exam_code: row for row in get_exam_readiness(self.user)}

        we01 = rows["WE-01"]
        # covers P-01 (2 topics, 1 done), P-02 (1 topic, 1 done),
        # E-01 (1 topic, 0 done) -> total 4, completed 2 -> 50%.
        self.assertEqual(we01["covered_lecture_count"], 3)
        self.assertEqual(we01["total_topics"], 4)
        self.assertEqual(we01["completed_topics"], 2)
        self.assertEqual(we01["remaining_topics"], 2)
        self.assertEqual(we01["percentage"], 50.0)
        self.assertEqual(we01["readiness_label"], "Needs Work")

        we02 = rows["WE-02"]
        self.assertEqual(we02["covered_lecture_count"], 1)
        self.assertEqual(we02["total_topics"], 1)
        self.assertEqual(we02["completed_topics"], 0)
        self.assertEqual(we02["percentage"], 0.0)
        self.assertEqual(we02["readiness_label"], "High Risk")

    def test_readiness_label_thresholds(self):
        self.assertEqual(readiness_label(100), "ready")
        self.assertEqual(readiness_label(90), "ready")
        self.assertEqual(readiness_label(89.9), "good")
        self.assertEqual(readiness_label(70), "good")
        self.assertEqual(readiness_label(69.9), "needs_work")
        self.assertEqual(readiness_label(40), "needs_work")
        self.assertEqual(readiness_label(39.9), "high_risk")
        self.assertEqual(readiness_label(0), "high_risk")

    def test_covered_lecture_referencing_unknown_code_is_ignored_not_crashed(self):
        exam = self.data["exams"]["we01"]
        exam.covered_lectures = ["P-01", "DOES-NOT-EXIST"]
        exam.save()

        rows = {row["exam"].exam_code: row for row in get_exam_readiness(self.user)}
        self.assertEqual(rows["WE-01"]["covered_lecture_count"], 1)

    def test_no_exams_returns_empty_list(self):
        from routines.models import Exam
        Exam.objects.all().delete()
        self.assertEqual(get_exam_readiness(self.user), [])

    def test_query_count_is_fixed_regardless_of_exam_count(self):
        with CaptureQueriesContext(connection) as ctx:
            get_exam_readiness(self.user)
        self.assertEqual(len(ctx.captured_queries), 2)

    def test_second_user_sees_zero_readiness(self):
        other = create_user("student2")
        rows = {row["exam"].exam_code: row for row in get_exam_readiness(other)}
        self.assertEqual(rows["WE-01"]["completed_topics"], 0)
        self.assertEqual(rows["WE-01"]["percentage"], 0.0)


class DashboardServiceTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_completion_stats(self):
        stats = get_completion_stats(self.user)
        self.assertEqual(stats["total_topics"], 5)
        self.assertEqual(stats["completed_topics"], 2)
        self.assertEqual(stats["remaining_topics"], 3)
        self.assertEqual(stats["completion_percentage"], 40.0)

    def test_completion_stats_zero_topics(self):
        from lectures.models import LectureTopic
        LectureTopic.objects.all().delete()
        stats = get_completion_stats(self.user)
        self.assertEqual(stats["total_topics"], 0)
        self.assertEqual(stats["completion_percentage"], 0)

    def test_completion_stats_isolated_per_user(self):
        other = create_user("student2")
        stats = get_completion_stats(other)
        self.assertEqual(stats["total_topics"], 5)  # shared curriculum
        self.assertEqual(stats["completed_topics"], 0)  # own progress is empty

    def test_lecture_stats_completed_definition(self):
        stats = get_dashboard_stats(self.user)
        self.assertEqual(stats["total_lectures"], 4)
        # Only P-02 has topics and all of them complete.
        self.assertEqual(stats["completed_lectures"], 1)

    def test_exam_stats_next_exam_and_days_remaining(self):
        stats = get_dashboard_stats(self.user)
        self.assertEqual(stats["total_exams"], 2)
        self.assertEqual(stats["upcoming_exams"], 2)
        self.assertEqual(stats["next_exam"].exam_code, "WE-01")
        self.assertEqual(stats["days_remaining"], 10)

    def test_exam_stats_no_upcoming_exam(self):
        from routines.models import Exam
        Exam.objects.all().delete()
        stats = get_dashboard_stats(self.user)
        self.assertEqual(stats["upcoming_exams"], 0)
        self.assertIsNone(stats["next_exam"])
        self.assertIsNone(stats["days_remaining"])

    def test_daily_progress_count(self):
        # Progress rows in build_sample_dataset() are all created "now".
        self.assertEqual(get_daily_progress_count(self.user), 2)

    def test_daily_progress_count_excludes_older_updates(self):
        Progress.objects.filter(
            user=self.user, lecture_topic=self.data["topics"]["t1"]
        ).update(updated_at=timezone.now() - timedelta(days=2))
        self.assertEqual(get_daily_progress_count(self.user), 1)

    def test_daily_progress_count_isolated_per_user(self):
        other = create_user("student2")
        self.assertEqual(get_daily_progress_count(other), 0)

    def test_widgets_recent_activity_and_upcoming_exams(self):
        widgets = get_dashboard_widgets(self.user)
        self.assertEqual(len(widgets["recent_activity"]), 2)
        self.assertEqual(
            [e.exam_code for e in widgets["upcoming_exams_list"]], ["WE-01", "WE-02"]
        )

    def test_widgets_most_least_completed_subject(self):
        widgets = get_dashboard_widgets(self.user)
        self.assertEqual(widgets["most_completed"]["subject"].code, "P")
        self.assertEqual(widgets["least_completed"]["subject"].code, "E")

    def test_widgets_ignore_subjects_with_zero_topics(self):
        from lectures.models import LectureTopic
        LectureTopic.objects.filter(lecture__subject=self.data["subject_e"]).delete()
        widgets = get_dashboard_widgets(self.user)
        self.assertEqual(widgets["most_completed"]["subject"].code, "P")
        self.assertEqual(widgets["least_completed"]["subject"].code, "P")

    def test_no_data_widgets_dont_crash(self):
        from lectures.models import LectureTopic
        from routines.models import Lecture, Exam
        from subjects.models import Subject, Chapter

        LectureTopic.objects.all().delete()
        Lecture.objects.all().delete()
        Exam.objects.all().delete()
        Chapter.objects.all().delete()
        Subject.objects.all().delete()

        widgets = get_dashboard_widgets(self.user)
        self.assertIsNone(widgets["most_completed"])
        self.assertIsNone(widgets["least_completed"])
        self.assertEqual(list(widgets["recent_activity"]), [])
        self.assertEqual(list(widgets["upcoming_exams_list"]), [])

    def test_widgets_isolated_per_user(self):
        other = create_user("student2")
        widgets = get_dashboard_widgets(other)
        self.assertEqual(len(widgets["recent_activity"]), 0)
        self.assertEqual(widgets["most_completed"]["percentage"], 0.0)


class ProgressToggleViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.client.force_login(self.user)

    def test_toggle_creates_progress_row_when_missing(self):
        topic = self.data["topics"]["t4"]
        self.assertFalse(Progress.objects.filter(user=self.user, lecture_topic=topic).exists())

        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        progress = Progress.objects.get(user=self.user, lecture_topic=topic)
        self.assertTrue(progress.class_done)

    def test_toggle_flips_existing_value(self):
        topic = self.data["topics"]["t2"]  # PARTIAL: class_done=True already
        url = reverse("progress-toggle", args=[topic.id, "class_done"])

        self.client.post(url)
        progress = Progress.objects.get(user=self.user, lecture_topic=topic)
        self.assertFalse(progress.class_done)

        self.client.post(url)
        progress.refresh_from_db()
        self.assertTrue(progress.class_done)

    def test_toggle_never_creates_duplicate_progress_row(self):
        topic = self.data["topics"]["t4"]
        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(
            Progress.objects.filter(user=self.user, lecture_topic=topic).count(), 1
        )

    def test_toggle_rejects_unknown_field(self):
        topic = self.data["topics"]["t1"]
        url = reverse("progress-toggle", args=[topic.id, "not_a_real_field"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_toggle_unknown_topic_404s(self):
        url = reverse("progress-toggle", args=[999999, "class_done"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_toggle_get_not_allowed(self):
        topic = self.data["topics"]["t1"]
        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        topic = self.data["topics"]["t1"]
        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_toggle_never_touches_another_users_progress_row(self):
        other = create_user("student2")
        topic = self.data["topics"]["t1"]
        Progress.objects.create(
            user=other, lecture_topic=topic,
            class_done=True, notes_done=True, revision_done=True, practice_done=True,
        )

        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        self.client.post(url)  # logged in as self.user

        other_progress = Progress.objects.get(user=other, lecture_topic=topic)
        self.assertTrue(other_progress.class_done)  # untouched by self.user's toggle
        self.assertEqual(Progress.objects.filter(lecture_topic=topic).count(), 2)


class ProgressOverviewViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_renders_with_subject_breakdown(self):
        response = self.client.get(reverse("progress-overview"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_topics"], 5)
        codes = {row["subject"].code for row in response.context["subject_rows"]}
        self.assertEqual(codes, {"P", "E"})

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("progress-overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class AnalyticsSubjectsViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("analytics-subjects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Physics")
        self.assertContains(response, "<html")

    def test_htmx_request_returns_partial_only(self):
        response = self.client.get(
            reverse("analytics-subjects"), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")
        self.assertContains(response, "Physics")

    def test_sort_query_param_applied(self):
        response = self.client.get(reverse("analytics-subjects"), {"sort": "completion"})
        rows = response.context["rows"]
        percentages = [row["percentage"] for row in rows]
        self.assertEqual(percentages, sorted(percentages, reverse=True))

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("analytics-subjects"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class AnalyticsChaptersViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("analytics-chapters"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vector")

    def test_filter_by_subject(self):
        response = self.client.get(reverse("analytics-chapters"), {"subject": "E"})
        self.assertEqual(list(response.context["page_obj"]), [])

    def test_htmx_partial_response(self):
        response = self.client.get(
            reverse("analytics-chapters"), HTTP_HX_REQUEST="true"
        )
        self.assertNotContains(response, "<html")

    def test_pagination_present_in_context(self):
        response = self.client.get(reverse("analytics-chapters"))
        self.assertIn("page_obj", response.context)
        self.assertEqual(response.context["page_obj"].paginator.count, 3)


class AnalyticsLecturesViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("analytics-lectures"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "P-01")

    def test_search_filter(self):
        response = self.client.get(reverse("analytics-lectures"), {"q": "P-02"})
        codes = [row["lecture"].lecture_code for row in response.context["page_obj"]]
        self.assertEqual(codes, ["P-02"])

    def test_subject_filter(self):
        response = self.client.get(reverse("analytics-lectures"), {"subject": "E"})
        codes = [row["lecture"].lecture_code for row in response.context["page_obj"]]
        self.assertEqual(codes, ["E-01"])

    def test_htmx_partial_response(self):
        response = self.client.get(
            reverse("analytics-lectures"), HTTP_HX_REQUEST="true"
        )
        self.assertNotContains(response, "<html")


class AnalyticsExamsViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response_with_readiness_badges(self):
        response = self.client.get(reverse("analytics-exams"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Needs Work")
        self.assertContains(response, "High Risk")

    def test_htmx_partial_response(self):
        response = self.client.get(
            reverse("analytics-exams"), HTTP_HX_REQUEST="true"
        )
        self.assertNotContains(response, "<html")

    def test_empty_state_when_no_exams(self):
        from routines.models import Exam
        Exam.objects.all().delete()
        response = self.client.get(reverse("analytics-exams"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No exams found")


# ---------------------------------------------------------------------
# Milestone 8 - Advanced Analytics ("study advisor" insights)
# ---------------------------------------------------------------------

class SubjectInsightsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_strongest_and_weakest(self):
        result = insights.get_subject_insights(self.user)
        self.assertEqual(result["strongest"]["subject"].code, "P")
        self.assertEqual(result["weakest"]["subject"].code, "E")

    def test_ranking_order_and_rank_numbers(self):
        ranking = insights.get_subject_insights(self.user)["ranking"]
        self.assertEqual([r["subject"].code for r in ranking], ["P", "E"])
        self.assertEqual([r["rank"] for r in ranking], [1, 2])

    def test_strongest_none_when_no_topics_exist(self):
        from lectures.models import LectureTopic
        LectureTopic.objects.all().delete()
        result = insights.get_subject_insights(self.user)
        self.assertIsNone(result["strongest"])
        self.assertIsNone(result["weakest"])

    def test_completion_trend_counts(self):
        trend = {r["subject"].code: r for r in insights.get_subject_completion_trend(self.user)}
        # t1 and t3 (subject P) were completed "now" by build_sample_dataset().
        self.assertEqual(trend["P"]["today"], 2)
        self.assertEqual(trend["P"]["last_7_days"], 2)
        self.assertEqual(trend["P"]["last_30_days"], 2)
        self.assertEqual(trend["E"]["today"], 0)

    def test_average_completion_speed(self):
        # 2 completed topics (t1, t3), both on the same (today's) date.
        self.assertEqual(insights.get_average_completion_speed(self.user), 2.0)

    def test_average_completion_speed_zero_when_nothing_completed(self):
        other = create_user("student2")
        self.assertEqual(insights.get_average_completion_speed(other), 0.0)

    def test_second_user_isolation(self):
        other = create_user("student2")
        result = insights.get_subject_insights(other)
        self.assertEqual(result["strongest"]["percentage"], 0.0)
        self.assertEqual(result["weakest"]["percentage"], 0.0)


class ChapterInsightsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_priority_chapters_rank_upcoming_exam_coverage_higher(self):
        rows = insights.get_priority_chapters(self.user)
        # P/1/1 and P/1/2 both have remaining topics and are covered by
        # an upcoming exam (WE-01/WE-02); P/2/1 is fully done (excluded).
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["in_upcoming_exam"] for r in rows))
        self.assertTrue(all(r["remaining"] > 0 for r in rows))

    def test_priority_chapters_accepts_precomputed_rows(self):
        chapter_rows = get_chapter_analytics(self.user)
        with CaptureQueriesContext(connection) as ctx:
            insights.get_priority_chapters(self.user, rows=chapter_rows)
        # Only the 2 "upcoming exam coverage" queries - chapter stats
        # query was skipped since `rows=` was supplied.
        self.assertEqual(len(ctx.captured_queries), 2)

    def test_neglected_chapters_excludes_recently_touched(self):
        # Everything in the fixture was touched "just now" - within the
        # default 14-day staleness window - so nothing should qualify.
        self.assertEqual(insights.get_neglected_chapters(self.user), [])

    def test_neglected_chapters_includes_stale_activity(self):
        Progress.objects.filter(user=self.user).update(
            updated_at=timezone.now() - timedelta(days=30)
        )
        rows = insights.get_neglected_chapters(self.user, stale_days=14)
        codes = {(r["chapter"].paper, r["chapter"].chapter_no) for r in rows}
        self.assertIn((1, 1), codes)
        self.assertIn((1, 2), codes)

    def test_most_unfinished_chapters_order(self):
        rows = insights.get_most_unfinished_chapters(self.user)
        self.assertTrue(all(r["remaining"] > 0 for r in rows))
        remaining = [r["remaining"] for r in rows]
        self.assertEqual(remaining, sorted(remaining, reverse=True))

    def test_most_completed_chapters_order(self):
        rows = insights.get_most_completed_chapters(self.user)
        percentages = [r["percentage"] for r in rows]
        self.assertEqual(percentages, sorted(percentages, reverse=True))
        self.assertEqual(rows[0]["percentage"], 100.0)


class LectureInsightsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_longest_untouched_lectures_dated_before_undated(self):
        rows = insights.get_longest_untouched_lectures(self.user)
        codes = [r["lecture"].lecture_code for r in rows]
        # P-06 and E-01 both have 0 completed topics; P-06 (undated) is
        # the fixture's only zero-completion lecture with no date at
        # all, E-01 likewise - both undated, so relative order is
        # stable, but P-01/P-02 (which have >=1 completed topic) must
        # never appear here.
        self.assertNotIn("P-01", codes)
        self.assertNotIn("P-02", codes)
        self.assertIn("P-06", codes)
        self.assertIn("E-01", codes)

    def test_recently_completed_lectures(self):
        rows = insights.get_recently_completed_lectures(self.user)
        self.assertEqual([r["lecture"].lecture_code for r in rows], ["P-02"])
        self.assertIsNotNone(rows[0]["completed_at"])

    def test_backlog_lectures_order(self):
        rows = insights.get_backlog_lectures(self.user)
        codes = {r["lecture"].lecture_code for r in rows}
        self.assertEqual(codes, {"P-01", "P-06", "E-01"})
        self.assertNotIn("P-02", codes)  # fully completed - no backlog

    def test_study_streak_single_day(self):
        streak = insights.get_study_streak(self.user)
        self.assertEqual(streak["current_streak"], 1)
        self.assertEqual(streak["longest_streak"], 1)

    def test_study_streak_no_activity(self):
        other = create_user("student2")
        streak = insights.get_study_streak(other)
        self.assertEqual(streak, {"current_streak": 0, "longest_streak": 0})

    def test_study_streak_multi_day_and_broken(self):
        # Simulate completions on 3 consecutive days ending 2 days ago -
        # a broken streak (nothing done yesterday or today).
        today = timezone.localdate()
        t1 = self.data["topics"]["t1"]
        t3 = self.data["topics"]["t3"]
        Progress.objects.filter(user=self.user, lecture_topic=t1).update(
            updated_at=timezone.now() - timedelta(days=4)
        )
        Progress.objects.filter(user=self.user, lecture_topic=t3).update(
            updated_at=timezone.now() - timedelta(days=3)
        )
        streak = insights.get_study_streak(self.user)
        self.assertEqual(streak["current_streak"], 0)  # broken - last activity 3 days ago
        self.assertEqual(streak["longest_streak"], 2)  # the two consecutive days

    def test_daily_completion_trend_zero_filled(self):
        trend = insights.get_daily_completion_trend(self.user, days=35)
        self.assertEqual(len(trend), 35)
        self.assertEqual(trend[-1]["date"], timezone.localdate())
        self.assertEqual(trend[-1]["count"], 2)
        self.assertEqual(trend[0]["count"], 0)

    def test_weekly_distribution_sums_to_total_completed(self):
        rows = insights.get_weekly_distribution(self.user)
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(r["count"] for r in rows), 2)

    def test_monthly_completion_timeline_length_and_current_month(self):
        rows = insights.get_monthly_completion_timeline(self.user, months=6)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[-1]["count"], 2)  # this month


class ExamInsightsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_readiness_score_blends_topic_and_lecture_completion(self):
        rows = {r["exam"].exam_code: r for r in insights.get_exam_insights(self.user)}

        we01 = rows["WE-01"]
        # topic completion 2/4 = 50%; lecture completion 1/3 (only
        # P-02 is a fully-completed lecture among P-01/P-02/E-01)
        # = 33.3% -> score = 0.6*50 + 0.4*33.3 = 43.3.
        self.assertEqual(we01["topic_completion_percentage"], 50.0)
        self.assertEqual(we01["completed_lecture_count"], 1)
        self.assertEqual(we01["covered_lecture_count"], 3)
        self.assertEqual(we01["readiness_score"], 43.3)
        self.assertEqual(we01["confidence_label"], "Needs Work")

        we02 = rows["WE-02"]
        self.assertEqual(we02["readiness_score"], 0.0)
        self.assertEqual(we02["confidence_label"], "High Risk")

    def test_coverage_gap_and_remaining_workload_fields(self):
        rows = {r["exam"].exam_code: r for r in insights.get_exam_insights(self.user)}
        we01 = rows["WE-01"]
        self.assertEqual(we01["total_topics"], 4)
        self.assertEqual(we01["completed_topics"], 2)
        self.assertEqual(we01["remaining_topics"], 2)
        self.assertEqual(we01["missing_percentage"], 50.0)

    def test_next_exam_insight_returns_nearest_upcoming(self):
        row = insights.get_next_exam_insight(self.user)
        self.assertEqual(row["exam"].exam_code, "WE-01")

    def test_next_exam_insight_none_when_no_exams(self):
        from routines.models import Exam
        Exam.objects.all().delete()
        self.assertIsNone(insights.get_next_exam_insight(self.user))

    def test_query_count_is_fixed(self):
        # 2 for the readiness math itself (see analytics.py's
        # get_exam_readiness) + 1 for Milestone 9's
        # get_exam_ready_lecture_codes() bulk lookup - still fixed
        # regardless of exam/lecture count, just one more constant.
        with CaptureQueriesContext(connection) as ctx:
            insights.get_exam_insights(self.user)
        self.assertEqual(len(ctx.captured_queries), 3)

    def test_second_user_sees_zero_readiness(self):
        other = create_user("student2")
        rows = {r["exam"].exam_code: r for r in insights.get_exam_insights(other)}
        self.assertEqual(rows["WE-01"]["readiness_score"], 0.0)


class AdvancedDashboardWidgetsTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_widgets_contain_all_expected_keys(self):
        widgets = insights.get_advanced_dashboard_widgets(self.user)
        self.assertEqual(
            set(widgets.keys()),
            {
                "strongest_subject", "weakest_subject", "priority_chapter",
                "longest_untouched_lecture", "study_streak", "ready_for_exam",
            },
        )
        self.assertEqual(widgets["strongest_subject"]["subject"].code, "P")
        self.assertEqual(widgets["ready_for_exam"]["exam"].exam_code, "WE-01")

    def test_widgets_isolated_per_user(self):
        other = create_user("student2")
        widgets = insights.get_advanced_dashboard_widgets(other)
        self.assertEqual(widgets["strongest_subject"]["percentage"], 0.0)
        self.assertEqual(widgets["study_streak"], {"current_streak": 0, "longest_streak": 0})

    def test_dashboard_view_includes_advanced_widgets(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["strongest_subject"]["subject"].code, "P")
        self.assertContains(response, "Study Advisor")

    def test_dashboard_widgets_endpoint_includes_advanced_widgets(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard-widgets"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ready For Exam")


class AnalyticsInsightsViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_full_page_response(self):
        response = self.client.get(reverse("analytics-insights"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "Study Heatmap")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("analytics-insights"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")
        self.assertContains(response, "Highest Priority Chapters")

    def test_context_contains_all_insight_sections(self):
        response = self.client.get(reverse("analytics-insights"))
        for key in (
            "subject_insights", "subject_trend", "average_speed",
            "priority_chapters", "neglected_chapters", "most_unfinished_chapters",
            "most_completed_chapters", "longest_untouched_lectures",
            "recently_completed_lectures", "backlog_lectures", "study_streak",
            "daily_trend", "weekly_distribution", "monthly_timeline", "exam_insights",
        ):
            self.assertIn(key, response.context)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("analytics-insights"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_two_user_isolation_on_insights_page(self):
        other = create_user("student2")
        self.client.force_login(other)
        response = self.client.get(reverse("analytics-insights"))
        self.assertEqual(response.context["subject_insights"]["strongest"]["completed"], 0)
        self.assertEqual(response.context["study_streak"]["current_streak"], 0)
