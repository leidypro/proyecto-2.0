from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.exceptions import ValidationError

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")

        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")

        return self.create_user(email, nombre, password, **extra_fields)


estado_usuario = (
    (True, "Activo"),
    (False, "Inactivo"),
)


class Usuario(AbstractUser):
    img_usuario = models.ImageField(upload_to="usuarios/", blank=True, null=True)
    nombre = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    estado = models.BooleanField(default=True, choices=estado_usuario)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "usuario"

    def get_rol(self):
        grupo = self.groups.first()
        return grupo.name if grupo else "Sin rol"

    def __str__(self):
        return self.nombre


class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    cargo = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"
        db_table = "administrador"

    def __str__(self):
        return self.usuario.nombre


class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    creador_por = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        db_table = "evento"

    def __str__(self):
        return self.titulo


class docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.TextField()

    class Meta:
        verbose_name = "docente"
        verbose_name_plural = "docentes"
        db_table = "docente"

    def __str__(self):
        return self.usuario.nombre


GRADOS_CURSO = [
    ("Preescolar", "Preescolar"),
    ("1", "1°"),
    ("2", "2°"),
    ("3", "3°"),
    ("4", "4°"),
    ("5", "5°"),
    ("6", "6°"),
    ("7", "7°"),
    ("8", "8°"),
    ("9", "9°"),
    ("10", "10°"),
    ("11", "11°"),
]

Estado_Matricula = [
    ("Matriculado", "Matriculado"),
    ("No Matriculado", "No Matriculado"),
    ("Retirado", "Retirado"),
    ("Graduado", "Graduado"),
    ("Sancionado", "Sancionado"),
]


class Curso(models.Model):
    id = models.AutoField(primary_key=True)
    grado = models.CharField(max_length=20, choices=GRADOS_CURSO)
    codigo = models.CharField(max_length=50, unique=True)
    capacidad = models.IntegerField()
    fechainicio = models.DateTimeField(auto_now_add=True, editable=False)
    fechafin = models.DateTimeField(null=True, blank=True)
    docenteid = models.ForeignKey(docente, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "curso"
        verbose_name_plural = "Cursos"
        db_table = "Curso"

    def __str__(self):
        return self.codigo


class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    fechaNacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    estadoMatricula = models.CharField(
        max_length=20, default="Matriculado", choices=Estado_Matricula
    )
    fechaIngreso = models.DateField(verbose_name="Fecha de Ingreso", default=timezone.now)
    cursoId = models.ForeignKey(Curso, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    qr = models.ImageField(upload_to="usuarios/", blank=True)

    def clean(self):
        if self.cursoId:
            total = Estudiante.objects.filter(cursoId=self.cursoId).count()
            if self.pk:
                total = (
                    Estudiante.objects.filter(cursoId=self.cursoId)
                    .exclude(pk=self.pk)
                    .count()
                )
            if total >= self.cursoId.capacidad:
                raise ValidationError(
                    {"cursoId": "El curso ya ha alcanzado su capacidad máxima."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.codigo:
            self.codigo = f"EST-{self.usuario.id}"
        if not self.qr:
            qr_img = qrcode.make(self.codigo)
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            self.qr.save(f"qr_{self.usuario.id}.png", File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.usuario.nombre

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        db_table = "Estudiante"


class Asistencia(models.Model):
    choices = [
        ("A tiempo", "A tiempo"),
        ("Tarde", "Tarde"),
        ("Inasistencia", "Inasistencia"),
    ]
    id = models.AutoField(primary_key=True)
    estudianteid = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now=True)
    horaentrada = models.TimeField()
    horasalida = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=choices)
    observaciones = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"
        db_table = "asistencia"


class Acudiente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    telefono = models.TextField(
        max_length=10, null=True, blank=True, verbose_name="Teléfono"
    )
    direccion = models.TextField(
        max_length=150, null=True, blank=True, verbose_name="Dirección"
    )

    def __str__(self):
        return f"{self.usuario.nombre} - Acudiente"

    class Meta:
        verbose_name = "Acudiente"
        verbose_name_plural = "Acudientes"
        db_table = "Acudiente"


class Estudianteacudiente(models.Model):
    estudianteId = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    acudienteId = models.ForeignKey(Acudiente, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.estudianteId.usuario.nombre} - Acudiente: {self.acudienteId.usuario.nombre}"

    class Meta:
        verbose_name = "Estudianteacudiente"
        verbose_name_plural = "Estudianteacudientes"
        db_table = "Estudianteacudiente"


class categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        db_table = "categoria"

    def __str__(self):
        return self.nombre


class tipoelemento(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "tipoelemento"
        verbose_name_plural = "tipoelementos"
        db_table = "tipoelemento"

    def __str__(self):
        return self.nombre


class marca(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "marca"
        verbose_name_plural = "marcas"
        db_table = "marca"

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
        db_table = "unidadmedida"

    def __str__(self):
        return self.nombre


class Elemento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    stockActual = models.IntegerField()
    stockMinimo = models.IntegerField()
    tipoElementoId = models.ForeignKey(tipoelemento, on_delete=models.CASCADE)
    categoriaId = models.ForeignKey(categoria, on_delete=models.CASCADE)
    marcaId = models.ForeignKey(marca, on_delete=models.CASCADE)
    unidadMedidaId = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=100)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaActualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Elemento"
        verbose_name_plural = "Elementos"
        db_table = "elemento"

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    choices = [
        ("Entrada", "Entrada"),
        ("Salida", "Salida"),
    ]
    tipo = models.CharField(max_length=50, choices=choices)
    fecha = models.DateTimeField(auto_now=True)
    cantidad = models.IntegerField()
    elementoId = models.ForeignKey(Elemento, on_delete=models.CASCADE)
    usuarioId = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cursoId = models.ForeignKey(Curso, on_delete=models.CASCADE)
    motivo = models.TextField()

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)
        if es_nuevo:
            elemento = self.elementoId
            if self.tipo == "Entrada":
                elemento.stockActual += self.cantidad
            elif self.tipo == "Salida":
                elemento.stockActual -= self.cantidad
            elemento.save(update_fields=["stockActual"])

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimiento"
        db_table = "movimiento"

    def __str__(self):
        return self.tipo


class Notificacion(models.Model):
    ESTADO_CHOICES = [
        ("no_leida", "No Leída"),
        ("leida", "Leída"),
    ]
    TIPO_CHOICES = [
        ("aviso", "Aviso"),
        ("actualizacion", "Actualización"),
        ("urgente", "Urgente"),
    ]
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="no_leida")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default="aviso")
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"
        db_table = "notificacion"

    def __str__(self):
        return self.titulo
