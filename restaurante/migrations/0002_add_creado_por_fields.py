# Generated manually to add creado_por fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("restaurante", "0002_remove_mesa_capacidad_remove_mesa_ubicacion_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="creado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="clientes_creados",
                to="restaurante.usuario",
            ),
        ),
        migrations.AddField(
            model_name="reserva",
            name="creado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reservas_creadas",
                to="restaurante.usuario",
            ),
        ),
        migrations.AddField(
            model_name="pedido",
            name="creado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pedidos_creados",
                to="restaurante.usuario",
            ),
        ),
    ]
