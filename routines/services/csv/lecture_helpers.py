"""Shared helper for resolving a Lecture by lecture_code, creating a
minimal ("virtual") one when routine.csv never scheduled it.

Milestone 3 skipped 31 lecture_topics.csv rows because LectureTopic.lecture
was a required FK and no Lecture existed for self-study subjects
(English/Bangla - no CLASS rows at all) or the intentional lecture-06
gap (class was skipped). Milestone 4.1 made Lecture.lecture_date/day/title
optional specifically so a real Lecture row can represent "this lecture
code exists but was never scheduled with a date" - which is true, not
fabricated. No date, day, time, or title is invented here; only the
lecture_code and subject (both real, CSV-sourced values) are set.
"""

from .routine_helpers import get_or_create_routine


def get_or_create_lecture(lecture_code, subject):
    from routines.models import Lecture

    routine = get_or_create_routine()
    lecture, _ = Lecture.objects.get_or_create(
        routine=routine,
        lecture_code=lecture_code,
        defaults={
            "subject": subject,
            "title": "",
            "lecture_date": None,
            "day": "",
            "start_time": None,
            "end_time": None,
            "notes": "",
        },
    )
    return lecture
