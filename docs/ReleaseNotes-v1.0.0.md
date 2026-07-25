# Release Notes — v1.0.0

**Release date:** 2026-07-26

Admission Helper's first production release. A personal study-tracking
and reminder application for Bangladesh university admission
preparation, built end-to-end across 20+ milestones documented in full
in `PROJECT_PROGRESS.md`. This is the summary version.

## Highlights

### Study Tracking & Progress

Import a coaching routine from CSV once, then track every lecture
topic across four independent activities - **Class, Notes, Revision,
Practice** - each worth an equal 25%, shown everywhere with fixed,
permanent colors (blue/green/amber/purple). Progress aggregates
automatically from a single Topic all the way up through its Chapter,
Lecture, Subject, and any Exam that covers it, to one Dashboard-wide
number - computed by a single Progress Service, always in bulk, never
recalculated per page.

### Timeline & Navigation

The Routine and Exam Timelines center on "now" and scroll outward -
no calendar pages, no pagination - sharing one "Routine Week"
numbering scheme. Every Subject, Chapter, Lecture, and Exam has exactly
one canonical page that every reference in the app links to.

### Revision System

Completing a lecture (all four activities, every topic) automatically
schedules three revision stages (1/3/7 days out). A filterable queue
(Due Today / Overdue / Upcoming / Completed) and a system-wide "Exam
Ready" status track the rest.

### Analytics

Five tabs - Insights (a "study advisor": priority chapters, neglected
topics, study streaks, exam-readiness scoring), Subjects, Chapters,
Lectures, and Exam Readiness - each sortable and filterable, none
duplicating another's calculation.

### Reminder System

Six reminder types (Daily Study Agenda, Weekly Overview, Revision Due,
Weekly/Monthly Exam Reminders, Weekly Progress), all generated from
existing study data by a single Reminder Engine, delivered as HTML
email with an automatically-generated plain-text fallback, and
protected against duplicate sends by a real database constraint - not
an in-memory check, so it survives a restart. Every user controls what
they receive and when. Staff get a dedicated Reminder Administration
page to verify email configuration and test-send anything before
relying on it in production.

### Theme Support

A Light/Dark/System appearance selector lives in the header on every
page, persisted client-side (no account field, no server round-trip),
with dark mode support across every shared component in the app.

### Design System

Every card, badge, button, form field, and the progress meter itself
is one reusable implementation, not a page-specific style - this is
what let the interface stay consistent while every one of these
features was added incrementally.

## What's Not Included (By Design)

See the README's "Version 1 Scope" section: this is a single/few-user
tool, not a multi-tenant product. No PDF text parsing, no calendar
view, no mobile app. See `KNOWN_ISSUES.md` for what's deliberately
deferred rather than out of scope entirely.

## Upgrading / Getting Started

See the README for local setup, `docs/Deployment.md` for a production
deployment, and `docs/UserGuide.md` for how to actually use the
application once it's running.

## Thanks

Built solo, milestone by milestone, with `PROJECT_PROGRESS.md` as the
running record of every decision, bug, and tradeoff along the way.
