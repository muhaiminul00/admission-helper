# Database Design

**Project:** Varsity Admission Tracker\
**Document:** 02_Database_Design.md\
**Version:** 1.1\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This document defines the database schema, relationships, constraints,
import mappings and data lifecycle for Version 1.

The design follows these principles:

-   Keep the schema simple.
-   One table represents one real-world concept.
-   Avoid duplicate data.
-   Store source data; calculate summaries.
-   CSV files are the canonical source of coaching data.
-   SQLite is the primary database.

------------------------------------------------------------------------

# 2. Architecture Overview

``` text
routine.csv
lecture_topics.csv
exams.csv
        │
        ▼
 CSV Import Validation
        │
        ▼
   SQLite Database
        │
        ▼
 Django ORM & Business Logic
        │
        ▼
 Dashboard / Email / Reports
```

------------------------------------------------------------------------

# 3. Entity Relationship Diagram (ERD)

``` text
+-----------+        +-----------+
| Subject   |1------∞| Chapter   |
+-----------+        +-----------+
      |                    ^
      |                    |
      |              ∞      |
      |             +---------------+
      |1          ∞ | LectureTopic  |1------∞+ Progress ∞------1+ User
      +--------------|               |
                     +-------^-------+
                             |
                             |
                      ∞       |1
                        +------------+
                        | Lecture    |1------∞+ RevisionSchedule ∞------1+ User
                        +------------+                   |
                              ^                           |1
                              |                           ∞
                       ∞      |1                    +-----------------+
                        +------------+               | RevisionHistory |
                        | Routine    |               +-----------------+
                        +------------+
                              |
                              |1
                              ∞
                        +------------+
                        | Exam       |
                        +------------+
```

Milestone 7 made Progress per-user (`Progress` -> `User`, many-to-one);
Milestone 9 added `RevisionSchedule` (per `Lecture` per `User`, three
rows per completed lecture) and `RevisionHistory` (append-only, one row
per completed revision).

------------------------------------------------------------------------

# 4. Tables

## Subject (Static)

  Column          Type      Constraints
  --------------- --------- ------------------
  id              PK        Auto
  name            TEXT      NOT NULL
  code            TEXT      UNIQUE, NOT NULL
  display_order   INTEGER   DEFAULT 0

------------------------------------------------------------------------

## Chapter (Static)

Subjects are subject-level (e.g. Physics), so each subject's syllabus
spans two papers, each with its own Chapter 1, Chapter 2, etc. `paper`
disambiguates which paper a chapter belongs to.

  Column          Type           Constraints
  --------------- -------------- -------------
  id              PK             Auto
  subject_id      FK → Subject   CASCADE
  paper           INTEGER        NOT NULL (1 or 2)
  chapter_no      INTEGER        NOT NULL
  name            TEXT           NOT NULL
  display_order   INTEGER        DEFAULT 0

Unique: - (subject_id, paper, chapter_no)

------------------------------------------------------------------------

## Routine

  Column        Type       Constraints
  ------------- ---------- -------------
  id            PK         Auto
  name          TEXT       NOT NULL
  imported_at   DATETIME   Auto
  active        BOOLEAN    DEFAULT True

------------------------------------------------------------------------

## Lecture

A Lecture may be "undated" (`lecture_date IS NULL`) when its
lecture_code is only referenced by `lecture_topics.csv`/`exams.csv` and
has no `routine.csv` CLASS row (self-study subjects, or an
intentionally-skipped lecture number) - see Milestone 4.1 in
PROJECT_PROGRESS.md.

  Column         Type           Constraints
  -------------- -------------- -------------
  id             PK             Auto
  routine_id     FK → Routine   CASCADE
  subject_id     FK → Subject   PROTECT
  lecture_code   TEXT           NOT NULL
  lecture_date   DATE           NULL
  start_time     TIME           NULL
  end_time       TIME           NULL
  notes          TEXT           NULL

