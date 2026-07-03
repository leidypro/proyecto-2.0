from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import connection
from django.views.generic import CreateView
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from app.models import (
    Usuario,
    Administrador,
    docente,
    Estudiante,
    Acudiente,
    Estudianteacudiente,
)

from app.forms import (
    UsuarioForm,
    UsuarioUpdateForm,
    AdministradorForm,
    DocenteForm,
    EstudianteForm,
    AcudienteForm,
    AcudienteReadOnlyForm,
    UsuarioEstudianteForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.contrib.auth.models import Group


def asignar_grupo(usuario, rol):
    usuario.groups.clear()  # eliminar roles anteriores
    grupo = Group.objects.get(name=rol.capitalize())
    usuario.groups.add(grupo)


def validar_formulario_rol(rol, data, instance=None):
    """
    Valida el formulario según el rol.
    """
    if rol == "administrador":
        form = AdministradorForm(data, instance=instance)
    elif rol == "docente":
        form = DocenteForm(data, instance=instance)
    elif rol == "estudiante":
        form = EstudianteForm(data, instance=instance)
    else:
        return False, None

    return form.is_valid(), form


def guardar_perfil_rol(usuario, rol, data):
    """Crea un perfil nuevo."""
    if rol == "administrador":
        Administrador.objects.create(usuario=usuario, cargo=data.get("cargo"))
    elif rol == "docente":
        docente.objects.create(usuario=usuario, especialidad=data.get("especialidad"))
    elif rol == "estudiante":
        estudiante = Estudiante.objects.create(
            usuario=usuario,
            codigo=data.get("codigo"),
            fechaNacimiento=data.get("fechaNacimiento"),
            estadoMatricula=data.get("estadoMatricula"),
            fechaIngreso=data.get("fechaIngreso"),
            cursoId_id=data.get("cursoId"),
        )
        # El acudiente se crea junto con el estudiante
        acudiente = Acudiente.objects.create(
            usuario=usuario,
            nombre=data.get("nombre", ""),
            telefono=data.get("telefono"),
            direccion=data.get("direccion"),
        )
        # Vincular estudiante con acudiente en la tabla intermedia
        Estudianteacudiente.objects.create(
            estudianteId=estudiante, acudienteId=acudiente
        )

    asignar_grupo(usuario, rol)


# --- VISTAS ---


class UsuarioListView(ListView):
    model = Usuario
    template_name = "usuario/index.html"

    def get_queryset(self):
        queryset = Usuario.objects.all().order_by("-id")

        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(nombre__icontains=buscar)

        rol = self.request.GET.get("rol")
        if rol:
            if rol == "Administrador":
                queryset = queryset.filter(administrador__isnull=False)
            elif rol == "Docente":
                queryset = queryset.filter(docente__isnull=False)
            elif rol == "Estudiante":
                queryset = queryset.filter(estudiante__isnull=False)
            elif rol == "Acudiente":
                queryset = queryset.filter(acudiente__isnull=False)

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=(estado == '1'))

        curso = self.request.GET.get("curso")
        if curso:
            queryset = queryset.filter(estudiante__cursoId_id=curso)

        return queryset

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        total = Usuario.objects.count()
        activos = Usuario.objects.filter(estado=True).count()
        inactivos = Usuario.objects.filter(estado=False).count()
        estudiantes = Estudiante.objects.count()
        docentes = docente.objects.count()
        administradores = Administrador.objects.count()

        context["titulo"] = "Gestión de Usuarios"
        context["subtitulo"] = "Administración de usuarios del sistema"
        context["crear_url"] = reverse_lazy("app:crear_usuario")
        context["limpiar_url"] = reverse_lazy("app:limpiar_usuario")
        context["total_count"] = total
        context["total_text"] = "Total de Usuarios"
        context["text"] = "Usuarios inactivos"
        context["low_stock"] = inactivos
        context["icon_primary"] = "fa-users"
        context["icon_secodary"] = "fa-user-slash"
        context["activos"] = activos
        context["estudiantes_count"] = estudiantes
        context["docentes_count"] = docentes
        context["administradores_count"] = administradores
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        context["puede_crear"] = user.has_perm(f"{app_label}.add_{model_name}")
        context["puede_editar"] = user.has_perm(f"{app_label}.change_{model_name}")
        context["puede_eliminar"] = user.has_perm(f"{app_label}.delete_{model_name}")

        from app.models import Curso
        context['cursos'] = Curso.objects.all()

        return context


