from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView
from django.db.models import Sum, F, Count
from django.urls import reverse_lazy
from django.contrib import messages
from collections import defaultdict
from datetime import datetime
from .utils import get_solicitud_sesion, guardar_solicitud_sesion, parse_items_json, generar_numero_inventario
from .forms import *
from .models import *

@login_required 
def home_page(request):
    productos = Producto.objects.all()
    total = productos.count()
    agotados = productos.filter(stock_actual=0).count()
    bajo_stock = productos.filter(stock_actual__lte=F('stock_minimo'), stock_actual__gt=0).count()
    en_stock = productos.filter(stock_actual__gt=F('stock_minimo')).count()

    print(f"Total productos: {total}, Agotados: {agotados}, Bajo stock: {bajo_stock}, En stock: {en_stock}")

    context = {
        'title_page': 'Inicio',
        'total_productos': int(total),
        'productos_agotados': int(agotados),
        'productos_bajo_stock': int(bajo_stock),
        'productos_en_stock': int(en_stock),
    }
    return render(request, 'dashboard/home_page.html', context)

#############################################################################################################################
###################################                       INVENTARIO                      ###################################
#############################################################################################################################
# genera y guarda el inventario de una ubicacion
@login_required
def revisar_inventario(request):
    ubicacion = Ubicacion.objects.filter(area = request.user.area)
    context = {
        'title_page' : 'Revisar Inventario',
        'ubicaciones' : ubicacion
    }
    return render(request, 'dashboard/inventario/revisar_inventario.html', context)

# lista las ubicaciones para consultar su inventario
@login_required
def list_inventario(request):
    ubicaciones = Ubicacion.objects.filter(area = request.user.area)
    if 'economico' in request.user.tipo_user or request.user.is_superuser:
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
    responsable_area = Usuario.objects.filter(tipo_user = 'jefe_area').filter(area = get_object_or_404(Ubicacion, pk=id).area).first()
    
    nombre_responsable_area = "No posee aún"
    if responsable_area is not None:
        nombre_responsable_area = f"{responsable_area.first_name} {responsable_area.last_name}"
    
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


# registra la entrada de un activo fijo y actualiza el stock del tipo de producto
@login_required
def entrada_activos(request):
    if request.method == 'POST':
        form = ActivoFijoForm(request.POST)
        if form.is_valid():
            activo = form.save(commit=False)
            activo.serial_number = generar_numero_inventario()
            activo.save()

            id_activo = activo.producto.id
            # filtrar todos los activos con el id del producto y contarlos
            cantidad = ActivoFijo.objects.filter(producto__id = id_activo).count()
            # actualizar el producto con la cantidad anterior
            Producto.objects.filter(pk=id_activo).update(stock_actual=cantidad)
            return redirect('entrada-activos')

    context = {
        'title_page' : 'Entrada de Activo Fijo',
        'form' : ActivoFijoForm()
    }
    return render(request, 'dashboard/inventario/activos_entrada.html', context)

# registra el cambio de ubicacion o area de un activo fijo
@login_required
def ajuste_activos(request):
    pass


# # # # # # # # # # # # # # # # # # # # # #              REVISAR              # # # # # # # # # # # # # # # # # # # # # #
# registra la salida de un activo fijo y actualiza el stock del tipo de producto
@login_required
def salida_activos(request, id):
    object_activo = get_object_or_404(ActivoFijo, pk = id)

    if request.method == 'POST':
        form = ActivoFijoForm(request.POST, instance=object_activo)
        if form.is_valid():
            activo = form.save(commit=False)
            activo.estado = ESTADOS.DADO_DE_BAJA
            activo.save()

            id_activo = activo.producto.id
            cantidad = ActivoFijo.objects.filter(producto__id=id_activo).exclude(estado__in=[ESTADOS.DADO_DE_BAJA, ESTADOS.EN_REPARACION]).count()
            Producto.objects.filter(pk=id_activo).update(stock_actual=int(cantidad-1))
            
            return redirect('salida-activos')
    context = {
        'title_page': 'Salida de Activo Fijo',
        'form': ActivoFijoForm(instance = object_activo)
    }
    return render(request, 'dashboard/inventario/activos_salida.html', context)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#############################################################################################################################
