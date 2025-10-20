from django.contrib import messages
from django.db.models import Max
from django.conf import settings
from .models import ActivoFijo
from pathlib import Path
import importlib
import json
import re

# obtiene la solicitud guardada en la session
def get_solicitud_sesion(request):
    return request.session.get('solicitud', {})

# guarda la solicitud guardada en la session
def guardar_solicitud_sesion(request, solicitud):
    request.session['solicitud'] = solicitud
    request.session.modified = True

# convierte la solicitud guardada en la session en json
def parse_items_json(items_json_str):
    if isinstance(items_json_str, dict):
        return items_json_str
    try:
        return json.loads(items_json_str)
    except Exception:
        return {}
    
# genera los numeros de los inventarios de Activos Fijos
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

# convertir de pesos cubanos CUP a dolar USD
def convert_CUP_to_USD(cant, CUP):
    return int(cant/CUP)
# convertir de dolar USD a pesos cubanos CUP
def convert_USD_to_CUP(cant, CUP):
    return int(cant*CUP)

# convertir un numero a expresiones de mil
# 3000000 --> 3 000 000
# 3000000.40 --> 3 000 000.40
# 3000000,40 --> 3 000 000,40
def convert_num(num):
    # Initialize decimal part
    b = "00"
    
    # Handle input - replace comma with dot for consistent splitting
    num = str(num).replace(",", ".")
    
    # Split into integer and decimal parts
    if "." in num:
        parts = num.split(".")
        a = parts[0]
        b = parts[1] if len(parts) > 1 else "00"
    else:
        a = num
    
    # Format integer part with spaces
    num_str = a.replace(" ", "")
    reversed_str = num_str[::-1]
    chunks = [reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)]
    a = " ".join(chunks)[::-1]
    
    # Ensure decimal part has 2 digits
    b = b.ljust(2, "0")[:2]
    
    return f"{a},{b}"

def manage_choice(request, class_name, action, choice_value=None, new_value=None):
    """
    Maneja todas las operaciones CRUD para TextChoices de Django
    """
    try:
        module = importlib.import_module('inventario.choices')
        
        if not hasattr(module, class_name):
            messages.error(request, f'{class_name} no encontrado.')
            return False

        choice_class = getattr(module, class_name)
        
        # Obtener los choices actuales como lista de tuplas (value, label)
        current_choices = [(choice.value, choice.label) for choice in choice_class]
        
        if action == "create":
            action = "crear elemento"
            if any(choice[0] == choice_value for choice in current_choices):
                messages.warning(request, f'El elemento "{choice_value}" ya existe..')
                return False
            current_choices.append((choice_value, choice_value))
            
        elif action == "update":
            action = "actualizar elemento"
            if not new_value:
                messages.error(request, 'Se requiere un nuevo valor para actualizar..')
                return False
                
            current_choices = [
                (new_value, new_value) if value == choice_value else (value, label)
                for value, label in current_choices
            ]
            
        elif action == "delete":
            action = "eliminar elemento"
            original_length = len(current_choices)
            current_choices = [choice for choice in current_choices if choice[0] != choice_value]
            if len(current_choices) == original_length:
                messages.warning(request, f'Elemento "{choice_value}" no encontrado..')
                return False

        # Reconstruir la clase de choices
        new_class_content = f"class {class_name}(models.TextChoices):\n"
        for value, label in current_choices:
            new_class_content += f"    {value.upper().replace(' ', '_')} = '{value}', '{label}'\n"
        
        # Leer y actualizar el archivo
        module_path = module.__file__
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la clase completa
        pattern = fr"class {class_name}\(models\.TextChoices\):.*?(?=\n\n|\Z)"
        new_content = re.sub(pattern, new_class_content.strip(), content, flags=re.DOTALL)
        
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Recargar el módulo
        importlib.reload(module)
        
        messages.success(request, f'Operación {action} realizada con éxito..')
        return True
        
    except Exception as e:
        messages.error(request, f'Error al {action}: {str(e)}..')
        return False

def actualizar_config(key_project=None, entidad_web=None, precio_usd=None, dominio=None, img_web=None):
    archivo = Path(settings.BASE_DIR) / 'core' / 'settings_web_project.py'
    try:
        if not Path(archivo).exists():
            raise FileNotFoundError(f"El archivo {archivo} no existe.")
        
        with open(archivo, 'r') as f:
            contenido = f.read()
        
        def actualizar_valor(contenido, variable, nuevo_valor):
            if isinstance(nuevo_valor, str):
                patron = fr"^{variable} = .*$"
                sustituto = f"{variable} = '{nuevo_valor}'"
            else:
                patron = fr"^{variable} = .*$"
                sustituto = f"{variable} = {nuevo_valor}"
            
            return re.sub(patron, sustituto, contenido, flags=re.MULTILINE)
        
        # Actualizar cada parámetro si se proporcionó
        if key_project is not None:
            contenido = actualizar_valor(contenido, 'KEY_PROJECT_INVSE', key_project)
        
        if entidad_web is not None:
            contenido = actualizar_valor(contenido, 'ENTIDAD_WEB', entidad_web)
        
        if precio_usd is not None:
            contenido = actualizar_valor(contenido, 'PRECIO_USD', precio_usd)
        
        if dominio is not None:
            contenido = actualizar_valor(contenido, 'DOMINIO', dominio)

        if img_web is not None:
            contenido = actualizar_valor(contenido, 'IMG_WEB', img_web)
        
        with open(archivo, 'w') as f:
            f.write(contenido)
        
        return True
    
    except Exception as e:
        print(f"Error al actualizar configuración: {str(e)}")
        return False