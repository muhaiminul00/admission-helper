# Deployment Guide

Primary target: **Render**, deployed via `render.yaml` (a Blueprint -
infrastructure as code). Railway works too, using the same `Procfile`
and environment variables, but without the Blueprint automation below.

```text
release: python manage.py migrate --noinput
web: gunicorn admission_helper.wsgi --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --timeout 30 --access-logfile - --error-logfile -
```

## Deploying via `render.yaml` (recommended)

`render.yaml` at the repository root defines everything Render needs
to create from scratch: the web service, a managed PostgreSQL
database, and five Scheduled Jobs (one per reminder command) - see
Section 6 below for why those five specific schedules. Applying it:

1. Render dashboard → **New → Blueprint**.
2. Connect this GitHub repository, branch `main`.
3. Render reads `render.yaml` and shows a plan of what it will create -
   review it, then **Apply**.
4. Render will pause on any environment variable marked `sync: false`
   in `render.yaml` and prompt you to enter it - see the checklist in
   Section 2 below for exactly which ones and what to enter.

`SECRET_KEY` is generated automatically by Render (`generateValue:
true` in `render.yaml`) - you never see or set it yourself.
`DATABASE_URL` is wired automatically from the created Postgres
instance to every service that needs it (web + all five cron jobs) -
also never entered manually.

Render validates `render.yaml` against its own current Blueprint
schema at apply time. If any field is rejected, that means Render's
schema has moved on since this file was written - check the error
message and Render's own Blueprint reference before assuming the
underlying deployment plan (one web service, one Postgres instance,
five cron jobs, the commands/schedule described below) is wrong.

## Manual Setup (Railway, or Render without a Blueprint)

The steps below describe the same end state `render.yaml` automates -
useful if deploying to Railway, or to Render without using a
Blueprint.

### 1. Database (PostgreSQL)

Create a Postgres instance on the platform and copy its connection
string into the `DATABASE_URL` environment variable. `DATABASES` (in
`admission_helper/settings.py`) uses `dj_database_url.config()`: with
`DATABASE_URL` set, Postgres is used; unset, the app falls back to the
same local `db.sqlite3` file development always uses, plus a health
check (`CONN_HEALTH_CHECKS`) so a stale persistent connection
reconnects transparently instead of surfacing as a request-time error.
Never run production on SQLite - it doesn't survive an ephemeral
filesystem and can't handle more than one web process.

### 2. Environment Variables

See `.env.example` for the complete, commented list. The checklist
below is specifically what `render.yaml` cannot fill in for you
(`sync: false` fields) - everything else it either generates
(`SECRET_KEY`) or hardcodes to a sensible production default
(`DEBUG=False`, `TIME_ZONE=Asia/Dhaka`).

| Variable | Purpose | Manual entry required? | Already in `.env.example`? |
| --- | --- | --- | --- |
| `SECRET_KEY` | Django's cryptographic signing key | No - Render generates it | Yes (dev only) |
| `DEBUG` | Must be `False` in production | No - `render.yaml` sets it | Yes |
| `ALLOWED_HOSTS` | Hostnames this deployment answers to | **Yes** - the exact Render-assigned domain (e.g. `admission-helper.onrender.com`), known only after the service exists | Yes |
| `CSRF_TRUSTED_ORIGINS` | Origins allowed to submit cross-site POSTs | **Yes** - `https://` + the same domain | Yes |
| `DATABASE_URL` | PostgreSQL connection string | No - wired automatically from the Blueprint's database | Documented, not a literal value |
| `EMAIL_HOST_USER` | Gmail address reminders are sent from | **Yes** - a real Gmail address, never invented | Yes |
| `EMAIL_HOST_PASSWORD` | Gmail **app password** (not your account password) | **Yes** - generate one at your Google Account's App Passwords page | Yes |
| `TIME_ZONE` | IANA timezone every date/time calculation uses | No - `render.yaml` sets `Asia/Dhaka` (change only if the admission cycle being tracked moves timezone) | Yes |
| `WEB_CONCURRENCY` | Gunicorn worker count | No - defaults to `2`; raise it only if the Render plan has the memory for more | Not applicable (Procfile-only) |

Production secrets (`EMAIL_HOST_PASSWORD` above, and anything like it)
belong **only** in Render's Environment Variables - never in a GitHub
Secret, never committed, never in this repository in any form.

### 3. Static Files (WhiteNoise)

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

### 4. Media Persistence

`media/routines/` (the Routine Archive - see the README) needs to
survive redeploys. Attach a persistent disk on Render/Railway and
point `MEDIA_ROOT` at it (already the default path;
`admission_helper/settings.py` reads `MEDIA_ROOT = BASE_DIR / 'media'`
- mount the persistent disk at that path). Without a persistent disk,
an uploaded (copied-in) routine PDF disappears on the next deploy.
`render.yaml` does not attach one automatically - add a disk to the
web service manually in the Render dashboard if you plan to use the
Routine Archive (**Settings → Disks** on the service).

