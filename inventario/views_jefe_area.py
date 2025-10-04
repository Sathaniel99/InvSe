from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib import messages
from datetime import datetime
from .utils import get_solicitud_sesion, guardar_solicitud_sesion
from .forms import *
from .models import *
from .choices import *

@login_required
def home_page(request):
    ubicaciones = Ubicacion.objects.filter(area=request.user.area)
    activos = ActivoFijo.objects.filter(ubicacion__area = request.user.area)
    
    for ax in ubicaciones:
        ax.activos = ActivoFijo.objects.filter(ubicacion = ax).exclude(estado = ESTADOS.DADO_DE_BAJA).exclude(estado = ESTADOS.EN_REPARACIÓN)
        ax.baja = ActivoFijo.objects.filter(ubicacion = ax).exclude(estado = ESTADOS.EN_USO).exclude(estado = ESTADOS.EN_REPARACIÓN)
        ax.reparacion = ActivoFijo.objects.filter(ubicacion = ax).exclude(estado = ESTADOS.EN_USO).exclude(estado = ESTADOS.DADO_DE_BAJA)

    context = {
        'title_page': 'Inicio',
        'ubicaciones': ubicaciones,
        'uso' : activos.filter(estado = ESTADOS.EN_USO).count(),
        'reparacion' : activos.filter(estado = ESTADOS.EN_REPARACIÓN).count(),
        'baja' : activos.filter(estado = ESTADOS.DADO_DE_BAJA).count(),
        'sin_ubicacion' : activos.filter(estado = ESTADOS.SIN_UBICACIÓN).count(),
    }
    return render(request, 'dashboard/jefe_area_home_page.html', context)

#############################################################################################################################
#############################                       SOLICITUDES PRODUCTOS                       #############################
#############################################################################################################################
@login_required
def eliminar_solicitudes_productos_tabla(request, id):
    solicitud = get_object_or_404(SolicitudesProductos, pk=id)
    solicitud.delete()
    messages.success(request,"Solicitudes eliminadas correctamente.")
    return redirect('solicitudes-productos-tabla')

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

@login_required
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
    
    pr_parts = [producto.nombre]
    if producto.marca:
        pr_parts.append(producto.marca)
    if producto.modelo:
        pr_parts.append(producto.modelo)
    pr = " ".join(pr_parts).strip()
    
    messages.success(request, f"{pr} agregado correctamente")

    return redirect('solicitar-productos')

@login_required
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

@login_required
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
        messages.info(request,mark_safe("Solicitud de productos creada.<br>Espere a ser Atendido."))
    return redirect('solicitudes-productos-tabla')

@login_required
def vaciar_carrito_api(request):
    guardar_solicitud_sesion(request, {})
    solicitud = get_solicitud_sesion(request)
    html = render_to_string('dashboard/productos/solicitudes/ver_solicitud_htmx.html', {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
    })

    return HttpResponse(html)

@login_required
def ver_solicitud(request):
    solicitud = get_solicitud_sesion(request)
    context = {
        'solicitud': solicitud.items(),
        'fecha': datetime.now().date,
    }
    html = render(request, 'dashboard/productos/solicitudes/ver_solicitud_htmx.html', context)
    return HttpResponse(html)


#############################################################################################################################
######################################                  ACTIVOS FIJOS                     ###################################
#############################################################################################################################
# # # # # # # # # # # # # # # # # # # # # #              REVISAR              # # # # # # # # # # # # # # # # # # # # # #
# registra la salida de un activo fijo
@login_required
def salida_activos(request, id):
    activo = get_object_or_404(ActivoFijo, pk = id)
    if request.method == 'POST':
        activo.estado = ESTADOS.DADO_DE_BAJA
        activo.save() 
        HistorialActivo.objects.create(
            activo = activo,
            responsable = request.user,
            accion = ACCIONES_HISTORIAL.DADO_DE_BAJA,
            estado = ESTADO_ACCION_HISTORIAL.COMPLETADO,
        )
    
    historial = HistorialActivo.objects.filter(activo = id)
    context = {
        'title_page': 'Salida de Activo Fijo',
        'historial' : historial,
        'last_act': historial.last,
        'activo': activo,
    }
    return render(request, 'dashboard/inventario/activos_salida.html', context)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# -+# # # # # # # # # # # # # # # # # # # # # #            IMPLEMENTAR            # # # # # # # # # # # # # # # # # # # # # # #
# registra el cambio de ubicacion o area de un activo fijo
@login_required
def ajuste_activos(request):
    pass