Unique: - (routine_id, lecture_code)

------------------------------------------------------------------------

## LectureTopic

`chapter_id` is nullable for subjects with no chapter breakdown at all
in `chapters.csv` (English, Bangla in this dataset).

  Column          Type           Constraints
  --------------- -------------- -------------
  id              PK             Auto
  lecture_id      FK → Lecture   CASCADE
  chapter_id      FK → Chapter   PROTECT, NULL
  topic           TEXT           NOT NULL
  display_order   INTEGER        DEFAULT 1

------------------------------------------------------------------------

## Progress

Milestone 7 made Progress per-user: `lecture_topic_id` is no longer
unique on its own (many users can each have a Progress row for the
same topic) - the unique constraint moved to (`user_id`,
`lecture_topic_id`).

  Column             Type                Constraints
  ------------------ ------------------- ---------------
  id                 PK                  Auto
  user_id            FK → User           CASCADE
  lecture_topic_id   FK → LectureTopic   CASCADE
  class_done         BOOLEAN             DEFAULT False
  notes_done         BOOLEAN             DEFAULT False
  revision_done      BOOLEAN             DEFAULT False
  practice_done      BOOLEAN             DEFAULT False
  updated_at         DATETIME            Auto

Unique: - (user_id, lecture_topic_id)

------------------------------------------------------------------------

## RevisionSchedule

One user's revision stage for one fully-completed Lecture (Milestone
9). References `Lecture` directly - no lecture/topic data is
duplicated here; a lecture's topics are reached via `lecture_id` when
a revision's detail page needs them.

  Column         Type           Constraints
  -------------- -------------- ----------------------------
  id             PK             Auto
  user_id        FK → User      CASCADE
  lecture_id     FK → Lecture   CASCADE
  revision_level INTEGER        NOT NULL (1, 2, or 3)
  due_date       DATE           NOT NULL
  completed_at   DATETIME       NULL
  status         TEXT           DEFAULT 'pending'
  created_at     DATETIME       Auto
  updated_at     DATETIME       Auto

Unique: - (user_id, lecture_id, revision_level)

------------------------------------------------------------------------

## RevisionHistory

An immutable, append-only completion record - never deleted or
edited once written (see Milestone 9 in PROJECT_PROGRESS.md).

  Column               Type                     Constraints
  -------------------- ------------------------ -------------
  id                   PK                       Auto
  revision_schedule_id FK → RevisionSchedule    CASCADE
  completed_at         DATETIME                 NOT NULL
  notes                TEXT                     NULL

------------------------------------------------------------------------

## Exam

  Column             Type           Constraints
  ------------------ -------------- -------------
  id                 PK             Auto
  routine_id         FK → Routine   CASCADE
  exam_code          TEXT           UNIQUE, NOT NULL
  exam_name          TEXT           NOT NULL
  exam_type          TEXT           NOT NULL
  exam_date          DATE           NOT NULL
  online_start       DATE           NULL
  online_end         DATE           NULL
  covered_lectures   TEXT           NULL
  notes              TEXT           NULL

`notes` is no longer populated by CSV import (the finalized `exams.csv`
has no `notes` column); `exam_code`/`online_start`/`online_end` are now
dedicated columns instead of being folded into `notes` as text (see
Milestone 4.1 in PROJECT_PROGRESS.md, which replaced that Milestone 3
workaround).

------------------------------------------------------------------------

## DatasetVersion

One imported CSV dataset snapshot (Milestone 10). `source` points at
the archived copy of that version's source CSVs
(`data/dataset_archive/<version_name>/`) - what actually makes
`rollback_dataset` able to restore a previous version's real data,
since `statistics` is a summary, not a row-level snapshot.

  Column         Type       Constraints
  -------------- ---------- ---------------------------------
  id             PK         Auto
  version_name   TEXT       UNIQUE, NOT NULL
  source         TEXT       NOT NULL
  description    TEXT       NULL
  imported_by_id FK → User  SET_NULL, NULL
  imported_at    DATETIME   Auto
  is_active      BOOLEAN    DEFAULT False
  checksum       TEXT       NOT NULL (SHA-256 hex, 64 chars)
  statistics     JSON       NOT NULL (default `{}`)

