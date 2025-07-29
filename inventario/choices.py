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
    SIN_UBICACION = 'Sin ubicación'

class ESTADOS_SOLICITUD(models.TextChoices):
    PENDIENTE = 'Pendiente',
    APROBADA = 'Aprobada',
    RECHAZADA = 'Rechazada',

class TIPO_USER(models.TextChoices):
    ECONOMICO = 'Económico',
    JEFE_AREA = 'Jefe de Área',
    ADMIN_SITIO = 'Administrador del sitio',

class ACCIONES_HISTORIAL(models.TextChoices):
    MANTENIMIENTO = "Mantenimiento",
    MOVIMIENTO_DE_AREA = "Movimiento de Área",
    CAMBIO_DE_RESPONSABLE = "Cambio de responsable",
    DADO_DE_BAJA = 'Dado de baja',
    OTROS = "Otros"

class ESTADO_ACCION_HISTORIAL(models.TextChoices):
    COMPLETADO = "Completado",
    PROCESO = "Proceso",
    FALLIDO = "Fallido",
