"""Milestone 15, Phase 8 - HTML email rendering + plain-text fallback
tests. Exercises `reminders.emails.renderer.render_reminder()` against
a `ReminderJob` built directly (bypassing generation entirely) for
every registered reminder type, so a broken template/registry entry
fails here regardless of whether its generator's own trigger
conditions are also under test.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.test_utils import build_sample_dataset
from progress.models import RevisionSchedule
from progress.services import revision as revision_service
from reminders.emails.registry import REMINDER_TYPES
from reminders.emails.renderer import render_reminder
from reminders.models import ReminderLog
from reminders.services.job import ReminderJob
from routines.models import Exam
from routines.services.exam_coverage import get_exam_coverage


class RegistryCompletenessTests(TestCase):
    def test_every_reminder_type_choice_is_registered(self):
        for value, _label in ReminderLog.ReminderType.choices:
            self.assertIn(value, REMINDER_TYPES)


class DailyAgendaRenderingTests(TestCase):
    def test_no_activity_message_renders(self):
        job = ReminderJob(
            user=build_sample_dataset()["user"],
            reminder_type=ReminderLog.ReminderType.DAILY_AGENDA,
            reference_key="2026-01-01",
            context={
                "today": timezone.localdate(), "lectures": [], "exams": [], "revisions": [],
                "overdue_revisions": [], "has_activity": False, "study_load": 0,
            },
        )
        subject, html, text = render_reminder(job)
        self.assertIn("Study Agenda", subject)
        self.assertIn("No scheduled study activities today.", html)
        self.assertIn("No scheduled study activities today.", text)
        self.assertNotIn("<", text)


class WeeklyOverviewRenderingTests(TestCase):
    def test_renders_days_and_counts(self):
        today = timezone.localdate()
        job = ReminderJob(
            user=build_sample_dataset()["user"],
            reminder_type=ReminderLog.ReminderType.WEEKLY_OVERVIEW,
            reference_key="3",
            context={
                "week_number": 3, "monday": today, "sunday": today + timedelta(days=6),
                "lecture_count": 2, "exam_count": 1, "revision_count": 1,
                "days": [{"date": today + timedelta(days=i), "lectures": [], "exams": []} for i in range(7)],
            },
        )
        subject, html, text = render_reminder(job)
        self.assertIn("Routine Week 3", subject)
        self.assertIn("Routine Week 3", html)
        self.assertIn("Free", html)  # every day has no lectures/exams in this fixture
        self.assertNotIn("<", text)


class RevisionDueRenderingTests(TestCase):
    def test_renders_lecture_and_priority(self):
        data = build_sample_dataset()
        user = data["user"]
        lecture = data["lectures"]["p02"]
        revision_service.ensure_revision_schedule(user, lecture, completion_date=timezone.localdate())
        schedule = RevisionSchedule.objects.get(
            user=user, lecture=lecture, revision_level=RevisionSchedule.Level.FIRST
        )
        job = ReminderJob(
            user=user, reminder_type=ReminderLog.ReminderType.REVISION_DUE,
            reference_key=str(schedule.id),
            context={
                "schedule": schedule, "lecture": lecture, "subject": lecture.subject,
                "chapters": [], "days_since_last_study": 5,
            },
        )
        subject, html, text = render_reminder(job)
        self.assertIn(lecture.lecture_code, subject)
        self.assertIn("First Revision", html)
        self.assertIn("5", html)
        self.assertNotIn("<", text)


class ExamReminderRenderingTests(TestCase):
    def test_renders_coverage_and_readiness(self):
        data = build_sample_dataset()
        user = data["user"]
        exam = data["exams"]["we01"]
        coverage = get_exam_coverage(exam)
        job = ReminderJob(
            user=user, reminder_type=ReminderLog.ReminderType.WEEKLY_EXAM,
            reference_key=f"{exam.pk}:1d_before",
            context={
                "exam": exam, "days_remaining": 1,
                "readiness": {"readiness_label": "Needs Work", "percentage": 42.0},
                "covered_subjects": coverage["covered_subjects"],
                "covered_chapters": coverage["covered_chapters"],
                "remaining_lectures": coverage["covered_lectures"],
            },
        )
        subject, html, text = render_reminder(job)
        self.assertIn(exam.exam_name, subject)
        self.assertIn("Needs Work", html)
        self.assertIn("Tomorrow", html)
        self.assertNotIn("<", text)

    def test_exam_day_renders_today_not_tomorrow(self):
        data = build_sample_dataset()
        exam = data["exams"]["we01"]
        job = ReminderJob(
            user=data["user"], reminder_type=ReminderLog.ReminderType.WEEKLY_EXAM,
            reference_key=f"{exam.pk}:day_of",
            context={
                "exam": exam, "days_remaining": 0, "readiness": None,
                "covered_subjects": [], "covered_chapters": [], "remaining_lectures": [],
            },
        )
        _subject, html, _text = render_reminder(job)
        self.assertIn("Today", html)
        self.assertIn("All covered lectures are exam-ready.", html)


class WeeklyProgressRenderingTests(TestCase):
    def test_renders_summary_and_next_week(self):
        today = timezone.localdate()
        job = ReminderJob(
            user=build_sample_dataset()["user"],
            reminder_type=ReminderLog.ReminderType.WEEKLY_PROGRESS,
            reference_key="4",
            context={
                "week_number": 4, "monday": today, "sunday": today + timedelta(days=6),
                "total_lectures": 5, "completed_lectures": 4, "completed_revisions": 3,
                "exams_completed_count": 1, "overall_percentage": 72.5,
                "next_week_number": 5, "next_week_lecture_count": 3, "next_week_exam_count": 1,
            },
        )
        subject, html, text = render_reminder(job)
        self.assertIn("Routine Week 4", subject)
        self.assertIn("4 / 5", html)
        self.assertIn("Routine Week 5", html)
        self.assertNotIn("<", text)
