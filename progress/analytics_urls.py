from django.urls import path

from .views import (
    AnalyticsChaptersView,
    AnalyticsExamsView,
    AnalyticsInsightsView,
    AnalyticsLecturesView,
    AnalyticsSubjectsView,
)

urlpatterns = [
    path("insights/", AnalyticsInsightsView.as_view(), name="analytics-insights"),
    path("subjects/", AnalyticsSubjectsView.as_view(), name="analytics-subjects"),
    path("chapters/", AnalyticsChaptersView.as_view(), name="analytics-chapters"),
    path("lectures/", AnalyticsLecturesView.as_view(), name="analytics-lectures"),
    path("exams/", AnalyticsExamsView.as_view(), name="analytics-exams"),
]
