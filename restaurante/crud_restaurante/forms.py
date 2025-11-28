from django import forms
from restaurante.models import Restaurante


class RestauranteForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['nombre', 'telefono', 'email', 'web', 'abierto', 'direccion', 'clientes_frecuentes']