######################################                    PRODUCTOS                       ###################################
#############################################################################################################################
# economico
@login_required
def resumen_productos(request):
    context = {
        'title_page' : 'Resumen de Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

def create_productos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('create-productos')  # Cambia '/' por el nombre de tu URL de éxito
    else:
        form = ProductoForm()

    context = {
        'form': form,
        'title_page': 'Agregar Producto',
    }

    return render(request, 'dashboard/productos/create.html', context)

@login_required
def list_productos(request):
    context = {
        'title_page' : 'Listado de Productos',
        'productos' : Producto.objects.all()
    }

    return render(request, 'dashboard/productos/list.html', context)

@login_required
def edit_productos(request,id):
    producto = get_object_or_404(Producto, pk = id)
    form = ProductoForm(instance=producto)
    html = render(request, 'dashboard/productos/htmx-update.html', {'form' : form, 'item' : producto, 'producto' : id})
    return HttpResponse(html)

@login_required
def show_productos(request,id):
    producto = get_object_or_404(Producto, pk = id)
    html = render(request, 'dashboard/productos/htmx-show.html', {'form' : producto, 'producto' : id})
    return HttpResponse(html)

@login_required
def update_productos(request,id):
    producto = get_object_or_404(Producto, id = id)
    form = ProductoForm()
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
    context = {
        'title_page' : 'Productos',
        'productos' : Producto.objects.all()
    }
    return render(request, 'dashboard/productos/list.html', context)

@login_required
def delete_productos(request, id):
    get_object_or_404(Producto, pk=id).delete()
    return redirect('list-productos')

@login_required
def productos_solicitados(request):
    solicitudes = SolicitudesProductos.objects.all()
    
    context = {
        'title_page' : 'Solicitudes de Productos',
        'solicitudes' : solicitudes
    }

    return render(request, 'dashboard/productos/productos_solicitados.html', context)

#############################################################################################################################
######################################                   PROVEEDORES                      ###################################
#############################################################################################################################
# rol economico
@login_required
def resumen_proveedores(request):
    
    # Mes actual
    hoy = datetime.today()
    dia_actual = hoy.day
    mes_actual = hoy.month
    year_actual = hoy.year
    
    # total de proveedores
    total_proveedores = Proveedor.objects.count()

    # cuantos proveedores aportaron este mes 
    proveedores_activos_mes = Proveedor.objects.filter(
        producto__movimientoinventario__tipo='entrada',
        producto__movimientoinventario__fecha__year=year_actual,
        producto__movimientoinventario__fecha__month=mes_actual
    ).distinct().count()
    
    # capital gastado este mes en proveedores
    total_gastado_mes = MovimientoInventario.objects.filter(
        tipo='entrada',
        producto__proveedor__isnull=False,
        fecha__year=year_actual,
        fecha__month=mes_actual
    ).annotate(
        costo_total=models.ExpressionWrapper(
            models.F('cantidad') * models.F('producto__precio_unitario'),
            output_field=models.DecimalField()
        )
    ).aggregate(total=models.Sum('costo_total'))['total'] or 0
    
    # top 5 proveedores mas usados
    proveedores_mas_usados = MovimientoInventario.objects.filter(
        tipo='entrada',
        fecha__year=year_actual,
        fecha__month=mes_actual
    ).values('producto__proveedor__nombre').annotate(
        total_entradas=Count('id'),
        total_gastado=Sum(F('cantidad') * F('producto__precio_unitario'))
    ).order_by('-total_entradas')[:5]

    # ultima entrada del mes
    ultima_entrada = MovimientoInventario.objects.filter(
        tipo='entrada',
        fecha__year=year_actual,
        fecha__month=mes_actual
    ).order_by('-fecha').first()

    if not ultima_entrada:
        # Última entrada registrada (sin importar la fecha)
        ultima_entrada = MovimientoInventario.objects.filter(
            tipo='entrada'
        ).order_by('-fecha').first()

    context = {
        'title_page' : 'Resumen de Proveedores',
        'fecha_hoy' : f"{dia_actual}/{mes_actual}/{year_actual}",
        'total_proveedores' : total_proveedores,
        'total_gastado_mes' : total_gastado_mes,
        'proveedores_activos_mes' : proveedores_activos_mes,
        'proveedores_mas_usados' : proveedores_mas_usados,
        'ultima_entrada' : ultima_entrada,
    }
    return render(request, 'dashboard/proveedores/resumen.html', context)

class create_proveedores(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'dashboard/proveedores/create.html'
    success_url = '/proveedores/create-proveedores/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'title_page': 'Agregar Proveedor',
        }

        return context

@login_required
def list_proveedores(request):
    proveedores = Proveedor.objects.all()
    context = {
        'title_page' : 'Listado de Proveedores',
        'proveedores' : proveedores
    }
    return render(request, 'dashboard/proveedores/list.html', context)

@login_required
def update_proveedores(request, id):
    proveedor = get_object_or_404(Proveedor, id = id)
    form = ProveedorForm()
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
    context = {
        'title_page' : 'Listar Proveedores',
        'proveedores' : Proveedor.objects.all()
    }
    return render(request, 'dashboard/proveedores/list.html', context)

@login_required
def delete_proveedores(request, id):
    get_object_or_404(Proveedor, pk=id).delete()
    return redirect('list-proveedores')

@login_required
def show_proveedor(request,id):
    proveedor = get_object_or_404(Proveedor, pk = id)
    form = ProveedorForm(instance=proveedor)
    html = render(request, 'dashboard/proveedores/htmx-update.html', {'form' : form, 'proveedor' : id})
    return HttpResponse(html)

#############################################################################################################################
######################################                    REPORTES                       ####################################
#############################################################################################################################
@login_required
def main_reportes(request):
    context = {
        'title_page' : 'Reportes'
    }
    return render(request, 'dashboard/reportes/reportes.html', context)


#############################################################################################################################
#############################                           AUTENTICACION                           #############################
#############################################################################################################################
class Main_LoginView(LoginView):
    template_name = 'auth/login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context = {
            'title_page': 'Iniciar Sesión',
        }

        return context

