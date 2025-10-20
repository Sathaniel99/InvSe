from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from core.settings_web_project import PRECIO_USD
from .utils import parse_items_json, convert_CUP_to_USD, convert_num
from .forms import *
from .models import *
from . import views_economico
from . import views_jefe_area
from . import views_admin

# Pagina en Construccion
@login_required
def build_page(request):
    context = {
        'title_page': 'Desarrollando página',
        'explicacion' : f"Página en desarrollo."
    }
    return render(request, 'includes/build.html', context)

################################################      Pagina de Inicio      #################################################
@login_required 
def home_page(request):
    if request.user.tipo_user == TIPO_USER.ECONOMICO:
        return views_economico.home_page(request)
    elif request.user.tipo_user == TIPO_USER.JEFE_AREA:
        return views_jefe_area.home_page(request)
    elif request.user.tipo_user == TIPO_USER.ADMIN_SITIO:
        return views_admin.home_page(request)
    else:
        return views_admin.home_page(request)

@login_required
def alertas_stock_api(request):
    alertas = Alertas.objects.all().filter(area__id = request.user.area.id).order_by("-fecha")
    html = render(request, 'dashboard/alertas_stocks_htmx.html', {'alertas' : alertas})
    return HttpResponse(html)

@login_required
def alertas_stocks_api_filter(request):
    text_input = request.POST.get('textInput', '')
    date_input = request.POST.get('dateInput', '')
    
    alertas = Alertas.objects.all()

    # filtrar por texto si se proporciona
    if text_input:
        alertas = alertas.filter(
            Q(producto__nombre__icontains=text_input) |
            Q(producto__marca__icontains=text_input) |
            Q(producto__modelo__icontains=text_input)
        )

    # filtrar por fecha si se proporciona
    if date_input:
        try:
            date_obj = timezone.datetime.strptime(date_input, '%Y-%m-%d').date()
            start_of_day = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()))
            end_of_day = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.max.time()))
            alertas = alertas.filter(fecha__range=(start_of_day, end_of_day))
        except ValueError:
            print(ValueError)

    html = render(request, 'dashboard/alertas_stocks_htmx.html', {'alertas': alertas})
    return HttpResponse(html)

@login_required
def alertas_stocks_api_delete(request, id):
    ax = Alertas.objects.get(pk=id)
    print(ax)
    # ax.delete()
    return HttpResponse(status=204)

#############################################################################################################################
#############################                           AUTENTICACION                           #############################
#############################################################################################################################
class Main_LoginView(LoginView):
    template_name = 'auth/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"¡Bienvenido {self.request.user.get_full_name() or self.request.user.username}!"
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al iniciar sesión. Verifica tus credenciales."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title_page': 'Iniciar Sesión',
        })
        return context

class Main_LogoutView(LogoutView):
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(
                request,
                f"Has cerrado sesión correctamente. ¡Hasta pronto {request.user.get_full_name() or request.user.username}!"
            )
        return super().dispatch(request, *args, **kwargs)


def password_forgot_htmx(request):
    html = render(request, 'auth/htmx/password_forgot_htmx.html')
    return HttpResponse(html)

def login_form_htmx(request):
    html = render(request, 'auth/htmx/login-form-htmx.html')
    return HttpResponse(html)

#############################################################################################################################
###################################                       INVENTARIO                      ###################################
#############################################################################################################################
# lista las ubicaciones para comprobar su inventario
@login_required
def revisar_inventario(request):
    ubicacion = Ubicacion.objects.filter(area = request.user.area)
    context = {
        'title_page' : 'Revisar Inventario',
        'ubicaciones' : ubicacion,
    }
    return render(request, 'dashboard/inventario/revisar_inventario.html', context)

# lista las ubicaciones para consultar su inventario con su historial
@login_required
def list_inventario(request):
    ubicaciones = Ubicacion.objects.filter(area = request.user.area)
    if 'Económico' in request.user.tipo_user or request.user.is_superuser:
        ubicaciones = Ubicacion.objects.all()
    context = {
        'title_page' : 'Listado de Inventarios',
        'ubicaciones' : ubicaciones,
    }
    return render(request, 'dashboard/inventario/list.html', context)

