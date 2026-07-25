"""Milestone 10 - Import & Dataset Management tests.

Kept in a separate module (matching the `progress/tests_revision.py`
precedent from Milestone 9) - Django's default `DiscoverRunner` test
pattern (`test*.py`) picks this up automatically.

Every test that actually runs an import (`call_command("import_csv")`,
`rollback_dataset`) overrides `DATASET_ARCHIVE_ROOT` to a temp
directory, so the test suite never writes into the real project's
`data/dataset_archive/` folder.
"""

import io
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from lectures.models import LectureTopic
from routines.models import DatasetVersion, Exam, ImportLog, Lecture
from routines.services.csv.validators import ImportValidationError
from routines.services.dataset import comparison, statistics, versioning
from routines.services.dataset.rollback import RollbackError, rollback_to
from routines.tests import CHAPTERS_CSV, EXAMS_CSV, ROUTINE_CSV, SUBJECTS_CSV, _chapter_ref, lecture_topics_csv
from subjects.models import Chapter, Subject


class DatasetTestCase(TestCase):
    """Base class: a temp source-CSV directory plus a temp archive
    root, so real imports triggered in tests never touch the actual
    project's CSVs or `data/dataset_archive/`."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmpdir.name)
        self.addCleanup(self.tmpdir.cleanup)

        self.archive_tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.archive_tmpdir.cleanup)
        self._settings_override = override_settings(
            DATASET_ARCHIVE_ROOT=self.archive_tmpdir.name
        )
        self._settings_override.enable()
        self.addCleanup(self._settings_override.disable)

    def write(self, filename, content):
        (self.base_dir / filename).write_text(content, encoding="utf-8")

    def write_full_dataset(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)

    def call_import(self, **options):
        out = io.StringIO()
        options.setdefault("dir", str(self.base_dir))
        call_command("import_csv", stdout=out, **options)
        return out.getvalue()


# ---------------------------------------------------------------------
# versioning.py
# ---------------------------------------------------------------------

class VersioningTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()

    def test_checksum_is_deterministic(self):
        self.assertEqual(versioning.compute_checksum(self.base_dir), versioning.compute_checksum(self.base_dir))

    def test_checksum_changes_when_a_file_changes(self):
        before = versioning.compute_checksum(self.base_dir)
        self.write("subjects.csv", SUBJECTS_CSV + "E,English,2\n")
        after = versioning.compute_checksum(self.base_dir)
        self.assertNotEqual(before, after)

    def test_archive_source_csvs_copies_all_five_files(self):
        archive_path = versioning.archive_source_csvs(self.base_dir, "test-version")
        for filename in versioning.DATASET_FILES:
            self.assertTrue((archive_path / filename).exists())
        self.assertEqual(
            (archive_path / "subjects.csv").read_text(encoding="utf-8"),
            (self.base_dir / "subjects.csv").read_text(encoding="utf-8"),
        )

    def test_create_dataset_version_not_active_by_default(self):
        version = versioning.create_dataset_version(self.base_dir, {"subject_count": 1})
        self.assertFalse(version.is_active)
        self.assertTrue(version.version_name)
        self.assertEqual(len(version.checksum), 64)

    def test_activate_version_deactivates_others(self):
        v1 = versioning.create_dataset_version(self.base_dir, {}, version_name="v1")
        v2 = versioning.create_dataset_version(self.base_dir, {}, version_name="v2")
        versioning.activate_version(v1)
        versioning.activate_version(v2)

        v1.refresh_from_db()
        v2.refresh_from_db()
        self.assertFalse(v1.is_active)
        self.assertTrue(v2.is_active)
        self.assertEqual(DatasetVersion.objects.filter(is_active=True).count(), 1)

    def test_get_active_version(self):
        version = versioning.create_dataset_version(self.base_dir, {}, version_name="v1")
        self.assertIsNone(versioning.get_active_version())
        versioning.activate_version(version)
        self.assertEqual(versioning.get_active_version(), version)

    def test_get_previous_version_orders_by_imported_at(self):
        v1 = versioning.create_dataset_version(self.base_dir, {}, version_name="v1")
        v2 = versioning.create_dataset_version(self.base_dir, {}, version_name="v2")
        versioning.activate_version(v2)
        self.assertEqual(versioning.get_previous_version(), v1)

    def test_get_previous_version_none_when_only_one_exists(self):
        v1 = versioning.create_dataset_version(self.base_dir, {}, version_name="v1")
        versioning.activate_version(v1)
        self.assertIsNone(versioning.get_previous_version())

    def test_imported_by_never_hardcoded(self):
        user = User.objects.create_user("carol", password="x")
        version = versioning.create_dataset_version(self.base_dir, {}, user=user)
        self.assertEqual(version.imported_by, user)
        version2 = versioning.create_dataset_version(self.base_dir, {}, version_name="v-anon")
        self.assertIsNone(version2.imported_by)


# ---------------------------------------------------------------------
# statistics.py
# ---------------------------------------------------------------------

class StatisticsTests(DatasetTestCase):
    def test_statistics_match_imported_data(self):
        self.write_full_dataset()
        self.call_import()

        stats = statistics.collect_statistics(self.base_dir)
        self.assertEqual(stats["subject_count"], Subject.objects.count())
        self.assertEqual(stats["chapter_count"], Chapter.objects.count())
        self.assertEqual(stats["lecture_count"], Lecture.objects.count())
        self.assertEqual(stats["lecture_topic_count"], LectureTopic.objects.count())
        self.assertEqual(stats["exam_count"], Exam.objects.count())
        self.assertEqual(stats["routine_event_count"], 1)  # one routine.csv row in the fixture


# ---------------------------------------------------------------------
# comparison.py
# ---------------------------------------------------------------------

class ComparisonTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()
        self.call_import()

    def test_unchanged_when_csvs_match_database(self):
        diff = comparison.compare_all(self.base_dir)
        self.assertEqual(len(diff["subjects"]["unchanged"]), 1)
        self.assertEqual(diff["subjects"]["added"], [])
        self.assertEqual(diff["subjects"]["modified"], [])
        self.assertEqual(diff["subjects"]["removed"], [])

    def test_subject_added(self):
        self.write("subjects.csv", SUBJECTS_CSV + "E,English,2\n")
        diff = comparison.compare_subjects(self.base_dir)
        self.assertEqual([e["key"] for e in diff["added"]], ["E"])
        self.assertEqual(len(diff["unchanged"]), 1)

    def test_subject_modified(self):
        self.write("subjects.csv", "code,name,display_order\nP,Physics Renamed,1\n")
        diff = comparison.compare_subjects(self.base_dir)
        self.assertEqual(len(diff["modified"]), 1)
        self.assertIn("name", diff["modified"][0]["changes"])
        self.assertEqual(diff["modified"][0]["changes"]["name"]["old"], "Physics")
        self.assertEqual(diff["modified"][0]["changes"]["name"]["new"], "Physics Renamed")

    def test_subject_removed(self):
        self.write("subjects.csv", "code,name,display_order\n")
        diff = comparison.compare_subjects(self.base_dir)
        self.assertEqual([e["key"] for e in diff["removed"]], ["P"])

    def test_chapter_comparison(self):
        self.write(
            "chapters.csv",
            "subject_code,paper,chapter_no,chapter_name,display_order\nP,1,1,Vector Renamed,1\n",
        )
        diff = comparison.compare_chapters(self.base_dir)
        self.assertEqual(len(diff["modified"]), 1)
        self.assertIn("chapter_name", diff["modified"][0]["changes"])

    def test_lecture_comparison_detects_title_change(self):
        self.write(
            "routine.csv",
            "date,day,event_type,subject_code,lecture_code,title,start_time,end_time,notes\n"
            "2026-01-01,Thu,CLASS,P,P-01,Physics 1 Renamed,,,\n",
        )
        diff = comparison.compare_lectures(self.base_dir)
        self.assertEqual(len(diff["modified"]), 1)
        self.assertIn("title", diff["modified"][0]["changes"])

    def test_lecture_topic_comparison_detects_display_order_change(self):
        self.write(
            "lecture_topics.csv",
            "lecture_code,subject_code,chapter_no,topic,display_order\n"
            f"P-01,P,{_chapter_ref(1)},Vectors intro,2\n",
        )
        diff = comparison.compare_lecture_topics(self.base_dir)
        self.assertEqual(len(diff["modified"]), 1)
        self.assertIn("display_order", diff["modified"][0]["changes"])

    def test_exam_comparison_detects_date_change(self):
        self.write(
            "exams.csv",
            "exam_code,exam_type,title,lecture_codes,exam_date,online_start,online_end\n"
            "WE-01,WEEKLY,Weekly Exam 1,P-01,2026-02-01,,\n",
        )
        diff = comparison.compare_exams(self.base_dir)
        self.assertEqual(len(diff["modified"]), 1)
        self.assertIn("exam_date", diff["modified"][0]["changes"])

    def test_routine_events_summary(self):
        result = comparison.compare_routine_events(self.base_dir)
        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["by_event_type"], {"CLASS": 1})
        self.assertEqual(result["class_rows_unchanged"], 1)

    def test_compare_all_includes_every_section(self):
        diff = comparison.compare_all(self.base_dir)
        for key in ("subjects", "chapters", "lectures", "lecture_topics", "exams", "routine_events"):
            self.assertIn(key, diff)


class DuplicateDetectionTests(DatasetTestCase):
    def test_duplicate_subject_code(self):
        self.write("subjects.csv", "code,name,display_order\nP,Physics,1\nP,Physics Two,2\n")
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertIn("P", dupes["subjects"])

    def test_duplicate_chapter_key(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write(
            "chapters.csv",
            "subject_code,paper,chapter_no,chapter_name,display_order\n"
            "P,1,1,Vector,1\nP,1,1,Vector Dup,2\n",
        )
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertIn(("P", "1", "1"), dupes["chapters"])

    def test_duplicate_class_lecture_code(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write(
            "routine.csv",
            "date,day,event_type,subject_code,lecture_code,title,start_time,end_time,notes\n"
            "2026-01-01,Thu,CLASS,P,P-01,Physics 1,,,\n"
            "2026-01-08,Thu,CLASS,P,P-01,Physics 1 Again,,,\n",
        )
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertIn("P-01", dupes["lectures"])

    def test_duplicate_topic(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write(
            "lecture_topics.csv",
            "lecture_code,subject_code,chapter_no,topic,display_order\n"
            f"P-01,P,{_chapter_ref(1)},Vectors intro,1\n"
            f"P-01,P,{_chapter_ref(1)},Vectors intro,2\n",
        )
        self.write("exams.csv", EXAMS_CSV)
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertIn(("P-01", "Vectors intro"), dupes["lecture_topics"])

    def test_duplicate_exam_code(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write(
            "exams.csv",
            "exam_code,exam_type,title,lecture_codes,exam_date,online_start,online_end\n"
            "WE-01,WEEKLY,Weekly Exam 1,P-01,2026-01-10,,\n"
            "WE-01,WEEKLY,Weekly Exam 1 Dup,P-01,2026-01-11,,\n",
        )
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertIn("WE-01", dupes["exams"])

    def test_no_duplicates_in_clean_dataset(self):
        self.write("subjects.csv", SUBJECTS_CSV)
        self.write("chapters.csv", CHAPTERS_CSV)
        self.write("routine.csv", ROUTINE_CSV)
        self.write("lecture_topics.csv", lecture_topics_csv())
        self.write("exams.csv", EXAMS_CSV)
        dupes = comparison.detect_duplicates(self.base_dir)
        self.assertFalse(comparison.has_duplicates(dupes))


# ---------------------------------------------------------------------
# import_csv command extensions
# ---------------------------------------------------------------------

class ImportCsvNormalPathTests(DatasetTestCase):
    """Regression coverage: the existing (pre-Milestone-10) import
    behavior must be unchanged."""

    def setUp(self):
        super().setUp()
        self.write_full_dataset()

    def test_real_import_creates_and_activates_dataset_version(self):
        self.call_import()
        version = DatasetVersion.objects.get()
        self.assertTrue(version.is_active)
        self.assertEqual(version.statistics["subject_count"], 1)

    def test_real_import_creates_success_import_log(self):
        self.call_import()
        log = ImportLog.objects.get()
        self.assertEqual(log.status, ImportLog.Status.SUCCESS)
        self.assertIsNotNone(log.dataset_version)
        self.assertEqual(log.imported_counts["subjects"], 1)
        self.assertGreaterEqual(log.duration_seconds, 0)

    def test_rerunning_import_creates_a_second_version_and_activates_it(self):
        self.call_import()
        v1 = DatasetVersion.objects.get()
        self.call_import()
        v2 = DatasetVersion.objects.exclude(pk=v1.pk).get()

        v1.refresh_from_db()
        self.assertFalse(v1.is_active)
        self.assertTrue(v2.is_active)

    def test_import_still_idempotent_on_actual_rows(self):
        self.call_import()
        self.call_import()
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Exam.objects.count(), 1)

    def test_user_flag_resolves_to_real_user(self):
        user = User.objects.create_user("dave", password="x")
        self.call_import(user="dave")
        version = DatasetVersion.objects.get()
        self.assertEqual(version.imported_by, user)

    def test_unknown_user_flag_does_not_crash(self):
        self.call_import(user="nonexistent")
        version = DatasetVersion.objects.get()
        self.assertIsNone(version.imported_by)

    def test_failed_import_creates_failed_log_and_no_dataset_version(self):
        self.write("subjects.csv", "code,name\nP,Physics\n")  # missing display_order column
        with self.assertRaises(SystemExit):
            self.call_import()
        log = ImportLog.objects.get()
        self.assertEqual(log.status, ImportLog.Status.FAILED)
        self.assertTrue(log.errors)
        self.assertFalse(DatasetVersion.objects.exists())

    def test_normal_import_output_unchanged(self):
        output = self.call_import()
        self.assertIn("Importing subjects...", output)
        self.assertIn("Import completed successfully.", output)


class ImportCsvPreviewTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()
        self.call_import()  # establish a baseline in the DB

    def test_preview_writes_nothing(self):
        self.write("subjects.csv", SUBJECTS_CSV + "E,English,2\n")
        before_subjects = Subject.objects.count()
        before_versions = DatasetVersion.objects.count()

        self.call_import(preview=True)

        self.assertEqual(Subject.objects.count(), before_subjects)
        self.assertEqual(DatasetVersion.objects.count(), before_versions)

    def test_preview_creates_a_preview_import_log(self):
        self.call_import(preview=True)
        log = ImportLog.objects.filter(status=ImportLog.Status.PREVIEW).get()
        self.assertIsNone(log.dataset_version)

    def test_preview_reports_added_and_unchanged(self):
        self.write("subjects.csv", SUBJECTS_CSV + "E,English,2\n")
        output = self.call_import(preview=True)
        self.assertIn("Subjects: 1 added", output)

    def test_preview_reports_validation_failure_without_writing(self):
        self.write("subjects.csv", "code,name\nP,Physics\n")
        with self.assertRaises(SystemExit):
            self.call_import(preview=True)
        self.assertEqual(Subject.objects.count(), 1)  # unchanged
        log = ImportLog.objects.filter(status=ImportLog.Status.PREVIEW).latest("started_at")
        self.assertTrue(log.errors)

    def test_preview_reports_duplicates(self):
        # The pre-flight duplicate scan reports the duplicate first;
        # the same duplicate then also trips the importer's own
        # DuplicateTracker during validate_only() (defense-in-depth,
        # per its docstring), so preview still exits non-zero - the
        # report is printed either way, which is what this test checks.
        self.write("subjects.csv", "code,name,display_order\nP,Physics,1\nP,Physics Two,2\n")
        out = io.StringIO()
        with self.assertRaises(SystemExit):
            call_command("import_csv", dir=str(self.base_dir), preview=True, stdout=out)
        self.assertIn("Duplicate keys found", out.getvalue())


class ImportCsvDryRunTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()

    def test_dry_run_rolls_back_completely(self):
        self.call_import(dry_run=True)
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(Chapter.objects.count(), 0)
        self.assertEqual(Lecture.objects.count(), 0)
        self.assertEqual(Exam.objects.count(), 0)
        self.assertFalse(DatasetVersion.objects.exists())

    def test_dry_run_creates_dry_run_import_log(self):
        self.call_import(dry_run=True)
        log = ImportLog.objects.get()
        self.assertEqual(log.status, ImportLog.Status.DRY_RUN)
        self.assertEqual(log.imported_counts["subjects"], 1)

    def test_dry_run_output_mentions_rollback(self):
        output = self.call_import(dry_run=True)
        self.assertIn("rolling back now", output)
        self.assertIn("Database is unchanged", output)

    def test_dry_run_on_invalid_dataset_still_rolls_back_and_logs_failure(self):
        self.write("chapters.csv", "subject_code,paper,chapter_no,chapter_name,display_order\nX,1,1,Bad,1\n")
        with self.assertRaises(SystemExit):
            self.call_import(dry_run=True)
        self.assertEqual(Chapter.objects.count(), 0)
        log = ImportLog.objects.get()
        self.assertEqual(log.status, ImportLog.Status.DRY_RUN)
        self.assertTrue(log.errors)

    def test_dry_run_does_not_affect_a_subsequent_real_import(self):
        self.call_import(dry_run=True)
        self.call_import()
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(DatasetVersion.objects.count(), 1)


# ---------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------

class RollbackServiceTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()
        self.call_import()
        self.v1 = DatasetVersion.objects.get()

        # A second version with a renamed subject.
        self.write("subjects.csv", "code,name,display_order\nP,Physics Renamed,1\n")
        self.call_import()
        self.v2 = DatasetVersion.objects.exclude(pk=self.v1.pk).get()

    def test_rollback_restores_previous_data(self):
        self.assertEqual(Subject.objects.get(code="P").name, "Physics Renamed")
        rollback_to(self.v1)
        self.assertEqual(Subject.objects.get(code="P").name, "Physics")

    def test_rollback_reactivates_target_version(self):
        rollback_to(self.v1)
        self.v1.refresh_from_db()
        self.v2.refresh_from_db()
        self.assertTrue(self.v1.is_active)
        self.assertFalse(self.v2.is_active)

    def test_rollback_creates_rollback_import_log(self):
        rollback_to(self.v1)
        log = ImportLog.objects.filter(status=ImportLog.Status.ROLLBACK).get()
        self.assertEqual(log.dataset_version, self.v1)

    def test_rollback_is_atomic_on_missing_archive(self):
        import shutil
        shutil.rmtree(self.v1.source)
        with self.assertRaises(RollbackError):
            rollback_to(self.v1)
        # nothing changed - still on v2's data
        self.assertEqual(Subject.objects.get(code="P").name, "Physics Renamed")

    def test_rollback_dataset_command_default_target(self):
        out = io.StringIO()
        call_command("rollback_dataset", stdout=out)
        self.assertEqual(Subject.objects.get(code="P").name, "Physics")
        self.assertIn("Rolled back successfully", out.getvalue())

    def test_rollback_dataset_command_explicit_target(self):
        out = io.StringIO()
        call_command("rollback_dataset", to=self.v1.version_name, stdout=out)
        self.assertEqual(Subject.objects.get(code="P").name, "Physics")

    def test_rollback_dataset_command_unknown_version_errors(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit):
            call_command("rollback_dataset", to="does-not-exist", stdout=out)

    def test_rollback_dataset_command_no_previous_version_errors(self):
        DatasetVersion.objects.exclude(pk=self.v2.pk).delete()
        out = io.StringIO()
        with self.assertRaises(SystemExit):
            call_command("rollback_dataset", stdout=out)


# ---------------------------------------------------------------------
# compare_dataset command
# ---------------------------------------------------------------------

class CompareDatasetCommandTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()
        self.call_import()

    def test_runs_without_writing_anything(self):
        before = Subject.objects.count()
        out = io.StringIO()
        call_command("compare_dataset", dir=str(self.base_dir), stdout=out)
        self.assertEqual(Subject.objects.count(), before)
        self.assertIn("Comparison complete", out.getvalue())

    def test_reports_changes(self):
        self.write("subjects.csv", SUBJECTS_CSV + "E,English,2\n")
        out = io.StringIO()
        call_command("compare_dataset", dir=str(self.base_dir), stdout=out)
        self.assertIn("Added: 1", out.getvalue())


# ---------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------

class DatasetHistoryViewTests(DatasetTestCase):
    def setUp(self):
        super().setUp()
        self.write_full_dataset()
        self.call_import()
        # Milestone 12, Phase 9: dataset management is staff-only.
        self.user = User.objects.create_user("erin", password="x", is_staff=True)
        self.client.force_login(self.user)

    def test_full_page_response(self):
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "Active")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("dataset-history"), HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "<html")

    def test_context_contains_active_version(self):
        response = self.client.get(reverse("dataset-history"))
        self.assertIsNotNone(response.context["active_version"])
        self.assertEqual(response.context["versions"].count(), 1)
        self.assertEqual(len(response.context["import_logs"]), 1)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_empty_state_when_nothing_imported(self):
        DatasetVersion.objects.all().delete()
        ImportLog.objects.all().delete()
        response = self.client.get(reverse("dataset-history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No dataset has been imported yet.")


class DatasetCompareViewTests(TestCase):
    """Uses the real project CSVs (via settings.BASE_DIR, the view's
    own default) against a freshly-imported-from-fixture database, so
    intentionally does NOT inherit DatasetTestCase's temp base_dir -
    this page always compares against whatever is in the project
    root, matching its own documented behavior."""

    def setUp(self):
        # Milestone 12, Phase 9: dataset management is staff-only.
        self.user = User.objects.create_user("frank", password="x", is_staff=True)
        self.client.force_login(self.user)

    def test_full_page_response(self):
        response = self.client.get(reverse("dataset-compare"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<html")
        self.assertContains(response, "Routine Events")

    def test_htmx_partial_response(self):
        response = self.client.get(reverse("dataset-compare"), HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "<html")

    def test_filter_by_entity(self):
        response = self.client.get(reverse("dataset-compare"), {"entity": "subjects"})
        self.assertEqual(len(response.context["sections"]), 1)
        self.assertEqual(response.context["sections"][0]["key"], "subjects")

    def test_filter_by_change_type(self):
        response = self.client.get(reverse("dataset-compare"), {"change": "added"})
        for section in response.context["sections"]:
            self.assertEqual(set(section["data"].keys()), {"added"})

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("dataset-compare"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_query_count_within_budget(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("dataset-compare"))
        self.assertLessEqual(len(ctx.captured_queries), 20)
