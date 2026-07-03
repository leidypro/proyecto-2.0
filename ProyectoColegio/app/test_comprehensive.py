from django.test import TestCase,Client
from django.utils import timezone
from datetime import date, time
from django.conf import settings
from app.models import (
    Usuario,
    docente,
    Curso,
    Estudiante,
    Administrador,
    Asistencia,
    categoria,
    marca,
    tipoelemento,
    UnidadMedida,
    Elemento,
    Notificacion,
    Usuario,
    docente,
    Curso,
    Estudiante,
    Acudiente
)


# ==========================
# PRUEBAS DEL MODELO USUARIO
# ==========================

class UsuarioTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="test@example.com",
            nombre="Usuario Prueba",
            password="test123"
        )

    def test_crear_usuario(self):
        self.assertEqual(self.usuario.email, "test@example.com")
        self.assertEqual(self.usuario.nombre, "Usuario Prueba")
        self.assertTrue(self.usuario.estado)

    def test_crear_superusuario(self):
        admin = Usuario.objects.create_superuser(
            email="admin@example.com",
            nombre="Administrador",
            password="admin123"
        )

        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_email_unico(self):
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                email="test@example.com",
                nombre="Otro Usuario",
                password="123456"
            )

    def test_usuario_inactivo(self):
        usuario = Usuario.objects.create_user(
            email="inactivo@example.com",
            nombre="Usuario Inactivo",
            password="123456",
            estado=False
        )

        self.assertFalse(usuario.estado)


# =================================
# PRUEBAS DEL MODELO ADMINISTRADOR
# =================================

class AdministradorTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="admin@example.com",
            nombre="Administrador",
            password="admin123"
        )

    def test_crear_administrador(self):

        administrador = Administrador.objects.create(
            usuario=self.usuario,
            cargo="Rector"
        )

        self.assertEqual(administrador.cargo, "Rector")
        self.assertEqual(administrador.usuario.nombre, "Administrador")

    def test_str_administrador(self):

        administrador = Administrador.objects.create(
            usuario=self.usuario,
            cargo="Coordinador"
        )

        self.assertIsInstance(str(administrador), str)


# ==========================
# PRUEBAS DEL MODELO CURSO
# ==========================

class CursoTest(TestCase):

    def setUp(self):

        usuario = Usuario.objects.create_user(
            email="docente@example.com",
            nombre="Carlos Pérez",
            password="123456"
        )

        self.docente = docente.objects.create(
            usuario=usuario,
            especialidad="Matemáticas"
        )

    def test_crear_curso(self):

        curso = Curso.objects.create(
            grado=10,
            codigo="10A",
            capacidad=40,
            docenteid=self.docente
        )

        self.assertEqual(curso.grado, 10)
        self.assertEqual(curso.codigo, "10A")
        self.assertEqual(curso.capacidad, 40)

    def test_capacidad_mayor_cero(self):

        curso = Curso.objects.create(
            grado=11,
            codigo="11A",
            capacidad=35,
            docenteid=self.docente
        )

        self.assertGreater(curso.capacidad, 0)


# ===============================
# PRUEBAS DEL MODELO ESTUDIANTE
# ===============================

class EstudianteTest(TestCase):

    def setUp(self):

        usuario_docente = Usuario.objects.create_user(
            email="docente@example.com",
            nombre="Docente",
            password="123456"
        )

        self.docente = docente.objects.create(
            usuario=usuario_docente,
            especialidad="Informática"
        )

        self.curso = Curso.objects.create(
            grado=10,
            codigo="10A",
            capacidad=40,
            docenteid=self.docente
        )

        self.usuario_estudiante = Usuario.objects.create_user(
            email="estudiante@example.com",
            nombre="Juan Pérez",
            password="123456"
        )

    def test_crear_estudiante(self):

        estudiante = Estudiante.objects.create(
            usuario=self.usuario_estudiante,
            fechaNacimiento=date(2008, 5, 20),
            estadoMatricula="Matriculado",
            cursoId=self.curso,
            codigo="EST001"
        )

        self.assertEqual(estudiante.usuario.nombre, "Juan Pérez")
        self.assertEqual(estudiante.estadoMatricula, "Matriculado")
        self.assertEqual(estudiante.codigo, "EST001")

    def test_codigo_unico(self):

        Estudiante.objects.create(
            usuario=self.usuario_estudiante,
            fechaNacimiento=date(2008, 5, 20),
            estadoMatricula="Matriculado",
            cursoId=self.curso,
            codigo="EST001"
        )

        otro_usuario = Usuario.objects.create_user(
            email="otro@example.com",
            nombre="Pedro Gómez",
            password="123456"
        )

        with self.assertRaises(Exception):

            Estudiante.objects.create(
                usuario=otro_usuario,
                fechaNacimiento=date(2007, 8, 15),
                estadoMatricula="Matriculado",
                cursoId=self.curso,
                codigo="EST001"
            )

    def test_buscar_estudiante(self):

        Estudiante.objects.create(
            usuario=self.usuario_estudiante,
            fechaNacimiento=date(2008, 5, 20),
            estadoMatricula="Matriculado",
            cursoId=self.curso,
            codigo="EST001"
        )

        existe = Estudiante.objects.filter(codigo="EST001").exists()

        self.assertTrue(existe)


