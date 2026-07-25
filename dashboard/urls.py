from django.urls import path

from .views import DashboardView, DashboardWidgetsView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("widgets/", DashboardWidgetsView.as_view(), name="dashboard-widgets"),
]
