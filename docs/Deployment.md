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
to create from scratch: the web service and a managed PostgreSQL
database. Applying it:

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
instance to the web service - also never entered manually.

Render validates `render.yaml` against its own current Blueprint
schema at apply time. If any field is rejected, that means Render's
schema has moved on since this file was written - check the error
message and Render's own Blueprint reference before assuming the
underlying deployment plan (one web service, one Postgres instance) is
wrong.

### Render Free plan: no Scheduled Jobs (Milestone 17.1)

`render.yaml` originally also defined five Render Scheduled Jobs
(`type: cron`), one per reminder command. **Render's Free plan
rejects Blueprints containing any `type: cron` service outright** -
apply fails immediately with `plan free not valid for service type
cron`, before creating anything at all. Those five job definitions
have been removed from `render.yaml` so the Blueprint applies cleanly
on Free.

This has no effect on the application itself: the five `send_*`
reminder commands (`reminders/management/commands/`) are unchanged,
fully idempotent, and safe to run manually at any time (e.g. via
Render's one-off Shell, or locally against the production database).
What's missing on Free is *automatic scheduling* - nothing invokes
those commands on its own yet. Reminder scheduling is deliberately
deferred to a follow-up milestone rather than solved with a
workaround here (e.g. a background thread inside the web process,
which would violate this milestone's "no alternative schedulers"
rule and behave unreliably on a service that can spin down when
idle). See Section 6 below for the schedule this project will use
once a scheduling mechanism (a paid Render plan, or an external
scheduler) is introduced.

### Render Free plan: no `preDeployCommand` either (Milestone 17.1)

Render also rejected `render.yaml`'s `preDeployCommand` on the web
service ("pre-deploy command is not supported for free tier
services") - like Scheduled Jobs, this is a paid-tier-only Blueprint
feature. The migration step (`python manage.py migrate --noinput`)
has been moved into `startCommand` instead, so it now runs
immediately before gunicorn starts, on every deploy and every service
restart:

```text
startCommand: python manage.py migrate --noinput && gunicorn admission_helper.wsgi --bind 0.0.0.0:$PORT ...
```

This is safe: Django migrations are idempotent (a no-op if already
applied), so running the command on every restart - not just every
deploy - has no adverse effect. The one behavioral difference from
`preDeployCommand`: a failed migration now also fails the web
process's own boot, rather than being caught earlier in a separate
pre-deploy step - check the web service's own deploy logs (not a
separate pre-deploy log) if a deploy fails at this point.

## Manual Setup (Railway, or Render without a Blueprint)

The steps below describe the same end state `render.yaml` automates -
useful if deploying to Railway, or to Render without using a
Blueprint.

### 1. Database (PostgreSQL)

**Current production database (Milestone 18): Neon**, not Render's own
Postgres. Render's free managed Postgres carries a hard 30-day expiry
per instance and is not renewable - the original instance
(`admission-helper-db`, created 2026-07-26) was set to be deleted
2026-08-25, which forced a migration onto Neon's free tier (no expiry)
ahead of everything else in `plan_v1.md`. `DATABASE_URL` points at
Neon's pooled connection string; nothing else about the app changed -
`DATABASES` (in `admission_helper/settings.py`) uses
`dj_database_url.config()` and doesn't care which Postgres provider is
behind the URL. With `DATABASE_URL` unset, the app falls back to the
same local `db.sqlite3` file development always uses, plus a health
check (`CONN_HEALTH_CHECKS`) so a stale persistent connection
reconnects transparently instead of surfacing as a request-time error.
Never run production on SQLite - it doesn't survive an ephemeral
filesystem, can't handle more than one web process, and (per Milestone
18, Part B) doesn't even enforce the same column constraints Postgres
does, which let a `varchar(255)` overflow slip past local testing and
CI once already.

