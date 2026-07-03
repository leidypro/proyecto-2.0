from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.utils import timezone as tz
from django.db.models import F

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from app.models import *
from app.forms import *


def index(request):
    return render(request, 'index.html')


def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, 'usuario/index.html', {'usuarios': usuario})


def listar_movimiento(request):
    movimiento = Movimiento.objects.all()
    return render(request, 'movimiento/index.html', {'movimientos': movimiento})


class MovimientoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Movimiento
    template_name = 'movimiento/index.html'
    context_object_name = 'movimientos'
    permission_required = 'app.view_movimiento'

    def get_queryset(self):
        queryset = Movimiento.objects.select_related("elementoId").order_by("-fecha")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                elementoId__nombre__icontains=buscar
            )

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        fecha = self.request.GET.get("fecha")
        if fecha:
            queryset = queryset.filter(fecha__date=fecha)

        elemento = self.request.GET.get("elemento")
        if elemento:
            queryset = queryset.filter(elementoId_id=elemento)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total = Movimiento.objects.count()
        entradas = Movimiento.objects.filter(tipo="Entrada").count()
        salidas = Movimiento.objects.filter(tipo="Salida").count()
        hoy = Movimiento.objects.filter(fecha__date=tz.localdate()).count()

        context['titulo'] = 'Listado de Movimientos'
        context['subtitulo'] = 'Registro de entradas y salidas de inventario'
        context['crear_url'] = reverse_lazy('app:crear_movimiento')
        context['limpiar_url'] = reverse_lazy('app:limpiar_movimiento')

        context['total_count'] = total
        context['total_text'] = "Total de Movimientos"
        context['text'] = "Salidas registradas"
        context['low_stock'] = salidas

        context['icon_primary'] = "fa-exchange-alt"
        context['icon_secodary'] = "fa-arrow-down"

        context['entradas'] = entradas
        context['hoy_count'] = hoy

        from app.models import Elemento
        context['elementos'] = Elemento.objects.all()

        user = self.request.user
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        context['puede_crear'] = user.has_perm(f'{app_label}.add_{model_name}')
        context['puede_editar'] = user.has_perm(f'{app_label}.change_{model_name}')
        context['puede_eliminar'] = user.has_perm(f'{app_label}.delete_{model_name}')

        return context


class MovimientoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'movimiento/crear.html'
    success_url = reverse_lazy('app:index_movimiento')
    permission_required = 'app.add_movimiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Movimiento creado correctamente")
        return super().form_valid(form)


class MovimientoupdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'movimiento/crear.html'
    success_url = reverse_lazy('app:index_movimiento')
    permission_required = 'app.change_movimiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        context['btn_name'] = "Actualizar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Movimiento actualizado correctamente")
        return super().form_valid(form)


class MovimientoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Movimiento
    template_name = 'movimiento/eliminar.html'
    success_url = reverse_lazy('app:index_movimiento')
    permission_required = 'app.delete_movimiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Movimiento"
        context['listar_url'] = reverse_lazy('app:index_movimiento')
        return context

    def form_valid(self, form):
        messages.success(self.request, "Movimiento eliminado correctamente")
        return super().form_valid(form)


class MovimientoCleandView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'app.delete_movimiento'

    def post(self, request, *args, **kwargs):
        Movimiento.objects.all().delete()

        with connection.cursor() as cursor:
            nombre_tabla = Movimiento._meta.db_table
            cursor.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';"
            )

        messages.success(request, "Todos los movimientos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_movimiento'))