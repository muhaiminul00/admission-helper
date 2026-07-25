from django.urls import path

from .views import (
    ExamTimelineView,
    ExamTimelineWindowView,
    RoutineArchiveFileView,
    RoutineResourcesView,
    RoutineTimelineView,
    RoutineTimelineWindowView,
    RoutineWeekView,
)

urlpatterns = [
    path("", RoutineTimelineView.as_view(), name="routine-list"),
    path("window/", RoutineTimelineWindowView.as_view(), name="routine-timeline-window"),
    path("week/<int:week_number>/", RoutineWeekView.as_view(), name="routine-week"),
    path("resources/", RoutineResourcesView.as_view(), name="routine-resources"),
    path("resources/file/<str:filename>/", RoutineArchiveFileView.as_view(), name="routine-archive-file"),
    path("exams/", ExamTimelineView.as_view(), name="exam-timeline"),
    path("exams/window/", ExamTimelineWindowView.as_view(), name="exam-timeline-window"),
]
