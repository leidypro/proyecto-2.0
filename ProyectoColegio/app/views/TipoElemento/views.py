from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from app.models import tipoelemento
from app.forms import TipoElementoForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class TipoElementoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = tipoelemento
    template_name = 'TipoElemento/index.html'
    context_object_name = 'tipos'
    permission_required = 'app.view_tipoelemento'

    def get_queryset(self):
        queryset = tipoelemento.objects.all().order_by("nombre")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(nombre__icontains=buscar)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Tipos de Elemento'
        context['subtitulo'] = 'Clasificación de inventario'
        context['crear_url'] = reverse_lazy('app:crear_tipo')
        context['limpiar_url'] = reverse_lazy('app:limpiar_tipo')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class TipoElementoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = tipoelemento
    form_class = TipoElementoForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:index_tipo')
    permission_required = 'app.add_tipoelemento'

    def form_valid(self, form):
        self.object = form.save()
        mensaje_texto = 'Se creó un nuevo tipo de elemento'

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'nombre': str(self.object),
                'message': mensaje_texto
            })

        messages.success(self.request, mensaje_texto)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


class TipoElementoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = tipoelemento
    form_class = TipoElementoForm
    template_name = 'TipoElemento/crear.html'
    success_url = reverse_lazy('app:index_tipo')
    permission_required = 'app.change_tipoelemento'

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de elemento actualizado correctamente')
        return super().form_valid(form)


class TipoElementoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = tipoelemento
    template_name = 'TipoElemento/eliminar.html'
    success_url = reverse_lazy('app:index_tipo')
    permission_required = 'app.delete_tipoelemento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Tipo de Elemento'
        context['subtitulo'] = '¿Está seguro de eliminar este tipo de elemento?'
        context['listar_url'] = reverse_lazy('app:index_tipo')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de elemento eliminado exitosamente')
        return super().form_valid(form)


class TipoCleandView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'app.delete_tipoelemento'

    def post(self, request, *args, **kwargs):
        tipoelemento.objects.all().delete()

        with connection.cursor() as cursor:
            nombre_tabla = tipoelemento._meta.db_table
            cursor.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';"
            )

        messages.success(request, "Todos los tipos de elemento fueron eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_tipo'))