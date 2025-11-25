from django import forms
from .models import Restaurante, Direccion, Cliente


# Formulario basado en forms.Form para edición completa
class RestauranteForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    email = forms.EmailField(label='Email', required=False)
    web = forms.URLField(label='Web', required=False)
    abierto = forms.BooleanField(label='Abierto', required=False, initial=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)


# Formulario de creación: excluye abierto, web y email según petición
class RestauranteCreateForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if direccion is None:
            return direccion
        # Si la dirección ya está asociada a un restaurante, error
        if Restaurante.objects.filter(direccion=direccion).exists():
            raise forms.ValidationError('Esa dirección ya está asociada a otro restaurante.')
        return direccion
