from django.core.management.base import BaseCommand

from reminders.models import ReminderLog
from reminders.services import engine


class Command(BaseCommand):
    help = "Send Revision Due reminders to every eligible user with a revision due today."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without sending it.")

    def handle(self, *args, **options):
        sent = engine.run(
            reminder_types=[ReminderLog.ReminderType.REVISION_DUE], dry_run=options["dry_run"]
        )
        verb = "Would send" if options["dry_run"] else "Sent"
        self.stdout.write(self.style.SUCCESS(f"{verb} {len(sent)} revision reminder email(s)."))
