from django.urls import path

from .views import NotificationPreferencesView, ReminderAdminView

urlpatterns = [
    path("preferences/", NotificationPreferencesView.as_view(), name="notification-preferences"),
    path("admin/", ReminderAdminView.as_view(), name="reminder-admin"),
]
