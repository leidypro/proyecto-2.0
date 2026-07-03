"""
Script de seeding de datos realistas para el sistema de gestión escolar.
Genera datos de prueba coherentes con el dominio educativo.
"""
from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from app.models import (
    Usuario, Administrador, docente, Estudiante,
    Curso, Evento, Asistencia, Acudiente,
    Estudianteacudiente, categoria, tipoelemento,
    marca, UnidadMedida, Elemento, Movimiento, Notificacion
)

fake = Faker('es_ES')


# ============================================================================
# CATÁLOGOS DE DATOS REALISTAS
# ============================================================================

ESPECIALIDADES_DOCENTES = [
    "Matemáticas",
    "Español",
    "Ciencias Naturales",
    "Ciencias Sociales",
    "Informática",
    "Inglés",
    "Educación Física",
    "Educación Artística",
    "Filosofía",
    "Química",
    "Física",
    "Biología",
]

CARGOS_ADMINISTRATIVOS = [
    "Rector",
    "Coordinador Académico",
    "Coordinador de Convivencia",
    "Secretario Académico",
    "Director de Grupo",
]

GRADOS_CON_SECCIONES = {
    "Preescolar": ["A", "B"],
    "1": ["A", "B"],
    "2": ["A", "B"],
    "3": ["A", "B"],
    "4": ["A", "B"],
    "5": ["A", "B"],
    "6": ["A", "B"],
    "7": ["A", "B"],
    "8": ["A", "B"],
    "9": ["A", "B"],
    "10": ["A", "B"],
    "11": ["A", "B"],
}

EVENTOS_INSTITUCIONALES = [
    {
        "titulo": "Entrega de Boletines",
        "descripcion": "Reunión de entrega de boletines académicos del periodo. "
                       "Los padres de familia deben asistir para revisar el rendimiento académico de sus hijos."
    },
    {
        "titulo": "Reunión de Padres",
        "descripcion": "Reunión general de padres de familia para tratar temas de convivencia "
                       "y procesos académicos del periodo."
    },
    {
        "titulo": "Semana Cultural",
        "descripcion": "Semana dedicada a actividades culturales: teatro, música, danza y exposiciones "
                       "artísticas de los estudiantes."
    },
    {
        "titulo": "Feria de Ciencias",
        "descripcion": "Feria anual de proyectos científicos y tecnológicos desarrollados por los estudiantes "
                       "de todos los grados."
    },
    {
        "titulo": "Jornada Deportiva",
        "descripcion": "Competencias deportivas intergrupales: fútbol, baloncesto, voleibol y atletismo."
    },
    {
        "titulo": "Izada de Bandera",
        "descripcion": "Ceremonia de izada de bandera con conmemoración de fecha especial. "
                       "Estudiantes preparan presentación cultural."
    },
    {
        "titulo": "Clausura Académica",
        "descripcion": "Ceremonia de clausura del año académico. Entrega de diplomas y reconocimientos "
                       "a estudiantes destacados."
    },
    {
        "titulo": "Actividad de Bienestar Estudiantil",
        "descripcion": "Jornada de actividades recreativas y de integración para promover el bienestar "
                       "emocional y social de los estudiantes."
    },
    {
        "titulo": "Día de la Familia",
        "descripcion": "Actividad especial donde los padres participan en actividades educativas y "
                       "recreativas con sus hijos en la institución."
    },
    {
        "titulo": "Olimpiadas Matemáticas",
        "descripcion": "Competencia académica de matemáticas donde los estudiantes demuestran sus "
                       "habilidades en resolución de problemas."
    },
]