class AsistenciaTest(TestCase):

    def setUp(self):

        usuario_docente = Usuario.objects.create_user(
            email="docente@example.com",
            nombre="Docente",
            password="123456"
        )

        self.docente = docente.objects.create(
            usuario=usuario_docente,
            especialidad="Matemáticas"
        )

        self.curso = Curso.objects.create(
            grado=10,
            codigo="10A",
            capacidad=40,
            docenteid=self.docente
        )

        usuario_estudiante = Usuario.objects.create_user(
            email="estudiante@example.com",
            nombre="Juan Pérez",
            password="123456"
        )

        self.estudiante = Estudiante.objects.create(
            usuario=usuario_estudiante,
            fechaNacimiento=date(2008, 5, 20),
            estadoMatricula="Matriculado",
            cursoId=self.curso,
            codigo="EST001"
        )

    def test_registrar_asistencia(self):

        asistencia = Asistencia.objects.create(
            estudianteid=self.estudiante,
            fecha=timezone.now().date(),
            horaentrada=time(7, 0),
            horasalida=time(16, 0),
            estado="A tiempo"
        )

        self.assertEqual(asistencia.estado, "A tiempo")

    def test_buscar_asistencia(self):

        Asistencia.objects.create(
            estudianteid=self.estudiante,
            fecha=timezone.now().date(),
            horaentrada=time(7, 5),
            estado="Tarde"
        )

        existe = Asistencia.objects.filter(
            estudianteid=self.estudiante
        ).exists()

        self.assertTrue(existe)

    def test_estado_asistencia(self):

        asistencia = Asistencia.objects.create(
            estudianteid=self.estudiante,
            fecha=timezone.now().date(),
            horaentrada=time(7, 10),
            estado="Excusada"
        )

        self.assertEqual(asistencia.estado, "Excusada")


# ===============================
# PRUEBAS DEL MODELO INVENTARIO
# ===============================

class InventarioTest(TestCase):

    def setUp(self):

        self.categoria = categoria.objects.create(
            nombre="Equipos"
        )

        self.marca = marca.objects.create(
            nombre="Dell"
        )

        self.tipo = tipoelemento.objects.create(
            nombre="Portátil"
        )

        self.unidad = UnidadMedida.objects.create(
            nombre="Unidad"
        )

    def test_crear_elemento(self):

        elemento = Elemento.objects.create(
            nombre="Computador",
            descripcion="Equipo para laboratorio",
            stockActual=10,
            stockMinimo=2,
            categoriaId=self.categoria,
            marcaId=self.marca,
            tipoElementoId=self.tipo,
            unidadMedidaId=self.unidad
        )

        self.assertEqual(elemento.nombre, "Computador")
        self.assertEqual(elemento.stockActual, 10)

    def test_stock_positivo(self):

        elemento = Elemento.objects.create(
            nombre="Video Beam",
            stockActual=5,
            stockMinimo=1,
            categoriaId=self.categoria,
            marcaId=self.marca,
            tipoElementoId=self.tipo,
            unidadMedidaId=self.unidad
        )

        self.assertGreaterEqual(elemento.stockActual, 0)

    def test_buscar_elemento(self):

        Elemento.objects.create(
            nombre="Impresora",
            stockActual=3,
            stockMinimo=1,
            categoriaId=self.categoria,
            marcaId=self.marca,
            tipoElementoId=self.tipo,
            unidadMedidaId=self.unidad
        )

        existe = Elemento.objects.filter(
            nombre="Impresora"
        ).exists()

        self.assertTrue(existe)


