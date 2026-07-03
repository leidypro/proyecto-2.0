from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    ordering = ("email",)

    list_display = (
        "email",
        "nombre",
        "estado",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "nombre",
    )

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "password",
            )
        }),
        ("Información personal", {
            "fields": (
                "nombre",
                "img_usuario",
            )
        }),
        ("Permisos", {
            "fields": (
                "estado",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Fechas importantes", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "nombre",
                "password1",
                "password2",
                "is_staff",
                "is_superuser",
            ),
        }),
    )