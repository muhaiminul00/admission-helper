"""Routine Archive tests (Milestone 14, Phase 1): filesystem discovery
service (`routines.services.archive`) and the `/routine/resources/`
viewer + `/routine/resources/file/<filename>/` download endpoints.
Each test gets its own temporary MEDIA_ROOT so no test depends on (or
pollutes) a real `media/routines/` folder.
"""

import shutil
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from core.test_utils import create_user
from routines.services import archive


def _make_media_root():
    return Path(tempfile.mkdtemp())


def _write_pdf(media_root, filename, content=b"%PDF-1.4 fake"):
    routines_dir = media_root / "routines"
    routines_dir.mkdir(parents=True, exist_ok=True)
    (routines_dir / filename).write_bytes(content)


class RoutineArchiveServiceTests(TestCase):
    def setUp(self):
        self.media_root = _make_media_root()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def test_empty_archive_returns_no_entries(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            self.assertEqual(archive.list_routines(), [])
            self.assertIsNone(archive.get_latest_routine())

    def test_missing_routines_directory_does_not_raise(self):
        # media_root exists but routines/ inside it was never created -
        # e.g. a fresh clone before any PDF has ever been added.
        with override_settings(MEDIA_ROOT=self.media_root):
            self.assertEqual(archive.list_routines(), [])

    def test_sorted_descending_by_filename(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        _write_pdf(self.media_root, "2026-08.pdf")
        _write_pdf(self.media_root, "2026-06.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            entries = archive.list_routines()
        self.assertEqual([e.filename for e in entries], ["2026-08.pdf", "2026-06.pdf", "2026-05.pdf"])

    def test_latest_routine_is_newest_by_filename(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            latest = archive.get_latest_routine()
        self.assertEqual(latest.filename, "2026-08.pdf")

    def test_non_pdf_files_are_ignored(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        (self.media_root / "routines" / "notes.txt").write_text("not a routine")
        (self.media_root / "routines" / "2026-05.pdf.bak").write_text("not a pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            entries = archive.list_routines()
        self.assertEqual([e.filename for e in entries], ["2026-05.pdf"])

    def test_malformed_filenames_are_ignored(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        for bad_name in ["routine.pdf", "2026-5.pdf", "26-05.pdf", "2026-13-extra.pdf"]:
            _write_pdf(self.media_root, bad_name)
        with override_settings(MEDIA_ROOT=self.media_root):
            entries = archive.list_routines()
        self.assertEqual([e.filename for e in entries], ["2026-05.pdf"])

    def test_subdirectories_inside_routines_are_ignored(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        (self.media_root / "routines" / "2026-99.pdf").mkdir()
        with override_settings(MEDIA_ROOT=self.media_root):
            entries = archive.list_routines()
        self.assertEqual([e.filename for e in entries], ["2026-05.pdf"])

    def test_resolve_valid_filename_returns_path(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            path = archive.resolve_routine_file("2026-05.pdf")
        self.assertIsNotNone(path)
        self.assertTrue(path.is_file())

    def test_resolve_rejects_path_traversal(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            self.assertIsNone(archive.resolve_routine_file("../../etc/passwd"))
            self.assertIsNone(archive.resolve_routine_file("..%2f..%2f2026-05.pdf"))
            self.assertIsNone(archive.resolve_routine_file("2026-05.pdf/../../secret"))

    def test_resolve_rejects_nonexistent_file(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            self.assertIsNone(archive.resolve_routine_file("2026-05.pdf"))

    def test_resolve_rejects_non_matching_filename(self):
        _write_pdf(self.media_root, "notes.txt")
        with override_settings(MEDIA_ROOT=self.media_root):
            self.assertIsNone(archive.resolve_routine_file("notes.txt"))


class RoutineResourcesViewTests(TestCase):
    def setUp(self):
        self.media_root = _make_media_root()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        self.user = create_user()
        self.client.login(username=self.user.username, password="testpass123")

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("routine-resources"))
        self.assertEqual(response.status_code, 302)

    def test_empty_archive_shows_empty_state(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"))
        self.assertContains(response, "No routine has been uploaded yet.")

    def test_latest_routine_selected_by_default(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"))
        self.assertContains(response, "Latest Routine")
        self.assertContains(response, reverse("routine-archive-file", args=["2026-08.pdf"]))

    def test_previous_routines_listed_excluding_selected(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"))
        self.assertContains(response, "2026-05")
        self.assertNotContains(response, ">2026-08<")

    def test_selecting_a_specific_routine(self):
        _write_pdf(self.media_root, "2026-05.pdf")
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"), {"routine": "2026-05.pdf"})
        self.assertContains(response, "Routine &middot; 2026-05")
        self.assertContains(response, reverse("routine-archive-file", args=["2026-05.pdf"]))

    def test_unknown_routine_param_falls_back_to_latest(self):
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"), {"routine": "does-not-exist.pdf"})
        self.assertContains(response, "Latest Routine")

    def test_htmx_request_returns_partial_only(self):
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-resources"), HTTP_HX_REQUEST="true")
        self.assertContains(response, "Latest Routine")
        self.assertNotContains(response, "<nav")


class RoutineArchiveFileViewTests(TestCase):
    def setUp(self):
        self.media_root = _make_media_root()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        self.user = create_user()
        self.client.login(username=self.user.username, password="testpass123")

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("routine-archive-file", args=["2026-08.pdf"]))
        self.assertEqual(response.status_code, 302)

    def test_serves_pdf_inline_by_default(self):
        _write_pdf(self.media_root, "2026-08.pdf", content=b"%PDF-1.4 hello")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-archive-file", args=["2026-08.pdf"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertNotIn("attachment", response.get("Content-Disposition", ""))
        response.close()

    def test_download_serves_as_attachment(self):
        _write_pdf(self.media_root, "2026-08.pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(
                reverse("routine-archive-file", args=["2026-08.pdf"]), {"download": "1"}
            )
        self.assertIn("attachment", response.get("Content-Disposition", ""))
        response.close()

    def test_nonexistent_file_404s(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-archive-file", args=["2026-08.pdf"]))
        self.assertEqual(response.status_code, 404)

    def test_path_traversal_filename_404s(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get("/routine/resources/file/..%2F..%2Fsecret.txt/")
        self.assertIn(response.status_code, (404, 400))

    def test_non_pdf_filename_404s(self):
        _write_pdf(self.media_root, "notes.txt", content=b"not a pdf")
        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.get(reverse("routine-archive-file", args=["notes.txt"]))
        self.assertEqual(response.status_code, 404)
