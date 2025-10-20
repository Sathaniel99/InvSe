from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.db.models import Sum, F, Count
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .utils import parse_items_json, generar_numero_inventario
from .forms import *
from .models import *

@login_required
def home_page(request):
    # Seccion Resumen de Productos
    productos = Producto.objects.all()
    productos_total = productos.aggregate(total=Sum('stock_actual'))['total']
    productos_agotados = productos.filter(stock_actual=0).count()
    productos_bajo_stock = productos.filter(stock_actual__lte=F('stock_minimo'), stock_actual__gt=0).count()
    productos_en_stock = productos.filter(stock_actual__gt=F('stock_minimo')).count()

    # Seccion Resumen de Activos Fijos
    activos_fijos = ActivoFijo.objects.all()
    activos_fijos_en_uso = activos_fijos.filter(estado=ESTADOS.EN_USO).count()
    activos_fijos_almacen = activos_fijos.filter(estado=ESTADOS.ALMACEN).count()
    activos_fijos_en_reparacion = activos_fijos.filter(estado=ESTADOS.EN_REPARACIÓN).count()
    activos_fijos_dado_de_baja = activos_fijos.filter(estado=ESTADOS.DADO_DE_BAJA).count()

    # Seccion Actividad Reciente
    # 4 recientes items 
    historial = HistorialActivo.objects.all().order_by('-id')[:4]
    
    # entradas, salidas, movimientos
    movimientos = MovimientoInventario.objects.all()
    
    # Obtener el primer y último día del mes actual
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    entradas = movimientos.filter(tipo=TIPO_MOVIMIENTO.ENTRADA,fecha__gte=start_of_month).count()
    salidas = movimientos.filter(tipo=TIPO_MOVIMIENTO.SALIDA,fecha__gte=start_of_month).count()
    ajustes = movimientos.filter(tipo=TIPO_MOVIMIENTO.AJUSTE,fecha__gte=start_of_month).count()

    # Seccion Alertas
    alertas = Alertas.objects.all()[:3]

    context = {
        'title_page': 'Inicio',
        'productos_total': int(productos_total),
        'productos_agotados': int(productos_agotados),
        'productos_bajo_stock': int(productos_bajo_stock),
        'productos_en_stock': int(productos_en_stock),
        'activos_fijos_en_uso': int(activos_fijos_en_uso),
        'activos_fijos_almacen': int(activos_fijos_almacen),
        'activos_fijos_en_reparacion': int(activos_fijos_en_reparacion),
        'activos_fijos_dado_de_baja': int(activos_fijos_dado_de_baja),
        'historial' : historial,
        'entradas': entradas,
        'salidas': salidas,
        'ajustes': ajustes,
        'alertas': alertas,
    }
    return render(request, 'dashboard/economico_home_page.html', context)

#############################################################################################################################
#############################                       SOLICITUDES PRODUCTOS                       #############################
#############################################################################################################################
@login_required
def productos_solicitados(request):
    solicitudes = SolicitudesProductos.objects.all().exclude(estado=ESTADOS_SOLICITUD.APROBADA)
    
    context = {
        'title_page' : 'Solicitudes de Productos',
        'solicitudes' : solicitudes
    }

    return render(request, 'dashboard/productos/productos_solicitados.html', context)

############################################## ==>       END POINTS       <== ###############################################
@login_required
def rechazar_solicitud(request, id):
    try:
        solicitud = get_object_or_404(SolicitudesProductos, pk=id)
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.success(request,'Solicitud rechazada con éxito.')
    except:
        messages.error(request, 'Ha ocurrido un error.')
    return redirect('productos-solicitados')

@login_required
def aprobar_solicitud(request, id):
    solicitud = get_object_or_404(SolicitudesProductos, pk=id)
    # Cambia el estado de la solicitud y guarda
    solicitud.estado = ESTADOS_SOLICITUD.APROBADA
    solicitud.save()

    # Convierte el campo items a dict (si es necesario)
    items_dict = parse_items_json(solicitud.items)

    # Itera sobre cada producto solicitado
    for item in items_dict.values():
        producto = Producto.objects.get(id=item['ID'])
        cantidad_solicitada = item['cantidad']

        # Verifica stock suficiente
        if producto.stock_actual >= cantidad_solicitada:
            # Resta la cantidad solicitada del stock
            producto.stock_actual -= cantidad_solicitada
            producto.save()

            # Crea un ActivoFijo por cada unidad solicitada
            for _ in range(cantidad_solicitada):
                ActivoFijo.objects.create(
                    codigo_interno = generar_numero_inventario(),
                    producto=producto,
                    responsable=solicitud.usuario,
                    ubicacion=None,  # Sin ubicación asignada
                    estado=ESTADOS.SIN_UBICACION,
                    descripcion=f"Activo generado por solicitud #{solicitud.id}",
                    fecha_adquisicion=datetime.now()
                )

    messages.success(request, "Solicitud Aprobada con éxito.")
    return redirect('productos-solicitados')

#############################################################################################################################
######################################                   PROVEEDORES                      ###################################
#############################################################################################################################
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

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Proveedor creado con éxito.")
        return response
    
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
            messages.success(request,"Proveedor editado con éxito.")
        else:
            messages.error(request,"Error al editar proveedor.")
    context = {
        'title_page' : 'Listar Proveedores',
        'proveedores' : Proveedor.objects.all()
    }
    return render(request, 'dashboard/proveedores/list.html', context)

@login_required
def delete_proveedores(request, id):
    get_object_or_404(Proveedor, pk=id).delete()
    messages.success(request,"Proveedor eliminado con éxito.")
    return redirect('list-proveedores')

@login_required
def show_proveedor(request,id):
    proveedor = get_object_or_404(Proveedor, pk = id)
    form = ProveedorForm(instance=proveedor)
    html = render(request, 'dashboard/proveedores/htmx-update.html', {'form' : form, 'proveedor' : id})
    return HttpResponse(html)

#############################################################################################################################
######################################                    PRODUCTOS                       ###################################
#############################################################################################################################

@login_required
def create_productos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Producto creado con éxito.")
            return redirect('create-productos')
        messages.error(request,"Error al crear el producto.")
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
            messages.success(request,"Producto editado con éxito.")
            form.save()
        else:
            messages.error(request,"Error al editar el producto.")
    context = {
        'title_page' : 'Productos',
        'productos' : Producto.objects.all()
    }
    return render(request, 'dashboard/productos/list.html', context)

@login_required
def delete_productos(request, id):
    get_object_or_404(Producto, pk=id).delete()
    messages.success(request,"Producto eliminado con éxito.")
    return redirect('list-productos')

#############################################################################################################################
######################################                  ACTIVOS FIJOS                     ###################################
#############################################################################################################################
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

