from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView , View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from app.models import *
from app.forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import Http404
# Create your views here.
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q

def index(request):
    return render(request, 'index.html')

# Ejemplo Listar_Usuarios


def listar_usuario(request):
    usuario = Usuario.objects.all()
    return render(request, 'usuario/index.html', {'usuarios': usuario})


def listar_curso(request):
    curso = Curso.objects.all()
    return render(request, 'curso/index.html', {'cursos': curso})


from django.views.generic import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy

class CursoListView(PermissionRequiredMixin, ListView):
    model = Curso
    template_name = 'curso/index.html'
    context_object_name = 'cursos'
    permission_required = 'app.view_curso'
    raise_exception = True

    def handle_no_permission(self):
        raise Http404("No tienes permisos para ver esta página")

    def get_queryset(self):
        user = self.request.user

        try:
            rol = user.get_rol()
        except Exception:
            rol = None

        if rol == "Administrador":
            queryset = Curso.objects.select_related("docenteid__usuario").all()
        else:
            queryset = Curso.objects.filter(docenteid__usuario=user)

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(
                Q(grado__icontains=buscar) |
                Q(docenteid__usuario__nombre__icontains=buscar)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # -----------------------
        # Manejo de rol seguro
        # -----------------------
        try:
            rol = user.get_rol()
        except Exception:
            rol = "Sin rol"

        curso = None
        estudiantes = []

        if rol != "Administrador":
            curso = Curso.objects.filter(docenteid__usuario=user).first()

            if curso:
                estudiantes = curso.estudiante_set.all()
            else:
                estudiantes = []

            context.update({
                'curso': curso,
                'estudiantes': estudiantes,
                'titulo': 'Listado de Estudiantes',
                'subtitulo': 'Bienvenido al listado de estudiantes de tu curso',
                'text': "Estudiantes inscritos en tu curso",
                'total_text': "Total de Estudiantes",
                'total_count': len(estudiantes),
                'low_stock': estudiantes.filter(estadoMatricula="No Matriculado").count() if curso else 0,
                'icon_primary': "fa-user-graduate",
                'icon_secondary': "fa-user-times",
            })

        else:
            total_cursos = Curso.objects.count()
            total_estudiantes = Estudiante.objects.count()

            context.update({
                'titulo': 'Listado de Cursos',
                'subtitulo': 'Gestión de cursos del colegio',
                'crear_url': reverse_lazy('app:crear_curso'),
                'limpiar_url': reverse_lazy('app:limpiar_curso'),
                'text': "Total de Estudiantes",
                'total_text': "Total de Cursos",
                'total_count': total_cursos,
                'low_stock': total_estudiantes,
                'icon_primary': "fa-graduation-cap",
                'icon_secondary': "fa-users",
            })

        # -----------------------
        # Permisos dinámicos seguros
        # -----------------------
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        context.update({
            'puede_crear': user.has_perm(f'{app_label}.add_{model_name}'),
            'puede_editar': user.has_perm(f'{app_label}.change_{model_name}'),
            'puede_eliminar': user.has_perm(f'{app_label}.delete_{model_name}'),

            'rol': rol,
            'modo': 'cursos' if rol == "Administrador" else 'estudiantes'
        })

        return context

class CursoCreateView(PermissionRequiredMixin,CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'curso/crear.html'    
    success_url = reverse_lazy('app:index_curso')
    permission_required = 'app.add_curso'
    raise_exception = True
    def handle_no_permission(self):
        raise Http404("No se encontro la paginas")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Crear Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        context['btn_name'] = "Guardar"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Curso creado correctamente")
        return super().form_valid(form)


class CursoupdateView(PermissionRequiredMixin,UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'curso/crear.html'
    success_url = reverse_lazy('app:index_curso')
    permission_required = 'app.change_curso'
    raise_exception = True

    def handle_no_permission(self):
        raise Http404("No se encontro la paginas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Actualizar Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        context['btn_name'] = "Actualizar"
        return context
    
    def form_valid(self, form):
        messages.success(self.request,"Curso actualizado correctamente")
        return super().form_valid(form)


class CursoDeleteView(DeleteView):
    model = Curso
    template_name = 'curso/eliminar.html'
    success_url = reverse_lazy('app:index_curso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Eliminar Curso"
        context['listar_url'] = reverse_lazy('app:index_curso')
        return context


    def form_valid(self, form):
        messages.success(self.request, "Curso eliminado correctamente")
        return super().form_valid(form)

class CursoCleandView(View):
   def post(self, request, *args, **kwargs):
        Curso.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Curso._meta.db_table
            print(nombre_tabla)
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{nombre_tabla}';")
        
        messages.success(self.request, "Todos los cursos han sido eliminados y el ID reiniciado.")
        return redirect(reverse_lazy('app:index_curso'))