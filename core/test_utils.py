"""Shared test fixture builder, used by dashboard/progress/routines tests.

Not a Django app module with models/views of its own - just a small,
deliberately hand-built dataset so every app's tests exercise the same
known values instead of duplicating setup logic (and drifting) across
each app's tests.py.

Dates are built relative to `timezone.localdate()` so the test suite
never depends on the wall-clock date it happens to run on.

Layout (see docstring math in Milestone 6's PROJECT_PROGRESS.md entry
for the full expected-value derivation used by the tests):

- Subject P (Physics, has chapters) / Subject E (English, self-study,
  no chapters at all - chapter breakdown intentionally absent).
- Chapter P/1/1, P/1/2, P/2/1.
- Lecture P-01 (dated), P-02 (dated), P-06 (undated: gap lecture),
  E-01 (undated: self-study).
- Topics: P-01 has 2 topics (one fully completed, one partially),
  P-02 has 1 topic (fully completed), P-06 has 1 topic (untouched),
  E-01 has 1 topic (untouched, chapter=None).
- Exam WE-01 covers [P-01, P-02, E-01]; Exam WE-02 covers [P-06].

Milestone 7: Progress became per-user, so every Progress row in this
fixture belongs to one `User` - by default a freshly-created
"student1" (password "testpass123"), returned as `data["user"]`, or an
explicit `user=` passed in by the caller (used by cross-user isolation
tests that need a second user's Progress to *not* appear in the first
user's data).
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from lectures.models import LectureTopic
from progress.models import Progress
from routines.models import Exam, Lecture, Routine
from subjects.models import Chapter, Subject

COMPLETE = dict(class_done=True, notes_done=True, revision_done=True, practice_done=True)
PARTIAL = dict(class_done=True, notes_done=False, revision_done=False, practice_done=False)

DEFAULT_PASSWORD = "testpass123"


def create_user(username="student1", password=DEFAULT_PASSWORD):
    return User.objects.create_user(username=username, password=password)


def build_sample_dataset(user=None):
    today = timezone.localdate()
    user = user or create_user()

    routine = Routine.objects.create(name="Test Routine", active=True)

    subject_p = Subject.objects.create(code="P", name="Physics", display_order=1)
    subject_e = Subject.objects.create(code="E", name="English", display_order=2)

    ch_p1_1 = Chapter.objects.create(
        subject=subject_p, paper=1, chapter_no=1, name="Vector", display_order=1
    )
    ch_p1_2 = Chapter.objects.create(
        subject=subject_p, paper=1, chapter_no=2, name="Motion", display_order=2
    )
    ch_p2_1 = Chapter.objects.create(
        subject=subject_p, paper=2, chapter_no=1, name="Electricity", display_order=1
    )
    # Subject E deliberately has zero Chapter rows (self-study, no
    # chapter breakdown) - LectureTopic.chapter stays None for it.

    lecture_p01 = Lecture.objects.create(
        routine=routine, lecture_code="P-01", subject=subject_p,
        title="Physics 1", lecture_date=today + timedelta(days=1), day="Sat",
    )
    lecture_p02 = Lecture.objects.create(
        routine=routine, lecture_code="P-02", subject=subject_p,
        title="Physics 2", lecture_date=today + timedelta(days=8), day="Sat",
    )
    lecture_p06 = Lecture.objects.create(
        routine=routine, lecture_code="P-06", subject=subject_p,
        title="", lecture_date=None,
    )
    lecture_e01 = Lecture.objects.create(
        routine=routine, lecture_code="E-01", subject=subject_e,
        title="", lecture_date=None,
    )

    topic1 = LectureTopic.objects.create(
        lecture=lecture_p01, chapter=ch_p1_1, topic="Vectors intro", display_order=1
    )
    topic2 = LectureTopic.objects.create(
        lecture=lecture_p01, chapter=ch_p1_2, topic="Motion intro", display_order=2
    )
    topic3 = LectureTopic.objects.create(
        lecture=lecture_p02, chapter=ch_p2_1, topic="Electricity intro", display_order=1
    )
    topic4 = LectureTopic.objects.create(
        lecture=lecture_p06, chapter=ch_p1_1, topic="Vectors extra", display_order=1
    )
    topic5 = LectureTopic.objects.create(
        lecture=lecture_e01, chapter=None, topic="Essay writing", display_order=1
    )

    Progress.objects.create(user=user, lecture_topic=topic1, **COMPLETE)
    Progress.objects.create(user=user, lecture_topic=topic2, **PARTIAL)
    Progress.objects.create(user=user, lecture_topic=topic3, **COMPLETE)
    # topic4, topic5 intentionally have no Progress row at all - a topic
    # with no Progress row must count identically to one with all-False
    # booleans (not started).

    exam1 = Exam.objects.create(
        routine=routine, exam_code="WE-01", exam_name="Weekly Exam 1",
        exam_type=Exam.ExamType.WEEKLY, exam_date=today + timedelta(days=10),
        covered_lectures=["P-01", "P-02", "E-01"],
    )
    exam2 = Exam.objects.create(
        routine=routine, exam_code="WE-02", exam_name="Weekly Exam 2",
        exam_type=Exam.ExamType.WEEKLY, exam_date=today + timedelta(days=20),
        covered_lectures=["P-06"],
    )

    return {
        "today": today,
        "user": user,
        "routine": routine,
        "subject_p": subject_p,
        "subject_e": subject_e,
        "chapters": {"p11": ch_p1_1, "p12": ch_p1_2, "p21": ch_p2_1},
        "lectures": {
            "p01": lecture_p01, "p02": lecture_p02,
            "p06": lecture_p06, "e01": lecture_e01,
        },
        "topics": {
            "t1": topic1, "t2": topic2, "t3": topic3, "t4": topic4, "t5": topic5,
        },
        "exams": {"we01": exam1, "we02": exam2},
    }
