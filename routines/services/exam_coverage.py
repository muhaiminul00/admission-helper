"""What a single Exam covers, resolved from `Exam.covered_lectures`
(a plain JSON list of lecture codes - see `routines/models.py`).

Extracted in Milestone 15 from `ExamDetailView` (Milestone 12, Phase
10) so the Exam Detail page and the new exam reminder emails share one
implementation instead of two copies of the same lecture/subject/
chapter resolution.
"""

from routines.models import Lecture
from subjects.models import Chapter


def get_exam_coverage(exam):
    """{covered_lecture_rows, covered_lectures, covered_subjects,
    covered_chapters} for `exam` - pure relational shaping of already-
    stored data, no completion/readiness calculation (that stays in
    `progress/services/analytics.py: get_exam_readiness()`)."""
    lectures_by_code = {
        lecture.lecture_code: lecture
        for lecture in Lecture.objects.filter(
            lecture_code__in=exam.covered_lectures
        ).select_related("subject")
    }
    covered_lecture_rows = [
        {"code": code, "lecture": lectures_by_code.get(code)}
        for code in exam.covered_lectures
    ]

    covered_lectures = [lec for lec in lectures_by_code.values() if lec is not None]
    seen_subjects, covered_subjects = set(), []
    for lecture in covered_lectures:
        if lecture.subject_id not in seen_subjects:
            seen_subjects.add(lecture.subject_id)
            covered_subjects.append(lecture.subject)

    covered_chapters = list(
        Chapter.objects.filter(lecture_topics__lecture__in=covered_lectures)
        .select_related("subject")
        .distinct()
        .order_by("subject", "paper", "chapter_no")
    )

    return {
        "covered_lecture_rows": covered_lecture_rows,
        "covered_lectures": covered_lectures,
        "covered_subjects": covered_subjects,
        "covered_chapters": covered_chapters,
    }
