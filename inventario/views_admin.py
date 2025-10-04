from .forms import UbicacionForm, AreaForm, UsuarioChangeForm, UsuarioCreateForm
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from core.settings_web_project import DOMINIO, ENTIDAD_WEB
from .utils import actualizar_config, manage_choice
from .choices import ESTADOS, ACCIONES_HISTORIAL, TIPO_USER
from .models import Ubicacion, Area, Usuario
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

def home_page(request):
    usuarios = dict()
    users = Usuario.objects
    ubicaciones = Ubicacion.objects
    
    for ax in TIPO_USER:
        usuarios[ax.value] = users.filter(tipo_user = ax.value).count()

    context = {
        'title_page': 'Inicio',
        'users' : usuarios.items(),
        'users_count' : users.count(),
        'ubicaciones' : ubicaciones.all(),
        'ubicaciones_count' : ubicaciones.count(),
        'area' : Area.objects.exclude(nombre="Sin Área")
    }
    return render(request, 'admin/home.html', context)

#############################################################################################################################
#############################                     CONFIGURACION DE SERVIDOR                     #############################
#############################################################################################################################
def server_config(request, id=None):
    # Vista para Crear, Editar y Eliminar elementos tales como:
    # => Models.py : Ubicaciones, Areas, Categorias
    # => Choices.py: ESTADOS (de un Activo), ACCIONES_HISTORIAL
    # Principalmente configurar las variables
    # => settings_web_project.py: ENTIDAD_WEB, DOMINIO
    # Tener un boton para crear Salva de BD (Opcional)
    if request.method == "POST":
        tipo = request.POST.get("type")
        try:
            if tipo == "ubicaciones":
                return accion_ubicaciones(request)
            elif tipo == "areas":
                return accion_areas(request)
            elif tipo == "estados1":
                return accion_estados(request)
            elif tipo == "estados2":
                return accion_estados_historial(request)
            elif tipo == "entidad" or tipo == "dominio":
                return accion_configuracion(request)
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {str(e)}')
        return redirect('server-config')

    context = {
        "title_page": "Configurar servidor",
        'ubicaciones' : Ubicacion.objects.all(),
        'areas' : Area.objects.all(),
        'ESTADOS' : ESTADOS,
        'ACCIONES_HISTORIAL' : ACCIONES_HISTORIAL,
        'dominio' : DOMINIO,
        'entidad' : ENTIDAD_WEB
    }
    return render(request, 'admin/server_config.html', context)

# Handlers para cada tipo de operación
def accion_ubicaciones(request):
    action = request.POST.get("action")
    
    if action == "create":
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación creada con éxito.')
        else:
            messages.error(request, 'Error al crear ubicación.')
    
    elif action == "delete":
        try:
            ubicacion = Ubicacion.objects.get(id=request.POST.get("element"))
            ubicacion.delete()
            messages.success(request, 'Ubicación eliminada con éxito.')
        except:
            messages.error(request, 'Error al eliminar Ubicación.')
    return redirect('server-config')

def accion_areas(request):
    action = request.POST.get("action")
    
    if action == "create":
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área creada con éxito.')
        else:
            messages.error(request, 'Error al crear área.')
    
    elif action == "delete":
        try:
            area = Area.objects.get(id=request.POST.get("element"))
            area.delete()
            messages.success(request, 'Área eliminada con éxito.')
        except:
            messages.error(request, 'Error al eliminar Área.')
    
    return redirect('server-config')

def accion_estados(request):
    action = request.POST.get("action")
    choice_value = request.POST.get("valor")
    new_value = request.POST.get("estado", None)

    # Para crear, el valor está en 'estado'
    if action == "create":
        choice_value = request.POST.get("estado")

    success = manage_choice(
        request=request,
        class_name='ESTADOS',
        action=action,
        choice_value=choice_value,
        new_value=new_value
    )
    return redirect('server-config')

def accion_estados_historial(request):
    action = request.POST.get("action")
    choice_value = request.POST.get("valor")
    new_value = request.POST.get("accion", None)

    # Para crear, el valor está en 'accion'
    if action == "create":
        choice_value = request.POST.get("accion")

    success = manage_choice(
        request=request,
        class_name='ACCIONES_HISTORIAL',
        action=action,
        choice_value=choice_value,
        new_value=new_value
    )
    return redirect('server-config')

def accion_configuracion(request):
    action = request.POST.get("action")
    if action == "update_dominio":
        dominio = request.POST.get("dominio")
        if dominio and actualizar_config(dominio=dominio):
            messages.success(request, 'Dominio actualizado con éxito..')
        else:
            messages.error(request, 'Error al actualizar dominio..')
    
    elif action == "update_entidad":
        entidad = request.POST.get("entidad")
        if entidad and actualizar_config(entidad_web=entidad):
            messages.success(request, 'Entidad actualizada con éxito..')
        else:
            messages.error(request, 'Error al actualizar entidad..')
    
    return redirect('server-config')

