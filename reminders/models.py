from datetime import time

from django.conf import settings
from django.db import models


class NotificationPreference(models.Model):
    """One user's reminder settings (Milestone 15, Phase 7).

    Created lazily: the notification settings page get_or_creates this
    row on first visit/save; reminder generation never creates one
    just by running - `reminders.services.preferences.get_preferences()`
    falls back to an unsaved instance (model field defaults below) for
    a user who has never visited the settings page, so "sensible
    defaults" apply without needing to backfill a row per user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preference"
    )
    daily_agenda_enabled = models.BooleanField(default=True)
    daily_agenda_time = models.TimeField(default=time(10, 0))
    weekly_overview_enabled = models.BooleanField(default=True)
    revision_reminder_enabled = models.BooleanField(default=True)
    weekly_exam_reminder_enabled = models.BooleanField(default=True)
    monthly_exam_reminder_enabled = models.BooleanField(default=True)
    weekly_progress_enabled = models.BooleanField(default=True)
    timezone = models.CharField(max_length=50, default=settings.TIME_ZONE)

    def __str__(self):
        return f"Notification preferences for {self.user}"


class ReminderLog(models.Model):
    """Durable idempotency record (Milestone 15, Phase 11).

    Once (user, reminder_type, reference_key) has been logged here,
    the reminder engine never generates that same reminder again -
    this table, not in-memory state, is what makes duplicate
    protection survive an application/scheduler restart.
    `reference_key` identifies *which occurrence* of a reminder type
    this is - a date (daily/weekly reminders), a `RevisionSchedule` id
    (revision reminders), or an "<exam_id>:<offset_label>" pair (exam
    reminders); see each generator in `reminders/services/` for its
    exact key format.
    """

    class ReminderType(models.TextChoices):
        DAILY_AGENDA = "daily_agenda", "Daily Agenda"
        WEEKLY_OVERVIEW = "weekly_overview", "Weekly Overview"
        REVISION_DUE = "revision_due", "Revision Due"
        WEEKLY_EXAM = "weekly_exam", "Weekly Exam Reminder"
        MONTHLY_EXAM = "monthly_exam", "Monthly Exam Reminder"
        WEEKLY_PROGRESS = "weekly_progress", "Weekly Progress"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    class TriggeredBy(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        MANUAL = "manual", "Manual"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminder_logs"
    )
    reminder_type = models.CharField(max_length=30, choices=ReminderType.choices, db_index=True)
    reference_key = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)
    # Milestone 15.1, Phase 8 - the Reminder Activity Log reuses this
    # same table rather than a second one; these three fields are the
    # only addition, recording *how it went* alongside *what/when* the
    # original Milestone 15 fields already captured.
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    error_message = models.TextField(blank=True, default="")
    triggered_by = models.CharField(
        max_length=10, choices=TriggeredBy.choices, default=TriggeredBy.AUTOMATIC
    )

    class Meta:
        ordering = ["-sent_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "reminder_type", "reference_key"], name="unique_reminder_delivery"
            ),
        ]

    def __str__(self):
        return f"{self.get_reminder_type_display()} sent to {self.user} ({self.reference_key})"
