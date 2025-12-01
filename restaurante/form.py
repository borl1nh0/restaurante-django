from django import forms
from .models import Restaurante, Direccion, Cliente, Plato, PerfilCliente, Mesa, Reserva
from datetime import date



# =============== FORMULARIOS DE RESTAURANTE ==================


class RestauranteForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)

    def clean(self):
        cleaned = super().clean()
        nombre = cleaned.get("nombre")
        telefono = cleaned.get("telefono")

        #Validación: teléfono solo numérico
        if telefono and not telefono.isdigit():
            self.add_error("telefono", "El teléfono solo puede contener números.")

        #Validación: nombre no repetido
        if nombre and Restaurante.objects.filter(nombre=nombre).exists():
            self.add_error("nombre", "Ya existe un restaurante con ese nombre.")

        return cleaned



class RestauranteCreateForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=True)
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True, empty_label=None)
    clientes_frecuentes = forms.ModelMultipleChoiceField(queryset=Cliente.objects.all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        direccion = cleaned_data.get('direccion')
        nombre = cleaned_data.get('nombre')

        #Validación: dirección única
        if direccion and Restaurante.objects.filter(direccion=direccion).exists():
            self.add_error('direccion', 'Esa dirección ya está asociada a otro restaurante.')

        #Validación: nombre no puede contener "prohibido"
        if nombre and "prohibido" in nombre.lower():
            self.add_error("nombre", "El nombre no puede contener la palabra 'prohibido'.")
            self.add_error("direccion", "El nombre elegido no es compatible con la dirección seleccionada.")

        return cleaned_data




# ===================== FORMULARIOS RESERVA ==================


class ReservaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Mesa.objects.none(), required=True)
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mesa'].queryset = Mesa.objects.filter(activa=True)

    def clean(self):
        cleaned = super().clean()
        fecha = cleaned.get("fecha")
        mesa = cleaned.get("mesa")

        #Validación: fecha no puede ser pasada
        if fecha and fecha < date.today():
            self.add_error("fecha", "La fecha no puede ser en el pasado.")

        #Validación: mesa debe estar activa
        if mesa and not mesa.activa:
            self.add_error("mesa", "No puede reservar una mesa que no está activa.")

        return cleaned



class ReservaCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    mesa = forms.ModelChoiceField(queryset=Mesa.objects.none(), required=True)
    fecha = forms.DateField(label='Fecha', widget=forms.SelectDateWidget())
    hora = forms.TimeField(label='Hora', widget=forms.TimeInput(format='%H:%M'))
    notas = forms.CharField(label='Notas', widget=forms.Textarea(), required=False)

    

    def clean(self):
        cleaned = super().clean()
        hora = cleaned.get("hora")
        fecha = cleaned.get("fecha")
        cliente = cleaned.get("cliente")

        #Validaci
        if hora and (hora.hour < 12 or hora.hour > 23):
            self.add_error("hora", "Solo se puede reservar de 12:00 a 23:00.")

        #Validacion no se puede duplicar reserva
        if cliente and fecha and hora:
            if Reserva.objects.filter(cliente=cliente, fecha=fecha, hora=hora).exists():
                self.add_error("cliente", "Ya tienes una reserva en esa fecha y hora.")
                self.add_error("hora", "Esta hora ya está reservada por este cliente.")

        return cleaned




# ================= FORMULARIOS PERFIL CLIENTE ===============


class PerfilClienteCreateForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True)
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        used = PerfilCliente.objects.values_list('cliente_id', flat=True)
        self.fields['cliente'].queryset = Cliente.objects.exclude(id__in=used)

    def clean(self):
        cleaned = super().clean()
        alergias = cleaned.get("alergias")
        preferencias = cleaned.get("preferencias")

        #Máximo 100 palabras
        if alergias and len(alergias.split()) > 100:
            self.add_error("alergias", "Las alergias no pueden superar 100 palabras.")

        #Si hay alergias, debe haber preferencias
        if alergias and not preferencias:
            self.add_error("preferencias", "Debes indicar preferencias si pones alergias.")
            self.add_error("alergias", "Alergias sin preferencias no es válido.")

        return cleaned



