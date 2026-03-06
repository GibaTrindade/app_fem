from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "core/profile.html"


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "core/change_password.html"
    success_url = reverse_lazy("core:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Senha alterada com sucesso.")
        return response

# Create your views here.