# end point para los htmx
# areas
def create_areas_htmx(request):
    form = AreaForm()
    html = render(request, 'admin/htmx/server_config_areas_new.html', {'form' : form})
    return HttpResponse(html)

def update_areas_htmx(request):
    id = request.GET.get("element")
    area = get_object_or_404(Area, pk=id)
    form = AreaForm(instance=area)
    html = render(request, 'admin/htmx/server_config_areas_edit.html', {'form' : form})
    return HttpResponse(html)

# ubicacion
def create_ubicacion_htmx(request):
    form = UbicacionForm()
    html = render(request, 'admin/htmx/server_config_ubicacion_new.html', {'form' : form})
    return HttpResponse(html)
    
def update_ubicacion_htmx(request):
    id = request.GET.get("element")
    if id:
        ubicacion = get_object_or_404(Ubicacion, pk=id)
        form = UbicacionForm(instance=ubicacion)
        html = render(request, 'admin/htmx/server_config_ubicacion_edit.html', {'form' : form})
        return HttpResponse(html)
    
    html_string = f"""<div class="p-2 border border-2 border-secondary rounded"><div class="bg-danger-subtle rounded"><h2 class="text-center p-4 m-0">Seleccione un elemento</h2></div></div>"""
    return HttpResponse(html_string)

# acciones
def create_acciones_htmx(request):
    html = render(request, 'admin/htmx/server_config_acciones_new.html')
    return HttpResponse(html)

def update_acciones_htmx(request):
    valor = request.POST.get("valor")
    if valor:
        html = render(request, 'admin/htmx/server_config_acciones_edit.html', {'valor' : valor})
        return HttpResponse(html)
    
    html_string = f"""<div class="p-2 border border-2 border-secondary rounded"><div class="bg-danger-subtle rounded"><h2 class="text-center p-4 m-0">Seleccione un elemento</h2></div></div>"""
    return HttpResponse(html_string)

# estados
def create_estados_htmx(request):
    html = render(request, 'admin/htmx/server_config_estados_new.html')
    return HttpResponse(html)

def update_estados_htmx(request):
    valor = request.POST.get("valor")
    if valor:
        html = render(request, 'admin/htmx/server_config_estados_edit.html', {'valor' : valor})
        return HttpResponse(html)
    
    html_string = f"""<div class="p-2 border border-2 border-secondary rounded"><div class="bg-danger-subtle rounded"><h2 class="text-center p-4 m-0">Seleccione un elemento</h2></div></div>"""
    return HttpResponse(html_string)

# actualizar areas y ubicaciones
def update_acciones_ubicaciones(request, id):
    tipo = request.POST.get("type")
    if tipo == "areas":
        area = Area.objects.get(id=id)
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área actualizada con éxito.')
        else:
            messages.error(request, 'Error al actualizar área.')

    elif tipo == "ubicaciones":
        ubicacion = Ubicacion.objects.get(id=id)
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación actualizada con éxito.')
        else:
            messages.error(request, 'Error al actualizar ubicación.')

    return redirect('server-config')


#############################################################################################################################
#############################                        GESTION DE USUARIOS                        #############################
#############################################################################################################################
def manage_users(request):

    context = {
        "title_page" : "Gestión de Usuarios",
        'users' : Usuario.objects.all().exclude(is_superuser = True).exclude(is_staff = True),
    }
    return render(request, 'admin/list_users.html', context)

# Cambia el estado activo de un usuario via HTMX
def  state_user(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    if not usuario.is_active:
        return HttpResponse("""<div class="badge text-bg-danger fs-6">Usuario Inactivo</div>""")
    return HttpResponse(f"""<div class="badge text-bg-success fs-6">Usuario Activo</div>""")

# Guarda el usuario despues de editar y redirige a la pagina de listar
# o devuelve una solicitud GET por htmx sin recargar la pagina
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('manage-users')
        else:
            messages.success(request, 'Error al actualizar usuario.')
            return redirect('manage-users')
    else:
        html = render(request, 'admin/htmx/users_edit.html', {'form' : UsuarioChangeForm(instance=usuario), 'user' : usuario})
        return HttpResponse(html)

# Funcion para crear Usuario
class UsuarioCreateView(CreateView):
    template_name = 'admin/create_user.html'
    form_class = UsuarioCreateForm
    success_url = reverse_lazy('create-user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = "Crear Usuario"
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario creado con éxito.')
        return response
    
    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, 'Error al crear el usuario.')
        return super().form_invalid(form)

def eliminar_usuario(request, id):
    try:
        user = get_object_or_404(Usuario, pk=id)
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    except:
        messages.error(request, 'Error al eliminar usuario.')
    return redirect('manage-users')