class UsuarioCreateView(View):
    template_name = "usuario/crear.html"
    success_url = reverse_lazy("app:index_usuario")

    def get_context(self, **kwargs):
        context = {
            "usuario_form": UsuarioForm(),
            "admin_form": AdministradorForm(),
            "docente_form": DocenteForm(),
            "estudiante_form": EstudianteForm(),
            "acudiente_form": AcudienteForm(),
            "acudiente_solo_form": AcudienteForm(),
            "titulo": "Crear Usuario",
            "listar_url": reverse_lazy("app:index_usuario"),
            "rol_actual": "",
            "btn_name": "Guardar",
        }
        context.update(kwargs)
        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    @transaction.atomic
    def post(self, request):

        usuario_form = UsuarioForm(request.POST, request.FILES)
        rol = request.POST.get("rol")

        if rol == "estudiante":
            usuario_form = UsuarioEstudianteForm(request.POST, request.FILES)  # ← este
            rol_form = EstudianteForm(request.POST, request.FILES)
            acudiente_form_post = AcudienteForm(request.POST)
        elif rol == "docente":
            rol_form = DocenteForm(request.POST, request.FILES)
            acudiente_form_post = None
        elif rol == "administrador":
            rol_form = AdministradorForm(request.POST, request.FILES)
            acudiente_form_post = None
        elif rol == "acudiente":
            usuario_form = UsuarioEstudianteForm(request.POST, request.FILES)
            # Inyectamos nombre y email del usuario principal al AcudienteForm
            data_acudiente = request.POST.copy()
            data_acudiente['nombre_acudiente'] = request.POST.get('nombre', '')
            data_acudiente['email_acudiente'] = request.POST.get('email', '')
            rol_form = AcudienteForm(data_acudiente)
            acudiente_form_post = None
        else:
            rol_form = None
            acudiente_form_post = None

        if not rol_form:
            messages.error(request, "Seleccione un rol válido")
            return redirect(request.path)

        acu_valido = (acudiente_form_post is None) or acudiente_form_post.is_valid()
        print("=" * 60)
        print("ROL:", rol)
        print("POST DATA:", request.POST)
        print("usuario_form válido:", usuario_form.is_valid())
        print("usuario_form errores:", usuario_form.errors)
        print("rol_form válido:", rol_form.is_valid())
        print("rol_form errores:", rol_form.errors)
        if acudiente_form_post:
            print("acudiente_form válido:", acudiente_form_post.is_valid())
            print("acudiente_form errores:", acudiente_form_post.errors)
        print("=" * 60)
        # ====================================
        if usuario_form.is_valid() and rol_form.is_valid() and acu_valido:

            # =========================
            # USUARIO PRINCIPAL
            # =========================
            usuario = usuario_form.save(commit=False)

            if rol in ["estudiante", "acudiente"]:
                usuario.set_unusable_password()
            else:
                usuario.set_password(usuario_form.cleaned_data["password"])

            usuario.save()

            # =========================
            # PERFIL
            # =========================
            perfil = rol_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            # =========================
            # ACUDIENTE STANDALONE
            # =========================
            if rol == "acudiente":
                usuario_acu = usuario
                usuario_acu.set_unusable_password()
                usuario_acu.save()

                acu = rol_form.save(commit=False)
                acu.usuario = usuario_acu
                acu.save()

                asignar_grupo(usuario_acu, "acudiente")
                messages.success(request, "Acudiente creado correctamente")
                return redirect(self.success_url)

            # =========================
            # ESTUDIANTE → ACUDIENTE
            # =========================
            if rol == "estudiante" and acudiente_form_post:

                usuario_acu = Usuario.objects.create(
                    email=acudiente_form_post.cleaned_data.get("email_acudiente"),
                    nombre=acudiente_form_post.cleaned_data.get("nombre_acudiente"),
                    estado=True,
                )
                usuario_acu.set_unusable_password()
                usuario_acu.save()

                acu = acudiente_form_post.save(commit=False)
                acu.usuario = usuario_acu
                acu.save()

                Estudianteacudiente.objects.get_or_create(
                    estudianteId=perfil, acudienteId=acu
                )

                asignar_grupo(usuario_acu, "acudiente")
            # =========================
            # ROL PRINCIPAL
            # =========================
            asignar_grupo(usuario, rol)

            messages.success(request, "Usuario creado correctamente")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            self.get_context(
                usuario_form=usuario_form,
                rol_actual=rol,
                acudiente_form=acudiente_form_post,
                acudiente_solo_form=rol_form if rol == "acudiente" else AcudienteForm(),
                estudiante_form=rol_form if rol == "estudiante" else EstudianteForm(),
                docente_form=rol_form if rol == "docente" else DocenteForm(),
                admin_form=rol_form if rol == "administrador" else AdministradorForm(),
            ),
        )