class PerfilClienteForm(forms.Form):
    alergias = forms.CharField(label='Alergias', widget=forms.Textarea(), required=False)
    preferencias = forms.CharField(label='Preferencias', widget=forms.Textarea(), required=False)

    def clean(self):
        cleaned = super().clean()
        alergias = cleaned.get("alergias", "")
        preferencias = cleaned.get("preferencias", "")

        #Alergias no puede contener "ninguna"
        if "ninguna" in alergias.lower():
            self.add_error("alergias", "No puedes escribir 'ninguna' en el campo alergias.")

        #Preferencias no pueden ser iguales a alergias
        if alergias and preferencias and alergias.strip() == preferencias.strip():
            self.add_error("preferencias", "Preferencias no pueden ser idénticas a las alergias.")
            self.add_error("alergias", "Los dos campos no pueden ser iguales.")

        return cleaned




# =================== FORMULARIO DIRECCIÓN ====================


class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = '__all__'
        widgets = {
            'numero': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }

    def clean(self):
        cleaned = super().clean()
        numero = cleaned.get("numero")
        calle = cleaned.get("calle")

        #Número mayor que 0
        if numero is not None and numero <= 0:
            self.add_error("numero", "El número debe ser mayor que 0.")

        #Calle con mínimo 3 caracteres
        if calle and len(calle) < 3:
            self.add_error("calle", "La calle debe tener al menos 3 caracteres.")

        return cleaned




# ====================== FORMULARIO CLIENTE ===================


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nombre', 'email', 'telefono')
        widgets = {'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),}
        #attrs={'placeholder': 'correo@ejemplo.com'} ponemos en el recuaddro un ejemplo de lo que tiene que poner
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        telefono = cleaned.get("telefono")

        # Email debe ser de dominio gmail.com
        if email and "@" not in email:
            self.add_error("email", "Debe contener un símbolo @ válido.")

        # Teléfono entre 9 y 15 dígitos
        if telefono and not (9 <= len(telefono) <= 15):
            self.add_error("telefono", "El teléfono debe tener entre 9 y 15 dígitos.")

        return cleaned

# ====================== FORMULARIO PLATO =====================
class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = '__all__'
        widgets = {'precio': forms.NumberInput(attrs={'step': '0.01'}),'disponible': forms.CheckboxInput(),}

    def clean(self):
        cleaned = super().clean()
        precio = cleaned.get("precio")
        nombre = cleaned.get("nombre")

        #Precio mayor a 0
        if precio is not None and precio <= 0:
            self.add_error("precio", "El precio debe ser mayor que 0.")

        #Nombre no puede contener palabras ofensivas (ejemplo)
        if nombre and "xxx" in nombre.lower():
            self.add_error("nombre", "El nombre contiene palabras no permitidas.")

        return cleaned


class RestauranteBusquedaAvanzadaForm(forms.Form):
    nombre = forms.CharField(required=False,widget=forms.TextInput(attrs={}))
    telefono = forms.CharField(required=False,widget=forms.TextInput(attrs={}))
    direccion = forms.CharField(required=False,widget=forms.TextInput(attrs={}))


    def clean(self):
        cleaned = super().clean()
        nombre = cleaned.get("nombre")
        telefono = cleaned.get("telefono")
        direccion = cleaned.get("direccion")

        # Validación 1
        if not nombre and not telefono and not direccion:
            self.add_error("nombre", "Debe rellenar al menos un campo para buscar.")
            self.add_error("telefono", "")
            self.add_error("direccion", "")
            return cleaned

        # Validación 2
        if telefono and not telefono.replace(" ", "").isdigit():
            self.add_error("telefono", "El teléfono debe contener solo números.")

        # Validación 3
        if nombre and nombre.strip() == "":
            self.add_error("nombre", "El nombre no puede estar vacío.")

        return cleaned
