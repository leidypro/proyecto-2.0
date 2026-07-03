from django.views.generic import ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin

from app.models import (
    Estudiante,
    Acudiente,
    Estudianteacudiente
)

APP = Estudianteacudiente._meta.app_label


class EstudianteAcudienteListView(
    PermissionRequiredMixin,
    ListView
):
    """
    Lista todas las relaciones Estudiante-Acudiente existentes.
    """

    model = Estudianteacudiente
    template_name = "estudianteacudiente/index.html"
    context_object_name = "relaciones"

    permission_required = (
        f"{APP}.view_estudianteacudiente"
    )
    raise_exception = True

    def get_queryset(self):
        return (
            Estudianteacudiente.objects
            .select_related(
                "estudianteId__usuario",
                "acudienteId__usuario",
            )
            .order_by(
                "estudianteId__usuario__nombre"
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total = self.get_queryset().count()

        user = self.request.user

        context["titulo"] = (
            "Relaciones Estudiante — Acudiente"
        )

        context["subtitulo"] = (
            "Vinculación entre estudiantes y sus acudientes"
        )

        context["crear_url"] = reverse_lazy(
            "app:crear_relacion"
        )

        context["limpiar_url"] = "#"

        context["total_count"] = total
        context["total_text"] = (
            "Total de Relaciones"
        )

        context["text"] = (
            "Estudiantes vinculados"
        )

        context["icon_primary"] = "fa-link"
        context["icon_secodary"] = "fa-user-group"

        context["puede_crear"] = user.has_perm(
            f"{APP}.add_estudianteacudiente"
        )

        context["puede_editar"] = user.has_perm(
            f"{APP}.change_estudianteacudiente"
        )

        context["puede_eliminar"] = user.has_perm(
            f"{APP}.delete_estudianteacudiente"
        )

        return context


class EstudianteAcudienteCreateView(
    PermissionRequiredMixin,
    View
):
    """
    Crea un vínculo entre un estudiante y un acudiente existentes.
    Evita duplicados.
    """

    permission_required = (
        f"{APP}.add_estudianteacudiente"
    )
    raise_exception = True

    template_name = (
        "estudianteacudiente/crear.html"
    )

    def _get_context(self, **kwargs):

        context = {
            "titulo": (
                "Vincular Estudiante con Acudiente"
            ),
            "listar_url": reverse_lazy(
                "app:index_relacion"
            ),
            "btn_name": "Guardar",
            "estudiantes": (
                Estudiante.objects
                .select_related("usuario")
                .order_by("usuario__nombre")
            ),
            "acudientes": (
                Acudiente.objects
                .select_related("usuario")
                .order_by("usuario__nombre")
            ),
        }

        context.update(kwargs)

        return context

    def get(self, request):

        return render(
            request,
            self.template_name,
            self._get_context()
        )

    @transaction.atomic
    def post(self, request):

        estudiante_id = request.POST.get(
            "estudiante_id"
        )

        acudiente_id = request.POST.get(
            "acudiente_id"
        )

        if not estudiante_id or not acudiente_id:

            messages.error(
                request,
                "Debe seleccionar un estudiante y un acudiente."
            )

            return render(
                request,
                self.template_name,
                self._get_context()
            )

        estudiante = get_object_or_404(
            Estudiante,
            pk=estudiante_id
        )

        acudiente = get_object_or_404(
            Acudiente,
            pk=acudiente_id
        )

        ya_existe = (
            Estudianteacudiente.objects.filter(
                estudianteId=estudiante,
                acudienteId=acudiente
            ).exists()
        )

        if ya_existe:

            messages.warning(
                request,
                f"El acudiente "
                f"'{acudiente.usuario.nombre}' "
                f"ya está vinculado al estudiante "
                f"'{estudiante.usuario.nombre}'."
            )

            return render(
                request,
                self.template_name,
                self._get_context()
            )

        Estudianteacudiente.objects.create(
            estudianteId=estudiante,
            acudienteId=acudiente
        )

        messages.success(
            request,
            f"Acudiente "
            f"'{acudiente.usuario.nombre}' "
            f"vinculado correctamente al estudiante "
            f"'{estudiante.usuario.nombre}'."
        )

        return redirect(
            reverse_lazy(
                "app:index_relacion"
            )
        )


class EstudianteAcudienteDeleteView(
    PermissionRequiredMixin,
    View
):
    """
    Elimina el vínculo entre un estudiante y un acudiente.
    No elimina los usuarios, solo la relación.
    """

    permission_required = (
        f"{APP}.delete_estudianteacudiente"
    )
    raise_exception = True

    template_name = (
        "estudianteacudiente/eliminar.html"
    )

    def get(self, request, pk):

        relacion = get_object_or_404(
            Estudianteacudiente.objects.select_related(
                "estudianteId__usuario",
                "acudienteId__usuario"
            ),
            pk=pk,
        )

        return render(
            request,
            self.template_name,
            {
                "object": relacion,
                "titulo": (
                    "Eliminar Relación Estudiante — Acudiente"
                ),
                "listar_url": reverse_lazy(
                    "app:index_relacion"
                ),
            }
        )

    def post(self, request, pk):

        relacion = get_object_or_404(
            Estudianteacudiente,
            pk=pk
        )

        nombre_est = (
            relacion.estudianteId.usuario.nombre
        )

        nombre_acu = (
            relacion.acudienteId.usuario.nombre
        )

        relacion.delete()

        messages.success(
            request,
            f"Relación entre "
            f"'{nombre_est}' y "
            f"'{nombre_acu}' "
            f"eliminada correctamente."
        )

        return redirect(
            reverse_lazy(
                "app:index_relacion"
            )
        )