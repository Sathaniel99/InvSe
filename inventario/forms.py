from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# --- Formulario: Categoria ---
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
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
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre de la Ubicación',
            'descripcion': 'Descripción',
        }

# --- Formulario: ActivoFijo ---
class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = [
            'codigo_interno',
            'descripcion',
            'fecha_adquisicion',
            'valor_adquisicion',
            'estado',
            'ubicacion',
            'observaciones'
        ]
        widgets = {
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_adquisicion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'codigo_interno': 'Código Interno',
            'descripcion': 'Descripción',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'valor_adquisicion': 'Valor de Adquisición',
            'estado': 'Estado',
            'ubicacion': 'Ubicación',
            'observaciones': 'Observaciones',
        }

# --- Formulario: Area ---
class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = [
            'nombre',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
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
            'descripcion',
            'unidad_medida',
            'stock_minimo',
            'stock_actual',
            'precio_unitario',
            'proveedor',
            'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

# --- Formulario: MovimientoInventario ---
class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo', 'cantidad', 'responsable', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'producto': 'Producto',
            'tipo': 'Tipo de Movimiento',
            'cantidad': 'Cantidad',
            'responsable': 'Responsable',
            'motivo': 'Motivo del Movimiento',
        }

# --- Formulario: Usuarios ---
class UsuarioCreationForm(UserCreationForm):
    telefono = forms.CharField(max_length=15, required=False, label="Teléfono")
    tipo_user = forms.ChoiceField(choices=Usuario.TIPO_USER, label="Tipo de Usuario")

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'telefono', 'tipo_user')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telefono = self.cleaned_data['telefono']
        user.tipo_user = self.cleaned_data['tipo_user']
        if commit:
            user.save()
        return user


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'tipo_user',
            'is_active',
            'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_user': forms.Select(attrs={'class': 'form-select'},choices=Usuario.TIPO_USER,),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }