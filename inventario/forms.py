from django import forms
from .models import Categoria, Proveedor, Ubicacion, ActivoFijo, Producto, MovimientoInventario

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
            'codigo_interno', 'nombre', 'categoria', 'marca', 'modelo',
            'descripcion', 'fecha_adquisicion', 'valor_adquisicion',
            'estado', 'ubicacion', 'proveedor', 'imagen', 'observaciones'
        ]
        widgets = {
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_adquisicion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'codigo_interno': 'Código Interno',
            'nombre': 'Nombre del Activo',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'descripcion': 'Descripción',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'valor_adquisicion': 'Valor de Adquisición',
            'estado': 'Estado',
            'ubicacion': 'Ubicación',
            'proveedor': 'Proveedor',
            'imagen': 'Imagen',
            'observaciones': 'Observaciones',
        }

# --- Formulario: Producto ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'descripcion', 'unidad_medida',
            'stock_minimo', 'stock_actual', 'precio_unitario',
            'proveedor', 'imagen'
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
        labels = {
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'unidad_medida': 'Unidad de Medida',
            'stock_minimo': 'Stock Mínimo',
            'stock_actual': 'Stock Actual',
            'precio_unitario': 'Precio Unitario',
            'proveedor': 'Proveedor',
            'imagen': 'Imagen',
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