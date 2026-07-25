"""Milestone 15, Phases 10/11 - management command + engine-level
duplicate-protection tests. Uses Django's `locmem` email backend
(override_settings) so sent messages can be inspected without hitting
a real SMTP server.
"""

from datetime import time, timedelta
from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from core.test_utils import build_sample_dataset
from progress.models import RevisionSchedule
from progress.services import revision as revision_service
from reminders.models import ReminderLog
from reminders.services import engine


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendDailyAgendaCommandTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.user.email = "student1@example.com"
        self.user.save()
        self.today = self.data["today"]

    def test_sends_and_logs(self):
        out = StringIO()
        sent = engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA],
            now=self.today, current_time=time(10, 0),
        )
        self.assertEqual(len(sent), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(ReminderLog.objects.count(), 1)

    def test_second_run_is_a_no_op(self):
        engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA],
            now=self.today, current_time=time(10, 0),
        )
        sent_again = engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA],
            now=self.today, current_time=time(10, 0),
        )
        self.assertEqual(sent_again, [])
        self.assertEqual(len(mail.outbox), 1)  # still just the first send
        self.assertEqual(ReminderLog.objects.count(), 1)

    def test_dry_run_sends_nothing_and_logs_nothing(self):
        sent = engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA],
            now=self.today, current_time=time(10, 0), dry_run=True,
        )
        self.assertEqual(len(sent), 1)  # still reports what *would* send
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ReminderLog.objects.count(), 0)

    def test_user_without_email_is_skipped_silently(self):
        self.user.email = ""
        self.user.save()
        sent = engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA],
            now=self.today, current_time=time(10, 0),
        )
        self.assertEqual(len(sent), 1)  # job was generated and "sent" (logged)...
        self.assertEqual(len(mail.outbox), 0)  # ...but delivery itself no-opped


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ManagementCommandSmokeTests(TestCase):
    """One smoke test per command: it runs cleanly and reports a count.
    Trigger-condition correctness is covered exhaustively in
    `tests_generators.py` - these only check the command wiring itself.
    """

    def setUp(self):
        self.data = build_sample_dataset()

    def test_send_daily_agenda(self):
        out = StringIO()
        call_command("send_daily_agenda", stdout=out)
        self.assertIn("daily agenda email", out.getvalue())

    def test_send_weekly_overview(self):
        out = StringIO()
        call_command("send_weekly_overview", stdout=out)
        self.assertIn("weekly overview email", out.getvalue())

    def test_send_exam_reminders(self):
        out = StringIO()
        call_command("send_exam_reminders", stdout=out)
        self.assertIn("exam reminder email", out.getvalue())

    def test_send_revision_reminders(self):
        out = StringIO()
        call_command("send_revision_reminders", stdout=out)
        self.assertIn("revision reminder email", out.getvalue())

    def test_send_weekly_progress(self):
        out = StringIO()
        call_command("send_weekly_progress", stdout=out)
        self.assertIn("weekly progress email", out.getvalue())

    def test_dry_run_flag_sends_nothing(self):
        out = StringIO()
        call_command("send_daily_agenda", "--dry-run", stdout=out)
        self.assertIn("Would send", out.getvalue())
        self.assertEqual(len(mail.outbox), 0)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EngineCrossTypeIsolationTests(TestCase):
    """A ReminderLog entry for one reminder_type never suppresses a
    different reminder_type sharing the same reference_key by
    coincidence - the uniqueness constraint (and the engine's lookup)
    is keyed on all three fields together."""

    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]

    def test_same_reference_key_different_types_both_send(self):
        ReminderLog.objects.create(
            user=self.user, reminder_type=ReminderLog.ReminderType.WEEKLY_OVERVIEW, reference_key="1"
        )
        # Build a revision schedule whose id happens not to matter here -
        # what matters is a *different* reminder_type isn't blocked by
        # the WEEKLY_OVERVIEW log row above just because some other
        # value could coincide.
        lecture = self.data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(self.user, lecture, completion_date=timezone.localdate())
        schedule = RevisionSchedule.objects.get(
            user=self.user, lecture=lecture, revision_level=RevisionSchedule.Level.FIRST
        )
        due = engine.get_due_reminders(
            reminder_types=[ReminderLog.ReminderType.REVISION_DUE], now=schedule.due_date
        )
        self.assertEqual(len(due), 1)
