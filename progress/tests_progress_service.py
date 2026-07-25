"""Milestone 15.2, Parts 2-4 - Progress Service tests.

`core.test_utils.build_sample_dataset()`'s `topic2` (class_done=True
only - the fixture's one deliberately partial topic) is exactly what
exercises the multi-dimensional formula: under the old "all four
required" definition it contributes 0 to everything; here it
contributes 25% (1 of 4 units) to every scope that includes it.
Hand-derived expected values are documented per test.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.test import TestCase

from core.test_utils import build_sample_dataset, create_user
from progress.services import progress_service as ps
from subjects.models import Chapter, Subject


class TopicProgressTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_fully_completed_topic_is_100_percent(self):
        result = ps.get_topic_progress(self.user, self.data["topics"]["t1"].id)
        self.assertEqual(result["completed_units"], 4)
        self.assertEqual(result["total_units"], 4)
        self.assertEqual(result["percentage"], 100.0)

    def test_partial_topic_gives_partial_credit_not_zero(self):
        # The core behavior change this milestone introduces: class_done
        # alone is 25%, not 0% (the old all-four-required definition's
        # result for this exact topic).
        result = ps.get_topic_progress(self.user, self.data["topics"]["t2"].id)
        self.assertEqual(result["completed_units"], 1)
        self.assertEqual(result["percentage"], 25.0)
        self.assertEqual(result["dimensions"]["class_done"]["completed"], 1)
        self.assertEqual(result["dimensions"]["notes_done"]["completed"], 0)

    def test_untouched_topic_is_zero(self):
        result = ps.get_topic_progress(self.user, self.data["topics"]["t4"].id)
        self.assertEqual(result["completed_units"], 0)
        self.assertEqual(result["percentage"], 0.0)

    def test_dimension_colors_are_fixed(self):
        result = ps.get_topic_progress(self.user, self.data["topics"]["t1"].id)
        self.assertEqual(result["dimensions"]["class_done"]["color_class"], "bg-blue-500")
        self.assertEqual(result["dimensions"]["notes_done"]["color_class"], "bg-emerald-500")
        self.assertEqual(result["dimensions"]["revision_done"]["color_class"], "bg-amber-400")
        self.assertEqual(result["dimensions"]["practice_done"]["color_class"], "bg-purple-500")


class HierarchicalAggregationTests(TestCase):
    """Chapter -> Lecture -> Subject -> overall, per Part 3's hierarchy."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_chapter_with_one_complete_one_untouched_topic(self):
        # ch_p1_1: topic1 (complete) + topic4 (untouched, different lecture).
        result = ps.get_chapter_progress(self.user, self.data["chapters"]["p11"].id)
        self.assertEqual(result["topic_count"], 2)
        self.assertEqual(result["completed_units"], 4)
        self.assertEqual(result["total_units"], 8)
        self.assertEqual(result["percentage"], 50.0)

    def test_chapter_with_only_the_partial_topic(self):
        result = ps.get_chapter_progress(self.user, self.data["chapters"]["p12"].id)
        self.assertEqual(result["topic_count"], 1)
        self.assertEqual(result["completed_units"], 1)
        self.assertEqual(result["percentage"], 25.0)

    def test_lecture_aggregates_its_two_topics(self):
        # lecture_p01: topic1 (complete) + topic2 (class only).
        result = ps.get_lecture_progress(self.user, self.data["lectures"]["p01"].id)
        self.assertEqual(result["topic_count"], 2)
        self.assertEqual(result["completed_units"], 5)
        self.assertEqual(result["total_units"], 8)
        self.assertEqual(result["percentage"], round(5 / 8 * 100, 1))

    def test_lecture_with_no_topics_touched(self):
        result = ps.get_lecture_progress(self.user, self.data["lectures"]["p06"].id)
        self.assertEqual(result["topic_count"], 1)
        self.assertEqual(result["completed_units"], 0)

    def test_subject_aggregates_all_its_lectures(self):
        # Subject P: topic1 (complete) + topic2 (class) + topic3 (complete)
        # + topic4 (untouched) = 4 topics, 16 units, 9 completed.
        result = ps.get_subject_progress(self.user, "P")
        self.assertEqual(result["topic_count"], 4)
        self.assertEqual(result["completed_units"], 9)
        self.assertEqual(result["total_units"], 16)

    def test_subject_with_no_chapter_breakdown_still_counts(self):
        # Subject E (self-study, zero Chapter rows) - topic5, untouched.
        result = ps.get_subject_progress(self.user, "E")
        self.assertEqual(result["topic_count"], 1)
        self.assertEqual(result["completed_units"], 0)

    def test_overall_progress_spans_every_topic(self):
        result = ps.get_overall_progress(self.user)
        self.assertEqual(result["topic_count"], 5)
        self.assertEqual(result["completed_units"], 9)
        self.assertEqual(result["total_units"], 20)
        self.assertEqual(result["percentage"], 45.0)

    def test_second_user_sees_zero_everywhere(self):
        other = create_user("student2")
        result = ps.get_overall_progress(other)
        self.assertEqual(result["completed_units"], 0)


class ExamProgressTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_exam_covering_three_lectures(self):
        # WE-01 covers P-01 (topic1+topic2), P-02 (topic3), E-01 (topic5)
        # = 4 topics, 16 units, 9 completed.
        result = ps.get_exam_progress(self.user, self.data["exams"]["we01"])
        self.assertEqual(result["topic_count"], 4)
        self.assertEqual(result["completed_units"], 9)
        self.assertEqual(result["total_units"], 16)

    def test_exam_covering_an_untouched_lecture(self):
        result = ps.get_exam_progress(self.user, self.data["exams"]["we02"])
        self.assertEqual(result["topic_count"], 1)
        self.assertEqual(result["completed_units"], 0)

    def test_bulk_matches_single_lookup(self):
        exams = list(self.data["exams"].values())
        bulk = ps.get_bulk_exam_progress(self.user, exams)
        for exam in exams:
            single = ps.get_exam_progress(self.user, exam)
            self.assertEqual(bulk[exam.id]["completed_units"], single["completed_units"])
            self.assertEqual(bulk[exam.id]["topic_count"], single["topic_count"])

    def test_bulk_exam_progress_is_one_query_regardless_of_exam_count(self):
        exams = list(self.data["exams"].values())
        with CaptureQueriesContext(connection) as ctx:
            ps.get_bulk_exam_progress(self.user, exams)
        self.assertEqual(len(ctx.captured_queries), 1)


class BulkProgressTests(TestCase):
    """Part 17 - no N+1: every bulk function costs exactly one query
    regardless of row count, and matches the single-scope function's
    numbers for the same entity."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_bulk_subject_progress_matches_single_and_is_one_query(self):
        with CaptureQueriesContext(connection) as ctx:
            bulk = ps.get_bulk_subject_progress(self.user)
        self.assertEqual(len(ctx.captured_queries), 1)
        for subject in Subject.objects.all():
            single = ps.get_subject_progress(self.user, subject.code)
            self.assertEqual(bulk[subject.id]["completed_units"], single["completed_units"])
            self.assertEqual(bulk[subject.id]["topic_count"], single["topic_count"])

    def test_bulk_chapter_progress_matches_single_and_is_one_query(self):
        chapters = Chapter.objects.all()
        with CaptureQueriesContext(connection) as ctx:
            bulk = ps.get_bulk_chapter_progress(self.user, chapters)
        self.assertEqual(len(ctx.captured_queries), 1)
        for chapter in chapters:
            single = ps.get_chapter_progress(self.user, chapter.id)
            self.assertEqual(bulk[chapter.id]["completed_units"], single["completed_units"])

    def test_bulk_lecture_progress_matches_single_and_is_one_query(self):
        lectures = self.data["routine"].lectures.all()
        with CaptureQueriesContext(connection) as ctx:
            bulk = ps.get_bulk_lecture_progress(self.user, lectures)
        self.assertEqual(len(ctx.captured_queries), 1)
        for lecture in lectures:
            single = ps.get_lecture_progress(self.user, lecture.id)
            self.assertEqual(bulk[lecture.id]["completed_units"], single["completed_units"])


class RevisionSchedulingUnaffectedTests(TestCase):
    """Part 2's own architectural rule: the new formula must never
    change when a lecture is considered "complete" for revision-
    scheduling purposes - that stays `is_lecture_completed()`'s strict
    all-four-required definition, entirely untouched by this module."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_partially_progressed_lecture_does_not_trigger_a_schedule(self):
        from progress.models import RevisionSchedule
        from progress.services import revision as revision_service

        # lecture_p01 is only partially done (topic2 lacks 3 of 4 flags) -
        # the new progress service reports 62.5% for it, but that must
        # not be enough to have ever created a revision schedule.
        created = revision_service.ensure_revision_schedule(self.user, self.data["lectures"]["p01"])
        self.assertFalse(created)
        self.assertEqual(
            RevisionSchedule.objects.filter(user=self.user, lecture=self.data["lectures"]["p01"]).count(), 0
        )
