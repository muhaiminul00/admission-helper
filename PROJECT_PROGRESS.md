# Admission Helper

## Current Milestone

Milestone 17 — Production Deployment (Render)

Status:
🟡 Code-side work completed; live deployment awaiting manual Render
dashboard steps (Blueprint apply, secret entry) - see this milestone's
entry below and the deployment report delivered alongside it.

Completion Date:
Code-side: 2026-07-26. Live deployment: pending.

---

## Completed Milestones

- [x] Milestone 1 — Project Setup
- [x] Milestone 2 — Database Models
- [x] Milestone 3.0 — Model Contract Revision (Chapter Paper Support)
- [x] Milestone 3.1 — Lecture Time Fields Made Optional
- [x] Milestone 3 — CSV Import System
- [x] Milestone 4 — Student Dashboard & Study Workflow
- [x] Milestone 4.1 — Resolve Remaining Importer Known Issues
- [x] Milestone 5 — Study Planner & Analytics
- [x] Milestone 6 — Testing, Hardening & UX Polish
- [x] Milestone 7 — Authentication & User Management
- [x] Milestone 8 — Advanced Analytics
- [x] Milestone 9 — Revision System
- [x] Milestone 10 — Import & Dataset Management
- [x] Milestone 10.5 — Timeline-Based Navigation
- [x] Milestone 11 — User Experience & UI Polish
- [x] Milestone 11.1 — Stabilization & Verification
- [x] Milestone 11.2 — Frontend Build Pipeline Repair
- [x] Milestone 12 — Navigation & Study Workspace
- [x] Milestone 13 — Interface Refinement & Design Consistency
- [x] Milestone 14 — Production Readiness, Routine Archive & Release Preparation
- [x] Milestone 15 — Reminder & Notification System
- [x] Milestone 15.1 — Reminder Administration, Theme System & UX Polish
- [x] Milestone 15.2 — Design System Refinement & Multi-Dimensional Progress
- [x] Milestone 15.3 — Version 1.0 Release Preparation
- [x] Milestone 16 — GitHub & Production Repository Setup
- [~] Milestone 17 — Production Deployment (Render) - code-side complete, live deployment pending manual steps

---

## Current Architecture

### Technology Stack

Backend

- Django

Frontend

- Django Templates
- HTMX
- Tailwind CSS

Database

- SQLite

Scheduler

- Render / Railway Scheduled Jobs

Email

- Gmail SMTP

Python Virtual Environment

- .admission_venv

---

## Current Project Structure

```text
Admission Helper/
├── .admission_venv/
├── .env.example
├── .gitignore
├── .github/workflows/ci.yml  # Milestone 14, Phase 6 - checkout, Python, Node, Tailwind
│                              # build, manage.py check, makemigrations --check, test
├── Procfile                  # Milestone 14, Phase 5 - `release`/`web` process types
│                              # (gunicorn), read by Render/Railway
├── LICENSE                   # Milestone 15.3, Part 1/7 - MIT
├── CHANGELOG.md              # Milestone 15.3, Part 5 - Keep a Changelog format,
│                              # first entry is v1.0.0 (this release)
├── KNOWN_ISSUES.md           # Milestone 15.3, Part 6 - deliberately deferred polish/
│                              # open items, meant to become individual GitHub issues
├── RELEASE_CHECKLIST.md      # Milestone 15.3, Part 10 - the exact steps for every
│                              # tagged release, not just v1.0.0
├── PROJECT_PROGRESS.md
├── README.md                 # Milestone 15.3, Part 4 - rewritten to the required
│                              # section order (Overview/Features/Installation/
│                              # Configuration/Running Locally/Tests/Tailwind/
│                              # Reminder Scheduler/Deployment/Architecture/License)
├── requirements.txt
├── manage.py
├── db.sqlite3 (created by migrate, git-ignored)
│
├── docs/                     # Milestone 15.3, Part 3 - deep-dive documentation the
│   │                          # README links out to rather than duplicating
│   ├── Architecture.md        # current-state system architecture summary
│   ├── Deployment.md          # full production deployment guide (Part 8)
│   ├── DeveloperGuide.md       # local setup, conventions, "how to add X"
│   ├── UserGuide.md            # end-user walkthrough of every feature
│   ├── GitWorkflow.md          # branching strategy, main/develop/feature/
│   │                            # bugfix/hotfix/release, the "no direct commits
│   │                            # to main after v1.0.0" rule (Part 2/14)
│   └── ReleaseNotes-v1.0.0.md  # Part 13 - this release, summarized for users
│
├── admission_helper/        # Django project package
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/                    # management/commands/validate_datasets.py
│   │                        # + RegisterView, RegistrationForm ("/accounts/register/", Milestone 7)
│   ├── forms.py, views.py, tests.py, tests_ui.py (Milestone 11)
│   ├── templatetags/ui_tags.py   # Milestone 11 - button_classes()/field_classes()/
│   │                              # class_if_positive()/pct_color()/times() - shared class-
│   │                              # string helpers for markup the includable components
│   │                              # in templates/components/ don't cover; Milestone 12 added
│   │                              # workspace_toolbar_classes(); Milestone 13 added
│   │                              # card_classes() (one canonical card wrapper, "normal"/
│   │                              # "dense" padding) and status_badge_classes() (one
│   │                              # canonical 5-tier status color mapping for template-
│   │                              # authored badges)
│   └── test_utils.py         # build_sample_dataset()/create_user() - shared test fixtures
├── dashboard/                # DashboardView ("/") + DashboardWidgetsView (HTMX widget refresh)
│   │                        # both LoginRequiredMixin-protected (Milestone 7)
│   ├── views.py, urls.py, tests.py
├── subjects/                 # models: Subject, Chapter (with paper); Milestone 12 gave this
│   │                          # app its first views: SubjectDetailView ("/subjects/<pk>/"),
│   │                          # ChapterDetailView ("/chapters/<pk>/") - the canonical pages
│   │                          # for these two entities, reusing analytics.py's existing
│   │                          # bulk functions rather than recalculating completion
│   ├── models.py, views.py, urls.py, tests.py (Milestone 12)
│   ├── admin.py
│   └── migrations/0001_initial.py, 0002_alter_chapter_options_and_more.py
├── lectures/                  # models: LectureTopic (chapter nullable); LectureDetailView
│   │                          # (LoginRequiredMixin; progress scoped to request.user;
│   │                          # gained Subject/Chapter/Previous-Next-Lecture/Upcoming-Exam
│   │                          # cross-navigation links, Milestone 12)
│   ├── models.py, views.py, urls.py, tests.py
│   ├── admin.py
│   └── migrations/0001_initial.py, 0002_alter_lecturetopic_chapter.py
├── progress/                  # models: Progress (per-user); RevisionSchedule, RevisionHistory
│   │                          # (Milestone 9); ProgressOverviewView + ProgressToggleView (HTMX)
│   │                          # + 5 Analytics*View pages + RevisionQueueView/RevisionDetailView/
│   │                          # RevisionCompleteView ("/revision/...") - all
│   │                          # LoginRequiredMixin-protected
│   ├── models.py, views.py, urls.py, analytics_urls.py, revision_urls.py, tests.py,
│   │              tests_revision.py (Milestone 9), tests_progress_service.py (Milestone 15.2)
│   ├── services/              # analytics.py/dashboard.py (basic metrics) + advanced_analytics.py
│   │                          # (Milestone 8 - "study advisor" insights) + revision.py
│   │                          # (Milestone 9 - schedule creation, due-date calculation,
│   │                          # exam-ready determination, queue fetching, completion,
│   │                          # revision dashboard/analytics stats; gained
│   │                          # get_pending_revision_counts() bulk helper, Milestone 10.5) -
│   │                          # every function takes a `user` arg
│   │                          # + progress_service.py (Milestone 15.2, Parts 2-4 - the
│   │                          # multi-dimensional Progress Service: independent 25%-each
│   │                          # Class/Notes/Revision/Practice credit, hierarchical
│   │                          # Topic->Chapter->Lecture->Subject->Exam->overall
│   │                          # aggregation, and get_bulk_*() variants for every list
│   │                          # page - all one query each, never one query per row.
│   │                          # Deliberately independent of analytics.py/dashboard.py/
│   │                          # revision.py: none of their return values changed, and
│   │                          # is_lecture_completed()'s all-four-required definition
│   │                          # for revision-scheduling purposes is untouched)
│   ├── admin.py
│   └── migrations/0001_initial.py,
│                  0002_progress_user_alter_progress_lecture_topic_and_more.py,
│                  0003_revisionschedule_revisionhistory_and_more.py
├── routines/                  # models: Routine, Lecture (undated-capable), Exam (+ exam_code,
│   │                          # online_start/end), DatasetVersion, ImportLog (Milestone 10);
│   │                          # CSV import system; RoutineTimelineView ("/routine/") +
│   │                          # ExamTimelineView ("/routine/exams/", Milestone 10.5 - replaces
│   │                          # the old page-based RoutineListView/exam-list-via-filter) +
│   │                          # ExamDetailView ("/exam/<id>/", gained Covered Subjects/
│   │                          # Chapters/Readiness cross-navigation, Milestone 12) +
│   │                          # DatasetHistoryView/DatasetCompareView ("/datasets/...",
│   │                          # Milestone 10 - staff-only since Milestone 12) +
│   │                          # RoutineWeekView ("/routine/week/<n>/") + RoutineResourcesView
│   │                          # ("/routine/resources/", Milestone 12's placeholder replaced by
│   │                          # Milestone 14's real, filesystem-backed Routine Archive) +
│   │                          # RoutineArchiveFileView ("/routine/resources/file/<filename>/",
│   │                          # Milestone 14 - serves one archived PDF, inline or as download)
│   ├── models.py, views.py, urls.py, dataset_urls.py (Milestone 10), tests.py,
│   │              tests_dataset.py (Milestone 10), tests_timeline.py (Milestone 10.5),
│   │              tests_navigation.py (Milestone 12), tests_archive.py (Milestone 14)
│   ├── admin.py
│   ├── migrations/0001_initial.py,
│   │              0002_alter_lecture_end_time_alter_lecture_start_time.py,
│   │              0003_exam_exam_code_exam_online_end_exam_online_start_and_more.py,
│   │              0004_alter_exam_exam_code.py,
│   │              0005_datasetversion_importlog_and_more.py
│   │              (no new migration for Milestone 10.5 - navigation/presentation only)
│   ├── management/commands/import_csv.py (extended: --preview/--dry-run/--user, Milestone 10),
│   │                       compare_dataset.py, rollback_dataset.py (Milestone 10)
│   ├── templatetags/routine_tags.py   # {% querystring_page %} (still used by analytics pagination)
│   └── services/
│       ├── timeline.py         # Milestone 10.5 - anchor resolution, event-based windowing,
│       │                       # week/date grouping; attach_lecture_progress()/
│       │                       # attach_revision_status()/attach_exam_readiness() bulk-merge
│       │                       # progress/revision/readiness from analytics.py/revision.py
│       │                       # (retires services/events.py - see Architectural Decisions);
│       │                       # Milestone 12 added a same-date `id` tie-breaker (anchor
│       │                       # determinism) and get_routine_week_map()/get_routine_week()/
│       │                       # attach_routine_week_numbers() (sequential Routine Week
│       │                       # numbering, Phase 6); Milestone 13 made get_routine_week_map()
│       │                       # span every ISO week from the earliest to latest dated
│       │                       # Lecture/Exam (not just weeks with a lecture in them), so the
│       │                       # Exam Timeline can share the exact same numbering instead of
│       │                       # keeping a separate ISO-based label
│       ├── dataset/            # versioning.py, statistics.py, comparison.py, rollback.py
│       │                       # (Milestone 10)
│       ├── exam_coverage.py    # Milestone 15 - get_exam_coverage(exam): covered
│       │                       # subjects/chapters/lecture rows, extracted from
│       │                       # ExamDetailView so it and the exam reminder emails
│       │                       # share one implementation instead of two
│       ├── archive.py          # Milestone 14, Phase 1 - the Routine Archive service:
│       │                       # list_routines()/get_latest_routine()/resolve_routine_file()
│       │                       # scan media/routines/*.pdf by filename convention
│       │                       # (YYYY-MM.pdf) only - no database table, no upload UI. The
│       │                       # only thing a future storage backend (S3, etc.) would need
│       │                       # to replace (Service-First Rule)
│       └── csv/
│           ├── utils.py, validators.py, base_importer.py (gained validate_only(), Milestone 10)
│           ├── routine_helpers.py, lecture_helpers.py
│           ├── subject_importer.py, chapter_importer.py, routine_importer.py
│           └── lecture_topic_importer.py, exam_importer.py
├── reminders/                 # Milestone 15 - the Reminder & Notification System;
│   │                          # Milestone 15.1 added Reminder Administration (Phases 3-8)
│   │                          # and left the engine itself untouched.
│   │                          # models: NotificationPreference (per-user settings, Phase 7;
│   │                          # 15.1 changed only the form's timezone widget, not the field),
│   │                          # ReminderLog (durable idempotency record, Phase 11; 15.1 added
│   │                          # status/error_message/triggered_by for the Activity Log);
│   │                          # NotificationPreferencesView ("/reminders/preferences/"),
│   │                          # ReminderAdminView ("/reminders/admin/", staff-only, 15.1)
│   ├── models.py, forms.py, views.py, urls.py, admin.py
│   ├── tests.py, tests_generators.py, tests_emails.py, tests_commands.py,
│   │              tests_admin.py (Milestone 15.1)
│   ├── migrations/0001_initial.py, 0002_reminderlog_error_message_reminderlog_status_and_more.py
│   ├── services/            # generation - "what reminders should be sent right now?"
│   │   ├── engine.py         # the only file every reminder type is registered in
│   │   │                     # (GENERATORS dict) - dispatches generators, filters
│   │   │                     # against ReminderLog, delivers, logs (Phase 1/11);
│   │   │                     # Milestone 15.1 added `users`/`triggered_by` params (both
│   │   │                     # additive, both default to exact original behavior) and
│   │   │                     # returns ReminderResult (job + delivered + error) instead
│   │   │                     # of bare jobs, so Reminder Administration can show outcomes
│   │   ├── job.py            # ReminderJob dataclass - the one shape every generator emits
│   │   ├── preferences.py    # get_preferences() - persisted row or unsaved default,
│   │   │                     # never writes
│   │   ├── targeting.py      # Milestone 15.1, Phase 5 - target_users(users): every
│   │   │                     # generator's shared "which users" resolution, default
│   │   │                     # every active user, narrowed only when Reminder
│   │   │                     # Administration passes a specific recipient
│   │   ├── timezones.py      # Milestone 15.1, Phase 1 - get_timezone_choices():
│   │   │                     # [(iana_name, "iana_name (UTC+06:00)")], powers the
│   │   │                     # notification preferences form's dropdown
│   │   ├── diagnostics.py    # Milestone 15.1, Phase 3.5 - get_email_config()/
│   │   │                     # test_smtp_connection()/send_test_email(): read-only
│   │   │                     # metadata (never a credential) + two actions, both
│   │   │                     # outside the reminder engine entirely
│   │   ├── daily.py          # Daily Study Agenda (Phase 3)
│   │   ├── weekly.py         # Weekly Overview (Phase 2)
│   │   ├── exams.py          # Weekly/Monthly Exam Reminders (Phase 5)
│   │   ├── revision.py       # Revision Due (Phase 4)
│   │   └── progress.py       # Weekly Progress Summary (Phase 6)
│   ├── emails/               # rendering + delivery - separate from generation (Phase 9)
│   │   ├── registry.py        # reminder_type -> {template, subject}
│   │   ├── renderer.py        # ReminderJob -> (subject, html_body, text_body);
│   │   │                      # `to_plain_text()` made public in Milestone 15.1 so
│   │   │                      # diagnostics.py's test email reuses it instead of a
│   │   │                      # second tag-stripping implementation
│   │   └── delivery.py        # the only file touching django.core.mail
│   └── management/commands/  # send_daily_agenda.py, send_weekly_overview.py,
│                              # send_exam_reminders.py, send_revision_reminders.py,
│                              # send_weekly_progress.py - each scheduler-agnostic,
│                              # each with --dry-run (Phase 10)
│
├── theme/                   # django-tailwind app (auto-generated)
│   ├── static/css/dist/styles.css  # compiled Tailwind output, git-ignored
│   ├── static_src/           # Tailwind v4 full source (Node/npm project); src/styles.css
│   │                         # gained `@custom-variant dark (&:where(.dark, .dark *));`
│   │                         # in Milestone 15.1 - class-based (not media-query-based)
│   │                         # dark mode, so the theme toggle can force Light/Dark
│   │                         # regardless of the OS preference
│   └── templates/base.html   # django-tailwind demo template (unused)
│
├── templates/
│   ├── base.html            # nav (auth-aware: Dashboard/Routine/Exams/Progress/Revision/
│   │                        # Analytics/Datasets-or-Routine-Resources/username/Logout when
│   │                        # logged in, Login/Register when anonymous - Milestone 10 added
│   │                        # the Datasets tab; Milestone 10.5 repointed "Exams" at the new
│   │                        # dedicated exam-timeline URL instead of a routine-list filter
│   │                        # param; Milestone 11 added a skip-to-content link, aria-current
│   │                        # on the active nav item, focus-visible rings throughout, and
│   │                        # horizontal scroll for the nav bar on narrow screens; Milestone
│   │                        # 12 made "Datasets" staff-only (`user.is_staff`), swapped to
│   │                        # "Routine Resources" for everyone else, made the header
│   │                        # `sticky top-0`, and added a page-wide sessionStorage scroll-
│   │                        # position script, Phase 8), HTMX CSRF header, global
│   │                        # #page-indicator loading bar
│   ├── 404.html, 500.html    # friendly error pages (Milestone 6, production-only: DEBUG=False)
│   ├── components/          # Milestone 11 - the shared design-system library (see
│   │   │                    # Implemented Features below for what each one does):
│   │   ├── page_header.html, section_header.html, card.html, metric_card.html
│   │   ├── badge.html, progress_bar.html, empty_state.html, loading_skeleton.html
│   │   ├── filter_panel.html, select_field.html, text_field.html, _filter_form_attrs.html
│   │   ├── form_field.html, auth_card.html
│   │   ├── smart_back.html   # Milestone 12, Phase 7 - one intelligent Back control,
│   │   │                     # replacing every page's hardcoded "Back to X" link
│   │   ├── timeline_body.html   # Milestone 13, Phase 13 - the week/day grouping shared by
│   │   │                        # the Routine and Exam Timeline (previously two near-
│   │   │                        # identical templates); accent colors/labels/card partial
│   │   │                        # passed in as literal params, per-page
│   │   ├── theme_toggle.html   # Milestone 15.1, Phase 9; Milestone 15.2, Part 1 moved it
│   │   │                       # inside the header's User Menu/mobile menu (no longer
│   │   │                       # floating) - takes an `id` param since it now renders
│   │   │                       # twice per authenticated page (desktop + mobile)
│   │   │                       # (every component above also gained `dark:` variants
│   │   │                       # in Milestone 15.1, Phase 10 - see Implemented Features)
│   │   └── progress_meter.html   # Milestone 15.2, Parts 5-6 - the multi-dimensional
│   │                             # progress visualization (blocks/segmented bar,
│   │                             # adapting to unit count alone), always rendered from
│   │                             # progress_service - replaces progress_bar.html
│   │                             # wherever real per-topic study data is shown
│   ├── partials/_timeline_jump_fab.html   # Milestone 10.5 - the floating jump-to-anchor
│   │                                      # button, included by Routine/Exam Timeline and
│   │                                      # the Revision Queue; Milestone 12 made its label
│   │                                      # context-aware ("Jump to Current / Next Class" /
│   │                                      # "Jump to Next Exam" / "Jump to Today's Revision")
│   │                                      # and moved scroll-position memory itself into
│   │                                      # base.html (Phase 8 - now page-wide, not just
│   │                                      # these three pages)
│   ├── registration/         # login.html, password_change_form.html, password_change_done.html,
│   │                        # password_reset_form.html, password_reset_done.html,
│   │                        # password_reset_confirm.html, password_reset_complete.html
│   │                        # (Milestone 7 - Django's default auth view template names;
│   │                        # Milestone 11 standardized every field loop onto
│   │                        # components/form_field.html)
│   ├── accounts/register.html   # Milestone 7 (Milestone 11: components/form_field.html;
│   │                            # Milestone 15.2, Part 14: minor spacing/dark-mode polish)
│   ├── accounts/profile.html    # Milestone 15.2, Part 1 - the header's User Menu
│   │                            # "Profile" destination: account facts + links onward
│   │                            # to Notification Preferences/(if staff) Reminder Admin -
│   │                            # deliberately minimal, no new academic feature
│   ├── dashboard/index.html, _widgets.html    # _widgets.html gained a "Study Advisor" section
│   │                                          # (Milestone 8) and a "Revision" section
│   │                                          # (Milestone 9: due today/overdue/upcoming/
│   │                                          # completed-this-week/exam-ready counts);
│   │                                          # Milestone 11 rebuilt both onto
│   │                                          # page_header/metric_card/section_header/
│   │                                          # progress_bar/empty_state
│   ├── routine/timeline.html,                 # Milestone 10.5 - replaces list.html/_table.html
│   │   partials/_timeline.html, _timeline_body.html, _lecture_card.html,
│   │   _window_previous.html, _window_next.html
│   │   (Milestone 11: page_header/filter_panel/progress_bar/badge/empty_state throughout;
│   │   Milestone 12: sticky workspace toolbar (Phase 1), "Routine Week N" week headers
│   │   linking to the new canonical page (Phase 6), subject-name links (Phase 5))
│   ├── routine/week_detail.html   # Milestone 12 - the canonical Routine Week page
│   │       # (Previous/Next Week nav, exam-ready badges)
│   ├── routine/resources.html, partials/_resources_viewer.html   # Milestone 14, Phase 1 -
│   │       # the real Routine Archive viewer (replaces Milestone 12's honest-empty-state
│   │       # placeholder); _resources_viewer.html is the HTMX-swappable partial (iframe +
│   │       # Download button + Previous Routines list) shared by the full-page render and
│   │       # every `?routine=<filename>` selection request
│   ├── lectures/detail.html, _topic_row.html   # detail.html gained a Revision Schedule list
│   │                                          # + Exam Ready badge (Milestone 9);
│   │                                          # Milestone 11 added aria-label to every
│   │                                          # progress checkbox and a table caption;
│   │                                          # Milestone 12 added Subject/Chapter links,
│   │                                          # Previous/Next Lecture, and Upcoming Exam
│   │                                          # cross-navigation (Phase 10), plus smart_back
│   ├── exams/detail.html, timeline.html,      # timeline.html + partials new in Milestone 10.5
│   │   partials/_timeline.html, _timeline_body.html, _exam_card.html,
│   │   _window_previous.html, _window_next.html
│   │   (Milestone 11: page_header/filter_panel/badge/empty_state; fixed a stale
│   │   "Back to exams" link left pointing at the pre-10.5 routine-list filter URL;
│   │   Milestone 12: detail.html gained Covered Subjects/Chapters/Readiness cross-
│   │   navigation (Phase 10) and smart_back, replacing that same link entirely)
│   ├── progress/overview.html   # Milestone 11: page_header/progress_bar/empty_state,
│   │                            # table caption; Milestone 12: subject-name links
│   ├── revision/queue.html, detail.html,      # Milestone 9; queue.html/_queue.html gained a
│   │       partials/_queue.html, _stats.html, _filters.html, _detail_content.html
│   │       # #today-marker divider + Jump-to-Today FAB include (Milestone 10.5);
│   │       # Milestone 11: page_header/section_header (sticky)/metric_card/badge/
│   │       # empty_state/filter_panel throughout; Milestone 12: sticky workspace toolbar,
│   │       # context-aware jump label ("Jump to Today's Revision")
│   ├── analytics/subjects.html, chapters.html, lectures.html, exams.html, insights.html
│   │   (Milestone 8), _nav.html, partials/_subjects_table.html, _chapters_table.html,
│   │   _lectures_table.html, _exams_table.html (gained an Exam Ready column, Milestone 9),
│   │   _pagination.html (Milestone 6),
│   │   _insights.html (Milestone 8 - CSS-only heatmap/bar-chart visualizations; gained a
│   │   Revision Insights section in Milestone 9)
│   │   (Milestone 11: page_header/filter_panel/metric_card/progress_bar/badge/
│   │   empty_state throughout; table captions; _nav.html gained aria-current;
│   │   Milestone 12: every subject/chapter/exam reference across all five pages now
│   │   links to its canonical page - Phase 5's "Universal Linking")
│   ├── datasets/history.html, compare.html,   # Milestone 10; both views now staff-only
│   │       partials/_history.html, _compare.html, _filters.html
│   │       # (`_StaffOnlyMixin`, Milestone 12, Phase 9) - templates themselves unchanged
│   ├── subjects/detail.html, chapter_detail.html   # new in Milestone 12 - the canonical
│   │       # Subject/Chapter pages (see Implemented Features below)
│   │       (Milestone 11: page_header/filter_panel/badge/empty_state throughout)
│   ├── reminders/preferences.html   # Milestone 15, Phase 7 - the notification settings
│   │       # form; timezone field became a dropdown in Milestone 15.1, Phase 1
│   ├── reminders/admin/dashboard.html   # Milestone 15.1, Phases 3-8 - the staff-only
│   │       # Reminder Administration page: Email Configuration, Send Test Email,
│   │       # Reminder Test Center, Reminder Activity Log, all as sections of one
│   │       # template re-rendered with a `result` context var per action (see
│   │       # Implemented Features below)
│   └── emails/               # Milestone 15, Phase 8 - table-based, inline-styled HTML
│           # email templates (a separate rendering surface from the app's own
│           # base.html - see Implemented Features below)
│           base.html, daily_agenda.html, weekly_overview.html, revision_due.html,
│           exam_reminder.html (shared by weekly + monthly), weekly_progress.html,
│           test_email.html (Milestone 15.1 - the standalone SMTP-verification email)
│
├── static/
├── staticfiles/              # collectstatic output (Milestone 14, Phase 5), git-ignored
├── media/                    # git-ignored - Milestone 14, Phase 1: routines/*.pdf lives here
│   └── routines/             # media/routines/YYYY-MM.pdf - the Routine Archive itself;
│                             # copying a new PDF in is the only "upload" step this app has
├── data/
│   └── dataset_archive/     # Milestone 10 - archived CSV snapshots, one folder per
│                            # DatasetVersion (created by archive_source_csvs());
│                            # CSVs currently live at project root, not here
│
├── subjects.csv, chapters.csv, routine.csv, lecture_topics.csv, exams.csv
│                             # the finalized, validated source dataset
├── validation_report.md     # generated by validate_datasets, 0 errors/0 warnings -
│                             # git-ignored as of Milestone 14 (a regenerable report, not
│                             # source data - see Phase 2/Known Issues)
│
├── 01_Product_Requirements_Document_PRD_v1.1.md
├── 02.1_Database_Model_Contract_v1.0.md
├── 02_Database_Design.md
├── 02_Database_Design_v1.1.md
├── 03_System_Architecture.md
├── 04_Navigation_Screen_Flow.md
├── 05_UI_UX_Specification.md
├── 06_CSV_Import_Specification.md
├── 07_Development_Roadmap.md
├── 08_Coding_Standards.md
└── Varsity_Admission_Tracker_Architecture_v1.md
```

---

## Implemented Features

Milestone 1 only implements project scaffolding. No application features exist yet.

- Python virtual environment `.admission_venv` created and used for all commands.
- Git repository initialized with `.gitignore` covering the venv, caches, SQLite
  DB, `.env`, editor folders, `node_modules/`, `staticfiles/`, `media/`, logs,
  and the compiled Tailwind CSS build output.
- Django project package `admission_helper` created at the repository root
  (root folder `Admission Helper`, package name `admission_helper` in
  snake_case per Python conventions).
- Seven Django apps created exactly as specified: `core`, `dashboard`,
  `subjects`, `lectures`, `progress`, `routines`, `reminders`. Each contains
  only the default files generated by `startapp` — no models, views, URLs, or
  business logic.
- All seven apps registered in `INSTALLED_APPS`, alongside `django_htmx`,
  `tailwind`, and the generated `theme` app.
- SQLite configured as the only database (Django default backend, `db.sqlite3`
  at project root, git-ignored).
- Packages installed in the virtual environment: `Django`, `django-htmx`,
  `django-tailwind` (with its `pytailwindcss` dependency). No Celery, Redis,
  DRF, or database drivers were installed.
- HTMX configured: `django_htmx.middleware.HtmxMiddleware` added to
  `MIDDLEWARE`, and `htmx.org` loaded via CDN `<script>` tag in
  `templates/base.html`. No HTMX interactions/attributes implemented yet.
- Tailwind CSS configured via `django-tailwind`:
  - `theme` app generated using the "Tailwind v4 Full" template (Node.js
    required; Node v24 / npm v11 were available in this environment).
  - `TAILWIND_APP_NAME = 'theme'` and `NPM_BIN_PATH` set in `settings.py`
    (see Architectural Decisions).
  - `python manage.py tailwind install` completed successfully and produced
    a compiled `theme/static/css/dist/styles.css`.
  - `templates/base.html` loads Tailwind via `{% tailwind_css %}`.
- `templates/base.html` created as a minimal HTML skeleton (doctype, head with
  Tailwind/HTMX includes, empty `content` block). No pages/views reference it
  yet since no app URLs were created in this milestone.
- `static/` and `data/` directories created at the project root. `data/` is
  intentionally empty (no CSV files added).
- `STATICFILES_DIRS` points at the project `static/` directory;
  `STATIC_URL = 'static/'` (Django default).
- `TIME_ZONE` set to `Asia/Dhaka` (see Architectural Decisions).
- `.env.example` created with placeholder keys: `SECRET_KEY`, `DEBUG`,
  `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`. No `.env` file was committed.
  Settings.py still uses the auto-generated `SECRET_KEY`/`DEBUG` values
  directly (not yet wired to environment variables) — wiring real env-var
  loading was not part of this milestone's scope.
- `requirements.txt` generated and manually trimmed to runtime-relevant
  packages only (Django, django-htmx, django-tailwind, pytailwindcss, and
  Django's direct dependencies asgiref/sqlparse/tzdata). Transitive packages
  pulled in only by the one-time `tailwind init` scaffolding step
  (cookiecutter and its dependencies) were excluded — see Architectural
  Decisions.
- Verified `python manage.py migrate` applies all default Django migrations
  successfully.
- Verified `python manage.py runserver` starts without errors and serves the
  default Django welcome page (HTTP 200).

### Milestone 2 — Database Models

Implemented the complete Version 1 database schema, translated exactly from
`02.1_Database_Model_Contract_v1.0.md` (primary source of truth per this
milestone's document priority order).

- `subjects/models.py`: `Subject`, `Chapter`.
- `routines/models.py`: `Routine`, `Lecture`, `Exam` (with `Exam.ExamType`
  `TextChoices`: `WEEKLY`, `MONTHLY`, `SPECIAL`).
- `lectures/models.py`: `LectureTopic`.
- `progress/models.py`: `Progress`.
- Every model uses `BigAutoField` primary keys, defines `Meta.ordering`, and
  implements `__str__()` exactly as specified in the contract.
- Every `ForeignKey`/`OneToOneField` defines both `related_name` and
  `on_delete`, matching the contract's relationship and delete-policy tables
  exactly:
  - `Chapter.subject` → CASCADE, `related_name="chapters"`
  - `Lecture.routine` → CASCADE, `related_name="lectures"`
  - `Lecture.subject` → PROTECT, `related_name="lectures"`
  - `LectureTopic.lecture` → CASCADE, `related_name="topics"`
  - `LectureTopic.chapter` → PROTECT, `related_name="lecture_topics"`
  - `Progress.lecture_topic` → CASCADE (`OneToOneField`),
    `related_name="progress"`
  - `Exam.routine` → CASCADE, `related_name="exams"`
- Unique constraints implemented via modern `Meta.constraints` +
  `UniqueConstraint` (not the deprecated `unique_together`):
  - `Chapter`: unique (`subject`, `chapter_no`)
  - `Lecture`: unique (`routine`, `lecture_code`)
  - `LectureTopic`: unique (`lecture`, `chapter`, `topic`)
  - `Subject.code` and `Subject.display_order` are unique via field-level
    `unique=True` (no composite constraint needed).
- Indexes: fields the contract marks with inline `db_index=True`
  (`Subject.code`, `Lecture.lecture_date`, `Routine.active`, `Exam.exam_date`,
  `Progress.updated_at`) were implemented as inline field options. `ForeignKey`
  fields (`Chapter.subject`, `Lecture.subject`, `LectureTopic.lecture`,
  `LectureTopic.chapter`, `Exam.routine`, `Routine`'s lectures/exams reverse
  FKs) already receive an automatic database index from Django's default
  `ForeignKey` behavior. Where the contract's "Indexes" section names a field
  that has neither an inline `db_index` nor an automatic FK index
  (`Chapter.chapter_no`, `Lecture.lecture_code`, `Exam.exam_type`), an explicit
  `Meta.indexes` entry was added. This avoids creating duplicate/overlapping
  indexes on the same column while still indexing every column the contract
  lists — verified with `manage.py sqlmigrate subjects 0001`, which confirms
  a single index per column (see Architectural Decisions).
- All seven models registered in Django Admin via plain
  `admin.site.register(Model)` — no `list_display`, `search_fields`, filters,
  fieldsets, or inlines.
- No views, URLs, templates, signals, custom managers, services, business
  logic, validators beyond the contract, fixtures, or tests were added.
- Migrations generated with `makemigrations` (one `0001_initial.py` per app:
  `subjects`, `routines`, `lectures`, `progress`) and applied with `migrate`.
  No migration files were hand-edited.
- Verified `python manage.py check` reports no issues, and
  `manage.py makemigrations --check --dry-run` reports no undetected model
  changes.

### Dataset Validation (pre-Milestone 3)

Before implementing the CSV import system, the real source dataset
(`subjects.csv`, `chapters.csv`, `routine.csv`, `lecture_topics.csv`,
`exams.csv` — prepared from Udvash Routine-01/02, located in the project
root) was validated. **No importer was implemented; no CSV data was
modified.**

- Added `core/management/commands/validate_datasets.py` — a read-only
  Django management command (`python manage.py validate_datasets
  [--dir DIR] [--out PATH]`) that parses all five CSVs and checks:
  structural quality (UTF-8/BOM, duplicate headers, cell whitespace, blank
  rows), per-file field validation (required columns, duplicates, valid
  dates/times/integers), and cross-file referential integrity (orphan
  subjects/chapters/lectures/topics/exam references). Defaults to reading
  from the project root and writes `validation_report.md` there. Exits
  non-zero when errors are found.
- Ran the command and generated `validation_report.md` at the project
  root. Result: **dataset currently fails validation** — 286 errors, 64
  warnings. No CSV files were edited; the CSV quality checks (encoding,
  BOM, cell whitespace, duplicate headers, NUL bytes) found nothing to
  objectively auto-fix, so none of the datasets were touched.
- The lecture-numbering gap at "06" (missing for every subject: `P-06`,
  `C-06`, `M-06`, `B-06`) was implemented as an explicitly allowed,
  non-reported gap per this task's instructions, both for `routine.csv`
  lecture sequencing and the analogous `WE-06` gap in `exams.csv`.
- Duplicate `lecture_code` detection in `routine.csv` was scoped to
  `event_type=CLASS` rows only: the same `lecture_code` legitimately
  recurs on a paired `DAILY_EXAM` row (e.g. `M-01` appears once as CLASS
  and once as DAILY_EXAM) and this is normal dataset structure, not a
  duplicate Lecture — only a `lecture_code` repeated across more than one
  CLASS row would be flagged.
- See Known Issues for the substantive findings (they are dataset/spec
  conflicts to be resolved by the architect, not something this validator
  or its author should silently fix).

### Dataset Revision (pre-Milestone 3)

Following the validation pass above, the finalized dataset design was
confirmed and the dataset + validator were brought into alignment with
it. **`validate_datasets` now reports 0 errors, 0 warnings — the dataset
is confirmed ready for Milestone 3 CSV import implementation.**

- **`subjects.csv` rewritten to subject-level codes**: `P1`/`P2` merged
  into `P` ("Physics"), `C1`/`C2` into `C` ("Chemistry"), `M1`/`M2` into
  `M` ("Higher Mathematics"), `B1`/`B2` into `B` ("Biology"); `E`
  ("English") and `BA` ("Bangla") unchanged. 10 rows → 6 rows,
  `display_order` renumbered 1–6. This was a deliberate design decision
  (papers are represented by chapters, not by separate subjects) — not a
  data error.
- **`chapters.csv` gained an explicit `paper` column** (`1` or `2`),
  since subject codes no longer encode which paper a chapter belongs to.
  `P1`/`P2`/`C1`/`C2`/`M1`/`M2`/`B1`/`B2` subject_code values were mapped
  to their subject-level code (`P`/`C`/`M`/`B`) plus the corresponding
  `paper` value. All 75 chapter rows were preserved — none removed, per
  instructions (the app must keep supporting both papers of every subject
  for future Udvash routines, even chapters unused by the current
  routine). New natural key: unique (`subject_code`, `paper`,
  `chapter_no`); `display_order` uniqueness is now scoped per
  (`subject_code`, `paper`) instead of per `subject_code`.
- **`routine.csv`, `lecture_topics.csv`, `exams.csv` were left
  unchanged** — their `subject_code` values (`M`/`P`/`C`/`B`/`E`/`BA`)
  already matched the finalized subject-level scheme, and their other
  content (event types, exam schema, Bengali chapter references) was
  already the finalized, correct data. No lecture, topic, or exam rows
  were invented, removed, or altered.
- **Validator rewritten** (`core/management/commands/validate_datasets.py`)
  to validate against the finalized design instead of the original
  06_CSV_Import_Specification.md draft:
  - `chapters.csv` required columns updated to include `paper`; the
    (subject_code, chapter_no) uniqueness/lookup key became
    (subject_code, paper, chapter_no).
  - `routine.csv`'s `event_type` enum updated to the finalized
    `{CLASS, DAILY_EXAM, WEEKLY_EXAM, MONTHLY_EXAM}` — no longer flagged
    as a deviation.
  - `exams.csv`'s required-column check updated to the finalized schema
    (`exam_code, exam_type, title, lecture_codes, exam_date,
    online_start, online_end`) — no longer flagged as missing the old
    spec's columns. Added format/ordering validation for the
    `online_start`/`online_end` columns (not present in the old spec).
  - **`lecture_topics.csv`'s `chapter_no` parser**: added
    `parse_chapter_ref()`, which parses the Bengali
    "`<১ম|২য়> পত্র অধ্যায়-<bengali digits>`" reference (e.g. `১ম পত্র
    অধ্যায়-০২` = 1st paper, chapter 2) into a (paper, chapter_no) pair
    and resolves it against the new `chapters.csv` key. Values are never
    replaced with bare integers, per instructions.
  - **Bengali Unicode normalization bug found and fixed during this
    work**: the Bengali letter "য়" (YYA) has two valid Unicode
    representations — the precomposed codepoint U+09DF, and the
    decomposed sequence YA (U+09AF) + NUKTA (U+09BC). They render
    identically but do not compare equal as Python strings, and
    `unicodedata.normalize()` does not convert between them (U+09DF has
    no canonical decomposition in the Unicode Character Database for
    this pair). The dataset consistently uses the precomposed form; an
    initial version of the parser's regex (typed via this session's
    tools) accidentally used the decomposed form, causing every
    Bengali chapter reference to fail to parse. Fixed by building the
    regex from explicit codepoint constants and normalizing input text
    before matching, so the encoding can't silently drift again.
  - **Self-study subjects**: subjects with zero `CLASS` rows in
    `routine.csv` (in this dataset: `E`, `BA` — English and Bangla are
    self-study only, no live class) are computed dynamically and exempted
    from the "lecture_code must exist in routine.csv" cross-check in
    `lecture_topics.csv` and `exams.csv`. This was confirmed against the
    uploaded routine data itself (routine.csv has no `E`/`BA` `CLASS`
    rows at all) rather than assumed — per instructions, no lecture rows
    were invented to force a match.
  - **Orientation row** (`routine.csv` row 2: `event_type=CLASS`, blank
    `subject_code` and `lecture_code`, title "ওরিয়েন্টেশন ক্লাস"): kept
    as-is in the data (not reassigned to a new event type, since only the
    four finalized event types are allowed, and orientation doesn't fit
    `DAILY_EXAM`/`WEEKLY_EXAM`/`MONTHLY_EXAM`). The validator's rule was
    revised instead: a `CLASS` row is only required to have both
    `subject_code` and `lecture_code` when at least one of them is
    present; a row with **both** blank is treated as an intentional
    general/orientation session not tied to any subject, not an error. A
    row with only one of the two blank is still flagged (inconsistent
    data).
  - The "06" numbering-gap exemption (already implemented in the prior
    validation pass) was extended to the lecture_code cross-file checks:
    `lecture_topics.csv` has pre-written topic content for `P-06`,
    `C-06`, `M-06`, `B-06` even though `routine.csv` has no `CLASS` row
    for lecture 06 of any subject (the live class was skipped). These
    references are now recognized as expected, not orphans.
- Re-ran `validate_datasets`: **0 errors, 0 warnings**. Updated
  `validation_report.md` accordingly (see Statistics: 6 subjects, 75
  chapters, 50 lectures, 91 lecture topics, 15 exams).
- `python manage.py check` re-verified clean after these changes (no
  Django models, migrations, or application code besides the validator
  were touched).

### Milestone 3.0 — Model Contract Revision (Chapter Paper Support)

Resolved the architectural gap flagged in the previous entry's Known
Issues (`Chapter` had no way to represent paper). This is a real schema
change to a model completed in Milestone 2 — scoped narrowly to `Chapter`
only, per instructions.

- `subjects/models.py`: `Chapter` gained a `paper` field —
  `PositiveSmallIntegerField` with a new `Chapter.Paper` `IntegerChoices`
  (`FIRST = 1, "1st Paper"`; `SECOND = 2, "2nd Paper"`).
- Unique constraint changed from (`subject`, `chapter_no`) to (`subject`,
  `paper`, `chapter_no`) — two chapters with the same number now
  coexist correctly when they belong to different papers of the same
  subject.
- `Meta.ordering` changed from `["subject", "display_order"]` to
  `["subject", "paper", "chapter_no"]`, per this task's explicit
  instruction.
- `__str__()` changed to
  `f"{self.subject.name} - {self.get_paper_display()} - Chapter {self.chapter_no} - {self.name}"`
  (e.g. "Physics - 1st Paper - Chapter 2 - Vector"), using the full
  subject name and the `Paper` choice's display label rather than the
  previous `f"{subject.code} Chapter {chapter_no}"`.
- `Subject`, `Routine`, `Lecture`, `LectureTopic`, `Exam`, `Progress` were
  not touched, per instructions.
- Migration `subjects/migrations/0002_alter_chapter_options_and_more.py`
  generated via `makemigrations` (one-off default `1` supplied
  interactively for the new non-nullable field, with
  `preserve_default=False` — confirmed the `Chapter` table had 0 rows at
  the time, since no importer exists yet, so the one-off default never
  actually applies to real data). Applied via `migrate`.
- `subjects/admin.py`: `Chapter` registration upgraded from a bare
  `admin.site.register(Chapter)` to a `ChapterAdmin` with
  `list_display = ["subject", "paper", "chapter_no", "name"]`,
  `list_filter = ["subject", "paper"]`, `search_fields = ["name"]`, per
  this task's explicit spec. `Subject` admin registration is unchanged
  (still a bare `admin.site.register(Subject)` — not part of this task's
  scope).
- Verified in the Django shell: chapters with the same `chapter_no` but
  different `paper` values save successfully; a true duplicate
  (`subject`, `paper`, `chapter_no`) raises `IntegrityError`. Verified
  the admin Chapter changelist renders (200 OK, authenticated) with the
  new columns, filters and search box present.
- Documentation synchronized: `02.1_Database_Model_Contract_v1.0.md`'s
  Chapter section (§3) updated to add `paper`/`Paper` choices, the new
  unique constraint, ordering, and `__str__()`; `02_Database_Design_v1.1.md`'s
  Chapter table, Index Strategy (§7), and the `lecture_topics.csv`
  CSV-mapping row (§6) updated to reflect `paper`. No other sections of
  either document, and no other design documents, were touched.
- No CSV files were modified; the validated dataset
  (`validation_report.md`: 0 errors, 0 warnings) is unchanged and
  untouched by this task.

### Milestone 3.1 — Lecture Time Fields Made Optional

A second, smaller model gap discovered while implementing the CSV
importer (see Milestone 3 below): `Lecture.start_time`/`end_time` were
required (`TimeField()`, no `null`/`blank`), but real `routine.csv` data
leaves them blank for essentially every `CLASS` row (only the skipped
orientation row has a time). This affected all ~50 lectures, not a
handful of rows, so — after checking with the user rather than
inventing a placeholder time or silently failing to import any lecture
— `start_time`/`end_time` were changed to `null=True, blank=True`.

- `routines/models.py`: `Lecture.start_time`/`Lecture.end_time` →
  `models.TimeField(null=True, blank=True)`.
- Migration `routines/migrations/0002_alter_lecture_end_time_alter_lecture_start_time.py`
  generated and applied.
- No other fields, models, or migrations touched.

### Milestone 3 — CSV Import System

Implemented the full CSV import pipeline, wired to `python manage.py
import_csv`. Two more schema/data gaps were discovered and resolved
during implementation (each confirmed with the user before proceeding,
given the blast radius) — see Architectural Decisions and Known Issues.

**Structure** (`routines/`):

```text
management/commands/import_csv.py
services/csv/
    __init__.py
    utils.py               # CSV reading (BOM-safe), Bengali digit/chapter-ref parsing
    validators.py           # ImportValidationError, require/parse_*/validate_choice, DuplicateTracker
    base_importer.py        # BaseImporter: read -> validate_header -> per-row validate+import, all in one transaction.atomic()
    routine_helpers.py       # get_or_create_routine() - shared fixed-name Routine lookup
    subject_importer.py
    chapter_importer.py
    routine_importer.py
    lecture_topic_importer.py
    exam_importer.py
```

- **Import order enforced** by `IMPORT_STAGES` in `import_csv.py`:
  subjects → chapters → routine → lecture_topics → exams. Each stage
  runs inside its own `transaction.atomic()` (in `BaseImporter.run()`);
  an `ImportValidationError` in any row rolls back that file's changes
  and stops the command immediately — later stages never run. Verified
  with a deliberately-corrupted scratch copy of `exams.csv` (bad date):
  the command aborted with a formatted error and the `Exam` count in the
  database stayed unchanged (rollback confirmed) — the real dataset was
  never touched for this test.
- **Idempotent**: every importer uses `update_or_create()` keyed on each
  model's natural identity (`Subject.code`; `Chapter`'s
  (`subject`,`paper`,`chapter_no`); `Lecture`'s (`routine`,
  `lecture_code`); `LectureTopic`'s (`lecture`,`chapter`,`topic`);
  `Exam`'s (`routine`,`exam_name`,`exam_date`) — see Known Issues re:
  `Exam` having no real unique constraint). Verified by running
  `import_csv` twice in a row: identical row counts both times (6
  subjects, 75 chapters, 50 lectures, 60 lecture topics, 15 exams), no
  duplicates.
- **`Routine`**: has no natural unique key (only `id`), so a single
  fixed name (`"Imported Routine"`, in `routine_helpers.py`) is
  reused/`update_or_create`d on every run, keeping repeated imports
  attached to the same `Routine` row.
- **Only `CLASS` rows in `routine.csv` become `Lecture` records.**
  `DAILY_EXAM`/`WEEKLY_EXAM`/`MONTHLY_EXAM` rows are read and validated
  (valid `event_type`, valid date) but have no corresponding model to
  persist into — the CSV Import Specification's Database Mapping table
  only maps `routine.csv` to `Routine` + `Lecture`. Counted internally
  (`event_type_counts`) but not reported as a separate "imported" figure
  since nothing is written to the database for them.
- **Orientation row** (`routine.csv` row 2: `CLASS`, blank
  `subject_code` and `lecture_code`): recognized as an intentional
  general session and skipped with a clear, itemized log line — matches
  the same rule established in `validate_datasets` for this exact row.
- **`lecture_topics.csv`'s Bengali chapter reference is resolved, not
  flattened**: `parse_chapter_ref()` (in `utils.py`) parses e.g. "১ম
  পত্র অধ্যায়-০২" into (paper=1, chapter_no=2) and looks up
  `Chapter.objects.get(subject=subject, paper=paper, chapter_no=chapter_no)`.
  A missing chapter raises the exact error shape from this milestone's
  spec (`Reason: Chapter not found`, plus `Subject`/`Paper`/`Chapter`
  detail lines).
- **31 of 91 `lecture_topics.csv` rows are skipped, not imported** — by
  explicit user direction (asked before implementing, given the scale):
  `LectureTopic.lecture` is a required FK, and 26 rows (English/Bangla,
  self-study subjects with zero `CLASS` rows in `routine.csv`) plus 5
  rows (the intentional lecture-06 gap: `P-06`/`C-06`/`M-06`×2/`B-06`)
  have no `Lecture` to attach to. Each skip is logged individually
  (`⚠ Skipped row N: ...reason...`), not silently dropped — final count:
  60 of 91 rows imported. "Self-study" is detected dynamically (does
  any `Lecture` exist for that subject code?), not hardcoded to `E`/`BA`.
- **`exams.csv` → `Exam` field mapping**: `title` → `exam_name` (matches
  the model's original "Exam title" intent). `exam_code`,
  `online_start`, `online_end` have no matching `Exam` field — by
  explicit user direction (asked before implementing), they are folded
  into `notes` as labeled text (`"exam_code: ...\nonline_start:
  ...\nonline_end: ..."`) rather than silently dropped or invented into
  new model fields. `lecture_codes` is stored as-is (a JSON list of
  code strings) in `covered_lectures` — no FK resolution needed for that
  field type; each code is still checked against known Lectures/
  self-study subjects/the lecture-06 gap, and a genuinely unknown code
  is rejected with a clear error (per this milestone's explicit "reject
  missing lecture references" requirement — this only applies to codes
  that don't match any recognized pattern).
- **Console logging** matches the milestone's requested format:
  `Importing <stage>...` / `✓ Imported N <unit>` per stage, itemized
  `⚠ Skipped row N: <reason>` lines for intentional skips, and a
  `ERROR / File: / Row: / Reason: / <extra labeled details>` block for
  hard failures. `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
  is called at the start of `handle()` so the ✓/⚠ symbols and Bengali
  chapter names in error details don't crash on a Windows console
  defaulting to cp1252 (hit and fixed during this task's own
  verification runs).
- Verified end-to-end: `import_csv` run twice (idempotent, see above);
  `manage.py check` clean; Django Admin changelists for `Subject`,
  `Chapter`, `Routine`, `Lecture`, `Exam`, `LectureTopic` all render
  (200 OK, authenticated) with real imported data, and a `LectureTopic`
  correctly shows its linked `Lecture` and `Chapter` (verified via
  `select_related` in the shell, e.g. `M-01` → "Higher Mathematics -
  1st Paper - Chapter 3 - সরলরেখা").
- No CSV files were modified by this milestone; `validate_datasets`
  re-run afterward still reports 0 errors, 0 warnings.

### Milestone 4 — Student Dashboard & Study Workflow

Implemented the first user-facing pages: Dashboard, Routine list,
Lecture detail (with progress checkboxes), and Exam detail, plus an
HTMX progress-toggle endpoint and a Progress overview page. No
authentication, notifications, email, analytics, REST APIs, or JS
frameworks were added, per this milestone's scope.

**Routes** (wired in `admission_helper/urls.py` + each app's `urls.py`):

```text
/                                        dashboard.views.DashboardView
/routine/                                routines.views.RoutineListView
/lecture/<lecture_code>/                 lectures.views.LectureDetailView
/exam/<int:pk>/                          routines.views.ExamDetailView
/progress/                               progress.views.ProgressOverviewView
/progress/topic/<int:id>/toggle/<field>/ progress.views.ProgressToggleView (HTMX, POST)
```

- **Dashboard** (`dashboard/views.py`, `templates/dashboard/index.html`):
  today's lectures/exams (via `timezone.localdate()`, `TIME_ZONE =
  "Asia/Dhaka"` from Milestone 1) with an explicit empty state when
  nothing is scheduled; next upcoming lecture/exam; 5 most recent
  `Progress` updates; overall completion bar. All values computed fresh
  per request (no caching), per this milestone's explicit instruction.
- **Routine List** (`routines/views.py: RoutineListView`,
  `templates/routine/list.html` + `_table.html` partial): see
  Architectural Decisions for why this merges `Lecture` and `Exam`
  rather than showing "every routine.csv event" literally — only CLASS
  rows (→ `Lecture`) and exams.csv rows (→ `Exam`) are persisted models;
  `DAILY_EXAM`/`WEEKLY_EXAM`/`MONTHLY_EXAM` routine.csv rows have none
  (see Milestone 3). Supports `?event_type=CLASS|EXAM` and
  `?subject=<code>` filtering (subject filtering an `EXAM` row checks
  whether any of its `covered_lectures` codes share that subject's
  prefix), pagination (20/page, `django.core.paginator.Paginator` over
  the merged, date-sorted list), and HTMX: the filter `<select>`s
  `hx-get` the same URL on `change` and swap `#routine-results`;
  pagination links do the same. The view's `get_template_names()`
  returns just `_table.html` when `request.htmx` is true (via
  `django_htmx`, configured in Milestone 1) so a full page is never
  re-sent for a filter/page change. A small `routine_tags` templatetag
  (`{% querystring_page %}`) rebuilds the current querystring with a new
  `page` value for pagination links.
- **Lecture Detail** (`lectures/views.py: LectureDetailView`,
  `templates/lectures/detail.html` + `_topic_row.html` partial): looked
  up by `lecture_code` (`slug_field`), not `pk` — matches the
  `/lecture/<lecture_code>/` route and 404s cleanly for an unknown code
  (verified: `/lecture/DOES-NOT-EXIST/` → 404). Shows lecture info,
  distinct chapters covered (deduplicated from its topics, in topic
  order), and a topic table. **Each topic gets 4 checkboxes**
  (`class_done`, `notes_done`, `revision_done`, `practice_done`) rather
  than a single "complete" toggle — `Progress` was deliberately modeled
  with four independent booleans in Milestone 2, and flattening that to
  one checkbox would have discarded information the schema was built to
  capture. Each checkbox is an independent HTMX control
  (`hx-post=".../toggle/<field>/"`, `hx-trigger="change"`,
  `hx-target="closest tr"`, `hx-swap="outerHTML"`) — toggling one
  re-renders just that `<tr>` with the new state, no page reload.
- **Progress toggle endpoint** (`progress/views.py:
  ProgressToggleView`): `Progress.objects.get_or_create(lecture_topic=topic)`
  — the `OneToOneField` guarantees this can never create a duplicate —
  then flips the requested boolean and saves (`updated_at` refreshes via
  `auto_now=True`, already on the model). The `field` URL segment is
  validated against a fixed allow-list (`TOGGLEABLE_FIELDS`); anything
  else 404s rather than being passed to `setattr` unchecked. Returns the
  re-rendered `_topic_row.html` fragment.
- **Exam Detail** (`routines/views.py: ExamDetailView`,
  `templates/exams/detail.html`): looked up by `pk`, 404s cleanly for an
  unknown id (verified). Displays exam info, notes, and each
  `covered_lectures` code resolved to its `Lecture` where one exists
  (linking to that lecture's detail page) or shown as plain text where
  it doesn't (self-study subjects/the lecture-06 gap — same categories
  documented in Milestone 3). "Online period" is parsed back out of the
  `notes` field's labeled text (`parse_exam_notes()`) — see Architectural
  Decisions re: why that data lives in `notes` rather than a dedicated
  field.
- **Progress overview** (`progress/views.py: ProgressOverviewView`,
  `templates/progress/overview.html`, backed by new `progress/services.py`):
  overall completion bar plus a per-subject completion breakdown table.
  `progress/services.py` centralizes the "what counts as a completed
  topic" definition (`get_completion_stats()`,
  `get_subject_completion_stats()`) so the Dashboard and this page can't
  drift out of sync on the definition.
- **Navigation** (`templates/base.html`): Dashboard / Routine / Exams /
  Progress links added to the existing base template's header. "Exams"
  links to `/routine/?event_type=EXAM` rather than a separate page/app —
  this milestone's spec listed an Exam **Detail** page but no Exam
  **List** page, and creating a new `exams` app or list view for that
  would have gone beyond spec (and the locked app structure from
  Milestone 1 doesn't include an `exams` app — `Exam` lives in
  `routines`). Active-page highlighting compares `request.path` (and,
  for the Routine/Exams split, `request.GET.event_type`) directly in the
  template — no per-view context variable needed.
- **HTMX CSRF fix**: the first end-to-end test of the progress toggle
  returned `403 Forbidden` — HTMX POSTs don't include Django's CSRF
  token by default. Fixed by adding
  `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` to `<body>` in
  `base.html`, so every HTMX request on every page carries it
  automatically; confirmed working afterward.
- Verified end-to-end (dev server, real imported data, not mocked):
  all six routes return 200 for valid input and 404 for invalid
  lecture codes / exam ids; dashboard's "Today's Routine" correctly
  shows the real `2026-07-23` Chemistry class (`C-12`) from the imported
  dataset — the system clock happens to fall inside the imported
  routine's date range, so this exercised real "today" logic, not just
  the empty state (which was also verified by checking other dates
  render "No routine scheduled for today." — implicitly, since most
  dates in the range have no lecture); HTMX routine filtering (event
  type and subject) returns partial fragments (no `<html>` wrapper) with
  correctly filtered rows; HTMX progress toggle returns the updated row,
  persists after a full page reload, and creates exactly one `Progress`
  row per topic (verified in the shell). `manage.py check` and
  `makemigrations --check --dry-run` clean throughout.
- No database models, migrations, or CSV files were touched by this
  milestone.

### Milestone 4.1 — Resolve Remaining Importer Known Issues

Resolved the two importer workarounds flagged as Known Issues in
Milestone 3/3.1: the 31 skipped `LectureTopic` rows, and `Exam`'s
missing `exam_code`/`online_start`/`online_end` fields. Both required
small, targeted model changes rather than more importer logic, per this
milestone's explicit preference.

**Issue 1 — LectureTopic no longer skips any row (91/91 imported):**

- `routines/models.py: Lecture` — `lecture_date`, `day`, `title` are now
  optional (`lecture_date`: `null=True, blank=True`; `day`/`title`:
  `blank=True, default=""`). `start_time`/`end_time` were already
  optional since Milestone 3.1.
- `lectures/models.py: LectureTopic.chapter` — now `null=True,
  blank=True`.
- New `routines/services/csv/lecture_helpers.py: get_or_create_lecture()`
  — resolves a `Lecture` by `lecture_code`, creating a minimal
  ("virtual") one the first time a code with no `routine.csv` CLASS row
  is encountered. Only real, CSV-sourced values (`lecture_code`,
  `subject`) are set; `lecture_date`/`day`/`title`/`start_time`/
  `end_time` are left blank/`None` — nothing is fabricated. This is a
  real database fact ("this lecture code exists, with no scheduled
  session"), not a fake routine event.
- `lecture_topic_importer.py` rewritten: every row now resolves via
  `get_or_create_lecture()` — no more skip/orphan logic. `chapter`
  resolution: if the subject has zero `Chapter` rows at all (checked
  dynamically via `Chapter.objects.filter(subject=subject).exists()` —
  English/Bangla in this dataset, not hardcoded), `chapter=None`; import
  proceeds. If the subject **does** have chapters, the Bengali
  paper+chapter reference must still parse and resolve to a real
  `Chapter` — a failure there remains a hard error, since that's
  genuinely bad data for a subject that should have a valid reference,
  not an exemption case.
- `exam_importer.py`: `covered_lectures` entries also resolve via
  `get_or_create_lecture()` (previously exempted self-study/gap codes
  from a "must already exist" check — now every code always resolves to
  a real `Lecture`, so the exemption logic was removed rather than kept
  around it).
- **Result**: `import_csv` now reports `✓ Imported 91 lecture topics`
  (was 60/91 with 31 skipped). `Lecture` count went from 50 to 80 (50
  real + 30 "virtual" undated ones: 26 self-study English/Bangla lecture
  codes + 4 distinct lecture-06 gap codes — `M-06` has 2 topic rows but
  is one lecture code, so one `Lecture`, matching `26 + 4 = 30`).

**Issue 2 — Exam has dedicated fields, no more notes-parsing:**

- `routines/models.py: Exam` — added `exam_code` (`CharField, unique=True`),
  `online_start`, `online_end` (`DateField, null=True, blank=True`).
  `exam_code` replaces the old synthetic `(routine, exam_name,
  exam_date)` `update_or_create` lookup key — simpler and, unlike the
  old key, backed by a real database constraint.
- `exam_importer.py` rewritten: reads `exam_code`/`online_start`/
  `online_end` directly into their dedicated fields; **no longer writes
  anything into `notes`** (the finalized `exams.csv` has no `notes`
  column, so there's nothing to put there — "import exactly what exists
  in the dataset"). `parse_exam_notes()` (the Milestone 4 view-layer
  helper that re-parsed this out of `notes` for the Exam Detail page)
  was removed from `routines/views.py`, and `ExamDetailView`/
  `exams/detail.html` now read the dedicated fields directly.
- `routines/admin.py`: `Exam` upgraded from a bare
  `admin.site.register(Exam)` to an `ExamAdmin` with
  `list_display = ["exam_code", "exam_name", "exam_type", "exam_date",
  "online_start", "online_end"]`, `list_filter = ["exam_type"]`,
  `search_fields = ["exam_code", "exam_name"]`.

**Importer cleanup:**

- `routines/services/csv/utils.py`: removed `ALLOWED_NUMBERING_GAPS`
  and `is_allowed_gap_lecture()` — dead code once
  `get_or_create_lecture()` made the gap/self-study exemption checks
  that used them unnecessary.
- `lecture_topic_importer.py` and `exam_importer.py` no longer contain
  any self-study/gap-lecture special-casing — every lecture_code is
  simply resolved (or created), full stop.

**Milestone 4 view fixes required by the model change** (not asked for
directly, but necessary to keep Milestone 4's pages from breaking now
that undated `Lecture`s exist):

- `routines/views.py: RoutineListView._get_events()` now excludes
  `Lecture.objects.filter(lecture_date__isnull=False)` from the routine
  timeline — the view sorts events in Python by date
  (`events.sort(key=lambda e: e["date"])`), which raises `TypeError`
  comparing `None` to a real date; undated lectures also have no
  calendar slot to show in a chronological list anyway.
- `templates/lectures/detail.html`: falls back to `lecture_code` when
  `title` is blank; shows "Not scheduled (self-study / no live class)"
  instead of a blank date/day when `lecture_date` is `None`.
- `templates/lectures/_topic_row.html`: shows "—" instead of blank when
  `topic.chapter` is `None`.
- `templates/exams/detail.html`: covered-lecture rows now always
  resolve to a `Lecture` (real or virtual), so the old "self-study / not
  found" fallback branch is effectively dead code path-wise but was kept
  as a defensive fallback; added a small "(self-study / no live class)"
  tag next to undated lecture links instead.
- `lectures/views.py: LectureDetailView.get_context_data()`: the
  distinct-chapters list now skips `None` chapters (previously would
  have appended a stray `None` entry once per lecture with any
  chapter-less topic).

**Incidental documentation fix**: while updating the Lecture Model
Contract section for this milestone's changes, also corrected
`start_time`/`end_time` there to reflect Milestone 3.1's `null=True`
(that milestone's scope was `PROJECT_PROGRESS.md` only, so the contract
document was never updated for it until now).

**Migration notes** (`routines/migrations/0003_...py`,
`routines/migrations/0004_alter_exam_exam_code.py`,
`lectures/migrations/0002_alter_lecturetopic_chapter.py`): the
`Lecture`/`LectureTopic` field relaxations were safe, ordinary
`AlterField`s (loosening `NOT NULL` never conflicts with existing
populated rows). Adding `Exam.exam_code` as `unique=True` to an
already-populated table (15 rows from Milestone 4 testing) needed care:
migration `0004` first `AddField`s `exam_code` as nullable (no
interactive default prompt), then a hand-added `RunPython` step deletes
all existing `Exam` rows — safe, since `Exam` data is entirely
CSV-derived and never hand-entered, and the mandatory `import_csv`
re-run (this milestone's own verification step) fully and correctly
repopulates the table immediately afterward, this time with dedicated
fields instead of the old notes-parsing workaround — then `AlterField`
makes `exam_code` `unique=True` with no default needed, since the table
is empty at that point. Verified: `makemigrations --check --dry-run`
reports no changes after these edits, confirming the hand-crafted
migration fully matches the model state.

**Verification**: `manage.py makemigrations --check --dry-run` (clean,
both before and after hand-editing migration 0004), `migrate`,
`import_csv` (91/91 lecture topics, 0 skipped — only remaining skip
message is the pre-existing, unrelated orientation-row skip from
Milestone 3/4; re-ran a second time to confirm idempotency, identical
counts), `validate_datasets` (0 errors, 0 warnings — dataset untouched),
`manage.py check` (clean). Verified via the dev server + Django Admin:
`ExamAdmin` changelist shows the new columns with real data (e.g.
`WE-01`); a self-study lecture (`E-01`) and a lecture-06-gap lecture
(`P-06`) both render correctly at `/lecture/<code>/` with the new
"Not scheduled" fallback instead of a blank/broken page; all Milestone 4
routes still return 200.
- No CSV files were modified by this milestone.

### Milestone 5 — Study Planner & Analytics

Extended the dashboard and added four new analytics pages
(Subjects/Chapters/Lectures/Exam Readiness) on top of the existing,
now-stable database — no model changes. All calculations live in a new
`progress/services/` package (`analytics.py`, `dashboard.py`); views
only call services and render, per this milestone's explicit "no
business logic in templates" instruction.

**Pre-existing regression fixed first**: `ExamDetailView` and
`templates/exams/detail.html` still called the Milestone 3
`parse_exam_notes()` helper on `Exam.notes` even though Milestone 4.1
added dedicated `exam_code`/`online_start`/`online_end` fields and
stopped populating `notes` — so the Exam Detail page had silently
regressed to showing "Not specified" for every exam's online period
and omitting the exam code. `parse_exam_notes()` was removed;
`ExamDetailView`/`exams/detail.html` now read `exam.exam_code`/
`exam.online_start`/`exam.online_end` directly, as Milestone 4.1
intended. Verified via the dev server: `/exam/1/` now shows `WE-01`
and its real online period again.

**`progress/services.py` (single file) restructured into a package**
(`progress/services/__init__.py`, `analytics.py`, `dashboard.py`).
`__init__.py` re-exports the public functions so `from progress.services
import ...` still works; internal callers (`progress/views.py`,
`dashboard/views.py`) updated to import from the specific submodule.
`get_subject_completion_stats()` was replaced by
`get_subject_analytics()`, which also **fixes a latent bug**: the old
function grouped topics by `chapter__subject`, silently excluding every
topic whose `chapter` is `None` (English/Bangla self-study topics, made
possible by Milestone 4.1) from all subject-level stats. The new
version groups by `lecture__subject` instead — `Lecture.subject` is
always set — so subject totals now correctly include chapterless
topics (verified: the six subjects' `total_topics` sum to 91, matching
the known imported topic count).

**Analytics calculations** (`progress/services/analytics.py`) — all use
conditional aggregation (`annotate`/`Case`/`When`/`Sum`/`Count`), not
per-row Python loops, so each page issues a small, fixed number of
queries regardless of dataset size (verified: 1–2 queries per analytics
function, see Architectural Decisions):

- `get_subject_analytics(sort=...)` — total/completed/remaining/% per
  `Subject`, sortable by `name` (A–Z), `completion` (highest first), or
  `remaining` (most remaining first).
- `get_chapter_analytics(subject_code=...)` — total/completed/remaining/%
  per `Chapter`, optionally filtered to one subject.
- `get_lecture_analytics(subject_code=..., search=...)` — total/completed
  topics and % per `Lecture`, filterable by subject and a free-text
  search over `lecture_code`/`title`.
- `get_exam_readiness()` — per `Exam`, resolves `covered_lectures` (a
  JSON list of lecture codes, not a FK) against bulk-fetched
  lecture/topic completion stats to avoid one query pair per exam,
  computing covered lecture count, total/completed/remaining topics,
  and a readiness % mapped to a label + Tailwind badge class:
  90–100% "Ready" (emerald), 70–89% "Good" (blue), 40–69% "Needs Work"
  (amber), below 40% "High Risk" (red) — thresholds and colors exactly
  as specified.
- A topic counts as "completed" using the same definition established
  in Milestone 4 (all four `Progress` booleans `True`) — verified this
  stays consistent across dashboard stats, subject/chapter/lecture
  analytics, and exam readiness by toggling one topic's `Progress` in
  the shell and confirming all four moved together.

**Dashboard analytics + widgets** (`progress/services/dashboard.py`):

- `get_dashboard_stats()`: total/completed/remaining topics + overall
  %, total/completed lectures (a lecture counts as completed only if it
  has at least one topic and all of them are complete), total/upcoming
  exams, and days remaining until the next upcoming exam (`None` if
  none).
- `get_dashboard_widgets()`: Recent Activity (last 10 completed
  topics), Upcoming Exams (next 5), Most/Least Completed Subject
  (ignoring subjects with zero topics), Daily Progress (topics
  completed today, by `Progress.updated_at__date`).
- `DashboardView` (`dashboard/views.py`) now renders
  `templates/dashboard/_widgets.html` (stats + all widgets) inside
  `dashboard/index.html`, alongside the pre-existing "Today's
  Routine"/"Upcoming Lecture"/"Upcoming Exam" sections (unchanged, not
  part of this milestone's widget list).
- **HTMX widget refresh**: a new `DashboardWidgetsView`
  (`/widgets/`, name `dashboard-widgets`) re-renders just
  `_widgets.html`; a "Refresh" button on the dashboard
  (`hx-get`/`hx-target="#dashboard-widgets"`/`hx-swap="outerHTML"`)
  updates stats/widgets in place without a full page reload — useful
  after toggling progress on another page in another tab.

**Analytics pages** (`progress/views.py`, mounted at `/analytics/` via
new `progress/analytics_urls.py`, included from
`admission_helper/urls.py`):

```text
/analytics/subjects/   AnalyticsSubjectsView  — sort by name/completion/remaining
/analytics/chapters/   AnalyticsChaptersView  — filter by subject
/analytics/lectures/   AnalyticsLecturesView  — search + subject filter
/analytics/exams/      AnalyticsExamsView     — exam readiness, color-coded
```

Each view follows the same `get_template_names()` + `request.htmx`
pattern established by `RoutineListView` in Milestone 4: a `<select>`/
`<input>` filter form `hx-get`s the same URL on `change` (search box
also on `keyup changed delay:300ms`) and swaps a results `<div>`; the
view returns just the partial table template for HTMX requests, the
full page otherwise. A shared `templates/analytics/_nav.html` tab strip
(Subjects/Chapters/Lectures/Exam Readiness, active-tab highlighted via
`request.path`) is included at the top of all four pages. A new
"Analytics" link was added to `templates/base.html`'s nav (highlighted
whenever `request.path` contains `/analytics/`).

**Templates** (`templates/analytics/`): `subjects.html` (card grid,
progress bar + %/remaining per subject), `chapters.html` (table:
Subject/Paper/Chapter/Topics/Completed/Remaining/Completion, subject
filter), `lectures.html` (table: Lecture Code/Subject/Total
Topics/Completed Topics/Completion, search + subject filter),
`exams.html` (table: Title/Date/Covered Lectures/Covered
Topics/Completed/Remaining/Readiness badge). All extend `base.html` and
use the existing card/progress-bar/badge/table Tailwind patterns
already established in `dashboard/index.html`, `routine/_table.html`,
and `progress/overview.html` — no new visual language introduced.

**Verified**: `manage.py check` clean; `makemigrations --check
--dry-run` reports "No changes detected" (no model changes made, as
required); all nine routes (`/`, four `/analytics/...` pages, their
HTMX-filtered variants, `/progress/`, `/exam/1/`) return 200 via the dev
server; each analytics service function checked with
`django.db.connection.queries` under `DEBUG=True` — 1–2 queries each,
`get_dashboard_stats()` at 7 (four independent small aggregate/count
queries plus their sub-parts), none scaling with row count; toggling a
`Progress` row in the shell and re-running every analytics function
confirmed completion counts/percentages update consistently everywhere
(dashboard stats, subject row, lecture row, exam readiness row all
moved together, then reverted cleanly after deleting the test
`Progress` row).
- No database models, migrations, importer code, or CSV files were
  touched by this milestone.

### Milestone 6 — Testing, Hardening & UX Polish

Not a new-feature milestone, per its own explicit framing: a full
codebase audit, a substantial automated test suite (0 tests → 85
passing), query-count verification, HTMX UX polish, and friendlier
error handling. No database models were changed.

**Phase 1 — Audit findings** (full list; each item's disposition
noted):

1. **`ExamDetailView`/`exams/detail.html` regression** — already found
   and fixed at the start of Milestone 5 (see that milestone's entry);
   re-verified still fixed, no further action.
2. **`progress/services/dashboard.py` imported `_completed_case`
   (leading-underscore "private" name) across module boundaries** from
   `analytics.py` — cosmetic inconsistency, not a bug. **Fixed**:
   renamed to `completed_case` (both are genuinely part of
   `analytics.py`'s public surface, used by both sibling modules).
3. **Unused `from lectures.models import LectureTopic` in
   `progress/services/analytics.py`** — referenced only inside a
   docstring, never in code. **Fixed**: removed.
4. **`RoutineListView._get_events()` was view-layer business logic**
   (merging `Lecture`+`Exam` into a unified, filtered, sorted event
   list) — flagged by the audit's "views doing business logic" /
   "opportunities for service extraction" categories, and made the
   filtering logic hard to unit-test without a full request/response
   cycle. **Fixed**: extracted verbatim (no behavior change) into
   `routines/services/events.py: get_routine_events(event_type,
   subject_code)`; `RoutineListView` now just calls it. This is also
   what made `RoutineEventsServiceTests` (5 tests) possible without
   spinning up the view.
5. **Bengali YYA-normalization logic (`normalize_bengali`,
   `CHAPTER_REF_RE`, `LECTURE_CODE_RE`) is duplicated between
   `core/management/commands/validate_datasets.py` and
   `routines/services/csv/utils.py`.** Investigated whether to merge:
   **left as intentional duplication, not fixed** — this split was a
   deliberate Milestone 3 architectural decision (validator lives in
   `core` specifically so it doesn't presuppose the importer's later
   module layout, and stays usable standalone before/without an
   importer existing). Merging now would require the read-only
   validator to import from the transactional importer's package (or
   vice versa), coupling two components that were deliberately kept
   independent. Documented here instead of silently merged, per this
   milestone's "do not modify behavior unless necessary" instruction.
6. **`ALLOWED_NUMBERING_GAPS`/`is_allowed_gap_lecture()` still exist in
   `validate_datasets.py`** — this looked like the same dead code
   removed from the importer in Milestone 4.1, but it is not dead: the
   validator is a separate, independent tool (see #5) that still needs
   its own gap-exemption logic for its own cross-file checks. **No
   action** — correctly still in use where it lives.
7. **Missing indexes**: reviewed every model's filter/annotate paths
   (`Progress`'s four boolean fields, `Exam.covered_lectures` JSON
   list) against the current dataset scale (~91 topics, ~80 lectures,
   15 exams). **No index added** — every current query already hits an
   existing index (FK auto-indexes, `Lecture.lecture_code`,
   `Lecture.lecture_date`, `Exam.exam_date`/`exam_type`,
   `Progress.updated_at`) and table sizes are small enough that a
   composite boolean index on `Progress` would add write overhead for
   no measurable read benefit at this scale. Flagged here rather than
   speculatively added, consistent with "do not modify behavior unless
   necessary."
8. **Analytics/dashboard pages already avoid N+1** (established in
   Milestone 5) — re-verified with `CaptureQueriesContext`, still true
   (see Phase 3 below). No action needed.
9. **Empty-state handling in all four analytics pages, the dashboard,
   and `progress/overview.html`** — re-verified all handle zero
   subjects/chapters/lectures/exams/topics without crashing (percentage
   helper already guards divide-by-zero; templates already have
   `{% empty %}` blocks). No action needed; covered by new
   `test_no_data_widgets_dont_crash`, `test_no_exams_returns_empty_list`,
   `test_empty_state_when_no_exams`, `test_empty_database_does_not_crash`.
10. **`core`, `dashboard`, `reminders`, `subjects` apps' default
    `models.py`/`views.py`/`admin.py` stub files are untouched
    scaffolding** (from Milestone 1) — not dead code to remove, since
    `subjects`/`reminders` are intentionally still-unbuilt feature areas
    per the Pending Milestones list, and `core` legitimately only hosts
    the validator command. No action.
11. **Naming**: `progress/services/dashboard.py`'s
    `COMPLETED_TOPIC_FILTER` dict and `analytics.py`'s `completed_case()`
    Case/When both express "all four Progress booleans true", in two
    different forms (a plain filter dict vs. a SQL-level annotation).
    Considered unifying into one representation: **left as two forms,
    not fixed** — they serve genuinely different query shapes
    (`Progress.objects.filter(**COMPLETED_TOPIC_FILTER)` for a direct
    count vs. `completed_case()` for annotating a *different* model via
    a join prefix) and forcing one into the other would either lose the
    direct-filter simplicity or require duplicating the join-prefix
    logic. Documented rather than force-merged.

**Phase 2 — Automated tests** (0 → 85 tests, all passing;
`core/test_utils.py: build_sample_dataset()` builds one shared,
hand-computed fixture - 2 subjects (one with chapters, one self-study
with none), 3 chapters, 4 lectures (2 dated, 2 undated), 5 topics with
deliberately mixed completion states, 2 exams - reused by every app's
tests so expected values are derived once and never drift):

- `routines/tests.py` (22 tests): every CSV importer stage
  (`SubjectImporter` standalone: import/idempotency/duplicate-code/
  missing-column/missing-file; a full 5-stage pipeline: import,
  re-run idempotency, self-study-subject undated-lecture creation,
  bad-row-rolls-back-the-whole-stage), `get_routine_events()` (merge,
  event_type filter, subject filter, undated-lecture exclusion),
  `RoutineListView` (full page vs. HTMX partial, filters),
  `ExamDetailView` (dedicated fields render correctly, undated covered
  lecture shows the self-study tag, unknown id 404s, query count).
  Importer tests build tiny CSV fixtures in a `tempfile.TemporaryDirectory()`
  — the real project-root CSVs are never read or written by any test.
- `progress/tests.py` (52 tests): all four analytics calculations
  (`get_subject_analytics`, `get_chapter_analytics`,
  `get_lecture_analytics`, `get_exam_readiness`) against the known
  fixture's hand-computed totals/percentages, every sort mode, every
  filter, `readiness_label()`'s exact threshold boundaries (39.9/40,
  69.9/70, 89.9/90), an exam covering an unknown/deleted lecture code
  (ignored, not crashed); all four analytics *views* (full page vs.
  HTMX partial, sort/filter query params, pagination context); the
  dashboard service layer (`get_completion_stats`, lecture/exam stats,
  `get_daily_progress_count` including a "not today" exclusion case,
  all four widgets, zero-topic-subjects excluded from
  most/least-completed); `ProgressToggleView` (creates vs. flips vs.
  never-duplicates a `Progress` row, rejects an unknown field/topic,
  rejects GET); `ProgressOverviewView`.
- `lectures/tests.py` (6 tests): dated vs. undated lecture rendering,
  unknown code 404, chapter de-duplication (including the `None`-chapter
  skip), query count.
- `dashboard/tests.py` (5 tests): full render with stats/widgets, empty
  database doesn't crash, the HTMX widgets-refresh endpoint returns a
  partial and reflects a `Progress` change made after the initial page
  load.
- Every test builds its own data (via `build_sample_dataset()` or, for
  the importer, its own temp CSVs) — none reads or depends on the real
  `subjects.csv`/`chapters.csv`/`routine.csv`/`lecture_topics.csv`/
  `exams.csv` at the project root, so the test suite can never mutate
  or be broken by dataset changes, and vice versa.

**Phase 3 — Performance verification**: `CaptureQueriesContext` query
counts confirmed against the real, imported dataset (not the test
fixture) — see the Query Count Summary below. All stayed small and
fixed, consistent with Milestone 5's original budget; no unnecessary
queries were found, so nothing needed removing.

**Phase 4 — HTMX UX polish**:

- **Global loading indicator**: a thin `#page-indicator` bar
  (`.htmx-indicator`, styled via Tailwind) added to `base.html`,
  wired via `hx-indicator="#page-indicator"` on every HTMX-triggering
  element that didn't already have one (dashboard refresh button,
  routine list filter form + pagination links, all four analytics
  filter forms + the new chapter/lecture pagination links). htmx.org
  injects the required `.htmx-indicator`/`.htmx-request` CSS itself, so
  no extra stylesheet was needed.
- **Pagination added to Chapter and Lecture analytics** (previously
  unpaginated — 75 chapters rendered as one long table). Reuses the
  exact `Paginator` + `{% querystring_page %}` pattern already
  established by `RoutineListView` in Milestone 4, via a new shared
  `templates/analytics/partials/_pagination.html` (parameterized by a
  `target` div id) rather than copy-pasting the pagination markup a
  third time. Subjects (6 rows) and Exam Readiness (15 rows) were left
  unpaginated — genuinely no benefit yet at that size, and adding it
  preemptively would be unrequested scope for this milestone's "not
  about adding major new features" framing.
- **Filter/sort state preservation during refresh**: audited, found
  already correct — every filter form lives *outside* the HTMX swap
  target (`#subject-results`/`#chapter-results`/etc.), so an HTMX swap
  only ever replaces the results table, never the form controls holding
  the user's current selection. No code change needed; documented as a
  verified property, not assumed.
- **Empty states**: audited, found already present on every page (see
  Phase 1, item 9). No change needed.

**Phase 5 — Error handling**:

- **Missing CSV file during import** previously raised a raw, unhandled
  `FileNotFoundError` with a Python traceback. **Fixed**:
  `BaseImporter.read()` (`routines/services/csv/base_importer.py`) now
  checks `self.path.exists()` first and raises the same
  `ImportValidationError` shape used for every other importer failure
  (`File:`/`Row: -`/`Reason: File is missing...`/`Directory:`),
  consistent with every other error the importer already produces.
  Covered by `test_missing_file_raises_friendly_error`.
- **Custom `404.html`/`500.html`** added at the template root.
  `404.html` extends `base.html` (full nav/branding, "back to
  Dashboard" link) since Django renders it with a normal
  request/context. `500.html` is deliberately a small, standalone,
  self-contained HTML page (no `{% extends %}`, no context processors
  relied on) — Django renders the 500 template with an empty `Context`
  (no `request`, no context processors), so depending on `base.html`
  here would risk a second failure while already handling the first
  one. Both only take effect in production (`DEBUG=False`); this
  project runs with `DEBUG=True` in development, so Django's normal
  debug error pages are unaffected day-to-day — this is forward-looking
  production hardening, not a change to current dev behavior.
- **Deleted lectures / invalid URLs / graceful empty analytics /
  importer validation failures**: all audited (Phase 1, items 8-9) and
  found already handled correctly by existing code from Milestones 3-5
  — no changes needed, now backed by explicit regression tests instead
  of only having been manually spot-checked.

- No CSV files, database models, or migrations were touched by this
  milestone.

### Milestone 7 — Authentication & User Management

Introduced Django's built-in authentication and made `Progress` (and
everything derived from it - analytics, dashboard stats, widgets)
user-specific. `Subject`/`Chapter`/`Routine`/`Lecture`/`LectureTopic`/
`Exam` remain shared, global curriculum data - only `Progress`
(explicitly "Application"-owned per the Database Model Contract's Data
Ownership table, i.e. per-student data, not CSV-derived) needed an
owner. No CSV files, importer, or custom user model were touched.

**Authentication** (`django.contrib.auth`, no reinvention):

- `django.contrib.auth.urls` included under `/accounts/` in
  `admission_helper/urls.py`, providing `login`, `logout`,
  `password_change`, `password_change_done`, `password_reset`,
  `password_reset_done`, `password_reset_confirm`,
  `password_reset_complete` for free via Django's own views.
- `/accounts/login/` is overridden with an explicit `path()` *before*
  the `include()` (Django's resolver matches the first pattern), using
  `LoginView.as_view(redirect_authenticated_user=True)` — the only
  customization needed, since the milestone's "redirect authenticated
  users to the dashboard" requirement isn't `LoginView`'s default
  behavior. Every other auth view (`logout`, password change/reset) is
  used completely unmodified.
- `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'dashboard'`,
  `LOGOUT_REDIRECT_URL = 'login'` added to `settings.py` — `LogoutView`
  is POST-only as of modern Django (CSRF-safe by default), matches the
  nav's new `<form method="post">` logout button.
- `EMAIL_BACKEND` set to the console backend so the password-reset
  flow is fully exercisable in development without real SMTP
  credentials (the milestone calls password reset "template-ready",
  not requiring real delivery/verification) — the email is printed to
  the runserver console instead of failing to send.
- `registration/password_reset_email.html`/`password_reset_subject.txt`
  were **not** added — Django's own `django.contrib.admin` app (already
  in `INSTALLED_APPS`) ships default templates for both, discovered
  automatically via `APP_DIRS=True`; the milestone's required-file list
  doesn't ask for them, and they weren't otherwise needed.

**Registration** (`/accounts/register/`, new — not part of
`django.contrib.auth.urls`, which deliberately excludes registration):

- `core/forms.py: RegistrationForm(UserCreationForm)` adds a required
  `email` field to the stock `username`/`password1`/`password2`.
- `core/views.py: RegisterView(CreateView)` — on success, logs the new
  user in immediately (`django.contrib.auth.login()`) and redirects to
  the dashboard, per the milestone's "Automatically log the user in
  after successful registration."
- Lives in the `core` app (not a new `accounts` app) — consistent with
  the Milestone 5 precedent of not creating a new Django app for a
  feature that fits into an existing one; `core` already hosts
  general, non-model-owning utilities (`validate_datasets`).

**Progress ownership** (`progress/models.py: Progress`):

- Added `user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE,
  related_name="progress_records")`.
- `lecture_topic` changed from `OneToOneField` to `ForeignKey` (same
  `on_delete=CASCADE`, `related_name` changed from `"progress"` to
  `"progress_records"`) — many users can now each have their own
  `Progress` row for the same topic, so the field-level one-to-one
  uniqueness no longer applies.
- New `Meta.constraints`: `UniqueConstraint(fields=["user",
  "lecture_topic"], name="unique_user_lecture_topic")` — this is what
  now enforces "at most one Progress row per user per topic" (the job
  the old `OneToOneField` used to do).
- Migration `progress/migrations/0002_progress_user_alter_progress_
  lecture_topic_and_more.py`: generated by `makemigrations` (interactive
  prompt answered with a one-off default of `1`, matching the
  Milestone 3.0 precedent — confirmed via the Django shell beforehand
  that the `Progress` table had 0 rows in this environment, so the
  placeholder default never actually applies to a real row).

**User-aware services** (`progress/services/analytics.py`,
`progress/services/dashboard.py`) — every function that touches
`Progress`, directly or via a join, now takes a `user` argument:

- `get_subject_analytics(user, sort=...)`, `get_chapter_analytics(user,
  subject_code=...)`, `get_lecture_analytics(user, subject_code=...,
  search=...)`, `get_exam_readiness(user)`, `get_completion_stats(user)`,
  `get_lecture_stats(user)`, `get_dashboard_stats(user)`,
  `get_recent_activity(user)`, `get_subject_extremes(user)`,
  `get_daily_progress_count(user)`, `get_dashboard_widgets(user)`.
  `get_exam_stats()`/`get_upcoming_exams_widget()` deliberately do
  **not** take a `user` - exam scheduling is shared curriculum data,
  identical for every user, not owned by anyone.
- `completed_case(user, join_prefix="")` (the shared Case/When helper
  behind every annotate-based completion count) now also filters the
  join on `<prefix>progress_records__user = user`, alongside the four
  boolean fields. This is the one piece of real query-logic change in
  this milestone (see Architectural Decisions for why it's still
  correct despite the join no longer being to-one).
- No analytics logic beyond adding this user filter changed — same
  thresholds, same percentage rounding, same sort orders, same N+1
  avoidance via `annotate`/`Case`/`When`/`Count(..., distinct=True)`.

**Route protection** (`LoginRequiredMixin` added to every study-facing
CBV; `ProgressToggleView` — a plain `View`, not generic — also mixes it
in):

```text
DashboardView, DashboardWidgetsView          dashboard/views.py
RoutineListView, ExamDetailView              routines/views.py
LectureDetailView                            lectures/views.py
ProgressOverviewView, ProgressToggleView,     progress/views.py
AnalyticsSubjectsView, AnalyticsChaptersView,
AnalyticsLecturesView, AnalyticsExamsView
```

An anonymous visitor to any of these is redirected to `LOGIN_URL` with
`?next=<original path>` (Django's default `LoginRequiredMixin`
behavior - no custom redirect logic written). Django Admin is
completely unaffected - it has always had its own separate
authentication (`admin:login`), unrelated to and untouched by this
milestone's `django.contrib.auth.urls` front-end login.

**Navigation** (`templates/base.html`): the whole nav `<ul>` is now
wrapped in `{% if user.is_authenticated %}...{% else %}...{% endif %}`
— authenticated users see Dashboard/Routine/Exams/Progress/Analytics
plus their username and a Logout button (a `<form method="post">`,
since `LogoutView` is POST-only); anonymous visitors see only
Login/Register. `django.contrib.auth.context_processors.auth` (already
present in `TEMPLATES` since Milestone 1's default scaffolding) is what
makes `user` available in every template with no per-view wiring.

**Admin** (`progress/admin.py: ProgressAdmin`): upgraded from a bare
`admin.site.register(Progress)` to `list_display = ["user",
"lecture_topic", "completion_status", "updated_at"]` (`completion_status`
a computed `@admin.display(boolean=True)` method - all four study-stage
booleans true), `list_filter = ["user", "lecture_topic__lecture__subject"]`
(filtering by subject through the FK chain since `Progress` has no
direct subject field), `search_fields = ["user__username",
"lecture_topic__topic"]`.

**Tests** (0 → 119, up from Milestone 6's 85 — 34 new/rewritten for
this milestone): `core/tests.py` (new) covers registration (valid
signup logs in + redirects; password mismatch and duplicate username
both rejected without creating a user), login/logout (valid/invalid
credentials, already-authenticated user redirected away from the login
page, logout redirects to login and revokes access), route protection
(every protected URL redirects an anonymous client, admin login is
unaffected), and end-to-end cross-user isolation (two real users via
`self.client.force_login()`: progress overview, dashboard statistics,
and the subjects analytics page all differ per user; toggling progress
as one user never changes what the other user sees). Every existing
app's test file (`progress`, `routines`, `lectures`, `dashboard`) was
updated to log a user in before hitting a protected view and to pass
`user` into every analytics/dashboard service call; several gained a
dedicated "second user sees zero completion" test. `core/test_utils.py`
gained `create_user()` and `build_sample_dataset(user=None)` (creates
and returns a default "student1" test user, `data["user"]`, if none is
given) so every app's tests keep sharing one fixture builder rather
than duplicating user-creation logic.

**Verification** (this milestone's own required steps, all run and
passing): `manage.py test` — **119 tests, all passing** (takes ~2-2.5
minutes locally, up from Milestone 6's sub-second 85 — real PBKDF2
password hashing on every `User.objects.create_user()` call across
~30+ users created by the test suite; a deliberate trade-off, see
Architectural Decisions); `manage.py check` clean; `makemigrations
--check --dry-run` reports "No changes detected". Manually verified
against the real imported dataset via the dev server: registered two
real users ("alice", "bob") through `/accounts/register/`, confirmed
both land on the dashboard immediately (auto-login), toggled one
`LectureTopic`'s `class_done` as alice, and confirmed in the database
that exactly one `Progress` row exists for that topic (owned by alice)
and bob's `/progress/` overview still reports 0 completed - real,
end-to-end proof of isolation, not just the test suite's fixture data.
Anonymous requests to `/` correctly redirect to
`/accounts/login/?next=/`.

- No CSV files, importer code, or non-`Progress` models were touched by
  this milestone.

### Milestone 8 — Advanced Analytics

Turned the existing "how much have I completed?" analytics into a
"study advisor": what to study next, which subjects/chapters/lectures
need attention, and whether the user is actually ready for the next
exam - not just how much of it is done. Analytics-only, per this
milestone's explicit scope: nothing here schedules revisions, writes
to any model, or stores a computed value - every number is
recalculated on demand, exactly like every prior analytics milestone.
No models, migrations, importer code, or CSV files were touched.

**New service** `progress/services/advanced_analytics.py` - kept
entirely separate from `analytics.py`/`dashboard.py` (which remain
focused on basic completion metrics, per this milestone's explicit
instruction not to replace them):

- **Subject insights**: `get_subject_insights(user)` - strongest/
  weakest subject (ties broken by completed count, then total topic
  count, not just raw percentage) plus a full ranked list with rank
  numbers; `get_subject_completion_trend(user)` - today/7-day/30-day
  completed-topic counts per subject; `get_average_completion_speed(user)`
  - topics completed per *active* study day (days with zero activity
    don't drag the average down).
- **Chapter insights**: `get_priority_chapters(user)` - unfinished
  chapters ranked highest first, with a priority bonus for chapters
  whose topics appear in an *upcoming* exam's coverage;
  `get_neglected_chapters(user, stale_days=14)` - unfinished chapters
  with no activity (of any kind, not just completions) in the given
  window; `get_most_unfinished_chapters(user)`/
  `get_most_completed_chapters(user)` - straightforward re-sorts of the
  existing `get_chapter_analytics()` rows by remaining/percentage.
- **Lecture insights**: `get_longest_untouched_lectures(user)` - zero-
  completion lectures, oldest-scheduled first (undated self-study/gap
  lectures sort last - no time reference to rank them "how long
  untouched"); `get_recently_completed_lectures(user)` - fully-done
  lectures, most recently finished first; `get_backlog_lectures(user)`
  - largest unfinished-topic backlog regardless of recency (the volume
  counterpart to "longest untouched," which is about dormancy/time);
  `get_study_streak(user)` - current and longest consecutive-study-day
  streaks, from distinct `Progress.updated_at` dates.
- **Trend/visualization data**: `get_daily_completion_trend(user, days=35)`
  (zero-filled per-day counts - the calendar heatmap's data source),
  `get_weekly_distribution(user)` (per-weekday totals via
  `ExtractWeekDay`), `get_monthly_completion_timeline(user, months=6)`
  (per-month totals via `TruncMonth`) - each a single annotated query.
- **Exam insights**: `get_exam_insights(user)` extends (does not
  replace) `analytics.py`'s `get_exam_readiness()` - adds a blended
  0-100 `readiness_score` (60% topic completion + 40% lecture
  completion - see Architectural Decisions for why), a coverage gap
  (`missing_percentage`), remaining workload (`remaining_topics`,
  already present but now framed as "workload"), and a `confidence_label`
  reusing the exact same `readiness_label()` thresholds/badge classes
  `analytics.py` already defines (Ready/Good/Needs Work/High Risk) -
  no new thresholds invented. `get_next_exam_insight(user)` picks the
  single nearest upcoming exam for the dashboard's "Ready For Exam"
  widget.
- **Shared with `analytics.py`, not duplicated**: `completed_case()`
  gained an optional `since=` date parameter (backward-compatible -
  every existing call site is unaffected) so completion-trend windows
  can be computed as multiple `Sum()` annotations in one query instead
  of one query per window. A new `get_lecture_completion_stats(user,
  lecture_codes)` helper was extracted out of `get_exam_readiness()`'s
  inline bulk-fetch block and is now called by both
  `get_exam_readiness()` and `get_exam_insights()` - one shared
  implementation of "bulk lecture-code -> topic completion stats"
  instead of two copies of the same query pattern.
- **`get_chapter_analytics()`/`get_lecture_analytics()`-reusing
  functions accept an optional `rows=` parameter** (`get_priority_chapters`,
  `get_most_unfinished_chapters`, `get_most_completed_chapters`,
  `get_longest_untouched_lectures`, `get_backlog_lectures`) - when a
  caller (the Insights page) already fetched the base rows once, it
  passes them in and the function skips its own redundant query,
  rather than each insight independently re-querying the same
  chapter/lecture completion data.
- **`get_lecture_analytics()` gained a `remaining` key** (`total -
  completed`), matching the key `get_subject_analytics()`/
  `get_chapter_analytics()` already exposed - a small additive gap-fill,
  not a behavior change, needed by the new backlog/untouched-lecture
  insights.

**Dashboard widgets** (`progress/services/advanced_analytics.py:
get_advanced_dashboard_widgets(user)`, called by both `DashboardView`
and `DashboardWidgetsView` alongside the existing, unchanged
`get_dashboard_widgets()`): a new "Study Advisor" section on the
dashboard (`templates/dashboard/_widgets.html`) with Study Streak,
Priority Chapter, Longest Untouched Lecture, and Ready For Exam cards,
plus a "View full insights" link to the new page. Recent Activity/
Today's Completion/Upcoming Exams were already on the dashboard since
Milestone 5 and needed no changes; Strongest/Weakest Subject are
already served by the existing Most/Least Completed Subject widgets
(same concept, kept as-is rather than duplicated - see Architectural
Decisions).

**New page** `/analytics/insights/` (`AnalyticsInsightsView`,
`templates/analytics/insights.html` + `partials/_insights.html`),
added to the shared `analytics/_nav.html` tab strip as the first tab
("Reuse the existing analytics navigation," per this milestone's
instruction) - login-protected like every other analytics page, with
an HTMX "Refresh" button (`hx-get` swaps `#insights-content`, matching
the dashboard's existing refresh pattern) and the same
`get_template_names()`/`request.htmx` partial-vs-full-page pattern
every analytics view has used since Milestone 5. One page renders all
of Subject Ranking + Completion Trend, the four Chapter Insight lists,
the three Lecture Insight lists, the Study Heatmap/Weekly
Distribution/Monthly Timeline visualizations, and the extended Exam
Readiness cards - reusing the exact progress-bar/badge/card Tailwind
patterns already established across the app, no new visual language.

**CSS-only visualizations** (no JavaScript, no chart library, per this
milestone's explicit "Do NOT introduce JavaScript chart libraries"):
progress bars and comparison bars reuse the existing `bg-gray-200`
track + `bg-emerald-600` fill pattern from every prior analytics page;
the **study heatmap** is a `grid-cols-7` of plain `<div>` cells shaded
by a 4-level intensity class (`bg-gray-100`/`emerald-200`/`emerald-400`/
`emerald-600`, thresholds computed server-side in
`AnalyticsInsightsView._daily_trend_with_levels()` - presentational
bucketing, not an analytics calculation); the **weekly/monthly bar
charts** are flexbox columns whose `height: N%` is computed server-side
as "value relative to the max in this series" (`_scale_to_percent()`
in `progress/views.py`) - again presentational scaling for the bars,
not a new metric.

**Query budget**: individual insight functions stay at 1-3 queries each
(verified via `CaptureQueriesContext` in tests - see Testing below);
the full Insights page, which renders all ~15 insight categories on
one page, measures at **18 queries** against the real dataset - close
to but slightly over this milestone's own "<=15" target for analytics
pages, an accepted, documented tradeoff for a genuinely comprehensive
single-page dashboard rather than an artificially fragmented one (see
Architectural Decisions). The Dashboard, which already sat well above
its own "<=10" target before this milestone even started (16 queries,
per Milestone 6's own measurement), now measures **26 queries** with
the 4 new "Study Advisor" widgets added - still a small, fixed number
that does **not** scale with row count (re-verified with a new
`test_query_count_does_not_scale_with_extra_data` test that adds 50
extra topics and asserts an identical query count before/after). See
Testing and Architectural Decisions for the full accounting and the
reasoning for not chasing the numeric target at the cost of either
correctness or splitting a single coherent page into several thinner
ones.

**Tests**: 119 → **157**, all passing (38 new, all in `progress/tests.py`
and `dashboard/tests.py` - no new app was created for this milestone's
tests, consistent with keeping insights inside the `progress` app).
Covers: strongest/weakest subject (including the tie-break rule and
the "no topics at all" edge case), subject ranking order and rank
numbers, completion trend counts, average completion speed (including
the zero-active-days case), priority chapter ranking (including the
`rows=` reuse path's reduced query count), neglected-chapter detection
(both the "recently touched, correctly excluded" and "genuinely stale,
correctly included" cases - the latter by aging `Progress.updated_at`
via `.update()` to bypass `auto_now`), most-unfinished/most-completed
chapter ordering, longest-untouched-lecture ordering (dated-before-
undated), recently-completed-lecture ordering, backlog-lecture
ordering, study streak (single-day, multi-day-with-a-break, and
zero-activity cases), the daily/weekly/monthly trend data sources
(zero-fill, correct totals, correct bucket counts), the exam readiness
score's exact blended-percentage math (hand-verified against the
fixture: 60%&times;50% + 40%&times;33.3% = 43.3), coverage gap and
remaining-workload fields, the "next upcoming exam" picker, dashboard
widgets (all expected keys present, both dashboard views render them),
the Insights page (full page vs. HTMX partial, every context key
present, anonymous redirect), and two-user isolation re-verified across
every new function (a second user sees zero completion/streak/
readiness everywhere, never the first user's data).

**Verification**: `manage.py test` - 157/157 passing; `manage.py check`
clean; `makemigrations --check --dry-run` reports "No changes detected"
(no model changes, as required). Manually verified against the real
imported dataset via the dev server, logged in as the "alice" account
created during Milestone 7's verification: `/analytics/insights/`
renders every section (Strongest/Weakest Subject, Study Streak,
Highest Priority Chapters, Neglected Chapters, Study Heatmap, Weekly
Study Distribution, Monthly Completion Timeline, Exam Readiness
Insights) with real data, the HTMX partial request returns no `<html>`
wrapper, and the dashboard's new "Study Advisor" section renders
alongside the pre-existing widgets without disturbing them.

- No CSV files, importer code, or database models were touched by this
  milestone.

### Milestone 9 — Revision System

Introduced spaced revision as the second core workflow, on top of the
existing one: **Lecture → Progress → Revision Queue → Revision
History → Exam Ready**. Deterministic only, per this milestone's
explicit design goal - every due date comes from fixed interval
constants, never AI or randomness; no notifications/reminders and no
background jobs (both explicitly deferred to a later milestone).

**New models** (`progress/models.py`):

- `RevisionSchedule` - one user's revision stage (First/Second/Final)
  for one fully-completed `Lecture`. References `Lecture` directly, not
  `LectureTopic`/`Chapter` - a lecture's topics collectively define
  "what to revise," so no lecture/topic data is duplicated here (per
  this milestone's explicit "Do NOT duplicate lecture/topic data").
  `(user, lecture, revision_level)` is a `UniqueConstraint` - this is
  what actually prevents duplicate schedules, not an application-level
  check alone (see Architectural Decisions for why both exist).
- `RevisionHistory` - an immutable, append-only completion record.
  Never deleted or edited once written; `RevisionSchedule.completed_at`
  reflects only the current state, this table is the durable trail.
- Migration `progress/migrations/0003_revisionschedule_revisionhistory_and_more.py`
  - both are brand-new tables, no existing-data migration concerns, no
  interactive prompts needed.

**Centralized scheduling configuration**
(`progress/services/revision.py: REVISION_INTERVALS`):

```text
Level 1 (First Revision):  completion_date + 1 day
Level 2 (Second Revision): Level 1's due date + 3 days
Level 3 (Final Revision):  Level 2's due date + 7 days
```

A single dict keyed by `RevisionSchedule.Level`, exactly as this
milestone asked ("Intervals should be centralized as configuration
constants for future adjustment") - changing the cadence app-wide means
editing three timedeltas in one place.

**Automatic schedule creation** (`ensure_revision_schedule(user,
lecture, completion_date=None)`): checks `is_lecture_completed(user,
lecture)` (every one of the lecture's topics fully done by that user -
two small, single-lecture-scoped queries, not a table scan), checks no
schedule already exists for `(user, lecture)`, then `bulk_create()`s
all three stages inside `transaction.atomic()`. A `try/except
IntegrityError` around the create (not just the existence check)
catches the race where two concurrent requests both pass the
existence check before either commits - the `UniqueConstraint` is the
real guarantee, the existence check is just the fast common-case path.
Called from `ProgressToggleView` after every save (Milestone 9's
actual trigger point - not a signal, not a background job, an explicit
service-layer call inline in the same request/response cycle that
completed the lecture).

**Revision Queue** (`/revision/`, `RevisionQueueView`): Due Today /
Overdue / Upcoming / Completed, computed by fetching all of a user's
`RevisionSchedule` rows in one query (`select_related("lecture",
"lecture__subject")`) and bucketing in Python by comparing `due_date`
to today - filterable by subject/status/revision level, all via the
same `get_template_names()`/`request.htmx` HTMX partial pattern every
other list page in this app already uses (routine list since
Milestone 4, all four analytics pages since Milestone 5/8).

**Revision Detail** (`/revision/<id>/`, `RevisionDetailView`): lecture,
subject, revision level, due date, the lecture's topics (via
`lecture.topics`, never duplicated onto the schedule itself), and this
schedule's `RevisionHistory` entries. A "Mark Complete" button
(HTMX `hx-post` to `/revision/<id>/complete/`, target `#revision-detail`,
`hx-swap="innerHTML"`) appears only while the schedule is still
pending.

**Revision Completion** (`RevisionCompleteView`,
`complete_revision(user, schedule_id, notes="")`): looked up by
`(pk, user=user)` together - a schedule belonging to another user
simply doesn't exist from this query's perspective, so it 404s rather
than leaking a "yes it exists, but you can't touch it" response.
Updates `status`/`completed_at` and creates exactly one
`RevisionHistory` row; completing an already-completed schedule is a
no-op (returns the schedule unchanged, doesn't create a second history
entry) - the one-way "mark complete" workflow this milestone asked
for, not a toggle. Completed schedules are never deleted.

**Exam Ready** (`is_lecture_exam_ready(user, lecture)` /
`get_exam_ready_lecture_codes(user)`): a lecture is Exam Ready only
when it's fully completed **and** all three revision levels are
completed - exactly this milestone's four-checkbox definition. The
bulk version (`get_exam_ready_lecture_codes`) is one annotated query
(`Count("revision_level", distinct=True) == 3` per lecture, grouped)
plus one small id→code lookup - not a per-lecture loop. Surfaced in
three places, per this milestone's explicit list:
  - **Lecture page** (`templates/lectures/detail.html`): an "Exam
    Ready" badge next to the title, plus a Revision Schedule list
    showing each stage's status once any schedule exists for that
    lecture.
  - **Exam readiness** (`analytics/exams.html` via `AnalyticsExamsView`,
    and `analytics/insights.html`'s Exam Readiness Insights via
    `advanced_analytics.get_exam_insights()`): both gained an
    "Exam Ready" column/field showing how many of an exam's covered
    lectures are fully exam-ready, computed by intersecting
    `exam.covered_lectures` with `get_exam_ready_lecture_codes(user)` -
    in the view layer for the basic exams page (keeping
    `analytics.py`'s `get_exam_readiness()` itself untouched, per "do
    not duplicate existing analytics logic"), and inside
    `get_exam_insights()` for the Insights page (which already extends
    readiness with additional fields, so this is one more).
  - **Dashboard**: `exam_ready_count` in the new Revision section (see
    below).

**Dashboard** (`progress/services/revision.py:
get_revision_dashboard_stats()`, called from both `DashboardView` and
`DashboardWidgetsView` alongside the pre-existing Milestone 5/8
widgets, none of which were modified): a new "Revision" section -
Due Today, Overdue, Upcoming, Completed This Week, an overall
completion-percentage bar, and the exam-ready lecture count. Refreshes
via the same `Refresh` button/`#dashboard-widgets` HTMX swap already in
place since Milestone 5.

**Analytics Integration** (extends `advanced_analytics.py`'s Insights
page with a new "Revision Insights" section, per this milestone's
explicit instruction - the calculations themselves live in
`revision.py`, not duplicated into `advanced_analytics.py`):
revision completion %, overdue count, workload (pending count),
upcoming load (pending due within 7 days), exam-ready count, average
revision delay (`completed_at.date() - due_date` in days, negative
means completed early), and a revision streak (current/longest
consecutive days with at least one revision completed - the
revision-workflow counterpart to `advanced_analytics.get_study_streak()`,
which tracks a different event stream, topic completions).

**Admin** (`progress/admin.py`): `RevisionScheduleAdmin`
(`list_display`: user/lecture/revision_level/due_date/status/
completed_at; `list_filter`: status/revision_level/subject/user; a
`RevisionHistoryInline` showing each schedule's completion history
directly on its admin page) and a standalone `RevisionHistoryAdmin`.

**Navigation**: "Revision" added between Progress and Analytics in
`templates/base.html`'s nav, exactly where this milestone specified.

**Tests**: 157 → **219** (+62, all in a new `progress/tests_revision.py`
module - kept separate from the already-845-line `progress/tests.py`
rather than appended; Django's default `DiscoverRunner` test-file
pattern `test*.py` picks it up automatically, no settings change
needed). Covers: `is_lecture_completed()` (fully done, partially done,
untouched, per-user isolation), schedule creation (all three stages
correct, exact due-date math verified against a fixed completion date,
no schedule for an incomplete lecture, duplicate prevention on a
second call, schedules never shared across users), the real
`ProgressToggleView` HTTP endpoint actually triggering schedule
creation on the exact toggle that completes a lecture (not just the
service function called directly) and *not* re-creating one when a
completed lecture is briefly toggled incomplete and back, exam-ready
determination (not ready before any revision/some revisions/ready only
once all three, isolated per user), the revision queue's four buckets
and every filter (subject/status/level), completion (status/
completed_at/history-entry creation, no-op on double-completion,
never deletes, another user's schedule can't be completed, unknown id
returns `None`), dashboard statistics (zero-state, overdue/due-today/
upcoming counts, completed-this-week, per-user isolation), every
analytics extra (delay sign, workload, upcoming load, overdue count,
streak), all three revision views (full page vs. HTMX partial,
filters, anonymous redirect, 404 on another user's schedule, query
budget), and the three integration points (lecture page shows the
schedule/badge only once earned, dashboard shows the new section and
is per-user, the exams/insights pages show the exam-ready count
correctly).

**Verification**: `manage.py test` - 219/219 passing; `manage.py check`
clean; `makemigrations --check --dry-run` reports "No changes
detected". Manually verified against the real imported dataset and the
"alice" account created during Milestone 7's verification: completed
`P-01`'s only topic via the real HTMX toggle endpoint, confirmed all
three revision stages appeared on both `/lecture/P-01/` and
`/revision/` with the correct due dates (today+1/+4/+11, matching the
interval constants), clicked "Mark Complete" on the First Revision via
HTMX and confirmed the status/history updated in place without a page
reload, and confirmed the Completed bucket's count on the queue page
updated to reflect it.

- No CSV files or importer code were touched by this milestone; the
  only model changes were the two brand-new tables described above (no
  existing model's fields changed).

---

### Milestone 10 — Import & Dataset Management

Turned the Milestone 3/4 CSV importer into a full dataset lifecycle
system, per this milestone's own framing: not a rewrite of the
importer ("Do NOT rewrite it"), but a layer around it that can answer
"what changed," "is this safe to import," "can I preview it," "can I
roll it back," and "which version am I on." Every new piece —
`validate_only()`, the `services/dataset/` package, the new CLI flags
— calls into the existing Milestone 3/4 importer classes rather than
re-implementing row parsing, validation, or CSV reading.

**New models** (`routines/models.py`):

- `DatasetVersion` - one row per completed import: `version_name`
  (unique), `source` (path to that version's archived CSVs),
  `description`, `imported_by` (`User`, `SET_NULL`, nullable - see
  Architectural Decisions), `imported_at`, `is_active`, `checksum`
  (SHA-256 hex over all 5 source CSVs), and `statistics` (a `JSONField`
  snapshot of row counts per entity, not a data backup - see below).
  A partial `UniqueConstraint(fields=["is_active"],
  condition=Q(is_active=True))` - the standard Django pattern for "at
  most one row may have this flag set" - is what actually guarantees a
  single active dataset, not application code alone.
- `ImportLog` - one row per *attempted* import of any kind (real,
  `--dry-run`, `--preview`, or `rollback_dataset`), each tagged with a
  `status` (`SUCCESS`/`FAILED`/`DRY_RUN`/`PREVIEW`/`ROLLBACK`):
  `dataset_version` (`SET_NULL`), `importer_version`, `user`
  (`SET_NULL`), `started_at`, `duration_seconds`, `imported_counts`/
  `skipped_counts` (JSON dicts), `errors`, `warnings` (JSON list).
  This is the durable "every import, ever" trail this milestone asked
  for - a narrow, explicitly-requested exception to "no audit logging"
  alongside Milestone 9's `RevisionHistory`, not a new general policy.
- Migration `routines/migrations/0005_datasetversion_importlog_and_more.py` -
  both are brand-new tables, no existing-data migration concerns.

**Minimal importer extension, not a rewrite**
(`routines/services/csv/base_importer.py: validate_only()`): reads the
file, validates the header, then runs every row through the importer's
own existing `validate_row()` - the exact same per-entity validation
logic each `*Importer` subclass already had - but never calls
`import_row()` and never opens a transaction, since nothing is written
and there is nothing to roll back. This one method is what makes
`--preview` and the pre-flight comparison possible without a second,
parallel validation implementation.

**`routines/services/dataset/` package** (four modules, each with one
job, mirroring this project's established `services/` pattern from
Milestone 3 onward):

- `versioning.py` - `compute_checksum(base_dir)` (SHA-256 over the 5
  CSVs concatenated in a fixed order - a change-fingerprint, not a
  verification signature); `archive_source_csvs(base_dir, version_name)`
  (copies the 5 CSVs into `data/dataset_archive/<version_name>/` -
  see Architectural Decisions for why this exists at all);
  `next_version_name()` (`v{N}-{timestamp}`); `create_dataset_version()`
  (archives + creates an unactivated `DatasetVersion` row);
  `activate_version(version)` (atomically deactivates every other
  version, then activates this one - the only code path allowed to
  flip `is_active`); `get_active_version()`/`get_previous_version()`.
- `statistics.py` - `collect_statistics(base_dir)`: DB row counts for
  Subject/Chapter/Lecture/LectureTopic/Exam, plus a `routine_event_count`
  read directly from `routine.csv` (the one statistic with no
  persisted model, since only `CLASS` rows become `Lecture` rows - a
  fact established since Milestone 3 and unchanged here).
- `comparison.py` - the engine behind both `--preview` and
  `compare_dataset`: a generic `_diff(new_by_key, old_by_key, fields)`
  helper natural-key-diffs Subjects (key = `code`), Chapters (key =
  `subject_code`+`paper`+`chapter_no`), Lectures (key = `lecture_code`,
  `CLASS` rows only), LectureTopics (key = `lecture_code`+`topic`,
  reusing the existing `parse_chapter_ref()` helper from
  `routines/services/csv/utils.py` rather than re-parsing chapter
  references), and Exams (key = `exam_code`) into Added/Updated/
  Removed/Unchanged buckets. `compare_routine_events()` deliberately
  does **not** force a 4-bucket diff for `DAILY_EXAM`/`WEEKLY_EXAM`/
  `MONTHLY_EXAM` rows - see Architectural Decisions for why - instead
  reporting a total/by-event-type breakdown alongside the already-
  computed `CLASS`-row (Lecture) diff. `compare_all(base_dir)` is the
  single entry point both `--preview` and `compare_dataset` call, and
  passes its already-computed lecture diff into
  `compare_routine_events()` so that function is never computed twice
  (a real double-computation I found in my own draft and fixed before
  it shipped - see Errors and Fixes). `detect_duplicates(base_dir)` is
  a separate pre-flight scan across all 5 CSVs, run before any import
  begins - deliberately kept independent of each importer's own inline
  `DuplicateTracker` (which still runs during the real import as
  defense-in-depth), not a replacement for it.
- `rollback.py` - `rollback_to(target_version, user=None, stdout=None)`:
  confirms the target's archived CSVs still exist on disk, then
  re-runs the *entire* normal import pipeline (`run_import_stages()`,
  the identical function a normal import uses - see Architectural
  Decisions) against those archived files, wrapped in one
  `transaction.atomic()` together with `activate_version(target_version)`,
  and finally writes an `ImportLog` row with `status=ROLLBACK`.

**CLI extensions** (`routines/management/commands/import_csv.py`,
restructured, not replaced): the original per-stage import loop was
extracted verbatim into `run_import_stages(base_dir, stdout, style)`
so the exact same code path now runs for a real import, a dry run, and
a rollback.

- `--preview` - runs `validate_only()` across all 5 importers plus
  `comparison.compare_all()`, prints an Added/Updated/Removed/Unchanged
  summary per entity, and writes an `ImportLog` (`status=PREVIEW`).
  Nothing is written to the domain tables at all.
- `--dry-run` - runs the real `run_import_stages()` inside
  `transaction.atomic()`, then deliberately raises an internal
  `_DryRunRollback` exception to force the transaction to roll back,
  caught immediately after - so a dry run exercises every line of the
  real import (including the parts `validate_only()` skips, like
  `import_row()` and the `DuplicateTracker`) with a guaranteed full
  rollback. Its `ImportLog` (`status=DRY_RUN`) still persists, since
  logging is metadata outside the rolled-back transaction.
- `--user <username>` - resolved via
  `get_user_model().objects.filter(username=...).first()`, silently
  `None` if not found - never a hardcoded id, per this milestone's
  explicit "Do NOT hardcode dataset versions" instruction (extended
  here to mean users too).
- A real (non-preview, non-dry-run) import now also calls
  `create_dataset_version()` + `activate_version()` after
  `run_import_stages()` succeeds, and writes an `ImportLog`
  (`status=SUCCESS`, or `FAILED` with the error captured if a stage
  raises). `IMPORTER_VERSION = "1.0"` module constant recorded on every
  log row.

**New management commands**: `compare_dataset.py` (`--dir`, defaults
to `settings.BASE_DIR`) and `rollback_dataset.py` (`--to VERSION_NAME`,
`--user`) - both thin wrappers that call straight into
`comparison.py`/`rollback.py`, no logic of their own.

**Dataset History UI** (`/datasets/`, `DatasetHistoryView`, read-only,
`LoginRequiredMixin`): every `DatasetVersion` (active one flagged),
each version's `statistics`, and the full `ImportLog` history
(status/duration/imported-skipped counts/errors/warnings), using the
same `get_template_names()`/`request.htmx` partial pattern every other
list page in this app has used since Milestone 4.

**CSV Comparison UI** (`/datasets/compare/`, `DatasetCompareView`,
read-only): runs `comparison.compare_all()` against the real project-
root CSVs and renders a color-coded Added/Modified/Removed/Unchanged
breakdown per entity, filterable by entity/change-type via GET params,
HTMX-refreshed with no page reload - no editing capability anywhere on
this page, per this milestone's explicit "no editing" instruction.

**Admin** (`routines/admin.py`): `DatasetVersionAdmin` and
`ImportLogAdmin`, following the same `list_display`/`list_filter`
pattern as every other admin registration in this project.

**Navigation**: "Datasets" added to `templates/base.html`'s nav,
highlighted active whenever the current path starts with `/datasets/`.

**Tests**: 219 → **284** (+65, all in a new `routines/tests_dataset.py`
module, kept separate from the existing `routines/tests.py` for the
same reason Milestone 9 kept revision tests in their own file). A
`DatasetTestCase` base class uses
`override_settings(DATASET_ARCHIVE_ROOT=<tempdir>)` so no test ever
writes into the real project's `data/dataset_archive/` folder - see
Errors and Fixes for why this was necessary. Covers: checksum
stability/change-detection, version creation/activation (single-active
constraint enforced, previous-version lookup), statistics collection
against a known fixture, comparison output for every entity (added/
modified/removed/unchanged, including the routine-events breakdown),
duplicate detection across all 5 CSVs, `--preview` (writes nothing,
`ImportLog` still created, duplicate keys correctly reported via the
importer's own validation - see Errors and Fixes), `--dry-run` (full
rollback confirmed via before/after row counts, `ImportLog` persists
despite the rollback), a normal import creating and activating a
`DatasetVersion`, `rollback_dataset` restoring a prior version's actual
data (not just flipping `is_active`), the `compare_dataset` command's
output, and both new views (full page vs. HTMX partial, anonymous
redirect, empty-state with nothing imported yet, query budget).

**Verification**: `manage.py test` - **284/284 passing**; `manage.py
check` clean; `makemigrations --check --dry-run` reports "No changes
detected"; `manage.py validate_datasets` still reports 0 errors/0
warnings (unaffected by this milestone, as expected - it validates raw
CSVs, this milestone versions and compares them). Manually verified
against the real project dataset: `import_csv --preview` reported "0
added, 0 modified, 0 removed" across all 5 entities plus a Routine
Events breakdown (51 CLASS, 49 DAILY_EXAM, 12 WEEKLY_EXAM, 3
MONTHLY_EXAM) with zero DB writes (row counts identical before/after);
`import_csv --dry-run` completed a full import pass then rolled back
completely (row counts unchanged, but its `ImportLog` row persisted);
a real `import_csv` run created and activated `DatasetVersion` "v1",
recorded in `/datasets/`; a second real run created and activated "v2";
`rollback_dataset --to v1` restored `is_active` to "v1" and the
underlying Subject/Chapter/Lecture data back to "v1"'s values,
confirmed row-for-row against a value changed between the two imports.

- No CSV files were modified, the existing importer classes were
  extended (via `validate_only()`) rather than rewritten, and no
  existing analytics/revision/progress logic was touched by this
  milestone.

---

### Milestone 10.5 — Timeline-Based Navigation

Replaced page-based Previous/Next navigation on the Routine and Exam
pages with a scrollable, event-based timeline that always opens around
the user's current study position - "Past <- Today -> Future" instead
of "Page 1 -> Page 2 -> Page 3". Navigation and presentation only, per
this milestone's own scope: no model/migration changes, no importer
changes, no analytics-calculation changes - every progress/readiness
number shown on a timeline card is bulk-fetched from the exact,
unmodified functions Milestone 5/8/9 already built.

**New service** (`routines/services/timeline.py`): owns anchor
resolution, event-based windowing, and week/date grouping - nothing
else. See Architectural Decisions below for the full reasoning behind
its windowing algorithm; in short:

- **Event-based, not calendar-day-based** (the milestone's own explicit
  requirement): `PREVIOUS_EVENTS = 5` / `NEXT_EVENTS = 10` centralized
  constants control how many *events* surround the anchor, not how
  many calendar days. A date is never split across a window boundary -
  once a date's first event is pulled in, every event on that date
  comes with it, so a busy day never gets truncated mid-day and empty
  calendar days never appear at all (the window is built by querying
  `Lecture`/`Exam` rows directly, never by iterating raw dates).
- **Smart anchor** (`_windowed_query()`): today's events if any exist,
  else the nearest upcoming event, else the nearest past event -
  resolved from the same two bounded queries the window itself needs
  (rows `< today` and rows `>= today`, each capped at a fixed
  `FETCH_CEILING`), so anchor resolution adds zero extra queries over
  building the window itself.
- **"Load more" via `before`/`after` cursors**: the HTMX "load
  older"/"load newer" endpoints pass the oldest/newest currently-loaded
  date back as a cursor, extending the window strictly past that date -
  one query, same whole-date-never-split guarantee.
- `get_lecture_timeline()` / `get_exam_timeline()`: the two concrete
  timelines, sharing the same private windowing engine
  (`_windowed_query()`) over `Lecture.lecture_date` and `Exam.exam_date`
  respectively.
- `attach_lecture_progress()` / `attach_revision_status()` /
  `attach_exam_readiness()`: bulk-merge progress/revision/readiness
  data onto a window's events in one query each (never one query per
  card), calling straight into `analytics.get_lecture_completion_stats()`,
  `revision.get_exam_ready_lecture_codes()` + a new
  `revision.get_pending_revision_counts()` bulk helper, and
  `analytics.get_exam_readiness()` - none of these existing functions
  were modified; only new code was added around them.
- `group_by_week()` / `window_bounds()`: presentation-only grouping and
  cursor-boundary helpers - no calculations.

**Routine Timeline** (`/routine/`, `RoutineTimelineView` - replaces
the old page-based `RoutineListView`): dated Lectures only. Filters:
Subject, Completed/Incomplete (reusing `analytics.completed_case()` -
the exact aggregation `get_lecture_analytics()` already uses, applied
as a queryset filter rather than a second completion calculation).
Each lecture card shows a completion bar (`completed_topics`/
`total_topics`, reusing `get_lecture_completion_stats()`), an "Exam
Ready" badge or pending-revision count (reusing
`get_exam_ready_lecture_codes()`/the new bulk helper). Today's date
section is visually distinct (blue background/border) with a "TODAY"
divider; weeks render under sticky headers.

**Exam Timeline** (`/routine/exams/`, `ExamTimelineView` - new; no
dedicated exam list page existed before this milestone, exams
previously only surfaced via a routine-list filter or the Analytics
readiness page). Centers on the current/next upcoming exam. Filters:
Subject (resolved via a small one-time bulk pass over `covered_lectures`
- see Architectural Decisions), Readiness status (a post-window filter
over the already-computed `readiness_label`, not a second readiness
calculation). Each exam card shows a countdown, the readiness
percentage/label/badge (all read directly from
`analytics.get_exam_readiness()`'s output), and covered-lecture count.

**Revision Timeline** (`/revision/` - the Milestone 9 Revision Queue,
enhanced rather than rebuilt): it already had no pagination and was
already bucketed into Overdue/Due Today/Upcoming/Completed, so this
milestone's changes here are deliberately small - a "TODAY" divider
between Overdue and Due Today, sticky section headers, and the shared
Jump-to-Today control. `get_revision_queue()` itself was not touched.

**HTMX lazy loading** (`RoutineTimelineWindowView`/
`ExamTimelineWindowView` at `/routine/window/`/`/routine/exams/window/`):
a sentinel `<div>` at each edge of the timeline carries
`hx-trigger="revealed"`, firing only when scrolled into view. Its
response replaces it (`hx-swap="outerHTML"`) with the newly-loaded
day-groups plus a fresh sentinel (if more remain) positioned so
history keeps loading in the correct direction - a new "prev-sentinel"
lands *above* the newly-loaded older content, a new "next-sentinel"
lands *below* the newly-loaded newer content. No JavaScript
IntersectionObserver code was needed; this is htmx's built-in
`revealed` trigger.

**Jump to Today + Timeline Memory**
(`templates/partials/_timeline_jump_fab.html`, shared by all three
timeline pages): a floating "Today" button scrolls to the `#today-marker`
element. Separately, a small inline script records `window.scrollY`
into `sessionStorage` (keyed by `location.pathname`) on every scroll
and restores it on load - so returning from a lecture/exam/revision
detail page lands back at approximately the same scroll position
instead of recentering. Only a fresh session (no stored key yet) or an
explicit Jump-to-Today click (which clears the stored key) recenters
on the anchor, exactly as this milestone specified. `sessionStorage`
only - nothing persisted server-side or in the database.

**Retired**: `routines/services/events.py` (`get_routine_events()`,
Milestone 6's Lecture+Exam merge for the old paginated routine list)
and `templates/routine/list.html`/`_table.html` - both fully superseded
by `timeline.py` and the new timeline templates; keeping them would
have meant two independent "merge Lecture+Exam into a list"
implementations, one of them dead. `templates/base.html`'s "Exams" nav
link now points at the dedicated Exam Timeline URL instead of
`routine-list?event_type=EXAM`.

**Tests**: 284 → **304** (net +20: a new `routines/tests_timeline.py`
module with ~30 tests covering anchor resolution (today/before-
schedule/after-schedule/nothing-scheduled cases, for both the Routine
and Exam timelines), event-based windowing (a date is never split,
empty days never consume budget, `has_more_previous`/`has_more_next`
flags), lazy-loading cursors (older/newer windows never duplicate or
skip events), week grouping, progress/revision/readiness integration
(bulk-correct, per-user isolated), the Completed/Incomplete and
Readiness-status filters, and all four timeline views (full page/HTMX
partial/anonymous redirect/query budget) - minus 10 tests removed from
`routines/tests.py` for the retired `get_routine_events()`/
`RoutineListView` (their behavior no longer exists to test; the
equivalent behavior is covered by the new timeline tests instead).

**Verification**: `manage.py test` - **304/304 passing**; `manage.py
check` clean; `makemigrations --check --dry-run` reports "No changes
detected" (confirming this milestone touched no models, as required).
Manually verified against the real project dataset via the Django
test client: `/routine/` opens with the "TODAY" divider positioned
correctly relative to the real dataset's schedule, `/routine/exams/`
centers on the next real upcoming exam, `/revision/` still shows all
four buckets with the new divider, the `window/` lazy-load endpoints
return additional day-groups with no duplication, and every page's
query count stayed within the ≤10 budget (8 for `/routine/`, 7 for
`/routine/exams/`, 11 for `/revision/` - unchanged from Milestone 9,
6/5 for the two `window/` endpoints).

- No CSV files, models, migrations, or existing analytics/revision
  calculation logic were touched by this milestone - only navigation,
  templates, and the new `timeline.py` service.

---

### Milestone 11 — User Experience & UI Polish

A refinement pass, not a redesign, per this milestone's own framing:
every page's HTML/Tailwind classes were reworked for consistency,
readability, and accessibility, but no view's business logic, no
service function, no model, and no query was touched beyond the
presentation-only reshaping described below. Nothing here changes
what any page *does* - only how consistently it looks and how well it
reads to assistive technology.

**New design-system component library** (`templates/components/`,
14 files - Phase 1): small, genuinely-reused includes, each solving
one concrete duplication problem found while surveying the app's
~50 templates:

- `page_header.html` - a page's `<h1>` + optional subtitle + optional
  action (an HTMX-refresh button, e.g. Dashboard/Insights, or a plain
  link). Replaces a slightly different hand-written header on every
  single page.
- `section_header.html` - a section's `<h2>` with an optional
  trailing count (`"Overdue (3)"`) and an optional trailing action
  link (`"View full insights →"`), with a `sticky` flag for the
  Revision Queue's pinned section headers.
- `metric_card.html` - the "label / big number / optional sublabel"
  stat tile repeated dozens of times across the Dashboard, Insights,
  and Revision Queue (previously hand-written `bg-white border
  rounded p-4` boxes with no shared markup at all). Supports an
  optional `total` (renders "12 / 20") and `unit` suffix without any
  string-concatenation gymnastics in the caller.
- `badge.html` - the small colored status pill (readiness labels,
  Exam Ready, dataset/import status, revision due/completed) used
  everywhere but previously copy-pasted with slightly different
  markup each time. Takes the color classes as a plain string, computed
  server-side exactly as before (`readiness_badge_class`,
  `confidence_badge_class`, etc.) - the component never encodes a
  business-logic threshold itself.
- `progress_bar.html` - the completion bar (`bg-gray-200` track +
  colored fill) used in every analytics table, the Dashboard, Progress
  overview, and timeline cards; adds `role="progressbar"` +
  `aria-valuenow/min/max` for the first time (Phase 10).
- `empty_state.html` - a friendly, specific "nothing here" sentence
  (Phase 6) instead of a bare "No data" - see the dedicated section
  below.
- `loading_skeleton.html` - static (non-animated, per this milestone's
  own "avoid animations" instruction) gray placeholder bars, shown via
  htmx's existing `htmx-indicator` convention (already used by the
  global `#page-indicator` bar since Milestone 1) - not currently wired
  into any specific page's HTMX swap, since none of this app's HTMX
  responses are slow enough to need one in practice (see Known Issues/
  Architectural Decisions for why this is available-but-unused).
- `filter_panel.html` / `select_field.html` / `text_field.html` /
  `_filter_form_attrs.html` - Phase 5's form standardization for the
  ~8 near-identical HTMX auto-submit filter forms (Routine/Exam
  Timeline, Revision Queue, Analytics Subjects/Chapters/Lectures,
  Datasets Compare). `filter_panel.html` takes a `fields` list built
  by the view (each `{"kind": "select"|"text", ...}`) and composes
  `select_field.html`/`text_field.html` - a presentation-only reshaping
  of data the view already had (the same `Subject` queryset, the same
  tuple choices), never a new query or calculation. `_filter_form_attrs.html`
  centralizes the `hx-get`/`hx-target`/`hx-trigger`/`hx-push-url`/
  `hx-indicator` attribute set every one of these forms shared anyway.
- `form_field.html` - Phase 5's form standardization for the 5
  Django-auth-form pages (login, register, password change, password
  reset request, password reset confirm) - one consistent
  label/widget/help-text/error layout per field, reused identically
  across all five instead of five separately-hand-written copies.
  `auth_card.html` (the shared "narrow centered card" shell those same
  five pages all use) was also built, but - corrected during Milestone
  11.1's stabilization pass - was never actually wired into any of the
  five pages; each kept its own 3-line inline wrapper `<div>` instead.
  Left as-is rather than retrofitted: the markup is identical across
  all five call sites but small enough (3 lines) that splitting each
  page into a wrapper+content-template pair (the only way `{% include
  %}` can wrap arbitrary child content in Django - see `card.html`'s
  docstring) would add more files than it removes duplication. Same
  status as `loading_skeleton.html` below: built, tested, available,
  not currently wired into a live page.

**`core/templatetags/ui_tags.py`** (new): small `simple_tag`/`filter`
helpers for the handful of cases an includable component doesn't fit -
`button_classes()`/`field_classes()` (canonical class strings for
elements whose other attributes vary per call site), `pct_color()`
(the three-tier completion color a progress bar's fill needs -
emerald/blue/amber - extracted so it's computed once, not
re-implemented per template), `class_if_positive()` (conditionally
applies a class, e.g. "Overdue" only turns red once the count is
actually positive - preserves behavior that predates this milestone),
and `times()` (Django templates have no built-in "loop N times" tag,
needed by `loading_skeleton.html`).

**Global layout & navigation** (`templates/base.html` - Phases 2/3/10):
a skip-to-content link (visually hidden until focused, jumps to a new
`#main-content` landmark), `aria-current="page"` on whichever nav item
matches the current page (re-verified by a dedicated test that exactly
one nav item is ever marked current), `focus-visible` rings on every
interactive nav element, and the nav `<ul>` now scrolls horizontally on
narrow viewports (`overflow-x-auto flex-nowrap`) rather than wrapping
awkwardly or requiring a hamburger menu - this milestone explicitly
ruled out a sidebar or any new navigation paradigm, so "let it scroll"
was the simplest fix that didn't change the nav's structure at all.

**Page-by-page polish** (Phase 4, all touched pages listed in the
Current Project Structure tree above): Dashboard, Routine Timeline,
Exam Timeline, Revision Queue, Progress, all five Analytics pages, both
Datasets pages, Lecture Detail, and Exam Detail were all rebuilt onto
the component library above, with consistent card borders
(`border-gray-200 rounded-lg`, replacing a mix of bare `border rounded`
elsewhere), consistent spacing, and `flex-wrap`/`gap-2` added to every
row-shaped element that previously had no wrap behavior at narrow
widths (Phase 9). Two small bugs were found and fixed along the way
(not part of any prior milestone's scope, caught while touching these
templates - see Errors and Fixes): a stale "Back to exams" link on the
Exam Detail page still pointed at the pre-Milestone-10.5 `routine-list
?event_type=EXAM` URL; nothing else was broken by it (the link still
resolved, just to the wrong page since Milestone 10.5 gave Exams its
own dedicated timeline).

**Forms standardized** (Phase 5): every filter form and every Django
auth form now shares one label/input/help-text/error layout via the
components above, with `focus:ring-2` on every input/select/button
that previously had no visible focus state at all.

**Empty states** (Phase 6): every "No data"/blank list in the app now
reads as a full, specific sentence instead of a generic placeholder -
e.g. Routine Timeline: "No lectures match these filters - try widening
the Subject or Status filter."; Revision Queue: "No overdue revisions
- you're on top of things." / "Nothing due today." / "No completed
revisions yet."; Dashboard: "You're all caught up - no upcoming
exams."; Dataset History: "No dataset has been imported yet. Run
import_csv to get started." No illustrations were added, per this
milestone's explicit instruction - text only.

**Accessibility** (Phase 10): every progress checkbox on the Lecture
Detail page gained a descriptive `aria-label` (e.g. "Class done for
Vectors intro") - previously four unlabeled checkboxes per row with no
accessible name at all; every data table gained a `<caption
class="sr-only">` describing its contents (`scope="col"` was already
present on most table headers from earlier milestones, now applied
consistently everywhere); every progress bar exposes
`role="progressbar"` + `aria-valuenow/min/max`; every interactive
element (links, buttons, form fields, nav items) has a visible
`focus-visible` ring, several of which previously had no focus
indicator at all. None of this changes behavior - purely additive
markup.

**Template cleanup** (Phase 11): retired `routine/list.html`/
`_table.html` were already gone (Milestone 10.5); this milestone
additionally removed the last remaining hand-rolled `bg-white border
rounded p-4` boxes app-wide (confirmed via a repo-wide grep finding
zero remaining matches of the old, inconsistent card class string)
in favor of the shared components. Genuinely single-use markup (the
Datasets "Duplicate Keys Found" warning box, the CSV comparison
Added/Modified/Removed count tiles, the Study Heatmap grid) was left
inline, per this milestone's own "don't over-abstract" instruction -
none of it repeats anywhere else in the app.

**Tests**: 304 → **323** (+19, all in a new `core/tests_ui.py` module):
component rendering in isolation (`page_header`, `section_header`,
`metric_card`, `badge`, `progress_bar`, `empty_state`, `filter_panel`,
`loading_skeleton`, each rendered directly via `render_to_string()` and
asserted against its expected output), base-layout tests (skip link
present, exactly one nav item ever marked `aria-current="page"`),
empty-state copy tests (the exact friendly sentences above, built
against a genuinely empty per-user dataset rather than just an
unauthenticated/filtered case), and accessibility-markup tests
(checkbox `aria-label`s present, table `<caption>`s present, progress
bars carry `role="progressbar"`). No existing test needed logic
changes; a small number of empty-state string assertions
(`routines/tests_dataset.py`) were checked against the new copy and
happened to still pass unchanged since the new sentences were written
to keep the original substring intact.

**Verification**: `manage.py test` - **323/323 passing**; `manage.py
check` clean; `makemigrations --check --dry-run` reports "No changes
detected" (confirming this milestone touched no models, as this
milestone required). Manually verified every touched page renders
correctly against the real project dataset via the Django test
client, in both its empty (no `Progress`/`RevisionSchedule` rows for a
fresh user) and populated (real imported dataset) states, and that no
page's query count regressed (re-confirmed by the existing
query-budget test suite, all of which still pass unchanged - see
Query Count Summary).

- No CSV files, models, migrations, importer logic, analytics
  calculations, revision calculations, or timeline windowing logic
  were touched by this milestone - only templates, the two new
  `core/templatetags/ui_tags.py` helpers, and small view-layer
  `filter_fields` list construction (reshaping data views already had
  into the shape `filter_panel.html` expects - no new queries).

---

### Milestone 11.1 — Stabilization & Verification

A conservative verification pass over Milestone 11's UI polish work
before starting any new feature milestone - no features added, no
pages redesigned, no workflows changed, per this milestone's own
explicit scope. Every phase of its checklist was performed against the
running app (via the Django test client, both as a fresh/empty user
and against the real imported dataset) rather than by inspection alone:

- **Rendering verification**: every page fetched in both full-page and
  HTMX-partial form, response HTML scanned for leaked `{% %}`/`{{ }}`
  template syntax, HTML comments, empty `class=""` attributes, and
  stray `None` text - none found. Every `{% include
  "components/*.html" %}` call site was grepped for missing required
  context variables (`badge.html` without `classes`, `metric_card.html`
  without `label`/`value`, `progress_bar.html` without `percentage`,
  `empty_state.html` without `message`, `filter_panel.html` without
  `fields`, `page_header.html`/`section_header.html` without `title`) -
  none found.
- **Styling verification**: confirmed the compiled Tailwind stylesheet
  still loads on every page; grepped for duplicate `class="..."
  class="..."` attributes and any remaining hand-rolled `bg-white
  border rounded p-4` card or `bg-gray-200 rounded h-*` progress-bar
  markup that should have used the shared components - none remain
  anywhere in the app.
- **Application smoke test**: every page in the milestone's checklist
  loads (200) for both a fresh user and the real dataset. (This app
  has no "Profile" page - it was never built in any prior milestone,
  and this stabilization pass does not add one, per "do not introduce
  new pages.") Every HTMX interaction was exercised directly: Routine/
  Exam Timeline filters and "load more" window endpoints, Revision
  Queue's subject/status/level filters, all three Analytics filter
  forms, the Dataset Compare filter, the Dashboard/Insights/Dataset
  History refresh buttons, a real progress-checkbox toggle (and
  reverted immediately after), and a real revision "Mark Complete"
  action (verified it flipped the schedule to completed, then reverted
  it and deleted the resulting `RevisionHistory` row so this
  verification pass left no trace on the real project database).
- **Responsive verification**: confirmed every template containing a
  `<table>` still wraps it in `overflow-x-auto`, the nav bar still
  scrolls horizontally on narrow viewports, and filter forms still wrap
  (`flex-wrap`).
- **Accessibility verification**: re-ran `core/tests_ui.py` (all 19
  tests, unchanged) confirming the skip link, single-active-nav-item
  `aria-current`, checkbox `aria-label`s, table `<caption>`s, and
  `progressbar` roles introduced in Milestone 11 are all still intact.
  Also confirmed no stray `tabindex` values exist anywhere except the
  intentional `tabindex="-1"` on the skip-link's `#main-content` target
  (the correct pattern - programmatically focusable without entering
  the natural tab order).
- **Component consistency**: the one inline (non-componentized) badge-
  shaped `<span>` remaining in the app
  (`routine/partials/_lecture_card.html`'s pending-revisions count) was
  reviewed and left as-is - it needs `|pluralize`, which `badge.html`'s
  flat `text`/`secondary` parameters can't express without the same
  `add`-filter concatenation bug this project already hit and fixed
  once during Milestone 11 (see that milestone's Architectural
  Decisions) - a single-line, already-documented exception, not a
  regression.

**One documentation inaccuracy found and corrected** (not a code bug -
nothing was rendering incorrectly): Milestone 11's write-up described
`auth_card.html` as reused across all 5 auth pages alongside
`form_field.html`, but `auth_card.html` was actually never wired into
any of them - each auth page kept its own small inline wrapper `<div>`
instead. Corrected in Milestone 11's Implemented Features entry above
rather than rewritten; `auth_card.html` remains built, tested, and
available (the same "exists but not currently used" status already
documented for `loading_skeleton.html`), left unwired deliberately
since retrofitting five working, already-passing-their-tests templates
onto a wrapper+content-template split for a 3-line shared shell would
be exactly the kind of unnecessary refactor this milestone's own
guiding principle rules out ("do not improve working code simply
because it can be refactored").

**No functional regressions found.** Every other phase of this
milestone's checklist confirmed Milestone 11's work was already
correct - nothing else needed changing.

**Verification**: `manage.py test` - **323/323 passing** (no change in
count - this was a verification pass, not a coverage-adding one);
`manage.py check` clean; `makemigrations --check --dry-run` reports
"No changes detected". All manual checks above passed with the real
imported dataset.

---

### Milestone 11.2 — Frontend Build Pipeline Repair

Milestone 11.1's stabilization pass verified rendering exclusively
through the Django test client - which never loads CSS and, critically,
strips real Django template comments in-process the same way it always
had, so neither of the two bugs below could have been caught by any of
that milestone's checks. This milestone's instruction to "use the
browser as the final source of truth" is what actually surfaced them.
Two independent, compounding root causes were found - both are now
fixed, and this milestone's own acceptance criteria (styled UI,
zero leaked comments, browser screenshots) are the direct evidence.

**Root cause #1 - the compiled Tailwind stylesheet was never rebuilt
since Milestone 1.** `theme/static/css/dist/styles.css` was still the
exact 5,569-byte file `tailwind install` produced at project scaffolding
time, containing only the handful of utilities used by
`theme/templates/base.html` (the unused django-tailwind demo template
noted in this file's project-structure tree since Milestone 1) -
`.flex`, `.container`, `.mx-auto`, `.items-center`, `.justify-center`,
`.bg-gray-50`, `.text-black`, and a few others. None of Milestones 2-11's
real template classes (`bg-white`, `border-gray-200`, `rounded-lg`,
`focus-visible:ring-2`, hundreds more) were ever compiled in, because
no milestone's workflow ever ran `npm run build` (or `npm run dev`) -
every milestone's "manual verification" step used `manage.py runserver`
+ the Django test client or curl, which returns HTTP 200 for the stale
static file and never inspects its actual content. **Verified the build
pipeline itself was never misconfigured**: `theme/static_src/postcss.config.js`
(`@tailwindcss/postcss` + `postcss-simple-vars` + `postcss-nested`) and
`theme/static_src/src/styles.css` (`@import "tailwindcss";` +
`@source "../../../**/*.{html,py,js}";`, Tailwind v4's CSS-first
config - there is no `tailwind.config.js` in this project, which is
correct for v4, not an oversight) are exactly what `django-tailwind`
generates and were never touched incorrectly. Running `npm run build`
from a clean `rimraf` of `dist/` (Phase 9's "rebuild from scratch")
produced a 23,275-byte stylesheet containing every utility this app's
templates actually use, confirmed by grepping for `.bg-white{`,
`.rounded-lg{`, `.focus-visible\:ring-2:focus-visible{`, and a dozen
others, and by the presence of `sr-only` (a class that only exists in
Milestone 11's skip-link markup) - proving the `@source` glob does
correctly discover every real template, including ones added in the
most recent milestone, once a build is actually run. **The fix here is
entirely operational, not code**: no config file changed. This project
has no CI/deploy step that runs `npm run build` automatically, so a
production or demo deployment must run it manually after `git pull`
(documented in Known Issues below).

**Root cause #2 - Django's `{# #}` comment tag cannot span multiple
lines, and 15 templates violated that unknowingly.** All 14 files in
`templates/components/` (Milestone 11) plus
`templates/partials/_timeline_jump_fab.html` (Milestone 10.5) opened
with a multi-line `{# Component: ... #}` docstring-style comment.
Django's shorthand `{# ... #}` tag is documented to only support
single-line content; when `{#` and `#}` are separated by a newline,
Django's tokenizer does not recognize the span as a comment token at
all and instead emits the entire `{# ... #}` block - opening marker,
docstring text, and closing marker - as a literal `TextNode`, rendered
verbatim into the page. This is **silent**: it is not a
`TemplateSyntaxError`, so `manage.py check`, `manage.py test`, and every
prior milestone's `assertContains`/`assertNotContains` checks all
passed cleanly, because none of them happened to search rendered HTML
for the literal substring `{#`. (Milestone 11.1's own leak-detection
regex checked for `\{%...%\}` and `\{\{...\}\}` but not `\{#...#\}` -
an oversight in that milestone's own verification, corrected here.)
Confirmed via a minimal reproduction
(`Template("{# a\nb #}").render(Context({}))` returns the comment text
verbatim, not an empty string) before touching any file. **Fix**:
every multi-line `{# #}` was converted to Django's block comment tag,
`{% comment %} ... {% endcomment %}`, which has no single-line
restriction and is otherwise behaviorally identical. A repo-wide scan
(not just `templates/components/`) confirmed these 15 files were the
only offenders.

**New regression tests** (`core/tests_ui.py`):

- `CompiledCSSTests` - asserts the compiled stylesheet exists, contains
  a representative set of the utilities this app's templates require
  (`.bg-white{`, `.bg-slate-900{`, `.border{`, `.rounded-lg{`,
  `.grid{`, `focus-visible\:ring-2`, etc.), and is larger than 15 KB (a
  stale demo-only build, the exact failure mode here, was ~5.8 KB) -
  this is explicitly a check on *this project's build output*, not a
  test of Tailwind itself, per this milestone's own framing.
- `NoLeakedTemplateCommentsTests` - one check renders every major page
  and asserts no response body contains a literal `{#`/`#}` marker; a
  second, independent check statically scans every file in
  `templates/components/` for a multi-line `{# #}` tag without needing
  any page to actually render it - catching the mistake at the
  template-source level for any component added in the future.

**One unrelated pre-existing bug found and fixed while running these
new tests**: `test_empty_state_renders_message_verbatim` (from
Milestone 11) asserted the raw string `"You're all caught up."`
against Django's HTML-autoescaped output, which correctly renders the
apostrophe as `&#x27;` - the test's assertion was wrong, not the
`empty_state.html` component (autoescaping user-facing text is the
correct, secure behavior). Fixed by asserting against the escaped form.

**Verification**: `manage.py test` - **327/327 passing** (323 after
Milestone 11.1, +4 for the two new `CompiledCSSTests`/
`NoLeakedTemplateCommentsTests` checks); `manage.py check` clean;
`makemigrations --check --dry-run` reports "No changes detected" (no
model, migration, or database change - this was a pure frontend-build/
template-syntax fix). Rebuilt the compiled stylesheet from a clean
`rimraf` of `dist/` and reconfirmed the same 23,275-byte, fully-
utility-complete output. **Browser-verified** (Playwright + headless
Chromium, logged in as a real user against the real imported dataset,
zero console/page errors on every navigation): Dashboard, Routine
Timeline, and Analytics Insights all render with fully styled
navigation (active-state highlighting, hover states), bordered/shadowed
cards, colored progress bars, colored readiness/status badges, the
Routine Timeline's sticky week headers and "TODAY" divider, and the
floating Jump-to-Today button - with no visible `{# ... #}` text
anywhere on any page.

- No models, migrations, importer logic, analytics/revision
  calculations, or timeline logic were touched by this milestone - the
  fix was entirely a stale build artifact (rebuilt, not reconfigured)
  and a template-comment syntax correction across 15 files, plus two
  new tests and one unrelated test-assertion fix.

---

### Milestone 12 — Navigation & Study Workspace

A connective-tissue milestone, per its own framing: "a student should
never feel lost." No new study algorithms, no duplicated business
logic - every number shown anywhere in this milestone's new pages
comes from an existing, unmodified service function (`analytics.py`,
`advanced_analytics.py`, `revision.py`, `timeline.py`), reused rather
than recalculated.

**Canonical pages** (Phase 4/5 - the "Single Canonical Entity" rule):

- **Subject** (`subjects/views.py: SubjectDetailView`, new -
  `/subjects/<pk>/`): the `subjects` app's first-ever view (it had
  only models/admin since Milestone 2). Shows overall completion
  (picked out of `analytics.get_subject_analytics(user)`'s existing
  result set - the same one-query-for-every-subject call every
  Analytics page already makes, not a second calculation), every
  chapter and lecture in the subject (via `get_chapter_analytics()`/
  `get_lecture_analytics()`, both already subject-filterable since
  Milestone 5), and every exam covering the subject (resolved via the
  same `covered_lectures` code-prefix matching `timeline.py`'s
  `_exam_ids_for_subject()` already established).
- **Chapter** (`ChapterDetailView`, new - `/chapters/<pk>/`): chapter-
  level completion (one row out of `get_chapter_analytics()`), every
  lecture touching the chapter, and a per-topic checklist built with
  the exact same bulk-Progress-lookup pattern `LectureDetailView`
  established in Milestone 4 (never a second way to compute "is this
  topic done").
- **Lecture** (existing `/lecture/<code>/`, unchanged URL) and
  **Exam** (existing `/exam/<id>/`, unchanged URL) - reused as-is, per
  this milestone's explicit "reuse existing pages" instruction; no
  duplicate "mini" detail views were created anywhere.
- **Routine Week** (`routines/views.py: RoutineWeekView`, new -
  `/routine/week/<n>/`): see the dedicated section below.

**Routine Week numbering** (Phase 6 -
`routines/services/timeline.py: get_routine_week_map()`/
`get_routine_week()`/`attach_routine_week_numbers()`): "Routine Week
N" is sequential relative to *this dataset's own imported schedule*
("Routine Week 1" is the earliest dated week, "Routine Week 2" the
next, and so on) - never the ISO calendar week of the year, which
would display as something like "Week 30" and mean nothing to a
student. This was a real spec/data gap worth flagging rather than
silently inventing: `routine.csv` has no week-number column at all
(confirmed against its header - `date,day,event_type,subject_code,
lecture_code,title,start_time,end_time,notes`), so there was no
existing field to "reuse" literally. The resolution treats this as a
relabeling of data that already exists (the exact `(iso_year,
iso_week)` grouping `timeline.group_by_week()` has computed since
Milestone 10.5), not a new calculation - `get_routine_week_map()` just
assigns 1, 2, 3... to those groups in chronological order. Applied to
the Routine Timeline's own week headers (now links to the canonical
page) but deliberately **not** to the Exam Timeline's week headers -
an exam's date doesn't necessarily fall inside any lecture week, so
forcing a "Routine Week" label onto exam groupings would sometimes be
meaningless; the Exam Timeline keeps its plain calendar week/year
label.

**Deterministic timeline anchor** (Phase 2 -
`timeline.py: _fetch_side()`): the anchor *date* was already
deterministic (min/max by date, no ties possible), but same-date
*events* had no secondary sort key, so the DB was free to return them
in any order - reading as "sometimes recentering differently" across
requests even with unchanged data. Fixed by adding `id` as an explicit
tie-breaker (same direction as the date field, so "closest to the
anchor first" stays consistent within a tied day) - a one-line change
to the query ordering, not a new algorithm. Routine's "Current lecture
> Next > Previous" and Exam's "Next > Current > Previous" priorities
(as this milestone specified them) turn out to collapse to the exact
same rule already implemented since Milestone 10.5 (today-or-later
wins, else nearest past) - there is no real distinction between
"happening now" and "starting later today" without lecture-level time
granularity the schedule doesn't reliably provide, so no algorithm
change was needed there, only the ordering fix above.

**Context-aware Jump button** (Phase 3 -
`partials/_timeline_jump_fab.html` gained a `label` parameter): "Today"
became "Jump to Current / Next Class" (Routine), "Jump to Next Exam"
(Exams), "Jump to Today's Revision" (Revision) - one shared component,
three call sites passing a different label.

**Workspace layout** (Phase 1/11 -
`core/templatetags/ui_tags.py: workspace_toolbar_classes()`): the top
nav bar is now `sticky top-0`; the Routine/Exam/Revision page's header
+ filters sit in one shared `sticky top-14` wrapper (one class-string
definition, not three copies, per Phase 11's "no duplicated layouts")
so both stay visible while only the timeline/queue content beneath
scrolls. The Revision Queue's already-sticky section headers
(Milestone 11) and the Routine/Exam Timeline's sticky week headers
were retargeted from `top-0` to `top-36` so they dock *below* the new
toolbar instead of being hidden behind it.

**Smart Back** (Phase 7 - `templates/components/smart_back.html`,
new): replaces every hardcoded "Back to Routine"/"Back to Exams"
link app-wide. Renders a real `<a>` (works with JavaScript disabled,
or on a direct page load with no history to return to) whose `href`
is a sensible fallback destination; a small script upgrades it to
`history.back()` only when there's actual same-origin app history to
return to (`document.referrer` same-origin **and**
`window.history.length > 1`) - browser back-navigation naturally lands
back on the exact previous URL, filters included (this app's filter
forms already used `hx-push-url="true"` since Milestone 4/6, so the
URL bar already encodes filter state). Nothing is stored in the
database, per this milestone's explicit instruction.

**Navigation Memory** (Phase 8 - `templates/base.html`, generalized
from Milestone 10.5's timeline-only version): every page now
remembers its own scroll position in `sessionStorage`, keyed by
`path + querystring`, restored on load - not just the three timeline
pages Milestone 10.5 originally covered. On the three pages with a
`#today-marker`, a fresh session (no saved position yet) still
recenters on it, same as before - that fallback now lives in one
place (`base.html`) instead of being duplicated per page.

**Admin vs. Student navigation** (Phase 9): the "Datasets" nav item is
now staff-only (`user.is_staff` - this project's only admin/user
distinction since Milestone 1, no custom roles ever existed, per the
Database Model Contract's Version 1 Constraints); non-staff users see
"Routine Resources" instead. Enforcement is at the **view** level too
(`routines/views.py: _StaffOnlyMixin`, a `UserPassesTestMixin`
checking `is_staff`, applied to `DatasetHistoryView`/
`DatasetCompareView`) - a non-staff user hitting those URLs directly
gets a 403, not just a hidden nav link, since hiding-only would be
security-by-obscurity. `RoutineResourcesView` (new -
`/routine/resources/`) is an honest placeholder: "Original routine
PDF," "Routine image," and a download button were requested, but no
file-upload feature, storage, or model for such assets exists anywhere
in this project (confirmed - no PDF/image sits in the repo, no prior
milestone built one), and this milestone's own constraints rule out
modifying existing models "unless absolutely necessary." Rather than
fabricating a fake upload feature, the page honestly shows "No routine
PDF has been uploaded yet." / "No routine image has been uploaded
yet." via the existing `empty_state.html` component - ready for a
future milestone to wire up real storage.

**Cross-navigation** (Phase 10):

- **Lecture Detail**: gained links to its Subject and every covered
  Chapter (previously plain text), Previous/Next Lecture (scoped to
  the same subject - comparing across subjects wouldn't mean anything
  to a student), and Upcoming Exam(s) covering this lecture (resolved
  via `covered_lectures` code matching, sorted by date).
  Revision Status was already shown (Milestone 9's Exam Ready badge +
  Revision Schedule list) - unchanged.
- **Exam Detail**: gained Covered Subjects and Covered Chapters
  (derived from the already-resolved covered-lecture objects, no
  second query pass over `covered_lectures`), a Readiness section
  (one row picked out of `analytics.get_exam_readiness(user)`), and a
  per-lecture "Exam Ready" badge on each covered lecture (reusing
  `revision.get_exam_ready_lecture_codes()`, already a bulk/single-
  query function). Its stale "Back to exams" link (dead since
  Milestone 10.5 replaced the filtered-list URL with a dedicated Exam
  Timeline, but nothing had touched Exam Detail since) was replaced
  entirely by `smart_back.html` in the same edit.

**Universal Linking** (Phase 5): every Subject/Chapter/Lecture/Exam
reference across Dashboard, Routine/Exam Timeline cards, Progress
overview, all three Analytics tables that show subject/chapter data,
and the Insights page (Strongest/Weakest Subject, Subject Ranking,
Completion Trend, all four chapter-insight lists, Exam Readiness
Insights) now links to its canonical page. Two deliberate exceptions,
both documented rather than silently inconsistent: the Revision
Queue's rows still link the *whole row* to the Revision Detail page
(the lecture/subject text sits inside that single anchor - nesting a
second `<a>` inside it would be invalid HTML and would fight the
row's existing click target), and one inline "N revision(s)" badge on
Routine Timeline cards stayed a hand-written `<span>` rather than
`badge.html` (needs `|pluralize`, which `badge.html`'s flat `text`/
`secondary` parameters can't express without reintroducing the
`add`-filter concatenation bug Milestone 11 already hit and fixed
once).

**Tests**: 327 → **370** (+43): `subjects/tests.py` (new - Subject/
Chapter detail rendering, reused-analytics correctness, per-user
isolation, query budgets), `routines/tests_navigation.py` (new -
Routine Week numbering/view/404-on-unknown-week/prev-next nav,
Routine Resources' honest empty state, staff-vs-non-staff dataset
permission enforcement including the anonymous-still-redirects case,
Exam Detail cross-navigation), `routines/tests_timeline.py` gained
`DeterministicOrderingTests` (same-date events order identically
across repeated calls, and specifically by ascending `id`),
`lectures/tests.py` gained `LectureDetailCrossNavigationTests`, and
`core/tests_ui.py` gained `SmartBackComponentTests`/
`WorkspaceLayoutTests` plus two new required-utility entries
(`.sticky{`, `.top-14{`, `.top-36{`) added to `CompiledCSSTests` after
this milestone's own development hit the exact "added new Tailwind
classes, forgot to rebuild" bug Milestone 11.2 exists to catch (see
Errors and Fixes) - confirming that regression test earns its keep.
Four pre-existing tests needed updating, none for a logic reason: three
fixture updates to keep reaching pages now gated behind the new
staff-only permission (`routines/tests_dataset.py`'s
`DatasetHistoryViewTests`/`DatasetCompareViewTests`, `core/tests_ui.py`'s
`NoLeakedTemplateCommentsTests`/`EmptyStateTests` - all switched their
test user to `is_staff=True`), and one query-budget bump
(`routines/tests.py: ExamDetailViewTests.test_query_count_is_small_and_fixed`,
5->10, for the real Covered Subjects/Chapters/Readiness/Exam-Ready
additions described above - the same "budget raised to reflect a real,
bounded addition" pattern every prior milestone's query-count changes
followed, not a regression).

**Verification**: `manage.py test` - **370/370 passing**; `manage.py
check` clean; `makemigrations --check --dry-run` reports "No changes
detected" (no model touched - `SubjectDetailView`/`ChapterDetailView`
are new views over existing models only). **Browser-verified**
(Playwright + headless Chromium, real login, real dataset): the
Routine Timeline's sticky nav+toolbar was confirmed to stay pinned
while scrolling past several weeks of content (caught and fixed a real
bug this way - see Errors and Fixes); Subject Detail, Exam Detail
cross-navigation, and Routine Week pages all screenshot correctly with
every described link present and working.

- No models, migrations, importer logic, analytics calculations,
  revision calculations, or timeline windowing logic were touched by
  this milestone - only new thin views over existing services, new
  templates/components, and navigation/permission wiring.

---

### Milestone 13 — Interface Refinement & Design Consistency

A consistency pass, per its own framing - "improve perception, not
complexity." No new pages, no new workflows; every change either
strengthens an existing shared component/service so every page using
it improves at once, or fixes a genuine inconsistency (including one
real, previously-undetected bug) found while auditing the app end to
end against this milestone's own "Component-First Principle."

**Phase 1 - Routine Week unification** (the milestone's own first,
explicit requirement): the Exam Timeline previously kept a separate,
plain ISO-week label because Milestone 12's `get_routine_week_map()`
only numbered weeks that actually contained a lecture - an exam
falling in a lecture-free week had no number to resolve to. Fixed by
making the map span **every** ISO week from the earliest to the
latest dated Lecture *or* Exam, inclusive, not just weeks with a
lecture in them (`date.fromisocalendar()` + a week-by-week walk from
the first Monday to the last). This is still "reusing existing
routine information, not inventing a calculation" (Milestone 12's own
framing, unchanged) - it fills in the gaps in an already-sequential
numbering rather than computing anything new. Both timelines now call
`attach_routine_week_numbers()` and render the identical "Routine
Week N" header, linking to the identical canonical page - **exactly
one shared Routine Week implementation**, per this milestone's own
acceptance criterion.

**Phase 13 - `timeline_body.html` consolidation**: auditing the
Routine and Exam Timeline templates side by side (prompted by fixing
Phase 1 above) found they were two near-identical files, differing
only in accent color, the today-marker label ("TODAY" vs. "NEXT
EXAM"), and which card partial each day's events render through -
exactly the kind of duplication this milestone's "Component-First
Principle" asks to be found and consolidated rather than left to
drift. Extracted into one shared `templates/components/timeline_body.html`
that both `routine/partials/_timeline_body.html` and
`exams/partials/_timeline_body.html` now call with their own accent
classes as parameters (literal strings, since Tailwind's build-time
scanner needs real class names in the source - a runtime-interpolated
`bg-{{ accent }}-500` would never be found by it). A bug fix to either
timeline's week/day rendering now only needs to happen once.

**Phase 3 - `card_classes()`**: audited every `bg-white border
border-gray-200 rounded-lg` card in the app (~44 occurrences) and
found two genuine padding tiers already in informal use - `p-4` for
content cards/stat tiles (the majority) and `p-3` for denser list-item
cards (Dashboard's Today's Routine, Routine/Exam Timeline event
cards). Rather than force these into one identical padding (which
would either bloat the dense lists or cramp the content cards),
codified both as a deliberate two-tier system via
`{% card_classes %}` / `{% card_classes 'dense' %}` - one definition,
two intentional variants, applied everywhere the literal string
previously appeared (including `metric_card.html` itself, which now
reuses this instead of duplicating the string a second time).

**Phase 4 - `status_badge_classes()` and a real bug it caught**:
auditing every `{% include "components/badge.html" %}` call's color
found one genuine inconsistency - a topic's "Pending" status badge was
gray on the new Chapter Detail page (Milestone 12) but amber
everywhere else "Pending" appears (Revision) - fixed to match. While
tracing every badge's color, found `revision/partials/_queue.html`'s
"Upcoming" section badge used
`text="due "|add:schedule.due_date|stringformat:"s"` - the exact
`add`-filter-can't-concatenate-a-string-with-a-date-object bug this
project already hit and fixed twice before (Milestone 11's
Architectural Decisions), which silently rendered that badge
**completely empty** in production. No existing test caught it - the
Revision Queue's tests asserted the section rendered, never what the
badge actually said. Fixed using the same `text`/`secondary`
parameter pattern established for exactly this reason, plus a new
regression test that renders the real page and checks the badge's
actual text, not just its presence. Every template-authored badge
color (i.e. not one already computed by a service like
`readiness_badge_class`) now goes through
`{% status_badge_classes %}`'s five semantic tiers (positive/warning/
danger/info/neutral) instead of a hand-picked color per call site.

**Phase 5 - past/today/future distinction**: `timeline_body.html`
(both timelines) now applies `opacity-75` to a day's card group once
it's strictly before the anchor - a subtle dimming that reads as
"already past" without changing any color, border, or spacing, kept
minimal per this milestone's explicit "avoid visual clutter"
instruction. The Revision Queue's existing Overdue/Due-Today/Upcoming/
Completed bucket coloring already provided a stronger, status-based
past/present/future distinction than a raw date comparison would, so
it was left unchanged.

**Phase 9 - table/list consistency**: audited every `<tr>`/`<li>` row
in a bordered list or table (~30 occurrences across 12 templates) and
found none had a hover state at all. Added `hover:bg-gray-50`
uniformly (skipping the color-coded diff rows on the Dataset Compare
page, which aren't interactive). Also found Lecture Detail's "Chapters
Covered" list was still a plain bulleted `<ul class="list-disc">` -
the one list in the app that never got migrated to the
`bg-white border rounded-lg divide-y` list-item pattern everywhere
else uses (likely because it predated Milestone 12's chapter links,
which is what made it worth revisiting) - converted to match.
Numeric-column alignment (`text-right` on count/percentage cells) was
reviewed and deliberately not swept in: every table's primary numeric
indicator already flows through `progress_bar.html`'s own right-
aligned percentage label, so a second alignment pass over raw count
cells was judged cosmetic-only relative to its effort, not left
silently undone - a documented scope decision, not an oversight.

**Phases 2/6/8/10/11/12** (visual hierarchy, navigation polish, forms,
responsive, accessibility, micro-interactions): reviewed against the
work already done in Milestones 11/12 and found already satisfied -
page headers/section headers/typography scale, nav active-states/
focus-visible rings, form field standardization, responsive card
stacking/table scrolling, skip link/ARIA/table captions, and hover/
focus feedback were all established then and needed no further
change here. This milestone's genuinely new work was the five phases
above; the rest of its checklist served as verification that nothing
had regressed, not a source of new changes.

**Tests**: 370 → **377** (+7): `CardAndBadgeConsistencyTests` (both
tags' every variant, including the neutral fallback for an unknown
variant),
`RevisionUpcomingBadgeRegressionTests` (the actual bug above, asserted
against the real rendered fragment, not just "the section exists"),
and `RoutineWeekNumberingTests`/`RoutineWeekViewTests` updated for the
now-continuous week map (a week with no lecture is a valid, navigable
week; total week counts changed to reflect the real span) plus a new
`test_exam_only_week_still_gets_a_number` covering Phase 1's actual
requirement directly.

**Verification**: `manage.py test` - **377/377 passing**; `manage.py check`
clean; `makemigrations --check --dry-run` reports "No changes
detected" (no model touched anywhere in this milestone). Rebuilt the
compiled Tailwind stylesheet after adding `opacity-75` and
`hover:bg-gray-50` (two classes this milestone introduced that didn't
exist in the prior build) - both now also added to
`CompiledCSSTests.REQUIRED_UTILITIES` (Milestone 11.2) so a future
milestone forgetting to rebuild after adding a class fails loudly
again, not silently. Manually smoke-tested every major page (including
a staff/non-staff pass over `/datasets/`) for template-syntax leaks
and correct status codes after every template edit.

- No models, migrations, importer logic, analytics calculations,
  revision calculations, or timeline windowing logic were touched by
  this milestone - `get_routine_week_map()`'s broadened span is a
  presentation-layer fill-in of an already-sequential numbering, not a
  new calculation, and every other change was templates/components/
  ui_tags only.

---

### Milestone 14 — Production Readiness, Routine Archive & Release Preparation

**Phase 1 - Routine Archive.** Replaced Milestone 12's honest-empty-
state `RoutineResourcesView` placeholder with a real, fully automatic
archive. `routines/services/archive.py` is the entire implementation:
`list_routines()` scans `media/routines/` once per request, keeps only
files matching `^\d{4}-\d{2}\.pdf$` (the `YYYY-MM.pdf` convention),
silently ignores everything else - other extensions, malformed names,
subdirectories - and returns them sorted descending by label, so the
newest filename is always index `0`. `get_latest_routine()` is that
entry. `resolve_routine_file(filename)` is the only function that ever
turns an untrusted filename into a filesystem path, and it rejects
anything before the join happens: the input must fully match the
strict pattern (`re.match` with `^`/`$` anchors) before `_archive_dir()
/ filename` is even constructed, so no `..`, path separator, or
absolute path can reach the filesystem - path traversal is prevented
by construction, not by sanitizing. No database table, no upload
interface, no admin functions: dropping a new `2026-09.pdf` into the
folder is the entire "upload" workflow, exactly as specified.

`RoutineResourcesView` (`/routine/resources/`) resolves `?routine=
<filename>` against the archive, falling back to the latest entry if
the parameter is missing or names something that doesn't exist (never
a 404 for a bad query param - the page just shows the best available
default). `RoutineArchiveFileView` (`/routine/resources/file/
<filename>/`) serves the resolved file via `FileResponse`, inline by
default (for the iframe) or `?download=1` (for the Download button,
`as_attachment=True`) - both routes require login, same as every other
page in the app. `templates/routine/partials/_resources_viewer.html`
(the iframe + Download button + Previous Routines list) is returned as
the full page's body on a normal GET and, unchanged, as the entire
response on an HTMX GET (`?routine=...`) - one template, two contexts,
no duplicated markup. Selecting a previous routine (`hx-get` +
`hx-target="#routine-archive-viewer"` + `hx-swap="innerHTML"` +
`hx-push-url="true"`) swaps the iframe/button/list in place without a
full page reload, while still leaving a real, bookmarkable/back-
button-safe URL behind via `hx-push-url`. An archive with zero PDFs
still renders cleanly via `components/empty_state.html` ("No routine
has been uploaded yet.") instead of a broken iframe.

**Phase 2 - Git Repository Standardization.** This was, in fact, the
project's first real commit - `git status` showed the entire tree
staged as new with no prior history. `.gitignore` gained several
entries that were previously just working by accident (`.venv/`,
`db.sqlite3-journal`, `.coverage`/`htmlcov/`, `*.egg-info/`, OS cruft)
plus one deliberate removal: `validation_report.md` (a regenerated
report from `validate_datasets`, not source data) was untracked and
added to `.gitignore` - it belongs in `Known Issues`/being regenerated
on demand, not committed and going stale. No secrets were found staged
anywhere; `.env` itself was already correctly ignored and never
existed in the tree.

**Phase 3 - Development Workflow.** Documented in README's "Development
Workflow" section as the fixed sequence every change follows: modify
code -> run tests -> `manage.py check` -> Tailwind build -> commit ->
push. This mirrors exactly what Phase 6's CI pipeline automates - the
local workflow and the CI pipeline are the same five checks, one run
by hand and one run automatically.

**Phase 4 - Production Settings.** `settings.py` was rewritten so every
environment-specific value is read from the process environment
(`os.environ`, with `.env` loaded locally via `python-dotenv` for
convenience - a real deployment sets real environment variables and
`load_dotenv` is simply a no-op there since no `.env` file exists).
`SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` all come
from the environment; `DEBUG` still defaults to `True` when unset so
local development and the test suite behave exactly as before with no
`.env` file present. `SECURE_PROXY_SSL_HEADER` was added so Render/
Railway's reverse-proxied HTTPS is recognized correctly. When
`DEBUG=False`: `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE`/
`SECURE_SSL_REDIRECT`/HSTS all turn on - none of this fires in
development, so `runserver` over plain HTTP is unaffected. Email
gained a real SMTP path: with `DEBUG=False` and both
`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` set, Gmail SMTP is used
instead of Milestone 7's console backend (which remains the default
otherwise, unchanged). Static files gained `STATIC_ROOT` +
WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`, placed
directly after `SecurityMiddleware` per WhiteNoise's own
documentation) with a `DEBUG`-conditional storage backend -
`CompressedManifestStaticFilesStorage` in production (requires
`collectstatic`'s manifest) vs. plain `CompressedStaticFilesStorage`
in dev/tests (no manifest requirement, so `{% static %}` never raises
`Missing staticfiles manifest entry` when `collectstatic` has never
been run - discovered by running the new archive tests and fixed
before it could affect every other template test in the suite). A
new `/health/` endpoint (`core.views.HealthCheckView`) answers `{
"status": "ok" }` with no auth and no database query, for the
deployment platform's liveness probe. `LOGGING` was added - plain
`StreamHandler` to stdout/stderr, which Render/Railway capture
directly, so no file handlers or third-party logging service were
introduced.

**Phase 5 - Deployment Preparation.** `DATABASES` now uses
`dj_database_url.config()`: `DATABASE_URL` set selects PostgreSQL (the
convention both Render and Railway populate automatically once a
Postgres add-on is attached); unset, it falls back to the exact same
local `db.sqlite3` file every prior milestone has used, so local setup
needs no changes. `psycopg[binary]` was added to `requirements.txt` as
the Postgres driver. A `Procfile` was added with `release: python
manage.py migrate --noinput` (runs automatically before each deploy on
both platforms) and `web: gunicorn admission_helper.wsgi --log-file -`
(the production entry point in place of `runserver`). `gunicorn` and
`whitenoise` were added to `requirements.txt`. Media persistence
(`media/routines/`) is documented as the deployment platform's
responsibility (a persistent/attached disk) - WhiteNoise only serves
`STATIC_ROOT`, never `MEDIA_ROOT`, by design.

**Phase 6 - CI Readiness.** `.github/workflows/ci.yml` runs on every
push/PR to `main`: checkout -> install Python 3.12 -> install Node 20
-> `pip install -r requirements.txt` -> `npm ci` + `npm run build` in
`theme/static_src/` -> `manage.py check` -> `manage.py makemigrations
--check --dry-run` -> `manage.py test`. This is the exact same
sequence Phase 3's documented local workflow follows, now automated -
not a separate, drifting definition of "passing."

**Phase 7 - Documentation.** `README.md` gained a real "Environment
Variables" reference table (every variable this milestone introduced,
not just the two Milestone 7 originally documented), a "Deployment"
section (Render/Railway steps, `DATABASE_URL`/media-persistence notes,
the `Procfile`'s two process types), and an expanded "Development
Workflow" section spelling out the fixed five-step sequence. This file
(`PROJECT_PROGRESS.md`) documents the Routine Archive's naming
convention, storage layout, and service architecture below and in this
section.

**Testing.** 24 new tests, net +22 (2 obsolete tests removed - see
below): `routines/tests_archive.py` -
`RoutineArchiveServiceTests` (empty archive, missing directory,
descending sort, latest selection, non-PDF files ignored, malformed
filenames ignored, subdirectories ignored, valid resolution, path-
traversal rejection via three distinct traversal attempts, nonexistent
file rejection, non-matching-filename rejection), `
RoutineResourcesViewTests` (login required, empty-archive empty state,
latest-selected-by-default, previous-routines list excludes the
selected entry, explicit selection via `?routine=`, unknown-filename
fallback to latest, HTMX partial-only response), `
RoutineArchiveFileViewTests` (login required, inline-by-default
`Content-Type`, `?download=1` attachment header, 404 on a nonexistent
file, 404 on a path-traversal filename, 404 on a non-PDF filename).
Every test builds its own temporary `MEDIA_ROOT` (via
`tempfile.mkdtemp()` + `override_settings`) so no test depends on or
pollutes a real `media/routines/` folder. `routines/tests_navigation.py`'s
`RoutineResourcesViewTests` (2 tests, Milestone 12) was removed - it
asserted the exact placeholder copy ("No routine PDF has been uploaded
yet.") that no longer exists now that the page is a real archive;
`tests_archive.py` supersedes its coverage (empty state, login
requirement) with fixture isolation the old tests didn't have.

**Verification.** `manage.py test` - **399/399 passing** (377 before
this milestone; +24 new, -2 obsolete removed). `manage.py check` -
clean. `manage.py makemigrations --check --dry-run` - no changes
(Phase 1's service is filesystem-only, no models touched). Query
budgets unaffected - the archive is a filesystem scan, not a database
query, and no existing page's query count moved.

---

### Milestone 15 — Reminder & Notification System

**Phase 1 - Architectural Rule: the Reminder Engine.** `reminders/
services/engine.py` is the one place every reminder type is
registered (`GENERATORS`, keyed by `ReminderLog.ReminderType`) - it
asks "what reminders should be sent right now?" by calling every
generator and filtering the combined result against `ReminderLog`
(Phase 11), rather than exposing "Run Daily Reminder"/"Run Weekly
Reminder"/"Run Exam Reminder" as distinct code paths. Each generator
module (`daily.py`/`weekly.py`/`exams.py`/`revision.py`/`progress.py`)
independently answers "what's due right now?" for its own type and
returns a list of `ReminderJob`s (a plain dataclass: user,
reminder_type, reference_key, context) - `engine.py` never contains
type-specific logic. Adding a future reminder type is exactly: write a
new generator, add one line to `GENERATORS`, add one entry to
`emails/registry.py`.

**No business logic was duplicated** - every generator reads from the
same services every other page in the app already uses:
`progress.services.revision.get_revision_queue()`/
`get_exam_ready_lecture_codes()`, `progress.services.analytics.
get_exam_readiness()`/`get_lecture_completion_stats()`,
`progress.services.dashboard.get_completion_stats()`, and
`routines.services.timeline.get_routine_week_map()`/
`get_routine_week()` (the exact same Routine Week implementation the
Routine/Exam Timelines use - Phase 2's trigger is not a second week
calculation). One small extraction was made to enable this cleanly:
`routines/services/exam_coverage.py: get_exam_coverage(exam)`, pulled
out of `ExamDetailView` (previously the only place that resolved an
exam's covered subjects/chapters/lectures) so the Exam Detail page and
the new exam reminder emails share one implementation instead of the
view growing a second copy.

**Phase 2 - Weekly Overview.** Triggers on the first day of a Routine
Week - not Saturday, Sunday, or the ISO calendar week.
`get_routine_week_map()` already keys every week by the Monday that
starts its ISO span (see Milestone 13's docstring for that function),
so "first day of Routine Week N" is exactly "today is a Monday whose
(iso_year, iso_week) is in the map" - no second definition of "week
boundary" was introduced. The email lists lecture/exam/revision counts
plus a day-by-day schedule (Monday through Sunday, weekly/monthly
exams highlighted), all derived from `get_routine_week()`'s lecture
list and a plain `Exam` date-range query - the same kind of direct
query the timeline modules already make, no completion calculation
involved.

**Phase 3 - Daily Study Agenda.** One reminder per active user per
calendar day, gated on a per-user configurable delivery time (Phase
7's `daily_agenda_time`, default 10:00) - the only reminder type with
a user-configurable time-of-day gate. Today's lectures/exams come from
plain date-filtered queries; today's/overdue revisions reuse
`get_revision_queue()`'s existing bucketing wholesale. An empty day
still sends "No scheduled study activities today." rather than being
silently skipped, per the milestone's explicit instruction.

**Phase 4 - Revision Reminder.** Fires the day a `RevisionSchedule`
becomes due. "One reminder per lecture per due occurrence" falls out
of the idempotency design for free: each of a lecture's three revision
levels is its own `RevisionSchedule` row, and that row's own id is the
`ReminderLog` `reference_key` - no separate occurrence-tracking was
needed.

**Phase 5 - Exam Reminders.** Weekly Exams: 1 day before + exam-day
morning. Monthly Exams: 7/3/1 days before + exam-day morning. The
exam-day "morning" gate (`EXAM_DAY_MORNING_TIME = 08:00`, not
user-configurable - only the Daily Agenda's time is, per Phase 7's
preference list) exists so a scheduler running more than once a day
never fires a same-day reminder before a reasonable hour. Coverage/
readiness data is entirely reused: `get_exam_coverage()` for covered
subjects/chapters/lectures, `get_exam_readiness()` for the percentage/
label, `get_exam_ready_lecture_codes()` to compute "remaining lectures
to revise" as a set difference against covered lectures - nothing here
recomputes any of those three calculations.

**Phase 6 - Weekly Progress Summary.** Fires the same Monday Phase 2's
Weekly Overview does (the day a completed Routine Week hands off to
the next one), but summarizes the week that just ended
(`today - 7 days`'s Monday) instead of the week ahead. Lecture
completion reuses `get_lecture_completion_stats()`; overall progress
reuses `get_completion_stats()`'s existing percentage - both computed
once per user, not re-derived.

**Phase 7 - Notification Preferences.** `NotificationPreference`
(one row per user, created lazily): each reminder type's on/off
switch, the Daily Agenda's delivery time, and a free-text IANA
timezone (validated against `zoneinfo.available_timezones()`).
`reminders/services/preferences.py: get_preferences()` is the only way
generators read this - it returns the persisted row, or an *unsaved*
instance (model field defaults apply) for a user who has never visited
`/reminders/preferences/`, so "sensible defaults" apply without
needing to backfill a row for every existing user. The settings page
itself (`NotificationPreferencesView`) does `get_or_create` on both GET
and POST, since visiting the page is what actually persists a row.

**Phase 8 - HTML Email System.** `templates/emails/base.html` is a
table-based, inline-styled layout - deliberately not built on the
app's own `base.html` (Tailwind classes and `<style>` blocks are
unreliable across email clients, many of which strip both). Six
content templates extend it. Plain-text alternatives (Phase 8's other
requirement) are *generated*, not hand-maintained as a second template
per type: `emails/renderer.py` strips tags from the already-rendered
HTML and collapses whitespace - every template was written with short,
readable block structure specifically so this reads cleanly, avoiding
two representations of the same content silently drifting apart.

**Phase 9 - Delivery Layer.** Three separate concerns, three separate
modules: generation (`services/*.py`, pure - reads the database,
never sends anything), rendering (`emails/renderer.py`: `ReminderJob`
-> subject/html/text strings, no I/O), delivery (`emails/delivery.py`:
the *only* file in this entire feature that imports
`django.core.mail`). The engine calls `delivery.send_reminder(job)`
and never sees an SMTP detail; swapping providers (SES/SendGrid/
Mailgun) only ever means changing `EMAIL_BACKEND` in `settings.py`
(Django's own backend abstraction, already wired for the SMTP/console
split since Milestone 14), never any of these three modules or
anything upstream of them.

**Phase 10 - Scheduling.** Five management commands
(`send_daily_agenda`, `send_weekly_overview`, `send_exam_reminders`,
`send_revision_reminders`, `send_weekly_progress`), each a thin
wrapper calling `engine.run(reminder_types=[...])` and printing a
count. Each accepts `--dry-run`. None of them care what invokes them -
cron, Render/Railway Scheduled Jobs, GitHub Actions, Celery beat all
work unchanged, since a management command is the scheduler-agnostic
interface Django already provides.

**Phase 11 - Duplicate Protection.** `ReminderLog` (user,
reminder_type, reference_key) with a `UniqueConstraint` on all three -
a real database constraint, not just an application-level check, so
duplicate protection survives a process restart or two scheduler runs
racing each other (the constraint itself would reject the race's
loser, not just the engine's own pre-check). `reference_key`'s format
is chosen per type to mean "this exact occurrence": an ISO date for
Daily Agenda/Weekly Overview/Weekly Progress, a `RevisionSchedule` id
for Revision Due, an `"<exam_id>:<offset_label>"` pair for Exam
Reminders (so 7-days-before and 1-day-before are distinct occurrences
of the same exam, each sent exactly once).

**Testing.** 56 new tests across four files: `tests.py` (
`NotificationPreference` defaults, `get_preferences()`'s persisted-vs-
unsaved-default behavior, `ReminderLog`'s uniqueness constraint, the
preferences view - login required, GET lazily creates a default row,
POST saves/validates an IANA timezone, never touches another user's
row), `tests_generators.py` (every trigger condition per phase above:
Routine Week first-day-only for Weekly Overview/Progress including a
non-Monday and an out-of-range date, weekly/monthly exam offsets
including the exam-day morning gate and cross-type isolation, revision
due-date/completed-schedule/before-due-date, the Daily Agenda's
configurable-time gate and no-activity flag - plus one preference-
disabled test per type), `tests_emails.py` (every registered reminder
type renders non-empty subject/HTML/text, the plain-text fallback
never contains a literal `<`, the "no activity"/"all exam-ready"/
"today vs. tomorrow" branches each render correctly), `tests_commands.py`
(all five commands run cleanly, `--dry-run` sends and logs nothing
while still reporting a count, a second `engine.run()` for the same
occurrence is a no-op, a user with no email address is skipped at
delivery but still logged so it isn't retried forever, same-
`reference_key`-different-`reminder_type` both still send). Every test
builds its own fixtures (`core.test_utils.build_sample_dataset()` plus
hand-built Routine/Lecture/Exam rows for week-aligned scenarios,
following `routines/tests_navigation.py`'s established pattern) -
nothing depends on wall-clock time or date, including the exam-day
morning gate and the Daily Agenda's delivery-time gate, both of which
needed a `current_time` parameter threaded through every generator (and
`engine.get_due_reminders()`/`run()`) specifically so tests never
depend on when they happen to run.

**Verification.** `manage.py test` - **455/455 passing** (399 before
this milestone; +56 new). `manage.py check` - clean. `manage.py
makemigrations --check --dry-run` - no changes after the one real
migration (`reminders.0001_initial` - `NotificationPreference`,
`ReminderLog`). No existing page's query count changed - every
reminder-related query happens inside a management command's process,
never a request.

---

### Milestone 15.1 — Reminder Administration, Theme System & UX Polish

**The Reminder Engine was not touched.** Every generator in
`reminders/services/`, the trigger conditions in each, `emails/
renderer.py`, `emails/delivery.py`'s core send path, and every
management command's behavior are exactly what Milestone 15 built.
This milestone's two changes to `engine.py` are both strictly additive
and both default to identical behavior when unset: `users=None` (every
active user, unchanged) narrows which users a generator considers -
for Reminder Administration's recipient selector - without changing
what's due for whichever users are considered; `triggered_by=None`
(defaults to `AUTOMATIC`) records manual-vs-automatic on `ReminderLog`
for the Activity Log. `engine.run()` also now returns a `ReminderResult`
(job + delivered + error) instead of a bare `ReminderJob` list, so
Reminder Administration can show real delivery outcomes - none of the
five existing management commands needed to change since they only
ever checked `len(sent)`.

**Phase 1 - Timezone dropdown.** `NotificationPreferenceForm.timezone`
became a `ChoiceField` (`reminders/services/timezones.py:
get_timezone_choices()`) instead of free text validated after the
fact. Choices are still every valid IANA identifier - `zoneinfo.
available_timezones()`, filtered to "Region/City" names plus bare
`"UTC"` (excluding deprecated aliases like `Etc/GMT+12`) - labeled with
their current UTC offset (`"Asia/Dhaka (UTC+06:00)"`). A native
`<select>` is genuinely searchable in every major browser (typing
jumps to the next matching option) without any custom JS combobox,
and - unlike a `<datalist>` + text input - structurally cannot submit
a value outside the list, satisfying "Do NOT allow free-form timezone
input" by construction rather than by validation alone. Validation and
storage are unchanged: still a real IANA name in `NotificationPreference.
timezone`.

**Phase 2 - Reminder Navigation.** `base.html`'s nav `<ul>` changed
from `overflow-x-auto flex-nowrap` (Milestone 11's original fix for a
crowded bar - it scrolled instead of overflowing) to `flex-wrap`: a
crowded header now wraps onto a second line instead of scrolling
either direction, and needed no new component or markup duplication -
one class swap on the exact same shared nav every page already uses.

**Phase 3/3.5 - Reminder Administration + Email Diagnostics.**
`/reminders/admin/` (`ReminderAdminView`, staff-only via the same
`_StaffOnlyMixin` pattern `routines.views` already established in
Milestone 12 - a non-staff user gets a real 403, not a hidden link).
`reminders/services/diagnostics.py` inspects `settings.EMAIL_*` and
reports backend/status/from-address/host/port/encryption/authenticated-
user/timezone as plain metadata - `EMAIL_HOST_PASSWORD` is read only
to check *whether it's set*, never returned in any value the template
can render (`test_password_never_exposed` asserts this directly against
the full config dict, not just the fields the template happens to
show). Status is "Ready" (SMTP backend, everything present), "Configuration
Incomplete" (SMTP backend, something missing - each missing setting
gets its own friendly guidance line), or "Sending Disabled" (any other
backend, which is honestly labeled as not actually delivering to
recipients). "Test SMTP Connection" opens and immediately closes a
real connection via `django.core.mail.get_connection()` without
sending anything, surfacing the exact SMTP exception on failure. "Send
Test Email" (`diagnostics.send_test_email()`) uses a dedicated
`templates/emails/test_email.html` through the shared `emails/base.html`
layout and `renderer.to_plain_text()` (made public this milestone
specifically so this doesn't duplicate the tag-stripping logic) but
calls `EmailMultiAlternatives` directly - it deliberately never touches
`engine.py` or `ReminderLog`, exactly as specified ("this should bypass
the reminder engine"), and the admin dashboard shows the exact HTML
(via an `<iframe srcdoc>`, sandboxed and never `|safe`-marked - Django's
attribute-context autoescaping handles it correctly) and plain-text
bodies that were sent.

**Phase 4/5/6/7 - Reminder Test Center.** One form, two buttons
(Preview / Send Now), a recipient `<select>` (every active user,
defaulting to the logged-in administrator) and a reminder-type
`<select>` (the six real types, plus "Run Reminder Engine (all types)"
for `reminder_types=None`). Both buttons call straight into
`engine.get_due_reminders()`/`engine.run()` with `users=[recipient]` -
the *exact* trigger-condition and duplicate-protection logic a real
scheduled run would use, never a parallel "preview mode" calculation.
Preview renders whatever's actually due via the same `renderer.
render_reminder()` every real send uses; if nothing's due (unmet
trigger condition, or already sent - duplicate protection working as
intended), the page says so honestly rather than showing a fake
preview. Every manual send is tagged `triggered_by=MANUAL` on its
`ReminderLog` row and reported back with success/failure, timestamp,
recipient, and reminder type (Phase 7's delivery feedback) - a failed
delivery shows Django's own exception text, not a generic "something
went wrong."

**Phase 8 - Reminder Activity Log.** The last 25 `ReminderLog` rows,
displayed with status (Success/Failed) and trigger (Automatic/Manual)
badges - reusing `ReminderLog` itself, extended with `status`/
`error_message`/`triggered_by` fields (Milestone 15's original three
fields - user/reminder_type/reference_key/sent_at - are untouched, and
its uniqueness constraint is unaffected). `engine.run()` now wraps
`send_reminder()` in a `try`/`except` so a real SMTP exception is
caught, recorded (`status=FAILED`, `error_message=str(exc)`), and
still logged - Phase 11's "never sent twice" was already understood to
mean "never re-attempt this exact occurrence," and a caught failure
now makes that explicit rather than silently crashing the whole run.

**Phase 9/10 - Global Theme System & Dark Mode.** `theme/static_src/src/
styles.css` gained `@custom-variant dark (&:where(.dark, .dark *));` -
class-based, not the media-query strategy, because "System" needs to
be *forced* to Light or Dark on demand, which a pure media query can't
do. `base.html`'s `<head>` runs a small inline script before the body
paints: reads `localStorage.getItem("theme")` (`"light"`/`"dark"`/
`"system"`, default `"system"`), computes the effective dark/light
state (checking `prefers-color-scheme` live for `"system"`), and
toggles the `.dark` class on `<html>` - no flash of the wrong theme,
and it defines `window.setTheme()` (used by the toggle's `onchange`)
plus a `matchMedia` change listener so a `"system"` user's OS switching
themes updates the page live without a reload. `components/theme_toggle.html`
(a native `<select>` - System/Light/Dark) is included once from
`base.html`, so it's on every page for every user, authenticated or
not - never gated behind Reminder pages. No database field: the whole
feature is `localStorage` plus one CSS variant. Dark variants were
added to `base.html` (body/header/skip-link), all five `core.
templatetags.ui_tags` class-string functions (`card_classes()`,
`status_badge_classes()`, `button_classes()`, `field_classes()`,
`workspace_toolbar_classes()` - each edited to keep its original,
already-tested light-mode substring intact and append `dark:` classes
after it, so no existing test needed to change), and every file in
`templates/components/` (`page_header`, `section_header`, `card`,
`metric_card`, `progress_bar`, `empty_state`, `loading_skeleton`,
`select_field`, `text_field`, `form_field`, `auth_card`, `smart_back`,
`timeline_body`) plus the two pages Milestone 15/15.1 directly built
(`reminders/preferences.html`, `reminders/admin/dashboard.html`).
Because most of the app's cards/badges/buttons/forms/tables already
route through these shared functions/components (Milestone 13's
consolidation work), this gives real, broad dark-mode coverage through
the "Shared Component Rule" rather than a page-by-page sweep - see
Known Issues for what a shared-component-only pass doesn't reach.

**Phase 11 - Accessibility.** The theme toggle and every Reminder
Administration action are native `<select>`/`<button>`/`<input>`
elements - no custom widget, so keyboard operation (Tab, Space/Enter,
Arrow keys to cycle a `<select>`'s options) is the browser's own,
already-tested behavior, not something this milestone had to
implement or verify separately. Dark-mode text/background pairings
throughout reused the same gray/slate scale Tailwind ships
pre-balanced for contrast (`gray-100`/`gray-400` on `slate-800`/
`slate-900`, matching the light-mode `gray-900`/`gray-500` on `white`/
`gray-50` pairings' contrast ratios) rather than picking new colors
per component.

**Testing.** 37 new tests: `reminders/tests.py` gained 6 (searchable
timezone dropdown rendering, `get_timezone_choices()`'s content/
labels/exclusions/sorting/IANA-validity, the invalid-choice rejection
message), `reminders/tests_admin.py` is entirely new with 25 (staff-
only access including POST, every diagnostics status branch including
the password-never-exposed assertion checked against the *full*
returned dict, the SMTP connection test's honest non-SMTP-backend
message, the standalone test email never touching `ReminderLog`,
preview/send against a selected recipient - both the "found" and
honest "nothing due" paths, a deterministic forced-due-job send that
asserts `triggered_by=MANUAL` and `status=SUCCESS`, a forced delivery
failure that asserts `status=FAILED` and shows up as "Failed" in the
activity log, and `users=` targeting on `engine.get_due_reminders()`
directly - excluded/included/default-to-everyone), `core/tests_ui.py`
gained 6 (`ThemeSystemTests`: toggle present on both an authenticated
and an anonymous page, `window.setTheme` defined before the toggle
renders, a real `<select>` not a custom widget, no `theme` field on
the User model; plus a nav no-longer-horizontally-scrolls check).
`CompiledCSSTests.REQUIRED_UTILITIES` gained `.flex-wrap{` and four
`dark\:` utilities, so a stale/pre-`npm run build` CSS bundle fails
this test loudly instead of shipping an unstyled (or un-dark-moded)
dashboard - the same incident class Milestone 11.1 originally caught
this test for.

**Verification.** `manage.py test` - **492/492 passing** (455 before
this milestone; +37 new). `manage.py check` - clean. `manage.py
makemigrations --check --dry-run` - no changes after the one real
migration (`reminders.0002_reminderlog_error_message_reminderlog_status_and_more` -
three new `ReminderLog` fields, all with defaults, backward-compatible
with every existing row). `npm run build` re-run in `theme/static_src/`
to compile the new `flex-wrap`/`dark:`/admin-dashboard utility classes.
No existing page's query count changed.

---

### Milestone 15.2 — Design System Refinement & Multi-Dimensional Progress

**Part 1 - Global Navigation Redesign (highest priority).** `base.html`'s
nav was rebuilt from a single flat `<ul>` (Milestone 15.1's `flex-wrap`
fix, which resolved horizontal scrolling but not visual crowding) into
three pieces, using native `<details>`/`<summary>` disclosures - zero
JS, fully keyboard-accessible (Tab/Enter/Space work out of the box),
following this project's own precedent of preferring a plain-HTML
mechanism over a hand-rolled widget (the same reasoning `smart_back.html`
and `theme_toggle.html` already used):

- A horizontal main-nav row (Dashboard/Routine/Exams/Progress/
  Revision/Analytics, plus "Routine Resources" for non-staff users -
  unchanged from before), visible on `sm:` and up.
- A **Staff Menu** dropdown (staff users only - Datasets, Reminder
  Administration), replacing those two items' previous permanent slot
  in the main row.
- A **User Menu** dropdown (every authenticated user - Profile, Theme,
  Logout), replacing the separate "Notifications" link and the
  floating standalone theme `<select>` Milestone 15.1 introduced.
  "Profile" is a new, deliberately minimal page (`/accounts/profile/`,
  `core.views.ProfileView`) - account facts plus links onward to
  Notification Preferences and (staff only) Reminder Administration;
  not a new academic feature, just a home for account-level actions.
- A mobile hamburger `<details>` (`sm:hidden`) - one flattened list of
  every link above, shown as a stacked menu on narrow screens.

The one non-obvious constraint this rebuild had to satisfy: `core/
tests_ui.py`'s `test_nav_marks_only_the_current_page` asserts exactly
one `aria-current="page"` in the whole page's HTML - not "exactly one
visible" - since both the desktop nav and the mobile hamburger's
markup exist in the DOM simultaneously (CSS `hidden`/`sm:flex` only
controls what's *painted*, not what's present), duplicating
`aria-current` logic into both copies would have produced two matches
on a narrow-viewport render regardless of which one is visually shown.
Resolved by making the desktop nav the single canonical, aria-current-
bearing copy and leaving the mobile hamburger's duplicate links
without it entirely - a very minor loss (mobile users lose one
redundant "you are here" signal inside a collapsed menu) traded for
never needing runtime logic to decide which copy is authoritative.
`routines.tests_navigation.AdminVsStudentNavigationTests` (staff sees
`Datasets`'s URL and never "Routine Resources" text; non-staff the
reverse) was preserved exactly as before - Datasets moved into a
dropdown, but the underlying staff/non-staff exclusivity is unchanged.

**Parts 2-4 - Multi-Dimensional Progress System & Progress Service.**
`progress/services/progress_service.py` is new, additive, and
completely independent of `analytics.py`/`dashboard.py`/`revision.py`:
none of their existing return values changed, and `revision.
is_lecture_completed()`'s all-four-required definition (which decides
whether a lecture's revision schedule gets created) is untouched.
Investigated first, before writing any code: an audit of `core.
test_utils.build_sample_dataset()` found exactly one deliberately
partial topic (`topic2`: `class_done=True` only) and traced every
existing test whose expected percentage would change if the
underlying formula were swapped in place (~8-10 assertions across
`progress/tests.py`/`dashboard/tests.py`, all keyed on that one
fixture row) - confirming the new system needed to be a **separate**
module, not a replacement, to satisfy both "replace the binary
progress system" and "regression tests must continue to pass"
simultaneously (Part 18).

Every study topic now contributes four independent units - Class,
Notes, Revision, Practice, each exactly 25% - instead of requiring all
four before any credit shows (a topic with `class_done=True` alone is
25%, not 0%). Colors are fixed and permanent (`bg-blue-500`/
`bg-emerald-500`/`bg-amber-400`/`bg-purple-500`), defined once in
`DIMENSION_META` and never re-picked per page. Aggregation is
hierarchical exactly as specified - Topic -> Chapter -> Lecture ->
Subject -> Exam -> Dashboard/Analytics - each scope built from the
same four `Progress` boolean columns via the same join-prefix `Sum(
Case(When(...)))` technique `analytics.completed_case()` already
established, applied per-dimension instead of requiring all four
together. Every list-page scope has a `get_bulk_*()` twin (subjects,
chapters, lectures, lecture-by-code, exams) costing exactly one query
regardless of row count - verified directly in
`tests_progress_service.py` via `CaptureQueriesContext` (Part 17: "no
N+1 queries"). Exam progress reuses the same by-lecture-code bulk
pattern `analytics.get_lecture_completion_stats()`/`get_exam_readiness()`
already use for `covered_lectures` (a JSON list of codes, not a FK).

**Parts 5-6 - Progress Component.** `templates/components/
progress_meter.html` renders from a `progress_service` result dict
only - no page computes any of these numbers itself. Rendering adapts
purely to `progress.total_units` (never a caller's choice), per Part
5's exact tiers: <=16 units renders one block per unit, grouped by
dimension (matching the milestone's own worked example - a 2-topic
chapter with Class1/Class2/Notes1 done renders Blue/Blue/Green/5
empty, not "37.5%"); 17-32 units renders the same blocks narrower;
>32 units renders one continuous 4-segment bar (one segment per
dimension, each internally filled proportional to that dimension's own
percentage) instead of dozens-to-hundreds of tiny blocks. Supports an
optional legend (`show_legend`), an optional "N/M units" caption
(`show_percentage`), and per-segment tooltips (`tooltip`) - all via
`default_if_none`, not Django's plain `default` filter, after that
exact footgun surfaced during testing: `default` substitutes on *any*
falsy value, so an explicit `tooltip=False` was silently replaced by
the "on" default (the same class of filter-semantics trap this
project has hit before with the `add` filter's silent-failure mode).
Carries `role="progressbar"` + `aria-valuenow`/`aria-label` itself, so
swapping a page's old `progress_bar.html` for this component needed no
change to `core/tests_ui.py`'s existing
`test_progress_bars_have_progressbar_role` test (which hits the real
`/progress/` page, not a component-unit render).

Wired into the pages where the visual bar genuinely represents raw
per-topic Class/Notes/Revision/Practice data: Subject/Chapter Detail
(header meter + per-row chapter/lecture table meters), Progress
Overview (overall meter + per-subject table), the Dashboard's "Overall
Completion" widget, and the Analytics Subjects/Chapters/Lectures
tables. Every existing text caption next to these meters (e.g. "12 / 20
topics completed") was left wired to its original `analytics.py` data
source, unchanged - only the *visual bar* was swapped, so no
regression test asserting those numbers needed to change. Deliberately
**not** swapped: the Dashboard's Revision-completion bar, `revision/
partials/_stats.html`, `exams/detail.html`'s readiness bar, `analytics/
partials/_insights.html`'s bars, and `routine/partials/_lecture_card.html`'s
timeline-card bars - none of these represent the four-dimension
Class/Notes/Revision/Practice breakdown (they're revision-schedule
completion, blended readiness scores, or other insight metrics), so
converting them would have been semantically wrong, not just
unnecessary.

**Parts 7-9 - Typography, Cards, Hierarchy.** `card_classes()` gained a
`variant` parameter ("primary" - unchanged default, kept byte-for-byte
identical to preserve every existing test asserting its exact output;
"secondary" - a quieter nested surface, `bg-gray-50`/`dark:bg-slate-900`;
"metric" - visually identical to primary, named separately so a stat-
tile call site self-documents what kind of card it is) - Part 9's
"three reusable card variants," implemented as one shared function
extension rather than three new components. `metric_card.html` now
passes `variant='metric'` explicitly.

**Part 10 - Analytics Tabs.** `templates/analytics/_nav.html`'s
underline-tab strip (which used `overflow-x-auto`, in tension with
this project's own "no horizontal scrolling" rule since Milestone
15.1, Phase 2) was replaced with a segmented-pill tab track (`bg-gray-100`/
`dark:bg-slate-800` container, active tab a raised white/`slate-700`
chip with `shadow-sm`) using `flex-wrap` instead.

**Part 11-12 - Dark Mode & Empty States.** `empty_state.html` gained a
small inline glyph (three centered dots, not an illustration - Milestone
11's "no illustrations" instruction still applies) and tighter vertical
padding (`py-6`, was `py-8`), so an empty table/list takes up
noticeably less vertical space without losing its friendly tone.

**Part 13-14 - Routine Resources & Login Polish.** The PDF viewer's
iframe grew a `min-h-[420px]` floor (so it never collapses uncomfortably
short on short viewports) and dark-mode-aware borders; "Previous
Routines" became a row of pill-style links instead of a plain divided
list, more scannable when there are several archived routines. Login/
Register gained dark-mode classes and a touch of top margin - spacing/
alignment only, per Part 14's explicit "no functional changes."

**Part 15-16 - Component Audit & Accessibility.** Reviewed every
shared component for dark-mode/focus-state consistency; found
`components/auth_card.html` has been unused dead code since it was
introduced (neither `login.html` nor `register.html` ever adopted it) -
left as-is rather than force a restructure of two auth-flow templates
this late, but flagged below as a real, documented gap rather than
silently ignored. Every new interactive element this milestone added
(nav disclosures, Progress Component) is a native, standards-based
control (`<details>`/`<summary>`, `role="progressbar"`) rather than a
custom widget requiring hand-built keyboard handling.

**Part 17 - Performance.** Every Progress Service scope - single or
bulk - costs exactly one query, verified directly via
`CaptureQueriesContext` in `tests_progress_service.py`, not just
asserted in a comment. No page's total query count was measured against
a fixed historical budget this milestone (unlike Milestones 12-15,
which track specific pages against specific ceilings) since Progress
Service queries are additive to already-established pages - see Query
Count Summary below for the exact per-page deltas.

**Testing.** ~37 new tests: `progress/tests_progress_service.py` (20 -
partial-credit vs. binary-formula behavior on the fixture's one
partial topic, full hierarchical aggregation Topic->Chapter->Lecture->
Subject->overall, exam progress via `covered_lectures`, every bulk
function's one-query guarantee and numeric agreement with its single-
scope equivalent, and an explicit confirmation that a partially-
progressed lecture never triggers a revision schedule), `core/
tests_ui.py` (`ProgressMeterTests` - small/medium/large tier
rendering, the spec's own worked example reproduced exactly, legend/
tooltip toggling including the `default_if_none` fix, the accessible
role/label; `NavigationRedesignTests` - hamburger presence, User Menu
contents, Staff Menu shown/hidden by role; a nav-classes test for the
new card variants), `core/tests.py` (`ProfileViewTests` - login
required, staff-only Reminder Admin link).

**Verification.** `manage.py check` - clean. `manage.py makemigrations
--check --dry-run` - no changes (Progress Service is presentation-
layer only, no new models). `npm run build` re-run for the Progress
Component's fixed dimension colors, the analytics tabs' active-chip
shadow, and the hamburger's marker-hiding utility; `CompiledCSSTests.
REQUIRED_UTILITIES` extended accordingly.

---

### Milestone 15.3 — Version 1.0 Release Preparation

No application code changed - this milestone is entirely
documentation, repository hygiene, and git structure, exactly as
specified ("No new application features should be added"). The one
settings change (`TIME_ZONE` becoming env-configurable, Part 7) is a
configurability improvement with the exact same default behavior as
before, not a feature.

**Part 1 - Repository Audit.** Confirmed clean before making any
changes: no `.env` file exists anywhere (only `.env.example`), no
`db.sqlite3`/`staticfiles/`/`media/` tracked or even present outside
test tempdirs, `node_modules/` correctly ignored via `theme/
static_src/.gitignore`, `package-lock.json` correctly tracked (lockfiles
should be committed). Added `.claude/` (this project's Claude Code
session directory - not something a real clone should carry) and
`*.bak` to `.gitignore` for hygiene. Intentionally-retained legacy
files documented in the README's Documentation section rather than
left unexplained: `Varsity_Admission_Tracker_Architecture_v1.md` (the
project's earliest draft, under its original working title),
`02_Database_Design.md` (superseded by `02_Database_Design_v1.1.md`
but kept per the Milestone 2 Architectural Decision to never silently
delete a design-phase document), and `validation_report.md`
(regenerated by `validate_datasets`, git-ignored since Milestone 14).

**Part 2/14 - Git Structure.** `docs/GitWorkflow.md` documents the
`main`/`develop`/`feature/*`/`bugfix/*`/`hotfix/*`/`release/*` model
and, per the user's own explicit instruction closing this milestone's
brief, the rule that takes effect the moment `v1.0.0` is tagged: no
direct commits to `main` ever again - every change starts on a
`feature/*`/`bugfix/*` branch off `develop`, merges via PR, and only
reaches `main` through a `release/*` branch once
`RELEASE_CHECKLIST.md` is fully satisfied. This is the project's first
real git history - every prior milestone's work existed only as
uncommitted/staged changes in this working tree (confirmed via `git
log`, which had no commits at all before this milestone) - so `main`
was created from scratch as the very first commit, immediately
followed by `develop` branching off it.

**Part 3/4 - Documentation Structure & README Rewrite.** `docs/`
created with five files (Architecture, Deployment, DeveloperGuide,
UserGuide, GitWorkflow) plus the v1.0.0 release notes.
`README.md` was restructured into the exact section order specified:
Overview, Features, Screenshots (placeholder), Installation,
Configuration, Running Locally, Running Tests, Tailwind Build,
Reminder Scheduler, Deployment Overview, Project Architecture,
Versioning, Version 1 Scope, License - condensing the deep-dive
content that used to live inline (full Reminders/Progress System/
Routine Archive explanations) into links out to `docs/UserGuide.md`/
`docs/Architecture.md`/`docs/Deployment.md`, so the README itself stays
a genuine quick-start rather than growing without bound as the README
always had before this milestone's constraint ("a new developer
should be able to clone and run the project using only the README" -
still true, just achieved via links rather than one ever-longer file).

**Part 5 - CHANGELOG.** `CHANGELOG.md` created in Keep a Changelog
format with the project's first entry, `[1.0.0]`, summarizing every
milestone from project inception through 15.2 under Added/Changed/
Fixed/Internal - including the real bugs found and fixed along the
way (the `add` filter's silent failure on the revision queue's
"Upcoming" badge, the `default` vs `default_if_none` footgun in the
Progress Component, the sparse Routine Week map, the stale-Tailwind-
build incident, the WhiteNoise manifest-storage/test conflict) rather
than only listing features - a changelog that hid its own bug history
would be less useful to a future maintainer than one that shows what
broke and why.

**Part 6 - KNOWN_ISSUES.** `KNOWN_ISSUES.md` consolidates every
"Known Issues" entry across Milestones 13-15.2 into one tracked list,
organized by area (UI/Responsive, Dark Mode Coverage, Reminders,
Deployment/Operations, Component Hygiene), plus the milestone's own
example categories (navigation-at-medium-widths, responsive header
refinement, dashboard spacing, dark mode refinements) added honestly -
hedged as "not yet verified/reported" rather than asserting bugs that
were never actually reproduced. Explicitly scoped against the README's
"Version 1 Scope" - out-of-scope-by-design items (multi-tenant use,
PDF parsing, a calendar view, a mobile app) are not repeated here as
if they were deferred bugs.

**Part 7 - Environment Configuration.** Reviewed every environment
variable end to end. `TIME_ZONE` was the one genuine gap - hardcoded
in `settings.py` since the project's very first milestone - made
env-configurable with the exact same default (`Asia/Dhaka`) so no
existing deployment's behavior changes. `SECRET_KEY`/`DEBUG`/
`ALLOWED_HOSTS`/`DATABASE_URL`/`EMAIL_*`/`CSRF_TRUSTED_ORIGINS` were
already fully environment-driven since Milestone 14; confirmed Session/
CSRF cookie security has no separate variable (it's automatic under
`DEBUG=False`) and documented that explicitly in `.env.example` rather
than leaving it unstated. `.env.example` rewritten with a comment
explaining every variable's purpose and default, not just its name.

**Part 8 - Deployment Guide.** `docs/Deployment.md` expands the
README's deployment overview into the full ten-section guide the
milestone's checklist specifies: PostgreSQL, static files/WhiteNoise,
media persistence, SMTP, the reminder scheduler (explicit about the
fact that nothing sends a reminder automatically until a platform
Scheduled Job is configured - this was already true and already
documented as a Known Issue, now given a proper home), superuser
creation, initial data import, health check, and a step-by-step
post-deploy verification list.

**Part 9 - Versioning.** Semantic Versioning adopted and documented in
the README's new "Versioning" section: MAJOR for breaking changes,
MINOR for backward-compatible features, PATCH for bug-fix-only
releases - cross-referenced from `CHANGELOG.md` and
`RELEASE_CHECKLIST.md` rather than restated in three places.

**Part 10 - Release Checklist.** `RELEASE_CHECKLIST.md` created,
covering code quality, frontend/CSS, static files, environment,
backup, documentation, git, deployment, smoke test, and post-release -
written to apply to every future tagged release, not just v1.0.0.

**Part 11 - GitHub Preparation.** No remote exists yet for this
repository (confirmed via `git remote -v`), so repository description/
topics/branch-protection settings are GitHub-side configuration to be
done once a remote is actually created - documented as the next
operational step in `docs/GitWorkflow.md` rather than performed here
(nothing to configure against yet). No GitHub Actions changes were
made beyond what Milestone 14 already established (`.github/workflows/
ci.yml`), matching the instruction not to add CI unless already
desired - it already was.

**Part 12/13 - First Version Tag & Release Notes.** `v1.0.0` tagged on
`main` after every check in `RELEASE_CHECKLIST.md` passed.
`docs/ReleaseNotes-v1.0.0.md` summarizes the release for an actual
reader (features, architecture, design, reminders, progress tracking,
timelines, analytics, theme support) rather than restating the
changelog's bullet-point format.

**Part 15 - Final Verification.** `manage.py test` - full suite
passing (exact count in Testing below). `manage.py check` - clean.
`manage.py makemigrations --check --dry-run` - no changes (the one
settings.py edit this milestone made has no model impact). No new
static assets were added, so no missing-static-file risk; `npm run
build` re-run as a matter of course before tagging, per `RELEASE_
CHECKLIST.md`'s own first section.

**Testing.** No new automated tests were added - this milestone
changed documentation, repository files, and one environment-variable
default's source, none of which are unit-testable in a way that adds
signal beyond the existing `manage.py check`/test-suite run. The full
existing suite (529 tests as of Milestone 15.2) was re-run in full to
confirm the `TIME_ZONE` change didn't alter any date/time-dependent
test's behavior - it didn't, since the default value is identical to
before.

---

### Milestone 16 — GitHub & Production Repository Setup

Infrastructure only, no application code changed. Created the GitHub
repository (`muhaiminul00/admission-helper`, private) via `gh repo
create` per the milestone's explicit instruction not to use the
browser; pushed `main`/`develop`/the `v1.0.0` tag (all three verified
present via `gh api`, not just assumed from a successful `git push`);
set the repository description, topics (`django`, `education`,
`study-planner`, `admission-helper`, `python`, `tailwindcss`,
`productivity`), and confirmed the default branch is `main`. Added
`.github/ISSUE_TEMPLATE/{bug_report,feature_request}.md`,
`.github/pull_request_template.md`, `.github/CODE_OF_CONDUCT.md`, and
`.github/CONTRIBUTING.md`, all cross-referencing `docs/GitWorkflow.md`
rather than restating its branching rules. Created the first GitHub
Release (`v1.0.0`, notes populated from `docs/ReleaseNotes-v1.0.0.md`).

Consistent with the "no direct commits to `main`" rule
`docs/GitWorkflow.md` established the milestone before: the community
files were committed on `feature/github-repository-setup`, merged
into both `develop` and `main` (not committed straight to `main`), and
both CI runs on the resulting merges passed before this was considered
done. Branch protection on `main` was attempted via `gh api
.../branches/main/protection` and rejected by GitHub - private
repositories require GitHub Pro (or public visibility) for protected
branches - documented as a Known Issue/manual step rather than
silently skipped or worked around by making the repository public
without being asked to.

**Verification.** All 3 GitHub Actions runs triggered during this
milestone (initial push, merge to `develop`, merge to `main`)
completed `success`. Repository/branches/tags/release all confirmed
via `gh api`/`gh release view`, not assumed from command exit codes
alone.

---

### Milestone 17 — Production Deployment (Render)

**Scope note:** this environment has no Render CLI, no Render API
token, and no browser access - every phase requiring actual Render
account/dashboard interaction (creating the Blueprint instance,
entering secret environment variable values, triggering the first
deploy, running one-off commands like `createsuperuser`, viewing live
logs) cannot be performed here and was handed to the user with exact
manual steps instead, per the milestone's own explicit instruction to
stop and explain rather than assume account access. What follows is
the code-side work that *is* completable without that access: Phases
1-3 and 5's checklist, in full; Phases 4/6/7/8/9's actual execution is
the user's remaining manual work (see the deployment report delivered
alongside this milestone for the exact current status).

**Phase 1 - Production Readiness Audit.** Found one real, deploy-
breaking gap: the `Procfile`'s gunicorn command never bound to
`0.0.0.0:$PORT` - it would have started successfully but been
completely unreachable by Render's routing layer, since gunicorn
defaults to `127.0.0.1:8000` with no `--bind` flag. Fixed, along with
adding an explicit worker count (`WEB_CONCURRENCY`, default 2, tunable
per the Render plan's available memory), a request timeout, and
access/error logging - none of this existed before, meaning a first
deploy attempt without this milestone's fix would have failed silently
(the process starts, health checks against the wrong bind address
fail, Render reports a boot failure with no obvious cause). Also added
a `LOGGING` formatter (timestamp/level/logger name - the previous
config emitted bare unstamped messages, unusable for correlating
issues in a real log stream) and `CONN_HEALTH_CHECKS` on the database
connection (so a stale persistent connection reconnects transparently
instead of surfacing as a request-time error). Everything else audited
- `DEBUG`/`SECRET_KEY`/`ALLOWED_HOSTS` handling, WhiteNoise's DEBUG-
conditional storage backend, `SECURE_PROXY_SSL_HEADER`, HSTS/cookie
security, PostgreSQL via `dj_database_url` - was already correct from
Milestones 14/15.3 and needed no change.

**Phase 2 - Reminder System Audit.** All five `send_*` commands
already had solid idempotency (`ReminderLog`'s unique `(user,
reminder_type, reference_key)` constraint - a real database
constraint, not an in-memory check, confirmed still true by re-reading
`engine.py`) and clean exception handling (a single delivery's SMTP
failure is caught and logged per-job, never crashes the whole run -
Milestone 15.1's design). The one genuine gap for a *production*
context specifically: every command's own stdout only ever reported a
bare count ("Sent 3 daily agenda email(s)."), never which deliveries
(if any) failed or why - meaning watching a Render Scheduled Job's
logs directly would never reveal a problem that Reminder
Administration's Activity Log would. Fixed via a small shared
`reminders/management/_report.py: report_results()` helper, reused by
all five commands (not duplicated five times) - failures now print as
a `FAILED -> <recipient>: <error>` line beneath the summary. Nothing
about generation, trigger conditions, or delivery semantics changed -
this is purely additive log output.

**Phase 3 - Render Configuration.** `render.yaml` (a Render Blueprint)
defines the web service, a managed PostgreSQL database, and five
Scheduled Jobs - one per reminder command - as infrastructure-as-code,
per the milestone's "hybrid" instruction (config in the repo, secrets
only in the dashboard). `SECRET_KEY` is Render-generated
(`generateValue: true` - never present in any commit); `DATABASE_URL`
is wired automatically from the Blueprint's own database to every
service that needs it. The four `sync: false` variables (`ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) are
the only values Render will prompt for on first apply - see Phase 5
below.

Cron schedules were derived from each generator's actual trigger
logic, not guessed, per the milestone's explicit instruction: `send_daily_agenda`
runs hourly (`0 * * * *`) because `NotificationPreference.
daily_agenda_time` is per-user and configurable, so only an hourly
cadence catches every setting. The other four run once daily at
`0 3 * * *` (03:00 UTC = 09:00 `Asia/Dhaka`) rather than at midnight
UTC specifically because `reminders/services/exams.py`'s exam-day-
morning reminder additionally requires the current wall-clock time to
be past `EXAM_DAY_MORNING_TIME` (08:00 `Asia/Dhaka`) - a schedule at,
say, 00:00 UTC (06:00 Dhaka) would run before that gate and silently
produce zero exam-day reminders every single day, not because of a
bug but because the generator would correctly (if unhelpfully, given
the schedule) decide "not yet morning." This reasoning - and the
general principle that a fixed-offset timezone (Dhaka is UTC+6, no
DST) never crosses a UTC calendar-day boundary at a mid-day UTC hour,
so no cron-side day-of-week logic is needed at all - is documented in
both `render.yaml`'s own comments and `docs/Deployment.md`, not left
implicit.

**Phase 5 - Environment Variables.** `docs/Deployment.md` gained a
checklist table distinguishing what `render.yaml` handles automatically
from what requires manual dashboard entry - narrowing what the user
actually needs to do to four real values (`ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`),
none of which were invented here - every one is either a fact only
knowable after the Render service exists (its assigned domain) or a
real credential the user must supply themselves.

**Phases 4/6/7/8/9 - Manual Steps.** Not performed in this session -
no Render CLI, API token, or browser access exists in this
environment. Handed to the user as an explicit, ordered set of manual
steps (Render dashboard Blueprint apply, entering the four `sync:
false` variables, verifying the first deploy, confirming all five
Scheduled Jobs ran, `createsuperuser`, and the Phase 9 smoke-test
checklist) - see the deployment report delivered alongside this
milestone for the exact current list.

**Testing.** 4 new tests (`reminders/tests_commands.py:
ReportResultsTests`) covering `report_results()`'s all-success,
all-failure, mixed, and dry-run-suppresses-failure-detail cases
directly (not through `call_command()`, which would depend on
whichever reminder happens to be due at the real wall-clock time a
test runs - the same wall-clock-independence principle Milestone 15's
own `current_time` parameter exists for). Full suite re-run: 533/533
passing (529 before this milestone).

**Verification.** `manage.py check` - clean. `manage.py
makemigrations --check --dry-run` - no changes (no model touched).
`render.yaml` parsed successfully with PyYAML as a syntax sanity
check (not a substitute for Render's own schema validation at apply
time, which this environment cannot perform). Work committed on
`feature/render-production-deployment`, merged into both `develop`
and `main` (never committed directly to `main`), both pushed; all
resulting CI runs passing.

---

### Milestone 17.1 — Render Free Plan Bootstrap

**Context.** Milestone 17's Blueprint assumed Render's paid tier
(Shell access, One-Off Jobs, `type: cron` Scheduled Jobs). Once the
account was actually on the Free plan, applying `render.yaml` failed
outright - Render rejected the five `send_*` Scheduled Jobs with
"plan free not valid for service type cron", and Free also provides
neither Shell nor One-Off Jobs, so `createsuperuser` and the first
`import_csv` run (both assumed to be run manually post-deploy in
Milestone 17) had no way to execute at all.

**Fixes, in the order they were needed:**

1. Removed the five Scheduled Jobs from `render.yaml` entirely so the
   Blueprint validates and applies on Free. The `send_*` commands
   themselves are untouched and fully idempotent - they simply have no
   scheduler invoking them yet (tracked below as an open gap; see
   Milestone 18 and `plan_v1.md` Phase A).
2. `preDeployCommand` (tried as a place to run `migrate`) is also
   unsupported on Free ("preDeployCommand is not available on your
   plan"). Folded `migrate --noinput` into `startCommand` instead, so
   it runs before `gunicorn` starts on every deploy.
3. Added `core/management/commands/ensure_superuser.py` - a small
   idempotent command that reads `DJANGO_SUPERUSER_USERNAME/EMAIL/
   PASSWORD` and no-ops if unset - and folded both it and `import_csv`
   into `startCommand` alongside `migrate`. All three are safe to
   re-run on every deploy: `ensure_superuser` creates-or-updates one
   user idempotently, and `import_csv` already uses
   `update_or_create()`.

Final `startCommand`: `migrate --noinput && ensure_superuser &&
import_csv && gunicorn ...`. `docs/Deployment.md` (Sections 2, 7, 8)
updated accordingly. This is the sequence every subsequent deploy in
this document actually ran through.

---

### Milestone 18 — Routine-4 Data, Postgres Compatibility Fix, Neon Migration & PDF Persistence

**Part A - Routine-4 CSV import.** A new routine PDF (`Routine-4`,
covering 6 Aug - 5 Oct 2026) was translated into the five-file CSV
dataset format and imported via `import_csv`: 82 new rows in
`routine.csv` (35 `CLASS` lectures across Physics/Chemistry/Higher
Math/Biology/English/Bangla plus their `DAILY_EXAM` rows, 6
`WEEKLY_EXAM` and 2 `MONTHLY_EXAM` markers), 55 new rows in
`lecture_topics.csv`, and 11 new rows in `exams.csv`
(`WE-14`-`WE-22`, `MRT-04`, `MRT-05`). Dataset versions `v3` and `v4`
archived under `data/dataset_archive/` (see Part B for why two).

**Part B - Postgres `varchar(255)` production-only bug.** The first
deploy of Routine-4's data (`v3`) failed twice in production with
`psycopg.errors.StringDataRightTruncation` on `LectureTopic.topic`
(`max_length=255`) - two topic strings (297 and 300 chars) exceeded
it. SQLite (local dev and CI's database) does not enforce `varchar`
length at the column level and Django's `update_or_create()` doesn't
call `full_clean()`, so this passed everywhere except real Postgres.
Production was never actually down - Render's `startCommand` runs
`migrate && ... && import_csv && gunicorn` in sequence, so the crash
happened before `gunicorn` started and the previous release kept
serving traffic through both failed attempts. Fixed by shortening the
two strings (`v4`) and auditing every CSV field against its model's
`max_length`; shipped and confirmed live via Render MCP logs
("Import completed successfully.", 85 routine events / 146 lecture
topics / 26 exams).

**Part C - Render → Neon Postgres migration.** Render's free Postgres
instance (`admission-helper-db`) carries a hard 30-day expiry
(created 2026-07-26, `expiresAt` 2026-08-25) and is not renewable -
this took priority over every other item in `plan_v1.md`, including
its own Phase A (GitHub Actions scheduler), since the alternative was
outright data loss. Migration performed with the Neon MCP server and
Django's own `dumpdata`/`loaddata` (no `pg_dump`/`psql` available in
this environment - both are pure-Python and go through the same
`psycopg` driver the app already depends on):

1. `dumpdata --natural-foreign --natural-primary -e contenttypes -e
   auth.permission -e sessions` against Render's external connection
   string - 430 records (2 users, 6 subjects, 75 chapters, 129
   lectures, 146 lecture topics, 26 exams, 15 progress rows, 15
   dataset versions/import logs). `reminders_notificationpreference`
   and `reminders_reminderlog` confirmed genuinely empty via a direct
   read-only query against Render (not a dump gap - no reminders had
   been sent yet).
2. Created a Neon project, ran `migrate` against it (clean schema,
   nothing hand-written), then `loaddata` the same 430 records - row
   counts verified to match exactly via SQL.
3. `sqlsequencereset` for every app table, since `loaddata` preserves
   explicit PKs but does not advance Postgres's identity sequences -
   skipping this would have let the next `INSERT` collide with an
   already-used ID.
4. Render's `DATABASE_URL` repointed at Neon's pooled connection
   string; redeploy confirmed via Render MCP logs: `migrate` found
   nothing to apply (schema already matched), `ensure_superuser`
   recognized and updated the existing superuser (not recreated), and
   `import_csv` re-ran cleanly with matching counts. `/health/`
   confirmed `{"status": "ok"}` post-cutover.

The old Render Postgres instance is no longer referenced anywhere and
was left to expire naturally on 2026-08-25 rather than deleted early
- no rollback was needed, but there was no reason to remove the
safety net before its already-scheduled disappearance.

**Part D - Routine Archive PDF persistence.** `media/` was fully
gitignored and Render Free attaches no persistent disk (`render.yaml`
Milestone 17's own Known Issue), so a PDF copied into
`media/routines/` at runtime - as Routine-4's was, in an earlier
session - never survived the next deploy; the Routine Resources page
had nothing to serve in production. Fixed the same way the CSV
dataset archive already is: un-ignored `media/routines/*.pdf`
specifically (the rest of `media/` stays ignored) and committed the
current routine (`2026-08.pdf`). No new infrastructure - it now ships
with every deploy automatically. `docs/Deployment.md`'s Known Issue
about `MEDIA_ROOT` having no persistent disk is resolved for the
Routine Archive specifically; a real user-uploaded-media feature (if
ever built) would still need a real solution (paid disk or object
storage).

**Verification.** Both fixes shipped through the same branch → PR →
CI → merge-to-`develop` → merge-to-`main` → auto-deploy discipline as
every prior milestone (`bugfix/routine-4-topic-length` → PR #2;
`bugfix/persist-routine-pdf-archive` → PR #3), both confirmed `live`
via Render MCP, both diffs are pure data/config (no application code
changed), so the existing 533/533 test suite is unaffected.

---

## Pending Milestones

- [x] ~~Subjects (dedicated subject list / chapter browsing pages — not
      part of this milestone's spec; subjects currently only surface as
      a routine-list filter and in the Progress overview's per-subject
      breakdown)~~ **Resolved by Milestone 12**: `SubjectDetailView`
      ("/subjects/<pk>/") and `ChapterDetailView` ("/chapters/<pk>/")
      are now the canonical pages for both entities, linked from
      everywhere a subject/chapter name appears app-wide. No dedicated
      "browse all subjects" index page was added (Analytics ->
      Subjects already serves that role and now links each row to its
      canonical page) - not requested by Milestone 12's spec either.
- [ ] "Continue Studying" logic (mentioned in `07_Development_Roadmap.md`
      Milestone 6, not requested by this milestone's spec — not built)
- [x] ~~Reminders~~ **Resolved by Milestone 15**: the full Reminder &
      Notification System (Daily Agenda, Weekly Overview, Revision Due,
      Weekly/Monthly Exam Reminders, Weekly Progress), all generated
      from existing study data - see that milestone's entry above.
- [x] ~~UI Polish~~ **Resolved by Milestone 11** (Design System & UI
      Polish) and further refined by Milestone 12 (Navigation & Study
      Workspace).
- [x] ~~Deployment~~ **Resolved by Milestone 14**: production settings,
      WhiteNoise/PostgreSQL/gunicorn support, `Procfile`, and a GitHub
      Actions CI pipeline are all in place. Actually deploying to
      Render/Railway (registering the service, attaching a database,
      setting real environment variables) is an operational step
      outside this repository's scope, not a remaining code task.

---

## Architectural Decisions

- **Timezone set to `Asia/Dhaka`** instead of the Django default `UTC`. The
  design documents do not specify a timezone; this project tracks a
  Bangladesh university admission schedule (per README), so local time was
  chosen for date/time display correctness. Not an architectural change —
  purely a locale setting. Flagged here since it was not explicitly stated
  in the design docs.
- **`django-tailwind` "Tailwind v4 Full" template chosen** (Node.js-based)
  over the "Standalone" (no Node.js) option, since Node.js/npm were already
  available in the development environment. This matches
  `03_System_Architecture.md`'s listed stack ("Tailwind CSS") without
  further specifying which integration variant; the roadmap's Milestone 1
  objective ("Configure Tailwind CSS ... Verify it is connected correctly")
  is satisfied either way.
- **`NPM_BIN_PATH` hardcoded to an absolute path** in `settings.py`
  (`E:\Programming\Applications\nodejs\npm.cmd`) because `django-tailwind`
  could not locate `npm` via `shutil.which` in this Windows environment.
  This is a machine-specific path. Since this is a single-user personal
  project developed on one machine, it was left as-is; if development moves
  to another machine, this path will need updating (or removal, if `npm` is
  discoverable there).
- **`requirements.txt` manually curated**, not a raw `pip freeze` output.
  Running `manage.py tailwind init` transiently installed `cookiecutter` and
  its dependency tree into the virtual environment as part of scaffolding
  the `theme` app; these are not runtime dependencies of the application and
  were excluded from `requirements.txt` to keep the dependency list minimal,
  per Coding Standards §14.
- **Compiled Tailwind CSS output (`theme/static/css/dist/`) is git-ignored**,
  treated as a build artifact analogous to `staticfiles/`. It is regenerated
  by `python manage.py tailwind build` (production) or
  `python manage.py tailwind start` (development).
- **`theme/templates/base.html`** (django-tailwind's auto-generated demo
  template) was left untouched as vendor scaffolding. The project's real
  base template is `templates/base.html` at the repository root, which takes
  precedence because it is resolved via `TEMPLATES[0]['DIRS']`, searched
  before per-app template directories.

### Milestone 2 — Database Models

- **Followed `02.1_Database_Model_Contract_v1.0.md` exactly where it
  conflicts with `02_Database_Design_v1.1.md`**, per this milestone's explicit
  document priority order (contract is priority 1, design doc is priority 2).
  Conflicts found (documented here per instructions, not resolved
  independently — flagging for the architect):
  - **Subject field name**: contract uses `code`; `02_Database_Design_v1.1.md`
    §4 uses `short_code`. Implemented `code`.
  - **Subject → Chapter delete policy**: contract §10 Delete Policy table
    specifies `CASCADE`; `02_Database_Design_v1.1.md` §8 Deletion Policy
    specifies `PROTECT`. Implemented `CASCADE` (contract).
  - **Routine fields**: contract defines `name`, `imported_at`, `active`
    (boolean, indexed) and no date range; `02_Database_Design_v1.1.md` §4
    defines `name`, `start_date`, `end_date`, `imported_at` and no `active`
    flag. Implemented the contract's field set (no `start_date`/`end_date`,
    includes `active`).
  - These are schema-level discrepancies between two "locked"/"approved"
    documents; they should be reconciled by the architect before Milestone 3
    (CSV Import), since the CSV import mapping in
    `02_Database_Design_v1.1.md` §6 still references `Subject.short_code` and
    assumes `Routine.start_date`/`end_date` exist.
- **Index strategy**: implemented each contract-listed index exactly once —
  via inline `db_index=True` where the contract's field table specifies it,
  via Django's automatic `ForeignKey` index where the field is a FK, or via an
  explicit `Meta.indexes` entry only for the remaining named fields that have
  neither. This satisfies every field named in each model's "Indexes" section
  without creating redundant duplicate indexes on the same column (verified
  via `manage.py sqlmigrate`).
- **Cross-app model imports**: `routines.models.Lecture` imports
  `subjects.models.Subject`; `lectures.models.LectureTopic` imports
  `routines.models.Lecture` and `subjects.models.Chapter`;
  `progress.models.Progress` imports `lectures.models.LectureTopic`. This
  mirrors the dependency direction shown in the contract's relationship
  diagram (Subject → Routine/Lecture → LectureTopic → Progress) and required
  no changes to `INSTALLED_APPS` ordering — Django resolves cross-app model
  dependencies via the migration graph, not app registration order.

### Documentation Synchronization (post-Milestone 2, pre-Milestone 3)

- The Database Model Contract (`02.1_Database_Model_Contract_v1.0.md`) is
  the canonical source for the database schema.
- Earlier design documents have been synchronized with the database
  contract. `02_Database_Design_v1.1.md` was updated: `Subject.short_code`
  renamed to `Subject.code` throughout (table definitions, CSV mapping,
  index strategy); `Subject` → `Chapter` delete policy corrected from
  `PROTECT` to `CASCADE`; `Routine.start_date`/`Routine.end_date` removed
  and replaced with the contract's actual field set
  (`name`, `imported_at`, `active`). `README.md`,
  `01_Product_Requirements_Document_PRD_v1.1.md`, and
  `06_CSV_Import_Specification.md` were checked and already used
  contract-consistent terminology (`subject_code` for the CSV column,
  no references to `short_code` or `Routine` date-range fields) — no
  changes were needed in those three files. `02_Database_Design.md`
  (unversioned v1.0, superseded by v1.1) was intentionally left unchanged,
  as it was not in scope for this synchronization pass.
- `Subject.code` is the official field name throughout the project.
- No Python code, models, or migrations were touched during this
  documentation-only pass.

### Dataset Validation (pre-Milestone 3)

- **Validator scoped as read-only and additive**: `validate_datasets`
  never writes to the CSVs or the database. It was placed under `core`
  (shared utilities app) rather than `routines` to avoid presupposing the
  as-yet-unimplemented importer's module layout (`routines/services/...`)
  from a prior milestone prompt.
- **Grouped error rendering**: the raw per-row findings were extremely
  repetitive (e.g. the same "unknown subject code" error on ~50 rows), so
  `validation_report.md` groups repeats of the same file/column/message
  template into one summary line listing every affected row and every
  distinct value, instead of one block per row. Small groups (≤5) are
  still rendered individually in the exact
  file/row/column/message format the CSV Import Specification's error
  example uses.
- **Dual-track spec compliance**: `exams.csv`'s actual header
  (`exam_code, exam_type, title, lecture_codes, exam_date, online_start,
  online_end`) does not match the locked
  `06_CSV_Import_Specification.md` header
  (`exam_name, exam_type, date, covered_lectures, notes`). The header
  mismatch is reported as an error (required columns missing), and the
  content-level checks this task also asked for (duplicate exam codes,
  lecture-reference validity, ordering) were still run against the file's
  actual column names, since that is the only way to usefully validate
  the real file. Both facts are reported side by side rather than
  silently picking one.
- **`subjects.csv`/`chapters.csv` are outside the locked CSV Import
  Specification's scope** (that document lists Subjects/Chapters as
  "Application"-owned, not CSV-imported), so no locked header format was
  enforced for them — they were validated only for internal
  self-consistency (duplicates, missing values, cross-references) as this
  task requested.

### Milestone 3.0 — Model Contract Revision (Chapter Paper Support)

- **Schema change scoped to `Chapter` only**, exactly as instructed:
  `Subject`, `Routine`, `Lecture`, `LectureTopic`, `Exam`, `Progress` were
  not touched, even though `Chapter`'s ordering/constraint change has no
  bearing on them.
- **One-off migration default (`1`) is safe here**: the `Chapter` table
  had zero rows (no importer exists yet), so the one-off default supplied
  to `makemigrations` for the new non-nullable `paper` field never
  actually applies to real data — confirmed via the Django shell before
  generating the migration.
- **`chapter_no`'s standalone `Meta.indexes` entry was kept unchanged**
  (not merged into a single composite index) even though the new unique
  constraint on (`subject`, `paper`, `chapter_no`) already creates a
  composite index covering `chapter_no` as a trailing column. The
  standalone index remains useful for lookups by `chapter_no` alone
  (e.g. "chapter 5 across all subjects/papers"), which the composite
  index cannot serve efficiently. Consistent with the indexing approach
  already established in Milestone 2.
- **`__str__()` switched from `subject.code` to `subject.name`** (e.g.
  "Physics - 1st Paper - Chapter 2 - Vector" instead of the old
  "P Chapter 2") to match this task's explicit example output. This is a
  cosmetic/display change only — no other code depends on `Chapter`'s
  string representation yet (no views/templates exist).
- **Admin scope matched exactly to this task's spec**: `list_display`,
  `list_filter`, `search_fields` were added only for `Chapter`, only with
  the specific fields requested. `Subject`'s admin registration was left
  as a bare `admin.site.register(Subject)`, since the task's Admin
  section only described `Chapter`'s display/filter/search requirements.

### Milestone 3.1 — Lecture Time Fields Made Optional

- **Scope kept to exactly the two fields discovered broken**
  (`start_time`, `end_time`) — no other `Lecture` fields, and no other
  models, were touched, even though this was a mid-implementation
  detour from Milestone 3 proper.
- **Asked before changing the schema**, since ~50 rows (essentially the
  entire dataset) were affected — this is architecturally equivalent to
  the Milestone 3.0 Chapter/paper situation (a real, dataset-wide
  model-vs-data mismatch discovered only once real data was pushed
  through the pipeline), not a one-off bad row to skip or reject.

### Milestone 3 — CSV Import System

- **`services/csv/` chosen over `services/` flat, per the milestone's
  explicit recommended structure** — not a free architectural choice,
  just following the spec.
- **Bengali Unicode encoding pitfall recurred and was fixed the same way
  as in `validate_datasets.py`**: typing the Bengali letter "য়" (YYA)
  directly in this session's file-editing tools produced the decomposed
  form (YA + NUKTA, U+09AF U+09BC) rather than the precomposed form
  (U+09DF) that the actual CSV data uses. `utils.py`'s constants were
  verified byte-for-byte (via a throwaway script printing `hex(ord(c))`
  for each character) after every edit attempt, and ultimately written
  directly via a Python script operating on exact codepoints rather than
  relying on the text-editing tool to preserve literal glyphs correctly.
  This is now a known, documented risk for any future code touching
  Bengali text in this codebase.
- **`ImportValidationError` carries free-form `**details`** (not just a
  fixed `column` field) specifically so the exact error shape requested
  by this milestone (`Reason: Chapter not found` / `Subject:` /
  `Paper:` / `Chapter:`) could be produced without a special case in the
  formatter — any importer can attach arbitrary labeled context to an
  error.
- **`BaseImporter.run()` wraps the entire file in one
  `transaction.atomic()`**, not one transaction per row. This was a
  judgment call: the milestone said "each importer must run inside its
  own transaction.atomic()" (singular, one per importer/stage) and "on
  failure: rollback current stage" — read together as file-level
  atomicity, matching `08_Coding_Standards.md` §9's "reject invalid
  imports rather than partially importing data" for the CSV system as a
  whole. Verified with a deliberately-corrupted scratch copy of
  `exams.csv` (not the real dataset).
- **Console reconfigured to UTF-8** (`sys.stdout.reconfigure(...)`) at
  the top of `import_csv`'s `handle()`, after hitting the same
  `UnicodeEncodeError` (Windows cp1252 console can't encode ✓/⚠) that
  was already worked around in `validate_datasets` — this time by fixing
  the actual command's stdout encoding, since (unlike the validator) the
  milestone's spec explicitly requires those symbols in the live console
  output, not just in a UTF-8 file.

### Milestone 4 — Student Dashboard & Study Workflow

- **Routine List merges `Lecture` + `Exam` instead of a literal "every
  routine event"**: as established in Milestone 3, only `CLASS` rows and
  exams.csv rows are persisted models at all — there is no database
  representation of routine.csv's `DAILY_EXAM`/`WEEKLY_EXAM`/
  `MONTHLY_EXAM` rows to list. Displaying the two entities that do exist,
  merged and sorted by date, is the closest faithful implementation
  without inventing a new model (explicitly out of scope: "Do NOT modify
  database models unless a critical issue is discovered" — this isn't
  one, it's a known, already-documented scope boundary from Milestone 3).
- **A "completed topic" is defined as all four `Progress` booleans being
  True** (`progress/services.py`). The milestone's spec speaks of a
  single "completion checkbox" per topic, but the `Progress` model (from
  Milestone 2) intentionally tracks four independent study stages; the
  UI exposes all four rather than silently collapsing them, and the
  dashboard/progress-overview statistics use "all four true" as the
  topic-level completion definition since that's the most defensible
  single number to report given the four-field schema.
- **HTMX partial responses via `request.htmx` + `get_template_names()`**,
  not a separate URL/view per partial — `RoutineListView` picks
  `_table.html` vs. the full `list.html` based on whether the request
  came from HTMX, keeping the filtering logic in one view.
- ~~**`parse_exam_notes()` is display-only and best-effort**: it
  re-extracts `exam_code`/`online_start`/`online_end` from the `notes`
  text produced by Milestone 3's importer.~~ **Removed in Milestone
  4.1** — `exam_code`/`online_start`/`online_end` are now dedicated
  `Exam` fields; `ExamDetailView` reads them directly, no parsing
  involved.
- **No dedicated "Exams" page/app was created.** The milestone's spec
  requested an Exam **Detail** page and an "Exams" nav link, but not an
  Exam **List** page — the nav link reuses the Routine List's
  `event_type=EXAM` filter instead. This also avoids creating a new
  `exams` app, which would contradict the locked app structure from
  Milestone 1 (`Exam` lives in `routines`, not a dedicated app).

### Milestone 4.1 — Resolve Remaining Importer Known Issues

- **Model change preferred over importer complexity, per explicit
  instruction**: both issues were resolved by relaxing field
  constraints (`Lecture.lecture_date`/`day`/`title`,
  `LectureTopic.chapter`) and adding real fields (`Exam.exam_code`/
  `online_start`/`online_end`), then *simplifying* the importers to
  match — removing the self-study/gap-lecture exemption branches
  entirely rather than adding a third way to handle them.
- **"Undated Lecture" chosen over a separate model for self-study/gap
  lecture codes**: rather than introducing a new concept (e.g. a
  `StudyUnit` model decoupled from `Lecture`), the existing `Lecture`
  model was relaxed to allow `lecture_date=None`. This keeps
  `LectureTopic.lecture` a simple required FK (satisfying "every
  LectureTopic belongs to exactly one Lecture") while still satisfying
  "no fake routine events are created" — an undated Lecture asserts only
  "this lecture code exists, with this subject", never a fabricated
  date/time. It also composes cleanly with "compatible with future
  Udvash routines": if a future routine *does* schedule a CLASS row for
  one of these codes, `RoutineImporter`'s `update_or_create` will fill
  in the real date on the same row (matched by `(routine, lecture_code)`),
  not create a duplicate.
- **`get_or_create_lecture()` centralized in
  `routines/services/csv/lecture_helpers.py`**, used identically by
  `lecture_topic_importer.py` and `exam_importer.py`, so the "resolve or
  create a minimal Lecture" behavior has exactly one implementation, not
  one per importer.
- **`Chapter` nullability for `LectureTopic` decided per-subject
  dynamically** (`Chapter.objects.filter(subject=subject).exists()`),
  not hardcoded to English/Bangla — consistent with how "self-study
  subject" was already detected dynamically for `Lecture` back in
  Milestone 3, and required by "the solution remains compatible with
  future Udvash routines" (a future subject with no chapter breakdown
  should be handled the same way without a code change).
- **`Exam.exam_code` chosen as the sole `update_or_create` lookup key**,
  replacing the old `(routine, exam_name, exam_date)` synthetic key from
  Milestone 3 — simpler, and for the first time backed by an actual
  database `unique=True` constraint rather than an assumption about the
  dataset.
- **Existing `Exam` rows deleted (not migrated in place) as part of
  migration 0004**: considered and rejected a `RunPython` backfill that
  parses `notes` to populate the new fields, since (a) it would
  duplicate the same notes-parsing logic this milestone's whole point
  is to delete, and (b) `Exam` data has no organic/hand-entered content
  to preserve — it is 100% reproducible from `exams.csv`, and this
  milestone's own verification steps mandate an `import_csv` re-run
  immediately after `migrate` anyway, which fully restores it correctly.
  `Lecture`/`LectureTopic`/`Chapter`/`Subject` data was never deleted —
  only `Exam`, and only because its new `unique=True` field made an
  in-place default value impossible to apply safely to multiple
  existing rows at once.

### Milestone 5 — Study Planner & Analytics

- **No new Django app created for analytics**, even though the spec
  read like a natural "Analytics" feature area. The locked app
  structure from Milestone 1 (`core`, `dashboard`, `subjects`,
  `lectures`, `progress`, `routines`, `reminders`) has no room for one,
  and analytics is entirely progress-completion math — it lives in
  `progress` (views, services, URLs), reusing the app that already owns
  the "what counts as complete" definition. `/analytics/` is mounted as
  its own URL prefix in `admission_helper/urls.py` pointing at a
  dedicated `progress/analytics_urls.py`, rather than nesting it under
  `/progress/analytics/...`, to match the milestone's exact requested
  paths.
- **`get_subject_analytics()` groups by `lecture__subject`, not
  `chapter__subject`** — the reverse of the Milestone 4 original. This
  is the only behavior change to pre-existing logic in this milestone;
  it was necessary because chapterless topics (English/Bangla,
  possible since Milestone 4.1) have no `chapter` to join through, so
  the old grouping silently excluded them from every subject's stats.
  `Lecture.subject` is a required field, so grouping through it is
  always complete. Applied consistently to the dashboard, progress
  overview, and all four analytics pages, so there's exactly one
  "topics belonging to a subject" definition, not two.
- **Exam readiness resolved via two bulk queries, not one query pair
  per exam**: `Exam.covered_lectures` is a plain `JSONField` list of
  lecture codes, not a FK relationship, so it can't be joined directly.
  Rather than looping over exams and querying `Lecture`/`LectureTopic`
  per exam (an explicit N+1 the "Performance" section warned against),
  every covered lecture code across all exams is collected first, one
  query fetches completion stats for all of them at once
  (`.values("lecture_code", "total_topics", "completed_topics")`), and
  a second, separate query fetches the exams themselves — then each
  exam's readiness is computed by dict lookup in Python. Query count
  stays at 2 regardless of how many exams or covered-lecture codes
  exist.
- **"Completed lecture" defined as: has at least one topic, and all of
  its topics are complete.** The spec listed "Completed Lectures" as a
  dashboard stat without defining completion for a `Lecture` (only
  `LectureTopic`/`Progress` have an explicit definition from Milestone
  2/4). A lecture with zero topics is not counted as completed (nothing
  to complete, would inflate the stat meaninglessly); this mirrors how
  `get_subject_extremes()` also excludes zero-topic subjects from
  "most/least completed" ranking.
- **Sort/filter state kept in the URL querystring** (`?sort=`,
  `?subject=`, `?q=`), matching the exact pattern `RoutineListView`
  established in Milestone 4 (`hx-push-url="true"` on every filter
  control) — bookmarkable/shareable analytics views, no server-side
  session state, consistent with "no authentication" and "no server
  state beyond the database" for this project.
- **Dashboard widget refresh implemented as a manual "Refresh" button**,
  not an automatic poll (`hx-trigger="every Ns"`). The milestone's
  "Progress Widgets"/"HTMX" sections asked for "dashboard widget
  refresh" via HTMX but did not ask for live/automatic updates, and this
  project has no background jobs or push mechanism (scheduling/
  notifications are explicitly out of scope per this milestone and
  prior ones) — a user-triggered refresh avoids implying a polling
  feature that wasn't requested.

### Milestone 6 — Testing, Hardening & UX Polish

- **`core/test_utils.py: build_sample_dataset()` is the single shared
  test fixture for every app**, rather than each app's `tests.py`
  building its own ad-hoc data. This directly serves this milestone's
  own "Do NOT reintroduce duplicated business logic" instruction
  extended to test setup: expected values (percentages, counts,
  readiness labels) are derived once, by hand, in one place, and every
  test file imports the same built objects rather than each
  re-deriving its own slightly-different fixture that could quietly
  drift out of sync with another app's assumptions about the same
  data.
- **Dates in the fixture are relative to `timezone.localdate()`**
  (`today + timedelta(days=N)`), not fixed calendar dates, so the test
  suite's "upcoming exam"/"days remaining" assertions never depend on
  which real-world date the suite happens to run on and will not
  silently start failing after this project's routine's date range
  ends.
- **Importer tests never touch the real project-root CSVs.** Every
  importer test builds its own minimal CSVs inside a
  `tempfile.TemporaryDirectory()` and points the importer at that
  directory (`BaseImporter.__init__(base_dir, stdout)` already accepted
  an arbitrary `base_dir` since Milestone 3, so no importer code needed
  changing to support this) — directly satisfying this milestone's "Do
  NOT modify CSV files" instruction while still exercising the real
  import logic end-to-end, including the Bengali chapter-reference
  parser (built via the importer's own verified `_PROTHOM`/`_PORTRO`/
  `_ODHYAY`/`BENGALI_DIGITS` constants in the test, rather than retyping
  Bengali glyphs a third time in this project - see the recurring YYA
  encoding bug documented under Milestone 3).
- **`RoutineListView._get_events()` extracted to
  `routines/services/events.py: get_routine_events()`** as a pure
  refactor (identical behavior, verified by the pre-existing manual
  Milestone 4 verification still holding plus 5 new dedicated tests) —
  the audit's "views doing business logic" / "service extraction"
  categories flagged this as the one place business logic still lived
  in a view rather than a service, and moving it was low-risk (no
  branching logic changed, just relocated) while directly unlocking
  unit tests that don't need a full request/response cycle.
- **Bengali-parsing duplication between `core/validate_datasets.py`
  and `routines/services/csv/utils.py` was audited and deliberately
  left unmerged** (see Implemented Features, Phase 1, item 5) — the
  Milestone 3 decision to keep the validator independent of the
  importer's module layout was intentional and still holds; merging
  them now would trade a well-understood, working duplication for a
  new coupling between two components designed to stand alone.
- **No new indexes added** despite the audit explicitly looking for
  missing ones (see Implemented Features, Phase 1, item 7) — every
  current query path already has index coverage, and the dataset scale
  (tens to low hundreds of rows per table) means a hypothetical
  composite index on `Progress`'s four booleans would be speculative
  optimization for a query pattern that isn't measurably slow, which
  this milestone's "do not modify behavior unless necessary" framing
  argues against.
- **500.html kept deliberately simple/standalone rather than extending
  `base.html`**: Django renders custom error-handler templates
  (`404.html`/`500.html`) outside the normal view/context-processor
  pipeline — `500.html` in particular gets an empty `Context` (no
  `request`), so leaning on `base.html`'s `{% url %}`/`request.path`
  nav-highlighting logic there would be untested territory for exactly
  the moment something has already gone wrong. `404.html` does extend
  `base.html`, since Django *does* pass a normal request/context to the
  404 handler.
- **Pagination reuses the exact Milestone 4 `Paginator` +
  `{% querystring_page %}` pattern**, factored into one shared
  `_pagination.html` partial instead of copy-pasting the markup a
  third time (Routine List already had it; Chapters and Lectures
  analytics gained it this milestone) — consistent with this
  milestone's "repeated HTMX patterns that can be shared" audit
  category.

### Milestone 7 — Authentication & User Management

- **No custom user model introduced.** Django's built-in `User` was
  sufficient for every requirement (`username`, `email`, password
  auth) - the milestone explicitly asked to avoid one "unless
  absolutely necessary," and nothing here needed extra fields on the
  user itself (no profile/role/preference data was requested).
  `Progress.user` references `settings.AUTH_USER_MODEL` (not a hard
  import of `django.contrib.auth.models.User`), which is the correct
  future-proof pattern regardless - if a custom user model is ever
  introduced later, this FK definition doesn't need to change.
- **`lecture_topic` changed from `OneToOneField` to `ForeignKey`, with
  the uniqueness moved to an explicit `UniqueConstraint(user,
  lecture_topic)`.** This was the only way to let many users each have
  independent progress on the same topic while still preventing a
  duplicate row for the *same* user+topic pair - a `OneToOneField`
  can't express "unique per (A, B) pair," only "unique per B alone."
- **`completed_case(user, join_prefix)` filters the join on `user` as
  well as the four booleans, rather than pre-filtering the base
  queryset to a specific user's `Progress` rows before the join.**
  Reasoned through carefully since `progress_records` is no longer
  to-one: a topic can now join-fan-out to one row per user who has
  touched it. The `When()` condition still produces the correct `Sum`
  regardless of this fan-out, because every fanned-out row from a
  *different* user fails the `user` equality and contributes exactly
  `0`, and `(user, lecture_topic)` being unique guarantees at most one
  row can ever satisfy the *entire* condition (all 4 booleans + the
  right user) per topic. `Count(..., distinct=True)` on the total-topics
  side (already in place since Milestone 5, originally defensive) is
  what makes this safe against the same fan-out — confirmed still
  correct via `test_query_count_is_fixed` assertions (still 1-2 queries
  per analytics function) and the "second user sees zero completion"
  tests added this milestone.
- **`get_exam_stats()`/`get_upcoming_exams_widget()` deliberately do
  NOT take a `user` parameter** — exams (like subjects/chapters/
  lectures) are shared curriculum data owned by nobody in particular;
  only a student's own completion of that curriculum (`Progress`) is
  personal. Threading a meaningless `user` argument through a function
  that would never use it was avoided rather than added for
  superficial consistency.
- **`RegisterView`/`RegistrationForm` live in `core`, not a new
  `accounts` app** — same reasoning Milestone 5 already established
  for not creating a new app for analytics: `core` is this project's
  existing home for cross-cutting, non-model-owning functionality, and
  registration is exactly that (one view, one form, no model of its
  own beyond Django's built-in `User`).
- **`/accounts/login/` explicitly overridden before `include(
  'django.contrib.auth.urls')`** rather than subclassing/wrapping the
  include, so only the one view that needed a behavior change
  (`redirect_authenticated_user=True`) required any code at all -
  logout, password change, and password reset are used completely
  stock, with zero custom view code, per "do not reinvent
  authentication."
- **Console `EMAIL_BACKEND` for password reset**: the milestone calls
  password reset "template-ready," and explicitly excludes email
  verification/real delivery from scope. Using the console backend
  makes the full reset flow (request -> emailed link -> set new
  password -> login) actually runnable and testable in development
  without requiring real SMTP credentials in `.env`, without
  implementing anything resembling "email verification" as a feature.
- **Test suite runtime increased from Milestone 6's sub-second 85
  tests to Milestone 7's ~2-2.5 minute 119 tests** - `manage.py test`
  was still run and passes cleanly (per this milestone's explicit
  verification requirement), but the added time is real, unavoidable
  PBKDF2 password hashing on every `User.objects.create_user()` call
  (~30+ across the suite - Django 6's default hasher runs 600,000+
  iterations by design). Deliberately **not** worked around by adding
  a faster password hasher to `settings.py`'s `PASSWORD_HASHERS`, since
  that setting has no test/production split in this project and doing
  so would weaken real password hashing in production, not just tests
  - correctness and security were prioritized over test suite speed,
  consistent with this milestone's security-focused scope.
- **Two real users manually created during verification** (via
  `/accounts/register/` against the actual dev database, not just the
  test suite's fixtures) to prove isolation end-to-end against the
  real imported dataset rather than only the hand-built test fixture -
  left in place afterward (`alice`/`bob`, both password
  `S3cure-Pass!23`) as a working demonstration, rather than deleted, so
  they remain inspectable via Django Admin if desired.

### Milestone 8 — Advanced Analytics

- **`advanced_analytics.py` kept as a fully separate module from
  `analytics.py`/`dashboard.py`**, per this milestone's explicit
  instruction that existing analytics stay "focused on basic
  completion metrics." Every new function still *calls into*
  `analytics.py` where it would otherwise duplicate a calculation
  (`get_subject_analytics`, `get_chapter_analytics`,
  `get_lecture_analytics`, `completed_case`, `readiness_label`,
  `get_lecture_completion_stats`) - the separation is about which
  module *owns* a concept (basic metric vs. derived insight), not
  about refusing to reuse code.
- **Readiness score formula (60% topic completion + 40% lecture
  completion) chosen over adding a third, separately-weighted
  "remaining workload" term**: workload is already exactly the inverse
  of topic completion (`100 - topic_completion_percentage`), so a
  third term built from the same number would only be double-counting
  it under a different name. The blend instead captures a genuinely
  independent second signal - *how many whole lectures* are finished,
  not just how many individual topics - which can diverge from raw
  topic completion (a lecture with 9/10 topics done contributes 0 to
  "lectures fully completed" despite being nearly finished). Both
  weights and the underlying `readiness_label()` thresholds are
  unchanged from `analytics.py` - this milestone extends the readiness
  calculation, per its own instruction, rather than inventing a
  parallel scoring system.
- **"Neglected chapters" defined by *any* recent activity, not just
  recent completions**: a chapter where the user made partial progress
  (e.g. `class_done=True` but nothing else) 2 days ago is not
  "neglected" in the way a chapter untouched for a month is, even
  though neither has a fully-completed topic in that window. The
  `Max("...progress_records__updated_at", filter=Q(...user=user))`
  annotation (not gated on the four completion booleans) reflects
  this - only `completed_case()`-based annotations require full
  completion; "was this chapter touched at all" deliberately does not.
- **Undated lectures sort *after* every dated one in "longest
  untouched," never mixed in by recency**: an undated lecture
  (self-study/gap, see Milestone 4.1) has no scheduled moment to
  measure "how long it's been untouched" against, so ranking it
  against a real, aging scheduled class using any synthetic fallback
  date (e.g. treating it as "oldest") would fabricate false urgency.
  Keeping it in its own tier after all dated lectures is the only
  framing that doesn't invent a fact the data doesn't contain.
- **`rows=` reuse parameters added to five functions** rather than
  making `AnalyticsInsightsView` call lower-level ORM code directly:
  keeps 100% of the actual calculation logic inside the service layer
  (per this milestone's explicit "avoid business logic in views"
  principle) while still letting one call site (the Insights page)
  avoid redundant queries. The parameter defaults to `None` (auto-fetch
  own rows) so every function remains independently callable and
  independently testable, matching how every function in `analytics.py`
  already works.
- **Insights page measures ~18 queries against ~15 target; Dashboard
  measures ~26 against ~10 target** - both over this milestone's stated
  performance targets. Investigated whether to force compliance by
  merging annotated queries further (e.g. computing chapter and lecture
  insights in one giant multi-join query) and deliberately chose not
  to: the milestone's own "no query should scale linearly with row
  count" is the property that actually protects performance as the
  dataset grows, and both pages already satisfy that (re-verified with
  `test_query_count_does_not_scale_with_extra_data`, which adds 50
  topics and asserts an unchanged query count). A fixed offset of "18
  instead of 15" queries costs a few milliseconds once, regardless of
  whether the course has 90 or 9,000 topics; forcing it down further
  would mean either fusing genuinely distinct insights into one
  unreadable mega-query, or re-fetching less data upfront and paying
  for it elsewhere. The Dashboard's overshoot is largely pre-existing
  (16 queries before this milestone touched it at all, per Milestone
  6's own measurement) plus this milestone's bounded, fixed-cost
  addition (+4 widgets, each 1-3 queries) - not a new scaling problem,
  just a wider fixed base.
- **Strongest/Weakest Subject dashboard widgets not added as new
  cards**: `get_dashboard_widgets()`'s existing Most/Least Completed
  Subject cards (Milestone 5) already show exactly this information.
  Adding a second, differently-named pair of cards computing the same
  thing (even with the new tie-break logic) would be visual noise, not
  a new insight - the milestone's own "Do NOT replace existing
  analytics" cuts both ways: don't remove the old cards, but also don't
  duplicate them under a new label. The full tie-broken ranking is
  still available in one place - `/analytics/insights/`'s Subject
  Ranking table - for anyone who needs the more precise ordering.

### Milestone 9 — Revision System

- **Revision scheduled per-Lecture, not per-Topic or per-Chapter**:
  the milestone's own suggested model structure references `Lecture`
  directly, and its "Do NOT duplicate lecture/topic data" instruction
  rules out mirroring `LectureTopic` rows onto a revision table. A
  lecture's topics remain the single source of truth for "what to
  revise" - `RevisionSchedule.lecture.topics` is how the detail page
  reaches them, never a copy.
- **Both an application-level existence check *and* a database
  `UniqueConstraint`** guard against duplicate schedules, not either
  alone. The existence check (`RevisionSchedule.objects.filter(user=,
  lecture=).exists()`) is the fast, common-case path that avoids even
  attempting a redundant `bulk_create()`; the `UniqueConstraint` (with
  a `try/except IntegrityError` around the create) is what actually
  makes duplicate-prevention correct under concurrency - two near-
  simultaneous requests both passing the existence check before either
  commits is a real possibility this project's other `get_or_create()`-
  based idempotency (e.g. `Progress`, `Routine`, `Exam` since
  Milestone 3/7) already relies on the database for, and revision
  schedules follow the same pattern.
- **Triggered by an explicit service call inside `ProgressToggleView`,
  not a Django signal** - the milestone's own "Version 1 Constraints"
  (as tracked in the Database Model Contract) rule out signals, and a
  plain function call at the one place completion state changes is
  simpler to read, test, and reason about than a signal handler that
  fires from a location several files away from where the state change
  actually happens. `ensure_revision_schedule()` is called
  unconditionally on every toggle (not just ones that "look like" they
  might complete something) since it's already a fast, idempotent
  no-op when the lecture isn't newly completed - simpler than adding
  logic to guess in advance which toggles could matter.
- **Not a background job**: also explicitly ruled out by this
  milestone's own scope ("Do NOT schedule background jobs"). Creating
  three rows synchronously inside the same request that completed the
  lecture is fast (a `bulk_create()` of 3 rows) and keeps the whole
  workflow's state changes atomic and immediately visible - no
  eventual-consistency window where a completed lecture temporarily
  has no revision schedule yet.
- **`RevisionHistory` is a deliberately narrow exception to "no audit
  logging"** (a Version 1 Constraint per the Database Model Contract),
  not a general-purpose audit trail added for every model. It exists
  because this milestone explicitly asked for it ("Do not delete
  completed revisions" / "record completed_at" / "create
  RevisionHistory entry") and because `RevisionSchedule.completed_at`
  alone would be silently overwritten if a schedule were ever
  reopened in a future milestone - nothing else in this app gained
  similar history tracking.
- **"Mark complete" is one-way, not a toggle** (unlike `Progress`'s
  four checkboxes, which do toggle): `complete_revision()` on an
  already-completed schedule is a no-op that returns the schedule
  unchanged rather than un-completing it. The milestone's own language
  ("Allow marking the revision as complete," "Do not delete completed
  revisions") describes a one-directional action, and `RevisionHistory`
  being append-only would otherwise need special-casing for "undo"
  that was never asked for.
- **Exam-ready lecture codes annotated onto exam rows in the view
  layer (`AnalyticsExamsView`) for the basic Exam Readiness page, but
  inside `get_exam_insights()` itself for the Insights page** - not
  the same approach in both places, and deliberately so.
  `analytics.py`'s `get_exam_readiness()` is Milestone 5's original,
  "focused on basic completion metrics" function; per this milestone's
  own "Do NOT duplicate existing analytics logic" and the established
  Milestone 8 precedent of never modifying `analytics.py` itself,
  augmenting its *output* one layer up (in the view) was preferred
  over touching the function. `get_exam_insights()`, on the other
  hand, is `advanced_analytics.py`'s own function - already
  established in Milestone 8 as the place that *extends* readiness
  with more fields - so adding one more field there is exactly what
  that function is for, not a boundary violation.
- **`get_exam_ready_lecture_codes()` matches by lecture *code*, not
  id**: `Exam.covered_lectures` (Milestone 3) is a `JSONField` list of
  code strings, not a FK relationship, so every other exam-readiness
  calculation in this app (`get_exam_readiness()`,
  `get_exam_insights()`) already works in terms of codes. Returning
  codes from this function too means it composes directly with that
  existing code, instead of requiring an id↔code translation at every
  call site.
- **Revision streak kept separate from `advanced_analytics.get_study_streak()`**
  rather than generalizing one streak function to accept an "event
  type" parameter: they track genuinely different event streams
  (topic completions vs. revision completions), and a student can
  have an active study streak with zero revision activity, or vice
  versa - collapsing them would either conflate two different signals
  or need enough branching to be no simpler than two small, separately
  testable functions.

### Milestone 10 — Import & Dataset Management

- **Rollback works by re-running the entire import pipeline against
  archived CSVs, not by restoring a data snapshot** - a deliberate
  design decision this milestone's spec didn't fully dictate.
  `DatasetVersion.statistics` is only a row-count summary, not a
  backup of every field of every row, so there was no way to
  literally "restore the previous version" from the model as
  specified without also keeping the actual source data somewhere.
  `archive_source_csvs()` copies the 5 CSVs to
  `data/dataset_archive/<version_name>/` at import time specifically
  so `rollback_to()` has something real to re-import - reusing
  `run_import_stages()` (the exact function a normal import calls)
  guarantees rollback produces identical results to importing that
  version fresh, rather than maintaining a second, parallel
  "restore" code path that could drift from the importer's real
  behavior.
- **`checksum` is a change-fingerprint, not a data-integrity or
  restoration mechanism** - it exists to answer "did the source CSVs
  change since the last import" cheaply (one SHA-256 comparison)
  without an existing/incoming diff, not to verify or reconstruct
  data. The actual verification of "did the import produce correct
  data" is `statistics` (row counts) plus the full `comparison.py`
  diff, not the checksum.
- **`compare_routine_events()` reports a total/by-event-type
  breakdown instead of a forced 4-bucket Added/Updated/Removed/
  Unchanged diff**: only `CLASS` rows in `routine.csv` become
  persisted `Lecture` rows (established since Milestone 3), so
  `DAILY_EXAM`/`WEEKLY_EXAM`/`MONTHLY_EXAM` rows have no database
  "previous state" to diff against. Fabricating one (e.g. by keying
  on row position) would produce a diff with no real meaning; instead
  this function reports what's actually knowable (row/type counts)
  and cross-references the properly natural-key-diffed `CLASS` subset
  already computed under "Lectures," rather than duplicating that
  computation.
- **`validate_only()` is a minimal, additive `BaseImporter` method,
  not a parallel validation system**: it calls the exact same
  `validate_header()`/`validate_row()` each importer subclass already
  had for Milestone 3/4's real import, just without `import_row()` or
  a transaction. This was the only way to satisfy "Do NOT duplicate
  validation logic" while still supporting `--preview` - any other
  approach would have meant re-deriving each entity's validation
  rules a second time.
- **`DATASET_ARCHIVE_ROOT` setting added purely for test isolation**:
  `archive_source_csvs()` originally hardcoded
  `Path(settings.BASE_DIR) / "data" / "dataset_archive"`, which would
  have meant every test exercising a real import wrote actual folders
  into this project's real `data/` directory. Reading
  `getattr(settings, "DATASET_ARCHIVE_ROOT", None)` first (falling
  back to the hardcoded path when unset, so production behavior is
  unchanged) let a new `DatasetTestCase` base class override it to a
  temp directory - the same "don't let tests touch real project
  state" principle already applied to CSV fixtures in Milestone 3's
  importer tests, extended to cover this milestone's new archiving
  step.
- **`DatasetVersion.imported_by` and `ImportLog.user` use `SET_NULL`,
  not `CASCADE`**: a dataset version or import log is a historical
  record of something that happened, not data owned by the user who
  triggered it - deleting a user account shouldn't erase the fact
  that an import occurred or which version is currently active,
  matching the same reasoning already applied to `RevisionHistory`
  being append-only in Milestone 9 and to every other "record of an
  event" table in this project.
- **Dataset UI added to the existing `routines` app, not a new app**:
  `DatasetVersion`/`ImportLog` are both about the CSV import pipeline,
  which has lived in `routines` since Milestone 3 - consistent with
  this project's locked app structure ("never add new Django apps"),
  the same reasoning Milestone 7-9 applied when adding auth to `core`
  and revision to `progress` rather than creating new apps for either.
- **Pre-flight `detect_duplicates()` kept separate from each
  importer's inline `DuplicateTracker`**, not a replacement for it:
  the pre-flight scan runs once across all 5 CSVs *before* any import
  begins (useful for `--preview`/`compare_dataset`, where nothing else
  has parsed the files yet), while each importer's own tracker still
  runs during the real import as defense-in-depth - removing either
  one would either lose the "check before you commit to anything" UX
  this milestone asked for, or remove a safety net that costs nothing
  to keep.

### Milestone 10.5 — Timeline-Based Navigation

- **Event-count windowing implemented as "fetch a bounded ceiling per
  source, then walk whole date-groups outward from the anchor until a
  target count is reached"**, rather than a plain SQL `LIMIT` on event
  rows: a plain `LIMIT` could stop mid-date (showing 3 of a day's 5
  lectures), which this milestone's spec explicitly rules out ("Do NOT
  load a fixed number of days... a date is never split"). `FETCH_CEILING`
  (a fixed constant, `max(PREVIOUS_EVENTS, NEXT_EVENTS) * 4 + 10`) is
  generous enough that real per-day event density here (a handful of
  lectures at most) never gets truncated before whole-date grouping
  runs, while staying a bounded `LIMIT` regardless of total table size -
  the window never loads the full dataset.
- **Anchor resolution reuses the same two queries the window itself
  needs, rather than a separate anchor-lookup step**: both `previous`
  (`date < today`) and `next-or-today` (`date >= today`) candidate
  pools are fetched once; the anchor (today / nearest upcoming /
  nearest past) is derived from whichever pool has data, and the
  window is then partitioned from those same rows. This means smart
  anchor resolution costs nothing extra over building the window -
  4 queries total for the Routine Timeline (2 sources x 2 directions),
  2 for the Exam Timeline (1 source x 2 directions), comfortably inside
  the ≤10-query budget with room for auth middleware and the subject
  filter dropdown.
- **Routine Timeline and Exam Timeline are separate pages, not one
  merged Lecture+Exam feed** (a deliberate change from Milestone 6's
  original merged `routine-list`/`?event_type=EXAM` design): this
  milestone's own spec describes them as two distinct sections with
  different filters (Subject/Completed-Incomplete vs. Subject/Status)
  and different highlights (Today vs. Next Exam) - keeping them as one
  merged feed would have meant compromising one windowing algorithm
  across two structurally different date fields and card layouts for
  no real benefit, since nothing in the spec asks for lectures and
  exams to appear interleaved in one list anymore.
- **Exam subject-filtering resolved via one bulk Python pass over
  `covered_lectures`, not a DB-level lookup**: `Exam.covered_lectures`
  is a plain `JSONField` list of code strings (Milestone 3), not a FK,
  so there's no indexable "subject" column to filter on directly. A
  bulk `Exam.objects.values_list("id", "covered_lectures")` pass (one
  extra query, only when a subject filter is active) is cheap and
  exact because the exam table is structurally small and bounded (one
  prep-year's worth of exams, unlike `Lecture` which grows over the
  whole study period) - a real, documented scaling assumption already
  implicit elsewhere in this app, not a new one introduced here.
- **Exam readiness-status filtering happens after the window is built
  and `attach_exam_readiness()` has run, not as a queryset filter**:
  readiness is a *computed* value (blended lecture/topic completion,
  from `analytics.get_exam_readiness()`), not a stored column, so it
  can't be filtered at the DB level without duplicating that
  computation into a queryset annotation. Filtering the already-
  attached `readiness_label` in Python after the window is built keeps
  the one true readiness calculation in `analytics.py` and accepts a
  known, minor tradeoff: a status filter could in theory show fewer
  than the configured window size if it excludes most of a fetched
  batch - negligible in practice given the exam table's small size
  (see previous point).
- **`get_pending_revision_counts()` added as a new bulk helper in
  `revision.py`, not a modification to any existing revision
  function**: Routine Timeline cards need "how many revisions are
  still pending for this lecture" without a query per card; the
  existing `get_revision_queue()`/`get_exam_ready_lecture_codes()`
  answer different questions (a user's full queue; whether all 3
  levels are done) and weren't reusable for this bulk lookup as-is -
  adding one small, single-purpose function alongside them (the same
  pattern `get_lecture_completion_stats()` established in Milestone 5)
  was preferred over overloading an existing one.
- **`routines/services/events.py`/`get_routine_events()` retired
  entirely rather than left in place unused**: once `RoutineTimelineView`
  stopped calling it, keeping it around would have meant two
  independent "merge Lecture+Exam into one list" implementations in
  the codebase, one of them provably dead (nothing else referenced
  it). The tests that exercised it directly (`RoutineEventsServiceTests`)
  were removed along with it rather than kept passing against dead
  code - their coverage is superseded by `routines/tests_timeline.py`'s
  windowing/anchor tests, which test the code that actually ships.
- **Timeline scroll memory uses `sessionStorage`, not a database
  field or Django session key**: this milestone's own spec explicitly
  says "do not store timeline position in the database," and
  `sessionStorage` (browser-tab-scoped, cleared on tab close) matches
  "remembers... during the current browser session" exactly - a
  `localStorage` or server-side-session approach would have persisted
  the position beyond a single browser session, which wasn't asked for.
- **No JavaScript framework or IntersectionObserver code for lazy
  loading**: htmx's own `hx-trigger="revealed"` already fires exactly
  once when an element scrolls into the viewport, which is precisely
  what an infinite-scroll sentinel needs - matching this milestone's
  "Do NOT introduce JavaScript frameworks" constraint and this
  project's existing "HTMX for interactivity, vanilla JS only where
  htmx has no equivalent" convention (unchanged since Milestone 1).

### Milestone 11 — User Experience & UI Polish

- **`card.html`/`auth_card.html` use a `content_template` indirection
  (an included template's path passed as a string), not literal child
  markup**: Django templates have no "slot" mechanism for `{% include %}`
  the way component frameworks do - a template name passed as a
  variable and included via `{% include content_template %}` is the
  only way to get a genuinely generic "wrapper renders arbitrary inner
  content" component in vanilla Django templates. `card.html` itself
  ended up lightly used (see the Phase 11 note on not over-abstracting
  single-use content) - most "card" shapes in this app turned out to
  be data-driven leaves (`metric_card.html`) rather than generic
  wrappers, so the indirection pattern exists and is documented but
  isn't forced onto every bordered box in the app.
- **`filter_panel.html` requires the view to pre-build a `fields`
  list**, rather than the template iterating a raw queryset directly
  (as every filter form did before this milestone): Django's `{% include
  %}` can't accept a filter's option set as a live queryset AND stay
  generic across "select from a subject queryset" vs. "select from a
  hardcoded choice list" vs. "free-text search box" - a plain list of
  `(value, label)` tuples (or `{"kind": "text", ...}` dicts) is the
  only shape simple enough for one template to render all three
  without branching on the caller's model. Building that list is one
  or two lines in each view's `get_context_data()` reshaping a
  queryset it already fetched (e.g. `[(s.code, s.name) for s in
  subjects]`) - no new query, no calculation, purely presentational -
  and was judged worth the small view-layer touch for the real
  duplication it removes (the same `hx-get`/`hx-trigger` boilerplate
  and `<select>`/`<option>` markup previously copy-pasted across 8
  forms).
- **String concatenation for badge/metric text is done via component
  parameters (`text` + `secondary`, `value` + `total` + `unit`), never
  via chained template filters** (e.g. `value|add:" / "|add:total`):
  Django's `add` filter silently returns an empty string on any type
  mismatch it can't coerce (int + date, or a string once an earlier
  int-conversion attempt already succeeded and the next one fails) -
  this was hit and fixed several times while building this milestone
  (see Errors and Fixes) before settling on "never concatenate through
  filters for anything but two same-type strings; pass the pieces as
  separate template variables instead," which every component in this
  milestone follows.
- **`loading_skeleton.html` exists but isn't wired into any specific
  page** (Phase 7's own instruction was "where appropriate" - this
  milestone judged that nowhere currently is): every existing HTMX
  swap in this app already completes fast enough that the global
  `#page-indicator` top-loading bar (present since Milestone 1) is
  sufficient feedback, and adding a skeleton that appears then
  immediately disappears would be visual noise, not polish. The
  component is built, tested, and ready for the first page where
  request latency actually warrants it (e.g. if a future milestone
  adds a slower report or export).
- **No hamburger menu or sidebar for mobile nav** (this milestone's
  own explicit constraint: "Do not create a sidebar," "keep navigation
  familiar"): a horizontally-scrolling nav bar (`overflow-x-auto
  flex-nowrap`) was chosen over a collapsing menu because it requires
  zero JavaScript, preserves the exact same link structure and click
  targets at every viewport width, and doesn't hide any navigation
  option behind an extra tap - simplicity over cleverness, per this
  milestone's own design philosophy.
- **`pct_color()`/`class_if_positive()` added as small template
  filters/tags in `core/templatetags/ui_tags.py`, not baked into
  `progress_bar.html`/`metric_card.html` themselves**: the three-tier
  completion color and the "only red if positive" rule are used by a
  handful of call sites with different thresholds and colors in a few
  cases (e.g. priority chapters use an amber fill regardless of
  percentage) - keeping the color decision in the caller (via a filter)
  rather than hardcoding it into the component preserves each
  component's ability to accept an explicit `color_class` override
  when the three-tier default doesn't apply.
- **Two bugs fixed opportunistically, not scoped-in by the milestone
  brief**: the stale `routine-list?event_type=EXAM` "Back to exams"
  link on Exam Detail (dead since Milestone 10.5 replaced that filtered
  view with a dedicated Exam Timeline, but nothing had touched Exam
  Detail since) - fixed to `{% url 'exam-timeline' %}` while already
  editing that template for consistency; and the `add`-filter
  concatenation bugs described above, caught during manual smoke-testing
  of the rendered HTML (see Errors and Fixes) before they could ship
  as silently-blank badge/metric text.

---

## Testing

`python manage.py test` — **533 tests, all passing** (529 after
Milestone 15.3/16; +4 for Milestone 17's `ReportResultsTests`, covering
the reminder commands' new per-failure log detail). Breakdown: `core`
20, `core` (UI) 50, `subjects` 12, `routines` 14, `routines`
(dataset) 65, `routines` (timeline) 32, `routines` (navigation) 21,
`routines` (archive) 24, `progress` 101, `progress` (revision) 62,
`progress` (progress service) 20, `lectures` 13, `dashboard` 8,
`reminders` 16, `reminders` (generators)
28, `reminders` (emails) 7, `reminders` (commands) 15, `reminders`
(admin) 25. Covers: CSV importer (all 5
stages, idempotency,
duplicate/missing-column/missing-file errors, transactional rollback
on a bad row), all four basic
analytics calculations and views (sorting, filtering, HTMX partials,
pagination, per-user scoping), the dashboard service layer and its
HTMX refresh endpoint, exam readiness thresholds, progress toggling
(duplicate-prevention, rejected invalid input, never touching another
user's row), lecture/exam detail pages, empty-state handling with zero
data, registration/login/logout, every protected route redirecting an
anonymous client while admin login stays unaffected, end-to-end
two-user isolation of progress/dashboard/analytics, every
advanced-analytics function (strongest/weakest subject with
tie-breaking, subject ranking/rank numbers, completion trend counts,
average completion speed, priority chapter ranking, neglected-chapter
detection, most-unfinished/most-completed chapter ordering,
longest-untouched/recently-completed/backlog lecture ordering, study
streak, daily/weekly/monthly trend data, the exam readiness score's
blended-percentage math, the Insights page), **and (Milestone 9) the
full revision workflow**: `is_lecture_completed()` (fully/partially/
untouched/per-user), schedule creation (exact due-date math, no
schedule for an incomplete lecture, duplicate prevention, never shared
across users), the real `ProgressToggleView` HTTP endpoint actually
triggering schedule creation on the exact toggle that completes a
lecture (not just the service function called directly), exam-ready
determination at every stage of partial completion, the revision
queue's four buckets and every filter (subject/status/level),
completion (status/`completed_at`/history creation, no-op on
double-completion, never deletes, cross-user protection at both the
service and view layer), every revision analytics extra (delay sign,
workload, upcoming load, overdue count, streak), all three revision
views (full page/HTMX partial/anonymous redirect/404-on-other-users-
schedule/query budget), and all three "Exam Ready" integration points
(lecture page, exam readiness page, Insights page) showing correct,
isolated-per-user counts, **and (Milestone 10) the full dataset-
management pipeline**: checksum stability and change-detection,
version creation/activation (single-active constraint enforced under
`IntegrityError`, previous-version lookup), statistics collection
against a known fixture, entity-by-entity comparison output (added/
modified/removed/unchanged, including the routine-events breakdown),
duplicate detection across all 5 CSVs, `--preview` (zero DB writes,
`ImportLog` still recorded, duplicate keys reported via the importer's
own validation), `--dry-run` (full rollback confirmed via before/after
row counts, its `ImportLog` still persists), a real import creating
and activating a `DatasetVersion`, `rollback_dataset` restoring a
prior version's actual data, the `compare_dataset` command's output,
and both new dataset views (full page/HTMX partial/anonymous
redirect/empty-state/query budget), **and (Milestone 10.5) the full
timeline-navigation stack**: anchor resolution for the Routine and
Exam timelines (today-has-events, before-schedule, after-schedule,
nothing-scheduled-yet), event-based windowing (a busy date is never
split across the window boundary, empty calendar days never consume
budget, `has_more_previous`/`has_more_next` correctly reflect whether
more data exists beyond the fetched ceiling), the `before`/`after`
lazy-loading cursors (older/newer windows never duplicate or drop
events at the boundary), ISO week/date grouping, the bulk progress/
revision-status/exam-readiness attachment helpers (correct values,
per-user isolated, and reusing - never duplicating -
`analytics.py`/`revision.py`'s existing calculations), the
Completed/Incomplete and Readiness-status filters, and all four
timeline views (full page vs. HTMX partial, anonymous redirect, query
budget) plus the Revision Queue's new Today marker/Jump-to-Today
control. No test reads or writes the real
project-root CSVs, and (Milestone 10 addition) no test writes into the
real project's `data/dataset_archive/` folder either -
`routines/tests_dataset.py`'s `DatasetTestCase` base class uses
`override_settings(DATASET_ARCHIVE_ROOT=<tempdir>)` for every test
that performs a real archive-producing import. Every test builds its
own data via `core/test_utils.py: build_sample_dataset()`/
`create_user()` or (for the importer/dataset tests) its own temporary
CSV fixtures, except Milestone 10.5's anchor/windowing tests, which
build their own date-controlled fixtures directly (relative to
`timezone.localdate()`, never the wall-clock date) since they need
explicit control over past/today/future lecture and exam dates that
`build_sample_dataset()`'s fixed layout doesn't cover, **and (Milestone
11) the design-system/UI-polish additions**: every shared component
rendered in isolation via `render_to_string()` and checked against its
expected output (`page_header`, `section_header`, `metric_card`,
`badge`, `progress_bar`, `empty_state`, `filter_panel`,
`loading_skeleton`), the base layout's skip link and single-active-nav-
item guarantee, the exact friendly empty-state sentences built against
a genuinely empty per-user dataset, and accessibility markup (checkbox
`aria-label`s, table `<caption>`s, `role="progressbar"`). No existing
test's *logic* needed changing - a few empty-state string assertions
were checked against the new, longer copy and continued to pass
unchanged because every new message was written to keep the original
tested substring intact (see Architectural Decisions), **and
(Milestone 12) navigation/canonical-page coverage**: `SubjectDetailView`/
`ChapterDetailView` (correct reuse of `analytics.py`'s existing bulk
numbers, per-user isolation, links to related canonical pages, query
budgets), Routine Week numbering (sequential-not-ISO, correct lecture
grouping, 404 on an unknown week, Previous/Next nav), same-date-event
ordering determinism (identical results across repeated calls, exact
ascending-`id` order),
staff-vs-non-staff dataset permission enforcement (403 for a logged-in
non-staff user, 302-to-login for anonymous - not conflated), Lecture/
Exam Detail cross-navigation (Subject/Chapter/Previous-Next-Lecture/
Upcoming-Exam links; Covered Subjects/Chapters/Readiness), the
`smart_back.html` component (fallback link/label rendering, presence
on every detail page), and the shared workspace sticky-toolbar class
string appearing on all three workspace pages, **and (Milestone 13)
the interface-consistency audit**: `card_classes()`/
`status_badge_classes()` (every variant of both, plus the neutral
fallback for an unrecognized badge variant), the continuous Routine
Week map (an empty week between two lecture weeks is still a valid,
navigable week; an exam-only week resolves to a number; the Exam
Timeline renders the identical "Routine Week N" label and links to
the identical canonical page), and a regression test for the "Due"
badge bug described above, asserted against the actual rendered date
fragment rather than just the section existing, **and (Milestone 14)
the Routine Archive**: filesystem discovery (empty archive, missing
directory, descending sort, latest selection, non-PDF/malformed-
filename/subdirectory filtering), path-traversal rejection (three
distinct traversal attempts, each confirmed rejected before the
filesystem join), the viewer's default/explicit/unknown-filename
selection behavior, the HTMX partial-only response, and the file-
serving endpoint's inline vs. `?download=1` attachment headers and
404s (nonexistent, non-PDF, path-traversal filename) - every test
using its own temporary `MEDIA_ROOT`, never the real `media/`
directory, **and (Milestone 15) the full reminder system**: every
trigger condition (Routine Week first-day-only, weekly/monthly exam
offsets including the exam-day morning gate, revision due-date,
Daily Agenda's configurable delivery time), preference filtering (one
disabled-type test per reminder type), idempotent delivery (a second
`engine.run()` for the same occurrence is a no-op; same-reference-key-
different-type both still send), every registered reminder type's
HTML/plain-text rendering, and all five management commands
(including `--dry-run`) - none of it dependent on wall-clock date or
time, via an explicit `current_time` parameter threaded through every
generator specifically so the exam-day/daily-agenda time gates are
deterministic in tests, **and (Milestone 15.1) Reminder Administration
and the theme system**: staff-only access enforced on both GET and
POST, every email-configuration status branch (ready/incomplete/
disabled) and its exact friendly guidance text, the password never
appearing anywhere in the returned config, the SMTP connection test's
honest per-backend messaging, a standalone test email that never
touches `ReminderLog`, the Reminder Test Center's preview/send against
an explicitly selected recipient (both when something is due and when
duplicate protection correctly reports nothing is), manual sends
recorded as `triggered_by=MANUAL` and a forced delivery failure
recorded as `status=FAILED` and surfaced in the Activity Log, `users=`
targeting on the engine directly, the theme toggle's presence on both
an authenticated and an anonymous page with no database field
involved, and the nav's `flex-wrap` replacing the old horizontally-
scrolling layout, **and (Milestone 15.2) the multi-dimensional Progress
Service/Component and navigation redesign**: partial-credit behavior
on the fixture's one deliberately-partial topic at every hierarchical
scope (Topic/Chapter/Lecture/Subject/overall) plus exam progress via
`covered_lectures`, every bulk function's exact numeric agreement with
its single-scope equivalent *and* its one-query guarantee (via
`CaptureQueriesContext`, not just a comment), an explicit confirmation
that the new formula never triggers a revision schedule a lecture
wouldn't otherwise earn, the Progress Component's small/medium/large
rendering tiers (including the milestone's own worked example
reproduced exactly), legend/tooltip toggling (including the
`default_if_none`-vs-`default` fix), the accessible progressbar role/
label, the rebuilt navigation's hamburger/User Menu/Staff Menu
presence and role-based visibility, and the new card variants. Runtime:
~7-8 minutes
(real PBKDF2 password hashing on test-created `User`s, per Milestone
7's Architectural Decisions - unchanged policy, not re-litigated here).

## Query Count Summary

Measured with `django.test.utils.CaptureQueriesContext` against the
real imported dataset (6 subjects, 75 chapters, ~80 lectures, 91
topics, 15 exams) — each page issues a small, fixed query count that
does **not** grow with row counts (verified: `get_subject_analytics`/
`get_chapter_analytics`/`get_lecture_analytics` = 1 query each,
`get_exam_readiness`/`get_exam_insights` = 2 queries regardless of exam
count, per Milestone 5's original design and re-confirmed here,
including for Milestone 8's new functions):

  Page                      Queries
  ------------------------- -------
  `/` (Dashboard)            34
  `/analytics/insights/`     27
  `/routine/`                10 (Milestone 13: +1, get_routine_week_map() now spans
                                 Lecture+Exam dates - 2 queries instead of 1, was 9)
  `/routine/window/`          8 (Milestone 13: +2, same reason, was 6)
  `/routine/exams/`           9 (Milestone 13: +2, the Exam Timeline now calls
                                 attach_routine_week_numbers() too, was 7)
  `/routine/exams/window/`    7 (Milestone 13: +2, same reason, was 5)
  `/routine/week/<n>/`        6 (Milestone 13: +1, was 5)
  `/routine/resources/`       2 (Milestone 12, new page)
  `/analytics/subjects/`     3
  `/analytics/chapters/`     4
  `/analytics/lectures/`     4
  `/analytics/exams/`        5
  `/exam/<id>/`              8 (Milestone 12: Covered Subjects/Chapters/Readiness/
                                Exam-Ready badges, was 2)
  `/lecture/<code>/`         12 (Milestone 12: Previous/Next Lecture + Upcoming Exam
                                 cross-navigation, was 10)
  `/subjects/<pk>/`           7 (Milestone 12, new page)
  `/chapters/<pk>/`           6 (Milestone 12, new page)
  `/progress/`               3
  `/revision/`               11 (unchanged since Milestone 9 - see below)
  `/datasets/`                6 (Milestone 10, new page)
  `/datasets/compare/`        7 (Milestone 10, new page)

No unnecessary queries were found during this audit, so nothing needed
removing; the numbers above are the "current query budget" future
milestones should stay within (per Milestone 6's Phase 3 instruction),
not a target that was reduced from something higher.

Milestone 7 added one query per protected page (Django's session/auth
middleware loading `request.user`) - fixed overhead from
`AuthenticationMiddleware` itself, present since Milestone 1.

**Milestone 8** raised Dashboard from 16→26 (+4 new "Study Advisor"
widgets, each a small fixed-cost query set - see that milestone's
Architectural Decisions for why this wasn't chased down further) and
added the new `/analytics/insights/` page at 18 queries (against a
15-query target for analytics pages - also discussed there). Every
other analytics page's small increase (1-2 → 3-4) is `AuthenticationMiddleware`
overhead plus `select_related`/`annotate` calls already in place since
Milestone 5; none of it scales with row count, which remains the
property future milestones should actually preserve.

**Milestone 9** raised Dashboard from 26→34 (+8: `get_revision_dashboard_stats()`'s
handful of small `.count()` queries plus `get_exam_ready_lecture_codes()`),
Insights from 18→27 (+9: the new Revision Insights section calls six
`revision.py` functions, most of them 1-2 queries each, plus
`get_exam_insights()`'s own +1 from the exam-ready lookup),
`/analytics/exams/` from 4→5 (+1, the same exam-ready lookup),
`/lecture/<code>/` from 4→10 (+6: `revision_schedules` fetch +
`is_lecture_exam_ready()`'s completion check and revision-level
lookup), and added the new `/revision/` page at 11 queries (against
the 15-query target for this milestone's Revision Queue - comfortably
under). None of these scale with lecture/topic/revision count -
`get_revision_queue()` is a single query regardless of how many
schedules exist (re-verified in `progress/tests_revision.py:
RevisionQueueServiceTests.test_query_count_is_fixed`), and every
per-lecture check (`is_lecture_completed`, `is_lecture_exam_ready`) is
scoped to that one lecture, never a table scan.

**Milestone 10** added two new pages, both measured against the real
imported dataset and comfortably under this milestone's 15-query
target for comparison pages: `/datasets/` at 6 queries (active
version, all versions, all import logs - none scoped to row count,
since `DatasetVersion`/`ImportLog` tables grow with imports, not with
subjects/chapters/lectures) and `/datasets/compare/` at 7 queries
(`comparison.compare_all()`'s five entity diffs plus the routine-
events breakdown all read directly from the CSVs and the domain
tables via `.values(...)` querysets, not per-row queries - confirmed
in `routines/tests_dataset.py: DatasetCompareViewTests.test_query_count_within_budget`,
asserting a ≤20-query budget). No other page's query count changed -
this milestone touched no existing view, service, or template beyond
adding the "Datasets" nav link.

**Milestone 10.5** replaced `/routine/` (page-based list, 3 queries)
with a timeline at 8 queries - 4 for the smart-anchor window itself
(previous/next Lecture rows x2 directions, since anchor resolution is
free - see Architectural Decisions), plus `AuthenticationMiddleware`
overhead, the subject-filter dropdown query, and the two bulk
progress/revision-status attachment queries (`attach_lecture_progress()`/
`attach_revision_status()`, one query each regardless of window size).
Added `/routine/window/` (6 queries) and the new `/routine/exams/`
(7 queries: 2 for the Exam-only window, plus
`attach_exam_readiness()`'s reuse of `get_exam_readiness()` - itself
still a fixed 2 queries per Milestone 8's original design, unchanged)
and `/routine/exams/window/` (5 queries) - all comfortably inside this
milestone's own ≤10-query target for every timeline page. `/revision/`
stayed at 11 queries, unchanged - this milestone's Revision Queue
changes were template-only (a divider + sticky headers + the shared
Jump-to-Today include), never touching `get_revision_queue()` or any
other service call. None of the new pages' query counts scale with
lecture/exam count: the windowing query is a fixed `LIMIT` regardless
of table size (re-verified in
`routines/tests_timeline.py: EventBasedWindowingTests`), and every
bulk attach helper is one query for the whole window, never one per
card.

**Milestone 11** changed no page's query count at all - every existing
query-budget test in the suite (Dashboard's 34, Insights' 27, the
Routine/Exam Timeline's 8/7, `/revision/`'s 11, every analytics page,
both dataset pages) passed unchanged after the full template rewrite,
confirmed by re-running the complete suite rather than spot-checking.
This was by design: every component added in this milestone
(`page_header.html`, `metric_card.html`, `badge.html`, `progress_bar.html`,
`filter_panel.html`, etc.) is a pure template include over data the
view already fetched - none of them call a service function, run a
queryset, or accept a "fetch more data" parameter. The one place this
milestone touched view code (`filter_fields` list construction in
`RoutineTimelineView`/`ExamTimelineView`/`RevisionQueueView`/the four
Analytics views/`DatasetCompareView`) reshapes an already-evaluated
queryset into `(value, label)` tuples in Python - the queryset itself
was already being iterated by the old hand-written `{% for subject in
subjects %}` template loop, so this moved where the iteration happens
without adding a second query.

**Milestone 12** added two new canonical pages (`/subjects/<pk>/` at 7
queries, `/chapters/<pk>/` at 6) plus a small, fixed-cost bump to
three existing pages for the cross-navigation data they now show:
`/routine/`'s week headers (+1, `get_routine_week_map()` - one query
over every dated Lecture regardless of window size, not per-week),
`/exam/<id>/`'s Covered Subjects/Chapters/Readiness/Exam-Ready badges
(+6: one `Chapter` query, `get_exam_readiness()`'s existing 2 queries,
`get_exam_ready_lecture_codes()`'s 1 query - covered Subjects/Lectures
came for free from data the view already had resolved), and
`/lecture/<code>/`'s Previous/Next Lecture + Upcoming Exam links (+2:
one query each way, only run when the lecture is dated; a single
`Exam.objects.all()` pass for covering exams, already small and
structurally bounded per Milestone 10.5's reasoning). None of these
scale with dataset size - `get_routine_week_map()` and the exam-
readiness/exam-ready lookups are all fixed-query-count functions
already established in earlier milestones, reused here rather than
reimplemented, and the two new detail pages reuse `get_subject_analytics()`/
`get_chapter_analytics()`/`get_lecture_analytics()` (Milestone 5's
originals, still 1 query each regardless of row count) rather than
computing anything new.

**Milestone 13** raised `/routine/`, `/routine/window/`,
`/routine/week/<n>/` by 1 query each and `/routine/exams/`/
`/routine/exams/window/` by 2 each - all for the same reason:
`get_routine_week_map()` (Phase 1's unification fix) now reads both
Lecture and Exam dates to compute its span, instead of just Lecture
dates, so it costs 2 queries instead of 1; the Exam Timeline pages
also call it for the first time (previously they didn't call it at
all, keeping a separate ISO-based label - see Phase 1 above), which is
where their +2 comes from. Every other change this milestone made was
templates/components/`ui_tags.py` only - card/badge styling, hover
states, and the `timeline_body.html` consolidation - none of which
touch the database, so no other page's query count moved. `/routine/`
now sits at exactly its historical ≤10-query budget (10); every other
touched page stayed comfortably under it.

**Milestone 14** did not move any page's query count. The Routine
Archive (`/routine/resources/`, `/routine/resources/file/<filename>/`)
issues zero database queries - `list_routines()`/
`resolve_routine_file()` are pure filesystem operations - and every
other change this milestone made was settings/deployment
configuration, not application code that queries the database.

**Milestone 15** did not move any page's query count either. Extracting
`get_exam_coverage()` out of `ExamDetailView` moved code, not query
shape - the view issues the exact same queries it did before, just
through a shared function - and the reminder system's own queries
(generation, rendering, delivery) all run inside a management
command's process, never inside a request.

**Milestone 15.1** did not move any student-facing page's query count -
the timezone dropdown, nav `flex-wrap`, and dark-mode classes are all
presentation-only. `/reminders/admin/` is a new, staff-only page never
subject to any prior milestone's query-budget commitments (those were
all made for student-facing pages); it necessarily costs more than a
typical page since a single GET renders email config, the last 25
`ReminderLog` rows, and the full active-user list, and a POST to the
Reminder Test Center runs a real generator pass. Not measured against
a fixed budget here, since - unlike every other page in this app -
its query cost scales with how many reminder types/users an
administrator is actively testing, which is expected and acceptable
for an internal diagnostic tool.

**Milestone 15.2** added exactly one Progress Service query to each
page it touched (a single `_aggregate_topics()`/bulk call per page,
regardless of how many rows that page lists): `/subjects/<pk>/` +1
(header meter) +1 (bulk chapter meters) +1 (bulk lecture meters) = +3;
`/chapters/<pk>/` +1; `/progress/` +1 (overall) +1 (bulk per-subject
meters) = +2; `/` (Dashboard) +1; `/analytics/subjects/` +1;
`/analytics/chapters/` +1 (scoped to the current page's rows only, not
the whole dataset); `/analytics/lectures/` +1 (same). None of these
scale with dataset size - every added query is a bulk aggregate over
however many rows that page already displays, the same shape every
other bulk function in this app already uses. The navigation redesign,
Progress Component, card variants, analytics tabs, and every other
polish change touch templates/`ui_tags.py` only - no query impact.

---

## Known Issues

- ~~**Contract vs. design-doc conflicts** (see Architectural Decisions,
  Milestone 2): `Subject.code` vs `short_code` naming, `Subject`→`Chapter`
  delete policy (`CASCADE` vs `PROTECT`), and `Routine` field set
  (`active` vs `start_date`/`end_date`) differ between
  `02.1_Database_Model_Contract_v1.0.md` and `02_Database_Design_v1.1.md`.
  The contract was followed as instructed. These should be reconciled before
  Milestone 3, since CSV import mapping documentation currently references
  the design doc's (now superseded) field names.~~
  **Resolved** — see "Documentation Synchronization" under Architectural
  Decisions below. `02_Database_Design_v1.1.md` has been updated to match
  the contract; no open issues remain.

- **Source dataset fails validation — 286 errors, 64 warnings** (see
  `validation_report.md` at the project root, generated by
  `python manage.py validate_datasets`). These are data/specification
  conflicts for the architect to resolve — nothing was auto-fixed, and no
  importer exists yet to be blocked. The substantive findings:
  1. **`subject_code` granularity mismatch**: `routine.csv` and
     `lecture_topics.csv` use single-letter/short subject codes (`M`,
     `P`, `C`, `B`) for subjects that `subjects.csv` splits into two
     papers each (`M1`/`M2`, `P1`/`P2`, `C1`/`C2`, `B1`/`B2`). None of
     `M`/`P`/`C`/`B` match any `Subject.code` in `subjects.csv`. This
     affects 50 rows in `routine.csv` and 65 rows in `lecture_topics.csv`.
     Needs an architectural decision: either add generic `M`/`P`/`C`/`B`
     subjects, or have the (future) importer resolve the specific paper
     from context — this is exactly the kind of decision this milestone's
     instructions say not to make unilaterally.
  2. **`lecture_topics.csv`'s `chapter_no` column contains descriptive
     Bengali text** (e.g. `১ম পত্র অধ্যায়-০২`, meaning "1st paper,
     chapter 2") instead of the integer required by
     `06_CSV_Import_Specification.md` and `02.1_Database_Model_Contract_v1.0.md`.
     All 91 data rows are affected. This also encodes the "which paper"
     information that issue #1 above needs — the two issues are likely
     related and may share one resolution.
  3. **`lecture_topics.csv` and `exams.csv` reference lecture codes that
     don't exist in `routine.csv`**: all `E-01`..`E-13` (English) and
     `BA-01`..`BA-13` (Bangla) codes, plus `P-06`/`C-06`/`M-06`/`B-06`
     (see the allowed "06" gap above — those three are expected gaps, not
     part of this issue). `routine.csv` has no CLASS rows at all for the
     English or Bangla subjects, yet both are referenced as if lectures
     for them exist.
  4. **`exams.csv` header does not match the locked CSV Import
     Specification**: actual columns are `exam_code, exam_type, title,
     lecture_codes, exam_date, online_start, online_end`; the locked spec
     defines `exam_name, exam_type, date, covered_lectures, notes`.
  5. **`routine.csv`'s `event_type` values don't match the locked enum**:
     actual values are `CLASS, DAILY_EXAM, WEEKLY_EXAM, MONTHLY_EXAM`;
     `06_CSV_Import_Specification.md` defines `CLASS, EXAM, OFFDAY,
     OTHER`. Reported as warnings (64 rows), since it doesn't block
     structural validation the way the errors above do, but it will block
     import logic that switches on `event_type`.
  6. **One data-only error**: `routine.csv` row 2 (the orientation class
     row) has `event_type=CLASS` but blank `subject_code` and
     `lecture_code`, both required for that event type.
  - None of the above were fixed — per this task's instructions, only
    completely objective fixes (e.g. whitespace trimming) were in scope,
    and the CSV quality checks found nothing of that kind to fix. The
    dataset is **not** ready for import until these are resolved.
  - **Resolved by the Dataset Revision pass** (see Architectural
    Decisions and Implemented Features above): #1 and #2 were resolved
    together — `subjects.csv` now uses subject-level codes, and
    `chapters.csv` gained a `paper` column, so the Bengali chapter
    reference in `lecture_topics.csv` (kept as-is, per instructions) now
    resolves correctly. #3 (E/BA orphan lecture refs) was resolved by
    recognizing them as self-study subjects (confirmed against
    `routine.csv`, which genuinely has no CLASS rows for `E`/`BA`) rather
    than inventing lecture rows. #4 and #5 were resolved by updating the
    validator to treat the actual `exams.csv` schema and `event_type`
    values as finalized, rather than the outdated
    `06_CSV_Import_Specification.md` draft. #6 (orientation row) was
    resolved by revising the validator's CLASS-row rule to allow both
    `subject_code` and `lecture_code` blank together (general session),
    while still catching a single blank field as an inconsistency.
    `validate_datasets` now reports **0 errors, 0 warnings** — dataset
    confirmed ready for Milestone 3.

- ~~**`Chapter` model has no `paper` field, but `chapters.csv` now needs
  one.**~~ **Resolved by Milestone 3.0** (see Implemented Features and
  Architectural Decisions below): `Chapter` now has a `paper` field
  (`Chapter.Paper` IntegerChoices, 1st/2nd Paper) and the unique
  constraint is (`subject`, `paper`, `chapter_no`). Migration
  `subjects/migrations/0002_alter_chapter_options_and_more.py` applied.
  No open issues remain — Milestone 3 (CSV Import) can proceed.

- ~~**`Lecture.start_time`/`end_time` required, but routine.csv leaves
  them blank for ~all CLASS rows.**~~ **Resolved by Milestone 3.1**: both
  fields are now `null=True, blank=True`. Migration
  `routines/migrations/0002_alter_lecture_end_time_alter_lecture_start_time.py`
  applied.

- ~~**`Exam` model has no field for `exam_code`, `online_start`, or
  `online_end`** (finalized `exams.csv` columns), and **no unique
  constraint of its own** (only `id`).~~ **Resolved by Milestone 4.1**:
  `Exam` now has dedicated `exam_code` (unique), `online_start`,
  `online_end` fields; the importer no longer folds anything into
  `notes`, and `update_or_create` is keyed on `exam_code` directly.
  Migration `routines/migrations/0004_alter_exam_exam_code.py` applied
  (see Architectural Decisions, Milestone 4.1, for why existing `Exam`
  rows were deleted rather than backfilled in place).

- ~~**31 of 91 `lecture_topics.csv` rows (English/Bangla self-study
  subjects, plus the intentional lecture-06 gap) are not represented as
  `LectureTopic` rows in the database**~~ **Resolved by Milestone 4.1**:
  `Lecture.lecture_date`/`day`/`title` and `LectureTopic.chapter` are
  now optional; every lecture_code resolves to a real (possibly undated)
  `Lecture` via `get_or_create_lecture()`, and every subject with no
  chapter breakdown gets `chapter=None` rather than being skipped.
  `import_csv` now imports all 91/91 `lecture_topics.csv` rows.
  Migrations `routines/migrations/0003_...py` and
  `lectures/migrations/0002_alter_lecturetopic_chapter.py` applied. No
  open issues remain from Milestone 3/3.1/4's importer work.

- ~~**Exam Detail page regressed after Milestone 4.1**: `ExamDetailView`/
  `exams/detail.html` still called the Milestone 3 `parse_exam_notes()`
  helper against `Exam.notes`, but Milestone 4.1's importer stopped
  populating `notes` once dedicated `exam_code`/`online_start`/
  `online_end` fields existed — so the page silently showed "Not
  specified" for online period and omitted the exam code on every
  exam, despite the data being present in the database.~~ **Resolved by
  Milestone 5** (found and fixed while reviewing the codebase before
  starting this milestone's own work): `parse_exam_notes()` removed;
  the view/template now read the dedicated fields directly. No open
  issues remain.

- ~~**No authentication/multi-user support exists** (out of scope for
  all of Version 1, per the Database Model Contract §12's "Version 1
  Constraints" list, which named "User authentication" and "Multi-user
  support" as explicitly out of scope).~~ **Superseded by Milestone 7**:
  authentication and per-user `Progress` were explicitly requested and
  implemented this milestone. ~~`02.1_Database_Model_Contract_v1.0.md`
  §12 was not edited at the time (Milestone 7's Documentation section
  said "Update only PROJECT_PROGRESS.md"), so that document's text
  still literally listed these as out of scope.~~ **Resolved by
  Milestone 9** (which explicitly asked to update the Database Model
  Contract and Database Design too): the contract's Progress section
  (§7) now reflects the actual per-user model, and §14 ("Version 1
  Constraints") strikes through the superseded "User authentication"/
  "Multi-user support" entries rather than silently deleting them, per
  this project's "never delete history" documentation convention. No
  open divergence remains between the contract and the actual models.

- **Remaining technical debt (documented, not defects)**: intentional
  duplication of Bengali chapter-reference parsing between
  `core/management/commands/validate_datasets.py` and
  `routines/services/csv/utils.py` (see Milestone 6 Architectural
  Decisions — kept deliberately separate); `subjects`/`reminders` apps
  remain unbuilt beyond scaffolding (see Pending Milestones); no
  role-based permissions exist beyond Django's standard user/admin
  split; Dashboard (34) and `/analytics/insights/` (27) sit above their
  respective 10/15-query performance targets, an accepted tradeoff
  documented in Milestone 8/9's Architectural Decisions (both are
  fixed, non-scaling costs, not N+1 patterns); no notifications/
  reminders exist for due/overdue revisions (explicitly deferred past
  Milestone 9, per that milestone's own scope); rollback
  (`rollback_dataset`) restores domain data by re-importing archived
  CSVs rather than from a field-level snapshot (see Milestone 10's
  Architectural Decisions for why this is intentional, not a
  shortcut) - this means a target version's archived CSVs must still
  exist on disk in `data/dataset_archive/` for rollback to succeed;
  `reminders` app remains unbuilt beyond scaffolding, unchanged by
  Milestone 10 despite now having both a revision schedule and an
  import history that could each generate reminders in a future
  milestone; Exam/Readiness-status filtering on the Exam Timeline is a
  post-window Python filter rather than a DB-level one (see Milestone
  10.5's Architectural Decisions) - a documented, currently-negligible
  tradeoff given the exam table's small, structurally-bounded size,
  worth revisiting only if a future milestone changes that assumption;
  Dashboard/lecture-detail/analytics pages were not restyled as part of
  Milestone 10.5 - only Routine, Exams, and Revision moved to the
  timeline model, per that milestone's own scope ("this milestone is
  not a UI redesign... that belongs to Milestone 11"). ~~Dashboard/
  lecture-detail/analytics/datasets pages not yet restyled for
  consistency~~ **Resolved by Milestone 11**: every page in the app
  (Dashboard, Routine/Exam Timeline, Revision Queue, Progress, all five
  Analytics pages, both Datasets pages, Lecture Detail, Exam Detail,
  and every auth page) now shares the same component library, card
  style, form style, and empty-state convention; `loading_skeleton.html`
  exists but isn't wired into any page yet (no page's HTMX response is
  currently slow enough to need one - see Milestone 11's Architectural
  Decisions); Exam Timeline's Readiness-status filter remains a
  post-window Python filter, unchanged by this milestone (a
  presentation concern Milestone 11 didn't need to touch); no
  automated visual-regression/screenshot testing exists (out of scope -
  this milestone's tests check markup/text, not pixel-level rendering).
  None of these block any currently-planned milestone.

- **No automated build step runs `npm run build` on deploy/CI** - this
  is the operational gap that let Milestone 11.2's stale-CSS bug persist
  silently through 11 milestones. `manage.py test`/`check` never load
  or inspect compiled CSS, so nothing in this project's automated
  verification would have caught it either, without the new
  `CompiledCSSTests` added in Milestone 11.2. Until a deploy/CI step is
  added (out of scope here - this project has no deployment pipeline
  yet, tracked in Pending Milestones), **`npm run build` (in
  `theme/static_src/`) must be run manually after pulling any change
  that touches template classes**, and before any manual/browser
  verification - `manage.py runserver` alone will silently keep serving
  a stale stylesheet otherwise. `CompiledCSSTests` will now fail loudly
  if this is forgotten and the stylesheet drifts far enough out of date
  to be missing required utilities.

- **Routine Resources has no real content yet** (Milestone 12, Phase
  9): `/routine/resources/` correctly shows "not uploaded yet" for
  both the routine PDF and routine image, since no file-upload
  feature, storage, or model for such assets exists anywhere in this
  project - none was in scope to build here (this milestone's own
  constraints ruled out modifying existing models "unless absolutely
  necessary," and no prior milestone specified this feature either).
  A future milestone adding real file storage (e.g. `FileField`/
  `ImageField` on a small new model, or a `media/` upload path) would
  wire directly into this page's two existing empty-state slots.
- **No dedicated "browse all subjects" index page** - `SubjectDetailView`/
  `ChapterDetailView` (Milestone 12) give every subject/chapter a
  canonical page, but there's still no single page listing every
  subject as a grid/list of cards; Analytics -> Subjects already
  serves that purpose today (and every row there now links to the new
  canonical page), so a separate index wasn't built - not requested by
  this milestone's spec, which asked for canonical *detail* pages, not
  a new browsing surface.
- **Smart Back's visible label can mismatch its actual destination**:
  `components/smart_back.html` shows a static fallback label (e.g.
  "Analytics" on the Subject Detail page) describing where the
  fallback link goes, but when real browser history exists the script
  upgrades the click to `history.back()` instead - which may return
  somewhere else entirely (e.g. the Routine Timeline, if that's where
  the user actually came from). This is an inherent, accepted tradeoff
  of "prefer real history first" (this milestone's own Phase 7
  instruction): the label can't know in advance where `history.back()`
  will land without inspecting browser history synchronously at
  render time, which Django's server-side template rendering has no
  way to do. Functionally correct (the user always ends up back where
  they actually came from), just not always label-accurate.
- **Numeric table columns aren't right-aligned** (Milestone 13, Phase
  9) - reviewed and deliberately not swept in, since every table's
  primary numeric indicator (completion percentage) already flows
  through `progress_bar.html`'s own right-aligned label; a second pass
  right-aligning raw count cells (Total/Completed/Remaining) was judged
  cosmetic-only relative to the effort of touching ~8 table templates,
  not silently skipped. Worth doing in a future pass focused purely on
  table polish, if one is ever requested.
- **`card_classes()`'s "dense"/"normal" split is informal, not
  enforced** - a future page could still hand-write `p-4`/`p-3` instead
  of using the tag, and nothing would catch it automatically (no lint
  rule exists for this project's templates). The tag exists so *new*
  cards have an obvious, documented default to reach for; it doesn't
  prevent someone from not using it.
- **Media persistence in production is the deployment platform's
  responsibility, not this codebase's** (Milestone 14, Phase 5) - the
  Routine Archive's `media/routines/` folder needs a persistent/
  attached disk on Render/Railway or an uploaded PDF disappears on the
  next redeploy. Documented in README's Deployment section; not
  something Django itself can guarantee.
- **Actually deploying (registering a Render/Railway service, attaching
  a database, setting real secrets) was not performed** - this
  milestone made the codebase deployment-*ready* (settings, `Procfile`,
  CI, docs); the operational act of deploying is outside a code
  milestone's scope and was never requested.
- **No GitHub Actions caching for `pip`/`npm`** - `ci.yml` reinstalls
  both dependency sets from scratch on every run. Acceptable for a
  single-developer project's CI cadence; worth adding `actions/cache`
  if CI runtime ever becomes a real friction point.
- **No actual scheduler is configured** (Milestone 15, Phase 10) - the
  five `send_*` management commands exist and are scheduler-agnostic
  by design, but nothing currently invokes them on a cron-like
  cadence. Wiring up Render/Railway Scheduled Jobs (or GitHub Actions,
  or `cron`) is an operational deployment step, the same category as
  "actually deploying" noted above - not a code change, and not
  requested as part of this milestone's scope.
- **Exam-day "morning" reminders assume server-local time, not each
  user's own timezone** (Milestone 15, Phase 5/7) - `NotificationPreference.
  timezone` is captured and validated but only the Daily Agenda's
  delivery-time gate is actually timezone-aware territory worth adding
  in the future; `EXAM_DAY_MORNING_TIME` (08:00) and every date-based
  trigger (Weekly Overview/Progress, Revision Due) compare against
  `timezone.localdate()`/`timezone.localtime()` - i.e. the server's
  configured `TIME_ZONE` (`Asia/Dhaka`), matching every other date
  calculation in this app (dashboard, revision due dates, exam dates)
  which has never been per-user. Not a regression - just not yet fully
  using the field it stores.
- **No unsubscribe-all / one-click-disable link in the emails
  themselves** - turning a reminder type off requires visiting
  `/reminders/preferences/` while logged in. Acceptable for a
  single/few-user personal tool; would need a signed-token link for a
  multi-tenant product.
- ~~Dark mode coverage follows the Shared Component Rule, not a full
  page-by-page sweep~~ (Milestone 15.1, Phase 10). **Resolved by
  Milestone 20**: the visual-identity rework replaced every literal
  `gray-*`/`slate-*`/`blue-*`/`bg-white` (including the hand-rolled
  markup this entry specifically called out, e.g. the Dashboard/
  Progress pages) with theme-aware tokens (`bg-surface`, `text-ink`,
  etc.) that are correct in both themes with no `dark:` class at all -
  not a page-by-page sweep of `dark:` variants, but the underlying gap
  (page markup bypassing the shared system) closed at the token level
  instead.
- **The Reminder Test Center's recipient selector is a plain `<select>`
  of every active user** (Milestone 15.1, Phase 5) - genuinely
  "searchable" via native browser type-ahead for a handful-to-dozens
  of users, but would need a real filterable/paginated widget if the
  user base grew into the hundreds. Fine for this project's
  single/few-user scope.
- **`EXAM_DAY_MORNING_TIME` and the Daily Agenda's delivery-time gate
  are still server-local time, not per-user** - unchanged from
  Milestone 15's own Known Issues entry; the timezone dropdown (Phase
  1) makes the *stored* value valid and constrained, but doesn't yet
  make any trigger condition read it. Documented once, not repeated
  here in full - see Milestone 15's entry above.
- **`components/auth_card.html` is unused dead code** (Milestone 15.2,
  Part 15's component audit finding) - it exists, is presumably meant
  for login/register, but neither template ever adopted it; both still
  hand-roll their own card markup (now with dark-mode classes added
  this milestone). Left as-is rather than restructure two auth-flow
  templates this late in a design-system milestone; a future pass
  could either adopt it (removing the duplication) or delete it if
  it's judged not worth the indirection for two call sites.
- **Some progress bars were deliberately left on the old flat
  `progress_bar.html`** (Milestone 15.2, Parts 5-6) - the Dashboard's
  Revision-completion bar, `revision/partials/_stats.html`, `exams/
  detail.html`'s readiness bar, `analytics/partials/_insights.html`'s
  bars, and `routine/partials/_lecture_card.html`'s timeline-card bars
  all represent metrics that aren't the raw Class/Notes/Revision/
  Practice breakdown (revision-schedule completion, blended readiness
  scores, other insight metrics) - converting them to the new
  multi-dimensional component would have been semantically incorrect,
  not merely incomplete coverage.
- **No per-page query budget was set for the pages Milestone 15.2
  touched** - each got exactly one Progress Service query added (see
  Query Count Summary above), but unlike Milestones 12-15's specific
  numeric ceilings, this milestone didn't establish new fixed budgets
  for `/subjects/<pk>/`, `/progress/`, etc. Worth doing in a future
  pass if page growth ever makes it necessary.
- **GitHub branch protection on `main` is not enabled** (Milestone 16)
  - `gh api .../branches/main/protection` returned 403: private
  repositories require GitHub Pro (or public visibility) for this
  feature. `docs/GitWorkflow.md`'s branching discipline is followed
  manually/by convention instead. Revisit if the repository ever goes
  public or the account upgrades.
- ~~**No scheduler currently invokes the five `send_*` reminder
  commands in production at all**~~ **Resolved by Milestone 19**:
  `.github/workflows/reminders.yml` now invokes them on the original
  Milestone 17 schedule; the four required secrets are set and a real
  `workflow_dispatch` dry run against production succeeded (2 daily
  agenda emails would have sent, 0 for the other four, no errors) -
  see Milestone 19 below. The underlying per-user-timezone gap
  (`EXAM_DAY_MORNING_TIME` and the Daily Agenda's delivery-time gate
  reading server/app `TIME_ZONE`, not each user's own
  `NotificationPreference.timezone`) is unchanged from Milestone
  15/15.1's original entry and still applies now that a scheduler
  exists.
- **Render deploys can fail on a transient Neon cold-start SSL drop**
  (Milestone 19) - PR #6's deploy (`dep-da436trncjis7394vle0`) failed
  with `django.db.utils.OperationalError: consuming input failed: SSL
  connection has been closed unexpectedly` on `migrate`'s very first
  query. Root cause: the Neon project's compute has
  `suspend_timeout_seconds: 0` (suspends immediately when idle), so
  the deploy's first DB connection had to cold-start a suspended
  compute - a known class of transient Neon/PgBouncer hiccup on the
  very first post-suspend connection, unrelated to the (docs-only) PR
  that happened to trigger it. Render kept the previous deploy
  (`dep-da4348s9v7es73fsnl0g`, PR #5) live throughout - `/health/`
  returned 200 continuously, zero downtime. No fix shipped: the next
  deploy (or a manual dashboard retry) is expected to succeed, since
  the failure is a one-off connection blip, not a reproducible bug.
  If this recurs, raising Neon's `suspend_timeout_seconds` above `0`
  is the direct mitigation (trades a small amount of always-on compute
  time for avoiding the cold-start window) - not applied here since it
  wasn't asked for and has a minor cost tradeoff.
- **`media/` has no persistent disk on Render Free** (Milestone 17,
  Phase 3) - resolved *for the Routine Archive specifically* by
  Milestone 18, Part D: `media/routines/*.pdf` is now git-tracked
  (un-ignored, committed), so it survives every deploy without needing
  a disk at all. This does not generalize - a future feature involving
  real user-uploaded media (not curated, git-committed content) would
  still need either a paid Render disk or object storage (S3/
  Cloudinary/Neon Object Storage), since git-tracking isn't a fit for
  user-generated content.

---

### Milestone 19 — GitHub Actions Reminder Scheduler (Phase A)

**Problem**: Milestone 17.1 removed Render's cron support entirely
(Free plan rejects `type: cron` services outright), leaving the five
`send_*` reminder commands (`reminders/management/commands/`) with
**zero scheduler** invoking them in production - not a suboptimal
schedule, an actual gap, since the Neon migration (Milestone 18).

**Fix**: added `.github/workflows/reminders.yml` - a GitHub Actions
workflow that runs on GitHub's own infrastructure and connects
straight to the production Neon database via `DATABASE_URL`. No
reminder logic or app code changed; the workflow calls the existing
management commands unchanged, exactly as Render's removed Scheduled
Jobs would have:

- Two `schedule` triggers, unchanged from the original Milestone 17
  cron derivation: hourly (`send_daily_agenda`, since
  `NotificationPreference.daily_agenda_time` is per-user/configurable)
  and daily at 03:00 UTC = 09:00 Asia/Dhaka (the other four, safely
  past `EXAM_DAY_MORNING_TIME`). A single step reads
  `github.event.schedule` to pick which command(s) that firing runs.
- `workflow_dispatch` with `command` (choice, default `all`) and
  `dry_run` (boolean, default `true`) inputs for safe manual testing
  from the Actions tab.
- Passed through `/simplify` before commit: merged two near-duplicate
  command loops into a single plan/run step split, added pip
  dependency caching (this runs hourly), and cross-referenced
  `render.yaml`'s `TIME_ZONE`/cron-derivation comment instead of
  re-deriving it undocumented in a second file.

**Requires** four GitHub Actions secrets configured before it can
actually send anything (`DATABASE_URL`, `SECRET_KEY`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) - see `docs/Deployment.md`
Section 6 for the full list and manual-test instructions. Shipped via
branch -> PR #5 -> CI (`test pass 2m58s`) -> `develop` -> `main`; no
app code changed, so all 533 tests remain unaffected.

**Verification: done.** All four secrets were set via `gh secret set`
(each piped from a scratchpad file deleted immediately after, same
handling as the Render DB URL in Milestone 18 - values never
committed or logged). A manual `workflow_dispatch` dry run
(`command=all`, `dry_run=true`) then ran clean against the live Neon
database: `Would send 2 daily agenda email(s)`, `0` for the other
four, no errors. The scheduler is genuinely live now - the next real
hourly/daily trigger will actually send.

One unrelated finding surfaced while checking on this: the very next
Render deploy (PR #6, docs-only) failed on a transient Neon cold-start
SSL drop during `migrate` - see the new Known Issues entry above.
Production was unaffected (previous deploy stayed live throughout);
no fix needed, just noted for the record.

### Milestone 20 — "Indigo Study" Visual Identity & Dashboard Restructure

**Problem**: two related complaints about the UI, not covered by any
prior milestone's scope. First, the visual design itself: zero
customization on top of Tailwind's defaults anywhere in the app - no
custom palette, no font import, `rounded-lg` everywhere, stock
`blue-600`/`gray-*` - the exact look of an unstyled tutorial project,
not a finished product. Second, independent of color: the Dashboard
had accumulated ~15 cards across six stacked sections (Today's
Routine, Upcoming Lecture/Exam, Overall Completion, 4 metric tiles,
Most/Least Completed Subject, 4 Study Advisor tiles, 4 Revision tiles
+ a bar, Recent Activity/Upcoming Exams) - everything the app knows
about a user, all at once, with no priority. For a tool whose stated
purpose is making study tracking *easy*, a landing page that takes
longer to read than to act on defeats its own point.

**Fix, Part 1 - visual identity**: designed and user-approved a
palette+type direction ("Indigo Study": cool blue-tinted neutrals,
one deliberate indigo accent, Newsreader for headings, Work Sans for
body - chosen from three full alternatives previewed as Artifacts
before any code changed), then implemented it as real design tokens
rather than a template-by-template reskin:

- `theme/static_src/src/styles.css` - semantic color tokens (`bg`,
  `surface`, `ink`/`ink-muted`/`ink-faint`, `accent`/`accent-strong`,
  `success`/`warning`/`danger`/`info` each with a paired `-wash` and,
  where a colored pill needs readable text in both themes,
  `-ink` variant, plus a theme-fixed `nav` chrome color) defined once
  as CSS custom properties in `:root` and swapped as a *whole set*
  under `.dark` (Tailwind v4's `@theme inline` maps each token to a
  `--color-*` var, so `bg-surface`/`text-ink`/etc. become normal
  utility classes that are simply already correct in both themes - no
  `dark:` sibling class needed anywhere, ever again). Newsreader/Work
  Sans set via one `--font-sans`/`--font-serif` override plus a
  three-selector heading rule - not a class added to every `<h1-h3>`.
- `core/templatetags/ui_tags.py` - `card_classes`, `button_classes`,
  `field_classes`, `status_badge_classes`, `pct_color` all migrated to
  the new tokens, which propagates the identity through every shared
  component (cards, buttons, form fields, badges, progress fills) for
  free.
- Every remaining template swept for literal `gray-*`/`slate-*`/
  `blue-*`/`emerald-*`/`amber-*`/`red-*` utilities and their `dark:`
  siblings (now redundant - the token already flips): ~450 individual
  class replacements across 65 templates, plus ~50 hand-rolled
  `bg-white` cards/tables that had never gone through `card_classes`
  in the first place (so were invisible to earlier dark-mode work).
- Four real contrast bugs surfaced and fixed, in two rounds: first,
  mid-sweep, the "TODAY"/"NEXT EXAM" timeline markers and the floating
  jump-to-today button, which hardcoded `text-white` on `bg-accent`/
  `bg-warning` - fine while those were fixed dark colors, but wrong
  once they become theme tokens (dark mode's `accent` is a *light*
  indigo; white-on-light is unreadable). Then `/simplify`'s altitude
  review caught two more of the same bug class that manual sweeping
  missed: `base.html`'s active-nav-link pill (`bg-accent` nested
  inside the permanently-dark header, still inheriting `text-white`)
  and `button_classes`'s `danger` variant (`bg-danger text-white`,
  same failure once dark mode's `danger` token goes light). All four
  fixed the same way - a paired `-ink` token per status color
  (`accent-ink`/`warning-ink`/`danger-ink`, plus `success-ink`/
  `info-ink` added preemptively even though nothing uses them solid
  yet, since the review's point was that the pattern needs to be a
  *rule* - "every solid `bg-<status>` fill pairs with a `<status>-ink`
  text token" - not a one-off patch applied only where a bug happened
  to be spotted).
- `/simplify` also caught: a leftover raw `bg-gray-50 dark:bg-slate-900`
  in `workspace_toolbar_classes()` (`ui_tags.py`) that the template
  sweep couldn't reach since it's Python, not a template; five auth
  submit buttons (register/login/password change/reset) that hand-
  wrote `button_classes('primary')`'s exact output instead of calling
  the tag; two Dashboard section headers (`Today's Routine`, `Recent
  Activity`) left as bare `<h2>`s instead of `section_header.html`,
  inconsistent with their sibling sections in the same restructure;
  and two now-dead direct queries in `DashboardView.get_context_data`
  (`upcoming_lecture`/`upcoming_exam`) that the Dashboard rewrite in
  Part 2 below stopped rendering - removed, since nothing else read
  them. (The service-level `most_completed`/`least_completed`/
  `upcoming_exams_list`/`upcoming_exams` keys the Dashboard also
  stopped rendering were *not* removed - `get_dashboard_stats`/
  `get_dashboard_widgets` each have their own dedicated unit tests in
  `progress/tests.py` exercising them as a tested service API
  independent of what the Dashboard UI currently shows, so trimming
  those was judged out of scope for this diff.)
- As a side effect, this closes the dark-mode-inconsistency Known
  Issue below (Dashboard/Progress never had `dark:` classes at all) -
  same tokens everywhere now, nothing left to sweep separately.

**Fix, Part 2 - Dashboard restructure**: `dashboard/index.html` and
`_widgets.html` rewritten around "what needs attention right now"
instead of "everything, all at once":

- Removed the redundant Upcoming Lecture/Upcoming Exam card pair
  (Today's Routine plus the Next Exam metric tile already cover this).
- Removed Most/Least Completed Subject entirely - Progress's full
  per-subject table already shows this, completely.
- Condensed the 4-tile Study Advisor grid into one card, one row per
  insight, since Analytics Insights (linked via a "View full
  insights" action, `components/section_header.html`) already covers
  Study Streak/Priority Chapter/Neglected Chapters/subject ranking in
  more depth - the dashboard's job is a teaser + link, not a second
  copy of the same numbers.
- Condensed the 4-tile Revision grid (Due Today/Overdue/Upcoming/
  Completed This Week) into a progress bar plus a row of count badges,
  linking out to Revision Queue for the actual list.
- Dropped the Upcoming Exams list at the bottom (redundant with the
  Next Exam metric tile and Exam Timeline); kept Recent Activity,
  since nothing else on the site shows it.
- Result: ~15 cards across six sections down to roughly eight
  elements across five, with every number's canonical detail view one
  click away instead of duplicated inline. No context variable, view,
  or query changed - `dashboard/views.py` and every `progress.services`
  function are untouched, so the existing query-count-budget tests
  (Milestone 8/9's fixed-query-count guards) still hold unmodified.

**Verification**: `core/tests_ui.py` updated to assert the new class
vocabulary (`bg-surface`/`text-ink`/etc. instead of the old literals)
and rebuilt-CSS required-utility list; all 536 tests pass, including
every dashboard/revision/analytics-widget test that asserts on exact
rendered text (`"Study Advisor"`, `"Ready For Exam"`, `"Revision"`,
`"No upcoming exam"` - each preserved verbatim in the new layout so
those assertions needed no changes). Compiled Tailwind CSS rebuilt via
`npm run build` and spot-checked for the new tokens.

## Next Milestone

The application is live in production (Render, now on Neon Postgres
per Milestone 18) with real users and real data - deployment itself is
done, not pending. `plan_v1.md` is the master V1 roadmap from here;
its own priority order, cross-checked against this document, is:

1. **GitHub Actions scheduler (`plan_v1.md` Phase A) - shipped and
   verified (Milestone 19).** Live on `main`, secrets set, manual dry
   run passed against production. Fully done.
2. **UI refinement (`plan_v1.md` Phase G)** - visual identity and the
   Dashboard's information density are done (Milestone 20). Still
   open: table-polish (numeric alignment, Milestone 13's Known
   Issues), resolving `auth_card.html`'s dead-code status (Milestone
   15.2's Known Issues).
3. **Production security audit, full reminder acceptance test, backup/
   recovery documentation, final smoke test, monitoring** (`plan_v1.md`
   Phases J-O) - none started yet; the scheduler they depend on
   (K/L) is now verified and ready to test against.
4. Smaller/ongoing: per-user timezone-aware reminder triggers
   (Milestone 15/15.1's Known Issue, still open), GitHub branch
   protection on `main` once the repo goes public or the account
   upgrades to Pro (Milestone 16's Known Issue).
