# System Architecture

**Project:** Varsity Admission Tracker\
**Document:** 03_System_Architecture.md\
**Version:** 1.0\
**Status:** Locked for Version 1

------------------------------------------------------------------------

# 1. Architecture Philosophy

The application is intentionally designed as a **simple Django
monolith**.

Goals:

-   Easy to understand
-   Easy to maintain
-   Minimal infrastructure
-   Suitable for personal use
-   Easy future migration if needed

The project avoids unnecessary complexity.

Not used in Version 1:

-   Microservices
-   Redis
-   Celery
-   Message queues
-   External databases

------------------------------------------------------------------------

# 2. Technology Stack

  Component     Technology
  ------------- ----------------------------------------------------------
  Backend       Django
  Frontend      Django Templates + HTMX + Tailwind CSS
  Database      SQLite
  Data Import   CSV
  Email         Gmail SMTP
  Scheduler     Render/Railway Scheduled Job + Django Management Command
  Hosting       Render Free or Railway Free

------------------------------------------------------------------------

# 3. High-Level Architecture

``` text
Browser
    │
    ▼
Django Application
    │
    ├── Dashboard
    ├── Subjects
    ├── Lectures
    ├── Progress
    ├── Routine Import
    └── Reminders
    │
    ▼
SQLite Database
```

------------------------------------------------------------------------

# 4. Application Modules

The Django project is divided into small feature-based apps.

``` text
core/
dashboard/
subjects/
lectures/
progress/
routines/
reminders/
```

## core

Shared utilities, settings and common code.

## dashboard

Home page and overview.

## subjects

Subjects and chapter management.

## lectures

Lectures and lecture topics.

## progress

Study progress tracking.

## routines

CSV import and routine management.

## reminders

Email reminders and management commands.

This structure is **locked for Version 1**.

------------------------------------------------------------------------

# 5. Request Flow

A normal page request follows this flow:

``` text
Browser
    │
    ▼
URL
    │
    ▼
Django View
    │
    ▼
SQLite
    │
    ▼
Template
    │
    ▼
Browser
```

------------------------------------------------------------------------

# 6. CSV Import Flow

The CSV files are the source of coaching information.

``` text
CSV Files
    │
    ▼
Validation
    │
    ▼
Create Routine
    │
    ▼
Create Lectures
    │
    ▼
Create Lecture Topics
    │
    ▼
Create Exams
    │
    ▼
Import Complete
```

If validation fails, nothing is imported.

------------------------------------------------------------------------

# 7. Progress Flow

Progress is updated from the Lecture page.

``` text
User checks a task
    │
    ▼
Progress table updated
    │
    ▼
Chapter progress recalculated
    │
    ▼
Dashboard refreshed
```

Only the smallest study unit (LectureTopic) stores progress.

------------------------------------------------------------------------

# 8. Reminder Flow

The application does not run a background worker.

Instead:

``` text
Render/Railway Scheduler
        │
        ▼
python manage.py process_reminders
        │
        ▼
SQLite
        │
        ▼
Find today's reminders
        │
        ▼
Send Email (Gmail SMTP)
```

A single management command decides what reminders should be sent.

------------------------------------------------------------------------

# 9. Project Structure

``` text
varsity_tracker/
│
├── core/
├── dashboard/
├── subjects/
├── lectures/
├── progress/
├── routines/
├── reminders/
│
├── templates/
├── static/
├── data/
│   ├── routine.csv
│   ├── lecture_topics.csv
│   ├── exams.csv
│   └── db.sqlite3
│
├── manage.py
└── requirements.txt
```

------------------------------------------------------------------------

# 10. Deployment

``` text
User
   │
   ▼
Render / Railway
   │
   ▼
Django
   │
   ▼
SQLite
   │
   ▼
Gmail SMTP
```

The application runs as a single web service.

------------------------------------------------------------------------

# 11. Design Decisions

## Why Django?

-   Mature framework
-   Batteries included
-   Excellent ORM
-   Easy maintenance

## Why SQLite?

-   Zero configuration
-   Reliable
-   Perfect for a personal project
-   Easy migration later

## Why CSV?

-   Portable
-   Easy to edit
-   Easy to back up
-   Independent of coaching PDF formats

## Why Scheduled Jobs?

-   No Redis
-   No Celery
-   One simple management command

## Why LectureTopic?

It is the smallest meaningful unit of study and progress tracking.

------------------------------------------------------------------------

# 12. Future Growth

If the project grows, the architecture supports:

-   PostgreSQL instead of SQLite
-   Cloud object storage
-   User authentication
-   Multiple users
-   Mobile application

These upgrades do not require redesigning the application structure.