class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = "usuario/crear.html"
    success_url = reverse_lazy("app:index_usuario")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.object
        context.update(
            {
                "titulo": "Editar Usuario",
                "listar_url": self.success_url,
                "usuario_form": context.get("form"),
                "admin_form": AdministradorForm(),
                "docente_form": DocenteForm(),
                "estudiante_form": EstudianteForm(),
                "acudiente_form": AcudienteForm(),
                "btn_name": "Actualizar",
            }
        )

        # Cargar perfiles existentes para mostrar datos en los campos
        admin = Administrador.objects.filter(usuario=usuario).first()
        if admin:
            context.update(
                {
                    "rol_actual": "administrador",
                    "admin_form": AdministradorForm(instance=admin),
                }
            )

        doc = docente.objects.filter(usuario=usuario).first()
        if doc:
            context.update(
                {"rol_actual": "docente", "docente_form": DocenteForm(instance=doc)}
            )

        est = Estudiante.objects.filter(usuario=usuario).first()
        if est:
            context.update(
                {
                    "rol_actual": "estudiante",
                    "estudiante_form": EstudianteForm(instance=est),
                }
            )
            # Buscar el acudiente real a través del vínculo Estudianteacudiente
            vinculo = Estudianteacudiente.objects.filter(estudianteId=est).select_related(
                "acudienteId__usuario"
            ).first()
            if vinculo:
                acu = vinculo.acudienteId
                context.update({
                    "acudiente_form": AcudienteReadOnlyForm(initial={
                        "nombre_acudiente": acu.usuario.nombre,
                        "email_acudiente": acu.usuario.email,
                        "telefono": acu.telefono or "",
                        "direccion": acu.direccion or "",
                    }),
                    "acudiente_readonly": True,
                })
            else:
                context.update({"acudiente_form": AcudienteForm()})

        return context

    def form_valid(self, form):
        usuario = form.save()
        nuevo_rol = self.request.POST.get("rol")

        # Buscar qué perfil tiene actualmente el usuario
        p_admin = Administrador.objects.filter(usuario=usuario).first()
        p_doc = docente.objects.filter(usuario=usuario).first()
        p_est = Estudiante.objects.filter(usuario=usuario).first()
        p_acu = Acudiente.objects.filter(usuario=usuario).first()

        perfil_previo = p_admin or p_doc or p_est or p_acu

        # Identificar la instancia que coincide con el rol seleccionado
        instancia_a_validar = None
        if nuevo_rol == "administrador":
            instancia_a_validar = p_admin
        elif nuevo_rol == "docente":
            instancia_a_validar = p_doc
        elif nuevo_rol == "estudiante":
            instancia_a_validar = p_est

        # Validar pasando la instancia para que Django sepa que es una EDICIÓN
        valido, rol_form = validar_formulario_rol(
            nuevo_rol, self.request.POST, instance=instancia_a_validar
        )

        if not valido:
            messages.error(self.request, "Errores en los campos del perfil.")
            return self.render_to_response(self.get_context_data(form=form))

        # Lógica de guardado
        if perfil_previo and instancia_a_validar is None:
            perfil_previo.delete()
            guardar_perfil_rol(usuario, nuevo_rol, self.request.POST)
        else:
            obj = rol_form.save(commit=False)
            obj.usuario = usuario
            obj.save()

            # Si es estudiante, actualizar o crear el acudiente también
            if nuevo_rol == "estudiante":
                acu_form = AcudienteForm(self.request.POST, instance=p_acu)
                if acu_form.is_valid():
                    acu = acu_form.save(commit=False)
                    # Si es un acudiente existente, mantener su usuario original
                    # Si es nuevo, crear el usuario del acudiente
                    if not p_acu:
                        # Crear nuevo usuario para el acudiente
                        usuario_acu = Usuario.objects.create(
                            email=acu_form.cleaned_data.get("email_acudiente"),
                            nombre=acu_form.cleaned_data.get("nombre_acudiente"),
                            estado=True,
                        )
                        usuario_acu.set_unusable_password()
                        usuario_acu.save()
                        acu.usuario = usuario_acu
                        asignar_grupo(usuario_acu, "acudiente")
                    # Si p_acu existe, NO sobrescribir acu.usuario (ya tiene su usuario asignado)
                    acu.save()
                    # Asegurar vínculo en la tabla intermedia
                    est = Estudiante.objects.get(usuario=usuario)
                    Estudianteacudiente.objects.get_or_create(
                        estudianteId=est, acudienteId=acu
                    )
        asignar_grupo(usuario, nuevo_rol)
        messages.success(self.request, "Usuario actualizado correctamente")
        return redirect(self.success_url)


