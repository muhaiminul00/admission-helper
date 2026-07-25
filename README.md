# Admission Helper

**Version 1.0.0**

A personal web application for managing Bangladesh university admission
preparation - coaching routines, lecture progress, exams, revision
scheduling, analytics, and reminders, built for a single user (or a
small handful) with a simple, maintainable architecture rather than a
multi-tenant SaaS product.

Full documentation lives in [`docs/`](docs/) and
[`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md) (the complete,
milestone-by-milestone build history). This README is the "clone it
and run it" quick start.

------------------------------------------------------------------------

# Features

-   Import coaching routines from CSV, with versioning/rollback
-   Multi-dimensional lecture-topic progress (Class/Notes/Revision/
    Practice, each independently tracked)
-   Dashboard with today's work and study-advisor insights
-   Subject/chapter/lecture/exam canonical pages with cross-navigation
-   Event-based Routine and Exam Timelines (centered on "now")
-   Automatic three-stage revision scheduling and an "Exam Ready" status
-   Weekly/monthly exam tracking with readiness scoring
-   Full analytics suite (subjects, chapters, lectures, exam readiness,
    study-advisor insights)
-   A Routine Archive (automatic PDF discovery, no upload interface)
-   A full reminder & notification system with a staff-only
    administration/testing page
-   Light/Dark/System appearance, persisted client-side
-   Responsive interface, no horizontal scrolling

See [`docs/UserGuide.md`](docs/UserGuide.md) for a full walkthrough of
every feature from a student's point of view.

------------------------------------------------------------------------

# Screenshots

*(to be added post-release)*

------------------------------------------------------------------------

# Installation

## Prerequisites

-   Python 3.12+
-   Node.js (for building Tailwind CSS)
-   Git

## Steps

```bash
git clone <repository>
cd admission-helper

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

cd theme/static_src
npm install
npm run build
cd ../..

python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`, then register an account at
`/accounts/register/` (or `python manage.py createsuperuser` for
staff/admin access).

------------------------------------------------------------------------

# Configuration

Copy `.env.example` to `.env` for local development, or set these as
real environment variables on your hosting platform. Every value has a
safe local default except in production, where `SECRET_KEY` must be
set explicitly.

  Variable                Required          Default                 Purpose
  ------------------------ ----------------- ----------------------- --------------------------------------------
  `SECRET_KEY`             Production only   dev-only insecure key   Django's cryptographic signing key
  `DEBUG`                  No                `True`                  `False` in production
  `ALLOWED_HOSTS`          Production only   `localhost,127.0.0.1`   Comma-separated list of allowed hostnames
  `CSRF_TRUSTED_ORIGINS`   If behind HTTPS   (empty)                 Comma-separated list, e.g. `https://your-app.onrender.com`
  `DATABASE_URL`           No                local SQLite            PostgreSQL connection string in production
  `EMAIL_HOST_USER`        No                (empty)                 Gmail address for SMTP delivery
  `EMAIL_HOST_PASSWORD`    No                (empty)                 Gmail app password
  `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_USE_TLS`   No   Gmail's own    SMTP overrides, only used once the two above are set
  `TIME_ZONE`              No                `Asia/Dhaka`            IANA timezone every date/time calculation uses

With `DEBUG=True` (or no `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`),
email is printed to the console instead of actually sent - no SMTP
credentials are required for local development. Session/CSRF cookie
security (Secure flag, HSTS) turns on automatically whenever
`DEBUG=False` - there's no separate variable to toggle it. See
`.env.example` for the complete, commented list.

------------------------------------------------------------------------

# Running Locally

```bash
python manage.py runserver
```

Import the sample dataset (routine.csv, lecture_topics.csv, exams.csv,
subjects.csv, chapters.csv at the project root):

```bash
python manage.py import_csv --preview   # validate first, writes nothing
python manage.py import_csv             # real import
```

See `06_CSV_Import_Specification.md` for the exact file formats and
import order (subjects → chapters → routine → lecture topics → exams).

------------------------------------------------------------------------

# Running Tests

```bash
python manage.py test                                  # full suite
python manage.py test progress.tests_progress_service   # one module
python manage.py check                                  # system checks
python manage.py makemigrations --check --dry-run        # no missing migrations
```

529 tests as of v1.0.0, covering the CSV importer, every analytics/
progress/revision calculation, the reminder system end to end, UI
consistency, accessibility markup, and the compiled CSS bundle itself.

------------------------------------------------------------------------

# Tailwind Build

Tailwind v4, CSS-first config (`theme/static_src/src/styles.css`, no
`tailwind.config.js`). Compiled output is git-ignored - it must be
rebuilt, never committed:

```bash
cd theme/static_src
npm run build     # one-off production build
npm run dev       # watch mode while editing templates
```

Run `npm run build` after adding **any** new Tailwind class to a
template. `core.tests_ui.CompiledCSSTests` catches a stale build, but
it's faster to just always rebuild after a template change.

------------------------------------------------------------------------

# Reminder Scheduler

Six reminder types (Daily Study Agenda, Weekly Overview, Revision Due,
Weekly/Monthly Exam Reminders, Weekly Progress), all generated from
existing study data by a single Reminder Engine - see
`docs/Architecture.md`. Each has its own management command:

```bash
python manage.py send_daily_agenda        # run at least hourly
python manage.py send_weekly_overview     # once daily
python manage.py send_exam_reminders      # once daily
python manage.py send_revision_reminders  # once daily
python manage.py send_weekly_progress     # once daily
```

Every command accepts `--dry-run` and is safe to run more than once -
a reminder is never sent twice (tracked in the `ReminderLog` table,
not in memory, so this survives restarts). Scheduler-agnostic: cron,
Render/Railway Scheduled Jobs, GitHub Actions, or Celery beat all work
unchanged. Nothing runs a schedule for you locally or by default - see
`docs/Deployment.md`, Section 6, for wiring one up in production.

Each user controls what they receive (and when) at
`/reminders/preferences/`. Staff get `/reminders/admin/` to verify
email configuration and test-send anything before relying on it.

------------------------------------------------------------------------

# Deployment Overview

Targets Render or Railway, building from the repository's `Procfile`:

```text
release: python manage.py migrate --noinput
web: gunicorn admission_helper.wsgi --log-file -
```

In short: attach a Postgres add-on (`DATABASE_URL`), set the
production environment variables above, point the build command at
`pip install` + `npm run build` + `collectstatic`, attach a persistent
disk for `media/` if you want the Routine Archive to survive
redeploys, and point the health check at `/health/`.

**Full step-by-step instructions:
[`docs/Deployment.md`](docs/Deployment.md).**

------------------------------------------------------------------------

# Project Architecture

Django + HTMX + Tailwind, no JS framework. Views stay thin; every
calculation lives in a `services/` module owned by the relevant app.
Every visual element has exactly one reusable implementation
(`templates/components/` + `core/templatetags/ui_tags.py`).

```text
core/           cross-cutting: auth extras, health check, profile, design-system tags
dashboard/      the "today's work" landing page
subjects/       Subject/Chapter models + canonical pages
lectures/       LectureTopic model + Lecture Detail
progress/       Progress/RevisionSchedule models, analytics, Progress Service, revision workflow
routines/       Routine/Lecture/Exam/DatasetVersion models, CSV importer, Timelines, Routine Archive
reminders/      the Reminder Engine, email rendering/delivery, notification preferences, admin tools

templates/      Django templates, organized to mirror the apps above
static/         non-compiled static assets
theme/          django-tailwind app (Tailwind v4 source + compiled output)
data/           archived CSV dataset snapshots
docs/           architecture/deployment/developer/user/git-workflow documentation
```

**Full architecture writeup, including the service-layer and
design-system rules every contribution follows:
[`docs/Architecture.md`](docs/Architecture.md).** Contributing?
Start with **[`docs/DeveloperGuide.md`](docs/DeveloperGuide.md)** and
**[`docs/GitWorkflow.md`](docs/GitWorkflow.md)**.

------------------------------------------------------------------------

# Documentation

-   [`docs/Architecture.md`](docs/Architecture.md) - how the system is put together
-   [`docs/Deployment.md`](docs/Deployment.md) - production deployment, step by step
-   [`docs/DeveloperGuide.md`](docs/DeveloperGuide.md) - local setup, conventions
-   [`docs/UserGuide.md`](docs/UserGuide.md) - how to use every feature
-   [`docs/GitWorkflow.md`](docs/GitWorkflow.md) - branching/release process
-   [`docs/ReleaseNotes-v1.0.0.md`](docs/ReleaseNotes-v1.0.0.md) - this release, summarized
-   [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md) - the complete milestone-by-milestone history
-   [`CHANGELOG.md`](CHANGELOG.md) - what changed, per version
-   [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) - deliberately deferred polish and open items
-   [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) - the exact release steps, every time

Original design-phase documents (pre-implementation, kept for
historical reference - not updated to match the current codebase):
`01_Product_Requirements_Document_PRD_v1.1.md`,
`02.1_Database_Model_Contract_v1.0.md`, `02_Database_Design.md`
(superseded by `02_Database_Design_v1.1.md`),
`03_System_Architecture.md`, `04_Navigation_Screen_Flow.md`,
`05_UI_UX_Specification.md`, `06_CSV_Import_Specification.md`,
`07_Development_Roadmap.md`, `08_Coding_Standards.md`, and
`Varsity_Admission_Tracker_Architecture_v1.md` (the project's earliest
draft, under its original working title).

------------------------------------------------------------------------

# Versioning

[Semantic Versioning](https://semver.org/) from v1.0.0 onward:

-   **MAJOR** (`v2.0.0`) - breaking changes (data model changes
    requiring migration steps beyond `manage.py migrate`, removed
    features, incompatible config changes).
-   **MINOR** (`v1.1.0`) - new features, backward-compatible.
-   **PATCH** (`v1.0.1`) - bug fixes only, no new features.

Every release is tagged on `main` and documented in `CHANGELOG.md` -
see `docs/GitWorkflow.md` for the branching model this follows and
`RELEASE_CHECKLIST.md` for the exact release steps.

------------------------------------------------------------------------

# Version 1 Scope

Included:

-   Single user (or a small handful, with full per-user data isolation)
-   SQLite (dev) / PostgreSQL (production)
-   CSV import
-   Multi-dimensional progress tracking
-   Email reminders

Not included (see `KNOWN_ISSUES.md` for deferred polish vs. these
explicit non-goals):

-   Multi-tenant/public SaaS use
-   PDF text parsing
-   A calendar view
-   A native mobile app

------------------------------------------------------------------------

# License

[MIT](LICENSE) - see the `LICENSE` file.
