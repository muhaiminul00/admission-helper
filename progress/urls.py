from django.urls import path

from .views import ProgressOverviewView, ProgressToggleView

urlpatterns = [
    path("", ProgressOverviewView.as_view(), name="progress-overview"),
    path(
        "topic/<int:topic_id>/toggle/<str:field>/",
        ProgressToggleView.as_view(),
        name="progress-toggle",
    ),
]
