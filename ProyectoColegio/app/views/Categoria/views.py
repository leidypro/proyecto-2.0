from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from app.models import categoria
from app.forms import CategoriaForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse

APP = categoria._meta.app_label


class CategoriaListView(PermissionRequiredMixin, ListView):
    model = categoria
    template_name = 'Categoria/index.html'
    context_object_name = 'categorias'

    permission_required = f'{APP}.view_categoria'
    raise_exception = True

    def get_queryset(self):
        queryset = categoria.objects.all().order_by("nombre")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(nombre__icontains=buscar)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Listado de Categorías'
        context['subtitulo'] = 'Gestión de categorías para inventario'
        context['crear_url'] = reverse_lazy('app:crear_categoria')

        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"

        user = self.request.user

        context['puede_crear'] = user.has_perm(
            f'{APP}.add_categoria'
        )

        context['puede_editar'] = user.has_perm(
            f'{APP}.change_categoria'
        )

        context['puede_eliminar'] = user.has_perm(
            f'{APP}.delete_categoria'
        )

        return context


class CategoriaCreateView(
    PermissionRequiredMixin,
    CreateView
):
    model = categoria
    form_class = CategoriaForm
    template_name = 'modals/modals_base.html'

    permission_required = f'{APP}.add_categoria'
    raise_exception = True

    success_url = reverse_lazy('app:index_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['listar_url'] = reverse_lazy(
            'app:index_categoria'
        )
        context['btn_name'] = "Guardar"

        return context

    def form_valid(self, form):

        self.object = form.save()

        mensaje_texto = (
            'Se creó una nueva categoría'
        )

        if self.request.headers.get(
            'x-requested-with'
        ) == 'XMLHttpRequest':

            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'nombre': str(self.object),
                'message': mensaje_texto
            })

        return super().form_valid(form)

    def form_invalid(self, form):

        if self.request.headers.get(
            'x-requested-with'
        ) == 'XMLHttpRequest':

            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

        return super().form_invalid(form)


class CategoriaUpdateView(
    PermissionRequiredMixin,
    UpdateView
):
    model = categoria
    form_class = CategoriaForm
    template_name = 'Categoria/crear.html'

    permission_required = f'{APP}.change_categoria'
    raise_exception = True

    success_url = reverse_lazy('app:index_categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = "Editar Categoría"
        context['listar_url'] = reverse_lazy(
            'app:index_categoria'
        )
        context['btn_name'] = "Actualizar"

        return context

    def form_valid(self, form):

        messages.success(
            self.request,
            "Categoría actualizada correctamente"
        )

        return super().form_valid(form)


class CategoriaDeleteView(
    PermissionRequiredMixin,
    DeleteView
):
    model = categoria
    template_name = 'Categoria/eliminar.html'

    permission_required = f'{APP}.delete_categoria'
    raise_exception = True

    success_url = reverse_lazy('app:index_categoria')

    def form_valid(self, form):

        messages.success(
            self.request,
            "Categoría eliminada correctamente"
        )

        return super().form_valid(form)