from django.core.management.base import BaseCommand

from reminders.management._report import report_results
from reminders.models import ReminderLog
from reminders.services import engine


class Command(BaseCommand):
    """Scheduler-agnostic (Phase 10): run this however you like - cron,
    Render/Railway Scheduled Jobs, GitHub Actions, Celery beat - as
    often as you want (e.g. hourly, to catch each user's configured
    delivery time). Idempotency (Phase 11) makes repeat runs harmless:
    a user who already got today's agenda is silently skipped."""

    help = "Send the Daily Study Agenda to every eligible user whose preferred delivery time has passed."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without sending it.")

    def handle(self, *args, **options):
        results = engine.run(
            reminder_types=[ReminderLog.ReminderType.DAILY_AGENDA], dry_run=options["dry_run"]
        )
        report_results(self, results, "daily agenda email(s)", options["dry_run"])