# ===============================
# PRUEBAS DEL MODELO NOTIFICACIÓN
# ===============================

class NotificacionTest(TestCase):

    def setUp(self):

        self.usuario = Usuario.objects.create_user(
            email="usuario@example.com",
            nombre="Usuario",
            password="123456"
        )

    def test_crear_notificacion(self):

        notificacion = Notificacion.objects.create(
            titulo="Aviso",
            mensaje="Mensaje de prueba",
            tipo="info",
            receptor=self.usuario
        )

        self.assertEqual(notificacion.titulo, "Aviso")
        self.assertEqual(notificacion.estado, "no_leida")

    def test_marcar_como_leida(self):

        notificacion = Notificacion.objects.create(
            titulo="Recordatorio",
            mensaje="Prueba",
            tipo="info",
            receptor=self.usuario,
            estado="no_leida"
        )

        notificacion.estado = "leida"
        notificacion.save()

        self.assertEqual(notificacion.estado, "leida")

    def test_buscar_notificacion(self):

        Notificacion.objects.create(
            titulo="Nueva Notificación",
            mensaje="Contenido",
            tipo="info",
            receptor=self.usuario
        )

        existe = Notificacion.objects.filter(
            titulo="Nueva Notificación"
        ).exists()

        self.assertTrue(existe)
        

# ==========================
# PRUEBAS DE VALIDACIONES
# ==========================

class ValidacionesTest(TestCase):

    def test_email_guardado_correctamente(self):

        usuario = Usuario.objects.create_user(
            email="correo@example.com",
            nombre="Usuario",
            password="123456"
        )

        self.assertEqual(usuario.email, "correo@example.com")

    def test_fecha_nacimiento_estudiante(self):

        usuario_docente = Usuario.objects.create_user(
            email="docente@example.com",
            nombre="Docente",
            password="123456"
        )

        docente_obj = docente.objects.create(
            usuario=usuario_docente,
            especialidad="Informática"
        )

        curso = Curso.objects.create(
            grado=10,
            codigo="10A",
            capacidad=35,
            docenteid=docente_obj
        )

        usuario_estudiante = Usuario.objects.create_user(
            email="estudiante@example.com",
            nombre="Laura Gómez",
            password="123456"
        )

        estudiante = Estudiante.objects.create(
            usuario=usuario_estudiante,
            fechaNacimiento=date(2008, 4, 10),
            estadoMatricula="Matriculado",
            cursoId=curso,
            codigo="EST010"
        )

        self.assertEqual(
            estudiante.fechaNacimiento,
            date(2008, 4, 10)
        )


# ==========================
# PRUEBAS DE SEGURIDAD
# ==========================

class SeguridadTest(TestCase):

    def setUp(self):

        self.client = Client()

        self.usuario = Usuario.objects.create_user(
            email="admin@example.com",
            nombre="Administrador",
            password="admin123"
        )

    def test_password_encriptado(self):

        self.assertNotEqual(
            self.usuario.password,
            "admin123"
        )

        self.assertTrue(
            self.usuario.password.startswith("pbkdf2")
        )

    def test_usuario_inactivo(self):

        usuario = Usuario.objects.create_user(
            email="inactivo@example.com",
            nombre="Usuario",
            password="123456",
            estado=False
        )

        self.assertFalse(usuario.estado)

    def test_secret_key_configurada(self):

        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, "")


# ==========================
# PRUEBAS DEL ACUDIENTE
# ==========================

class AcudienteTest(TestCase):

    def setUp(self):

        self.usuario = Usuario.objects.create_user(
            email="acudiente@example.com",
            nombre="María Pérez",
            password="123456"
        )

    def test_crear_acudiente(self):

        acudiente = Acudiente.objects.create(
            usuario=self.usuario,
            telefono="3001234567",
            direccion="Calle 10 # 20 - 30"
        )

        self.assertEqual(
            acudiente.usuario.nombre,
            "María Pérez"
        )

    def test_buscar_acudiente(self):

        Acudiente.objects.create(
            usuario=self.usuario,
            telefono="3001234567",
            direccion="Calle 10 # 20 - 30"
        )

        existe = Acudiente.objects.filter(
            usuario=self.usuario
        ).exists()

        self.assertTrue(existe)

    def test_str_acudiente(self):

        acudiente = Acudiente.objects.create(
            usuario=self.usuario,
            telefono="3001234567",
            direccion="Calle 10 # 20 - 30"
        )

        self.assertIsInstance(str(acudiente), str)