Partial unique index: - `is_active` unique where `is_active = True`
(at most one active dataset at a time, enforced by the database).

------------------------------------------------------------------------

## ImportLog

An audit record of one `import_csv`/`rollback_dataset` run - success,
failure, preview, dry run, or rollback (Milestone 10).

  Column            Type        Constraints
  ----------------- ----------- ---------------------------
  id                PK          Auto
  dataset_version_id FK → DatasetVersion  SET_NULL, NULL
  importer_version  TEXT        NOT NULL
  user_id           FK → User   SET_NULL, NULL
  started_at        DATETIME    NOT NULL
  duration_seconds  FLOAT       NULL
  status            TEXT        NOT NULL (indexed)
  imported_counts   JSON        NOT NULL (default `{}`)
  skipped_counts    JSON        NOT NULL (default `{}`)
  errors            TEXT        NULL
  warnings          JSON        NOT NULL (default `[]`)
  created_at        DATETIME    Auto

------------------------------------------------------------------------

# 5. Relationships

-   Subject → Chapters (1:N)
-   Subject → Lectures (1:N)
-   Routine → Lectures (1:N)
-   Routine → Exams (1:N)
-   Lecture → LectureTopics (1:N)
-   Chapter → LectureTopics (1:N)
-   LectureTopic → Progress (1:N) - one row per user who has touched
    that topic (Milestone 7)
-   User → Progress (1:N)
-   Lecture → RevisionSchedule (1:N) - up to 3 rows per user (one per
    revision level) (Milestone 9)
-   User → RevisionSchedule (1:N)
-   RevisionSchedule → RevisionHistory (1:N) - in practice 0 or 1, since
    a schedule only completes once, but modeled as 1:N since nothing
    in the schema prevents re-completion in a future milestone
-   User → DatasetVersion (1:N) - `imported_by` (Milestone 10)
-   User → ImportLog (1:N)
-   DatasetVersion → ImportLog (1:N) - typically 1:1 in practice (one
    successful import creates one version and one log), but a version
    can also be referenced by a later `rollback` log that reactivates
    it

------------------------------------------------------------------------

# 6. CSV Import Mapping

CSV -> Database Field mappings below are unchanged from Milestone 3.
Milestone 10 introduces no new CSV columns or mappings - `DatasetVersion`/
`ImportLog` are populated from import *metadata* (timing, counts,
checksums), never from a new or modified CSV column.

## routine.csv

  CSV Column     Database Field
  -------------- ----------------------
  date           Lecture.lecture_date
  subject_code   Subject.code
  lecture_code   Lecture.lecture_code
  start_time     Lecture.start_time
  end_time       Lecture.end_time
  notes          Lecture.notes

## lecture_topics.csv

  CSV Column      Database Field
  --------------- ----------------------------
  lecture_code    Lecture.lecture_code
  subject_code    Subject.code
  chapter_no      Chapter.paper, Chapter.chapter_no (parsed from the
                  finalized "<paper> পত্র অধ্যায়-<chapter>" reference)
  topic           LectureTopic.topic
  display_order   LectureTopic.display_order

## exams.csv

  CSV Column      Database Field
  --------------- -----------------------
  exam_code       Exam.exam_code
  title           Exam.exam_name
  exam_type       Exam.exam_type
  exam_date       Exam.exam_date
  online_start    Exam.online_start
  online_end      Exam.online_end
  lecture_codes   Exam.covered_lectures

The finalized `exams.csv` has no `notes` column; `Exam.notes` is not
populated by import.

------------------------------------------------------------------------

# 7. Index Strategy

Create indexes on:

