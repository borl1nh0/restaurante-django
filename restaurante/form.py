from django import forms
from .models import Restaurante

class RestauranteForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['nombre', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del restaurante'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
        }