# restaurante-django

Proyecto de un **restaurante** con clientes, platos, mesas, reservas y pedidos.  
Para usar desde el **panel de administración**.

---
- **10 modelos** (Dirección, Cliente, Plato, etc.).
- Datos de prueba con **Faker** (crea 10 de cada modelo).
- **Fixture** (copia de seguridad) para guardar/cargar datos.
- Trabajo por **ramas** para que en GitHub se vea cada paso.

---

## Modelos (explicación completa)

### 1) `Direccion`
**dirección física completa (se asocia 1–1 con Restaurante).**

| Campo          | Tipo                     | Parámetros                 | Descripción                                      |
|----------------|--------------------------|----------------------------|--------------------------------------------------|
| `calle`        | `CharField`              | `max_length=120`           | Nombre de la calle o avenida.                    |
| `numero`       | `PositiveIntegerField`   | —                          | Número de portal/edificio (entero positivo).     |
| `ciudad`       | `CharField`              | `max_length=80`            | Ciudad.                                          |
| `codigo_postal`| `CharField`              | `max_length=10`            | Código postal (permite formatos como “E-28001”). |
| `provincia`    | `CharField`              | `max_length=80`            | Provincia.                                       |

- `__str__`: `"{calle} {numero}, {ciudad}"`

---

### 2) `Cliente`
**persona registrada que puede reservar y hacer pedidos.**

| Campo             | Tipo              | Parámetros                   | Descripción                                 |
|-------------------|-------------------|------------------------------|---------------------------------------------|
| `nombre`          | `CharField`       | `max_length=100`             | Nombre del cliente.                         |
| `email`           | `EmailField`      | `unique=True`                | Email único (sin duplicados).               |
| `telefono`        | `CharField`       | `max_length=20`, `blank=True`| Teléfono opcional.                          |
| `fecha_registro`  | `DateTimeField`   | `auto_now_add=True`          | Fecha/hora de alta automática.              |

- `__str__`: nombre del cliente.

---

### 3) `PerfilCliente`
**información extra de un cliente (relación 1–1).**

| Campo              | Tipo               | Parámetros                 | Descripción                                            |
|--------------------|--------------------|----------------------------|--------------------------------------------------------|
| `cliente`          | `OneToOneField`    | `on_delete=CASCADE`        | Enlace único a `Cliente` (si se borra, se borra perfil). |
| `alergias`         | `TextField`        | `blank=True`               | Alergias (opcional).                                   |
| `preferencias`     | `TextField`        | `blank=True`               | Preferencias (opcional).                               |
| `recibe_noticias`  | `BooleanField`     | `default=False`            | Suscripción a noticias/promos (por defecto: no).       |

- `__str__`: `"Perfil de {cliente.nombre}"`

---

### 4) `Restaurante`
**un restaurante con datos de contacto, dirección única y clientes frecuentes.**

| Campo                 | Tipo               | Parámetros                                   | Descripción                                                |
|-----------------------|--------------------|----------------------------------------------|------------------------------------------------------------|
| `nombre`              | `CharField`        | `max_length=100`                             | Nombre del restaurante.                                    |
| `telefono`            | `CharField`        | `max_length=20`                              | Teléfono.                                                  |
| `email`               | `EmailField`       | `blank=True`                                 | Email (opcional).                                          |
| `web`                 | `URLField`         | `blank=True`                                 | Web (opcional).                                            |
| `abierto`             | `BooleanField`     | `default=True`                               | Indicador de apertura.                                     |
| `direccion`           | `OneToOneField`    | `on_delete=CASCADE`                          | Enlace único a `Direccion`.                                |
| `clientes_frecuentes` | `ManyToManyField`  | `Cliente`, `blank=True`, `related_name="restaurantes_favoritos"` | Clientes habituales; acceso inverso: `cliente.restaurantes_favoritos`. |

- `__str__`: nombre del restaurante.

---

### 5) `Etiqueta`
**categorías/etiquetas para platos (ej. “vegano”, “picante”).**

| Campo       | Tipo         | Parámetros                  | Descripción                                 |
|-------------|--------------|-----------------------------|---------------------------------------------|
| `nombre`    | `CharField`  | `max_length=50`, `unique=True` | Nombre único de la etiqueta.             |
| `descripcion`| `TextField` | `blank=True`                | Texto opcional.                             |
| `color`     | `CharField`  | `max_length=10`, `default="verde"` | Color asociado (referencial).         |
| `slug`      | `SlugField`  | `unique=True`               | Identificador URL-friendly único.           |

- `__str__`: nombre de la etiqueta.

---

### 6) `Plato`
**ítem del menú de un restaurante.**

| Campo        | Tipo             | Parámetros                                   | Descripción                                       |
|--------------|------------------|----------------------------------------------|---------------------------------------------------|
| `restaurante`| `ForeignKey`     | `Restaurante`, `on_delete=CASCADE`           | Cada plato pertenece a 1 restaurante.             |
| `nombre`     | `CharField`      | `max_length=100`                             | Nombre del plato.                                 |
| `precio`     | `DecimalField`   | `max_digits=6`, `decimal_places=2`           | Precio con 2 decimales (ej. 12.50).               |
| `categoria`  | `CharField`      | `max_length=20`, `default="principal"`       | Categoría (ej. entrada/principal/postre).         |
| `disponible` | `BooleanField`   | `default=True`                               | Si está a la venta.                               |
| `etiquetas`  | `ManyToManyField`| `Etiqueta`, `blank=True`                     | Muchas etiquetas por plato (opcional).            |

