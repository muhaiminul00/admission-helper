from django.urls import path

from .views import LectureDetailView

urlpatterns = [
    path("<str:lecture_code>/", LectureDetailView.as_view(), name="lecture-detail"),
]