CATEGORIAS_INVENTARIO = {
    "Tecnología": {
        "tipos": ["Equipo", "Periférico", "Componente"],
        "elementos": [
            ("Computador de escritorio", "Computador de escritorio para sala de sistemas", ["HP", "Dell", "Lenovo"]),
            ("Portátil", "Portátil para uso educativo", ["HP", "Dell", "Lenovo", "Asus"]),
            ("Mouse", "Mouse óptico USB", ["Logitech", "Genius", "HP"]),
            ("Teclado", "Teclado estándar USB", ["Logitech", "Genius", "HP"]),
            ("Impresora", "Impresora multifuncional", ["Epson", "HP", "Canon"]),
            ("Video Beam", "Proyector de video para aulas", ["Epson", "Optoma", "ViewSonic"]),
            ("Tablet", "Tablet educativa", ["Samsung", "Apple", "Lenovo"]),
        ]
    },
    "Mobiliario": {
        "tipos": ["Mueble", "Silla", "Equipo"],
        "elementos": [
            ("Pupitre", "Pupitre individual para estudiante", ["Sin marca", "Sin marca", "Sin marca"]),
            ("Silla de aula", "Silla ergonómica para estudiantes", ["Sin marca", "Sin marca", "Sin marca"]),
            ("Escritorio docente", "Escritorio para docente con cajones", ["Sin marca", "Sin marca", "Sin marca"]),
            ("Archivador", "Archivador metálico de 4 gavetas", ["Sin marca", "Sin marca", "Sin marca"]),
            ("Mesa de laboratorio", "Mesa para prácticas de laboratorio", ["Sin marca", "Sin marca", "Sin marca"]),
        ]
    },
    "Útiles Escolares": {
        "tipos": ["Papelería", "Escritura", "Arte"],
        "elementos": [
            ("Cuaderno", "Cuaderno universitario 100 hojas", ["Norma", "Scribe", "Offset"]),
            ("Lápiz", "Lápiz grafito #2", ["Faber Castell", "Pelikan", "Maped"]),
            ("Borrador", "Borrador de nata", ["Faber Castell", "Pelikan", "Maped"]),
            ("Regla", "Regla de 30 cm", ["Faber Castell", "Maped", "Norma"]),
            ("Marcador", "Marcador permanente", ["Sharpie", "Norma", "Pelikan"]),
            ("Corrector", "Corrector líquido", ["Pelikan", "Norma", "Maped"]),
            ("Lápiz de colores", "Caja de 12 lápices de colores", ["Faber Castell", "Prismacolor", "Maped"]),
            ("Resaltador", "Resaltador de texto", ["Faber Castell", "Sharpie", "Pelikan"]),
        ]
    },
    "Material Didáctico": {
        "tipos": ["Didáctico", "Equipo", "Material"],
        "elementos": [
            ("Globo Terráqueo", "Globo terráqueo físico de 30 cm", ["National Geographic", "Otros", "Otros"]),
            ("Mapa de Colombia", "Mapa político de Colombia", ["Instituto Geográfico", "Otros", "Otros"]),
            ("Ábaco", "Ábaco educativo para matemáticas", ["Otros", "Otros", "Otros"]),
            ("Kit de Ciencias", "Kit de experimentos científicos", ["Otros", "Otros", "Otros"]),
            ("Reloj didáctico", "Reloj para enseñanza de las horas", ["Otros", "Otros", "Otros"]),
            ("Rompecabezas", "Rompecabezas educativo de 100 piezas", ["Otros", "Otros", "Otros"]),
        ]
    },
    "Aseo": {
        "tipos": ["Limpieza", "Desinfección", "Papelería"],
        "elementos": [
            ("Escoba", "Escoba de cerdas duras", ["Klin", "Ace", "Otros"]),
            ("Trapero", "Trapero de microfibra", ["Klin", "Ace", "Otros"]),
            ("Desinfectante", "Desinfectante de superficies 1L", ["Ace", "Klin", "Mr. Clean"]),
            ("Jabón Líquido", "Jabón líquido para manos 1L", ["Dove", "Protex", "Otros"]),
            ("Papel Higiénico", "Paquete de papel higiénico x4", ["Familia", "Tender", "Otros"]),
            ("Detergente", "Detergente en polvo para ropa", ["Ariel", "Fab", "Otros"]),
        ]
    },
}

MARCAS_POR_TIPO = {
    "Tecnología": ["HP", "Dell", "Lenovo", "Epson", "Logitech", "Samsung", "Asus"],
    "Mobiliario": ["Sin marca", "RTA", "Forma", "Office"],
    "Papelería": ["Norma", "Faber Castell", "Pelikan", "Maped", "Scribe"],
    "Limpieza": ["Ace", "Klin", "Ariel", "Fab", "Familia"],
    "Didáctico": ["National Geographic", "Instituto Geográfico", "Otros"],
}

UNIDADES_MEDIDA = ["Unidad", "Caja", "Paquete", "Litro", "Metro", "Kilogramo", "Set", "Par"]

