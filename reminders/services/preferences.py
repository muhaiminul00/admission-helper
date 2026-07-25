from ..models import NotificationPreference


def get_preferences(user):
    """The persisted `NotificationPreference` for `user`, or an unsaved
    default instance (model field defaults apply - see
    `reminders/models.py`) if they have never visited the notification
    settings page. Reminder generation only ever reads preferences
    through this function, so it never has the side effect of creating
    a database row - only the settings page's own save does that."""
    return NotificationPreference.objects.filter(user=user).first() or NotificationPreference(user=user)
