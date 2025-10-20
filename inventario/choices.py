from django.db import models

class TIPO_MOVIMIENTO(models.TextChoices):
    ENTRADA = 'Entrada',
    SALIDA = 'Salida',
    AJUSTE = 'Ajuste',

class ESTADOS(models.TextChoices):
    EN_USO = 'En uso', 'En Uso'
    ALMACEN = 'Almacen', 'Almacen'
    EN_REPARACIÓN = 'En reparación', 'En Reparacion'
    DADO_DE_BAJA = 'Dado de baja', 'Dado De Baja'
    SIN_UBICACIÓN = 'Sin ubicación', 'Sin Ubicacion'

class ESTADOS_SOLICITUD(models.TextChoices):
    PENDIENTE = 'Pendiente',
    APROBADA = 'Aprobada',
    RECHAZADA = 'Rechazada',

class TIPO_USER(models.TextChoices):
    TRABAJADOR = 'Trabajador',
    ECONOMICO = 'Económico',
    JEFE_AREA = 'Jefe de Área',
    ADMIN_SITIO = 'Administrador del sitio',

class ACCIONES_HISTORIAL(models.TextChoices):
    MANTENIMIENTO = 'Mantenimiento', 'Mantenimiento'
    MOVIMIENTO_DE_ÁREA = 'Movimiento de Área', 'Movimiento De Area'
    CAMBIO_DE_RESPONSABLE = 'Cambio de responsable', 'Cambio De Responsable'
    DADO_DE_BAJA = 'Dado de baja', 'Dado De Baja'
    OTROS = 'Otros', 'Otros'

class ESTADO_ACCION_HISTORIAL(models.TextChoices):
    COMPLETADO = "Completado",
    PROCESO = "Proceso",
    FALLIDO = "Fallido",

# 'array' es la lista de valores a excluir
# 'choice' es el choice a devolver
def get_choices_filtrados(choice, array):
    # Devolver las opciones filtradas
    return [
        (estado.value, estado.label)
        for estado in choice
        if estado.value not in array
    ]
