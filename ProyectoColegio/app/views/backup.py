import os
import shutil
import platform
import subprocess

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


# =========================================================
# OBTENER CREDENCIALES MYSQL (MULTIPLATAFORMA)
# =========================================================
def obtener_credenciales_mysql():
    """
    Detecta automáticamente el sistema operativo
    y configura la ruta de MySQL.
    """

    db_config = settings.DATABASES['default']
    sistema = platform.system()

    creds = {
    'host': db_config.get('HOST') or '127.0.0.1',
    'user': db_config.get('USER') or 'root',
    'password': db_config.get('PASSWORD') or '',
    'database': db_config.get('NAME') or 'colegio_db',
    'port': db_config.get('PORT') or 3306,
    }

    # ================= WINDOWS =================
    if sistema == "Windows":

        rutas_posibles = [
            r'C:\Program Files\MySQL\MySQL Server 8.0\bin',
            r'C:\Program Files\MySQL\MySQL Server 8.4\bin',
            r'C:\xampp\mysql\bin'
        ]

        mysql_path = next(
            (ruta for ruta in rutas_posibles if os.path.exists(ruta)),
            None
        )

        if mysql_path:
            creds['mysql_path'] = mysql_path
        else:
            creds['mysql_path'] = ''

        creds['ext'] = '.exe'

    # ================= LINUX / MAC =================
    else:

        mysql_bin = shutil.which('mysql')

        if mysql_bin:
            creds['mysql_path'] = os.path.dirname(mysql_bin)
        else:
            creds['mysql_path'] = '/usr/bin'

        creds['ext'] = ''

    return creds


# =========================================================
# PROBAR CONEXIÓN MYSQL
# =========================================================
def probar_conexion_mysql():
    """
    Ejecuta un SELECT 1 para validar conexión MySQL.
    """

    creds = obtener_credenciales_mysql()
    print(creds)
    try:

        exe = f"mysql{creds['ext']}"

        mysql_exe = os.path.join(
            creds['mysql_path'],
            exe
        )

        cmd = [
            mysql_exe,
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', str(creds['port']),
        ]

        # Agregar contraseña solo si existe
        if creds['password']:
            cmd.append(f'--password={creds["password"]}')

        cmd.extend([
            '-e',
            'SELECT 1;',
            creds['database']
        ])

        print("Comando conexión:", cmd)

        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if resultado.returncode != 0:
            print("Error MySQL:")
            print(resultado.stderr)
            return False

        return True

    except FileNotFoundError:
        print("No se encontró el ejecutable de MySQL.")
        return False

    except subprocess.TimeoutExpired:
        print("La conexión tardó demasiado.")
        return False

    except Exception as e:
        print("Error general:", e)
        return False


# =========================================================
# VISTA PRINCIPAL
# =========================================================
@require_http_methods(["GET", "POST"])
def backup(request):
    """
    Muestra el panel de respaldo y restauración.
    """

    if request.method == "POST":

        accion = request.POST.get('accion')

        try:

            # ================= RESPALDO COMPLETO =================
            if accion == 'backup_completo':

                if not probar_conexion_mysql():
                    return JsonResponse({
                        'error': 'Error de conexión con MySQL'
                    }, status=400)

                return realizar_respaldo_completo()

        except Exception as e:

            return JsonResponse({
                'error': str(e)
            }, status=400)

    context = {
        'titulo': 'Gestión Base de Datos',
        'mysql_conectado': probar_conexion_mysql(),
    }

    return render(
        request,
        'backup/menu.html',
        context
    )


# =========================================================
# REALIZAR RESPALDO COMPLETO
# =========================================================
def realizar_respaldo_completo():
    """
    Genera respaldo SQL completo.
    """

    creds = obtener_credenciales_mysql()

    try:

        exe = f"mysqldump{creds['ext']}"

        mysqldump_exe = os.path.join(
            creds['mysql_path'],
            exe
        )

        cmd = [
            mysqldump_exe,
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', str(creds['port']),
        ]

        # Contraseña
        if creds['password']:
            cmd.append(f'--password={creds["password"]}')

        cmd.extend([
            '--routines',
            '--triggers',
            '--events',
            '--single-transaction',
            '--quick',
            creds['database']
        ])

        print("Comando backup:", cmd)

        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=60
        )

        if resultado.returncode != 0:
            raise Exception(resultado.stderr)

        header = (
            "-- ======================================\n"
            "-- RESPALDO PROYECTO COLEGIO\n"
            f"-- FECHA: {datetime.now()}\n"
            "-- ======================================\n\n"
        )

        contenido = header + resultado.stdout

        return generar_archivo_descarga(
            contenido,
            'respaldo_colegio'
        )

    except subprocess.TimeoutExpired:
        raise Exception(
            "El respaldo tardó demasiado."
        )

    except FileNotFoundError:
        raise Exception(
            "No se encontró mysqldump."
        )

    except Exception as e:
        raise Exception(
            f"Error generando backup: {str(e)}"
        )


# =========================================================
# RESTAURAR BASE DE DATOS
# =========================================================
@require_http_methods(["POST"])
def restaurar_datos(request):
    """
    Restaura la base de datos desde un archivo SQL.
    """

    if 'archivo' not in request.FILES:

        return JsonResponse({
            'error': 'No se seleccionó archivo'
        }, status=400)

    archivo = request.FILES['archivo']

    # ================= VALIDAR EXTENSIÓN =================
    if not archivo.name.endswith('.sql'):

        return JsonResponse({
            'error': 'El archivo debe ser .sql'
        }, status=400)

    # ================= VALIDAR TAMAÑO =================
    if archivo.size == 0:

        return JsonResponse({
            'error': 'El archivo está vacío'
        }, status=400)

    try:

        contenido_sql = archivo.read().decode('utf-8')

        # ================= VALIDAR CONTENIDO =================
        if not contenido_sql.strip():

            return JsonResponse({
                'error': 'El archivo no contiene SQL válido'
            }, status=400)

        creds = obtener_credenciales_mysql()

        exe = f"mysql{creds['ext']}"

        mysql_exe = os.path.join(
            creds['mysql_path'],
            exe
        )

        cmd = [
            mysql_exe,
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', str(creds['port']),
        ]

        # Contraseña
        if creds['password']:
            cmd.append(f'--password={creds["password"]}')

        cmd.append(creds['database'])

        print("Comando restaurar:", cmd)

        proceso = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = proceso.communicate(
            input=contenido_sql,
            timeout=120
        )

        if proceso.returncode != 0:
            raise Exception(stderr)

        return JsonResponse({
            'exito': True,
            'mensaje': 'Base de datos restaurada correctamente'
        })

    except UnicodeDecodeError:

        return JsonResponse({
            'error': 'El archivo debe estar codificado en UTF-8'
        }, status=400)

    except subprocess.TimeoutExpired:

        return JsonResponse({
            'error': 'La restauración tardó demasiado'
        }, status=400)

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        }, status=400)


# =========================================================
# GENERAR DESCARGA SQL
# =========================================================
def generar_archivo_descarga(contenido, nombre):
    """
    Genera descarga del archivo SQL.
    """

    response = HttpResponse(
        contenido.encode('utf-8'),
        content_type='application/sql'
    )

    fecha = datetime.now().strftime(
        '%Y%m%d_%H%M%S'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; '
        f'filename="{nombre}_{fecha}.sql"'
    )

    return response