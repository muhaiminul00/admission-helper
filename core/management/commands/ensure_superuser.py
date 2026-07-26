"""Milestone 17.1 - Render Free's Shell and One-Off Jobs are both
paid-tier-only features, so `python manage.py createsuperuser`
cannot be run interactively against the deployed instance. This
command is the deployment-bootstrap substitute: it reads credentials
from environment variables and is safe to run on every deploy
(idempotent - never errors or duplicates if the user already exists,
unlike `createsuperuser --noinput`).

Does nothing (and does not fail the deploy) if the env vars are unset,
so it's harmless to always include in startCommand.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Idempotently ensure a superuser exists, using the "
        "DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD environment variables. "
        "No-op if they are unset."
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD not set - skipping.")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        user.set_password(password)
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} superuser '{username}'."))
