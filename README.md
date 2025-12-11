# restaurante-django

Proyecto de un **restaurante** con clientes, platos, mesas, reservas y pedidos.  
Para usar desde el **panel de administración**.

---
- **10 modelos** (Dirección, Cliente, Plato, etc.).
- Datos de prueba con **Faker** (crea 10 de cada modelo).
- **Fixture** (copia de seguridad) para guardar/cargar datos.
- Trabajo por **ramas** para que en GitHub se vea cada paso.

---
Modelos 

# 1) Dirección

calle (CharField, max_length=120): nombre de la calle.

numero (PositiveIntegerField): número del portal.

ciudad (CharField, 80).

codigo_postal (CharField, 10): se usa Char para permitir formatos con letras.

provincia (CharField, 80).

Uso: una dirección se asigna a un restaurante (OneToOne).

# 2) Cliente

nombre (CharField, 100).

email (EmailField, unique=True): no se puede repetir.

telefono (CharField, 20, blank=True): opcional.

fecha_registro (DateTimeField, auto_now_add=True): fecha de alta automática.

# 3) PerfilCliente

cliente (OneToOne a Cliente, on_delete=CASCADE): si borro el cliente, se borra su perfil.

alergias (TextField, blank=True).

preferencias (TextField, blank=True).

recibe_noticias (BooleanField, default=False).

# 4) Restaurante

nombre (CharField, 100).

telefono (CharField, 20).

email (EmailField, blank=True).

web (URLField, blank=True).

abierto (BooleanField, default=True).

direccion (OneToOne a Dirección, CASCADE).

clientes_frecuentes (ManyToMany a Cliente, blank=True, related_name="restaurantes_favoritos").

# 5) Etiqueta

nombre (CharField, 50, unique=True): p.ej. “vegano”, “picante”.

descripcion (TextField, blank=True).

color (CharField, 10, default="verde").

slug (SlugField, unique=True): nombre apto para URL.

# 6) Plato

restaurante (ForeignKey a Restaurante, CASCADE).

nombre (CharField, 100).

precio (DecimalField, max_digits=6, decimal_places=2): dinero con 2 decimales.

categoria (CharField, 20, default="principal"): entrada, principal, postre…

disponible (BooleanField, default=True).

etiquetas (ManyToMany a Etiqueta, blank=True).

# 7) Mesa

restaurante (ForeignKey a Restaurante, CASCADE).

numero (PositiveIntegerField).

capacidad (PositiveIntegerField).

ubicacion (CharField, 20, default="interior").

activa (BooleanField, default=True).

# 8) Reserva

cliente (ForeignKey a Cliente, CASCADE).

mesa (ForeignKey a Mesa, CASCADE).

fecha (DateField) y hora (TimeField).

estado (CharField, 20, default="pendiente"): pendiente/confirmada/cancelada.

notas (TextField, blank=True).

# 9) Pedido

cliente (ForeignKey a Cliente, CASCADE).

restaurante (ForeignKey a Restaurante, CASCADE).

reserva (OneToOne a Reserva, SET_NULL, null=True, blank=True): un pedido puede estar ligado a una reserva; si se borra la 
reserva, queda NULL.

total (DecimalField, 8,2, default=0).

pagado (BooleanField, default=False).

creado (DateTimeField, auto_now_add=True).

platos (ManyToMany a Plato, through="LineaPedido"): relación con tabla intermedia.

# 10) Línea de Pedido (tabla intermedia con extras)
pedido (ForeignKey a Pedido, CASCADE).

plato (ForeignKey a Plato, CASCADE).

cantidad (PositiveIntegerField, default=1).

precio_unitario (DecimalField, 6,2): precio del plato en ese momento.

comentario (CharField, 120, blank=True).

descuento_porcentaje (PositiveIntegerField, default=0).



# self.stdout.write(self.style.SUCCESS -> Nos avisa por consola que se a creado bien
# on_delete=models.SET_NULL es para que si se anula un pedido, no lo borre de la base de datos( tenia pensado hacer una pagina de desperdicios pero se me iba de las manos)

