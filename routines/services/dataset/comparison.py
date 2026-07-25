"""Compares a set of new CSVs against the current database state
(Milestone 10) - the engine behind `import_csv --preview` and the
standalone `compare_dataset` command (both call the exact same
functions here, so there is only one comparison implementation, not
two).

Every entity's comparison is keyed by its natural identity (the same
key each importer already uses for `update_or_create()`), read via the
importer's own `read_csv_rows()` / `parse_chapter_ref()` (reused, not
reimplemented) and fetched from the database with `.values(...)` -
never loading full model instances for rows that will only be diffed
field-by-field.

`Lectures` here means only `routine.csv`'s `CLASS` rows (the ones that
become `Lecture` rows - see PROJECT_PROGRESS.md, Milestone 3).
`Routine Events` is a separate, deliberately lighter-weight summary of
*every* `routine.csv` row (including `DAILY_EXAM`/`WEEKLY_EXAM`/
`MONTHLY_EXAM`, which have no persisted model at all) - see
`compare_routine_events()` for why it can't use the same
Added/Removed/Modified/Unchanged shape as the other five.
"""

from pathlib import Path

from lectures.models import LectureTopic
from routines.models import Exam, Lecture
from subjects.models import Chapter, Subject

from ..csv.utils import parse_chapter_ref, read_csv_rows

EMPTY_DIFF = {"added": [], "removed": [], "modified": [], "unchanged": []}


def _diff(new_by_key, old_by_key, fields):
    """Generic Added/Removed/Modified/Unchanged diff.

    `new_by_key`/`old_by_key`: {key: {field: value, ...}}. `fields` is
    the list of field names to compare when a key exists on both sides.
    """
    result = {"added": [], "removed": [], "modified": [], "unchanged": []}

    for key, new_row in new_by_key.items():
        old_row = old_by_key.get(key)
        if old_row is None:
            result["added"].append({"key": key, "new": new_row})
            continue
        changes = {
            field: {"old": old_row.get(field), "new": new_row.get(field)}
            for field in fields
            if old_row.get(field) != new_row.get(field)
        }
        if changes:
            result["modified"].append({"key": key, "changes": changes})
        else:
            result["unchanged"].append({"key": key})

    for key, old_row in old_by_key.items():
        if key not in new_by_key:
            result["removed"].append({"key": key, "old": old_row})

    return result


def compare_subjects(base_dir):
    _, rows = read_csv_rows(Path(base_dir) / "subjects.csv")
    new_by_key = {
        row.get("code", "").strip(): {
            "name": row.get("name", "").strip(),
            "display_order": row.get("display_order", "").strip(),
        }
        for row in rows
        if row.get("code", "").strip()
    }
    old_by_key = {
        s["code"]: {"name": s["name"], "display_order": str(s["display_order"])}
        for s in Subject.objects.values("code", "name", "display_order")
    }
    return _diff(new_by_key, old_by_key, ["name", "display_order"])


def compare_chapters(base_dir):
    _, rows = read_csv_rows(Path(base_dir) / "chapters.csv")
    new_by_key = {
        (
            row.get("subject_code", "").strip(),
            row.get("paper", "").strip(),
            row.get("chapter_no", "").strip(),
        ): {
            "chapter_name": row.get("chapter_name", "").strip(),
            "display_order": row.get("display_order", "").strip(),
        }
        for row in rows
        if row.get("subject_code", "").strip()
    }
    old_by_key = {
        (c["subject__code"], str(c["paper"]), str(c["chapter_no"])): {
            "chapter_name": c["name"], "display_order": str(c["display_order"]),
        }
        for c in Chapter.objects.values("subject__code", "paper", "chapter_no", "name", "display_order")
    }
    return _diff(new_by_key, old_by_key, ["chapter_name", "display_order"])


