# Release Checklist

Follow this exactly, in order, for every tagged release - not just
v1.0.0. See `docs/GitWorkflow.md` for the branch this happens on
(`release/x.y.z`, merged into `main` only once every box below is
checked).

## 1. Code Quality

- [ ] `python manage.py test` - full suite passes, zero failures.
- [ ] `python manage.py check` - no issues.
- [ ] `python manage.py makemigrations --check --dry-run` - no changes
      detected (every model change already has a committed migration).

## 2. Frontend

- [ ] `npm run build` (in `theme/static_src/`) - Tailwind rebuilt from
      the latest templates.
- [ ] `python manage.py test core.tests_ui.CompiledCSSTests` passes -
      confirms the rebuilt CSS actually contains what the templates need.

## 3. Static Files

- [ ] `python manage.py collectstatic --noinput` runs cleanly (dry-run
      locally before the platform runs it for real).

## 4. Environment

- [ ] Every variable in `.env.example` has a real value set on the
      deployment platform (not just the dev defaults).
- [ ] `SECRET_KEY` is a real, random production value - never the
      insecure development default.
- [ ] `DEBUG=False` in production.
- [ ] `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` match the real production
      domain.

## 5. Backup

- [ ] Production database backed up (or, for a first deploy, confirm
      there is no production data yet to lose).

## 6. Documentation

- [ ] `CHANGELOG.md` has an entry for this version (Added/Changed/
      Fixed/Internal, as applicable - see the Versioning Policy in
      the README for what bumps which number).
- [ ] `KNOWN_ISSUES.md` reflects the current state - remove anything
      this release fixed, add anything newly deferred.
- [ ] `PROJECT_PROGRESS.md` updated if any architecture changed.

## 7. Git

- [ ] All of the above verified on the `release/x.y.z` branch.
- [ ] `release/x.y.z` merged into `main`.
- [ ] `release/x.y.z` merged back into `develop` (so `develop` never
      falls behind a release's last-minute fixes).
- [ ] Tag created on `main`:
      `git tag -a vX.Y.Z -m "Version X.Y.Z"`.

## 8. Deployment

- [ ] Deploy `main` to the platform.
- [ ] `release` step (`python manage.py migrate --noinput`) completed
      without error - check the platform's deploy logs.

## 9. Smoke Test

- [ ] `/health/` returns `200`.
- [ ] Login works with a real (non-test) account.
- [ ] Dashboard loads with no console errors.
- [ ] A protected page (e.g. `/progress/`) redirects to login when
      logged out, and loads normally when logged in.
- [ ] Staff-only Reminder Administration (`/reminders/admin/`) shows a
      "Ready" or expected email-configuration status.
- [ ] "Send Test Email" from Reminder Administration actually arrives.
- [ ] No broken static assets (check the browser's network tab for any
      404 on `/static/...`).

## 10. Post-Release

- [ ] Push the tag: `git push origin main --tags` (once a remote
      exists).
- [ ] Announce/record the release (see `docs/ReleaseNotes-v1.0.0.md`
      for the v1.0.0 example).
