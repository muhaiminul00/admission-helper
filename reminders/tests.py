"""Milestone 15 - core model/service/view tests for the reminder
system's non-generator pieces: `NotificationPreference` defaults,
`ReminderLog`'s uniqueness constraint, `services.preferences.
get_preferences()`, and the notification settings page. Generation
logic lives in `tests_generators.py`, rendering in `tests_emails.py`,
management commands in `tests_commands.py`. Milestone 15.1 added
`TimezoneChoicesTests` (Phase 1's searchable dropdown) and
`ReminderAdminAccessTests`/etc. in `tests_admin.py`.
"""

from datetime import time

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from core.test_utils import create_user

from .models import NotificationPreference, ReminderLog
from .services.preferences import get_preferences
from .services.timezones import get_timezone_choices


class NotificationPreferenceDefaultsTests(TestCase):
    def test_sensible_defaults(self):
        user = create_user()
        preference = NotificationPreference.objects.create(user=user)
        self.assertTrue(preference.daily_agenda_enabled)
        self.assertEqual(preference.daily_agenda_time, time(10, 0))
        self.assertTrue(preference.weekly_overview_enabled)
        self.assertTrue(preference.revision_reminder_enabled)
        self.assertTrue(preference.weekly_exam_reminder_enabled)
        self.assertTrue(preference.monthly_exam_reminder_enabled)
        self.assertTrue(preference.weekly_progress_enabled)
        self.assertEqual(preference.timezone, "Asia/Dhaka")


class GetPreferencesTests(TestCase):
    def test_unsaved_default_for_user_with_no_row(self):
        user = create_user()
        preference = get_preferences(user)
        self.assertIsNone(preference.pk)
        self.assertTrue(preference.daily_agenda_enabled)
        self.assertEqual(NotificationPreference.objects.filter(user=user).count(), 0)

    def test_returns_persisted_row_when_it_exists(self):
        user = create_user()
        NotificationPreference.objects.create(user=user, daily_agenda_enabled=False)
        preference = get_preferences(user)
        self.assertIsNotNone(preference.pk)
        self.assertFalse(preference.daily_agenda_enabled)


class ReminderLogUniquenessTests(TestCase):
    def test_duplicate_delivery_is_rejected(self):
        user = create_user()
        ReminderLog.objects.create(
            user=user, reminder_type=ReminderLog.ReminderType.DAILY_AGENDA, reference_key="2026-01-01"
        )
        with self.assertRaises(IntegrityError):
            ReminderLog.objects.create(
                user=user, reminder_type=ReminderLog.ReminderType.DAILY_AGENDA, reference_key="2026-01-01"
            )

    def test_different_reference_key_is_allowed(self):
        user = create_user()
        ReminderLog.objects.create(
            user=user, reminder_type=ReminderLog.ReminderType.DAILY_AGENDA, reference_key="2026-01-01"
        )
        ReminderLog.objects.create(
            user=user, reminder_type=ReminderLog.ReminderType.DAILY_AGENDA, reference_key="2026-01-02"
        )
        self.assertEqual(ReminderLog.objects.count(), 2)


class NotificationPreferencesViewTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.login(username=self.user.username, password="testpass123")

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("notification-preferences"))
        self.assertEqual(response.status_code, 302)

    def test_get_creates_a_default_row_if_none_exists(self):
        # The view get_or_creates so the form always has a real instance
        # to bind/save against - a first visit gets sensible defaults,
        # not an empty unsaved form.
        self.client.get(reverse("notification-preferences"))
        preference = NotificationPreference.objects.get(user=self.user)
        self.assertTrue(preference.daily_agenda_enabled)

    def test_post_creates_and_saves_preferences(self):
        response = self.client.post(
            reverse("notification-preferences"),
            {
                "daily_agenda_time": "09:30",
                "timezone": "Asia/Dhaka",
                # unchecked boxes simply omitted, per HTML checkbox semantics
                "weekly_overview_enabled": "on",
                "revision_reminder_enabled": "on",
                "weekly_exam_reminder_enabled": "on",
                "monthly_exam_reminder_enabled": "on",
                "weekly_progress_enabled": "on",
            },
        )
        self.assertContains(response, "Notification preferences saved.")
        preference = NotificationPreference.objects.get(user=self.user)
        self.assertFalse(preference.daily_agenda_enabled)  # omitted -> False
        self.assertEqual(preference.daily_agenda_time, time(9, 30))

    def test_invalid_timezone_rejected(self):
        # Milestone 15.1, Phase 1: timezone is now a constrained
        # dropdown (ChoiceField), not free text - an out-of-list value
        # is rejected by Django's own "not a valid choice" validation
        # rather than a hand-written message.
        response = self.client.post(
            reverse("notification-preferences"),
            {"daily_agenda_time": "10:00", "timezone": "Not/A_Zone"},
        )
        self.assertEqual(NotificationPreference.objects.filter(user=self.user, timezone="Not/A_Zone").count(), 0)
        self.assertContains(response, "Select a valid choice")

    def test_never_creates_another_users_preferences(self):
        other = create_user(username="other_student")
        self.client.post(reverse("notification-preferences"), {"daily_agenda_time": "10:00", "timezone": "UTC"})
        self.assertEqual(NotificationPreference.objects.filter(user=other).count(), 0)

    def test_page_renders_a_searchable_timezone_dropdown(self):
        response = self.client.get(reverse("notification-preferences"))
        html = response.content.decode()
        self.assertIn("<select", html)
        self.assertIn('name="timezone"', html)
        self.assertIn("Asia/Dhaka (UTC+06:00)", html)
        # Not a free-text input for timezone (Phase 1's explicit constraint).
        self.assertNotIn('name="timezone" type="text"', html)


class TimezoneChoicesTests(TestCase):
    """Milestone 15.1, Phase 1 - the constrained IANA timezone dropdown."""

    def test_includes_default_and_common_zones(self):
        choices = dict(get_timezone_choices())
        self.assertIn("Asia/Dhaka", choices)
        self.assertIn("UTC", choices)
        self.assertIn("Europe/London", choices)
        self.assertIn("America/New_York", choices)

    def test_labels_include_utc_offset(self):
        choices = dict(get_timezone_choices())
        self.assertIn("UTC+06:00", choices["Asia/Dhaka"])

    def test_excludes_non_geographic_aliases(self):
        names = [name for name, _label in get_timezone_choices()]
        self.assertTrue(all(not name.startswith(("Etc/", "posix/", "right/", "SystemV/")) for name in names))

    def test_sorted_alphabetically(self):
        names = [name for name, _label in get_timezone_choices()]
        self.assertEqual(names, sorted(names))

    def test_only_valid_iana_names_are_choices(self):
        import zoneinfo
        available = zoneinfo.available_timezones()
        names = [name for name, _label in get_timezone_choices()]
        self.assertTrue(all(name in available for name in names))