UBICACIONES_COLEGIO = [
    "Bodega Principal",
    "Biblioteca",
    "Sala de Sistemas",
    "Coordinación Académica",
    "Secretaría",
    "Salón de Clase 101",
    "Salón de Clase 102",
    "Salón de Clase 103",
    "Laboratorio de Ciencias",
    "Auditorio",
]

TIPOS_MOVIMIENTO = ["Entrada", "Salida"]

ESTADOS_ASISTENCIA = ["A tiempo", "Tarde", "Inasistencia"]

TIPOS_NOTIFICACION = [
    "Nuevo evento programado",
    "Asistencia registrada",
    "Stock mínimo alcanzado",
    "Nueva matrícula registrada",
    "Recordatorio de reunión",
    "Cambio de horario",
    "Entrega de boletines",
    "Actividad extracurricular",
]


class Command(BaseCommand):
    help = 'Generar datos de prueba realistas para el sistema de gestión escolar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos antes de generar nuevos',
        )
        parser.add_argument(
            '--cantidad',
            type=int,
            default=1,
            help='Cantidad de veces a repetir el patrón de datos (default: 1)',
        )

    def handle(self, *args, **kwargs):
        clear_data = kwargs.get('clear', False)
        repeticiones = kwargs.get('cantidad', 1)

        if clear_data:
            self.stdout.write("Limpiando base de datos...")
            self.clear_database()
            self.stdout.write(self.style.SUCCESS("Base de datos limpiada\n"))

        self.stdout.write("Generando datos de prueba realistas...\n")

        for i in range(repeticiones):
            if repeticiones > 1:
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(f"Generando conjunto {i+1} de {repeticiones}")
                self.stdout.write(f"{'='*60}\n")
            
            self.generar_datos()

        self.stdout.write(self.style.SUCCESS("\n✓ Datos generados correctamente"))

    def generar_datos(self):
        """Método principal que orquesta la generación de datos"""
        
        # =========================
        # 0. CREAR GRUPOS SI NO EXISTEN
        # =========================
        self.stdout.write("0. Verificando grupos de usuarios...")
        rol_admin, _ = Group.objects.get_or_create(name="Administrador")
        rol_docente, _ = Group.objects.get_or_create(name="Docente")
        rol_estudiante, _ = Group.objects.get_or_create(name="Estudiante")
        rol_acudiente, _ = Group.objects.get_or_create(name="Acudiente")

        # =========================
        # 1. USUARIOS BASE
        # =========================
        self.stdout.write("1. Creando usuarios base...")
        usuarios = self.crear_usuarios(30)

        # =========================
        # 2. ADMINISTRADORES
        # =========================
        self.stdout.write("2. Creando administradores...")
        admins = self.crear_administradores(usuarios[:5], rol_admin)

        # =========================
        # 3. DOCENTES
        # =========================
        self.stdout.write("3. Creando docentes...")
        docentes = self.crear_docentes(usuarios[5:15], rol_docente)

        # =========================
        # 4. CURSOS
        # =========================
        self.stdout.write("4. Creando cursos...")
        cursos = self.crear_cursos(docentes)

        # =========================
        # 5. ESTUDIANTES
        # =========================
        self.stdout.write("5. Creando estudiantes...")
        estudiantes = self.crear_estudiantes(usuarios[15:30], rol_estudiante, cursos)

        # =========================
        # 6. EVENTOS
        # =========================
        self.stdout.write("6. Creando eventos institucionales...")
        eventos = self.crear_eventos(admins)

        # =========================
        # 7. ASISTENCIAS
        # =========================
        self.stdout.write("7. Creando registros de asistencia...")
        self.crear_asistencias(estudiantes)

        # =========================
        # 8. ACUDIENTES
        # =========================
        self.stdout.write("8. Creando acudientes...")
        acudientes = self.crear_acudientes(rol_acudiente)

        # RELACIÓN ESTUDIANTE-ACUDIENTE
        self.crear_relaciones_estudiante_acudiente(estudiantes, acudientes)

        # =========================
        # 9. INVENTARIO
        # =========================
        self.stdout.write("9. Creando inventario...")
        elementos = self.crear_inventario()

        # =========================
        # 10. MOVIMIENTOS
        # =========================
        self.stdout.write("10. Creando movimientos de inventario...")
        self.crear_movimientos(elementos, usuarios, cursos)

        # =========================
        # 11. NOTIFICACIONES
        # =========================
        self.stdout.write("11. Creando notificaciones...")
        self.crear_notificaciones(usuarios, eventos, estudiantes, elementos)

        # Resumen
        self.mostrar_resumen(usuarios, admins, docentes, cursos, estudiantes, 
                            eventos, acudientes, elementos)

    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================

    def crear_usuarios(self, cantidad):
        """Crea usuarios base con datos realistas"""
        usuarios = []
        nombres_generados = set()
        
        for _ in range(cantidad):
            # Generar nombre único
            while True:
                nombre = fake.name()
                if nombre not in nombres_generados:
                    nombres_generados.add(nombre)
                    break
            
            user = Usuario.objects.create(
                email=fake.unique.email(),
                nombre=nombre,
                estado=True
            )
            user.set_password("123456")
            user.save()
            usuarios.append(user)
        
        return usuarios

    def crear_administradores(self, usuarios, rol):
        """Crea administradores con cargos realistas"""
        admins = []
        cargos_usados = []
        
        for user in usuarios:
            # Asignar cargo único
            cargo = random.choice([c for c in CARGOS_ADMINISTRATIVOS if c not in cargos_usados])
            cargos_usados.append(cargo)
            
            admin = Administrador.objects.create(
                usuario=user,
                cargo=cargo
            )
            user.groups.add(rol)
            admins.append(admin)
        
        return admins

    def crear_docentes(self, usuarios, rol):
        """Crea docentes con especialidades realistas del sistema educativo"""
        docentes = []
        especialidades_usadas = []
        
        for user in usuarios:
            # Asignar especialidad (permitir repeticiones pero priorizar variedad)
            if especialidades_usadas:
                especialidad = random.choice(ESPECIALIDADES_DOCENTES)
            else:
                especialidad = random.choice(ESPECIALIDADES_DOCENTES)
            especialidades_usadas.append(especialidad)
            
            doc = docente.objects.create(
                usuario=user,
                especialidad=especialidad
            )
            user.groups.add(rol)
            docentes.append(doc)
        
        return docentes

    def crear_cursos(self, docentes):
        """Crea cursos con grados y secciones coherentes"""
        cursos = []
        codigos_usados = set()
        
        for grado, secciones in GRADOS_CON_SECCIONES.items():
            for seccion in secciones:
                # Generar código único
                while True:
                    codigo = f"CUR-{grado}-{seccion}"
                    if codigo not in codigos_usados:
                        codigos_usados.add(codigo)
                        break
                
                curso = Curso.objects.create(
                    grado=grado,
                    codigo=codigo,
                    capacidad=random.randint(25, 35),
                    docenteid=random.choice(docentes)
                )
                cursos.append(curso)
        
        return cursos

    def crear_estudiantes(self, usuarios, rol, cursos):
        """Crea estudiantes con edades coherentes según el grado"""
        estudiantes = []
        
        # Mapeo de edades por grado
        edades_por_grado = {
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
        
        for user in usuarios:
            # Seleccionar curso
            curso = random.choice(cursos)
            
            # Calcular fecha de nacimiento según el grado
            edad_min, edad_max = edades_por_grado[curso.grado]
            fecha_nacimiento = fake.date_of_birth(minimum_age=edad_min, maximum_age=edad_max)
            
            est = Estudiante.objects.create(
                usuario=user,
                fechaNacimiento=fecha_nacimiento,
                estadoMatricula="Matriculado",
                fechaIngreso=fake.date_this_decade(),
                cursoId=curso
            )
            user.groups.add(rol)
            estudiantes.append(est)
        
        return estudiantes

    def crear_eventos(self, admins):
        """Crea eventos institucionales realistas"""
        eventos = []
        
        # Seleccionar eventos aleatorios del catálogo
        eventos_seleccionados = random.sample(
            EVENTOS_INSTITUCIONALES, 
            min(len(EVENTOS_INSTITUCIONALES), 8)
        )
        
        for evento_data in eventos_seleccionados:
            # Generar fecha en el próximo mes
            fecha_base = timezone.now() + timedelta(days=random.randint(7, 60))
            fecha_inicio = fecha_base.replace(
                hour=random.randint(8, 14),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )
            fecha_fin = fecha_inicio + timedelta(hours=random.randint(2, 4))
            
            # Asegurar que las fechas sean timezone-aware
            fecha_inicio = timezone.make_aware(fecha_inicio) if timezone.is_naive(fecha_inicio) else fecha_inicio
            fecha_fin = timezone.make_aware(fecha_fin) if timezone.is_naive(fecha_fin) else fecha_fin
            
            evento = Evento.objects.create(
                titulo=evento_data["titulo"],
                descripcion=evento_data["descripcion"],
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                creador_por=random.choice(admins)
            )
            eventos.append(evento)
        
        return eventos

    def crear_asistencias(self, estudiantes):
        """Crea registros de asistencia realistas"""
        for est in estudiantes:
            # Generar 10 registros de asistencia por estudiante
            for _ in range(10):
                # Generar fecha en los últimos 30 días
                fecha = timezone.now() - timedelta(days=random.randint(0, 30))
                
                # Hora de entrada realista (7:00 AM - 8:30 AM)
                hora_entrada = datetime.strptime(
                    f"{random.randint(7, 8)}:{random.randint(0, 59)}:00",
                    "%H:%M:%S"
                ).time()
                
                # Hora de salida (posterior a entrada, entre 12:00 PM y 4:00 PM)
                hora_salida = datetime.strptime(
                    f"{random.randint(12, 16)}:{random.randint(0, 59)}:00",
                    "%H:%M:%S"
                ).time()
                
                # Determinar estado de asistencia
                estado = random.choices(
                    ESTADOS_ASISTENCIA,
                    weights=[70, 20, 10],  # 70% a tiempo, 20% tarde, 10% inasistencia
                    k=1
                )[0]
                
                # Si es inasistencia, no hay hora de salida
                if estado == "Inasistencia":
                    hora_salida = None
                
                Asistencia.objects.create(
                    estudianteid=est,
                    fecha=fecha,
                    horaentrada=hora_entrada,
                    horasalida=hora_salida,
                    estado=estado,
                    observaciones=fake.text(max_nb_chars=100) if estado != "A tiempo" else ""
                )

    def crear_acudientes(self, rol):
        """Crea acudientes con datos de contacto realistas"""
        acudientes = []
        
        for i in range(10):
            user = Usuario.objects.create(
                email=fake.unique.email(),
                nombre=fake.name(),
                estado=True
            )
            user.set_password("123456")
            user.save()
            user.groups.add(rol)

            acu = Acudiente.objects.create(
                usuario=user,
                telefono=f"3{random.randint(10, 99)}{random.randint(1000000, 9999999)}"[:10],
                direccion=fake.address().replace('\n', ', ')[:150]
            )
            acudientes.append(acu)
        
        return acudientes

    def crear_relaciones_estudiante_acudiente(self, estudiantes, acudientes):
        """Crea relaciones entre estudiantes y acudientes"""
        for est in estudiantes:
            # Cada estudiante tiene al menos un acudiente
            Estudianteacudiente.objects.create(
                estudianteId=est,
                acudienteId=random.choice(acudientes)
            )

    def crear_inventario(self):
        """Crea inventario con categorías, tipos, elementos y marcas coherentes"""
        
        # Crear unidades de medida
        unidades = []
        for nombre in UNIDADES_MEDIDA:
            unidad, _ = UnidadMedida.objects.get_or_create(nombre=nombre)
            unidades.append(unidad)
        
        # Crear categorías, tipos y marcas
        categorias_dict = {}
        tipos_dict = {}
        marcas_instancias_dict = {}  # Diccionario de instancias de marca por categoría
        
        for nombre_cat, datos_cat in CATEGORIAS_INVENTARIO.items():
            # Crear categoría
            cat, _ = categoria.objects.get_or_create(nombre=nombre_cat)
            categorias_dict[nombre_cat] = cat
            
            # Crear tipos para esta categoría
            tipos_list = []
            for nombre_tipo in datos_cat["tipos"]:
                tipo, _ = tipoelemento.objects.get_or_create(nombre=nombre_tipo)
                tipos_list.append(tipo)
            tipos_dict[nombre_cat] = tipos_list
            
            # Crear marcas para esta categoría (como instancias del modelo)
            marcas_instancias_list = []
            for nombre_marca in MARCAS_POR_TIPO.get(nombre_cat, ["Otros"]):
                marca_obj, _ = marca.objects.get_or_create(nombre=nombre_marca)
                marcas_instancias_list.append(marca_obj)
            marcas_instancias_dict[nombre_cat] = marcas_instancias_list
        
        # Crear elementos
        elementos = []
        for nombre_cat, datos_cat in CATEGORIAS_INVENTARIO.items():
            cat = categorias_dict[nombre_cat]
            tipos_cat = tipos_dict[nombre_cat]
            marcas_cat = marcas_instancias_dict[nombre_cat]  # Usar instancias, no strings
            
            for nombre_elem, descripcion, nombres_marcas_elem in datos_cat["elementos"]:
                # Seleccionar tipo aleatorio de la categoría
                tipo = random.choice(tipos_cat)
                
                # Seleccionar marca de las disponibles para este elemento
                # Buscar la instancia de marca que coincida con el nombre
                marca_elem = None
                for nombre_marca in nombres_marcas_elem:
                    for marca_inst in marcas_cat:
                        if marca_inst.nombre == nombre_marca:
                            marca_elem = marca_inst
                            break
                    if marca_elem:
                        break
                
                # Si no se encontró, usar una marca aleatoria de la categoría
                if not marca_elem:
                    marca_elem = random.choice(marcas_cat)
                
                # Seleccionar unidad de medida apropiada
                if "Litro" in nombre_elem or "Jabón" in nombre_elem or "Desinfectante" in nombre_elem:
                    unidad = UnidadMedida.objects.get(nombre="Litro")
                elif "Paquete" in nombre_elem or "Caja" in nombre_elem:
                    unidad = UnidadMedida.objects.get(nombre="Caja")
                elif "Metro" in nombre_elem:
                    unidad = UnidadMedida.objects.get(nombre="Metro")
                elif "Kilogramo" in nombre_elem:
                    unidad = UnidadMedida.objects.get(nombre="Kilogramo")
                else:
                    unidad = random.choice(unidades)
                
                elem = Elemento.objects.create(
                    nombre=nombre_elem,
                    descripcion=descripcion,
                    stockActual=random.randint(5, 50),
                    stockMinimo=random.randint(2, 10),
                    tipoElementoId=tipo,
                    categoriaId=cat,
                    marcaId=marca_elem,
                    unidadMedidaId=unidad,
                    ubicacion=random.choice(UBICACIONES_COLEGIO)
                )
                elementos.append(elem)
        
        return elementos

    def crear_movimientos(self, elementos, usuarios, cursos):
        """Crea movimientos de inventario realistas"""
        for _ in range(30):
            elemento = random.choice(elementos)
            
            # Determinar tipo de movimiento
            tipo = random.choice(TIPOS_MOVIMIENTO)
            
            # La cantidad no puede exceder el stock actual para salidas
            if tipo == "Salida":
                cantidad = random.randint(1, min(10, elemento.stockActual))
            else:
                cantidad = random.randint(1, 20)
            
            # Motivo realista según el tipo
            if tipo == "Entrada":
                motivos_entrada = [
                    "Compra de dotación escolar",
                    "Donación de materiales",
                    "Reposición de inventario",
                    "Adquisición para nuevo periodo académico",
                ]
                motivo = random.choice(motivos_entrada)
            else:
                motivos_salida = [
                    f"Asignación a {random.choice(cursos).codigo}",
                    "Uso en aula de clase",
                    "Préstamo para actividad especial",
                    "Mantenimiento preventivo",
                ]
                motivo = random.choice(motivos_salida)
            
            Movimiento.objects.create(
                tipo=tipo,
                cantidad=cantidad,
                elementoId=elemento,
                usuarioId=random.choice(usuarios),
                cursoId=random.choice(cursos),
                motivo=motivo
            )

    def crear_notificaciones(self, usuarios, eventos, estudiantes, elementos):
        """Crea notificaciones relacionadas con procesos reales"""
        
        for _ in range(20):
            tipo_notif = random.choice(TIPOS_NOTIFICACION)
            receptor = random.choice(usuarios)
            
            # Generar contenido según el tipo
            if tipo_notif == "Nuevo evento programado":
                titulo = f"Nuevo evento: {random.choice(eventos).titulo}"
                mensaje = fake.text(max_nb_chars=150)
                evento_rel = random.choice(eventos)
            
            elif tipo_notif == "Asistencia registrada":
                estudiante = random.choice(estudiantes)
                titulo = f"Asistencia registrada - {estudiante.usuario.nombre}"
                mensaje = f"Se ha registrado la asistencia del estudiante {estudiante.usuario.nombre} del curso {estudiante.cursoId.codigo}."
                evento_rel = None
            
            elif tipo_notif == "Stock mínimo alcanzado":
                elemento = random.choice(elementos)
                titulo = f"Alerta de stock: {elemento.nombre}"
                mensaje = f"El elemento {elemento.nombre} ha alcanzado el stock mínimo. "
                mensaje += f"Stock actual: {elemento.stockActual}, Stock mínimo: {elemento.stockMinimo}."
                evento_rel = None
            
            elif tipo_notif == "Nueva matrícula registrada":
                estudiante = random.choice(estudiantes)
                titulo = "Nueva matrícula registrada"
                mensaje = f"Se ha registrado la matrícula de {estudiante.usuario.nombre} en el curso {estudiante.cursoId.codigo}."
                evento_rel = None
            
            elif tipo_notif == "Recordatorio de reunión":
                titulo = "Recordatorio: Reunión de padres"
                mensaje = "Se recuerda la reunión de padres programada para esta semana. "
                mensaje += "Por favor confirmar asistencia."
                evento_rel = random.choice(eventos) if eventos else None
            
            elif tipo_notif == "Cambio de horario":
                titulo = "Cambio de horario"
                mensaje = "Se ha realizado un cambio en el horario de clases. "
                mensaje += "Consulte la nueva programación."
                evento_rel = None
            
            elif tipo_notif == "Entrega de boletines":
                titulo = "Entrega de boletines"
                mensaje = "Se informa que la entrega de boletines del periodo se realizará la próxima semana."
                evento_rel = random.choice(eventos) if eventos else None
            
            else:  # Actividad extracurricular
                titulo = "Nueva actividad extracurricular"
                mensaje = "Se ha programado una nueva actividad extracurricular. "
                mensaje += "Inscríbase en coordinación."
                evento_rel = None
            
            Notificacion.objects.create(
                titulo=titulo,
                mensaje=mensaje,
                estado=random.choice(["no_leida", "leida"]),
                tipo=random.choice(["aviso", "actualizacion", "urgente"]),
                receptor=receptor,
                evento=evento_rel
            )

    def mostrar_resumen(self, usuarios, admins, docentes, cursos, estudiantes, 
                       eventos, acudientes, elementos):
        """Muestra resumen de datos generados"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("RESUMEN DE DATOS GENERADOS"))
        self.stdout.write("="*60)
        self.stdout.write(f"  Usuarios totales:           {len(usuarios)}")
        self.stdout.write(f"  - Administradores:          {len(admins)}")
        self.stdout.write(f"  - Docentes:                 {len(docentes)}")
        self.stdout.write(f"  - Estudiantes:              {len(estudiantes)}")
        self.stdout.write(f"  - Acudientes:               {len(acudientes)}")
        self.stdout.write(f"  Cursos:                     {len(cursos)}")
        self.stdout.write(f"  Eventos:                    {len(eventos)}")
        self.stdout.write(f"  Elementos de inventario:    {len(elementos)}")
        self.stdout.write(f"  Asistencias:                {len(estudiantes) * 10}")
        self.stdout.write(f"  Movimientos:                30")
        self.stdout.write(f"  Notificaciones:             20")
        self.stdout.write(f"  Relaciones Est-Acu:         {len(estudiantes)}")
        self.stdout.write("="*60 + "\n")

    def clear_database(self):
        """Elimina todos los datos de las tablas en el orden correcto"""
        self.stdout.write("Eliminando datos existentes...")
        
        # Eliminar en orden inverso por las dependencias de claves foráneas
        Notificacion.objects.all().delete()
        Movimiento.objects.all().delete()
        Asistencia.objects.all().delete()
        Estudianteacudiente.objects.all().delete()
        Estudiante.objects.all().delete()
        Acudiente.objects.all().delete()
        Evento.objects.all().delete()
        Elemento.objects.all().delete()
        UnidadMedida.objects.all().delete()
        marca.objects.all().delete()
        tipoelemento.objects.all().delete()
        categoria.objects.all().delete()
        Curso.objects.all().delete()
        docente.objects.all().delete()
        Administrador.objects.all().delete()
        
        # Eliminar usuarios (excepto superusuarios)
        Usuario.objects.filter(is_superuser=False).delete()