# consulta el inventario actual de una ubicacion
@login_required
def actual_inventario_api(request, id):
    activos_fijos = ActivoFijo.objects.filter(ubicacion__id = id).select_related('producto').order_by('producto__nombre')
    responsable_area = Usuario.objects.filter(tipo_user = TIPO_USER.JEFE_AREA).filter(area = get_object_or_404(Ubicacion, pk=id).area).first()
    
    nombre_responsable_area = "No posee aún"
    if responsable_area is not None:
        nombre_responsable_area = f"{responsable_area.first_name} {responsable_area.last_name}"
    
    grouped_data = defaultdict(list)

    for af in activos_fijos:
        if af.estado == ESTADOS.EN_USO:
            
            key = af.producto.nombre
            if af.producto.modelo:
                key = f"{key} {af.producto.modelo}"
            if af.producto.marca:
                key = f"{key} {af.producto.marca}"
            
            grouped_data[key].append({
                'codigo_interno': af.codigo_interno,
                'serial_number': af.serial_number or 'No registrado'
            })
    
    # formato final con listas unidas
    processed_data = []
    counter = 1
    for producto_nombre, items in grouped_data.items():
        codigos = '<br>'.join([item['codigo_interno'] for item in items])
        seriales = '<br>'.join([item['serial_number'] for item in items])

        processed_data.append({
            'no': counter,
            'producto_nombre': producto_nombre,
            'cantidad': len(items),
            'codigos': codigos,
            'seriales': seriales,
        })
        counter += 1

    # Renderizar el template con los datos agrupados
    html = render(request, 'dashboard/inventario/actual_inventario_htmx.html', {
        'grouped_activo_list': processed_data,
        'ubicacion' : Ubicacion.objects.get(pk=id).nombre,
        "responsable_area" : nombre_responsable_area
    })

    return HttpResponse(html)

# revisar el inventario actual de una ubicacion
@login_required
def revisar_inventario_api(request, id):
    activos_fijos = ActivoFijo.objects.filter(ubicacion__id = id).select_related('producto').order_by('producto__nombre')
    
    grouped_data = defaultdict(list)

    for af in activos_fijos:
        if af.get_estado_display() == 'En uso':
            key = af.producto.nombre
            grouped_data[key].append({
                'codigo_interno': af.codigo_interno,
                'serial_number': af.serial_number or 'No registrado'
            })

    # formato final con listas unidas
    processed_data = []
    counter = 1
    for producto_nombre, items in grouped_data.items():
        codigos = '<br>'.join([item['codigo_interno'] for item in items])
        seriales = '<br>'.join([item['serial_number'] for item in items])

        processed_data.append({
            'no': counter,
            'producto_nombre': producto_nombre,
            'cantidad': len(items),
            'codigos': codigos,
            'seriales': seriales,
        })
        counter += 1

    # Renderizar el template con los datos agrupados
    html = render(request, 'dashboard/inventario/revisar_inventario_htmx.html', {
        'grouped_activo_list': activos_fijos,
        'ubicacion' : Ubicacion.objects.get(pk=id).nombre,
    })

    return HttpResponse(html)

# consulta el historial del inventario seleccionado
@login_required
def historial_inventario_api(request, id):
    inventario = Inventario.objects.filter(ubicacion__id=id).order_by("-fecha")
    html = render(request, 'dashboard/inventario/historial_inventario_htmx.html', {'historial' : inventario})
    return HttpResponse(html)

# consulta el ultimo inventario de una ubicacion
@login_required
def read_inventario(request, id):
    inventario = Inventario.objects.filter(ubicacion__id=id).order_by('fecha')
    
    print(inventario)
    html = render(request, 'dashboard/inventario/read_htmx.html', {'context' : inventario})
    return HttpResponse(html)

# actualiza el inventario de una ubicacion
@login_required
def update_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    return render(request, 'dashboard/inventario/list.html', context)

# elimina el inventario de una ubicacion si tiene menos de 24h creadas
@login_required
def delete_inventario(request, id):
    inventario = get_object_or_404(Inventario, pk=id)
    return redirect('list-inventario')

#############################################################################################################################
######################################                  ACTIVOS FIJOS                     ###################################
#############################################################################################################################
# ENDPOINTS
@login_required
def sin_local_activos(request):
    if request.method == 'POST':
        id_activo = request.POST.get('activo_id')
        ubicacion_id = request.POST.get('ubicacion_id')
        activo = get_object_or_404(ActivoFijo, pk=id_activo)
        ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)

        # Asignar la nueva ubicación al activo
        activo.ubicacion = ubicacion
        activo.estado = ESTADOS.EN_USO
        activo.save()

        # Registrar el historial del cambio de ubicación
        HistorialActivo.objects.create(
            activo=activo,
            responsable=request.user,
            accion=ACCIONES_HISTORIAL.MOVIMIENTO_DE_ÁREA,
            estado=ESTADO_ACCION_HISTORIAL.COMPLETADO,
            descripcion=f"Activo movido a {ubicacion.nombre}"
        )

        messages.success(request, 'Activo movido correctamente.')
        return redirect('sin-local-activos')
    
    area = request.user.area
    activos = ActivoFijo.objects.filter(
        responsable__area=area,
        ubicacion__isnull=True
    ).filter(estado=ESTADOS.SIN_UBICACIÓN)
    context = {
        'title_page' : 'Activos sin local',
        'activos' : activos
    }
    return render(request, 'dashboard/inventario/activos_sin_local.html', context)

