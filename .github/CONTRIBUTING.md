# Contributing

Thanks for your interest in Admission Helper. This is primarily a
personal project, but contributions that fit its scope are welcome.

## Before You Start

1. Read `README.md`'s "Version 1 Scope" section and `KNOWN_ISSUES.md` -
   check your idea isn't already explicitly out of scope or already
   tracked.
2. Read `docs/DeveloperGuide.md` for local setup and this project's
   conventions (service-layer separation, the shared design system,
   bulk-not-N+1 queries).
3. Read `docs/GitWorkflow.md` - this project follows a strict
   `main`/`develop`/`feature`/`bugfix`/`hotfix`/`release` branching
   model. **No direct commits to `main`.**

## Workflow

1. Fork the repository (or branch directly, if you have push access).
2. Branch from `develop`:
   - `feature/short-description` for new functionality.
   - `bugfix/short-description` for a non-urgent fix.
3. Make your change, following `08_Coding_Standards.md`.
4. Run the full local check sequence:
   ```bash
   python manage.py test
   python manage.py check
   python manage.py makemigrations --check --dry-run
   npm run build   # in theme/static_src/, if you touched a template
   ```
5. Open a Pull Request into `develop` using the PR template. CI
   (`.github/workflows/ci.yml`) must pass before merge.

## Reporting Bugs / Requesting Features

Use the issue templates (`.github/ISSUE_TEMPLATE/`) - they'll prompt
you for what's actually needed to act on the report.

## Code Style

- Views stay thin; all calculation lives in a `services/` module.
- Reuse `templates/components/*.html` and `core/templatetags/
  ui_tags.py` before writing new page-specific styling.
- Every academic entity has exactly one canonical page - never add a
  second detail view for something that already has one.
- See `08_Coding_Standards.md` for the full style guide.

## Code of Conduct

This project follows the Contributor Covenant - see
`.github/CODE_OF_CONDUCT.md`.
