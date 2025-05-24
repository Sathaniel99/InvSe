from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.urls import reverse_lazy
from datetime import datetime
from .forms import *
from .models import *

@login_required
def home_page(request):
    context = {
        'title_page' : 'Inicio'
    }
    return render(request, 'dashboard/home_page.html', context)

#############################################################################################################################
###################################                       INVENTARIO                      ###################################
#############################################################################################################################
@login_required
def main_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    return render(request, 'dashboard/inventario/inventario.html', context)

@login_required
def create_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    return render(request, 'dashboard/inventario/inventario.html', context)

@login_required
def list_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    
    return render(request, 'dashboard/inventario/inventario.html', context)

@login_required
def read_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    return render(request, 'dashboard/inventario/inventario.html', context)

@login_required
def update_inventario(request):
    context = {
        'title_page' : 'Inventario'
    }
    return render(request, 'dashboard/inventario/inventario.html', context)

@login_required
def delete_inventario(request):
    return redirect('list-inventario')

#############################################################################################################################
######################################                    PRODUCTOS                       ###################################
#############################################################################################################################
@login_required
def resumen_productos(request):
    context = {
        'title_page' : 'Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

@login_required
def create_productos(request):
    context = {
        'title_page' : 'Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

@login_required
def list_productos(request):
    context = {
        'title_page' : 'Productos'
    }
    producto = Producto.objects.all()

    return render(request, 'dashboard/productos/list.html', context)

@login_required
def read_productos(request):
    context = {
        'title_page' : 'Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

@login_required
def update_productos(request):
    context = {
        'title_page' : 'Productos'
    }
    return render(request, 'dashboard/productos/productos.html', context)

@login_required
def delete_productos(request):
    return redirect('list-productos')


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
        'title_page' : 'Proveedores',
        'fecha_hoy' : f"{dia_actual}/{mes_actual}/{year_actual}",
        'total_proveedores' : total_proveedores,
        'total_gastado_mes' : total_gastado_mes,
        'proveedores_activos_mes' : proveedores_activos_mes,
        'proveedores_mas_usados' : proveedores_mas_usados,
        'ultima_entrada' : ultima_entrada,
    }
    return render(request, 'dashboard/proveedores/resumen.html', context)

from django.views.generic.edit import CreateView

class create_proveedores(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'dashboard/proveedores/create.html'
    success_url = '/'

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
        'title_page' : 'Listar Proveedores',
        'proveedores' : proveedores
    }
    return render(request, 'dashboard/proveedores/list.html', context)

@login_required
def read_proveedores(request, id):
    proveedor = Proveedor.objects.get_object_or_404(id = id)
    
    context = {
        'title_page' : 'Proveedores',
        'proveedor' : proveedor
    }
    return render(request, 'dashboard/proveedores/proveedores.html', context)

@login_required
def update_proveedores(request, id):
    proveedor = Proveedor.objects.get_object_or_404(id = id)
    form = ProveedorForm()
    errors = ""
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
        else:
            errors = form.errors
    context = {
        'title_page' : 'Listar Proveedores',
        'proveedores' : Proveedor.objects.all(),
        'errors' : errors
    }
    return render(request, 'dashboard/proveedores/list.html', context)

@login_required
def delete_proveedores(request, id):
    Proveedor.objects.get_object_or_404(pk=id).delete()
    return redirect('list-proveedores')

def search_proveedor_id(request,id):
    proveedor = Proveedor.objects.get_object_or_404(pk = id)
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