def compare_lectures(base_dir):
    """Only `CLASS` rows with both `subject_code` and `lecture_code`
    present - the general/orientation row and non-`CLASS` rows have no
    `Lecture` counterpart to compare against (see module docstring)."""
    _, rows = read_csv_rows(Path(base_dir) / "routine.csv")
    new_by_key = {}
    for row in rows:
        if row.get("event_type", "").strip() != "CLASS":
            continue
        lecture_code = row.get("lecture_code", "").strip()
        subject_code = row.get("subject_code", "").strip()
        if not lecture_code or not subject_code:
            continue
        new_by_key[lecture_code] = {
            "subject_code": subject_code,
            "title": row.get("title", "").strip(),
            "date": row.get("date", "").strip(),
            "day": row.get("day", "").strip(),
            "start_time": row.get("start_time", "").strip(),
            "end_time": row.get("end_time", "").strip(),
            "notes": row.get("notes", "").strip(),
        }

    old_by_key = {
        lec["lecture_code"]: {
            "subject_code": lec["subject__code"],
            "title": lec["title"],
            "date": str(lec["lecture_date"]) if lec["lecture_date"] else "",
            "day": lec["day"],
            "start_time": lec["start_time"].strftime("%H:%M") if lec["start_time"] else "",
            "end_time": lec["end_time"].strftime("%H:%M") if lec["end_time"] else "",
            "notes": lec["notes"],
        }
        for lec in Lecture.objects.filter(lecture_date__isnull=False).values(
            "lecture_code", "subject__code", "title", "lecture_date", "day",
            "start_time", "end_time", "notes",
        )
    }
    return _diff(
        new_by_key, old_by_key,
        ["subject_code", "title", "date", "day", "start_time", "end_time", "notes"],
    )


def compare_lecture_topics(base_dir):
    """Keyed by (lecture_code, topic) - `topic` text is effectively
    unique within a lecture in this dataset, and avoids needing to
    re-resolve each row's chapter reference against the database just
    to build a comparison key (the point of this pass is detecting
    *changes*, not re-validating chapter references - that's still the
    importer's job)."""
    _, rows = read_csv_rows(Path(base_dir) / "lecture_topics.csv")
    new_by_key = {
        (row.get("lecture_code", "").strip(), row.get("topic", "").strip()): {
            "chapter_ref": row.get("chapter_no", "").strip(),
            "display_order": row.get("display_order", "").strip(),
        }
        for row in rows
        if row.get("lecture_code", "").strip() and row.get("topic", "").strip()
    }

    old_by_key = {}
    for topic in LectureTopic.objects.select_related("chapter", "lecture").only(
        "topic", "display_order", "lecture__lecture_code", "chapter__paper", "chapter__chapter_no"
    ):
        chapter_ref = ""
        if topic.chapter_id is not None:
            chapter_ref = f"{topic.chapter.paper}-{topic.chapter.chapter_no}"
        old_by_key[(topic.lecture.lecture_code, topic.topic)] = {
            "chapter_ref": chapter_ref,
            "display_order": str(topic.display_order),
        }

    # Normalize the new side's Bengali chapter references to the same
    # "paper-chapter_no" shorthand used above, via the importer's own
    # parser, so a real chapter change is detected even though the raw
    # text representations differ.
    for key, row in new_by_key.items():
        parsed = parse_chapter_ref(row["chapter_ref"])
        row["chapter_ref"] = f"{parsed[0]}-{parsed[1]}" if parsed else ""

    return _diff(new_by_key, old_by_key, ["chapter_ref", "display_order"])


def compare_exams(base_dir):
    _, rows = read_csv_rows(Path(base_dir) / "exams.csv")
    new_by_key = {
        row.get("exam_code", "").strip(): {
            "title": row.get("title", "").strip(),
            "exam_type": row.get("exam_type", "").strip(),
            "exam_date": row.get("exam_date", "").strip(),
            "online_start": row.get("online_start", "").strip(),
            "online_end": row.get("online_end", "").strip(),
            "lecture_codes": row.get("lecture_codes", "").strip(),
        }
        for row in rows
        if row.get("exam_code", "").strip()
    }
    old_by_key = {
        e["exam_code"]: {
            "title": e["exam_name"],
            "exam_type": e["exam_type"].upper(),
            "exam_date": str(e["exam_date"]),
            "online_start": str(e["online_start"]) if e["online_start"] else "",
            "online_end": str(e["online_end"]) if e["online_end"] else "",
            "lecture_codes": ",".join(e["covered_lectures"]),
        }
        for e in Exam.objects.values(
            "exam_code", "exam_name", "exam_type", "exam_date",
            "online_start", "online_end", "covered_lectures",
        )
    }
    return _diff(
        new_by_key, old_by_key,
        ["title", "exam_type", "exam_date", "online_start", "online_end", "lecture_codes"],
    )