### 5. Email (SMTP)

With `DEBUG=False` and both `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`
set, `settings.py` automatically switches from the console backend to
real Gmail SMTP (port 587, TLS). Use a Gmail **app password**, not your
account password - Gmail requires this for any third-party SMTP
client. Verify delivery works using the Reminder Administration
page's "Send Test Email" tool (`/reminders/admin/`, staff-only) before
relying on it - it bypasses the reminder engine entirely and exists
specifically for this.

### 6. Reminder Scheduler

Nothing sends reminders automatically until a scheduler runs the five
`send_*` management commands - `render.yaml` configures this as five
Render Scheduled Jobs. The schedules are derived from each command's
actual trigger logic, not guessed:

```text
send_daily_agenda        0 * * * *   (hourly)
send_weekly_overview     0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_exam_reminders      0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_revision_reminders  0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_weekly_progress     0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
```

**Daily Agenda runs hourly** because `NotificationPreference.
daily_agenda_time` is per-user and configurable - only an hourly
cadence reliably catches every possible setting.

**The other four run once daily at 03:00 UTC**, not at midnight, for a
specific reason: `reminders/services/exams.py`'s exam-day-morning
reminder additionally requires the current wall-clock time to be past
`EXAM_DAY_MORNING_TIME` (08:00 in `Asia/Dhaka`). 03:00 UTC = 09:00
`Asia/Dhaka` - safely past that gate. Running any earlier (e.g.
midnight UTC = 06:00 Dhaka) would silently skip every exam-day
reminder, since the generator itself would correctly decide "not yet
morning" and produce nothing - not a crash, just a quietly-missed
reminder, which is why this schedule was derived from the actual code
rather than assumed. The other three commands (`send_weekly_overview`/
`send_revision_reminders`/`send_weekly_progress`) have no time-of-day
gate, only a date one, so they run safely at this same time out of
convenience/consistency, not necessity.

Every command is idempotent (`ReminderLog` prevents any duplicate
send, even across manual re-runs) and accepts `--dry-run` for a no-op
verification run. Each also now reports per-failure detail (recipient
+ exact error) to its own stdout, not just a bare count - check a
Scheduled Job's logs directly if a send count looks wrong.

### 7. Superuser Creation

Staff access (Datasets, Reminder Administration) requires a Django
superuser or a regular user with `is_staff=True`. Create one after the
first deploy:

```bash
python manage.py createsuperuser
```

Run this via the platform's shell/one-off-job feature (Render "Shell",
Railway "Run a command") - not as part of the release/migrate step,
since it needs interactive input.

### 8. Initial Data

The application starts with zero academic data. Import the coaching
routine CSVs (`routine.csv`, `lecture_topics.csv`, `exams.csv`, plus
`subjects.csv`/`chapters.csv`) with:

```bash
python manage.py import_csv
```

Run `import_csv --preview` first to validate without writing anything,
and see `06_CSV_Import_Specification.md` for the exact file formats.

### 9. Health Check

Point the platform's health check at `/health/` - an unauthenticated,
database-free liveness probe (`core.views.HealthCheckView`) that
returns `{"status": "ok"}`. `render.yaml`'s web service already
declares this via `healthCheckPath`.

### 10. Verifying a Deploy

After the first deploy, confirm:

- `/health/` returns `200`.
- Login/registration work.
- Staff Reminder Administration (`/reminders/admin/`) shows "Ready"
  status for email configuration, and "Send Test Email" actually
  arrives.
- `manage.py migrate` ran cleanly (check the deploy/pre-deploy step's
  logs).
- Each of the five Scheduled Jobs has run at least once (Render →
  the job → Logs) and reports a sane count with no unexpected
  `FAILED` lines.

See `RELEASE_CHECKLIST.md` for the complete pre/post-deploy checklist
this project follows for every release, not just v1.0.0.

## Recovery

- **A deploy fails during migration**: Render's `preDeployCommand`
  runs before traffic switches to the new instance, so a failed
  migration blocks the deploy rather than serving a broken app -
  check the deploy's logs, fix forward (a new migration, not editing
  history), and redeploy.
- **A Scheduled Job fails repeatedly**: check its logs for the
  `FAILED ->` lines the command now prints; a single user's bad email
  address never blocks anyone else's reminder (see Section 6), so a
  full-job failure means something more fundamental (DATABASE_URL,
  SMTP credentials) needs checking via the Reminder Administration
  page's diagnostics.
- **Rolling back**: redeploy a previous commit/tag from the Render
  dashboard (Deploys → select a prior successful deploy → Redeploy).
  Never force-push or rewrite `main`'s history to "undo" a bad
  deploy - `git revert` a commit forward instead.
