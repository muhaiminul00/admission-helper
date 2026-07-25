"""Rendering: turns a `ReminderJob` into (subject, html_body,
text_body). Knows nothing about generation (it trusts `job.context`
completely) or delivery (it returns strings, never sends anything).
"""

import re

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .registry import REMINDER_TYPES


def render_reminder(job):
    config = REMINDER_TYPES[job.reminder_type]
    subject = config["subject"](job.context)
    html_body = render_to_string(config["template"], {**job.context, "user": job.user})
    text_body = to_plain_text(html_body)
    return subject, html_body, text_body


def to_plain_text(html_body):
    """A plain-text alternative generated from the rendered HTML
    (Phase 8), rather than hand-maintaining a second template per
    reminder type - every email template is already written with
    short, readable block structure, so stripped tags plus whitespace
    collapsing reads cleanly in a plain-text client. Public (not just
    `render_reminder()`'s internal helper) so Milestone 15.1's "Send
    Test Email" tool - which deliberately bypasses the reminder engine
    entirely, per its own spec - can still reuse this instead of
    duplicating it (Phase 3.5: "No duplicated template code")."""
    text = strip_tags(html_body)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
