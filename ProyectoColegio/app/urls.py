from django.urls import path
from app.views.Curso.views import *
from app.views.Usuario.views import *
from app.views.Inventario.views import *
from app.views.Marca.views import *
from app.views.TipoElemento.views import *
from app.views.UnidadMedida.views import *
from app.views.Categoria.views import *
from app.views.Asistencia.views import *
from app.views.Movimiento.views import *
from app.views.Evento.views import *
from app.views.Notificacion.views import *
from app.views.Index.views import DashboardView , NotificacionesView,MarcarComoleidasNotificaciones
from app.views.IA.views import preguntar_ia_local
from app.views.EstudianteAcudiente.views import (
    EstudianteAcudienteListView,
    EstudianteAcudienteCreateView,
    EstudianteAcudienteDeleteView,
)

from app.views.reportes import *
from app.views.backup import *
app_name = 'app'
urlpatterns = [

    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('preguntas1/',preguntar_ia_local,name="preguntar2" ),
    path('mis_notificaciones/',NotificacionesView.as_view(),name="mis_notificaciones"),
    path("mis_notificaciones/<int:pk>/leer/", MarcarComoleidasNotificaciones.as_view(), name="notificacion_leida"),
    # path('Curso/',listar_curso,name="listar_curso" ),
    path('curso/', CursoListView.as_view(), name="index_curso"),
    path('curso/crear/', CursoCreateView.as_view(), name="crear_curso"),
    path('curso/editar/<int:pk>/', CursoupdateView.as_view(), name="editar_curso"),
    path('curso/eliminar/<int:pk>/',
         CursoDeleteView.as_view(), name="eliminar_curso"),
    path('curso/limpiar/', CursoCleandView.as_view(), name="limpiar_curso"),
    # REPORTES DE CURSOS (Agrega esto al final de urlpatterns)
    path('reporte/curso/pdf/', ExportarCursoPDF.as_view(), name="exportar_cursos"),
    path('reporte/curso/excel/', ExportarCursoExcel.as_view(),
         name="exportar_cursos_excel"),

    # Usuario
    path('usuario/', UsuarioListView.as_view(), name="index_usuario"),
    path('usuario/crear/', UsuarioCreateView.as_view(), name="crear_usuario"),
    path('usuario/editar/<int:pk>/',
         UsuarioUpdateView.as_view(), name="editar_usuario"),
    path('usuario/eliminar/<int:pk>/',
         UsuarioDeleteView.as_view(), name="eliminar_usuario"),
    path('usuario/detalle/<int:pk>/',
         UsuarioDetailView.as_view(), name="detalle_usuario"),
    path('usuario/limpiar/', UsuarioCleandView.as_view(), name="limpiar_usuario"),
    path('usuario/perfil/',PerfilView.as_view(),name="perfil"),
    path('usuario/<int:user_id>/permisos/', GestionPermisosUsuarioView.as_view(), name='gestionar_permisos'),
    path('usuario/descargar-qr/<int:estudiante_id>/', DescargarQRView.as_view(), name='descargar_qr'),
    path('reporte/usuario/pdf/', ExportarUsuarioPDF.as_view(), name="reporte_usuario_pdf"),
    path('reporte/usuario/excel/', ExportarUsuarioExcel.as_view(),
         name="reporte_usuario_excel"),
    # INVENTARIO
    path('inventario/', InventarioListView.as_view(), name="index_inventario"),
    path('inventario/crear/', ElementoCreateView.as_view(), name="crear_elemento"),
    path('inventario/editar/<int:pk>/',
         ElementoUpdateView.as_view(), name="editar_elemento"),
    path('inventario/eliminar/<int:pk>/',
         ElementoDeleteView.as_view(), name="eliminar_elemento"),
    path('inventario/limpiar/', InventarioCleanView.as_view(),
         name="limpiar_inventario"),
    # MARCA
    path('marca/', marcaListView.as_view(), name='index_marca'),
    path('marca/crear/', marcaCreateView.as_view(), name='crear_marca'),
    path('marca/editar/<int:pk>/', marcaUpdateView.as_view(), name='editar_marca'),
    path('marca/eliminar/<int:pk>/',
         marcaDeleteView.as_view(), name='eliminar_marca'),

    # TIPO DE ELEMENTO
    path('tipo/', TipoElementoListView.as_view(), name='index_tipo'),
    path('tipo/crear/', TipoElementoCreateView.as_view(), name='crear_tipo'),
    path('tipo/editar/<int:pk>/',
         TipoElementoUpdateView.as_view(), name="actualizar_tipo"),
    path('tipo/eliminar/<int:pk>/',
         TipoElementoDeleteView.as_view(), name="eliminar_tipo"),


    # UNIDAD DE MEDIDA
    path('unidad/', UnidadMedidaListView.as_view(), name='index_unidad'),
    path('unidad/crear/', UnidadMedidaCreateView.as_view(), name='crear_unidad'),
    path('unidad/editar/<int:pk>/',
         UnidadMedidaUpdateView.as_view(), name='editar_unidad'),
    path('unidad/eliminar/<int:pk>/',
         UnidadMedidaDeleteView.as_view(), name='eliminar_unidad'),
    # CATEGORIA
    path('categoria/', CategoriaListView.as_view(), name='index_categoria'),
    path('categoria/crear/', CategoriaCreateView.as_view(), name='crear_categoria'),
    path('categoria/editar/<int:pk>/',
         CategoriaUpdateView.as_view(), name='editar_categoria'),
    path('categoria/eliminar/<int:pk>/',
         CategoriaDeleteView.as_view(), name='eliminar_categoria'),

    # ASISTENCIA
    path("asistencia/", AsistenciaListView.as_view(), name="index_asistencia"),
    path('asistencia/crear/', AsistenciaCreateView.as_view(),
         name="crear_asistencia"),
    path("asistencia/editar/<int:pk>/",
         AsistenciaupdateView.as_view(), name="editar_asistencia"),
    path('asistencia/eliminar/<int:pk>/',
         AsistenciaDeleteView.as_view(), name="eliminar_asistencia"),
    path('asistencia/camara/',camara,name="Camara"),
    path('registrar_asistencia/',AsistenciaQR.as_view(),name="Asistencia_qr"),
    path('asistencia/limpiar/', AsistenciaCleandView.as_view(),
         name="limpiar_asistencia"),
    path('reporte/asistencia/pdf', ExportarAsistenciaPDF.as_view(),
         name="reporte_asistencia_pdf"),
    path('reporte/asistencia/excel', ExportarAsistenciaExcel.as_view(),
         name="reporte_asistencia_excel"),


    path('movimiento/', MovimientoListView.as_view(), name="index_movimiento"),
    path('movimiento/crear/', MovimientoCreateView.as_view(),
         name="crear_movimiento"),
    path('movimiento/editar/<int:pk>/',
         MovimientoupdateView.as_view(), name="editar_movimiento"),
    path('movimiento/eliminar/<int:pk>/',
         MovimientoDeleteView.as_view(), name="eliminar_movimiento"),
    path('movimiento/limpiar/', MovimientoCleandView.as_view(),
         name="limpiar_movimiento"),
    # EVENTO
    path('evento/', EventoListView.as_view(), name="index_evento"),
    path('evento/crear/', EventoCreateView.as_view(), name="crear_evento"),
    path('evento/editar/<int:pk>/',
         EventoupdateView.as_view(), name="editar_evento"),
    path('evento/eliminar/<int:pk>/',
         EventoDeleteView.as_view(), name="eliminar_evento"),
    path('evento/limpiar/', EventoCleandView.as_view(), name="limpiar_evento"),
    path('reporte/evento/pdf', ExportarEventosPDF.as_view(),
         name="reporte_evento_pdf"),
    path('reporte/evento/excel', ExportarEventosExcel.as_view(),
         name="reporte_evento_excel"),
    path('evento/calendario',listar_eventos,name="evento_calendario"),
    path('notificacion/', NotificacionListView.as_view(),
         name="index_notificacion"),
    path('notificacion/crear/', NotificacionCreateView.as_view(),
         name="crear_notificacion"),
    path('notificacion/editar/<int:pk>/',
         NotificacionupdateView.as_view(), name="editar_notificacion"),
    path('notificacion/eliminar/<int:pk>/',
         NotificacionDeleteView.as_view(), name="eliminar_notificacion"),
    path('notificacion/limpiar/', NotificacionCleandView.as_view(),
         name="limpiar_notificacion"),
    path('reporte/movimiento/pdf', ExportarMovimientosPDF.as_view(),
         name="reporte_movimiento_pdf"),
    path('reporte/movimiento/excel', ExportarMovimientosExcel.as_view(),
         name="reporte_movimiento_excel"),
    path('reporte/inventario/pdf', ExportarInventarioPDF.as_view(),
         name="reporte_inventario_pdf"),
    path('reporte/inventario/excel', ExportarInventarioExcel.as_view(),
         name="reporte_inventario_excel"),
    path('backup/', backup, name="backup"),
    path('backup/restaurar', restaurar_datos, name="restaurar_datos"),
    path('relacion/', EstudianteAcudienteListView.as_view(), name="index_relacion"),
    path('relacion/crear/', EstudianteAcudienteCreateView.as_view(), name="crear_relacion"),
    path('relacion/eliminar/<int:pk>/', EstudianteAcudienteDeleteView.as_view(), name="eliminar_relacion"),
]
