import os
import requests
from app.models import *
from openai import OpenAI
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from app.utils import obtener_rutas
import os
import re
import json
import requests

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# ==========================
# CONFIGURACIÓN
# ==========================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_IA = "qwen3:8b"



def cargar_prompt():

    ruta_prompt = os.path.join(
        settings.BASE_DIR,
        "prompt_sistema.txt"
    )

    try:

        with open(
            ruta_prompt,
            "r",
            encoding="utf-8"
        ) as archivo:

            return archivo.read()

    except Exception as e:

        print(
            "Error cargando prompt:",
            e
        )

        return ""


# ==========================
# CARGAR BASE DE CONOCIMIENTO
# ==========================

def cargar_base_conocimiento():

    ruta_md = os.path.join(
        settings.BASE_DIR,
        "base_conocimiento_ia.md"
    )

    try:

        with open(
            ruta_md,
            "r",
            encoding="utf-8"
        ) as archivo:

            return archivo.read()

    except Exception as e:

        print(
            "Error leyendo base conocimiento:",
            e
        )

        return ""


# ==========================
# NORMALIZAR TEXTO
# ==========================

def limpiar_texto(texto):

    texto = texto.lower()

    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto
    )

    return texto


# ==========================
# BÚSQUEDA DE CONTEXTO
# ==========================

def buscar_fragmentos(
    texto,
    consulta,
    max_fragmentos=5
):

    consulta_limpia = limpiar_texto(
        consulta
    )

    palabras = {

        palabra

        for palabra in consulta_limpia.split()

        if len(palabra) > 2

    }

    bloques = texto.split("---")

    resultados = []

    for bloque in bloques:

        contenido = limpiar_texto(
            bloque
        )

        score = 0

        for palabra in palabras:

            if palabra in contenido:
                score += 1

        if score > 0:

            resultados.append(
                (
                    score,
                    bloque.strip()
                )
            )

    resultados.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return "\n\n".join(
        bloque
        for _, bloque in resultados[
            :max_fragmentos
        ]
    )


# ==========================
# CHAT IA
# ==========================

@csrf_exempt
def preguntar_ia_local(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error":
                "Método no permitido"
            },
            status=405
        )

    try:

        data = json.loads(
            request.body
        )

        mensaje = data.get(
            "mensaje",
            ""
        ).strip()

        if not mensaje:

            return JsonResponse(
                {
                    "respuesta":
                    "Debe escribir una pregunta."
                },
                status=400
            )

        prompt_sistema = (
            cargar_prompt()
        )

        conocimiento = (
            cargar_base_conocimiento()
        )

        if not conocimiento:

            return JsonResponse(
                {
                    "respuesta":
                    "No se encontró la base de conocimiento."
                },
                status=500
            )

        contexto = buscar_fragmentos(
            conocimiento,
            mensaje,
            max_fragmentos=5
        )

        print("\n" + "=" * 80)
        print("PREGUNTA:")
        print(mensaje)
        print("=" * 80)

        print("CONTEXTO:")
        print(contexto)

        print("=" * 80)
        print(
            "TAMAÑO CONTEXTO:",
            len(contexto)
        )
        print("=" * 80)

        if not contexto.strip():

            return JsonResponse(
                {
                    "respuesta":
                    "No se encontró información relacionada con esa consulta."
                }
            )

        prompt_completo = f"""
{prompt_sistema}

CONTEXTO:

{contexto}

PREGUNTA:

{mensaje}

RESPUESTA:
"""

        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO_IA,
                "prompt": prompt_completo,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "top_p": 0.8,
                    "num_predict": 350,
                },
            },
            timeout=120,
        )

        respuesta.raise_for_status()

        resultado = respuesta.json()

        ia_texto = resultado.get(
            "response",
            ""
        ).strip()

        if not ia_texto:

            ia_texto = (
                "No se encontró información relacionada con esa consulta."
            )

        ia_texto = re.sub(
            r"^(respuesta:|answer:)",
            "",
            ia_texto,
            flags=re.IGNORECASE
        ).strip()

        # Protección básica
        respuesta_normalizada = (
            ia_texto.lower()
        )

        patrones_prohibidos = [
            "http://",
            "https://",
            "/usuario/",
            "/curso/",
            "/inventario/",
            "/dashboard/",
            "/login/"
        ]

        for patron in patrones_prohibidos:

            if patron in respuesta_normalizada:

                ia_texto = (
                    "No se encontró información relacionada con esa consulta."
                )

                break

        if len(ia_texto) > 1500:

            ia_texto = (
                ia_texto[:1500]
                + "..."
            )

        return JsonResponse(
            {
                "respuesta":
                ia_texto
            }
        )

    except requests.exceptions.RequestException as e:

        print(
            "Error Ollama:",
            e
        )

        return JsonResponse(
            {
                "respuesta":
                "Error de comunicación con la IA."
            },
            status=500
        )

    except Exception as e:

        print(
            "Error general:",
            e
        )

        return JsonResponse(
            {
                "respuesta":
                "Ocurrió un error inesperado."
            },
            status=500
        )

