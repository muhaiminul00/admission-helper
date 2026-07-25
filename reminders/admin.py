from django.contrib import admin

from .models import NotificationPreference, ReminderLog


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "daily_agenda_enabled", "daily_agenda_time", "timezone")
    list_filter = ("daily_agenda_enabled", "weekly_overview_enabled", "revision_reminder_enabled")
    search_fields = ("user__username", "user__email")


@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ("user", "reminder_type", "reference_key", "sent_at")
    list_filter = ("reminder_type",)
    search_fields = ("user__username", "reference_key")
    readonly_fields = ("user", "reminder_type", "reference_key", "sent_at")
