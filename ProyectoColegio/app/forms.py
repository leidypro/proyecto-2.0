from django.urls import reverse_lazy
from django import forms
from django.utils import timezone
from app.models import (
    Curso,
    categoria,
    Elemento,
    marca,
    tipoelemento,
    UnidadMedida,
    Movimiento,
    Evento,
    Asistencia,
    Usuario,
    Administrador,
    Acudiente,
    Estudiante,
    docente,
    Notificacion,
)
import re
from django.utils import timezone
from datetime import time

# ── Helper de validación


def solo_letras(value, campo="Este campo"):
    """Solo letras (incluye tildes, ñ y espacios). Sin números ni especiales."""
    value = value.strip()
    if not value:
        raise forms.ValidationError(f"{campo} es obligatorio.")
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", value):
        raise forms.ValidationError(
            f"{campo} solo puede contener letras y espacios, sin números ni caracteres especiales."
        )
    return value



class CursoForm(forms.ModelForm):

    class Meta:
        model = Curso
        fields = "__all__"

        labels = {
            "grado": "Grado",
            "codigo": "Código",
            "capacidad": "Capacidad",
            "docenteid": "Docente",
            "fechafin": "Fecha de Fin",
        }

        widgets = {
            "grado": forms.Select(attrs={"class": "form-control"}),
            "codigo": forms.NumberInput(attrs={"class": "form-control"}),
            "capacidad": forms.NumberInput(attrs={"class": "form-control"}),
            "docenteid": forms.Select(attrs={"class": "form-control"}),
            "fechafin": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def clean_nom(self):
        return solo_letras(self.cleaned_data.get("nom", ""), "El nombre del curso")

    def clean_jornada(self):
        return solo_letras(self.cleaned_data.get("jornada", ""), "La jornada")

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get("capacidad")
        if capacidad <= 0:
            raise forms.ValidationError("La capacidad debe ser un número positivo.")
        return capacidad


class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = "__all__"
        labels = {
            "estudianteid": "Estudiante",
            "horaentrada": "Hora de Entrada",
            "horasalida": "Hora de Salida",
            "observaciones": "Observaciones",
            "fecha": "Fecha",
            "estado": "Estado",
        }
        widgets = {
            "estudianteid": forms.Select(attrs={"class": "form-control"}),
            "horaentrada": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "horasalida": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "observaciones": forms.TextInput(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "estado": forms.HiddenInput(
                attrs={"class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado"].required = False

    def clean_observaciones(self):
        obs = self.cleaned_data.get("observaciones")
        if obs:
            if len(obs) > 200:
                raise forms.ValidationError("Máximo 200 caracteres.")
            if len(obs) < 10:
                raise forms.ValidationError("Mínimo 10 caracteres.")
        return obs

    def clean(self):
        cleaned_data = super().clean()
        estudiante = cleaned_data.get("estudianteid")
        horaentrada = cleaned_data.get("horaentrada")
        horasalida = cleaned_data.get("horasalida")

        if estudiante:
            fecha_hoy = timezone.now().date()
            existe = (
                Asistencia.objects.filter(estudianteid=estudiante, fecha=fecha_hoy)
                .exclude(pk=self.instance.pk)
                .exists()
            )

            if existe:
                self.add_error(
                    "estudianteid", "Este estudiante ya tiene asistencia hoy."
                )

        if horaentrada:
            limite = time(7, 0)
            cleaned_data["estado"] = "A tiempo" if horaentrada <= limite else "Tarde"

        if horaentrada and horasalida:
            if horaentrada >= horasalida:
                self.add_error(
                    "horasalida",
                    "La hora de salida debe ser posterior a la de entrada.",
                )

        return cleaned_data


# ── Formulario para Crear Usuario


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nombre", "email", "password", "estado", "img_usuario"]
        labels = {
            "email": "Correo Electrónico",
            "img_usuario": "Imagen de Perfil",
        }
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre completo"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Contraseña",
                    "id": "id_contraseña",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "img_usuario": forms.FileInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return solo_letras(nombre, "El nombre")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email

        email = email.lower()

        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.fields["email"].widget.attrs["class"] = "form-control is-invalid"
            raise forms.ValidationError(
                "Este correo ya se encuentra registrado. Intenta con uno diferente."
            )

        dominios_permitidos = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
        partes = email.split("@")
        if len(partes) > 1 and partes[1] not in dominios_permitidos:
            self.fields["email"].widget.attrs["class"] = "form-control is-invalid"
            raise forms.ValidationError(
                f"Solo se permiten correos de: {', '.join(dominios_permitidos)}"
            )

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            return password

        errores = []
        if len(password) < 8:
            errores.append("al menos 8 caracteres")
        if not any(c.isupper() for c in password):
            errores.append("una mayúscula")
        if not any(c.isdigit() for c in password):
            errores.append("un número")

        if errores:
            raise forms.ValidationError(f"Falta: {', '.join(errores)}.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = self.data.get("confirmar_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("password", "Las contraseñas no coinciden.")
        return cleaned_data


# ── Formulario para Editar Usuario
class UsuarioEstudianteForm(UsuarioForm):
    """UsuarioForm sin validación de password para estudiante y acudiente"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].required = False

    def clean_password(self):
        return self.cleaned_data.get("password", "")

    def clean(self):
        # Omitir validación de confirmación de contraseña
        return super(forms.ModelForm, self).clean()


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nombre", "email", "estado", "img_usuario"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "img_usuario": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        return solo_letras(nombre, "El nombre")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email

        email = email.lower()

        # Validar que no exista otro usuario con el mismo email (excluyendo el actual)
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.fields["email"].widget.attrs["class"] = "form-control is-invalid"
            raise forms.ValidationError(
                "Este correo ya se encuentra registrado. Intenta con uno diferente."
            )

        dominios_permitidos = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
        partes = email.split("@")
        if len(partes) > 1 and partes[1] not in dominios_permitidos:
            self.fields["email"].widget.attrs["class"] = "form-control is-invalid"
            raise forms.ValidationError(
                f"Solo se permiten correos de: {', '.join(dominios_permitidos)}"
            )

        return email

    def clean_img_usuario(self):
        imagen = self.cleaned_data.get("img_usuario")
        if imagen:
            # Validar tipo de archivo
            tipos_permitidos = ["image/jpeg", "image/png", "image/webp"]
            if imagen.content_type not in tipos_permitidos:
                raise forms.ValidationError(
                    "Solo se permiten imágenes JPG, PNG o WEBP."
                )
            # Validar tamaño (5MB máximo)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "La imagen no puede superar 5MB."
                )
        return imagen


# ── Formularios de Roles


class AdministradorForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ["cargo"]
        widgets = {
            "cargo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Cargo"}
            )
        }

    def clean_cargo(self):
        return solo_letras(self.cleaned_data.get("cargo", ""), "El cargo")


class DocenteForm(forms.ModelForm):
    class Meta:
        model = docente
        fields = ["especialidad"]
        widgets = {
            "especialidad": forms.Textarea(attrs={"class": "form-control", "rows": 3})
        }

    def clean_especialidad(self):
        return solo_letras(self.cleaned_data.get("especialidad", ""), "La especialidad")


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ["fechaNacimiento", "estadoMatricula", "fechaIngreso", "cursoId"]
        labels = {
            "fechaNacimiento": "Fecha de Nacimiento",
            "estadoMatricula": "Estado de Matrícula",
            "fechaIngreso": "Fecha de Ingreso",
            "cursoId": "Curso",
        }
        widgets = {
            "fechaNacimiento": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d"
            ),
            "fechaIngreso": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d"
            ),
            "estadoMatricula": forms.Select(attrs={"class": "form-control"}),
            "cursoId": forms.Select(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fechaNacimiento"].input_formats = ["%Y-%m-%d"]
        self.fields["fechaIngreso"].input_formats = ["%Y-%m-%d"]
    def clean_fechaNacimiento(self):
        fecha = self.cleaned_data.get("fechaNacimiento")
        if fecha and fecha == timezone.localdate():
            raise forms.ValidationError(
                "La fecha de nacimiento no puede ser el día de hoy."
            )
        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError(
                "La fecha de nacimiento no puede ser una fecha futura."
            )
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        curso = cleaned_data.get("cursoId")
        fecha_nacimiento = cleaned_data.get("fechaNacimiento")

        # Validar capacidad del curso
        if curso:
            # Contar estudiantes matriculados en el curso (excluyendo el estudiante actual si es edición)
            estudiantes_en_curso = Estudiante.objects.filter(
                cursoId=curso,
                estadoMatricula="Matriculado"
            )
            
            # Si es edición, excluir el estudiante actual del conteo
            if self.instance.pk:
                estudiantes_en_curso = estudiantes_en_curso.exclude(pk=self.instance.pk)
            
            cantidad_actual = estudiantes_en_curso.count()
            
            if cantidad_actual >= curso.capacidad:
                raise forms.ValidationError(
                    f"El curso {curso.codigo} ya ha alcanzado su capacidad máxima "
                    f"({curso.capacidad} estudiantes). Por favor seleccione otro curso."
                )

        # Validar coherencia entre edad y grado
        if fecha_nacimiento and curso:
            from dateutil.relativedelta import relativedelta
            
            hoy = timezone.localdate()
            edad = relativedelta(hoy, fecha_nacimiento).years
            
            # Mapeo de edades esperadas por grado
            edades_esperadas = {
                "Preescolar": (5, 6),
                "1": (6, 7),
                "2": (7, 8),
                "3": (8, 9),
                "4": (9, 10),
                "5": (10, 11),
                "6": (11, 12),
                "7": (12, 13),
                "8": (13, 14),
                "9": (14, 15),
                "10": (15, 16),
                "11": (16, 18),
            }
            
            if curso.grado in edades_esperadas:
                edad_min, edad_max = edades_esperadas[curso.grado]
                if edad < edad_min or edad > edad_max:
                    raise forms.ValidationError(
                        f"La edad del estudiante ({edad} años) no corresponde al grado {curso.grado}. "
                        f"Edad esperada: {edad_min} a {edad_max} años."
                    )

        return cleaned_data


class AcudienteForm(forms.ModelForm):
    email_acudiente = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-custom",
                "placeholder": "correo@ejemplo.com",
            }
        ),
    )
    nombre_acudiente = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-custom",
                "placeholder": "Nombre del acudiente",
            }
        ),
    )

    class Meta:
        model = Acudiente
        fields = ["telefono", "direccion"]  # ← nombre ya no está
        widgets = {
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "10"}
            ),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def clean_nombre_acudiente(self):
        return solo_letras(
            self.cleaned_data.get("nombre_acudiente", ""), "El nombre del acudiente"
        )

    def clean_email_acudiente(self):
        email = self.cleaned_data.get("email_acudiente", "").lower()
        dominios_permitidos = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
        partes = email.split("@")
        if len(partes) > 1 and partes[1] not in dominios_permitidos:
            raise forms.ValidationError(
                f"Solo se permiten correos de: {', '.join(dominios_permitidos)}"
            )
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not re.match(r"^\d{7,10}$", telefono):
            raise forms.ValidationError(
                "El teléfono debe contener solo dígitos (7 a 10 cifras)."
            )
        return telefono

    def clean_direccion(self):
        return self.cleaned_data.get("direccion", "")


class AcudienteReadOnlyForm(forms.Form):
    """
    Formulario de solo lectura para mostrar los datos del acudiente
    en la edición del estudiante. Los campos están deshabilitados
    para que no puedan modificarse desde aquí.
    """
    nombre_acudiente = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "disabled": True}
        ),
    )
    email_acudiente = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "disabled": True}
        ),
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "disabled": True}
        ),
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "disabled": True}
        ),
    )


class TipoElementoForm(forms.ModelForm):
    class Meta:
        model = tipoelemento
        fields = "__all__"
        widgets = {"nombre": forms.TextInput(attrs={"class": "form-control"})}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        exist = (
            tipoelemento.objects.filter(nombre=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exist:
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "Este tipo de elemento ya se encuentra registrado"
            )
        return nombre


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = "__all__"
        widgets = {"nombre": forms.TextInput(attrs={"class": "form-control"})}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        exist = (
            UnidadMedida.objects.filter(nombre=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exist:
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "Esta unidad de medida ya se encuentra registrada"
            )
        return nombre


class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = "__all__"
        labels = {
            "nombre": "Nombre",
            "cantidad": "Cantidad",
            "marcaId": "Marca",
            "tipoElementoId": "Tipo de Elemento",
            "unidadMedidaId": "Unidad de Medida",
            "categoriaId": "Categoría",
            "descripcion": "Descripción",
            "stockActual": "Stock Actual",
            "stockMinimo": "Stock Mínimo",
            "ubicacion": "Ubicación",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "marcaId": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-crear-url": reverse_lazy("app:crear_marca"),
                    "data-label": "Marca",
                }
            ),
            "tipoElementoId": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-crear-url": reverse_lazy("app:crear_tipo"),
                    "data-label": "Tipo de Elemento",
                }
            ),
            "unidadMedidaId": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-crear-url": reverse_lazy("app:crear_unidad"),
                    "data-label": "Unidad de Medida",
                }
            ),
            "categoriaId": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-crear-url": reverse_lazy("app:crear_categoria"),
                    "data-label": "Categoría",
                }
            ),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "stockActual": forms.NumberInput(attrs={"class": "form-control"}),
            "stockMinimo": forms.NumberInput(attrs={"class": "form-control"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        exist = (
            Elemento.objects.filter(nombre=nombre).exclude(pk=self.instance.pk).exists()
        )

        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ][A-Za-z ÁÉÍÓÚáéíóúÑñ]*$"

        if not re.match(patron, nombre):
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "El Nombre no es válido (debe iniciar con letra y no usar caracteres especiales ni números)"
            )

        if exist:
            self.fields["nombre"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError("Este elemento ya se encuentra registrado")

        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion", "").strip()

        # Validar que no esté vacía
        if not descripcion:
            self.fields["descripcion"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError("La descripción no puede estar vacía.")

        # Validar longitud
        if len(descripcion) > 200:
            self.fields["descripcion"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "La descripción no puede superar los 200 caracteres."
            )

        # Validar que empiece con letra
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ][A-Za-z0-9 ÁÉÍÓÚáéíóúÑñ.,;:()\-]*$"
        if not re.match(patron, descripcion):
            self.fields["descripcion"].widget.attrs["class"] = "form-control-invalid"
            raise forms.ValidationError(
                "La descripción debe iniciar con una letra y no contener caracteres especiales inválidos."
            )

        return descripcion

    def clean_stockActual(self):
        stock = self.cleaned_data.get("stockActual")
        if stock is not None:
            if stock < 0:
                raise forms.ValidationError("El stock no puede ser negativo ")
            if float(stock) != int(stock):
                raise forms.ValidationError("El stock no puede ser decimal ")
        return stock

    def clean_stockMinimo(self):
        stock = self.cleaned_data.get("stockMinimo")
        if stock is not None:
            if stock < 0:
                raise forms.ValidationError("El stock no puede ser negativo ")
            if float(stock) != int(stock):
                raise forms.ValidationError("El stock no puede ser decimal ")
        return stock

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get("ubicacion", "").strip()
        ubicacion = re.sub(r"\s+", " ", ubicacion)
        if len(ubicacion) < 3:
            raise forms.ValidationError(
                "La ubicación debe tener al menos 3 caracteres."
            )
        patron = r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-]+$"
        if not re.match(patron, ubicacion):
            raise forms.ValidationError(
                "La ubicación solo puede contener letras, números y guiones."
            )
        return ubicacion


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = "__all__"
        labels = {
            "tipo": "Tipo de Movimiento",
            "codigo": "Código",
            "cantidad": "Cantidad",
            "docenteid": "Docente",
            "fecha": "Fecha",
            "motivo": "Motivo",
            "elementoId": "Elemento",
            "usuarioId": "Usuario",
            "cursoId": "Curso",
        }
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "docenteid": forms.Select(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "motivo": forms.Textarea(attrs={"class": "form-control"}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad == 0:
            raise forms.ValidationError("No se puede tener una cantidad igual a 0")

        if cantidad < 0:
            raise forms.ValidationError("No se puede tener una cantidad negativa")
        return cantidad

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        cantidad = cleaned_data.get("cantidad")
        elemento = cleaned_data.get("elementoId")

        if tipo == "Salida" and elemento and cantidad:
            # Si es edición, considerar el stock actual más la cantidad original del movimiento
            stock_disponible = elemento.stockActual
            if self.instance.pk:
                stock_disponible += self.instance.cantidad

            if cantidad > stock_disponible:
                self.add_error(
                    "cantidad",
                    f"La cantidad ({cantidad}) supera el stock disponible del elemento "
                    f"'{elemento.nombre}' ({stock_disponible} unidades).",
                )

        return cleaned_data

    def clean_motivo(self):
        motivo = self.cleaned_data.get("motivo")
        motivo = motivo.strip()
        if len(motivo) < 10 or len(motivo) > 200:
            raise forms.ValidationError(
                "El motivo debe tener entre 10 y 200 caracteres."
            )
        return motivo


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = "__all__"
        exclude = ['google_event_id']
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "fecha_fin": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["fecha_inicio"].input_formats = ("%Y-%m-%dT%H:%M",)

        self.fields["fecha_fin"].input_formats = ("%Y-%m-%dT%H:%M",)

    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo")

        if titulo.isdigit():
            raise forms.ValidationError("El título no puede contener solo números.")

        if not re.match(r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$", titulo):
            raise forms.ValidationError(
                "El título no puede contener caracteres especiales."
            )

        if (
            Evento.objects.filter(titulo__iexact=titulo)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe un evento con este título.")

        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")

        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")
        if len(descripcion) < 10:
            raise forms.ValidationError(
                "La descripción debe tener mínimo 10 caracteres."
            )
        if len(descripcion) > 200:
            raise forms.ValidationError(
                "La descripción no puede superar los 200 caracteres."
            )

        return descripcion

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get("fecha_inicio")
        if fecha_inicio and fecha_inicio < timezone.now():
            raise forms.ValidationError(
                "La fecha de inicio no puede ser una fecha pasada."
            )
        return fecha_inicio

    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data.get("fecha_fin")
        if fecha_fin and fecha_fin < timezone.now():
            raise forms.ValidationError(
                "La fecha de fin no puede ser una fecha pasada."
            )
        return fecha_fin

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                self.add_error(
                    "fecha_fin",
                    "La fecha de fin debe ser mayor que la fecha de inicio.",
                )

        return cleaned_data


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = "__all__"
        labels = {
            "titulo": "Título",
            "mensaje": "Mensaje",
            "fecha_envio": "Fecha de Envío",
            "estado": "Estado",
            "tipo": "Tipo",
            "receptor": "Receptor",
            "evento": "Evento",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "mensaje": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_envio": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "receptor": forms.Select(attrs={"class": "form-control"}),
            "evento": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo")

        if titulo.isdigit():
            raise forms.ValidationError("El título no puede contener solo números.")

        if not re.match(r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$", titulo):
            raise forms.ValidationError(
                "El título no puede contener caracteres especiales."
            )

        return titulo

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get("mensaje")

        if not mensaje:
            raise forms.ValidationError("El mensaje es obligatorio.")
        if len(mensaje) < 10:
            raise forms.ValidationError("El mensaje debe tener mínimo 10 caracteres.")
        if len(mensaje) > 200:
            raise forms.ValidationError(
                "El mensaje no puede superar los 200 caracteres."
            )

        return mensaje


class MarcaForm(forms.ModelForm):
    class Meta:
        model = marca
        fields = "__all__"
        widgets = {"nombre": forms.TextInput(attrs={"class": "form-control"})}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        nombre = re.sub(r"\s+", " ", nombre)

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")

        patron = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$"
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios."
            )

        if (
            marca.objects.filter(nombre__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe una marca con este nombre.")

        return nombre


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = categoria
        fields = ["nombre"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "form-control"})}

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        nombre = re.sub(r"\s+", " ", nombre)

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")

        patron = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$"
        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios."
            )

        if (
            categoria.objects.filter(nombre__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe una categoría con este nombre.")

        return nombre
