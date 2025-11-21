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
    
    def clean(self):
        super().clean()
        telefono = self.cleaned_data.get('telefono')
        nombre = self.cleaned_data.get('nombre')

        if not telefono.isdigit():
            self.add_error('telefono', 'El teléfono debe contener solo números.')
        
        if len(telefono) < 9:
            self.add_error('telefono', 'El teléfono debe contener al menos 9 dígitos.')

        if(len(nombre) < 3):
            self.add_error('nombre', 'El nombre debe tener al menos 3 caracteres.')
            nombre = Restaurante.objects.filter(nombre=nombre)
        
        if (not nombre is None):
            self.add_error('nombre', 'El nombre del restaurante ya existe.')
        
        return self.cleaned_data

        
class DireccionForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['direccion']
        widgets = {
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección completa'}),
        }
    
    def clean(self):
        super().clean()
        direccion = self.cleaned_data.get('direccion')

        if direccion and len(direccion) < 10:
            self.add_error('direccion', 'La dirección debe tener al menos 10 caracteres.')

