from django import forms
from .models import Restaurante, Direccion, Cliente



class RestauranteForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)


# Formulario de creación
class RestauranteCreateForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if direccion is None:
            return direccion
       
        if Restaurante.objects.filter(direccion=direccion).exists():
            raise forms.ValidationError('Esa dirección ya está asociada a otro restaurante.')
        return direccion


# Formulario para Reserva 
class ReservaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    estado = forms.CharField(label='Estado', max_length=20, required=False, initial='pendiente')
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        from .models import Mesa
        self.fields['mesa'].queryset = Mesa.objects.filter(activa=True)


# Formulario para creación
class ReservaCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Mesa
        self.fields['mesa'].queryset = Mesa.objects.filter(activa=True)


# Formularios para PerfilCliente 
class PerfilClienteCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from .models import PerfilCliente
        used = PerfilCliente.objects.values_list('cliente_id', flat=True)
        self.fields['cliente'].queryset = Cliente.objects.exclude(id__in=used)


class PerfilClienteForm(forms.Form):
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)
    # 'recibe_noticias' removed from forms per UI requirement; field remains in model.
