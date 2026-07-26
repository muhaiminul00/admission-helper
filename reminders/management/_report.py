"""Shared stdout reporting for the five `send_*` commands (Milestone
17, Phase 2 - production observability). Not a reminder-system
redesign: `engine.run()`'s behavior, return value, and per-job
success/failure semantics are all unchanged - this only makes what it
already returns visible in a scheduled job's log output, which
previously only reported a bare count and silently dropped which
deliveries (if any) failed and why.
"""


def report_results(command, results, noun, dry_run):
    """`results` is `engine.run()`'s return value - a list of
    `ReminderResult`. Prints the same summary line every existing test
    already asserts against (`"{verb} {N} {noun}."`), then, only when
    something actually failed, one warning line per failure with the
    recipient and the exact error `ReminderLog.error_message` also
    records - so a scheduled job's log is self-explanatory without
    needing to open Reminder Administration to see what went wrong.
    """
    verb = "Would send" if dry_run else "Sent"

    if dry_run:
        command.stdout.write(command.style.SUCCESS(f"{verb} {len(results)} {noun}."))
        return

    failures = [result for result in results if not result.delivered]
    successes = len(results) - len(failures)
    command.stdout.write(command.style.SUCCESS(f"{verb} {successes} {noun}."))

    for result in failures:
        recipient = result.job.user.email or f"user #{result.job.user.id} (no email on file)"
        command.stdout.write(command.style.WARNING(f"  FAILED -> {recipient}: {result.error}"))
    if failures:
        command.stdout.write(
            command.style.WARNING(f"{len(failures)} {noun} failed to send - see above.")
        )
