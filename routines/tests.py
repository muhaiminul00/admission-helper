import io
import tempfile
from pathlib import Path

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from core.test_utils import build_sample_dataset
from lectures.models import LectureTopic
from routines.models import Exam, Lecture, Routine
from routines.services.csv.base_importer import BaseImporter
from routines.services.csv.chapter_importer import ChapterImporter
from routines.services.csv.exam_importer import ExamImporter
from routines.services.csv.lecture_topic_importer import LectureTopicImporter
from routines.services.csv.routine_importer import RoutineImporter
from routines.services.csv.subject_importer import SubjectImporter
from routines.services.csv.utils import BENGALI_DIGITS, _ODHYAY, _PORTRO, _PROTHOM
from routines.services.csv.validators import ImportValidationError
from subjects.models import Chapter, Subject


def _chapter_ref(chapter_no):
    """Build a valid '<paper> পত্র অধ্যায়-<digits>' reference from the
    importer's own verified constants, rather than retyping Bengali
    glyphs (see PROJECT_PROGRESS.md re: the recurring YYA encoding bug).
    """
    digits = "".join(BENGALI_DIGITS[int(d)] for d in str(chapter_no))
    return f"{_PROTHOM} {_PORTRO} {_ODHYAY}-{digits}"


SUBJECTS_CSV = "code,name,display_order\nP,Physics,1\n"
CHAPTERS_CSV = "subject_code,paper,chapter_no,chapter_name,display_order\nP,1,1,Vector,1\n"
ROUTINE_CSV = (
    "date,day,event_type,subject_code,lecture_code,title,start_time,end_time,notes\n"
    "2026-01-01,Thu,CLASS,P,P-01,Physics 1,,,\n"
)


def lecture_topics_csv():
    return (
        "lecture_code,subject_code,chapter_no,topic,display_order\n"
        f"P-01,P,{_chapter_ref(1)},Vectors intro,1\n"
    )


EXAMS_CSV = (
    "exam_code,exam_type,title,lecture_codes,exam_date,online_start,online_end\n"
    "WE-01,WEEKLY,Weekly Exam 1,P-01,2026-01-10,,\n"
)


class ImporterTestCase(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmpdir.name)
        self.addCleanup(self.tmpdir.cleanup)
        self.stdout = io.StringIO()

    def write(self, filename, content):
        (self.base_dir / filename).write_text(content, encoding="utf-8")

    def write_full_dataset(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)

    def run_all_stages(self):
        SubjectImporter(self.base_dir, self.stdout).run()
        ChapterImporter(self.base_dir, self.stdout).run()
        RoutineImporter(self.base_dir, self.stdout).run()
        LectureTopicImporter(self.base_dir, self.stdout).run()
        ExamImporter(self.base_dir, self.stdout).run()


