from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from app.models import *
from app.forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from app.google_api import (
    obtener_servicio,
    crear_evento,
    actualizar_evento,
    eliminar_evento,
)
from datetime import datetime
from django.http import JsonResponse
from googleapiclient.errors import HttpError


class EventoListView(
    PermissionRequiredMixin,
    ListView
):
    model = Evento
    template_name = "evento/index.html"
    context_object_name = "eventos"

    permission_required = "app.view_evento"
    raise_exception = True

    def get_queryset(self):
        queryset = Evento.objects.all().order_by("fecha_inicio")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                titulo__icontains=buscar
            ) | queryset.filter(
                descripcion__icontains=buscar
            )

        fecha = self.request.GET.get("fecha")
        if fecha:
            queryset = queryset.filter(fecha_inicio__date=fecha)

        return queryset

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from django.utils import timezone as tz

        hoy = tz.now()

        total = Evento.objects.count()
        proximos = Evento.objects.filter(
            fecha_inicio__gte=hoy
        ).count()

        pasados = Evento.objects.filter(
            fecha_fin__lt=hoy
        ).count()

        context["titulo"] = "Listado de Eventos"
        context["subtitulo"] = "Calendario de actividades del colegio"
        context["crear_url"] = reverse_lazy("app:crear_evento")
        context["limpiar_url"] = reverse_lazy("app:limpiar_evento")

        context["total_count"] = total
        context["total_text"] = "Total de Eventos"

        context["text"] = "Próximos eventos"
        context["low_stock"] = proximos

        context["icon_primary"] = "fa-calendar-alt"
        context["icon_secodary"] = "fa-calendar-check"

        context["pasados"] = pasados

        user = self.request.user

        context["puede_crear"] = user.has_perm(
            "app.add_evento"
        )

        context["puede_editar"] = user.has_perm(
            "app.change_evento"
        )

        context["puede_eliminar"] = user.has_perm(
            "app.delete_evento"
        )

        return context


class EventoCreateView(
    PermissionRequiredMixin,
    CreateView
):
    model = Evento
    form_class = EventoForm
    template_name = "evento/crear.html"

    permission_required = "app.add_evento"
    raise_exception = True

    success_url = reverse_lazy("app:index_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["titulo"] = "Crear Evento"
        context["listar_url"] = reverse_lazy(
            "app:index_evento"
        )
        context["btn_name"] = "Guardar"

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        evento = self.object

        try:
            evento_google = crear_evento(
                evento.titulo,
                evento.descripcion,
                evento.fecha_inicio,
                evento.fecha_fin,
            )

            if evento_google:
                evento.google_event_id = evento_google["id"]
                evento.save()

        except Exception as e:
            print(
                "Error en Google Calendar:",
                e
            )

        messages.success(
            self.request,
            "Evento creado correctamente"
        )

        return response


class EventoupdateView(
    PermissionRequiredMixin,
    UpdateView
):
    model = Evento
    form_class = EventoForm
    template_name = "evento/crear.html"

    permission_required = "app.change_evento"
    raise_exception = True

    success_url = reverse_lazy("app:index_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["titulo"] = "Actualizar Evento"
        context["listar_url"] = reverse_lazy(
            "app:index_evento"
        )
        context["btn_name"] = "Actualizar"

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        evento = self.object

        try:
            actualizar_evento(
                evento.google_event_id,
                evento.titulo,
                evento.descripcion,
                evento.fecha_inicio,
                evento.fecha_fin,
            )

        except Exception as e:
            print(
                "Error al actualizar en Google Calendar:",
                e
            )

        messages.success(
            self.request,
            "Evento actualizado correctamente"
        )

        return response


class EventoDeleteView(
    PermissionRequiredMixin,
    DeleteView
):
    model = Evento
    template_name = "evento/eliminar.html"

    permission_required = "app.delete_evento"
    raise_exception = True

    success_url = reverse_lazy("app:index_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["titulo"] = "Eliminar Evento"
        context["listar_url"] = reverse_lazy(
            "app:index_evento"
        )

        return context

    def form_valid(self, form):
        evento = self.get_object()

        try:
            if evento.google_event_id:
                eliminar_evento(
                    evento.google_event_id
                )

        except Exception as e:
            print(
                "Error en Google Calendar:",
                e
            )

        messages.success(
            self.request,
            "Evento eliminado correctamente"
        )

        return super().form_valid(form)


class EventoCleandView(
    PermissionRequiredMixin,
    View
):
    permission_required = "app.delete_evento"
    raise_exception = True

    def post(self, request, *args, **kwargs):

        Evento.objects.all().delete()

        with connection.cursor() as cursor:

            nombre_tabla = Evento._meta.db_table

            cursor.execute(
                f"DELETE FROM sqlite_sequence "
                f"WHERE name='{nombre_tabla}';"
            )

        messages.success(
            request,
            "Todos los eventos han sido eliminados y el ID reiniciado."
        )

        return redirect(
            reverse_lazy("app:index_evento")
        )


@permission_required(
    "app.view_evento",
    raise_exception=True
)
def listar_eventos(request):

    try:
        servicio = obtener_servicio()

        ahora = datetime.utcnow().isoformat() + "Z"

        eventos_resultado = (
            servicio.events()
            .list(
                calendarId="primary",
                timeMin=ahora,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        eventos = eventos_resultado.get("items", [])

        lista = []

        for evento in eventos:

            inicio = evento["start"].get(
                "dateTime",
                evento["start"].get("date")
            )

            fin = evento["end"].get(
                "dateTime",
                evento["end"].get("date")
            )

            lista.append({
                "titulo": evento.get("summary"),
                "descripcion": evento.get("description"),
                "inicio": inicio,
                "fin": fin,
                "origen": "google"
            })

        return JsonResponse({
            "eventos": lista
        })

    except Exception as error:

        # Fallback a la base de datos
        eventos_bd = Evento.objects.all().order_by("fecha_inicio")[:10]

        lista = []

        for evento in eventos_bd:
            lista.append({
                "titulo": evento.titulo,
                "descripcion": evento.descripcion,
                "inicio": evento.fecha_inicio.isoformat(),
                "fin": evento.fecha_fin.isoformat(),
                "origen": "base_datos"
            })

        return JsonResponse({
            "eventos": lista,
            "mensaje": "No fue posible consultar Google Calendar. Se muestran los eventos almacenados localmente.",
            "error_google": str(error)
        })