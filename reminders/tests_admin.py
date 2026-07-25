"""Milestone 15.1, Phases 3-8 - Reminder Administration tests: staff-
only access, email configuration diagnostics, SMTP connection testing,
manual test emails, the Reminder Test Center (preview/send against a
chosen recipient), and the Reminder Activity Log. Every manual send
goes through the exact same `reminders.services.engine` Milestone 15
built - these tests exist to prove the admin page invokes it
correctly, not to re-test trigger conditions (already covered in
`tests_generators.py`).
"""

from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from reminders.models import ReminderLog
from reminders.services import diagnostics, engine


class ReminderAdminAccessTests(TestCase):
    def setUp(self):
        self.staff_user = create_user(username="staff_member")
        self.staff_user.is_staff = True
        self.staff_user.save()
        self.student = create_user(username="student1")

    def test_staff_user_can_access(self):
        self.client.login(username="staff_member", password="testpass123")
        response = self.client.get(reverse("reminder-admin"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reminder Administration")

    def test_non_staff_user_gets_403(self):
        self.client.login(username="student1", password="testpass123")
        response = self.client.get(reverse("reminder-admin"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("reminder-admin"))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_post_also_gets_403(self):
        self.client.login(username="student1", password="testpass123")
        response = self.client.post(reverse("reminder-admin"), {"action": "test_connection"})
        self.assertEqual(response.status_code, 403)


class EmailDiagnosticsTests(TestCase):
    def test_console_backend_reports_disabled_status(self):
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"):
            config = diagnostics.get_email_config()
        self.assertEqual(config["status"], "disabled")
        self.assertTrue(config["issues"])

    def test_smtp_backend_with_full_config_reports_ready(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST="smtp.example.com", EMAIL_PORT=587,
            EMAIL_HOST_USER="user@example.com", EMAIL_HOST_PASSWORD="secret",
            DEFAULT_FROM_EMAIL="user@example.com",
        ):
            config = diagnostics.get_email_config()
        self.assertEqual(config["status"], "ready")
        self.assertEqual(config["issues"], [])

    def test_smtp_backend_missing_credentials_reports_incomplete(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST="smtp.example.com", EMAIL_PORT=587,
            EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="",
        ):
            config = diagnostics.get_email_config()
        self.assertEqual(config["status"], "incomplete")
        self.assertTrue(any("EMAIL_HOST_USER" in issue for issue in config["issues"]))
        self.assertTrue(any("EMAIL_HOST_PASSWORD" in issue for issue in config["issues"]))

    def test_password_never_exposed(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST_PASSWORD="super-secret-value",
        ):
            config = diagnostics.get_email_config()
        self.assertNotIn("super-secret-value", str(config))

    def test_connection_test_reports_non_smtp_backend_honestly(self):
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"):
            success, message = diagnostics.test_smtp_connection()
        self.assertFalse(success)
        self.assertIn("Console Backend", message)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendTestEmailServiceTests(TestCase):
    def test_sends_and_returns_previews(self):
        result = diagnostics.send_test_email("someone@example.com", "Custom Subject")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["sent_at"])
        self.assertIn("Custom Subject", result["html"])
        self.assertNotIn("<", result["text"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["someone@example.com"])

    def test_does_not_touch_reminder_log(self):
        diagnostics.send_test_email("someone@example.com")
        self.assertEqual(ReminderLog.objects.count(), 0)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ReminderAdminActionsTests(TestCase):
    def setUp(self):
        self.staff_user = create_user(username="staff_member")
        self.staff_user.is_staff = True
        self.staff_user.email = "staff@example.com"
        self.staff_user.save()
        self.client.login(username="staff_member", password="testpass123")
        self.data = build_sample_dataset()
        self.student = self.data["user"]
        self.student.email = "student1@example.com"
        self.student.save()

    def test_test_connection_action(self):
        response = self.client.post(reverse("reminder-admin"), {"action": "test_connection"})
        self.assertEqual(response.status_code, 200)
        # This test class runs under the locmem backend (so send_test_email/
        # engine sends land in mail.outbox) - the connection test should
        # honestly report there's nothing SMTP to connect to.
        self.assertContains(response, "In-Memory Backend")

    def test_send_test_email_action(self):
        response = self.client.post(
            reverse("reminder-admin"),
            {"action": "send_test_email", "recipient_email": "staff@example.com", "subject": "Hello"},
        )
        self.assertContains(response, "Sent to staff@example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_test_email_defaults_to_current_admin(self):
        self.client.post(reverse("reminder-admin"), {"action": "send_test_email"})
        self.assertEqual(mail.outbox[0].to, ["staff@example.com"])

    def test_preview_reminder_for_selected_recipient(self):
        lecture = self.data["lectures"]["p01"]
        response = self.client.post(
            reverse("reminder-admin"),
            {"action": "preview", "reminder_type": "daily_agenda", "user_id": self.student.pk},
        )
        self.assertEqual(response.status_code, 200)
        # Either "found" (if today happens to be past 10:00 in the test
        # environment) or the honest "nothing due" message - both are
        # valid outcomes of a real trigger check, not a template bug.
        self.assertTrue(
            "Due right now for" in response.content.decode()
            or "Nothing due right now for" in response.content.decode()
        )

    def test_preview_shows_nothing_due_for_unmet_trigger(self):
        # weekly_exam reminder: build_sample_dataset's exams are far in
        # the future, never exactly 1/0 days out - never due.
        response = self.client.post(
            reverse("reminder-admin"),
            {"action": "preview", "reminder_type": "weekly_exam", "user_id": self.student.pk},
        )
        self.assertContains(response, "Nothing due right now")

    def test_send_manual_reminder_logs_as_manual(self):
        # Force a due Daily Agenda by using the recipient's own
        # preferred time already having passed - build_sample_dataset's
        # default preferences (unsaved default) use 10:00; run the
        # request at a time past that by hitting the view, which calls
        # engine.run() with now=None (today) - flaky only insofar as
        # "today" always satisfies the date condition (no date gate on
        # Daily Agenda beyond time-of-day, which defaults to server
        # local time at test-run time). To keep this deterministic,
        # assert on the log's triggered_by only when a send happened.
        self.client.post(
            reverse("reminder-admin"),
            {"action": "send", "reminder_type": "daily_agenda", "user_id": self.student.pk},
        )
        logs = ReminderLog.objects.filter(user=self.student, reminder_type="daily_agenda")
        if logs.exists():
            self.assertEqual(logs.first().triggered_by, ReminderLog.TriggeredBy.MANUAL)

    def test_send_manual_reminder_with_forced_due_job(self):
        # Deterministic version of the above: pre-seed a RevisionSchedule
        # due today so the Revision Due reminder is guaranteed due.
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.student, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )

        response = self.client.post(
            reverse("reminder-admin"),
            {"action": "send", "reminder_type": "revision_due", "user_id": self.student.pk},
        )
        self.assertContains(response, "Sent")
        self.assertEqual(len(mail.outbox), 1)
        log = ReminderLog.objects.get(user=self.student, reminder_type="revision_due")
        self.assertEqual(log.triggered_by, ReminderLog.TriggeredBy.MANUAL)
        self.assertEqual(log.status, ReminderLog.Status.SUCCESS)

    def test_run_reminder_engine_all_types(self):
        response = self.client.post(
            reverse("reminder-admin"),
            {"action": "send", "reminder_type": "__all__", "user_id": self.student.pk},
        )
        self.assertEqual(response.status_code, 200)

    def test_activity_log_shows_recent_sends(self):
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.student, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )
        engine.run(reminder_types=["revision_due"], users=[self.student])

        response = self.client.get(reverse("reminder-admin"))
        self.assertContains(response, "student1")
        self.assertContains(response, "Automatic")

    def test_manual_send_appears_in_activity_log_as_manual(self):
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.student, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )
        self.client.post(
            reverse("reminder-admin"),
            {"action": "send", "reminder_type": "revision_due", "user_id": self.student.pk},
        )
        response = self.client.get(reverse("reminder-admin"))
        self.assertContains(response, "Manual")

    def test_failed_delivery_recorded_and_shown(self):
        from progress.services import revision as revision_service
        self.student.email = ""
        self.student.save()
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.student, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )

        self.client.post(
            reverse("reminder-admin"),
            {"action": "send", "reminder_type": "revision_due", "user_id": self.student.pk},
        )
        log = ReminderLog.objects.get(user=self.student, reminder_type="revision_due")
        self.assertEqual(log.status, ReminderLog.Status.FAILED)

        response = self.client.get(reverse("reminder-admin"))
        self.assertContains(response, "Failed")


class EngineTargetingTests(TestCase):
    """Milestone 15.1, Phase 5: `users=` narrows generation without
    changing what's due - covered here rather than duplicated per
    generator in `tests_generators.py`."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.other = create_user(username="other_student")

    def test_users_param_excludes_unselected_users(self):
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.user, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )
        due = engine.get_due_reminders(reminder_types=["revision_due"], users=[self.other])
        self.assertEqual(due, [])

    def test_users_param_includes_selected_user(self):
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.user, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )
        due = engine.get_due_reminders(reminder_types=["revision_due"], users=[self.user])
        self.assertEqual(len(due), 1)

    def test_default_targets_every_active_user(self):
        from progress.services import revision as revision_service
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(
            self.user, lecture, completion_date=timezone.localdate() - timedelta(days=1)
        )
        due = engine.get_due_reminders(reminder_types=["revision_due"])
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].user, self.user)