@login_required
def sin_local_activos_htmx(request,id):
    context = {
        'item' : get_object_or_404(ActivoFijo, pk = id),
        'ubicaciones' : Ubicacion.objects.filter(area = request.user.area),
    }
    html = render(request, 'dashboard/inventario/activos_sin_local_htmx.html', context)
    return HttpResponse(html)

#############################################################################################################################
######################################                    PRODUCTOS                       ###################################
#############################################################################################################################
@login_required
def resumen_productos(request):
    context = {
        'title_page' : 'Resumen de Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

#############################################################################################################################
######################################                    REPORTES                       ####################################
#############################################################################################################################
@login_required
def main_reportes(request):
    context = {
        'title_page' : 'Reportes'
    }
    return render(request, 'dashboard/reportes/reportes.html', context)

@login_required
def reporte_valoracion_economica(request):
    ubicaciones = Ubicacion.objects.filter(area = request.user.area)
    context = {
        'ubicaciones': [],
        'total_coste' : '',
        'usd': ''
    }
    total_coste = 0

    for ubicacion in ubicaciones:
        activos = ActivoFijo.objects.filter(ubicacion = ubicacion)
        coste = 0
        for activo in activos:
            coste += activo.producto.precio_unitario
        total_coste += coste
        # añadir la información de cada ubicación al contexto
        context['ubicaciones'].append({
            'nombre': ubicacion.nombre,
            'coste': convert_num(str(coste)),
        })
    
    context['total_coste'] = convert_num(str(total_coste))
    context['usd'] = convert_num(str(convert_CUP_to_USD(total_coste, PRECIO_USD)))
    
    html = render(request, 'dashboard/reportes/valoracion_economica_htmx.html', context)
    return HttpResponse(html)

#############################################################################################################################
#############################                           CONFIGURACION                           #############################
#############################################################################################################################
@login_required
def self_account_config(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    context = {
        'title_page' : 'Configuración',
        'UsuarioChangeForm' : UsuarioChangeForm(instance=usuario),
        'PasswordChangeForm' : PasswordChangeForm(user=usuario),

    }            
    return render(request, 'auth/config.html', context)

@login_required
def update_self_user(request):
    user = get_object_or_404(Usuario, pk=request.user.id)
    
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "¡Tus datos se actualizaron correctamente!")
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
            return redirect('self-config')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    
    return redirect('self-config')

@login_required
def update_self_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Su contraseña ha sido actualizada correctamente.')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    return redirect('self-config')

@login_required
def update_self_photo(request):
    if request.method != 'POST':
        return redirect("self-config")
    
    # Verificar si se envió un archivo
    if 'imageUpload' not in request.FILES:
        messages.error(request, "No se seleccionó ningún archivo")
        return redirect("self-config")
    
    # Obtener el archivo subido
    new_image = request.FILES['imageUpload']
    
    # Validar que sea una imagen (por extensión y tipo MIME)
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    extension = new_image.name.split('.')[-1].lower()
    
    if extension not in valid_extensions:
        messages.error(request, "Formato de archivo no válido. Use JPG, JPEG, PNG o GIF")
        return redirect("self-config")
    
    # Validar tamaño del archivo (ejemplo: máximo 5MB)
    if new_image.size > 5 * 1024 * 1024:
        messages.error(request, "La imagen es demasiado grande (máximo 5MB)")
        return redirect("self-config")
    
    try:
        # Actualizar la imagen del usuario
        user = request.user
        user.img = new_image
        user.save()
        
        messages.success(request, "Foto de perfil actualizada correctamente")
    except Exception as e:
        messages.error(request, f"Error al actualizar la foto: {str(e)}")
    
    return redirect("self-config")

#############################################################################################################################
#############################                            SOLICITUDES                            #############################
#############################################################################################################################
def ver_solicitud_creada(request, id):
    solicitud = SolicitudesProductos.objects.get(id=id)
    items_dict = parse_items_json(solicitud.items)

    context = {
        'solicitud': items_dict,
        'fecha_creada' : solicitud.fecha_creacion,
        'estado' : solicitud.estado.upper(),
        'fecha': datetime.now().date,
        'title_page': 'Ver Solicitud',
    }
    html = render(request, 'dashboard/productos/solicitudes/ver_solicitud_creada_htmx.html', context)
    return HttpResponse(html)

#############################################################################################################################
#############################                           VISTAS A UBICAR                         #############################
#############################################################################################################################
# INVENTARIO
# ACTIVOS FIJOS
# REPORTES