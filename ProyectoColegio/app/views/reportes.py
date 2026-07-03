from django.shortcuts import render, redirect
from django.views.generic import View
from django.views import View as DjangoView
from django.http import HttpResponse
from app.models import *
from django.db.models import Q, F
from app.utils import exportar_pdf, exportar_excel
from datetime import datetime
from django.contrib import messages
# ====== VISTAS PARA EXPORTAR REPORTES ======


class ExportarUsuarioPDF(DjangoView):

    def get(self, request):
        print("Aqui")

        usuarios = Usuario.objects.all()
        if not usuarios.exists():
            messages.warning(
                request, "No existen usuarios registrados en el sistema.")
            return redirect('app:index_usuario')
        buscar = request.GET.get('buscar', '').strip()
        rol = request.GET.get('rol', '').strip()

        estado = request.GET.get('estado', '').strip()

        curso = request.GET.get('curso', '').strip()

        # ===== BUSQUEDA =====
        if buscar:
            usuarios = usuarios.filter(
                Q(nombre__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        # ===== ESTADO =====
        if estado in ['0', '1']:
            usuarios = usuarios.filter(estado=(estado == '1'))

        # ===== ROL =====
        if rol == "administrador":
            usuarios = usuarios.filter(administrador__isnull=False)

        elif rol == "docente":
            usuarios = usuarios.filter(docente__isnull=False)

        elif rol == "estudiante":
            usuarios = usuarios.filter(estudiante__isnull=False)

        # ===== CURSO =====
        if curso:
            usuarios = usuarios.filter(estudiante__cursoId_id=curso)

        # ===== VALIDAR RESULTADOS =====
        if not usuarios.exists():
            messages.warning(request, "No existen usuarios con ese filtro")
            return redirect('app:index_usuario')

        columnas = ['ID', 'Nombre', 'Email', 'Rol', 'Estado']

        datos = [
            (
                us.id,
                us.nombre,
                us.email,
                us.get_rol(),
                "Activo" if us.estado else "Inactivo"
            )
            for us in usuarios
        ]

        nombre_archivo = f'Reporte_Usuarios_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_pdf(
            request,
            titulo='REPORTE DE USUARIOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarUsuarioExcel(DjangoView):
    """
    VISTA PARA EXPORTAR CATEGORIAS A EXCEL
    Obtiene todas las categorias y las exporta en formato Excel
    """

    def get(self, request):
        print("Aqui")

        usuarios = Usuario.objects.all()
        if not usuarios.exists():
            messages.warning(
                request, "No existen usuarios registrados en el sistema.")
            return redirect('app:index_usuario')
        buscar = request.GET.get('buscar', '').strip()
        rol = request.GET.get('rol', '').strip()
        estado = request.GET.get('estado', '').strip()
        curso = request.GET.get('curso', '').strip()

        # ===== BUSQUEDA =====
        if buscar:
            usuarios = usuarios.filter(
                Q(nombre__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        # ===== ESTADO =====
        if estado in ['0', '1']:
            usuarios = usuarios.filter(estado=(estado == '1'))

        # ===== ROL =====
        if rol == "administrador":
            usuarios = usuarios.filter(administrador__isnull=False)

        elif rol == "docente":
            usuarios = usuarios.filter(docente__isnull=False)

        elif rol == "estudiante":
            usuarios = usuarios.filter(estudiante__isnull=False)

        # ===== CURSO =====
        if curso:
            usuarios = usuarios.filter(estudiante__cursoId_id=curso)

        # ===== VALIDAR RESULTADOS =====
        if not usuarios.exists():
            messages.warning(request, "No existen usuarios con ese filtro")
            return redirect('app:index_usuario')

        columnas = ['ID', 'Nombre', 'Email', 'Rol', 'Estado']

        datos = [
            (
                us.id,
                us.nombre,
                us.email,
                us.get_rol(),
                "Activo" if us.estado else "Inactivo"
            )
            for us in usuarios
        ]

        nombre_archivo = f'Reporte_Usuarios_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE CATEGORIAS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarAsistenciaPDF(DjangoView):
    """
    VISTA PARA EXPORTAR ASISTENCIAS A PDF
    Obtiene las asistencias filtradas y las exporta en formato PDF
    """

    def get(self, request):
        # Obtener todas las asistencias
        asistencia = Asistencia.objects.select_related("estudianteid").all()
        if not asistencia.exists():
            messages.warning(
                request, "No existen asistencias registrados en el sistema.")
            return redirect('app:index_asistencia')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        fecha = request.GET.get('fecha', '').strip()
        estado = request.GET.get('estado', '').strip()
        curso = request.GET.get('curso', '').strip()

        if buscar:
            asistencia = asistencia.filter(
                estudianteid__usuario__nombre__icontains=buscar
            )

        if fecha:
            asistencia = asistencia.filter(fecha=fecha)

        if estado:
            asistencia = asistencia.filter(estado=estado)

        if curso:
            asistencia = asistencia.filter(estudianteid__cursoId_id=curso)

        # Validar resultados
        if not asistencia.exists():
            messages.warning(request, "No existen asistencias con ese filtro")
            return redirect('app:index_asistencia')
        
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'NOMBRE DEL ESTUDIANTE', 'FECHA', 'HORA', 'ESTADO', 'OBSERVACIONES']

        # Preparar los datos en formato de tuplas
        datos = [
            (asi.id, asi.estudianteid.usuario.nombre, asi.fecha, asi.horaentrada.strftime('%H:%M'), asi.estado, asi.observaciones)
            for asi in asistencia
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Asistencias_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE ASISTENCIAS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarAsistenciaExcel(DjangoView):
    """
    VISTA PARA EXPORTAR ASISTENCIAS A EXCEL
    Obtiene las asistencias filtradas y las exporta en formato Excel
    """

    def get(self, request):
        # Obtener todas las asistencias
        asistencia = Asistencia.objects.select_related("estudianteid").all()
        if not asistencia.exists():
            messages.warning(
                request, "No existen asistencias registrados en el sistema.")
            return redirect('app:index_asistencia')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        fecha = request.GET.get('fecha', '').strip()
        estado = request.GET.get('estado', '').strip()
        curso = request.GET.get('curso', '').strip()

        if buscar:
            asistencia = asistencia.filter(
                estudianteid__usuario__nombre__icontains=buscar
            )

        if fecha:
            asistencia = asistencia.filter(fecha=fecha)

        if estado:
            asistencia = asistencia.filter(estado=estado)

        if curso:
            asistencia = asistencia.filter(estudianteid__cursoId_id=curso)

        # Validar resultados
        if not asistencia.exists():
            messages.warning(request, "No existen asistencias con ese filtro")
            return redirect('app:index_asistencia')
        
        # Definir las columnas que se mostraran en el reporte
        columnas = ['ID', 'NOMBRE DEL ESTUDIANTE', 'FECHA', 'HORA', 'ESTADO', 'OBSERVACIONES']

        # Preparar los datos en  tuplas
        datos = [
            (asi.id, asi.estudianteid.usuario.nombre, asi.fecha, asi.horaentrada.strftime('%H:%M'), asi.estado, asi.observaciones)
            for asi in asistencia
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Asistencias_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE ASISTENCIA',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarEventosPDF(DjangoView):
    """
    VISTA PARA EXPORTAR EVENTOS A PDF
    Obtiene los eventos filtrados y los exporta en formato PDF
    """

    def get(self, request):
        # Obtener todos los eventos
        evento = Evento.objects.all()
        if not evento.exists():
            messages.warning(
                request, "No existen eventos registrados en el sistema.")
            return redirect('app:index_evento')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        fecha = request.GET.get('fecha', '').strip()

        if buscar:
            evento = evento.filter(
                Q(titulo__icontains=buscar) |
                Q(descripcion__icontains=buscar)
            )

        if fecha:
            evento = evento.filter(fecha_inicio__date=fecha)

        # Validar resultados
        if not evento.exists():
            messages.warning(request, "No existen eventos con ese filtro")
            return redirect('app:index_evento')
        
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'TITULO', 'DESCRIPCION', 'FECHA INICIO', 'FECHA FIN']

        # Preparar los datos en formato de tuplas
        datos = [
            (ev.id, ev.titulo, ev.descripcion, ev.fecha_inicio.strftime('%d/%m/%Y %H:%M'), ev.fecha_fin.strftime('%d/%m/%Y %H:%M'))
            for ev in evento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Eventos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE EVENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarEventosExcel(DjangoView):

    def get(self, request):
        # Obtener todos los eventos
        evento = Evento.objects.all()
        if not evento.exists():
            messages.warning(
                request, "No existen eventos registrados en el sistema.")
            return redirect('app:index_evento')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        fecha = request.GET.get('fecha', '').strip()

        if buscar:
            evento = evento.filter(
                Q(titulo__icontains=buscar) |
                Q(descripcion__icontains=buscar)
            )

        if fecha:
            evento = evento.filter(fecha_inicio__date=fecha)

        # Validar resultados
        if not evento.exists():
            messages.warning(request, "No existen eventos con ese filtro")
            return redirect('app:index_evento')
        
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'TITULO', 'DESCRIPCION', 'FECHA INICIO', 'FECHA FIN']

        # Preparar los datos en formato de tuplas
        datos = [
            (ev.id, ev.titulo, ev.descripcion, ev.fecha_inicio.strftime('%d/%m/%Y %H:%M'), ev.fecha_fin.strftime('%d/%m/%Y %H:%M'))
            for ev in evento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Eventos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE EVENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarMovimientosPDF(DjangoView):
    """
    VISTA PARA EXPORTAR MOVIMIENTOS A PDF
    Obtiene los movimientos filtrados y los exporta en formato PDF
    """

    def get(self, request):
        # Obtener todos los movimientos
        movimiento = Movimiento.objects.select_related("elementoId").all()
        if not movimiento.exists():
            messages.warning(
                request, "No existen movimientos registrados en el sistema.")
            return redirect('app:index_movimiento')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        fecha = request.GET.get('fecha', '').strip()
        elemento = request.GET.get('elemento', '').strip()

        if buscar:
            movimiento = movimiento.filter(
                elementoId__nombre__icontains=buscar
            )

        if tipo:
            movimiento = movimiento.filter(tipo=tipo)

        if fecha:
            movimiento = movimiento.filter(fecha__date=fecha)

        if elemento:
            movimiento = movimiento.filter(elementoId_id=elemento)

        # Validar resultados
        if not movimiento.exists():
            messages.warning(request, "No existen movimientos con ese filtro")
            return redirect('app:index_movimiento')
        
        # Definir las columnas que se muestran en el reporte
        columnas = ['ID', 'ELEMENTO', 'TIPO', 'CANTIDAD', 'FECHA', 'MOTIVO']

        # Preparar los datos en formato de tuplas
        datos = [
            (mo.id, mo.elementoId.nombre, mo.tipo, mo.cantidad, mo.fecha.strftime('%d/%m/%Y %H:%M'), mo.motivo)
            for mo in movimiento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Movimientos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a PDF
        return exportar_pdf(
            request,
            titulo='REPORTE DE MOVIMIENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarMovimientosExcel(DjangoView):
    """
    VISTA PARA EXPORTAR MOVIMIENTOS A EXCEL
    Obtiene los movimientos filtrados y los exporta en formato Excel
    """

    def get(self, request):
        # Obtener todos los movimientos
        movimiento = Movimiento.objects.select_related("elementoId").all()
        if not movimiento.exists():
            messages.warning(
                request, "No existen movimientos registrados en el sistema.")
            return redirect('app:index_movimiento')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        fecha = request.GET.get('fecha', '').strip()
        elemento = request.GET.get('elemento', '').strip()

        if buscar:
            movimiento = movimiento.filter(
                elementoId__nombre__icontains=buscar
            )

        if tipo:
            movimiento = movimiento.filter(tipo=tipo)

        if fecha:
            movimiento = movimiento.filter(fecha__date=fecha)

        if elemento:
            movimiento = movimiento.filter(elementoId_id=elemento)

        # Validar resultados
        if not movimiento.exists():
            messages.warning(request, "No existen movimientos con ese filtro")
            return redirect('app:index_movimiento')
        
        # Definir las columnas que se mostraran en el reporte
        columnas = ['ID', 'ELEMENTO', 'TIPO', 'CANTIDAD', 'FECHA', 'MOTIVO']

        # Preparar los datos en  tuplas
        datos = [
            (mo.id, mo.elementoId.nombre, mo.tipo, mo.cantidad, mo.fecha.strftime('%d/%m/%Y %H:%M'), mo.motivo)
            for mo in movimiento
        ]

        # Generar nombre del archivo con timestamp
        nombre_archivo = f'Reporte_Movimientos_{datetime.now().strftime("%d_%m_%Y")}'

        # Llamar funcion de exportacion a Excel
        return exportar_excel(
            titulo='REPORTE DE MOVIMIENTOS',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarInventarioPDF(DjangoView):
    def get(self, request):
        inventario = Elemento.objects.select_related(
            'marcaId', 'categoriaId', 'tipoElementoId', 'unidadMedidaId'
        ).all()
        if not inventario.exists():
            messages.warning(
                request, "No existen elementos registrados en el sistema.")
            return redirect('app:index_inventario')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        categoria = request.GET.get('categoria', '').strip()
        marca = request.GET.get('marca', '').strip()
        stock = request.GET.get('stock', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        unidad = request.GET.get('unidad', '').strip()

        if buscar:
            inventario = inventario.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(ubicacion__icontains=buscar)
            )

        if categoria:
            inventario = inventario.filter(categoriaId_id=categoria)

        if marca:
            inventario = inventario.filter(marcaId_id=marca)

        if stock == 'bajo':
            inventario = inventario.filter(stockActual__lte=F('stockMinimo'))
        elif stock == 'normal':
            inventario = inventario.filter(stockActual__gt=F('stockMinimo'))

        if tipo:
            inventario = inventario.filter(tipoElementoId_id=tipo)

        if unidad:
            inventario = inventario.filter(unidadMedidaId_id=unidad)

        # Validar resultados
        if not inventario.exists():
            messages.warning(request, "No existen elementos con ese filtro")
            return redirect('app:index_inventario')
        
        columnas = ['ID', 'Nombre', 'Marca', 'Categoría', 'Tipo', 'Unidad', 'Stock Actual', 'Stock Mínimo', 'Ubicación']

        datos = [
            (
                inv.id,
                inv.nombre,
                inv.marcaId.nombre if inv.marcaId else 'N/A',
                inv.categoriaId.nombre if inv.categoriaId else 'N/A',
                inv.tipoElementoId.nombre if inv.tipoElementoId else 'N/A',
                inv.unidadMedidaId.nombre if inv.unidadMedidaId else 'N/A',
                inv.stockActual,
                inv.stockMinimo,
                inv.ubicacion
            )
            for inv in inventario
        ]

        nombre_archivo = f'Reporte_Inventario_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_pdf(
            request,
            titulo='REPORTE DE INVENTARIO',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo,
        )


class ExportarInventarioExcel(DjangoView):
    def get(self, request):
        inventario = Elemento.objects.select_related(
            'marcaId', 'categoriaId', 'tipoElementoId', 'unidadMedidaId'
        ).all()
        if not inventario.exists():
            messages.warning(request, "No existen elementos registrados en el sistema.")
            return redirect('app:index_inventario')
        
        # Aplicar filtros
        buscar = request.GET.get('buscar', '').strip()
        categoria = request.GET.get('categoria', '').strip()
        marca = request.GET.get('marca', '').strip()
        stock = request.GET.get('stock', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        unidad = request.GET.get('unidad', '').strip()

        if buscar:
            inventario = inventario.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(ubicacion__icontains=buscar)
            )

        if categoria:
            inventario = inventario.filter(categoriaId_id=categoria)

        if marca:
            inventario = inventario.filter(marcaId_id=marca)

        if stock == 'bajo':
            inventario = inventario.filter(stockActual__lte=F('stockMinimo'))
        elif stock == 'normal':
            inventario = inventario.filter(stockActual__gt=F('stockMinimo'))

        if tipo:
            inventario = inventario.filter(tipoElementoId_id=tipo)

        if unidad:
            inventario = inventario.filter(unidadMedidaId_id=unidad)

        # Validar resultados
        if not inventario.exists():
            messages.warning(request, "No existen elementos con ese filtro")
            return redirect('app:index_inventario')
        
        columnas = ['ID', 'Nombre', 'Marca', 'Categoría', 'Tipo', 'Unidad', 'Stock Actual', 'Stock Mínimo', 'Ubicación']

        datos = [
            (
                inv.id,
                inv.nombre,
                inv.marcaId.nombre if inv.marcaId else 'N/A',
                inv.categoriaId.nombre if inv.categoriaId else 'N/A',
                inv.tipoElementoId.nombre if inv.tipoElementoId else 'N/A',
                inv.unidadMedidaId.nombre if inv.unidadMedidaId else 'N/A',
                inv.stockActual,
                inv.stockMinimo,
                inv.ubicacion
            )
            for inv in inventario
        ]

        nombre_archivo = f'Reporte_Inventario_{datetime.now().strftime("%d_%m_%Y")}'

        return exportar_excel(
            titulo='REPORTE DE INVENTARIO',
            columnas=columnas,
            datos=datos,
            nombre_archivo=nombre_archivo
        )


class ExportarCursoPDF(DjangoView):
    def get(self, request):

        buscar = request.GET.get("buscar", "").strip()

        cursos = Curso.objects.select_related("docenteid__usuario")

        if buscar:
            cursos = cursos.filter(
                Q(grado__icontains=buscar) |
                Q(docenteid__usuario__nombre__icontains=buscar)
            )
            titulo_reporte = f"REPORTE DE CURSOS - Filtro: {buscar}"
        else:
            titulo_reporte = "REPORTE GENERAL DE CURSOS"

        if not cursos.exists():
            messages.warning(request, "No se encontraron cursos.")
            return redirect("app:index_curso")

        columnas = ["ID", "Grado", "Código", "Docente", "Capacidad"]

        datos = [
            (
                c.id,
                c.get_grado_display(),
                c.codigo,
                c.docenteid.usuario.nombre,
                c.capacidad,
            )
            for c in cursos
        ]

        return exportar_pdf(
            request,
            titulo=titulo_reporte,
            columnas=columnas,
            datos=datos,
            nombre_archivo="Reporte_Cursos"
        )


class ExportarCursoExcel(DjangoView):
    def get(self, request):

        buscar = request.GET.get("buscar", "").strip()

        cursos = Curso.objects.select_related("docenteid__usuario")

        if buscar:
            cursos = cursos.filter(
                Q(grado__icontains=buscar) |
                Q(docenteid__usuario__nombre__icontains=buscar)
            )
            titulo_reporte = f"REPORTE DE CURSOS - Filtro: {buscar}"
        else:
            titulo_reporte = "REPORTE GENERAL DE CURSOS"

        if not cursos.exists():
            messages.warning(request, "No se encontraron cursos.")
            return redirect("app:index_curso")

        columnas = ["ID", "Grado", "Código", "Docente", "Capacidad"]

        datos = [
            (
                c.id,
                c.get_grado_display(),
                c.codigo,
                c.docenteid.usuario.nombre,
                c.capacidad,
            )
            for c in cursos
        ]

        return exportar_excel(
            titulo=titulo_reporte,
            columnas=columnas,
            datos=datos,
            nombre_archivo="Reporte_Cursos"
        )