class UsuarioDetailView(View):
    def get(self, request, pk):
        usuario = Usuario.objects.get(pk=pk)

        data = {
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": str(usuario.get_rol()),
            "estado": "Activo" if usuario.estado else "Inactivo",
            "fecha_creacion": usuario.fecha_creacion,
        }

        return JsonResponse(data)


class UsuarioCleandView(View):
    def post(self, request, *args, **kwargs):
        Usuario.objects.all().delete()
        with connection.cursor() as cursor:
            nombre_tabla = Usuario._meta.db_table
            cursor.execute(f"ALTER TABLE {nombre_tabla} auto_increment = 1;")

        messages.success(
            self.request, "Todos los Usuarios han sido eliminados y el ID reiniciado."
        )
        return redirect(reverse_lazy("app:index_usuario"))


class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = "usuario/eliminar.html"
    success_url = reverse_lazy("app:index_usuario")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Eliminar Usuario"
        context["subtitulo"] = "¿Está seguro de eliminar este usuario?"
        context["listar_url"] = reverse_lazy("app:index_usuario")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Usuario eliminado exitosamente.")
        return super().form_valid(form)


class PerfilView(LoginRequiredMixin, View):
    template_name = "modals/perfil.html"

    def handle_no_permission(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":

            return JsonResponse({"redirect": "/login/"}, status=401)
        return redirect("/login/?next=" + self.request.path)

    def get(self, request):
        return render(request, self.template_name, {"user": request.user})

    def post(self, request):
        usuario = request.user
        errores = []

        nombre = request.POST.get("nombre", "").strip()
        print("nombre", nombre)
        if nombre:
            usuario.nombre = nombre
            print("nombre recibido", usuario.nombre)
        else:
            errores.append("El nombre no puede estar vacío.")
        if "img_usuario" in request.FILES:
            foto = request.FILES["img_usuario"]
            tipos_permitidos = ["image/jpeg", "image/png", "image/webp"]
            if foto.content_type not in tipos_permitidos:
                errores.append("Solo se permiten imágenes JPG, PNG o WEBP.")
            elif foto.size > 5 * 1024 * 1024:
                errores.append("La imagen no puede superar 5MB.")
            else:
                usuario.img_usuario = foto

        password = request.POST.get("password", "").strip()
        if password:
            if len(password) < 8:
                errores.append("La contraseña debe tener al menos 8 caracteres.")
            else:
                usuario.set_password(password)

        if errores:
            return JsonResponse({"success": False, "message": " ".join(errores)})

        try:
            usuario.save()
            if password and len(password) >= 8:
                update_session_auth_hash(request, usuario)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Perfil actualizado correctamente.",
                    "nombre": usuario.nombre,
                }
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": "Error al guardar los cambios."}
            )


