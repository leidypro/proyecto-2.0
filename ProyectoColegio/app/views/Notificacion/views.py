from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from app.models import *
from app.forms import *


def index(request):
    return render(request, 'index.html')


def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, 'usuario/index.html', {'usuarios': usuario})


def listar_notificacion(request):
    notificacion = Notificacion.objects.all()
    return render(request, 'notificacion/index.html', {'notificaciones': notificacion})


class NotificacionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Notificacion
    template_name = 'notificacion/index.html'
    context_object_name = 'notificaciones'
    permission_required = 'app.view_notificacion'

    def get_queryset(self):
        usuario = self.request.user
        rol = usuario.get_rol()

        if rol == "Administrador":
            queryset = Notificacion.objects.all()
        else:
            queryset = Notificacion.objects.filter(receptor=usuario.id)

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                titulo__icontains=buscar
            ) | queryset.filter(
                mensaje__icontains=buscar
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = self.get_queryset()

        total = qs.count()
        no_leidas = qs.filter(estado="no_leida").count()
        urgentes = qs.filter(tipo="urgente").count()

        context['titulo'] = 'Listado de Notificaciones'
        context['subtitulo'] = 'Centro de notificaciones del sistema'
        context['crear_url'] = reverse_lazy('app:crear_notificacion')
        context['limpiar_url'] = reverse_lazy('app:limpiar_notificacion')

        context['total_count'] = total
        context['total_text'] = "Total de Notificaciones"
        context['text'] = "Sin leer"
        context['low_stock'] = no_leidas

        context['icon_primary'] = "fa-bell"
        context['icon_secodary'] = "fa-envelope"

        context['urgentes'] = urgentes

        user = self.request.user
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        context['puede_crear'] = user.has_perm(f'{app_label}.add_{model_name}')
        context['puede_editar'] = user.has_perm(f'{app_label}.change_{model_name}')
        context['puede_eliminar'] = user.has_perm(f'{app_label}.delete_{model_name}')

        return context


class NotificacionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificacion/crear.html'
    success_url = reverse_lazy('app:index_notificacion')
    permission_required = 'app.add_notificacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear notificación"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Notificación creada correctamente")
        return super().form_valid(form)


class NotificacionupdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'notificacion/crear.html'
    success_url = reverse_lazy('app:index_notificacion')
    permission_required = 'app.change_notificacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Notificación"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        context['btn_name'] = "Actualizar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Notificación actualizada correctamente")
        return super().form_valid(form)


class NotificacionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Notificacion
    template_name = 'notificacion/eliminar.html'
    success_url = reverse_lazy('app:index_notificacion')
    permission_required = 'app.delete_notificacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar notificación"
        context['listar_url'] = reverse_lazy('app:index_notificacion')
        return context

    def form_valid(self, form):
        messages.success(self.request, "Notificación eliminada correctamente")
        return super().form_valid(form)


class NotificacionCleandView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'app.delete_notificacion'

    def post(self, request, *args, **kwargs):
        Notificacion.objects.all().delete()

        with connection.cursor() as cursor:
            nombre_tabla = Notificacion._meta.db_table
            cursor.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';"
            )

        messages.success(request, "Todas las notificaciones han sido eliminadas y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_notificacion'))