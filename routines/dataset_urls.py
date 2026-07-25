from django.urls import path

from .views import DatasetCompareView, DatasetHistoryView

urlpatterns = [
    path("", DatasetHistoryView.as_view(), name="dataset-history"),
    path("compare/", DatasetCompareView.as_view(), name="dataset-compare"),
]
