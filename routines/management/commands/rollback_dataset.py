"""Roll back to a previous DatasetVersion (Milestone 10).

Usage:
    python manage.py rollback_dataset [--to VERSION_NAME] [--user USERNAME]

Without --to, rolls back to the DatasetVersion imported immediately
before the currently active one. Re-imports that version's archived
source CSVs (see routines/services/dataset/versioning.py) through the
same import pipeline import_csv uses, atomically.
"""

import sys

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from routines.models import DatasetVersion
from routines.services.csv.validators import ImportValidationError
from routines.services.dataset import versioning
from routines.services.dataset.rollback import RollbackError, rollback_to


class Command(BaseCommand):
    help = "Roll back to a previous DatasetVersion, re-importing its archived source CSVs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--to", default=None,
            help="version_name to roll back to (default: the version before the active one).",
        )
        parser.add_argument("--user", default=None, help="Username to record on the ImportLog.")

    def handle(self, *args, **options):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        user = None
        if options.get("user"):
            user = get_user_model().objects.filter(username=options["user"]).first()

        if options["to"]:
            try:
                target = DatasetVersion.objects.get(version_name=options["to"])
            except DatasetVersion.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No dataset version named '{options['to']}'."))
                raise SystemExit(1)
        else:
            target = versioning.get_previous_version()
            if target is None:
                self.stdout.write(self.style.ERROR(
                    "No previous dataset version to roll back to."
                ))
                raise SystemExit(1)

        self.stdout.write(f"Rolling back to '{target.version_name}' (imported {target.imported_at})...")
        self.stdout.write("")

        try:
            rollback_to(target, user=user, stdout=self.stdout)
        except RollbackError as exc:
            self.stdout.write(self.style.ERROR(str(exc)))
            raise SystemExit(1)
        except ImportValidationError as exc:
            self.stdout.write(self.style.ERROR(
                f"Rollback failed - the archived dataset itself did not validate: {exc}"
            ))
            raise SystemExit(1)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Rolled back successfully. '{target.version_name}' is now the active dataset."
        ))