- `__str__`: nombre del plato.

---

### 7) `Mesa`
 **mesa física en el restaurante.**

| Campo       | Tipo               | Parámetros                          | Descripción                                   |
|-------------|--------------------|-------------------------------------|-----------------------------------------------|
| `restaurante`| `ForeignKey`      | `Restaurante`, `on_delete=CASCADE`  | La mesa pertenece a un restaurante.           |
| `numero`    | `PositiveIntegerField` | —                                 | Número identificador.                         |
| `capacidad` | `PositiveIntegerField` | —                                 | Nº máximo de comensales.                      |
| `ubicacion` | `CharField`        | `max_length=20`, `default="interior"` | Interior/terraza, etc.                      |
| `activa`    | `BooleanField`     | `default=True`                      | Si está disponible para reservas.             |

- `__str__`: `"Mesa {numero}"`

---

### 8) `Reserva`
**reserva de una mesa por un cliente, con fecha y hora.**

| Campo     | Tipo            | Parámetros                         | Descripción                     |
|-----------|-----------------|------------------------------------|---------------------------------|
| `cliente` | `ForeignKey`    | `Cliente`, `on_delete=CASCADE`     | Quién reserva.                  |
| `mesa`    | `ForeignKey`    | `Mesa`, `on_delete=CASCADE`        | Qué mesa.                       |
| `fecha`   | `DateField`     | —                                  | Día de la reserva.              |
| `hora`    | `TimeField`     | —                                  | Hora de la reserva.             |
| `estado`  | `CharField`     | `max_length=20`, `default="pendiente"` | Estado (pendiente, confirmada…). |
| `notas`   | `TextField`     | `blank=True`                        | Observaciones (opcional).       |

- `__str__`: `"Reserva {cliente.nombre} {fecha} {hora}"`

---

### 9) `Pedido`
**compra del cliente; puede estar asociada a una reserva.**

| Campo       | Tipo            | Parámetros                                              | Descripción                                        |
|-------------|-----------------|---------------------------------------------------------|----------------------------------------------------|
| `cliente`   | `ForeignKey`    | `Cliente`, `on_delete=CASCADE`                          | Quién compra.                                      |
| `restaurante`| `ForeignKey`   | `Restaurante`, `on_delete=CASCADE`                      | Dónde compra.                                      |
| `reserva`   | `OneToOneField` | `Reserva`, `on_delete=SET_NULL`, `null=True`, `blank=True` | Enlace 1–1 opcional con `Reserva`.                 |
| `total`     | `DecimalField`  | `max_digits=8`, `decimal_places=2`, `default=0`         | Importe total.                                     |
| `pagado`    | `BooleanField`  | `default=False`                                         | Si está abonado.                                   |
| `creado`    | `DateTimeField` | `auto_now_add=True`                                     | Fecha/hora de creación.                            |
| `platos`    | `ManyToManyField`| `"Plato"`, `through="LineaPedido"`                     | M:N con `Plato` a través de `LineaPedido`.         |

- `__str__`: `"Pedido {id}"`

---

### 10) `LineaPedido`
**detalle del pedido (qué plato, cuántas unidades, precio…).***

| Campo                 | Tipo                 | Parámetros                    | Descripción                              |
|-----------------------|----------------------|-------------------------------|------------------------------------------|
| `pedido`              | `ForeignKey`         | `Pedido`, `on_delete=CASCADE` | A qué pedido pertenece.                  |
| `plato`               | `ForeignKey`         | `Plato`, `on_delete=CASCADE`  | Qué plato es.                            |
| `cantidad`            | `PositiveIntegerField`| `default=1`                   | Nº de unidades del plato.                |
| `precio_unitario`     | `DecimalField`       | `max_digits=6`, `decimal_places=2` | Precio por unidad.                  |
| `comentario`          | `CharField`          | `max_length=120`, `blank=True`| Observaciones (opcional).                |
| `descuento_porcentaje`| `PositiveIntegerField`| `default=0`                   | Descuento (%) aplicado a la línea.       |

- `__str__`: `"{cantidad}x {plato.nombre}"`

---

## Parámetros usados (qué significan)
- `max_length=N`: límite de caracteres en campos de texto.
- `unique=True`: no se permiten valores repetidos en ese campo.
- `blank=True`: el campo puede enviarse vacío en formularios.
- `null=True`: el campo puede guardar `NULL` en la base de datos.
- `default=…`: valor por defecto si no se especifica otro.
- `auto_now_add=True`: guarda automáticamente fecha/hora al crear.
- `on_delete=CASCADE`: si se borra el relacionado, se borra este registro.
- `on_delete=SET_NULL`: si se borra el relacionado, se pone a `NULL`.
- `related_name="..."`: nombre para acceder desde el otro modelo.
- `through="LineaPedido"`: M:N usando una tabla intermedia con campos extra.

---

## Resumen de relaciones
- **Uno a uno (1–1):** `Restaurante ↔ Direccion`, `PerfilCliente ↔ Cliente`, `Pedido ↔ Reserva (opcional)`
- **Uno a muchos (1–N):** `Restaurante → Plato`, `Restaurante → Mesa`, `Cliente → Reserva`, `Mesa → Reserva`, `Cliente → Pedido`, `Restaurante → Pedido`, `Pedido → LineaPedido`, `Plato → LineaPedido`
- **Muchos a muchos (M–N):** `Plato ↔ Etiqueta`, `Restaurante ↔ Cliente (clientes_frecuentes)`, `Pedido ↔ Plato (a través de LineaPedido)`

---
