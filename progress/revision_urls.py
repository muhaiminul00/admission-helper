from django.urls import path

from .views import RevisionCompleteView, RevisionDetailView, RevisionQueueView

urlpatterns = [
    path("", RevisionQueueView.as_view(), name="revision-queue"),
    path("<int:pk>/", RevisionDetailView.as_view(), name="revision-detail"),
    path("<int:pk>/complete/", RevisionCompleteView.as_view(), name="revision-complete"),
]
