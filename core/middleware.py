from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        path = request.path
        allowed_prefixes = (
            settings.LOGIN_URL,
            "/logout/",
            "/admin/",
            "/static/",
            "/media/",
        )
        if path.startswith(allowed_prefixes):
            return self.get_response(request)

        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
