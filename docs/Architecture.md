# Architecture

A condensed, current-state view of how Admission Helper is built.
`PROJECT_PROGRESS.md` is the authoritative, milestone-by-milestone
history of *why* each piece exists; this document is the "what it
looks like today" summary for a new developer. `03_System_Architecture.md`
is the original design-phase document (pre-implementation) - kept for
historical reference, not updated to match the current codebase.

---

## Stack

- **Backend:** Django 6.0
- **Frontend:** Django Templates + HTMX + Tailwind CSS v4 (no JS
  framework, no SPA build step - HTMX handles partial-page updates,
  vanilla JS only where HTMX has no equivalent)
- **Database:** SQLite in development, PostgreSQL in production (via
  `DATABASE_URL`, using `dj-database-url`)
- **Email:** Django's console backend in development, Gmail SMTP in
  production
- **Static files:** WhiteNoise
- **Deployment target:** Render or Railway

## Django Apps

| App | Responsibility |
| --- | --- |
| `core` | Cross-cutting concerns: registration, login extras, health check, profile page, the shared design-system template tags (`ui_tags.py`), shared test fixtures |
| `dashboard` | The "today's work" landing page |
| `subjects` | `Subject`/`Chapter` models and their canonical detail pages |
| `lectures` | `LectureTopic` model and the Lecture Detail page |
| `progress` | `Progress`/`RevisionSchedule`/`RevisionHistory` models; all analytics, dashboard-stats, revision-workflow, advanced-insights, and multi-dimensional Progress Service calculations; the Progress Overview, Analytics, and Revision pages |
| `routines` | `Routine`/`Lecture`/`Exam`/`DatasetVersion`/`ImportLog` models; the CSV importer; the Routine/Exam Timelines; the Routine Archive; dataset management |
| `reminders` | The reminder engine, email rendering/delivery, notification preferences, Reminder Administration |

## The Service Layer Rule

Views stay thin. Every calculation - completion percentages, revision
due dates, exam readiness, reminder trigger conditions, progress
aggregation - lives in a `services/` module under the owning app, and
is called by name from the view. No template ever computes a number a
service already could; no view ever duplicates a calculation another
view already made. This is the single rule most consistently enforced
across every milestone in `PROJECT_PROGRESS.md`.

Two services are worth knowing by name as the "single source of truth"
for their domain:

- **`progress/services/progress_service.py`** - the multi-dimensional
  Progress Service (Milestone 15.2). Every study topic contributes
  four independent, equally-weighted units (Class/Notes/Revision/
  Practice, 25% each), aggregated hierarchically (Topic -> Chapter ->
  Lecture -> Subject -> Exam -> overall) and always in bulk for list
  pages. Deliberately independent of `analytics.py`/`dashboard.py`/
  `revision.py` - none of their existing percentages changed, and
  `revision.is_lecture_completed()`'s stricter "all four required"
  definition (which decides whether a revision schedule gets created)
  is untouched by this newer, presentation-facing calculation.
- **`reminders/services/engine.py`** - the Reminder Engine (Milestone
  15). Asks "what reminders should be sent right now?" via a
  `GENERATORS` registry (one generator per reminder type - Daily
  Agenda, Weekly Overview, Revision Due, Weekly/Monthly Exam, Weekly
  Progress), filters against `ReminderLog` for idempotency, and
  delivers through a strictly separate rendering/delivery layer
  (`reminders/emails/`) that never touches the database and knows
  nothing about SMTP details beyond Django's own `EMAIL_BACKEND`.

## The Design System Rule

Every visual element - cards, badges, buttons, form fields, the
progress meter, the navigation - has exactly one reusable
implementation: either a template in `templates/components/*.html` or
a class-string tag in `core/templatetags/ui_tags.py`. A page never
hand-writes its own card border or badge color. This is what let
Milestone 13/15.1/15.2's design-system passes change the whole app by
editing a handful of files instead of sweeping every page.

## Canonical Pages

Every academic entity has exactly one canonical URL that every
cross-reference in the app links to - `/subjects/<pk>/`,
`/chapters/<pk>/`, `/lecture/<code>/`, `/exam/<pk>/`,
`/routine/week/<n>/`. No entity has two competing detail pages.

## Timeline & Reminder Idempotency

The Routine/Exam Timelines use event-based windowing (a fixed *count*
of events on each side of an anchor, never a fixed number of calendar
days) rather than pagination - see `routines/services/timeline.py`.
The Reminder Engine's duplicate-protection is a real database
constraint (`ReminderLog`'s unique `(user, reminder_type,
reference_key)`), not an in-memory check, so it survives a process
restart.

## Where To Look Next

- `docs/DeveloperGuide.md` - local setup, running tests, adding a new
  feature the way this codebase expects it.
- `docs/Deployment.md` - taking this to production.
- `PROJECT_PROGRESS.md` - the full history, one section per milestone,
  including every architectural decision and why it was made.
