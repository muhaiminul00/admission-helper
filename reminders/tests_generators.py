"""Milestone 15 - reminder generation tests: trigger conditions
(Routine Week first-day, exam offsets, revision due-today) and
preference filtering, for every generator in `reminders/services/`.
Rendering/delivery are exercised separately in `tests_emails.py`/
`tests_commands.py` - these tests only check *what* each generator
decides is due right now.
"""

from datetime import time, timedelta

from django.test import TestCase
from django.utils import timezone

from core.test_utils import build_sample_dataset, create_user
from lectures.models import LectureTopic
from progress.models import Progress, RevisionSchedule
from progress.services import revision as revision_service
from reminders.models import NotificationPreference
from reminders.services import daily, exams, progress as progress_gen, revision as revision_gen, weekly
from routines.models import Exam, Lecture, Routine
from subjects.models import Subject


def _monday_on_or_before(d):
    return d - timedelta(days=d.weekday())


def _make_lecture(routine, subject, code, lecture_date, topic_count=1):
    lecture = Lecture.objects.create(
        routine=routine, lecture_code=code, subject=subject, title=code, lecture_date=lecture_date, day="Mon",
    )
    for i in range(topic_count):
        LectureTopic.objects.create(lecture=lecture, topic=f"{code} topic {i}", display_order=i)
    return lecture


class DailyAgendaGeneratorTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.today = self.data["today"]

    def test_no_job_before_preferred_time(self):
        jobs = daily.generate(now=self.today, current_time=time(9, 0))
        self.assertEqual(jobs, [])

    def test_job_after_preferred_time(self):
        jobs = daily.generate(now=self.today, current_time=time(10, 0))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].user, self.user)
        self.assertEqual(jobs[0].reference_key, self.today.isoformat())

    def test_no_activity_flagged_correctly(self):
        # Fixture's lectures/exams are all in the future relative to "today".
        jobs = daily.generate(now=self.today, current_time=time(10, 0))
        self.assertFalse(jobs[0].context["has_activity"])

    def test_disabled_preference_produces_no_job(self):
        NotificationPreference.objects.create(user=self.user, daily_agenda_enabled=False)
        jobs = daily.generate(now=self.today, current_time=time(10, 0))
        self.assertEqual(jobs, [])

    def test_custom_preferred_time_respected(self):
        NotificationPreference.objects.create(user=self.user, daily_agenda_time=time(18, 0))
        self.assertEqual(daily.generate(now=self.today, current_time=time(10, 0)), [])
        self.assertEqual(len(daily.generate(now=self.today, current_time=time(18, 30))), 1)

    def test_todays_lecture_included(self):
        lecture = self.data["lectures"]["p01"]
        lecture_date = lecture.lecture_date
        jobs = daily.generate(now=lecture_date, current_time=time(10, 0))
        self.assertIn(lecture, jobs[0].context["lectures"])
        self.assertTrue(jobs[0].context["has_activity"])


class WeeklyOverviewGeneratorTests(TestCase):
    def setUp(self):
        self.routine = Routine.objects.create(name="Weekly Test Routine", active=True)
        self.subject = Subject.objects.create(code="P", name="Physics", display_order=1)
        self.user = create_user()

        today = timezone.localdate()
        self.week1_monday = _monday_on_or_before(today)
        self.week2_monday = self.week1_monday + timedelta(days=7)

        _make_lecture(self.routine, self.subject, "P-01", self.week1_monday)
        _make_lecture(self.routine, self.subject, "P-02", self.week2_monday + timedelta(days=1))  # Tuesday

    def test_no_job_on_a_non_monday(self):
        jobs = weekly.generate(now=self.week1_monday + timedelta(days=1))
        self.assertEqual(jobs, [])

    def test_job_on_first_day_of_a_routine_week(self):
        jobs = weekly.generate(now=self.week1_monday)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].context["week_number"], 1)
        self.assertEqual(jobs[0].context["lecture_count"], 1)
        self.assertEqual(jobs[0].reference_key, "1")

    def test_second_week_resolves_to_week_number_two(self):
        jobs = weekly.generate(now=self.week2_monday)
        self.assertEqual(jobs[0].context["week_number"], 2)

    def test_day_by_day_schedule_places_lecture_on_correct_day(self):
        jobs = weekly.generate(now=self.week2_monday)
        days = jobs[0].context["days"]
        tuesday = days[1]
        self.assertEqual(tuesday["date"], self.week2_monday + timedelta(days=1))
        self.assertEqual(len(tuesday["lectures"]), 1)
        monday = days[0]
        self.assertEqual(monday["lectures"], [])

    def test_disabled_preference_produces_no_job(self):
        NotificationPreference.objects.create(user=self.user, weekly_overview_enabled=False)
        jobs = weekly.generate(now=self.week1_monday)
        self.assertEqual(jobs, [])

    def test_no_job_when_date_outside_any_routine_week(self):
        jobs = weekly.generate(now=self.week1_monday - timedelta(days=70))
        self.assertEqual(jobs, [])


