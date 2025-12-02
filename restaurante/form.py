from django import forms
from .models import Restaurante, Direccion, Cliente, Plato, PerfilCliente, Mesa


class RestauranteForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)


class RestauranteCreateForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)

    def clean(self):
        """Validación completa del formulario que añade errores a campos
        concretos usando self.add_error en lugar de lanzar ValidationError
        globales. Ejemplo de uso (similar al solicitado):
            self.add_error('idioma', 'No puede usar la Biblioteca de la Universidad de Sevilla y el idioma Fránces')
            self.add_error('biblioteca', 'No puede usar la Biblioteca de la Universidad de Sevilla y el idioma Fránces')

        Aquí validamos que la dirección no esté ya asociada a otro restaurante
        y añadimos el error al campo 'direccion' con self.add_error.
        """
        cleaned_data = super().clean()
        direccion = cleaned_data.get('direccion')

        if direccion is None:
            return cleaned_data

        if Restaurante.objects.filter(direccion=direccion).exists():
            # Añadimos el error al campo concreto en lugar de lanzar excepción
            self.add_error('direccion', 'Esa dirección ya está asociada a otro restaurante.')

        return cleaned_data


# --- Formularios de Reserva ---
class ReservaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    # para elegir la fecha 
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    # formato HH:MM para la hora
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    estado = forms.CharField(label='Estado', max_length=20, required=False, initial='pendiente')
    #para notas largas
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mesa'].queryset = Mesa.objects.filter(activa=True)


class ReservaCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mesa'].queryset = Mesa.objects.filter(activa=True)


# --- Formularios para PerfilCliente ---
class PerfilClienteCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        used = PerfilCliente.objects.values_list('cliente_id', flat=True)
        self.fields['cliente'].queryset = Cliente.objects.exclude(id__in=used)
        


class PerfilClienteForm(forms.Form):
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)

class DireccionForm(forms.ModelForm):
    """Form de Dirección.
    Widget usado:
      - numero: NumberInput para forzar entrada numérica (campo 'numero').
    """
    class Meta:
        model = Direccion
        fields = '__all__'
        widgets = {
            'numero': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }


class ClienteForm(forms.ModelForm):
    """Form de Cliente.
    Widget usado:
      - email: EmailInput para mostrar input tipo email y mejorar validación en navegador.
    """
    class Meta:
        model = Cliente
        fields = ('nombre', 'email', 'telefono')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
        }


class PlatoForm(forms.ModelForm):
    """Form de Plato.
    Widgets usados:
      - precio: NumberInput con step para decimales.
      - disponible: CheckboxInput para marcar si el plato está disponible.
    """
    class Meta:
        model = Plato
        fields = '__all__'
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}), 
            'disponible': forms.CheckboxInput(),
        }
