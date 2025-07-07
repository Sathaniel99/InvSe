from django.db import models

class TIPO_MOVIMIENTO(models.TextChoices):
        ENTRADA = 'Entrada',
        SALIDA = 'Salida',
        AJUSTE = 'Ajuste',

class ESTADOS(models.TextChoices):
    EN_USO = 'En uso',
    ALMACEN = 'Almacen',
    EN_REPARACION = 'En reparación',
    DADO_DE_BAJA = 'Dado de baja',

class ESTADOS_SOLICITUD(models.TextChoices):
    PENDIENTE = 'Pendiente',
    APROBADA = 'Aprobada',
    RECHAZADA = 'Rechazada',

class TIPO_USER(models.TextChoices):
        ECONOMICO = 'Económico',
        JEFE_AREA = 'Jefe de Área',
        ADMIN_SITIO = 'Administrador del sitio',