class WeeklyProgressGeneratorTests(TestCase):
    def setUp(self):
        self.routine = Routine.objects.create(name="Progress Test Routine", active=True)
        self.subject = Subject.objects.create(code="P", name="Physics", display_order=1)
        self.user = create_user()

        today = timezone.localdate()
        self.week1_monday = _monday_on_or_before(today)
        self.week2_monday = self.week1_monday + timedelta(days=7)

        self.lecture = _make_lecture(self.routine, self.subject, "P-01", self.week1_monday)
        # A second, later week so the map spans two weeks and week 1 has a
        # definite end (the map's span is Lecture/Exam-date-derived).
        _make_lecture(self.routine, self.subject, "P-02", self.week2_monday)

    def test_no_job_on_a_non_monday(self):
        jobs = progress_gen.generate(now=self.week2_monday + timedelta(days=1))
        self.assertEqual(jobs, [])

    def test_summarizes_the_week_that_just_ended(self):
        jobs = progress_gen.generate(now=self.week2_monday)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].context["week_number"], 1)
        self.assertEqual(jobs[0].reference_key, "1")
        self.assertEqual(jobs[0].context["next_week_number"], 2)

    def test_completed_lecture_counted(self):
        for topic in self.lecture.topics.all():
            Progress.objects.create(
                user=self.user, lecture_topic=topic,
                class_done=True, notes_done=True, revision_done=True, practice_done=True,
            )
        jobs = progress_gen.generate(now=self.week2_monday)
        self.assertEqual(jobs[0].context["completed_lectures"], 1)
        self.assertEqual(jobs[0].context["total_lectures"], 1)

    def test_disabled_preference_produces_no_job(self):
        NotificationPreference.objects.create(user=self.user, weekly_progress_enabled=False)
        jobs = progress_gen.generate(now=self.week2_monday)
        self.assertEqual(jobs, [])

    def test_no_job_when_no_prior_week_exists(self):
        jobs = progress_gen.generate(now=self.week1_monday)
        self.assertEqual(jobs, [])


class RevisionReminderGeneratorTests(TestCase):
    def setUp(self):
        self.data = build_sample_dataset()
        self.user = self.data["user"]
        self.lecture = self.data["lectures"]["p02"]  # fully completed in the fixture
        revision_service.ensure_revision_schedule(self.user, self.lecture, completion_date=timezone.localdate())

    def test_job_generated_on_due_date(self):
        schedule = RevisionSchedule.objects.get(
            user=self.user, lecture=self.lecture, revision_level=RevisionSchedule.Level.FIRST
        )
        jobs = revision_gen.generate(now=schedule.due_date)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].reference_key, str(schedule.id))
        self.assertEqual(jobs[0].context["lecture"], self.lecture)

    def test_no_job_before_due_date(self):
        jobs = revision_gen.generate(now=timezone.localdate())
        self.assertEqual(jobs, [])

    def test_completed_schedule_produces_no_job(self):
        schedule = RevisionSchedule.objects.get(
            user=self.user, lecture=self.lecture, revision_level=RevisionSchedule.Level.FIRST
        )
        revision_service.complete_revision(self.user, schedule.id)
        jobs = revision_gen.generate(now=schedule.due_date)
        self.assertEqual(jobs, [])

    def test_disabled_preference_produces_no_job(self):
        NotificationPreference.objects.create(user=self.user, revision_reminder_enabled=False)
        schedule = RevisionSchedule.objects.get(
            user=self.user, lecture=self.lecture, revision_level=RevisionSchedule.Level.FIRST
        )
        jobs = revision_gen.generate(now=schedule.due_date)
        self.assertEqual(jobs, [])


class ExamReminderGeneratorTests(TestCase):
    def setUp(self):
        self.routine = Routine.objects.create(name="Exam Test Routine", active=True)
        self.user = create_user()
        self.today = timezone.localdate()
        self.weekly_exam = Exam.objects.create(
            routine=self.routine, exam_code="WE-01", exam_name="Physics Weekly",
            exam_type=Exam.ExamType.WEEKLY, exam_date=self.today + timedelta(days=1),
            covered_lectures=[],
        )
        self.monthly_exam = Exam.objects.create(
            routine=self.routine, exam_code="ME-01", exam_name="Physics Monthly",
            exam_type=Exam.ExamType.MONTHLY, exam_date=self.today + timedelta(days=7),
            covered_lectures=[],
        )

    def test_weekly_exam_one_day_before(self):
        jobs = exams.generate_weekly(now=self.today)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].reference_key, f"{self.weekly_exam.pk}:1d_before")

    def test_weekly_exam_day_of_gated_by_morning_time(self):
        jobs = exams.generate_weekly(now=self.today + timedelta(days=1), current_time=time(7, 0))
        self.assertEqual(jobs, [])
        jobs = exams.generate_weekly(now=self.today + timedelta(days=1), current_time=time(8, 30))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].reference_key, f"{self.weekly_exam.pk}:day_of")

    def test_weekly_exam_not_due_two_days_before(self):
        jobs = exams.generate_weekly(now=self.today - timedelta(days=1))
        self.assertEqual(jobs, [])

    def test_monthly_exam_seven_three_one_days_before(self):
        for offset, label in [(7, "7d_before"), (3, "3d_before"), (1, "1d_before")]:
            jobs = exams.generate_monthly(now=self.monthly_exam.exam_date - timedelta(days=offset))
            self.assertEqual(len(jobs), 1, f"expected a job {offset} days before")
            self.assertEqual(jobs[0].reference_key, f"{self.monthly_exam.pk}:{label}")

    def test_monthly_exam_not_due_four_days_before(self):
        jobs = exams.generate_monthly(now=self.monthly_exam.exam_date - timedelta(days=4))
        self.assertEqual(jobs, [])

    def test_monthly_exam_not_returned_by_weekly_generator(self):
        # monthly_exam is dated today+7, which coincides with the date
        # the weekly generator's "1 day before" offset would check from
        # today+6 - confirms exam_type filtering, not just date offsets.
        jobs = exams.generate_weekly(now=self.monthly_exam.exam_date - timedelta(days=1))
        self.assertEqual(jobs, [])

    def test_disabled_preference_produces_no_job(self):
        NotificationPreference.objects.create(user=self.user, weekly_exam_reminder_enabled=False)
        jobs = exams.generate_weekly(now=self.today)
        self.assertEqual(jobs, [])
