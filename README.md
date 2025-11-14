# restaurante-django

Proyecto de un **restaurante** con clientes, platos, mesas, reservas y pedidos.  
Para usar desde el **panel de administración**.

---
- **10 modelos** (Dirección, Cliente, Plato, etc.).
- Datos de prueba con **Faker** (crea 10 de cada modelo).
- **Fixture** (copia de seguridad) para guardar/cargar datos.
- Trabajo por **ramas** para que en GitHub se vea cada paso.

---

Modelos (explicación clara)

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

De los viwers me entere poco sinceramente.

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


## Requisitos de entrega
- Menú superior con links (`templates/site/partials/_navbar.html`)
- Pie de página  (`templates/site/partials/_footer.html`)
- Plantilla base que incluye ambas y define blocks `header` y `content`  (`templates/site/layout.html` + `templates/site/base.html`)
- CSS/JS/Logo cargados con `{% static %}`  (`static/site/...`)
- Herencia de todas las páginas desde `site/base.html`  (`templates/site/pages/*.html`)
- Refactor de listas con `{% include %}`  (`productos_list.html` → `includes/_producto_item.html`)
- **Template tags (≥5)**: `extends`, `include`, `url`, `if/else`, `for/empty`, `with (opcional)`
- **Operadores en if (≥5)**: `and`, `or`, `not`, `in`, `==`, `>`, `!=` (ver plantillas)
- Fechas con formato correcto: `date`, `timesince` (opcional `humanize`)
- **Template filters (≥10)**: `date`, `timesince`, `default`, `default_if_none`, `length`, `upper`, `capfirst`, `truncatechars`, `truncatewords`, `floatformat`, `pluralize`


