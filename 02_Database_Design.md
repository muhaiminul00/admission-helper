# Database Design

**Project:** Varsity Admission Tracker\
**Version:** 1.0\
**Status:** Locked

------------------------------------------------------------------------

# 1. Design Principles

-   Keep the database simple.
-   One table represents one real-world concept.
-   Store only source data.
-   Calculate progress instead of storing aggregates.
-   CSV files are the source of coaching data.
-   SQLite is the primary database for Version 1.

------------------------------------------------------------------------

# 2. Data Flow

``` text
CSV Files
    │
    ▼
CSV Import
    │
    ▼
SQLite Database
    │
    ▼
Django Application
```

Source CSV files:

-   routine.csv
-   lecture_topics.csv
-   exams.csv

------------------------------------------------------------------------

# 3. Entity Relationship Overview

``` text
Subject
   │
   ├── Chapter
   │
Routine
   │
   ├── Lecture
   │      │
   │      └── LectureTopic
   │                 │
   │                 └── Progress
   │
   └── Exam
```

------------------------------------------------------------------------

# 4. Tables

## Subject

Static reference data.

  Column          Type      Notes
  --------------- --------- ----------
  id              PK        Auto
  name            TEXT      Physics
  short_code      TEXT      P
  display_order   INTEGER   UI order

------------------------------------------------------------------------

## Chapter

Static syllabus.

  Column          Type           Notes
  --------------- -------------- -----------------------------
  id              PK             Auto
  subject_id      FK → Subject   
  chapter_no      INTEGER        Subject-wise chapter number
  name            TEXT           Chapter title
  display_order   INTEGER        UI order

Constraint:

-   UNIQUE(subject_id, chapter_no)

------------------------------------------------------------------------

## Routine

Represents one imported coaching routine.

  Column        Type
  ------------- ----------
  id            PK
  name          TEXT
  start_date    DATE
  end_date      DATE
  imported_at   DATETIME

------------------------------------------------------------------------

## Lecture

One scheduled lecture.

  Column         Type
  -------------- --------------
  id             PK
  routine_id     FK → Routine
  subject_id     FK → Subject
  lecture_code   TEXT
  lecture_date   DATE
  start_time     TIME
  end_time       TIME
  notes          TEXT NULL

Constraint:

-   UNIQUE(routine_id, lecture_code)

------------------------------------------------------------------------

## LectureTopic

Smallest study unit.

  Column          Type
  --------------- --------------
  id              PK
  lecture_id      FK → Lecture
  chapter_id      FK → Chapter
  topic           TEXT
  display_order   INTEGER

------------------------------------------------------------------------

## Progress

Study progress for one LectureTopic.

  Column             Type
  ------------------ -------------------
  id                 PK
  lecture_topic_id   FK → LectureTopic
  class_done         BOOLEAN
  notes_done         BOOLEAN
  revision_done      BOOLEAN
  practice_done      BOOLEAN
  updated_at         DATETIME

Constraint:

-   UNIQUE(lecture_topic_id)

------------------------------------------------------------------------

## Exam

  Column             Type
  ------------------ --------------
  id                 PK
  routine_id         FK → Routine
  exam_name          TEXT
  exam_type          TEXT
  exam_date          DATE
  covered_lectures   TEXT
  notes              TEXT NULL

------------------------------------------------------------------------

# 5. Relationships

-   One Subject has many Chapters.
-   One Subject has many Lectures.
-   One Routine has many Lectures.
-   One Routine has many Exams.
-   One Lecture has many LectureTopics.
-   One Chapter can appear in many LectureTopics.
-   One LectureTopic has one Progress record.

------------------------------------------------------------------------

# 6. Locked CSV Specification

## routine.csv

  Column
  --------------
  date
  day
  event_type
  subject_code
  lecture_code
  title
  start_time
  end_time
  notes

## lecture_topics.csv

  Column
  ---------------
  lecture_code
  subject_code
  chapter_no
  topic
  display_order

## exams.csv

  Column
  ------------------
  exam_name
  exam_type
  date
  covered_lectures
  notes

These formats are locked for Version 1.

------------------------------------------------------------------------

# 7. Design Decisions

-   SQLite is the primary database.
-   CSV files are the canonical source for coaching data.
-   Subjects and Chapters are static.
-   Routines, Lectures and Exams are imported.
-   Chapter progress is calculated from Progress records.
-   No ChapterProgress table.
-   No Topic master table.
-   No many-to-many bridge tables beyond LectureTopic.

------------------------------------------------------------------------

# 8. Future Migration

The schema is designed to be database-agnostic.

Future migration from SQLite to PostgreSQL can be handled through Django
migrations without changing the data model.
