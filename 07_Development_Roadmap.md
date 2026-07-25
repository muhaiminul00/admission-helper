# Development Roadmap

**Project:** Varsity Admission Tracker\
**Document:** 07_Development_Roadmap.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Purpose

This roadmap defines the recommended implementation order for Version 1.

The goal is to build a working application through small, testable
milestones rather than developing every feature at once.

------------------------------------------------------------------------

# 2. Development Principles

-   Build one feature at a time.
-   Keep the application deployable after every milestone.
-   Test before moving to the next phase.
-   Avoid premature optimization.
-   Prefer working software over perfect software.

------------------------------------------------------------------------

# 3. Milestone Overview

``` text
Project Setup
      ↓
Database Models
      ↓
CSV Import
      ↓
Dashboard
      ↓
Subjects
      ↓
Lectures & Progress
      ↓
Exams
      ↓
Reminders
      ↓
UI Polish
      ↓
Deployment
```

------------------------------------------------------------------------

# 4. Milestone 1 --- Project Setup

## Objectives

-   Create Django project
-   Create Django apps
-   Configure Tailwind CSS
-   Configure HTMX
-   Configure SQLite
-   Create base template

### Deliverable

A running Django application with the agreed project structure.

------------------------------------------------------------------------

# 5. Milestone 2 --- Database Models

## Objectives

Implement models:

-   Subject
-   Chapter
-   Routine
-   Lecture
-   LectureTopic
-   Progress
-   Exam

### Deliverable

Database migrations completed and models verified.

------------------------------------------------------------------------

# 6. Milestone 3 --- CSV Import

## Objectives

-   CSV upload page
-   Validation
-   Import Routine
-   Import Lectures
-   Import Lecture Topics
-   Import Exams
-   Import summary

### Deliverable

A complete routine can be imported successfully.

------------------------------------------------------------------------

# 7. Milestone 4 --- Dashboard

## Objectives

Implement:

-   Today's Classes
-   Today's Exams
-   Continue Studying
-   Pending Tasks
-   Subject Progress
-   Upcoming Exams

### Deliverable

Dashboard displays live data from the database.

------------------------------------------------------------------------

# 8. Milestone 5 --- Subjects

## Objectives

Build:

-   Subject list
-   Subject details
-   Chapter details

### Deliverable

Users can browse the syllabus and related lectures.

------------------------------------------------------------------------

# 9. Milestone 6 --- Lectures & Progress

## Objectives

Build:

-   Lecture Details page
-   Progress checklist
-   Automatic progress updates
-   Continue Studying logic

### Deliverable

Users can track study progress.

------------------------------------------------------------------------

# 10. Milestone 7 --- Exams

## Objectives

Build:

-   Exam list
-   Exam details
-   Upcoming exam display

### Deliverable

Exam schedule is fully integrated.

------------------------------------------------------------------------

# 11. Milestone 8 --- Reminders

## Objectives

-   Gmail SMTP
-   process_reminders management command
-   Scheduled job configuration
-   Reminder history (if implemented)

### Deliverable

Reminder emails are sent automatically.

------------------------------------------------------------------------

# 12. Milestone 9 --- UI Polish

## Objectives

-   Responsive layouts
-   Empty states
-   Error messages
-   Loading indicators
-   Final visual consistency

### Deliverable

Application is ready for daily use.

------------------------------------------------------------------------

# 13. Milestone 10 --- Deployment

## Objectives

-   Deploy to Render or Railway
-   Configure environment variables
-   Configure scheduled job
-   Final production testing

### Deliverable

Live application.

------------------------------------------------------------------------

# 14. Testing Checklist

Test after each milestone.

-   Database migrations
-   CSV validation
-   Import workflow
-   Dashboard data
-   Progress updates
-   Exam display
-   Reminder emails
-   Mobile layout

------------------------------------------------------------------------

# 15. Out of Scope (Version 1)

Do not implement:

-   User accounts
-   Multiple users
-   Dark mode
-   Analytics dashboard
-   Calendar view
-   PDF parsing
-   PostgreSQL
-   Mobile app

------------------------------------------------------------------------

# 16. Success Criteria

Version 1 is complete when a user can:

1.  Import coaching data from CSV.
2.  View today's classes and exams.
3.  Track lecture-topic progress.
4.  Continue unfinished study.
5.  Receive reminder emails.
6.  Use the application on desktop and mobile.
7.  Deploy the application with minimal configuration.

------------------------------------------------------------------------

# 17. Estimated Build Order

  Phase                 Priority
  --------------------- ----------
  Project Setup         Highest
  Database Models       Highest
  CSV Import            Highest
  Dashboard             High
  Subjects              High
  Lectures & Progress   High
  Exams                 Medium
  Reminders             Medium
  UI Polish             Medium
  Deployment            Final

The application should remain functional after each completed milestone.
