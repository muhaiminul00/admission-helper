# Varsity Admission Tracker

## Product Requirements & Architecture (Version 1.0)

> **Purpose:** This document defines the product vision, architecture,
> data model, UI philosophy, and technical stack for the Varsity
> Admission Tracker before implementation.

------------------------------------------------------------------------

# 1. Vision

The application is **not** a generic study planner or task manager.

Its primary goals are:

1.  Never miss a coaching class or exam.
2.  Always know what to study today.
3.  Track study progress in a way that matches the coaching structure.
4.  Keep the interface simple and fast.

The system should answer three questions immediately:

-   What do I have today?
-   What should I finish next?
-   How far have I progressed?

------------------------------------------------------------------------

# 2. Core Design Philosophy

The system has two independent layers.

## A. Static Layer (Permanent)

This is entered once and rarely changes.

-   Subjects
-   Chapters (Admission syllabus)

Chapter cards exist from the first day.

Example:

Physics - Chapter 1 - Chapter 2 - ... - Chapter 10

## B. Dynamic Layer (Routine)

Every new coaching routine creates:

-   Lecture schedule
-   Lecture codes (P-10, C-08, M-12, etc.)
-   Topics covered
-   Exam schedule

Old progress must never be lost when a new routine is imported.

------------------------------------------------------------------------

# 3. Core Data Model

Subject ├── Chapter (Static) │ └── Lecture (Dynamic) │ ├── Chapter
Section │ ├── Topics │ └── Progress │ ├── Chapter Section │ ├── Topics │
└── Progress │ └── ...

Important:

Progress is **NOT** stored on the lecture.

Progress is stored on each Chapter Section inside a lecture.

This supports:

-   one lecture → multiple chapters
-   one chapter → multiple lectures

------------------------------------------------------------------------

# 4. Example

Lecture:

P-11

Contains:

Chapter 9 - Wave (Remaining)

Chapter 10 - Ideal Gas

Progress:

Chapter 9

-   Class
-   Notes
-   Revision
-   Practice

Chapter 10

-   Class
-   Notes
-   Revision
-   Practice

These are tracked independently.

------------------------------------------------------------------------

# 5. Chapter Card Behaviour

Every chapter card exists before any routine is imported.

States:

1.  Not Scheduled
    -   No lecture assigned.
2.  Scheduled
    -   Future lecture exists.
3.  In Progress
    -   At least one lecture section completed.
4.  Completed
    -   All lecture sections completed.

The state is calculated automatically.

------------------------------------------------------------------------

# 6. Lecture Card Behaviour

Displays:

-   Lecture Code
-   Date
-   Subject
-   Covered chapters
-   Topics
-   Progress for each chapter section

Example:

P-11

Chapter 9

✓ Class ✓ Notes □ Revision □ Practice

------------------------------------------------------------------------

Chapter 10

✓ Class □ Notes □ Revision □ Practice

------------------------------------------------------------------------

# 7. Dashboard

Displays:

-   Today's class
-   Today's exam
-   Upcoming weekly exam
-   Upcoming monthly exam
-   Continue Studying
-   Pending work
-   Subject cards

------------------------------------------------------------------------

# 8. Subject Page

Shows every chapter card.

Each card displays:

-   Phase
-   Progress
-   Next lecture
-   Lecture count
-   Overall completion

------------------------------------------------------------------------

# 9. Chapter Page

Displays:

-   Chapter information
-   Related lectures
-   Timeline
-   Completion statistics

------------------------------------------------------------------------

# 10. Lecture Page

Displays:

-   Lecture code
-   Date
-   Topics
-   Separate progress block for every chapter section

------------------------------------------------------------------------

# 11. Reminder System (MVP)

Daily

-   Morning reminder
-   One-hour-before-class reminder
-   Night reminder if class not marked complete

Weekly

-   Weekly schedule summary
-   Weekly exam reminder

Monthly

-   Monthly revision test reminder

Delivery:

-   Email

------------------------------------------------------------------------

# 12. Routine Import

Admin uploads a coaching routine.

Importer creates:

-   Lectures
-   Dates
-   Topics
-   Chapter mappings
-   Exams

No manual chapter creation required.

------------------------------------------------------------------------

# 13. Database (Conceptual)

Subjects

Chapters

Lectures

LectureChapter - lecture - chapter - topics

Progress - lecture_chapter - class_done - notes_done - revision_done -
practice_done - timestamps

Routine

Exam

------------------------------------------------------------------------

# 14. UI Principles

-   Minimal clicks
-   No clutter
-   Color-based status
-   Mobile-first
-   Fast loading
-   No unnecessary charts

Status Colors

Green = Done

Red = Pending

Gray = Not Scheduled

Yellow = In Progress

------------------------------------------------------------------------

# 15. Technology Stack

Backend

-   Python
-   Django

Frontend

-   Django Templates
-   HTMX
-   Tailwind CSS

Database

-   SQLite (development)
-   PostgreSQL (production)

Background Jobs

-   Celery + Redis (or Django-Q)

Email

-   Gmail SMTP

Deployment

-   Railway / Render / VPS

------------------------------------------------------------------------

# 16. MVP Scope

Included

-   Authentication
-   Dashboard
-   Subject pages
-   Chapter cards
-   Lecture pages
-   Chapter-section progress
-   Daily reminders
-   Weekly reminders
-   Monthly reminders
-   Routine import
-   Email notifications

Excluded

-   AI recommendations
-   Analytics
-   Mobile app
-   Telegram/WhatsApp
-   OCR automation
-   Spaced repetition

------------------------------------------------------------------------

# 17. Guiding Principle

The application should mirror **how the coaching actually teaches**, not
force the coaching into a textbook hierarchy.

Everything revolves around lectures, while progress is tracked at the
smallest meaningful unit:

**Chapter Section inside a Lecture**.

This ensures accurate progress tracking, automatic chapter updates, and
a clean user experience that scales with future coaching routines.