from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, get_object_or_404, redirect
from collections import defaultdict

User = get_user_model()


class DescargarQRView(LoginRequiredMixin, View):
    def get(self, request, estudiante_id):

        if not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para descargar códigos QR.")
            return redirect("app:index_usuario")
        
        estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
        
        if not estudiante.qr:
            messages.error(request, "El estudiante no tiene código QR generado.")
            return redirect("app:index_usuario")
        
        ruta_archivo = estudiante.qr.path
        with open(ruta_archivo, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            nombre_archivo = f"QR_{estudiante.usuario.nombre.replace(' ', '_')}.png"
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response


class GestionPermisosUsuarioView(View):
    template_name = "usuario/permisos_usuario.html"

    def get(self, request, user_id):
        usuario = get_object_or_404(User, id=user_id)
        
        # 1. Traemos los grupos con sus permisos optimizados
        grupos = Group.objects.prefetch_related("permissions").all()
        
        # 2. Construimos el mapa de permisos POR FUERA del bucle de permisos individuales
        grupos_permisos_map = {
            grupo.id: list(grupo.permissions.values_list("id", flat=True))
            for grupo in grupos
        }
        
        # 3. Traemos permisos optimizando el ContentType para evitar queries N+1
        permisos = Permission.objects.select_related("content_type").order_by("content_type__model", "name")
        
        permisos_por_modelo = defaultdict(list)
        for p in permisos:
            permisos_por_modelo[p.content_type.model].append(p)
        
        # 4. Optimizamos las búsquedas de los actuales convirtiendo a listas de inmediato
        grupos_actuales = list(usuario.groups.values_list("id", flat=True))
        permisos_actuales = list(usuario.user_permissions.values_list("id", flat=True))

        return render(
            request,
            self.template_name,
            {
                "usuario": usuario,
                "grupos": grupos,
                "permisos_por_modelo": dict(permisos_por_modelo),
                "grupos_actuales": grupos_actuales,
                "permisos_actuales": permisos_actuales,
                "grupos_permisos_map": grupos_permisos_map,
            },
        )

    def post(self, request, user_id):
        usuario = get_object_or_404(User, id=user_id)
        

        grupos_ids = [int(g) for g in request.POST.getlist("grupos") if g.isdigit()]
        permisos_ids = [int(p) for p in request.POST.getlist("permisos") if p.isdigit()]
        

        usuario.groups.set(grupos_ids)
        usuario.user_permissions.set(permisos_ids)


        for attr in ("_perm_cache", "_user_perm_cache", "_group_perm_cache"):
            if hasattr(usuario, attr):
                delattr(usuario, attr)

  
        messages.success(request, f"Permisos actualizados correctamente para {usuario.nombre}.")

        return redirect("app:index_usuario")