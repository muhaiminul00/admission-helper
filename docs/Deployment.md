# Deployment Guide

Targets Render or Railway, both of which build from the repository's
`Procfile`:

```text
release: python manage.py migrate --noinput
web: gunicorn admission_helper.wsgi --log-file -
```

## 1. Database (PostgreSQL)

Create a Postgres instance on the platform and copy its connection
string into the `DATABASE_URL` environment variable. `DATABASES` (in
`admission_helper/settings.py`) uses `dj_database_url.config()`: with
`DATABASE_URL` set, Postgres is used; unset, the app falls back to the
same local `db.sqlite3` file development always uses. Never run
production on SQLite - it doesn't survive an ephemeral filesystem and
can't handle more than one web process.

## 2. Environment Variables

Set every variable in `.env.example` as a real platform environment
variable - never commit a `.env` file. At minimum for production:

```text
SECRET_KEY=<a real, random secret - never the dev default>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
DATABASE_URL=<from the platform's Postgres add-on>
EMAIL_HOST_USER=<gmail address>
EMAIL_HOST_PASSWORD=<gmail app password, not your real password>
```

See `.env.example` for the complete list and every variable's
purpose/default.

## 3. Static Files (WhiteNoise)

The platform's build command must install dependencies, build
Tailwind, and run `collectstatic`:

```bash
pip install -r requirements.txt \
  && npm --prefix theme/static_src ci \
  && npm --prefix theme/static_src run build \
  && python manage.py collectstatic --noinput
```

Compiled Tailwind CSS (`theme/static/css/dist/styles.css`) is
git-ignored (see `PROJECT_PROGRESS.md`, Milestone 11.2's build-pipeline
incident) - it must be built at deploy time, every time, not committed
once and forgotten. `manage.py collectstatic` then gathers everything
under `STATIC_ROOT`, and WhiteNoise (`whitenoise.middleware.
WhiteNoiseMiddleware`, already wired in `settings.py`) serves it
directly from the Django process - no separate static file server or
CDN is required for this project's scale.

## 4. Media Persistence

`media/routines/` (the Routine Archive - see the README) needs to
survive redeploys. Attach a persistent disk on Render/Railway and
point `MEDIA_ROOT` at it (already the default path;
`admission_helper/settings.py` reads `MEDIA_ROOT = BASE_DIR / 'media'`
- mount the persistent disk at that path). Without a persistent disk,
an uploaded (copied-in) routine PDF disappears on the next deploy.

## 5. Email (SMTP)

With `DEBUG=False` and both `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`
set, `settings.py` automatically switches from the console backend to
real Gmail SMTP (port 587, TLS). Use a Gmail **app password**, not your
account password - Gmail requires this for any third-party SMTP
client. Verify delivery works using the Reminder Administration
page's "Send Test Email" tool (`/reminders/admin/`, staff-only) before
relying on it - it bypasses the reminder engine entirely and exists
specifically for this.

## 6. Reminder Scheduler

Nothing sends reminders automatically until a scheduler is configured
to run the five `send_*` management commands. Neither Render nor
Railway runs cron jobs by default from a `Procfile` alone - use the
platform's own Scheduled Jobs feature (Render "Cron Jobs", Railway
"Cron Schedule") pointed at:

```bash
python manage.py send_daily_agenda      # at least hourly
python manage.py send_weekly_overview   # once daily
python manage.py send_exam_reminders    # once daily
python manage.py send_revision_reminders  # once daily
python manage.py send_weekly_progress   # once daily
```

Every command is idempotent (`ReminderLog` prevents any duplicate
send) and accepts `--dry-run` for a no-op verification run.

## 7. Superuser Creation

Staff access (Datasets, Reminder Administration) requires a Django
superuser or a regular user with `is_staff=True`. Create one after the
first deploy:

```bash
python manage.py createsuperuser
```

Run this via the platform's shell/one-off-job feature (Render "Shell",
Railway "Run a command") - not as part of the `Procfile`'s `release`
step, since it needs interactive input.

## 8. Initial Data

The application starts with zero academic data. Import the coaching
routine CSVs (`routine.csv`, `lecture_topics.csv`, `exams.csv`, plus
`subjects.csv`/`chapters.csv`) with:

```bash
python manage.py import_csv
```

Run `import_csv --preview` first to validate without writing anything,
and see `06_CSV_Import_Specification.md` for the exact file formats.

## 9. Health Check

Point the platform's health check at `/health/` - an unauthenticated,
database-free liveness probe (`core.views.HealthCheckView`) that
returns `{"status": "ok"}`.

## 10. Verifying a Deploy

After the first deploy, confirm:

- `/health/` returns `200`.
- Login/registration work.
- Staff Reminder Administration (`/reminders/admin/`) shows "Ready"
  status for email configuration, and "Send Test Email" actually
  arrives.
- `manage.py migrate` ran cleanly (check the `release` step's logs).

See `RELEASE_CHECKLIST.md` for the complete pre/post-deploy checklist
this project follows for every release, not just v1.0.0.
