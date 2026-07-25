"""Delivery: sends one already-rendered reminder email.

The only function in this whole package that touches
`django.core.mail` - the reminder engine calls `send_reminder(job)`
and never sees an SMTP detail. Swapping providers (SES/SendGrid/
Mailgun) only ever means changing `EMAIL_BACKEND` in settings.py
(Django's own backend abstraction), never this function or anything
upstream of it (Phase 9).
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .renderer import render_reminder


def send_reminder(job):
    """Renders and sends `job`. Returns False without sending if the
    user has no email address on file (nothing to deliver to);
    otherwise sends a multipart email (HTML + plain-text fallback,
    Phase 8) and returns True."""
    if not job.user.email:
        return False

    subject, html_body, text_body = render_reminder(job)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@admission-helper.local"

    message = EmailMultiAlternatives(
        subject=subject, body=text_body, from_email=from_email, to=[job.user.email]
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
    return True
