"""Email configuration diagnostics for Reminder Administration
(Milestone 15.1, Phase 3.5). Read-only metadata inspection plus two
actions - testing an SMTP connection without sending anything, and
sending one standalone test email - both deliberately outside the
reminder engine (Phase 3.5: "This email should bypass the reminder
engine"). Never returns a secret: `EMAIL_HOST_PASSWORD`/anything
credential-shaped is read only to decide whether it's *present*, never
included in a returned value.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone

from ..emails.renderer import to_plain_text

SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

BACKEND_LABELS = {
    SMTP_BACKEND: "SMTP Backend",
    "django.core.mail.backends.console.EmailBackend": "Console Backend",
    "django.core.mail.backends.filebased.EmailBackend": "File Backend",
    "django.core.mail.backends.dummy.EmailBackend": "Dummy Backend",
    "django.core.mail.backends.locmem.EmailBackend": "In-Memory Backend (testing)",
}


def get_email_config():
    """Safe-to-display configuration + a friendly issues list (Phase
    3.5's "Configuration Validation") - never the password itself,
    only whether one is set."""
    backend = settings.EMAIL_BACKEND
    is_smtp = backend == SMTP_BACKEND
    host = getattr(settings, "EMAIL_HOST", "") or ""
    port = getattr(settings, "EMAIL_PORT", None)
    host_user = getattr(settings, "EMAIL_HOST_USER", "") or ""
    host_password_set = bool(getattr(settings, "EMAIL_HOST_PASSWORD", ""))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or ""
    use_tls = getattr(settings, "EMAIL_USE_TLS", False)
    use_ssl = getattr(settings, "EMAIL_USE_SSL", False)

    issues = []
    if is_smtp:
        if not host:
            issues.append("EMAIL_HOST is not set.")
        if not port:
            issues.append("EMAIL_PORT is not set.")
        if not host_user:
            issues.append("EMAIL_HOST_USER is not set - SMTP authentication will fail.")
        if not host_password_set:
            issues.append("EMAIL_HOST_PASSWORD is not set - SMTP authentication will fail.")
    else:
        issues.append(
            f"{BACKEND_LABELS.get(backend, backend)} is active - reminders are not actually "
            "delivered to recipients until EMAIL_BACKEND is switched to SMTP."
        )
    if not from_email:
        issues.append("DEFAULT_FROM_EMAIL is not set.")

    if is_smtp and not issues:
        status = "ready"
    elif is_smtp:
        status = "incomplete"
    else:
        status = "disabled"

    encryption = "TLS" if use_tls else "SSL" if use_ssl else "None"

    return {
        "backend": backend,
        "backend_label": BACKEND_LABELS.get(backend, backend),
        "status": status,
        "from_email": from_email or "Not configured",
        "host": host or None,
        "port": port,
        "encryption": encryption,
        "host_user": host_user or "Not configured",
        "timezone": settings.TIME_ZONE,
        "issues": issues,
    }


def test_smtp_connection():
    """(success, message) - opens and immediately closes a connection,
    never sending anything. Only meaningful for the SMTP backend;
    every other backend reports honestly that there's nothing to
    connect to rather than a misleading "success"."""
    if settings.EMAIL_BACKEND != SMTP_BACKEND:
        return False, f"Current backend is {BACKEND_LABELS.get(settings.EMAIL_BACKEND, settings.EMAIL_BACKEND)} - no SMTP connection to test."

    connection = get_connection()
    try:
        connection.open()
    except Exception as exc:  # noqa: BLE001 - surface the exact SMTP error to the administrator
        return False, str(exc)
    finally:
        connection.close()
    return True, "Connection successful."


DEFAULT_TEST_SUBJECT = "Admission Helper Test Email"


def send_test_email(to_email, subject=DEFAULT_TEST_SUBJECT):
    """Sends one standalone email using the shared HTML layout, via
    the exact same renderer/delivery primitives the reminder engine
    uses (Phase 3.5/6: "Reuse the production renderer", "No duplicated
    template code") - but never through `engine.py` or `ReminderLog`,
    since this exists purely to verify delivery, not to represent a
    real reminder occurrence. Returns a dict the admin view renders
    directly: success, sent_at, error, and the exact html/text bodies
    sent (Phase 3.5's "Email Preview")."""
    sent_at = timezone.now()
    html_body = render_to_string("emails/test_email.html", {"subject": subject, "sent_at": sent_at})
    text_body = to_plain_text(html_body)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "no-reply@admission-helper.local"

    message = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=[to_email])
    message.attach_alternative(html_body, "text/html")
    try:
        message.send()
    except Exception as exc:  # noqa: BLE001 - surface the exact delivery error to the administrator
        return {"success": False, "sent_at": None, "error": str(exc), "html": html_body, "text": text_body}
    return {"success": True, "sent_at": sent_at, "error": "", "html": html_body, "text": text_body}
