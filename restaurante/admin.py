from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
	pass


admin.site.register(models.Direccion)
admin.site.register(models.Cliente)
admin.site.register(models.PerfilCliente)
admin.site.register(models.Restaurante)
admin.site.register(models.Etiqueta)
admin.site.register(models.Plato)
admin.site.register(models.Mesa)
admin.site.register(models.Reserva)
admin.site.register(models.Pedido)
admin.site.register(models.LineaPedido)
