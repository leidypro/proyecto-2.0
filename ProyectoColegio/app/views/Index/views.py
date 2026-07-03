from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from app.models import Usuario,Asistencia,Elemento,Notificacion
from django.urls import reverse_lazy
from app.mixins import RolMixin
from django.db.models.functions import TruncDate
from django.db.models import Count ,Sum, F
from django.utils.timezone import now
from datetime import timedelta
from django.views import View
from django.http import JsonResponse
import json
from app.models import Curso,Estudiante,Movimiento,docente,Estudianteacudiente
from django.shortcuts import render

class DashboardView(LoginRequiredMixin,RolMixin, TemplateView):
    template_name = 'index/dashboard.html'
    login_url = reverse_lazy('login:login')
    roles_permitidos = ['Administrador', 'Docente']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        rol = user.get_rol()

        context['usuario_nombre'] = user.nombre
        context['usuario_rol'] = rol
        context['usuario_estado'] = 'Activo' if user.estado else 'Inactivo'

        hoy = now().date()
        inicio = hoy - timedelta(days=6)

        if rol == 'Docente':
            cursos = Curso.objects.filter(docenteid__usuario=user)

            estudiantes_ids = Estudiante.objects.filter(
                cursoId__in=cursos
            ).values_list('usuario_id', flat=True)

            datos = (
                Asistencia.objects
                .filter(fecha__range=[inicio, hoy], estudianteid__in=estudiantes_ids)
                .values('fecha')
                .annotate(total=Count('id'))
                .order_by('fecha')
            )

            datos_inventario = (
                Movimiento.objects
                .filter(cursoId__in=cursos)
                .values('elementoId__categoriaId__nombre')
                .annotate(total=Sum('elementoId__stockActual'))
                .order_by('elementoId__categoriaId__nombre')
            )

            # Tarjetas del docente
            context['stat_estudiantes'] = Estudiante.objects.filter(cursoId__in=cursos).count()
            context['stat_asistencias_hoy'] = Asistencia.objects.filter(
                fecha=hoy, estudianteid__in=estudiantes_ids
            ).count()
            context['stat_tardanzas_hoy'] = Asistencia.objects.filter(
                fecha=hoy, estado="Tarde", estudianteid__in=estudiantes_ids
            ).count()
            context['stat_cursos'] = cursos.count()

        else:
            datos = (
                Asistencia.objects
                .filter(fecha__range=[inicio, hoy])
                .values('fecha')
                .annotate(total=Count('id'))
                .order_by('fecha')
            )

            datos_inventario = (
                Elemento.objects
                .exclude(categoriaId__isnull=True)
                .values('categoriaId__nombre')
                .annotate(total=Sum('stockActual'))
                .order_by('categoriaId__nombre')
            )

            # Tarjetas del administrador
            context['stat_usuarios'] = Usuario.objects.count()
            context['stat_estudiantes'] = Estudiante.objects.count()
            context['stat_cursos'] = Curso.objects.count()
            context['stat_stock_bajo'] = Elemento.objects.filter(
                stockActual__lte=F('stockMinimo')
            ).count()
            context['stat_asistencias_hoy'] = Asistencia.objects.filter(fecha=hoy).count()
            context['stat_notificaciones'] = Notificacion.objects.filter(
                estado='no_leida', receptor=user
            ).count()

        # Gráficas
        labels, data = [], []
        for item in datos:
            if item['fecha']:
                labels.append(item['fecha'].strftime('%d %b'))
                data.append(item['total'])

        context['labels'] = json.dumps(labels)
        context['data'] = json.dumps(data)

        labels_elemento, datos_elemento = [], []
        for item in datos_inventario:
            nombre_categoria = (
                item.get('categoriaId__nombre') or
                item.get('elementoId__categoriaId__nombre')
            )
            labels_elemento.append(nombre_categoria)
            datos_elemento.append(item['total'])

        context['labels_elemento'] = json.dumps(labels_elemento)
        context['datos_elemento'] = json.dumps(datos_elemento)

        return context

class Qr_code(TemplateView):
    template_name = "escaner/escaner.html"
    

class NotificacionesView(View):
    template_name = "modals/modals_notificaciones.html"

    def get(self, request):
        notificaciones = Notificacion.objects.filter(
            receptor_id=request.user
        ).order_by('-fecha_envio')

        return render(request, self.template_name, {
            'notificaciones': notificaciones
        })
        
    
class MarcarComoleidasNotificaciones(View):
    def post(self,request,pk):
        try:
            notificacion = Notificacion.objects.get(
                pk = pk,
                receptor_id = request.user.id
            )
            notificacion.estado = 'leida'
            notificacion.save()
            return JsonResponse({
                "success": True,
                "message" : "Notificacion marcada como leida"
            })
        except Notificacion.DoesNotExist:
            return JsonResponse({
                "success":False,
                "message": "No se encontro el mensaje"
            },status=404)
            