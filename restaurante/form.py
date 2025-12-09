from django import forms
from .models import Restaurante, Direccion, Cliente, Plato, PerfilCliente, Mesa, Reserva
from datetime import date
from django.db.models import Q



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

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if direccion is None:
            return direccion

        if Restaurante.objects.filter(direccion=direccion).exists():
            raise forms.ValidationError('Esa dirección ya está asociada a otro restaurante.')
        return direccion

    def clean(self):
        cleaned = super().clean()
        nombre = cleaned.get("nombre")
        telefono = cleaned.get("telefono")

        # Validación: teléfono solo numérico
        if telefono and not telefono.isdigit():
            self.add_error("telefono", "El teléfono solo puede contener números.")

        # Validación: nombre único
        if nombre and Restaurante.objects.filter(nombre=nombre).exists():
            self.add_error("nombre", "Ya existe un restaurante con ese nombre.")

        # Validación: longitudes máximas (defensivo, además del modelo)
        if nombre and len(nombre) > 100:
            self.add_error("nombre", "El nombre no puede superar 100 caracteres.")
        if telefono and len(telefono) > 20:
            self.add_error("telefono", "El teléfono no puede superar 20 caracteres.")

        return cleaned


# --- Formularios de Reserva ---
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
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'disponible': forms.CheckboxInput(),
        }

    def clean(self):
        cleaned = super().clean()
        nombre = cleaned.get("nombre")
        precio = cleaned.get("precio")
        restaurante = cleaned.get("restaurante")

        
        if precio is not None and precio <= 0:
            self.add_error("precio", "El precio debe ser mayor que 0.")

        
        if nombre is not None and nombre.strip() == "":
            self.add_error("nombre", "El nombre no puede estar vacío.")
        if nombre and len(nombre) > 100:
            self.add_error("nombre", "El nombre no puede superar 100 caracteres.")

       
        if restaurante and nombre:
            qs = Plato.objects.filter(restaurante=restaurante, nombre=nombre)
            
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("nombre", "Ya existe un plato con ese nombre en este restaurante.")

        return cleaned

#====================== Busqueda avanzada==================
class RestauranteBusquedaAvanzadaForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        required=False,
        label="Nombre del Restaurante",
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Sabor Andaluz'})
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 600123456'})
    )
    
    direccion = forms.CharField(
        max_length=200,
        required=False,
        label="Dirección (Calle, Ciudad o C.P.)",
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Sevilla o 41001'})
    )

    def clean(self):
        cleaned = super().clean()

        nombre = cleaned.get("nombre")
        telefono = cleaned.get("telefono")
        direccion = cleaned.get("direccion")

        
        if not nombre and not telefono and not direccion:
            mensaje = "Debes rellenar al menos un campo."
            self.add_error("nombre", mensaje)
            self.add_error("telefono", mensaje)
            self.add_error("direccion", mensaje)

        else:
            
            if telefono and not telefono.isdigit():
                self.add_error("telefono", "El teléfono solo puede contener números.")

            
            if nombre is not None and nombre.strip() == "":
                self.add_error("nombre", "No puedes poner solo espacios.")

            if direccion is not None and direccion.strip() == "":
                self.add_error("direccion", "No puedes poner solo espacios.")

        return cleaned