-   Subject.code
-   Chapter(subject_id, paper, chapter_no)
-   Lecture.lecture_date
-   Lecture.lecture_code
-   Lecture.subject_id
-   LectureTopic.lecture_id
-   LectureTopic.chapter_id
-   Exam.exam_date
-   Progress(user_id, lecture_topic_id) - via the unique constraint
    (Milestone 7)
-   RevisionSchedule.due_date, RevisionSchedule.status (Milestone 9 -
    both are filtered on directly by the revision queue's Due
    Today/Overdue/Upcoming/Completed buckets)
-   DatasetVersion.version_name (unique), DatasetVersion.is_active
    (partial unique) (Milestone 10)
-   ImportLog.status (Milestone 10 - the dataset history page filters/
    groups by this)

------------------------------------------------------------------------

# 8. Deletion Policy

  Parent             Child              Policy
  ------------------ ------------------ ----------
  Routine            Lecture            CASCADE
  Routine            Exam               CASCADE
  Lecture            LectureTopic       CASCADE
  Lecture            RevisionSchedule   CASCADE
  LectureTopic       Progress           CASCADE
  Subject            Chapter            CASCADE
  Subject            Lecture            PROTECT
  Chapter            LectureTopic       PROTECT
  User               Progress           CASCADE
  User               RevisionSchedule   CASCADE
  RevisionSchedule   RevisionHistory    CASCADE
  User               DatasetVersion     SET_NULL
  User               ImportLog          SET_NULL
  DatasetVersion     ImportLog          SET_NULL

------------------------------------------------------------------------

# 9. Locked CSV Specification

## routine.csv

date, day, event_type, subject_code, lecture_code, title, start_time,
end_time, notes

## lecture_topics.csv

lecture_code, subject_code, chapter_no, topic, display_order

## exams.csv

exam_name, exam_type, date, covered_lectures, notes

These formats are locked for Version 1.

------------------------------------------------------------------------

# 10. Design Decisions

-   SQLite is the only database for V1.
-   Django ORM manages all database access.
-   CSV files are the canonical source of coaching data.
-   Subjects and Chapters are static reference data.
-   Progress is stored only at the LectureTopic level.
-   Chapter progress is always calculated.
-   No ChapterProgress table.
-   No Topic master table.
-   Progress is per-user (Milestone 7) - `django.contrib.auth`'s
    built-in `User`, no custom user model.
-   Revision is scheduled per-Lecture, not per-Topic (Milestone 9) - no
    RevisionTopic table; a lecture's topics are reached via its
    LectureTopics when needed, never duplicated into RevisionSchedule.
-   Revision due dates are deterministic, computed from fixed interval
    constants - no AI, no randomness, no stored "next due date" that
    could drift from the constants that generated it.
-   Revision completion history (RevisionHistory) is append-only and
    never edited or deleted - the narrow exception to "no audit
    logging," scoped specifically to revisions, not a general-purpose
    audit trail for every model.
-   `DatasetVersion.statistics` is a summary (row counts), not a data
    snapshot (Milestone 10) - actual rollback capability comes from
    archived source CSVs on disk (`DatasetVersion.source`), re-imported
    through the same pipeline as any other import, not from
    reconstructing rows out of counts.
-   `DatasetVersion.checksum` is a one-way SHA-256 fingerprint, not
    reversible - it can detect "this exact CSV content was already
    imported as version X," but cannot itself restore data (see
    `source`/archiving above for that).
-   Only one `DatasetVersion` may be active at a time, enforced by a
    partial unique index on `is_active`, not application logic alone.
-   `ImportLog` records every `import_csv`/`rollback_dataset` run,
    including previews and dry runs (which write nothing else to the
    database) and failures (which create no `DatasetVersion`) - "what
    was attempted and when" is tracked independently of "did it
    succeed."

------------------------------------------------------------------------

# 11. Future Compatibility

The schema is database-agnostic.

Migration from SQLite to PostgreSQL can be performed using standard
Django migrations without redesigning the data model.
