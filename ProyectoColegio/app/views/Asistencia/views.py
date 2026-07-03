from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import time
from app.models import *
from app.forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
import json

APP = Asistencia._meta.app_label


@permission_required(f"{APP}.view_asistencia", raise_exception=True)
def camara(request):
    return render(request, "asistencia/camara.html")


class AsistenciaQR(PermissionRequiredMixin, View):

    permission_required = f"{APP}.add_asistencia"
    raise_exception = True

    def post(self, request):

        data = json.loads(request.body)
        codigo = data.get("codigo")

        estudiante = Estudiante.objects.filter(codigo=codigo).first()

        if estudiante:

            fecha_hoy = timezone.localdate()

            asistencia_existe = Asistencia.objects.filter(
                estudianteid=estudiante, fecha=fecha_hoy
            ).exists()

            if asistencia_existe:
                return JsonResponse(
                    {"status": "error", "mensaje": "La asistencia ya fue registrada"}
                )

            hora_actual = timezone.localtime().time()

            if hora_actual > time(7, 15):
                estado = "Tarde"
            else:
                estado = "A tiempo"

            Asistencia.objects.create(
                estado=estado,
                estudianteid=estudiante,
                fecha=timezone.localdate(),
                horaentrada=hora_actual,
                observaciones="",
                horasalida=time(13, 0),
            )

            return JsonResponse({"status": "ok", "mensaje": "Registrado exitosamente"})

        return JsonResponse({"status": "error", "mensaje": "El estudiante no existe"})


def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, "usuario/index.html", {"usuarios": usuario})


def listar_asistencia(request):
    asistencia = Asistencia.objects.all()
    return render(request, "asistencia/index.html", {"asistencias": asistencia})


class AsistenciaListView(PermissionRequiredMixin, ListView):

    model = Asistencia
    template_name = "asistencia/index.html"
    context_object_name = "asistencias"

    permission_required = f"{APP}.view_asistencia"
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pass

    def get_queryset(self):
        queryset = Asistencia.objects.select_related("estudianteid").order_by("-fecha", "-horaentrada")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                estudianteid__usuario__nombre__icontains=buscar
            )

        fecha = self.request.GET.get("fecha")
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        curso = self.request.GET.get("curso")
        if curso:
            queryset = queryset.filter(
                estudianteid__cursoId_id=curso
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = timezone.localdate()

        total = Asistencia.objects.count()

        tardanzas = Asistencia.objects.filter(estado="Tarde").count()

        hoy_count = Asistencia.objects.filter(fecha=hoy).count()

        inasistencias = Asistencia.objects.filter(estado="Inasistencia").count()

        context["titulo"] = "Listado de Asistencias"
        context["subtitulo"] = "Bienvenido al listado de asistencias"
        context["crear_url"] = reverse_lazy("app:crear_asistencia")
        context["limpiar_url"] = reverse_lazy("app:limpiar_asistencia")

        context["total_count"] = total
        context["total_text"] = "Total de Asistencias"

        context["text"] = "Tardanzas registradas"
        context["low_stock"] = tardanzas

        context["icon_primary"] = "fa-clipboard-check"
        context["icon_secodary"] = "fa-clock"

        context["hoy_count"] = hoy_count
        context["inasistencias"] = inasistencias

        from app.models import Curso
        context['cursos'] = Curso.objects.all()

        user = self.request.user

        context["puede_crear"] = user.has_perm(f"{APP}.add_asistencia")

        context["puede_editar"] = user.has_perm(f"{APP}.change_asistencia")

        context["puede_eliminar"] = user.has_perm(f"{APP}.delete_asistencia")

        return context


class AsistenciaCreateView(PermissionRequiredMixin, CreateView):

    model = Asistencia
    form_class = AsistenciaForm
    template_name = "asistencia/crear.html"

    permission_required = f"{APP}.add_asistencia"
    raise_exception = True

    success_url = reverse_lazy("app:index_asistencia")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["titulo"] = "Crear Asistencia"
        context["listar_url"] = reverse_lazy("app:index_asistencia")
        context["btn_name"] = "Guardar"

        return context

    def form_valid(self, form):

        messages.success(self.request, "Asistencia creada correctamente")

        return super().form_valid(form)


class AsistenciaupdateView(PermissionRequiredMixin, UpdateView):

    model = Asistencia
    form_class = AsistenciaForm
    template_name = "asistencia/crear.html"

    permission_required = f"{APP}.change_asistencia"
    raise_exception = True

    success_url = reverse_lazy("app:index_asistencia")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["titulo"] = "Actualizar Asistencia"
        context["listar_url"] = reverse_lazy("app:index_asistencia")
        context["btn_name"] = "Actualizar"

        return context

    def form_valid(self, form):

        messages.success(self.request, "Asistencia actualizada correctamente")

        return super().form_valid(form)


class AsistenciaDeleteView(PermissionRequiredMixin, DeleteView):

    model = Asistencia
    template_name = "asistencia/eliminar.html"

    permission_required = f"{APP}.delete_asistencia"
    raise_exception = True

    success_url = reverse_lazy("app:index_asistencia")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["titulo"] = "Eliminar Asistencia"
        context["listar_url"] = reverse_lazy("app:index_asistencia")

        return context

    def form_valid(self, form):

        messages.success(self.request, "Asistencia eliminada correctamente")

        return super().form_valid(form)


class AsistenciaCleandView(PermissionRequiredMixin, View):

    permission_required = f"{APP}.delete_asistencia"
    raise_exception = True

    def post(self, request, *args, **kwargs):

        Asistencia.objects.all().delete()

        with connection.cursor() as cursor:

            nombre_tabla = Asistencia._meta.db_table

            cursor.execute(f"ALTER TABLE {nombre_tabla} AUTO_INCREMENT = 1;")

        messages.success(
            request, "Todas las asistencias han sido eliminadas y el ID reiniciado."
        )

        return redirect(reverse_lazy("app:index_asistencia"))