from django.db.models import Q, Count, Sum, Avg --> herramientas para construir consultas (QuerySets) 

## Validaciones
- En la app revisamos algunas cosas para que los datos no se líen ni haya errores.

- Lo que hace la base de datos sola:

- Algunos números, como el número de mesa o la cantidad de un pedido, tienen que ser positivos (no puedes poner -2 mesas ni 0 en un pedido).

- La dirección sólo puede tenerla un restaurante, no se comparte entre varios.

- Los precios se guardan con dos decimales, para no liar los cálculos de dinero.

- Lo que revisa el formulario antes de guardar:

- Cuando creas un restaurante, te pide nombre, teléfono y dirección, pero si la dirección ya está ocupada por otro restaurante, te salta un aviso y no te deja.

- Al reservar, eliges cliente, mesa, fecha y hora.

- Si intentas hacer otro perfil para el mismo cliente, no te deja, sólo puede haber uno por cliente.


## Widgets usados en los formularios

- `SelectDateWidget` — usado en `ReservaForm`/`ReservaCreateForm` (campo `fecha`).
	- Selector de fecha por campos día/mes/año

- `TimeInput(format='%H:%M')` — usado en `ReservaForm`/`ReservaCreateForm` (campo `hora`).
	- Entrada de hora con formato HH:MM 

- `Textarea` — usado en `ReservaForm` (campo `notas`) y en `PerfilClienteForm`/`PerfilClienteCreateForm` (campos `alergias`, `preferencias`).
	-texto para notas

- `EmailInput` — usado en `ClienteForm` (campo `email`).
	- Input tipo email 

- `NumberInput` — usado en `DireccionForm` (campo `numero`) y en `PlatoForm` (campo `precio` con `step='0.01'`).
	-Input numérico; en `precio` se añade `step` para decimales."

- `CheckboxInput` — usado en `PlatoForm` (campo `disponible`).
	-Checkbox para marcar si un plato está disponible (True/False)."
## -------------------------------------------------------------------------------------------- ##
## Tipos de usuario y accesos

En la aplicación se usan principalmente **dos roles de trabajo**:

- **Gerente** (grupo "Gerentes")
	- Acceso al panel de gestión completo desde la web:
		- CRUD de **Restaurantes**, **Clientes**, **Direcciones**, **Perfiles de cliente**, **Platos**, **Reservas** y **Pedidos**.
	- Ve todos los bloques de la página de inicio y puede entrar en todas las opciones de menú relacionadas con gestión.

- **Empleado** (grupo "Empleados")
	- Puede ver el listado de **Platos** y trabajar con **Reservas** y **Pedidos** (crear y modificar los que haga falta).
	- No puede crear ni borrar **Restaurantes**, **Clientes**, **Direcciones** ni tocar la configuración general.
	- En el menú ve: **Inicio**, **Restaurantes**, **Platos**, **Pedidos** y **Búsqueda avanzada**, pero sin opciones de administración completas.

Además, existe el **superusuario de Django** (administrador técnico) que se usa solo para tareas internas en `/admin`, pero no se considera un rol funcional de la aplicación.



## -------------------------------------------------------------------------------------------- ##
## Cómo ejecutar en Linux

git clone https://github.com/borl1nh0/restaurante-django

py -m venv myvenv

myvenv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py loaddata backups\datos.json   # o: python manage.py seed_10

python manage.py runserver

## Cómo ejecutar en Windows (lo hice en windows)

git clone https://github.com/borl1nh0/restaurante-django

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -> Se usa para activar un entorno virtual ya que por politicas de windows lo bloquea, de esta forma hacemos una "excepcion".

myvenv\Scripts\activate 

pip install -r requirements.txt

python manage.py migrate

python manage.py loaddata backups\datos.json  o: python manage.py seed_10

python manage.py runserver