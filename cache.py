from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import UbicacionForm, AreaForm, UsuarioForm
from .models import Usuario

def users_edit(request, id=None):
    """
    Vista para editar usuarios. Maneja la creación, edición y eliminación de usuarios.

    Args:
        request (HttpRequest): La solicitud HTTP.
        id (int, optional): El ID del usuario a editar. Defaults to None.
Returns:
        HttpResponse: La respuesta HTTP.
    """
    # Si la solicitud es de tipo POST, procesamos los datos del formulario
    if request.method == "POST":
        # Obtenemos el tipo de operación a realizar
        tipo = request.POST.get("type")
        try:
            if tipo == "create":
                # Creamos un formulario de usuario con los datos de la solicitud
                form = UsuarioForm(request.POST)
                if form.is_valid():
                    # Si el formulario es válido, guardamos los datos
                    form.save()
                    # Mostramos un mensaje de éxito
                    messages.success(request, 'Usuario creado con éxito.')
                else:
                    # Si el formulario no es válido, mostramos un mensaje de error
                    messages.error(request, 'Error al crear el usuario.')
            elif tipo == "edit":
                # Obtenemos el usuario a editar
                user = get_object_or_404(Usuario, pk=id)
                # Creamos un formulario de usuario con los datos de la solicitud y la instancia del usuario
                form = UsuarioForm(request.POST, instance=user)
                if form.is_valid():
                    # Si el formulario es válido, guardamos los datos
                    form.save()
                    # Mostramos un mensaje de éxito
                    messages.success(request, 'Usuario editado con éxito.')
                else:
                    # Si el formulario no es válido, mostramos un mensaje de error
                    messages.error(request, 'Error al editar el usuario.')
            else:
                # Obtenemos el usuario a eliminar
                user = get_object_or_404(Usuario, pk=id)
                # Eliminamos el usuario
                user.delete()
                # Mostramos un mensaje de éxito
                messages.success(request, 'Usuario eliminado con éxito.')
        except Exception as e:
            # Si ocurre un error, mostramos un mensaje de error
            messages.error(request, f'Ocurrió un error: {str(e)}')
        # Redirigimos a la página de edición de usuarios
        return redirect('users_edit')  # Asegúrate de tener una URL con este nombre en tus urls.py

    # Si la solicitud no es de tipo POST, renderizamos la página de edición de usuarios
    context = {
        "title_page": "Editar usuarios",
    }
    return render(request, 'pagina.html', context)