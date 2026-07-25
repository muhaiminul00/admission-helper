from django.urls import path

from .views import ChapterDetailView, SubjectDetailView

# Milestone 12: canonical Subject/Chapter detail pages. Mounted at the
# root (no path prefix on this include - see admission_helper/urls.py)
# so the URLs are exactly /subjects/<id>/ and /chapters/<id>/, per the
# milestone's "Single Canonical Entity" spec.
urlpatterns = [
    path("subjects/<int:pk>/", SubjectDetailView.as_view(), name="subject-detail"),
    path("chapters/<int:pk>/", ChapterDetailView.as_view(), name="chapter-detail"),
]
