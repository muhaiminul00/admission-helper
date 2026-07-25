"""Imports lecture_topics.csv into LectureTopic.

Every validated row is imported - no lecture_code is treated as an
"orphan" anymore (see Milestone 4.1, resolving the Milestone 3 gap):

- `LectureTopic.lecture` resolves via `get_or_create_lecture()`, which
  creates a minimal, undated Lecture the first time a lecture_code with
  no routine.csv CLASS row is encountered (self-study subjects, the
  intentional lecture-06 gap). Nothing is fabricated - only the real
  lecture_code and subject are set; date/day/time/title are left blank.
- `LectureTopic.chapter` is left `None` for subjects that have zero
  chapters defined in chapters.csv (English, Bangla in this dataset -
  detected dynamically, not hardcoded), since chapter_no for those rows
  is a non-varying placeholder label ("Weekly Exam Syllabus"), not a
  real chapter reference. Subjects that DO have chapters must still
  resolve a valid paper+chapter reference - a parse/lookup failure
  there is a genuine error, not a self-study exemption.
"""

from subjects.models import Chapter, Subject

from .base_importer import BaseImporter
from .lecture_helpers import get_or_create_lecture
from .utils import parse_chapter_ref
from .validators import DuplicateTracker, ImportValidationError, parse_int, require


class LectureTopicImporter(BaseImporter):
    filename = "lecture_topics.csv"
    required_columns = ["lecture_code", "subject_code", "chapter_no", "topic", "display_order"]

    def __init__(self, base_dir, stdout):
        super().__init__(base_dir, stdout)
        self._subject_cache = {}
        self._subject_has_chapters_cache = {}
        self._dup_display_order = DuplicateTracker(
            self.filename, "display_order",
            "Duplicate display_order within a lecture (key: lecture_code, display_order) = {key}.",
        )

    def _get_subject(self, code, line):
        if code not in self._subject_cache:
            try:
                self._subject_cache[code] = Subject.objects.get(code=code)
            except Subject.DoesNotExist:
                raise ImportValidationError(
                    self.filename, line,
                    f"Unknown subject code '{code}' (not present in the imported subjects).",
                    Column="subject_code",
                )
        return self._subject_cache[code]

    def _subject_has_chapters(self, subject):
        if subject.code not in self._subject_has_chapters_cache:
            self._subject_has_chapters_cache[subject.code] = Chapter.objects.filter(
                subject=subject
            ).exists()
        return self._subject_has_chapters_cache[subject.code]

    def _resolve_chapter(self, subject, chapter_ref_raw, line):
        if not self._subject_has_chapters(subject):
            return None  # no chapter breakdown exists for this subject - not an error

        parsed = parse_chapter_ref(chapter_ref_raw)
        if parsed is None:
            raise ImportValidationError(
                self.filename, line,
                f"chapter_no '{chapter_ref_raw}' does not match the finalized "
                "'<paper> পত্র অধ্যায়-<chapter>' reference format.",
                Column="chapter_no",
            )
        paper, chapter_no = parsed

        try:
            return Chapter.objects.get(subject=subject, paper=paper, chapter_no=chapter_no)
        except Chapter.DoesNotExist:
            raise ImportValidationError(
                self.filename, line, "Chapter not found",
                Subject=subject.name, Paper=paper, Chapter=f"{chapter_no:02d}",
            )

    def validate_row(self, row):
        line = row["_line"]
        lecture_code = require(self.field(row, "lecture_code"), self.filename, line, "lecture_code")
        subject_code = require(self.field(row, "subject_code"), self.filename, line, "subject_code")
        require(self.field(row, "chapter_no"), self.filename, line, "chapter_no")
        require(self.field(row, "topic"), self.filename, line, "topic")
        parse_int(self.field(row, "display_order"), self.filename, line, "display_order")

        subject = self._get_subject(subject_code, line)
        self._resolve_chapter(subject, self.field(row, "chapter_no").strip(), line)
        self._dup_display_order.check(
            (lecture_code, self.field(row, "display_order").strip()), line
        )

    def import_row(self, row):
        line = row["_line"]
        lecture_code = self.field(row, "lecture_code").strip()
        subject_code = self.field(row, "subject_code").strip()
        chapter_ref_raw = self.field(row, "chapter_no").strip()
        topic = self.field(row, "topic").strip()
        display_order = int(self.field(row, "display_order").strip())

        subject = self._get_subject(subject_code, line)
        lecture = get_or_create_lecture(lecture_code, subject)
        chapter = self._resolve_chapter(subject, chapter_ref_raw, line)

        from lectures.models import LectureTopic

        LectureTopic.objects.update_or_create(
            lecture=lecture, chapter=chapter, topic=topic,
            defaults={"display_order": display_order},
        )
        self.imported_count += 1