class SubjectImporterTests(ImporterTestCase):
    def test_imports_subject(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        count = SubjectImporter(self.base_dir, self.stdout).run()
        self.assertEqual(count, 1)
        subject = Subject.objects.get(code="P")
        self.assertEqual(subject.name, "Physics")
        self.assertEqual(subject.display_order, 1)

    def test_idempotent_on_rerun(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        SubjectImporter(self.base_dir, self.stdout).run()
        SubjectImporter(self.base_dir, self.stdout).run()
        self.assertEqual(Subject.objects.count(), 1)

    def test_duplicate_code_raises(self):
        self.write(
            "subjects.csv",
            "code,name,display_order\nP,Physics,1\nP,Physics Dup,2\n",
        )
        with self.assertRaises(ImportValidationError):
            SubjectImporter(self.base_dir, self.stdout).run()
        self.assertEqual(Subject.objects.count(), 0)  # rolled back

    def test_missing_required_column_raises(self):
        self.write("subjects.csv", "code,name\nP,Physics\n")
        with self.assertRaises(ImportValidationError):
            SubjectImporter(self.base_dir, self.stdout).run()

    def test_missing_file_raises_friendly_error(self):
        with self.assertRaises(ImportValidationError) as ctx:
            SubjectImporter(self.base_dir, self.stdout).run()
        self.assertIn("missing", ctx.exception.reason.lower())


class FullImportTests(ImporterTestCase):
    def test_full_pipeline_imports_everything(self):
        self.write_full_dataset()
        self.run_all_stages()

        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 1)
        self.assertEqual(Routine.objects.count(), 1)
        self.assertEqual(Lecture.objects.filter(lecture_date__isnull=False).count(), 1)
        self.assertEqual(LectureTopic.objects.count(), 1)
        self.assertEqual(Exam.objects.count(), 1)

        exam = Exam.objects.get(exam_code="WE-01")
        self.assertEqual(exam.online_start, None)
        self.assertEqual(exam.covered_lectures, ["P-01"])

    def test_rerunning_full_pipeline_is_idempotent(self):
        self.write_full_dataset()
        self.run_all_stages()
        self.run_all_stages()

        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 1)
        self.assertEqual(Lecture.objects.count(), 1)
        self.assertEqual(LectureTopic.objects.count(), 1)
        self.assertEqual(Exam.objects.count(), 1)

    def test_lecture_topic_for_self_study_subject_creates_undated_lecture(self):
        self.write("subjects.csv", "code,name,display_order\nP,Physics,1\nE,English,2\n")
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)  # no CLASS row for E at all
        self.write(
            "lecture_topics.csv",
            "lecture_code,subject_code,chapter_no,topic,display_order\n"
            f"P-01,P,{_chapter_ref(1)},Vectors intro,1\n"
            "E-01,E,Essay basics,Essay writing,1\n",
        )
        self.write("exams.csv", EXAMS_CSV)
        self.run_all_stages()

        e01 = Lecture.objects.get(lecture_code="E-01")
        self.assertIsNone(e01.lecture_date)
        self.assertEqual(LectureTopic.objects.filter(lecture=e01).count(), 1)
        self.assertIsNone(LectureTopic.objects.get(lecture=e01).chapter)

    def test_bad_row_rolls_back_entire_stage(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write(
            "chapters.csv",
            "subject_code,paper,chapter_no,chapter_name,display_order\n"
            "P,1,1,Vector,1\n"
            "P,9,2,BadPaper,2\n",  # paper must be 1 or 2
        )
        SubjectImporter(self.base_dir, self.stdout).run()
        with self.assertRaises(ImportValidationError):
            ChapterImporter(self.base_dir, self.stdout).run()
        self.assertEqual(Chapter.objects.count(), 0)  # entire stage rolled back


class ExamDetailViewTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.client.force_login(self.data["user"])

    def test_renders_dedicated_fields_directly(self):
        exam = self.data["exams"]["we01"]
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, exam.exam_code)

    def test_covered_lecture_rows_resolve_real_and_undated_lectures(self):
        exam = self.data["exams"]["we02"]  # covers only P-06 (undated)
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        rows = response.context["covered_lecture_rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["lecture"].lecture_code, "P-06")
        self.assertContains(response, "self-study / no live class")

    def test_unknown_exam_id_404s(self):
        response = self.client.get(reverse("exam-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_query_count_is_small_and_fixed(self):
        # Milestone 12 added Covered Subjects/Chapters, a Readiness row
        # (get_exam_readiness()), and per-lecture Exam Ready badges
        # (get_exam_ready_lecture_codes()) - each a small, fixed-cost
        # addition (not scaling with lecture/topic count), budget raised
        # 5->10 to reflect that real, bounded addition (see
        # PROJECT_PROGRESS.md's Query Count Summary).
        exam = self.data["exams"]["we01"]
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertLessEqual(len(ctx.captured_queries), 10)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        exam = self.data["exams"]["we01"]
        response = self.client.get(reverse("exam-detail", args=[exam.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
