import json
from django.db.models import Max
from .models import ActivoFijo

def get_solicitud_sesion(request):
    return request.session.get('solicitud', {})

def guardar_solicitud_sesion(request, solicitud):
    request.session['solicitud'] = solicitud
    request.session.modified = True

def parse_items_json(items_json_str):
    if isinstance(items_json_str, dict):
        return items_json_str
    try:
        return json.loads(items_json_str)
    except Exception:
        return {}
    

def generar_numero_inventario():
    # Obtener el último número registrado
    ultimo_numero = ActivoFijo.objects.aggregate(
        ultimo=Max('codigo_interno')
    ).get('ultimo')

    # Número inicial personalizado (cambia 600000 por tu valor deseado)
    numero_inicial = "600000"

    if not ultimo_numero:
        return numero_inicial  # Usar el valor personalizado

    try:
        # Incrementar el último número y formatear a 6 dígitos
        nuevo_numero = int(ultimo_numero) + 1
        return f"{nuevo_numero:06d}"
    except (ValueError, TypeError):
        return numero_inicial  # Respaldar si el último número no es válido