class Main_LogoutView(LogoutView):
    success_url = reverse_lazy('home')

@login_required
def self_account_config(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)
    
    context = {
        'title_page' : 'Configuración',
        'UsuarioChangeForm' : UsuarioChangeForm(instance=usuario),
        'PasswordChangeForm' : PasswordChangeForm(user=usuario),

    }            
    return render(request, 'auth/config.html', context)

# ARREGLAR CON EL CAMBIAR CONTRASEÑA
@login_required
def update_self_user(request):
    user = get_object_or_404(Usuario, pk=request.user.id)
    
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('self-config')
        else:
            print(form.errors)  # Para ver errores en consola

    return redirect('self-config')

# ARREGLAR CON EL UPDATE CUENTA
@login_required
def update_self_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión iniciada
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('self-config')  # Cambia por tu URL de éxito
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
            print(form.errors)  # Para ver los errores en consola
    return redirect('self-config')


@login_required
def self_cambiar_password(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if not request.user.is_authenticated or request.user.pk != usuario.pk:
        return redirect('inicio')  # O donde dirijas al usuario no autorizado

    if request.method == 'POST':
        form = PasswordChangeForm(user=usuario, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige al login o a un mensaje de éxito
    else:
        form = PasswordChangeForm(user=usuario)

    redirect('auth-config')


#############################################################################################################################
#############################                            SOLICITUDES                            #############################
#############################################################################################################################
# rol Jefe de Area

@login_required
def solicitudes_productos_tabla(request):
    solicitudes = SolicitudesProductos.objects.filter(usuario = request.user.id)
    context = {
        'title_page' : 'Solicitudes de Productos',
        'solicitudes' : solicitudes,
    }
    return render(request, 'dashboard/productos/solicitudes.html', context)

@login_required
def solicitar_productos(request):
    context = {
        'title_page' : 'Solicitar Productos',
        'productos' : Producto.objects.exclude(stock_actual = 0),
    }
    return render(request, 'dashboard/productos/solicitar.html', context)

@login_required
def solicitudes_productos_api(request):
    solicitudes = SolicitudesProductos.objects.filter(usuario = request.user.id)
    context = {
        'title_page' : 'Solicitudes de Productos',
        'solicitudes' : solicitudes,
    }
    return render(request, 'dashboard/productos/solicitudes/solicitudes_htmx.html', context)


def preparar_solicitud_api(request, id, cant):
    producto = get_object_or_404(Producto, pk=id)
    
    # Validación adicional
    try:
        cant = int(cant)
    except ValueError:
        return HttpResponse("Cantidad inválida", status=400)

    if cant <= 0:
        return HttpResponse("<p>Cantidad debe ser mayor a cero.</p>", status=400)

    stock_actual = int(producto.stock_actual or 0)
    stock_restante = max(stock_actual - cant, 0)

    context = {
        'producto': f"{producto.nombre} {producto.marca or ''} {producto.modelo or ''}".strip(),
        'img': producto.imagen.url if producto.imagen else "",
        'precio_unitario': float(producto.precio_unitario or 0),
        'stock_restante': stock_restante,
        'cantidad': cant,
        'id': id,
    }

    html = render(request, 'dashboard/productos/solicitudes/preparar_solicitud_htmx.html', context)
    return HttpResponse(html)

# agregar producto a la lista de solicitud
def agregar_a_la_solicitud_api(request, id, cant):
    producto = get_object_or_404(Producto, id=id)
    solicitud = get_solicitud_sesion(request)
    cant = int(cant)

    solicitud[str(id)] = {
        "ID": producto.id,
        "nombre": producto.nombre,
        "marca": producto.marca,
        "modelo": producto.modelo,
        "proveedor": producto.proveedor.nombre if producto.proveedor else "",
        "imagen": producto.imagen.url if producto.imagen else "",
        "cantidad": cant,
        "precio": float(producto.precio_unitario or 0),
    }

    guardar_solicitud_sesion(request, solicitud)

    # Devuelve el HTML actualizado del carrito
    context = {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
        'title_page' : 'Solicitar Productos',
        'productos' : Producto.objects.exclude(stock_actual = 0),
    }
    return redirect('solicitar-productos')

def ver_solicitud(request):
    solicitud = get_solicitud_sesion(request)
    context = {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
    }
    html = render(request, 'dashboard/productos/solicitudes/ver_solicitud_htmx.html', context)
    return HttpResponse(html)

def eliminar_item_solicitud_api(request, producto_id):
    solicitud = get_solicitud_sesion(request)
    producto_id_str = str(producto_id)

    if producto_id_str in solicitud:
        del solicitud[producto_id_str]
        guardar_solicitud_sesion(request, solicitud)

    html = render_to_string('dashboard/productos/solicitudes/ver_solicitud_htmx.html', {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
    })

    return HttpResponse(html)

def confirmar_solicitud_api(request):
    if request.method == 'POST':
        solicitud = get_solicitud_sesion(request)

        # Guardar la solicitud
        SolicitudesProductos.objects.create(
            usuario=request.user,
            items=solicitud,
            fecha_creacion=datetime.now(),
            estado='pendiente'
        )

        # Limpiar la solicitud después de guardar
        guardar_solicitud_sesion(request, {})

    return redirect('solicitudes-productos-tabla')

def ver_solicitud_creada(request, id):
    solicitud = SolicitudesProductos.objects.get(id=id)
    items_dict = parse_items_json(solicitud.items)  # Asegúrate que esto devuelve un dict

    context = {
        'solicitud': items_dict,
        'fecha_creada' : solicitud.fecha_creacion,
        'estado' : solicitud.estado.upper(),
        'fecha': datetime.now().date,
        'title_page': 'Ver Solicitud',
    }
    html = render(request, 'dashboard/productos/solicitudes/ver_solicitud_creada_htmx.html', context)
    return HttpResponse(html)

def eliminar_solicitudes_productos_tabla(request, id):
    solicitud = get_object_or_404(SolicitudesProductos, pk=id)
    solicitud.delete()
    
    return redirect('solicitudes-productos-tabla')

def vaciar_carrito_api(request):
    guardar_solicitud_sesion(request, {})
    solicitud = get_solicitud_sesion(request)
    html = render_to_string('dashboard/productos/solicitudes/ver_solicitud_htmx.html', {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
    })

    return HttpResponse(html)

def rechazar_solicitud(request, id):
    solicitud = get_object_or_404(SolicitudesProductos, pk=id)
    solicitud.estado = 'rechazada'
    solicitud.save()

    return redirect('productos-solicitados')

def aprobar_solicitud(request, id):
    solicitud = get_object_or_404(SolicitudesProductos, pk=id)
    solicitud.estado = 'aprobada'
    solicitud.save()

    # aqui viene la logica de restar de la base de datos la cantidad solicitada a la cantidad registrada, osea
    # si existen 3 servidores y se aprueba la solicitud de 2 quedaria 1 servidor disponible
    # Asegúrate de tener un dict real
    items_dict = parse_items_json(solicitud.items)

    # Itera sobre los valores (cada producto solicitado)
    for item in items_dict.values():
        producto = Producto.objects.get(id=item['ID'])
        if producto.stock_actual >= item['cantidad']:
            producto.stock_actual -= item['cantidad']
            producto.save()
            
    return redirect('productos-solicitados')