To move production data to a new Postgres instance (Neon or
otherwise) without `pg_dump`/`psql`: Django's own `dumpdata`/
`loaddata` management commands work directly through `psycopg` (the
same driver the app already depends on) against any reachable
`DATABASE_URL` -

```bash
# 1. Point DATABASE_URL at the OLD database, dump everything:
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.permission -e sessions \
  -o dump.json

# 2. Point DATABASE_URL at the NEW database, build the schema, load:
python manage.py migrate --noinput
python manage.py loaddata dump.json

# 3. loaddata preserves explicit PKs but does NOT advance Postgres's
#    identity sequences - reset every sequence or the next INSERT can
#    collide with an already-used ID:
python manage.py sqlsequencereset <app_label> [<app_label> ...]
#    (pipe the output into the new database via `manage.py dbshell`,
#    or run each statement through the provider's SQL console/MCP)
```

Then update `DATABASE_URL` on the hosting platform and redeploy.

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
| `DJANGO_SUPERUSER_USERNAME`/`_EMAIL`/`_PASSWORD` | Bootstraps one admin/staff user on every deploy (see Section 7) | **Optional** - only needed on Render Free, since there's no Shell/One-Off Jobs access to run `createsuperuser` interactively; leave all three unset and `ensure_superuser` silently no-ops | Not applicable (Render Free workaround only) |

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

**Routine Archive PDFs (Milestone 18, Part D): solved via git, not a
disk.** `media/routines/*.pdf` is specifically un-ignored in
`.gitignore` (the rest of `media/` stays ignored) and the current
routine PDF is committed directly to the repository - the same
pattern already used for `data/dataset_archive/`. Since Render/Railway
rebuild the filesystem from git on every deploy, this means a
committed routine PDF ships with every deploy automatically, with no
persistent disk needed. Adding a new routine PDF is now: drop
`YYYY-MM.pdf` into `media/routines/`, `git add` it (it's no longer
gitignored), commit, and push through the normal branch/PR flow -
Section 8 below covers importing that routine's structured CSV data
the same way.

This only works because the Routine Archive's content is curated and
git-committed, not user-uploaded at runtime. A future feature
involving real user-uploaded media (profile pictures, attachments,
anything a user submits through the app itself) would still need
either a persistent disk (attach one manually in the Render dashboard,
**Settings → Disks** - `render.yaml` does not do this automatically)
or object storage (S3, Cloudinary, Neon Object Storage). Don't extend
the git-tracking approach to anything users upload themselves.

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

**Status (Milestone 19, Phase A): GitHub Actions, live.**
`.github/workflows/reminders.yml` runs the five `send_*` management
commands unchanged, on GitHub's infrastructure, against the
production Neon database - Render Free supports no Scheduled Jobs at
all (Milestone 17.1), so an external scheduler was the only option
that needed no paid plan. No reminder logic, no app code changed.

Schedule (unchanged from the original Milestone 17 design - derived
from each command's actual trigger logic, not guessed):

```text
send_daily_agenda        0 * * * *   (hourly)
send_weekly_overview     0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_exam_reminders      0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_revision_reminders  0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
send_weekly_progress     0 3 * * *   (daily, 03:00 UTC = 09:00 Asia/Dhaka)
```

The workflow has two `schedule:` triggers (`0 * * * *` and
`0 3 * * *`); a step reads `github.event.schedule` to pick which
command(s) that firing should run, so one workflow file covers all
five without duplicating jobs.

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
verification run. Each also reports per-failure detail (recipient +
exact error) to its own stdout, not just a bare count - check the
workflow run's logs directly if a send count looks wrong.

**Required GitHub Actions secrets** (repo Settings -> Secrets and
variables -> Actions), all read the same way `render.yaml`'s envVars
are:

```text
DATABASE_URL        Neon connection string (pooled is fine - one-off, short-lived runs)
SECRET_KEY           same value as production's SECRET_KEY
EMAIL_HOST_USER       Gmail address reminders send from
EMAIL_HOST_PASSWORD   Gmail app password (not the account password)
```

`DEBUG=False` and `TIME_ZONE=Asia/Dhaka` are hardcoded into the
workflow's `env:` block, not secrets, since neither is sensitive.

**Manual/test runs**: trigger the workflow from the Actions tab
("Reminder Scheduler" -> "Run workflow") - pick a single command or
`all`, and leave `dry_run` checked (the default) to verify without
sending anything. Uncheck it only once a dry run looks correct.

### 7. Superuser Creation

Staff access (Datasets, Reminder Administration) requires a Django
superuser or a regular user with `is_staff=True`. Normally:

```bash
python manage.py createsuperuser
```

run via the platform's shell/one-off-job feature (Render "Shell",
Railway "Run a command") - not as part of the release/migrate step,
since it needs interactive input.

