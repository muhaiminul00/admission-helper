from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from .emails.renderer import render_reminder
from .forms import NotificationPreferenceForm
from .models import NotificationPreference, ReminderLog
from .services import diagnostics, engine
from .services.diagnostics import DEFAULT_TEST_SUBJECT

User = get_user_model()


class NotificationPreferencesView(LoginRequiredMixin, View):
    """Milestone 15, Phase 7: `/reminders/preferences/` - lets a user
    turn each reminder type on/off, set their Daily Agenda delivery
    time, and set their timezone. `get_or_create` here (not
    `services.preferences.get_preferences()`, which deliberately
    avoids writing) is what actually persists a row - a user only ever
    gets a `NotificationPreference` row once they've visited this page.

    Re-renders the same page with `saved=True` on a successful POST
    rather than redirecting - this project doesn't use the Django
    messages framework anywhere else (no display block exists in
    `base.html`), so a redirect-based flash message would have nowhere
    to show.
    """

    template_name = "reminders/preferences.html"

    def get(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        form = NotificationPreferenceForm(instance=preference)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        form = NotificationPreferenceForm(request.POST, instance=preference)
        saved = False
        if form.is_valid():
            form.save()
            saved = True
        return render(request, self.template_name, {"form": form, "saved": saved})


class _StaffOnlyMixin(UserPassesTestMixin):
    """Mirrors `routines.views._StaffOnlyMixin` (Milestone 12, Phase 9)
    exactly - reuses Django's existing `is_staff` flag rather than a
    new permission system, and a non-staff user gets a 403 here too,
    not just a hidden nav link."""

    def test_func(self):
        return self.request.user.is_staff


class ReminderAdminView(LoginRequiredMixin, _StaffOnlyMixin, View):
    """Milestone 15.1, Phases 3-8: `/reminders/admin/` - a staff-only
    dashboard for verifying email configuration and manually
    exercising the reminder system before relying on it in production.
    Every action here calls straight into the exact same
    `reminders.services.engine`/`emails.renderer`/`emails.delivery`
    Milestone 15 already built - nothing about generation, rendering,
    or delivery is reimplemented (Architectural Rule: "Reminder
    Administration only invokes the existing engine").

    One view, one template, dispatching POST by an `action` field and
    re-rendering the same dashboard with a `result` describing what
    just happened - the same "re-render with a flag" pattern
    `NotificationPreferencesView` above already uses, rather than a
    maze of separate endpoints for each of the seven buttons Phase 4
    asks for.
    """

    template_name = "reminders/admin/dashboard.html"

    def get(self, request):
        return render(request, self.template_name, self._context(request))

    def post(self, request):
        action = request.POST.get("action", "")
        handler = {
            "test_connection": self._handle_test_connection,
            "send_test_email": self._handle_send_test_email,
            "preview": self._handle_preview,
            "send": self._handle_send,
        }.get(action)
        result = handler(request) if handler else {"kind": "unknown", "action": action}
        return render(request, self.template_name, self._context(request, result=result))

    def _context(self, request, result=None):
        return {
            "email_config": diagnostics.get_email_config(),
            "recent_logs": ReminderLog.objects.select_related("user").order_by("-sent_at")[:25],
            "last_success": ReminderLog.objects.filter(status=ReminderLog.Status.SUCCESS).order_by("-sent_at").first(),
            "last_failure": ReminderLog.objects.filter(status=ReminderLog.Status.FAILED).order_by("-sent_at").first(),
            "reminder_types": ReminderLog.ReminderType.choices,
            "recipients": User.objects.filter(is_active=True).order_by("username"),
            "default_test_subject": DEFAULT_TEST_SUBJECT,
            "result": result,
        }

    def _handle_test_connection(self, request):
        success, message = diagnostics.test_smtp_connection()
        return {"kind": "connection", "success": success, "message": message}

    def _handle_send_test_email(self, request):
        recipient_email = request.POST.get("recipient_email") or request.user.email
        subject = request.POST.get("subject") or DEFAULT_TEST_SUBJECT
        outcome = diagnostics.send_test_email(recipient_email, subject)
        return {"kind": "test_email", "recipient_email": recipient_email, **outcome}

    def _resolve_recipient(self, request):
        user_id = request.POST.get("user_id")
        if not user_id:
            return request.user
        return User.objects.filter(pk=user_id).first() or request.user

    def _resolve_reminder_types(self, request):
        reminder_type = request.POST.get("reminder_type", "")
        if not reminder_type or reminder_type == "__all__":
            return None
        return [reminder_type]

    def _handle_preview(self, request):
        recipient = self._resolve_recipient(request)
        reminder_types = self._resolve_reminder_types(request)
        due = engine.get_due_reminders(
            reminder_types=reminder_types, now=timezone.localdate(), users=[recipient]
        )
        if not due:
            return {"kind": "preview", "found": False, "recipient": recipient}
        subject, html, text = render_reminder(due[0])
        type_labels = dict(ReminderLog.ReminderType.choices)
        return {
            "kind": "preview", "found": True, "recipient": recipient,
            "reminder_type": type_labels.get(due[0].reminder_type, due[0].reminder_type),
            "subject": subject, "html": html, "text": text,
        }

    def _handle_send(self, request):
        recipient = self._resolve_recipient(request)
        reminder_types = self._resolve_reminder_types(request)
        results = engine.run(
            reminder_types=reminder_types, users=[recipient], triggered_by=ReminderLog.TriggeredBy.MANUAL
        )
        type_labels = dict(ReminderLog.ReminderType.choices)
        entries = [
            {
                "delivered": item.delivered,
                "error": item.error,
                "type_label": type_labels.get(item.job.reminder_type, item.job.reminder_type),
            }
            for item in results
        ]
        return {"kind": "send", "recipient": recipient, "entries": entries}
