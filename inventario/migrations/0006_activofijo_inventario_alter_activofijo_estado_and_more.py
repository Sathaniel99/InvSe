# Generated by Django 5.2.1 on 2025-05-30 17:30

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_remove_inventario_codigo_remove_inventario_producto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activofijo',
            name='inventario',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='inventario.inventario'),
        ),
        migrations.AlterField(
            model_name='activofijo',
            name='estado',
            field=models.CharField(choices=[('en_uso', 'En uso'), ('en_reparacion', 'En reparación'), ('dado_de_baja', 'Dado de baja'), ('almacen', 'Almacen')], max_length=30),
        ),
        migrations.AlterField(
            model_name='inventario',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2025, 5, 30, 13, 30, 30, 141556)),
        ),
        migrations.AlterField(
            model_name='solicitudesproductos',
            name='fecha_creacion',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 30, 13, 30, 30, 143063)),
        ),
    ]
