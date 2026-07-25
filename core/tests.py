from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.test_utils import DEFAULT_PASSWORD, build_sample_dataset, create_user


class RegistrationViewTests(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    def test_valid_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "email": "newstudent@example.com",
                "password1": "S3cure-Pass!23",
                "password2": "S3cure-Pass!23",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.email, "newstudent@example.com")

        # Automatically logged in - a follow-up request is authenticated.
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_password_mismatch_rejected(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "email": "newstudent@example.com",
                "password1": "S3cure-Pass!23",
                "password2": "TotallyDifferent!45",
            },
        )
        self.assertEqual(response.status_code, 200)  # re-rendered with errors
        self.assertFalse(User.objects.filter(username="newstudent").exists())

    def test_duplicate_username_rejected(self):
        create_user("existing")
        response = self.client.post(
            reverse("register"),
            {
                "username": "existing",
                "email": "existing2@example.com",
                "password1": "S3cure-Pass!23",
                "password2": "S3cure-Pass!23",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existing").count(), 1)


class ProfileViewTests(TestCase):
    """Milestone 15.2, Part 1 - the header's User Menu "Profile" link."""

    def setUp(self):
        self.user = create_user("student1")

    def test_login_required(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_shows_account_details(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student1")

    def test_non_staff_does_not_see_reminder_admin_link(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertNotContains(response, reverse("reminder-admin"))

    def test_staff_sees_reminder_admin_link(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertContains(response, reverse("reminder-admin"))


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.user = create_user("student1")

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"), {"username": "student1", "password": DEFAULT_PASSWORD}
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"), {"username": "student1", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "didn't match")

    def test_already_authenticated_user_redirected_away_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_logged_out_user_loses_access(self):
        self.client.force_login(self.user)
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)


class RouteProtectionTests(TestCase):
    """Every study page redirects an anonymous visitor to login; admin
    is unaffected (uses its own separate auth, unchanged by this
    milestone)."""

    def setUp(self):
        self.data = build_sample_dataset()

    def test_anonymous_visitor_redirected_from_every_protected_page(self):
        protected_urls = [
            reverse("dashboard"),
            reverse("dashboard-widgets"),
            reverse("routine-list"),
            reverse("lecture-detail", args=[self.data["lectures"]["p01"].lecture_code]),
            reverse("exam-detail", args=[self.data["exams"]["we01"].pk]),
            reverse("progress-overview"),
            reverse("analytics-subjects"),
            reverse("analytics-chapters"),
            reverse("analytics-lectures"),
            reverse("analytics-exams"),
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)

    def test_anonymous_visitor_cannot_toggle_progress(self):
        topic = self.data["topics"]["t1"]
        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_admin_login_unaffected(self):
        # Admin has its own separate login page - not django's front-end
        # `login` view - and stays reachable regardless of this milestone.
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)


class CrossUserIsolationTests(TestCase):
    """End-to-end verification (Milestone 7's own "Verification" section):
    two real users, logged in via the test client, never see each
    other's progress/analytics/dashboard data."""

    def setUp(self):
        self.data = build_sample_dataset()  # owned by data["user"] ("student1")
        self.user1 = self.data["user"]
        self.user2 = create_user("student2")

    def test_progress_overview_differs_per_user(self):
        self.client.force_login(self.user1)
        response1 = self.client.get(reverse("progress-overview"))

        self.client.force_login(self.user2)
        response2 = self.client.get(reverse("progress-overview"))

        self.assertEqual(response1.context["completed_topics"], 2)
        self.assertEqual(response2.context["completed_topics"], 0)

    def test_dashboard_statistics_differ_per_user(self):
        self.client.force_login(self.user1)
        response1 = self.client.get(reverse("dashboard"))

        self.client.force_login(self.user2)
        response2 = self.client.get(reverse("dashboard"))

        self.assertEqual(response1.context["completion_percentage"], 40.0)
        self.assertEqual(response2.context["completion_percentage"], 0)

    def test_analytics_subject_page_differs_per_user(self):
        self.client.force_login(self.user1)
        response1 = self.client.get(reverse("analytics-subjects"))
        rows1 = {r["subject"].code: r["percentage"] for r in response1.context["rows"]}

        self.client.force_login(self.user2)
        response2 = self.client.get(reverse("analytics-subjects"))
        rows2 = {r["subject"].code: r["percentage"] for r in response2.context["rows"]}

        self.assertEqual(rows1["P"], 50.0)
        self.assertEqual(rows2["P"], 0.0)

    def test_toggling_progress_as_one_user_does_not_affect_the_other(self):
        topic = self.data["topics"]["t4"]  # untouched by either user

        self.client.force_login(self.user2)
        url = reverse("progress-toggle", args=[topic.id, "class_done"])
        self.client.post(url)

        self.client.force_login(self.user1)
        response = self.client.get(reverse("progress-overview"))
        # user1's completed count is unaffected by user2's toggle.
        self.assertEqual(response.context["completed_topics"], 2)
