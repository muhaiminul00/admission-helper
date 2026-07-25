from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import RegistrationForm


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """Milestone 15.2, Part 1: `/accounts/profile/` - the destination
    the header's User Menu points "Profile" at. Deliberately minimal
    (account facts + links onward) - no new academic feature, just a
    home for account-level actions that don't belong in the main study
    workflow."""

    template_name = "accounts/profile.html"


class HealthCheckView(View):
    """Milestone 14, Phase 4: `/health/` - an unauthenticated liveness
    probe for the deployment platform (Render/Railway). Deliberately
    does nothing but confirm the process can handle a request; it
    doesn't touch the database, so it can't itself become a source of
    downtime."""

    def get(self, request):
        return JsonResponse({"status": "ok"})