def compare_routine_events(base_dir, lecture_diff=None):
    """A row-count breakdown of the *new* `routine.csv` by
    `event_type`, not an Added/Removed/Modified/Unchanged diff:
    `DAILY_EXAM`/`WEEKLY_EXAM`/`MONTHLY_EXAM` rows have no persisted
    model at all (see PROJECT_PROGRESS.md, Milestone 3), so there is no
    "previous state" in the database to diff a non-`CLASS` row
    against - reporting a fabricated diff for data that was never
    stored would be misleading. `CLASS` rows *are* diffed properly,
    just under "Lectures" (`compare_lectures()`), which this function
    cross-references rather than duplicating.

    `lecture_diff` lets `compare_all()` pass in the `compare_lectures()`
    result it already computed, rather than this function silently
    recomputing the same diff (a second CSV read + DB query) - pass
    nothing when calling this function on its own.
    """
    _, rows = read_csv_rows(Path(base_dir) / "routine.csv")
    by_event_type = {}
    for row in rows:
        event_type = row.get("event_type", "").strip()
        by_event_type[event_type] = by_event_type.get(event_type, 0) + 1

    if lecture_diff is None:
        lecture_diff = compare_lectures(base_dir)
    return {
        "total_rows": len(rows),
        "by_event_type": by_event_type,
        "class_rows_added": len(lecture_diff["added"]),
        "class_rows_modified": len(lecture_diff["modified"]),
        "class_rows_removed": len(lecture_diff["removed"]),
        "class_rows_unchanged": len(lecture_diff["unchanged"]),
    }


COMPARISON_SECTIONS = [
    ("subjects", "Subjects", compare_subjects),
    ("chapters", "Chapters", compare_chapters),
    ("lectures", "Lectures", compare_lectures),
    ("lecture_topics", "Lecture Topics", compare_lecture_topics),
    ("exams", "Exams", compare_exams),
]


def compare_all(base_dir):
    """Every model-backed comparison, plus the routine-events summary,
    in one dict - the single function both `import_csv --preview` and
    `compare_dataset` call."""
    result = {key: fn(base_dir) for key, _label, fn in COMPARISON_SECTIONS}
    result["routine_events"] = compare_routine_events(base_dir, lecture_diff=result["lectures"])
    return result


def _find_dupes(keys):
    seen = set()
    dupes = []
    for key in keys:
        if key in seen and key not in dupes:
            dupes.append(key)
        seen.add(key)
    return dupes


def detect_duplicates(base_dir):
    """A pre-flight duplicate scan across all five CSVs, *before* any
    import stage runs (per this milestone's "Detect ... before import
    begins").

    This is deliberately a second, independent check from each
    importer's inline `DuplicateTracker` (which still runs during the
    real import as defense-in-depth, per its own docstring) - this one
    exists to produce one consolidated report up front (for
    `--preview` and `compare_dataset`) rather than aborting import at
    the first duplicate row encountered.
    """
    base_dir = Path(base_dir)

    _, subject_rows = read_csv_rows(base_dir / "subjects.csv")
    _, chapter_rows = read_csv_rows(base_dir / "chapters.csv")
    _, routine_rows = read_csv_rows(base_dir / "routine.csv")
    _, topic_rows = read_csv_rows(base_dir / "lecture_topics.csv")
    _, exam_rows = read_csv_rows(base_dir / "exams.csv")

    class_lecture_codes = [
        row.get("lecture_code", "").strip()
        for row in routine_rows
        if row.get("event_type", "").strip() == "CLASS" and row.get("lecture_code", "").strip()
    ]

    return {
        "subjects": _find_dupes(row.get("code", "").strip() for row in subject_rows),
        "chapters": _find_dupes(
            (
                row.get("subject_code", "").strip(),
                row.get("paper", "").strip(),
                row.get("chapter_no", "").strip(),
            )
            for row in chapter_rows
        ),
        "lectures": _find_dupes(class_lecture_codes),
        "lecture_topics": _find_dupes(
            (row.get("lecture_code", "").strip(), row.get("topic", "").strip())
            for row in topic_rows
        ),
        "exams": _find_dupes(row.get("exam_code", "").strip() for row in exam_rows),
    }


def has_duplicates(duplicate_report):
    return any(duplicate_report.values())
