# Navigation & Screen Flow

**Project:** Varsity Admission Tracker\
**Document:** 04_Navigation_Screen_Flow.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This document defines every screen in the application and how users move
between them.

The navigation is intentionally shallow so that every important feature
is reachable within one or two clicks.

------------------------------------------------------------------------

# 2. Navigation Principles

-   Keep navigation simple.
-   One primary navigation bar.
-   Maximum three navigation levels.
-   Dashboard is always the home screen.
-   Every page has a clear way back.

------------------------------------------------------------------------

# 3. Main Navigation

``` text
Dashboard
│
├── Subjects
├── Routine
├── Exams
└── Settings
```

These four items form the primary navigation.

------------------------------------------------------------------------

# 4. Screen Flow

``` text
Dashboard
│
├── Subjects
│     │
│     ├── Subject Details
│     │      │
│     │      ├── Chapter Details
│     │      │       │
│     │      │       └── Lecture Details
│     │      │
│     │      └── Continue Studying
│     │
│     └── Back to Dashboard
│
├── Routine
│     │
│     ├── Current Routine
│     ├── Import CSV
│     └── Import History
│
├── Exams
│     │
│     ├── Upcoming Exams
│     └── Exam Details
│
└── Settings
      │
      ├── Email Settings
      └── About
```

------------------------------------------------------------------------

# 5. Screen Definitions

## Dashboard

The application's landing page.

Displays:

-   Today's Classes
-   Today's Exams
-   Continue Studying
-   Pending Tasks
-   Subject Progress
-   Upcoming Exams

Actions:

-   Open Subject
-   Open Lecture
-   View Routine
-   View Exams

------------------------------------------------------------------------

## Subjects

Displays all subjects.

Each subject card shows:

-   Subject name
-   Overall progress
-   Number of chapters
-   Next lecture

Selecting a subject opens the Subject Details page.

------------------------------------------------------------------------

## Subject Details

Displays all chapters for the selected subject.

Each chapter card shows:

-   Chapter name
-   Progress
-   Status
-   Related lectures

Selecting a chapter opens Chapter Details.

------------------------------------------------------------------------

## Chapter Details

Displays:

-   Chapter information
-   Related lecture topics
-   Progress timeline

Selecting a lecture opens Lecture Details.

------------------------------------------------------------------------

## Lecture Details

Primary study page.

Displays:

-   Lecture information
-   Lecture topics
-   Progress checklist

Users update:

-   Class
-   Notes
-   Revision
-   Practice

After saving, the user returns to the previous page or Dashboard.

------------------------------------------------------------------------

## Routine

Displays:

-   Active routine
-   Import button
-   Import history

Importing a routine starts the CSV validation process.

------------------------------------------------------------------------

## Exams

Displays:

-   Upcoming exams
-   Exam type
-   Date
-   Covered lectures

Selecting an exam opens Exam Details.

------------------------------------------------------------------------

## Exam Details

Displays:

-   Exam information
-   Covered lectures
-   Notes

------------------------------------------------------------------------

## Settings

Displays:

-   Email address
-   Reminder preferences
-   Application information

Version 1 intentionally keeps this page minimal.

------------------------------------------------------------------------

# 6. Common Navigation Paths

## Daily Study

``` text
Dashboard
    │
    ▼
Continue Studying
    │
    ▼
Lecture Details
    │
    ▼
Update Progress
    │
    ▼
Dashboard
```

------------------------------------------------------------------------

## Subject Review

``` text
Dashboard
    │
    ▼
Subjects
    │
    ▼
Subject Details
    │
    ▼
Chapter Details
```

------------------------------------------------------------------------

## Routine Import

``` text
Dashboard
    │
    ▼
Routine
    │
    ▼
Import CSV
    │
    ▼
Validation
    │
    ▼
Import Complete
    │
    ▼
Dashboard
```

------------------------------------------------------------------------

## Exam Review

``` text
Dashboard
    │
    ▼
Exams
    │
    ▼
Exam Details
```

------------------------------------------------------------------------

# 7. Screen Hierarchy

``` text
Level 1
--------
Dashboard
Subjects
Routine
Exams
Settings

Level 2
--------
Subject Details
Current Routine
Upcoming Exams

Level 3
--------
Chapter Details
Lecture Details
Exam Details
Import History
```

No screen should exceed Level 3.

------------------------------------------------------------------------

# 8. Version 1 Scope

Included:

-   Dashboard
-   Subjects
-   Subject Details
-   Chapter Details
-   Lecture Details
-   Routine
-   CSV Import
-   Exams
-   Settings

Excluded:

-   Search
-   Notifications page
-   User profile
-   Calendar view
-   Analytics dashboard
-   Multiple users

------------------------------------------------------------------------

# 9. Design Decisions

-   Dashboard is always the entry point.
-   "Continue Studying" provides the fastest path back to unfinished
    work.
-   Navigation depth is limited to three levels.
-   Routine management is separated from study pages.
-   Study progress is updated only from the Lecture Details page.
-   Every screen has a single primary purpose to reduce complexity.
