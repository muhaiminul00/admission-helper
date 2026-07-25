# Developer Guide

## Setup

```bash
git clone <repository>
cd admission-helper

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

cd theme/static_src
npm install
npm run build
cd ../..

python manage.py migrate
python manage.py runserver
```

Copy `.env.example` to `.env` and adjust if you need anything other
than the defaults (SQLite, console email, `DEBUG=True` all work with
zero configuration).

## Everyday Commands

```bash
python manage.py test                          # full test suite
python manage.py test progress.tests_progress_service   # one module
python manage.py check                         # system checks
python manage.py makemigrations --check --dry-run   # verify no missing migrations
npm run build                                  # rebuild Tailwind (theme/static_src/)
npm run dev                                     # watch mode while editing templates
```

Run `npm run build` after adding **any** new Tailwind utility class to
a template - the compiled CSS is git-ignored and only regenerated on
demand (`core/tests_ui.py: CompiledCSSTests` catches a stale build,
but it's faster to just always rebuild after a template change).

## The Fixed Development Workflow

Every code change, from a one-line fix to a full milestone, follows
the same sequence - the same one CI (`.github/workflows/ci.yml`)
enforces automatically:

```text
Modify code
  -> python manage.py test
  -> python manage.py check
  -> npm run build            (if templates changed)
  -> git commit (on a feature/bugfix branch - see docs/GitWorkflow.md)
  -> Pull Request into develop
```

## Conventions This Codebase Expects

- **Views stay thin.** All calculation lives in a `services/` module
  under the owning app (e.g. `progress/services/progress_service.py`,
  `reminders/services/engine.py`). A view calls a service function and
  passes the result to a template; it never computes a percentage,
  due date, or trigger condition itself.
- **One shared implementation per visual element.** Before adding a
  new card/badge/button style, check `templates/components/*.html` and
  `core/templatetags/ui_tags.py` first - extend what exists rather
  than writing page-specific CSS.
- **Every academic entity has one canonical page.** Never build a
  second detail view for a `Subject`/`Chapter`/`Lecture`/`Exam` -
  link to the existing canonical URL instead.
- **Bulk, not N+1.** Any calculation shown on a list page (Analytics
  tables, timeline cards) must have a `get_bulk_*()` variant costing
  one query regardless of row count - see `progress_service.py`'s
  `get_bulk_subject_progress()`/etc. for the established pattern
  (`Sum(Case(When(...)))` over an annotated queryset).
- **Business logic and presentation stay separate**, even when a new
  presentation-layer calculation looks similar to an existing one -
  see `progress_service.py`'s docstring for why it doesn't touch
  `revision.is_lecture_completed()`'s definition of "complete."
- **Write the test that would have caught the bug.** Every milestone
  in `PROJECT_PROGRESS.md` documents real bugs found during its own
  development (Django template filter gotchas, off-by-one week
  numbering, N+1 queries) - the fix always came with a regression test
  asserting the specific failure mode, not just the happy path.

## Adding a New Reminder Type

1. Add a generator module to `reminders/services/` (`generate(now=None,
   current_time=None, users=None)` returning a list of `ReminderJob`s -
   copy an existing generator's shape).
2. Register it in `reminders/services/engine.py`'s `GENERATORS` dict
   and `reminders/models.py`'s `ReminderLog.ReminderType` choices.
3. Add its template to `templates/emails/` and an entry to
   `reminders/emails/registry.py`.
4. Add a management command under `reminders/management/commands/`.
5. Add it to the Notification Preferences form/model and the Reminder
   Test Center's type list.

## Adding a New Analytics/Progress Display

Reuse `progress/services/progress_service.py` (multi-dimensional,
per-topic) or `progress/services/analytics.py` (binary completion
percentage) - whichever matches what's actually being shown; see
`docs/Architecture.md` for which is which and why they're kept
separate.

## Project Structure

See `PROJECT_PROGRESS.md`'s "Current Project Structure" section for
the complete, annotated file tree - it's kept up to date every
milestone and is more detailed than is useful to duplicate here.

## Documentation Map

| Document | Audience | Purpose |
| --- | --- | --- |
| `README.md` | Everyone | Overview, quick start |
| `docs/DeveloperGuide.md` (this file) | Developers | Local setup, conventions |
| `docs/Architecture.md` | Developers | How the system is put together |
| `docs/Deployment.md` | Whoever deploys it | Production setup, step by step |
| `docs/UserGuide.md` | Students using the app | How to use every feature |
| `docs/GitWorkflow.md` | Contributors | Branching/release process |
| `PROJECT_PROGRESS.md` | Developers | Full milestone-by-milestone history |
| `CHANGELOG.md` | Everyone | What changed, per version |
| `KNOWN_ISSUES.md` | Everyone | What's known-imperfect and deliberately deferred |
| `RELEASE_CHECKLIST.md` | Whoever ships a release | The exact steps, every time |
