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
        help_texts = {
            'direccion': 'Crea primero una direccion valida.',
        }
        
class DireccionForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['direccion']
        widgets = {
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección completa'}),
        }