# utils.py

def get_solicitud_sesion(request):
    return request.session.get('solicitud', {})

def guardar_solicitud_sesion(request, solicitud):
    request.session['solicitud'] = solicitud