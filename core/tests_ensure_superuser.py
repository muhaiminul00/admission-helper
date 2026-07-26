"""Milestone 17.1 - `ensure_superuser` is the deployment-bootstrap
substitute for `createsuperuser` on Render Free (no Shell/One-Off Jobs
access there). Covers: no-op when unset, creates when absent, and is
idempotent (updates rather than erroring) when the user already exists.
"""

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase


class EnsureSuperuserCommandTests(TestCase):
    def test_noop_when_env_vars_unset(self):
        call_command("ensure_superuser")
        self.assertEqual(User.objects.count(), 0)

    def test_creates_superuser_when_absent(self):
        import os
        os.environ["DJANGO_SUPERUSER_USERNAME"] = "admin"
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "S3cure-Pass!23"
        os.environ["DJANGO_SUPERUSER_EMAIL"] = "admin@example.com"
        try:
            call_command("ensure_superuser")
        finally:
            del os.environ["DJANGO_SUPERUSER_USERNAME"]
            del os.environ["DJANGO_SUPERUSER_PASSWORD"]
            del os.environ["DJANGO_SUPERUSER_EMAIL"]

        user = User.objects.get(username="admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("S3cure-Pass!23"))

    def test_existing_user_is_updated_not_duplicated(self):
        import os
        User.objects.create_user(username="admin", password="old-password")
        os.environ["DJANGO_SUPERUSER_USERNAME"] = "admin"
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "new-password"
        try:
            call_command("ensure_superuser")
        finally:
            del os.environ["DJANGO_SUPERUSER_USERNAME"]
            del os.environ["DJANGO_SUPERUSER_PASSWORD"]

        self.assertEqual(User.objects.filter(username="admin").count(), 1)
        user = User.objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("new-password"))
