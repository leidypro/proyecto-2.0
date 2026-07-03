from django.urls import path
from login.views import *
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

app_name = "login"
urlpatterns = [
    path("login/", CreLoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(next_page="login:login"), name="logout"),
    path(
        "reset/",
        CustomPasswordResetView.as_view(
            template_name="login/reset_password.html",
            email_template_name="login/password_reset_email.html",
            success_url="/reset/enviado/",
        ),
        name="reset_password",
    ),
    path(
        "reset/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="login/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="login/password_reset_confirm.html",
            success_url="/reset/completo/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="login/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
