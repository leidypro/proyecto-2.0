from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app.models import UnidadMedida
from app.forms import UnidadMedidaForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class UnidadMedidaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = UnidadMedida
    template_name = 'UnidadMedida/index.html'
    context_object_name = 'unidades'
    permission_required = 'app.view_unidadmedida'

    def get_queryset(self):
        queryset = UnidadMedida.objects.all().order_by("nombre")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(nombre__icontains=buscar)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Unidades de Medida'
        context['subtitulo'] = 'Gestión de unidades para inventario'
        context['crear_url'] = reverse_lazy('app:crear_unidad')
        context['icon_primary'] = "fa-arrow-up"
        context['icon_secodary'] = "fa-arrow-down"
        return context


class UnidadMedidaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'modals/modals_base.html'
    success_url = reverse_lazy('app:index_unidad')
    permission_required = 'app.add_unidadmedida'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_url'] = reverse_lazy('app:index_unidad')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        self.object = form.save()
        mensaje_texto = 'Se creó una nueva unidad de medida'

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


class UnidadMedidaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'UnidadMedida/crear.html'
    success_url = reverse_lazy('app:index_unidad')
    permission_required = 'app.change_unidadmedida'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_url'] = reverse_lazy('app:index_unidad')
        context['btn_name'] = "Actualizar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida actualizada correctamente")
        return super().form_valid(form)


class UnidadMedidaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = UnidadMedida
    template_name = 'UnidadMedida/eliminar.html'
    success_url = reverse_lazy('app:index_unidad')
    permission_required = 'app.delete_unidadmedida'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Unidad de Medida'
        context['subtitulo'] = '¿Está seguro de eliminar esta unidad de medida?'
        context['redirect'] = reverse_lazy('app:index_unidad')
        return context

    def form_valid(self, form):
        messages.success(self.request, "Unidad de medida eliminada correctamente")
        return super().form_valid(form)