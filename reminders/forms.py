from django import forms

from core.templatetags.ui_tags import FIELD_CLASSES

from .models import NotificationPreference
from .services.timezones import get_timezone_choices

# Matches the focus-ring-only styling _topic_row.html's progress
# checkboxes already use, rather than inventing a second checkbox
# style for this one form.
CHECKBOX_CLASSES = "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"


class NotificationPreferenceForm(forms.ModelForm):
    # Milestone 15.1, Phase 1: a constrained dropdown, not free text -
    # `choices` is still every valid IANA identifier (via
    # `get_timezone_choices()`), so validation/storage stay exactly
    # what they were (a real IANA name in `NotificationPreference.
    # timezone`); only the *input* method changed from typing to
    # picking from a list a browser's native <select> lets you jump
    # through by typing ("searchable" without introducing custom JS).
    timezone = forms.ChoiceField(choices=get_timezone_choices, label="Timezone")

    class Meta:
        model = NotificationPreference
        fields = [
            "daily_agenda_enabled",
            "daily_agenda_time",
            "weekly_overview_enabled",
            "revision_reminder_enabled",
            "weekly_exam_reminder_enabled",
            "monthly_exam_reminder_enabled",
            "weekly_progress_enabled",
            "timezone",
        ]
        labels = {
            "daily_agenda_enabled": "Daily Study Agenda",
            "daily_agenda_time": "Preferred delivery time",
            "weekly_overview_enabled": "Weekly Overview",
            "revision_reminder_enabled": "Revision Reminders",
            "weekly_exam_reminder_enabled": "Weekly Exam Reminders",
            "monthly_exam_reminder_enabled": "Monthly Exam Reminders",
            "weekly_progress_enabled": "Weekly Progress Summary",
        }
        widgets = {
            "daily_agenda_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "weekly_overview_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "revision_reminder_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "weekly_exam_reminder_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "monthly_exam_reminder_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "weekly_progress_enabled": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
            "daily_agenda_time": forms.TimeInput(attrs={"type": "time", "class": FIELD_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["timezone"].widget.attrs["class"] = FIELD_CLASSES
