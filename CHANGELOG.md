# Changelog

All notable changes to this project are documented in this file. The
format loosely follows [Keep a Changelog](https://keepachangelog.com/),
and versioning follows [Semantic Versioning](https://semver.org/) - see
`docs/GitWorkflow.md`/the README's Versioning section for the policy.

This is the first release; every milestone from project inception
through Milestone 15.2 is summarized here as v1.0.0. See
`PROJECT_PROGRESS.md` for the complete, milestone-by-milestone history
behind every line below.

---

## [1.0.0] - 2026-07-26

### Added

- CSV import pipeline for coaching routines (subjects, chapters,
  lectures, lecture topics, exams), with `--preview`/`--dry-run`
  modes, checksums, versioning, and rollback.
- Student dashboard, subject/chapter/lecture progress tracking, and a
  multi-dimensional Progress System (Class/Notes/Revision/Practice,
  each worth an independent 25%), aggregated hierarchically from Topic
  through Chapter, Lecture, Subject, Exam, up to the Dashboard/
  Analytics.
- Weekly/monthly exam tracking with per-exam readiness scoring.
- A full revision workflow: automatic three-stage revision scheduling
  on lecture completion, a filterable revision queue, and per-lecture
  "Exam Ready" status.
- Advanced analytics ("Study Advisor"): priority/neglected chapters,
  completion trends, study streaks, exam-readiness blending, and a
  dedicated Insights page.
- User authentication (registration, login, logout, password
  reset/change) with full per-user data isolation.
- Event-based Routine/Exam Timelines (centered on "now," not paginated
  by calendar page) with a canonical "Routine Week" numbering scheme
  shared by both.
- Canonical detail pages for every academic entity (Subject, Chapter,
  Lecture, Exam, Routine Week) with cross-navigation between them.
- A CSV dataset management system (version history, comparison,
  duplicate detection, rollback), restricted to staff users.
- A Routine Archive: automatic discovery of routine PDFs from
  `media/routines/` by filename convention, with a browsable viewer
  and download - no upload interface or database table required.
- A full Reminder & Notification System: Daily Study Agenda, Weekly
  Overview, Revision Due, Weekly/Monthly Exam Reminders, and Weekly
  Progress - all generated from existing study data via a single
  Reminder Engine, delivered as HTML email with an auto-generated
  plain-text fallback, and protected against duplicate sends by a
  durable database constraint.
- Per-user Notification Preferences (per-type on/off, configurable
  delivery time, searchable IANA timezone dropdown).
- A staff-only Reminder Administration page: email configuration
  diagnostics (with credentials never displayed), an SMTP connection
  test, a standalone test-email tool, a Reminder Test Center
  (preview/send any reminder to any user on demand), and a Reminder
  Activity Log.
- A minimal account Profile page.
- A shared design system: cards (three variants), badges, buttons,
  forms, timelines, and a responsive multi-dimensional progress meter
  component, all with light/dark mode support.
- A global Light/Dark/System theme selector, persisted client-side.
- Production-readiness: environment-driven settings, WhiteNoise static
  file serving, PostgreSQL support via `DATABASE_URL`, a `Procfile`,
  and a GitHub Actions CI pipeline.

### Changed

- Replaced the original horizontally-scrolling/wrapping navigation
  with a compact header (main nav row, staff-only dropdown, user-menu
  dropdown, mobile hamburger).
- Replaced the binary ("all four activities or nothing") progress
  display with the multi-dimensional Progress System everywhere a
  progress bar represents real per-topic study data.
- Consolidated the Routine and Exam Timelines' week/day rendering into
  one shared component (previously two near-identical templates).
- Standardized card padding/radius/borders, status badge colors, table
  hover states, and analytics navigation (segmented tabs) across the
  entire application.
- Tightened empty-state spacing and added a small non-illustrative
  glyph in place of a bare "no data" message.
- Replaced the Datasets nav item's default visibility for staff with a
  dedicated Staff Menu; non-staff continue to see Routine Resources in
  its place.

### Fixed

- A revision-queue "Upcoming" badge silently rendered empty in
  production due to Django's `add` template filter's silent failure
  mode on incompatible types (string + date) - found during a
  design-system audit, not reported by a user.
- A Django template `default` filter footgun in the new Progress
  Component: `default` (unlike `default_if_none`) replaces *any*
  falsy value, so an explicit `tooltip=False` was silently overridden
  back to "on" - caught by the component's own test suite before
  release.
- Routine Week numbering was sparse (only weeks containing a lecture
  were numbered), causing the Exam Timeline to fall back to a
  different, ISO-based numbering scheme when an exam landed in an
  otherwise lecture-free week - fixed by making the week map span
  every week in range, giving both timelines exactly one shared
  numbering implementation.
- A stale/never-rebuilt Tailwind CSS bundle silently shipped an
  unstyled application for several milestones before being caught -
  now guarded by an automated test that checks the compiled CSS
  actually contains the utility classes the templates require.
- WhiteNoise's manifest-based static storage broke every
  `{% static %}` render in local development/tests (no `collectstatic`
  manifest exists there) - fixed by using manifest storage only when
  `DEBUG=False`.

### Internal

- Established a strict service-layer convention: no view or template
  computes a number a `services/` module could instead - enforced
  project-wide by Milestone 13's design-system audit and every
  milestone since.
- Every list-page calculation (analytics tables, timeline cards,
  reminder generation, progress meters) has a bulk variant costing
  exactly one query regardless of row count, verified directly via
  `CaptureQueriesContext` in tests, not just asserted in a comment.
- Query-count budgets tracked and documented per page since Milestone
  5, with every intentional increase explained rather than left
  silent.
- 529 automated tests as of this release, covering the CSV importer,
  every analytics/progress/revision calculation, the reminder system
  (generation, rendering, delivery, idempotency), navigation, theme
  persistence, accessibility markup, and the compiled CSS bundle
  itself.