**On Render Free (Milestone 17.1): neither Shell nor One-Off Jobs are
available** (both are paid-tier-only), so there is no way to run the
above interactively against the deployed instance. `render.yaml`'s
`startCommand` instead runs:

```bash
python manage.py ensure_superuser
```

on every deploy/restart - a small custom command
(`core/management/commands/ensure_superuser.py`) that reads
`DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_EMAIL` /
`DJANGO_SUPERUSER_PASSWORD` from the environment and idempotently
creates-or-updates exactly that one user as a superuser. Set those
three in the Render dashboard (see the checklist in Section 2) if you
have no other way to reach the admin/staff pages; leave them unset and
the command silently does nothing. Because it runs on every restart,
changing `DJANGO_SUPERUSER_PASSWORD` and redeploying is also how you
reset that account's password if you ever lose it - there is no
"forgot password" flow needed for this one bootstrap account.

If you deploy somewhere that *does* have shell/one-off-job access
(Railway, or a paid Render plan), running `createsuperuser`
interactively works exactly as before and `ensure_superuser` is not
required.

### 8. Initial Data

The application starts with zero academic data. Import the coaching
routine CSVs (`routine.csv`, `lecture_topics.csv`, `exams.csv`, plus
`subjects.csv`/`chapters.csv`) with:

```bash
python manage.py import_csv
```

Run `import_csv --preview` first to validate without writing anything,
and see `06_CSV_Import_Specification.md` for the exact file formats.

**On Render Free (Milestone 17.1)**, this also runs automatically as
part of `startCommand` on every deploy/restart, for the same reason as
`ensure_superuser` above (no Shell/One-Off Jobs to run it by hand).
It's safe to run repeatedly: every importer uses `update_or_create()`
keyed on each model's natural identity, so re-running never creates
duplicate data - if the CSVs at the repo root are ever updated and
committed, the next deploy picks up the changes automatically too.

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
- `manage.py migrate` ran cleanly (check the web service's own deploy
  logs - on Render Free the migration runs as part of `startCommand`,
  not a separate pre-deploy step; see "Render Free plan: no
  `preDeployCommand` either" above).
- On Render Free (Milestone 17.1): no Scheduled Jobs exist yet - see
  Section 6 above. Confirm reminders instead by running one `send_*`
  command manually via Render's Shell and checking its output. On a
  plan that supports Scheduled Jobs, confirm each of the five has run
  at least once (Render → the job → Logs) and reports a sane count
  with no unexpected `FAILED` lines.

See `RELEASE_CHECKLIST.md` for the complete pre/post-deploy checklist
this project follows for every release, not just v1.0.0.

## Recovery

- **A deploy fails during migration**: on a plan with
  `preDeployCommand` support, Render runs it before traffic switches
  to the new instance, so a failed migration blocks the deploy rather
  than serving a broken app. On Render Free (Milestone 17.1),
  migration runs as the first step of `startCommand` instead - a
  failed migration means the web process never finishes booting and
  the deploy is reported as failed the same way. Either way: check the
  deploy's logs, fix forward (a new migration, not editing history),
  and redeploy.
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
