from django.contrib.auth.models import AbstractUser
from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=15, blank=False, null=False)

class Usuario(AbstractUser):
    TIPO_USER = (
        ('economico', 'Económico'),
        ('jefe_area', 'Jefe de Área'),
        ('admin_sitio', 'Administrador del sitio'),
    )
    telefono = models.CharField(max_length=15, blank=True, null=True)
    tipo_user = models.CharField(max_length=11, choices=TIPO_USER)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

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

    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    # PRINCIPAL UBICACION "Almacen"

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
        return f"{self.categoria} - {self.nombre}"
    
    class Meta:
        verbose_name_plural = "Productos"

class ActivoFijo(models.Model):
    codigo_interno = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_adquisicion = models.DateField()
    valor_adquisicion = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=30, choices=[
        ('en_uso', 'En uso'),
        ('almacen', 'Almacen'),
        ('en_reparacion', 'En reparación'),
        ('dado_de_baja', 'Dado de baja')
    ])
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"

    class Meta:
        verbose_name_plural = "Activos Fijos"

class Inventario(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
            return f"{self.codigo}"
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=100)
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        verbose_name_plural = "Movimientos de Inventario"

class SolicitudesProductos(models.Model):
    estado_solicitud = {
        'aceptada' : 'Aceptada',
        'en_espera' : 'En espera',
        'denegada' : 'Denegada',
    }
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    estado = models.CharField(choices=estado_solicitud)

    class Meta:
        verbose_name = "Solicitud de productos"
        verbose_name_plural = "Solicitudes de productos"

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - [ {self.cantidad} - {self.producto.nombre} ] - {self.ubicacion}"
    