from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from core.settings_web_project import ENTIDAD_WEB
from .choices import *

class Area(models.Model):
    nombre = models.CharField(max_length=15, blank=False, null=False)

    class Meta:
            verbose_name = "Área"
            verbose_name_plural = "Áreas"

    def __str__(self):
        return f"{self.id} - {self.nombre}"

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True, null=True)
    tipo_user = models.CharField(max_length=23, choices=TIPO_USER)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, default=1)
    img = models.ImageField(upload_to='users-img/', null=True, blank=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.first_name} - {self.get_tipo_user_display()}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='proveedores/', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Proveedores"

class Ubicacion(models.Model):
    # PRINCIPAL UBICACION "Almacen"
    # SECUNDARIA UBICACION "Sin Ubicacion"
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Ubicaciones"

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, default="unidad")
    stock_minimo = models.PositiveIntegerField(default=10)
    stock_actual = models.PositiveIntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        marca = self.marca if self.marca else ""
        modelo = self.modelo if self.modelo else ""
        return f"{self.nombre} {marca} {modelo} -> {self.precio_unitario}"
    
    class Meta:
        verbose_name_plural = "Productos"

class Inventario(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField(default=now)
    file = models.FileField(upload_to='inventario-files/', null=True, blank=True)
    img = models.ImageField(upload_to='inventario-imgs/', null=True, blank=True)

    def __str__(self):
            return f"{self.ubicacion} - {self.fecha}"
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
class ActivoFijo(models.Model):
    codigo_interno = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_adquisicion = models.DateField(default=now)
    estado = models.CharField(max_length=30, choices=ESTADOS, default=ESTADOS.ALMACEN)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, default=("-----------"))
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, default="")
    observaciones = models.TextField(blank=True, null=True)
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, default="")
 
    def __str__(self):
        return f"{self.ubicacion} - {ENTIDAD_WEB} - {self.codigo_interno}"

    class Meta:
        verbose_name_plural = "Activos Fijos"

class MovimientoInventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=now)
    responsable = models.CharField(max_length=100)
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} : {self.tipo.capitalize()} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        verbose_name_plural = "Movimientos de Inventario"

class SolicitudesProductos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    items = models.JSONField(default=dict)
    fecha_creacion = models.DateTimeField(default=now)
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default=ESTADOS_SOLICITUD.PENDIENTE)

    def __str__(self):
        return f"Solicitud #{self.id} - {self.usuario.first_name} {self.usuario.last_name}"

    def total_items(self):
        return sum(v['cantidad'] for v in self.items.values())
    
    class Meta:
        verbose_name_plural = "Solicitudes de Productos"
    
class HistorialActivo(models.Model):
    activo = models.ForeignKey(ActivoFijo, on_delete=models.CASCADE)
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=now)
    accion = models.CharField(max_length=25, choices=ACCIONES_HISTORIAL)
    estado = models.CharField(max_length=20, choices=ESTADO_ACCION_HISTORIAL)
    
    def __str__(self):
        return f"Activo fijo {self.activo.codigo_interno} - Usuario -> {self.responsable.first_name} {self.responsable.last_name} - {self.fecha}"
    
    class Meta:
        verbose_name_plural = "Historial de Activos"

class Alertas(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    historial = models.ForeignKey(HistorialActivo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=now)
    stock = models.PositiveIntegerField(default=10)
    stock_minimo = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.id} : {self.fecha} - {self.producto.nombre} {self.producto.marca} {self.producto.modelo}"
    
    class Meta:
        verbose_name_plural = "Alertas"