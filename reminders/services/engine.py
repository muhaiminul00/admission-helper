"""The Reminder Engine (Milestone 15, Phase 1 - Architectural Rule).

Asks "what reminders should be sent right now?" rather than exposing
"Run Daily Reminder"/"Run Weekly Reminder"/"Run Exam Reminder" as
distinct code paths. `GENERATORS` is the only thing a new reminder
type needs to extend - each generator module (`daily`/`weekly`/
`exams`/`revision`/`progress`) independently answers "what's due right
now?" for its own type; this file never contains type-specific logic
itself.

Duplicate protection (Phase 11) lives here, not in each generator:
every generated job is checked against `ReminderLog` before being
counted as "due," so a generator never has to know whether it already
ran today - it can (and does) simply describe every reminder that
*would* be correct right now, and the engine filters out what already
went out.

Milestone 15.1 added two purely additive parameters, both defaulted to
production's exact original behavior: `users` (Reminder
Administration's recipient selector - narrows which users a generator
considers, never changes what's due for whichever users are
considered) and `triggered_by` (records manual-vs-automatic on
`ReminderLog`, for the Reminder Activity Log). Neither touches trigger
conditions, delivery, or duplicate-protection semantics.
"""

from dataclasses import dataclass

from ..emails.delivery import send_reminder
from ..models import ReminderLog
from . import daily, exams, progress as progress_reminders, revision, weekly

GENERATORS = {
    ReminderLog.ReminderType.DAILY_AGENDA: daily.generate,
    ReminderLog.ReminderType.WEEKLY_OVERVIEW: weekly.generate,
    ReminderLog.ReminderType.REVISION_DUE: revision.generate,
    ReminderLog.ReminderType.WEEKLY_EXAM: exams.generate_weekly,
    ReminderLog.ReminderType.MONTHLY_EXAM: exams.generate_monthly,
    ReminderLog.ReminderType.WEEKLY_PROGRESS: progress_reminders.generate,
}


@dataclass
class ReminderResult:
    """One attempted (or, with `dry_run`, would-be) delivery -
    everything Phase 7/8's delivery feedback and activity log need,
    without either of them re-deriving success/failure themselves."""

    job: object
    delivered: object  # True/False, or None for a dry-run (not attempted)
    error: str = ""


def _already_sent_keys(jobs):
    if not jobs:
        return set()
    user_ids = {job.user.id for job in jobs}
    types = {job.reminder_type for job in jobs}
    existing = ReminderLog.objects.filter(
        user_id__in=user_ids, reminder_type__in=types
    ).values_list("user_id", "reminder_type", "reference_key")
    return set(existing)


def get_due_reminders(reminder_types=None, now=None, current_time=None, users=None):
    """Every `ReminderJob` that should be sent right now, across the
    requested generator(s) (default: all), already filtered against
    user preferences (each generator's own concern) and already-sent
    history (this function's concern). `now`/`current_time` let tests
    (and only tests - production callers never pass them) pin the
    date/time-of-day a generator sees, since some reminders gate on
    both (e.g. the Daily Agenda's configurable delivery time). `users`
    narrows which users are considered (default: every active user)."""
    jobs = []
    for reminder_type, generator in GENERATORS.items():
        if reminder_types and reminder_type not in reminder_types:
            continue
        jobs.extend(generator(now=now, current_time=current_time, users=users))

    sent_keys = _already_sent_keys(jobs)
    return [job for job in jobs if (job.user.id, job.reminder_type, job.reference_key) not in sent_keys]


def run(reminder_types=None, now=None, current_time=None, dry_run=False, users=None, triggered_by=None):
    """Generates + delivers every due reminder, logging each send so it
    is never generated again (Phase 11). Returns a `ReminderResult` per
    job (or, with `dry_run=True`, one per job that *would* send -
    nothing is delivered or logged in that case). A delivery failure
    (missing email, an SMTP exception) still logs - Phase 11's
    "never sent twice" applies to the occurrence, not just to
    successful sends, so a failure is never silently retried forever
    by the next scheduled run."""
    jobs = get_due_reminders(reminder_types, now, current_time, users)
    triggered_by = triggered_by or ReminderLog.TriggeredBy.AUTOMATIC

    results = []
    for job in jobs:
        if dry_run:
            results.append(ReminderResult(job=job, delivered=None))
            continue

        try:
            delivered = send_reminder(job)
            error = "" if delivered else "This user has no email address on file."
        except Exception as exc:  # noqa: BLE001 - any backend/SMTP failure must still be logged, not crash the run
            delivered = False
            error = str(exc)

        ReminderLog.objects.create(
            user=job.user, reminder_type=job.reminder_type, reference_key=job.reference_key,
            status=ReminderLog.Status.SUCCESS if delivered else ReminderLog.Status.FAILED,
            error_message=error, triggered_by=triggered_by,
        )
        results.append(ReminderResult(job=job, delivered=delivered, error=error))
    return results
