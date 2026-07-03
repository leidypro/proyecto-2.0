import os

from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

TOKEN_PATH = os.path.join(
    settings.BASE_DIR,
    "token.json"
)

CREDENTIALS_PATH = os.path.join(
    settings.BASE_DIR,
    "credentials.json"
)


def obtener_servicio():

    creds = None

    # Cargar token existente
    if os.path.exists(TOKEN_PATH):

        try:
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH,
                SCOPES
            )

            print("\n=== ESTADO DEL TOKEN ===")
            print("Valid:", creds.valid)
            print("Expired:", creds.expired)
            print("Refresh token:", bool(creds.refresh_token))
            print("========================\n")

        except Exception as e:
            print(f"Error leyendo token.json: {e}")
            creds = None

    # Si hay credenciales expiradas intentar renovar
    if creds and creds.expired and creds.refresh_token:

        print("Intentando renovar token...")

        try:

            creds.refresh(Request())

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

            print("✅ Token renovado correctamente")

        except Exception as e:

            print(f"❌ Error renovando token: {e}")

            # No abrir navegador automáticamente
            raise Exception(
                f"No fue posible renovar el token: {e}"
            )

    # Si no existen credenciales válidas
    elif not creds:

        print("No existe token válido.")
        print("Iniciando autenticación OAuth...")

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES
        )

        creds = flow.run_local_server(
            port=8080,
            prompt="consent",
            access_type="offline"
        )

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

        print("Token generado correctamente")

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service

def crear_evento(
    titulo,
    descripcion,
    fecha_inicio,
    fecha_fin
):

    servicio = obtener_servicio()

    evento = {

        "summary": titulo,

        "description": descripcion,

        "start": {
            "dateTime": fecha_inicio.isoformat(),
            "timeZone": "America/Bogota",
        },

        "end": {
            "dateTime": fecha_fin.isoformat(),
            "timeZone": "America/Bogota",
        },
    }

    evento_creado = servicio.events().insert(
        calendarId='primary',
        body=evento
    ).execute()

    return evento_creado


def actualizar_evento(
    google_event_id,
    titulo,
    descripcion,
    fecha_inicio,
    fecha_fin
):
    try:
        servicio = obtener_servicio()
        evento_actualizado = {
            "summary":titulo,
            "description":descripcion,
            "start":{
                "dateTime":fecha_inicio.isoformat(),
                "timeZone":"America/Bogota",
                },
            "end":{
                "dateTime":fecha_fin.isoformat(),
                "timeZone":"America/Bogota",
                },
        }
        resultado = servicio.events().update(
            calendarId = 'primary',
            eventId=google_event_id,
            body=evento_actualizado
        ).execute()
        return resultado
    
    except HttpError as error:
        print("Error actualizando el evento" , error)
        return None
    
    
    
def eliminar_evento(google_event_id):
    try:
        servicio = obtener_servicio()
        
        servicio.events().delete(
            calendarId = 'primary',
            eventId = google_event_id
        ).execute()
        print("Evento eliminado del Google Calendar")
    
    except Exception as e:
        print("Error al eliminar el evento ",e)