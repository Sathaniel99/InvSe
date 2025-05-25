from django.contrib import admin
from .models import *

admin.site.register(Usuario),
admin.site.register(Area),
admin.site.register(Categoria),
admin.site.register(Proveedor),
admin.site.register(Ubicacion),
admin.site.register(ActivoFijo),
admin.site.register(Inventario),
admin.site.register(Producto),
admin.site.register(MovimientoInventario),
admin.site.register(SolicitudesProductos)
