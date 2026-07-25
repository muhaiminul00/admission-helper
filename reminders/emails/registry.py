"""Reminder type -> (template, subject line) - the one place a new
reminder type registers how it renders. Adding a new generator to
`reminders/services/` also means adding one entry here; nothing else
in the rendering/delivery layer needs to change.
"""

from ..models import ReminderLog

ReminderType = ReminderLog.ReminderType

REMINDER_TYPES = {
    ReminderType.DAILY_AGENDA: {
        "template": "emails/daily_agenda.html",
        "subject": lambda ctx: f"Your Study Agenda for {ctx['today']:%B %d}",
    },
    ReminderType.WEEKLY_OVERVIEW: {
        "template": "emails/weekly_overview.html",
        "subject": lambda ctx: f"Routine Week {ctx['week_number']} — What's Ahead",
    },
    ReminderType.REVISION_DUE: {
        "template": "emails/revision_due.html",
        "subject": lambda ctx: f"Revision Due Today: {ctx['lecture'].lecture_code}",
    },
    ReminderType.WEEKLY_EXAM: {
        "template": "emails/exam_reminder.html",
        "subject": lambda ctx: f"Weekly Exam Reminder: {ctx['exam'].exam_name}",
    },
    ReminderType.MONTHLY_EXAM: {
        "template": "emails/exam_reminder.html",
        "subject": lambda ctx: f"Monthly Exam Reminder: {ctx['exam'].exam_name}",
    },
    ReminderType.WEEKLY_PROGRESS: {
        "template": "emails/weekly_progress.html",
        "subject": lambda ctx: f"Weekly Progress — Routine Week {ctx['week_number']}",
    },
}
