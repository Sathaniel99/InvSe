from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .utils import generar_numero_inventario
from core.settings_web_project import DOMINIO, ENTIDAD_WEB

# --- Formulario: Categoria ---
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
        }

# --- Formulario: Proveedor ---
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'nombre': 'Nombre del Proveedor',
            'contacto': 'Contacto',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'direccion': 'Dirección',
        }

# --- Formulario: Ubicacion ---
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'descripcion', 'area']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
            'area': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            'nombre': 'Nombre de la Ubicación',
            'descripcion': 'Descripción',
            'area': 'Área',
        }

    def __init__(self, *args, **kwargs):
        super(UbicacionForm, self).__init__(*args, **kwargs)
        self.fields['area'].required = False
        self.fields['area'].empty_label = "Seleccione un Área"

# --- Formulario: ActivoFijo ---
class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = [
            'producto',
            'descripcion',
            'fecha_adquisicion',
            'estado',
            'serial_number',
            'ubicacion',
            'observaciones'
        ]
        widgets = {
            'producto' : forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
            'fecha_adquisicion': forms.DateInput(format='%Y-%m-%d',attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'estado': forms.Select(attrs={'class': 'form-select form-select-sm pe-none'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select form-select-sm pe-none'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }
        labels = {
            'producto' : 'Producto',
            'descripcion': 'Descripción',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'estado': 'Estado',
            'serial_number' : 'Número de serie',
            'ubicacion': 'Ubicación',
            'observaciones': 'Observaciones',
        }

        def __init__(self, *args, **kwargs):
            super(ActivoFijoForm, self).__init__(*args, **kwargs)
            self.fields['serial_number'].initial = generar_numero_inventario()

# --- Formulario: Area ---
class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = [
            'nombre',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'nombre': 'Nombre del Área',
        }

# --- Formulario: Producto ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'categoria',
            'marca',
            'modelo',
            'descripcion',
            'unidad_medida',
            'stock_minimo',
            'stock_actual',
            'precio_unitario',
            'proveedor',
            'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'categoria': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'marca': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'style' : 'field-sizing: content;'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'proveedor': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor'].queryset = Proveedor.objects.all().order_by('nombre')

# --- Formulario: MovimientoInventario ---
class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo', 'cantidad', 'responsable', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'tipo': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }
        labels = {
            'producto': 'Producto',
            'tipo': 'Tipo de Movimiento',
            'cantidad': 'Cantidad',
            'responsable': 'Responsable',
            'motivo': 'Motivo del Movimiento',
        }

# --- Formulario: Usuarios ---
class UsuarioCreateForm(UserCreationForm):
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        label="Área",
        required=True,
        empty_label=None,  # Esto evita que Django añada el "---------" automáticamente
    )
    tipo_user = forms.ChoiceField(
        choices=TIPO_USER,
        label="Tipo de Usuario",
        required=True,
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'area',
            'tipo_user'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm rounded-end'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm rounded-end'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm rounded-end'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm rounded-end'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Atributos adicionales para los select
        self.fields['area'].widget.attrs.update({'class': 'form-select form-select-sm rounded-end'})
        self.fields['tipo_user'].widget.attrs.update({'class': 'form-select form-select-sm rounded-end'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control form-control-sm rounded-end'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control form-control-sm rounded-end'})

        # Help texts
        self.fields['first_name'].help_text = 'Nombre/s real del usuario.'
        self.fields['last_name'].help_text = 'Apellidos del usuario.'
        self.fields['email'].help_text = f'Se recomienda correo: "@{DOMINIO}"'
        self.fields['area'].help_text = 'Área a ubicar el trabajador.'
        self.fields['tipo_user'].help_text = f'Función que ejercerá el usuario en la plataforma de la entidad {ENTIDAD_WEB}.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.area_id = self.cleaned_data['area'].id
        user.tipo_user = self.cleaned_data['tipo_user']
        if commit:
            user.save()
        return user

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'tipo_user', 'area', 'img')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'img': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super(UsuarioChangeForm, self).__init__(*args, **kwargs)
        self.fields['tipo_user'] = forms.ChoiceField(choices=TIPO_USER, widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
        self.fields['area'] = forms.ModelChoiceField(queryset=Area.objects.all(), widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))