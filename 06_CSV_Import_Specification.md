# CSV Import Specification

**Project:** Varsity Admission Tracker\
**Document:** 06_CSV_Import_Specification.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This document defines the CSV import process for Version 1.

The CSV files are the **canonical source** of coaching data. The
application imports these files into SQLite after validation.

------------------------------------------------------------------------

# 2. Supported Files

The application accepts exactly three CSV files:

1.  `routine.csv`
2.  `lecture_topics.csv`
3.  `exams.csv`

Any other file names or structures are unsupported.

------------------------------------------------------------------------

# 3. Import Order

Files are imported in the following order:

``` text
routine.csv
      ↓
lecture_topics.csv
      ↓
exams.csv
```

If any step fails validation, the entire import is cancelled.

------------------------------------------------------------------------

# 4. CSV Specifications

## routine.csv

  Column         Required      Type                         Description
  -------------- ------------- ---------------------------- ------------------------
  date           Yes           Date (YYYY-MM-DD)            Lecture or event date
  day            No            Text                         Optional display value
  event_type     Yes           CLASS, EXAM, OFFDAY, OTHER   Event category
  subject_code   Conditional   Text                         Required for CLASS
  lecture_code   Conditional   Text                         Required for CLASS
  title          No            Text                         Display title
  start_time     No            HH:MM (24-hour)              Start time
  end_time       No            HH:MM (24-hour)              End time
  notes          No            Text                         Remarks

------------------------------------------------------------------------

## lecture_topics.csv

  Column          Required   Type      Description
  --------------- ---------- --------- ----------------------------
  lecture_code    Yes        Text      Must exist in routine.csv
  subject_code    Yes        Text      Must match a Subject
  chapter_no      Yes        Integer   Must exist for the subject
  topic           Yes        Text      Topic or remaining portion
  display_order   No         Integer   Default = 1

------------------------------------------------------------------------

## exams.csv

  ---------------------------------------------------------------------------------
  Column             Required            Type              Description
  ------------------ ------------------- ----------------- ------------------------
  exam_name          Yes                 Text              Exam title

  exam_type          Yes                 WEEKLY, MONTHLY,  Exam category
                                         MODEL             

  date               Yes                 Date              Exam date

  covered_lectures   No                  Comma-separated   Example: P-10,P-11,C-05
                                         text              

  notes              No                  Text              Remarks
  ---------------------------------------------------------------------------------

------------------------------------------------------------------------

# 5. Validation Rules

General:

-   UTF-8 encoded CSV files
-   First row must contain headers
-   Column names must match exactly
-   Blank rows are ignored

Routine validation:

-   Dates must use `YYYY-MM-DD`
-   Time must use `HH:MM` (24-hour)
-   `lecture_code` must be unique within a routine
-   `subject_code` must exist in the static syllabus

Lecture Topic validation:

-   Every `lecture_code` must exist in `routine.csv`
-   Every `(subject_code, chapter_no)` must exist in the syllabus
-   `topic` cannot be empty

Exam validation:

-   `exam_type` must be supported
-   Dates must be valid

------------------------------------------------------------------------

# 6. Duplicate Handling

  Item                                    Behavior
  --------------------------------------- ----------------------
  Duplicate lecture_code in one routine   Reject import
  Duplicate lecture topic row             Reject duplicate row
  Duplicate exam                          Reject duplicate row

------------------------------------------------------------------------

# 7. Error Handling

If validation fails:

-   Nothing is imported
-   Existing data remains unchanged
-   Errors are displayed in a readable list

Example:

``` text
Row 15: Lecture code 'P-11' not found.
Row 28: Chapter 12 does not exist for Physics.
Row 41: Invalid date format. Expected YYYY-MM-DD.
```

------------------------------------------------------------------------

# 8. Import Workflow

``` text
Upload CSV Files
        │
        ▼
Validate Structure
        │
        ▼
Validate Relationships
        │
        ▼
Create Routine
        │
        ▼
Create Lectures
        │
        ▼
Create LectureTopics
        │
        ▼
Create Exams
        │
        ▼
Import Complete
```

------------------------------------------------------------------------

# 9. Database Mapping

  CSV File             Database Tables
  -------------------- ------------------
  routine.csv          Routine, Lecture
  lecture_topics.csv   LectureTopic
  exams.csv            Exam

Progress is never imported. It is created and maintained by the
application.

------------------------------------------------------------------------

# 10. Source of Truth

  Data             Source
  ---------------- -------------
  Subjects         Application
  Chapters         Application
  Routines         CSV
  Lectures         CSV
  Lecture Topics   CSV
  Exams            CSV
  Progress         Application

------------------------------------------------------------------------

# 11. Future Compatibility

Future versions may support:

-   Excel (.xlsx)
-   Direct PDF extraction
-   Bulk routine updates

Version 1 supports **CSV only**.
