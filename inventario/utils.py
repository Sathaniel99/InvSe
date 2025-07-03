import json

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