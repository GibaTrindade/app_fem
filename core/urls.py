from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import ProfileView, UserPasswordChangeView

app_name = "core"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("meu-perfil/", ProfileView.as_view(), name="profile"),
    path(
        "meu-perfil/alterar-senha/",
        UserPasswordChangeView.as_view(),
        name="change_password",
    ),
]
