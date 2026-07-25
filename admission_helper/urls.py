"""
URL configuration for admission_helper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from core.views import HealthCheckView, ProfileView, RegisterView
from routines.views import ExamDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    # Overrides django.contrib.auth.urls's default 'login' below, adding
    # redirect_authenticated_user (an already-logged-in visitor to
    # /accounts/login/ goes straight to the dashboard, per Milestone 7's
    # "Redirect authenticated users to the dashboard" login requirement -
    # django.contrib.auth's LoginView does not do this by default).
    path('accounts/login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('dashboard.urls')),
    path('routine/', include('routines.urls')),
    path('lecture/', include('lectures.urls')),
    path('progress/', include('progress.urls')),
    path('analytics/', include('progress.analytics_urls')),
    path('revision/', include('progress.revision_urls')),
    path('datasets/', include('routines.dataset_urls')),
    path('reminders/', include('reminders.urls')),
    path('exam/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('', include('subjects.urls')),
]
