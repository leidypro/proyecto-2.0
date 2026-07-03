from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.db.models import Q, F

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from app.models import *
from app.forms import *


def listar_inventario(request):
    elementos = Elemento.objects.all()
    return render(request, 'inventario/index.html', {'elementos': elementos})


class InventarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Elemento
    template_name = 'Inventario/index.html'
    context_object_name = 'elementos'
    permission_required = 'app.view_elemento'

    def get_queryset(self):
        queryset = Elemento.objects.select_related(
            "tipoElementoId",
            "categoriaId",
            "marcaId",
            "unidadMedidaId"
        ).order_by("-id")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(ubicacion__icontains=buscar)
            )

        categoria = self.request.GET.get("categoria")
        if categoria:
            queryset = queryset.filter(categoriaId_id=categoria)

        marca = self.request.GET.get("marca")
        if marca:
            queryset = queryset.filter(marcaId_id=marca)

        stock = self.request.GET.get("stock")
        if stock == "bajo":
            queryset = queryset.filter(stockActual__lte=F("stockMinimo"))
        elif stock == "normal":
            queryset = queryset.filter(stockActual__gt=F("stockMinimo"))

        bajo_stock = self.request.GET.get("bajo_stock")
        if bajo_stock == "1":
            queryset = queryset.filter(
                stockActual__lte=F("stockMinimo")
            )

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipoElementoId_id=tipo)

        unidad = self.request.GET.get("unidad")
        if unidad:
            queryset = queryset.filter(unidadMedidaId_id=unidad)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Inventario General'
        context['subtitulo'] = 'Gestión de elementos del colegio'
        context['crear_url'] = reverse_lazy('app:crear_elemento')
        context['limpiar_url'] = reverse_lazy('app:limpiar_inventario')
        context["total_text"] = "Total de Elementos"
        context["text"] = "Stock Bajo"

        context['total_count'] = Elemento.objects.count()

        context['stock_bajo'] = Elemento.objects.filter(
            stockActual__lte=F("stockMinimo")
        ).count()

        from app.models import categoria, marca, tipoelemento, UnidadMedida
        context['categorias'] = categoria.objects.all()
        context['marcas'] = marca.objects.all()
        context['tipos'] = tipoelemento.objects.all()
        context['unidades'] = UnidadMedida.objects.all()

        user = self.request.user
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        context['puede_crear'] = user.has_perm(
            f'{app_label}.add_{model_name}'
        )

        context['puede_editar'] = user.has_perm(
            f'{app_label}.change_{model_name}'
        )

        context['puede_eliminar'] = user.has_perm(
            f'{app_label}.delete_{model_name}'
        )

        return context

class ElementoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Elemento
    form_class = ElementoForm
    template_name = 'Inventario/crear.html'
    success_url = reverse_lazy('app:index_inventario')
    permission_required = 'app.add_elemento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(*kwargs)
        context['titulosi'] = 'Registrar Elemento'
        context['listar_url'] = reverse_lazy("app:index_inventario")
        context['btn_name'] = 'Guardar'
        return context
    def form_valid(self, form):
        messages.success(self.request, "Elemento registrado correctamente")
        return super().form_valid(form)


class ElementoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Elemento
    form_class = ElementoForm
    template_name = 'Inventario/crear.html'
    success_url = reverse_lazy('app:index_inventario')
    permission_required = 'app.change_elemento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(*kwargs)
        context['titulosi'] = 'Editar Elemento'
        context['listar_url'] = reverse_lazy("app:index_inventario")
        context['btn_name'] = 'Actualizar'
        return context
    def form_valid(self, form):
        messages.success(self.request, "Elemento actualizado correctamente")
        return super().form_valid(form)


class ElementoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Elemento
    template_name = 'Inventario/eliminar.html'
    success_url = reverse_lazy('app:index_inventario')
    permission_required = 'app.delete_elemento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Elemento"
        context['listar_url'] = reverse_lazy('app:index_inventario')
        return context
    def form_valid(self, form):
        messages.success(self.request, "Elemento eliminado correctamente")
        return super().form_valid(form)


class InventarioCleanView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'app.delete_elemento'

    def post(self, request, *args, **kwargs):
        Elemento.objects.all().delete()

        with connection.cursor() as cursor:
            nombre_tabla = Elemento._meta.db_table
            cursor.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';"
            )

        messages.success(request, "Inventario eliminado y contador reiniciado.")
        return redirect(reverse_lazy('app:index_inventario'))