from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import logout


class LoginRequiredMiddleware:

    EXEMPT_URL_NAMES = [
        "login:login",
        "login:logout",
        "login:reset_password",
        "login:password_reset_done",
        "login:password_reset_complete",
    ]

    # URLs que no requieren autenticación
    EXEMPT_URL_PREFIXES = [
        "/reset/",  # password_reset_confirm
        "/static/css/",
        "/media/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

        self.exempt_urls = []

        for name in self.EXEMPT_URL_NAMES:
            try:
                self.exempt_urls.append(str(reverse_lazy(name)))
            except Exception:
                pass

    def __call__(self, request):

        path = request.path_info

        # Permitir URLs exactas
        if path in self.exempt_urls:
            return self.get_response(request)

        # Permitir URLs dinámicas
        if any(path.startswith(prefix) for prefix in self.EXEMPT_URL_PREFIXES):
            return self.get_response(request)

        # Si no está autenticado, redirigir al login
        if not request.user.is_authenticated:
            return self.redirect_to_login(path)

        # Refrescar datos del usuario desde la BD
        try:
            request.user.refresh_from_db()
        except Exception:
            logout(request)
            return self.redirect_to_login(path)

        # Validar estado del usuario
        if hasattr(request.user, "estado"):
            if not request.user.estado:
                logout(request)
                return self.redirect_to_login(path)

        return self.get_response(request)

    def redirect_to_login(self, path):
        login_url = str(reverse_lazy(settings.LOGIN_URL))
        return redirect(f"{login_url}?next={path}")