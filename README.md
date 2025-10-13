<!--
# restaurante-django


# Proyecto de un restaurante con clientes, platos, mesas, reservas y pedidos.  


---

¿Que trae?
- **10 modelos** con nombres (Dirección, Cliente, Plato, etc.).
- Datos de prueba con **Faker** (crea 10 de cada cosa).
- Copia de seguridad de los datos (fixture).
- Ramas separadas para que en GitHub se vea cada paso que di.


Modelos
1. Direccion
Descripción general: Representa una dirección física completa, utilizada principalmente para asociar ubicaciones a restaurantes (relación uno a uno). Es una entidad independiente pero vinculada.

calle: models.CharField(max_length=120)

Tipo: Cadena de texto.
Parámetros: max_length=120 (límite de 120 caracteres para evitar entradas excesivamente largas).
Descripción: Nombre de la calle o avenida donde se encuentra la dirección.
numero: models.PositiveIntegerField()

Tipo: Entero positivo.
Parámetros: Ninguno adicional (valor mínimo implícito de 0, pero típicamente >0).
Descripción: Número de la puerta o edificio en la calle.
ciudad: models.CharField(max_length=80)

Tipo: Cadena de texto.
Parámetros: max_length=80.
Descripción: Nombre de la ciudad donde se ubica la dirección.
codigo_postal: models.CharField(max_length=10)

Tipo: Cadena de texto (para permitir formatos como "28001" o "E-28001").
Parámetros: max_length=10.
Descripción: Código postal de la zona.
provincia: models.CharField(max_length=80)

Tipo: Cadena de texto.
Parámetros: max_length=80.
Descripción: Nombre de la provincia o estado.
str: Método que devuelve una cadena formateada como "{calle} {numero}, {ciudad}" para una representación legible.
------------------------------------------------------------------------------------------------------------------

2. Cliente
Descripción general: Representa a un cliente registrado en el sistema, con información básica de contacto. Puede tener un perfil extendido y relaciones con reservas, pedidos y restaurantes favoritos.

nombre: models.CharField(max_length=100)

Tipo: Cadena de texto.
Parámetros: max_length=100.
Descripción: Nombre completo del cliente.
email: models.EmailField(unique=True)

Tipo: Campo de email validado por Django.
Parámetros: unique=True (no se permiten emails duplicados).
Descripción: Dirección de email única para contacto y autenticación.
telefono: models.CharField(max_length=20, blank=True)

Tipo: Cadena de texto.
Parámetros: max_length=20, blank=True (opcional, puede estar vacío).
Descripción: Número de teléfono para contacto (formato libre, e.g., "+34 123 456 789").
fecha_registro: models.DateTimeField(auto_now_add=True)

Tipo: Fecha y hora.
Parámetros: auto_now_add=True (se establece automáticamente al crear el registro, no editable).
Descripción: Fecha y hora en que se registró el cliente.
str: Método que devuelve el nombre del cliente.
------------------------------------------------------------------------------------------------------------------

3. PerfilCliente
Descripción general: Extensión uno a uno del modelo Cliente, para almacenar información personalizada como preferencias y alergias. Se elimina si se elimina el cliente asociado (CASCADE).

cliente: models.OneToOneField(Cliente, on_delete=models.CASCADE)

Tipo: Relación uno a uno.
Parámetros: on_delete=models.CASCADE (elimina el perfil si se elimina el cliente).
Descripción: Referencia única al cliente asociado.
alergias: models.TextField(blank=True)

Tipo: Texto largo.
Parámetros: blank=True (opcional).
Descripción: Descripción de alergias alimentarias del cliente (e.g., "alergia a nueces").
preferencias: models.TextField(blank=True)

Tipo: Texto largo.
Parámetros: blank=True.
Descripción: Preferencias dietéticas o de comida (e.g., "vegetariano, sin gluten").
recibe_noticias: models.BooleanField(default=False)

Tipo: Booleano.
Parámetros: default=False (por defecto, no recibe newsletters).
Descripción: Indica si el cliente desea recibir noticias o promociones por email.
str: Método que devuelve "Perfil de {cliente.nombre}".
------------------------------------------------------------------------------------------------------------------

4. Restaurante
Descripción general: Representa un restaurante, con detalles de contacto y una dirección única. Puede tener clientes frecuentes y platos/mesas asociados.

nombre: models.CharField(max_length=100)

Tipo: Cadena de texto.
Parámetros: max_length=100.
Descripción: Nombre del restaurante.
telefono: models.CharField(max_length=20)

Tipo: Cadena de texto.
Parámetros: max_length=20.
Descripción: Número de teléfono del restaurante.
email: models.EmailField(blank=True)

Tipo: Campo de email.
Parámetros: blank=True.
Descripción: Email de contacto (opcional).
web: models.URLField(blank=True)

Tipo: URL validada.
Parámetros: blank=True.
Descripción: Sitio web del restaurante (opcional).
abierto: models.BooleanField(default=True)

Tipo: Booleano.
Parámetros: default=True.
Descripción: Indica si el restaurante está abierto para operaciones.
direccion: models.OneToOneField(Direccion, on_delete=models.CASCADE)

Tipo: Relación uno a uno.
Parámetros: on_delete=models.CASCADE.
Descripción: Dirección única asociada al restaurante.
clientes_frecuentes: models.ManyToManyField(Cliente, blank=True, related_name="restaurantes_favoritos")

Tipo: Relación muchos a muchos.
Parámetros: blank=True (opcional), related_name="restaurantes_favoritos" (permite acceder desde Cliente a sus restaurantes favoritos).
Descripción: Lista de clientes que frecuentan este restaurante.
str: Método que devuelve el nombre del restaurante.
------------------------------------------------------------------------------------------------------------------

5. Etiqueta
Descripción general: Representa etiquetas o categorías para platos (e.g., "vegetariano", "picante"), con opciones de color y slug para URLs amigables.

nombre: models.CharField(max_length=50, unique=True)

Tipo: Cadena de texto.
Parámetros: max_length=50, unique=True.
Descripción: Nombre de la etiqueta (e.g., "Vegano").
descripcion: models.TextField(blank=True)

Tipo: Texto largo.
Parámetros: blank=True.
Descripción: Descripción detallada de la etiqueta (opcional).
color: models.CharField(max_length=10, default="verde")

Tipo: Cadena de texto.
Parámetros: max_length=10, default="verde".
Descripción: Color asociado para visualización (e.g., "rojo", "azul").
slug: models.SlugField(unique=True)

Tipo: Slug (cadena URL-friendly, e.g., "vegetariano").
Parámetros: unique=True.
Descripción: Versión URL-safe del nombre para rutas web.
str: Método que devuelve el nombre de la etiqueta.
------------------------------------------------------------------------------------------------------------------

6. Plato
Descripción general: Representa un plato o ítem del menú de un restaurante, con precio, disponibilidad y etiquetas asociadas.

restaurante: models.ForeignKey(Restaurante, on_delete=models.CASCADE)

Tipo: Relación uno a muchos (un restaurante tiene muchos platos).
Parámetros: on_delete=models.CASCADE (elimina platos si se elimina el restaurante).
Descripción: Restaurante al que pertenece el plato.
nombre: models.CharField(max_length=100)

Tipo: Cadena de texto.
Parámetros: max_length=100.
Descripción: Nombre del plato (e.g., "Paella Valenciana").
precio: models.DecimalField(max_digits=6, decimal_places=2)

Tipo: Decimal para precisión monetaria.
Parámetros: max_digits=6 (hasta 9999.99), decimal_places=2.
Descripción: Precio del plato en la moneda base (e.g., 15.50).
categoria: models.CharField(max_length=20, default="principal")

Tipo: Cadena de texto.
Parámetros: max_length=20, default="principal".
Descripción: Categoría del plato (e.g., "entrada", "postre").
disponible: models.BooleanField(default=True)

Tipo: Booleano.
Parámetros: default=True.
Descripción: Indica si el plato está disponible en el menú.
etiquetas: models.ManyToManyField(Etiqueta, blank=True)

Tipo: Relación muchos a muchos.
Parámetros: blank=True.
Descripción: Etiquetas asociadas al plato (e.g., vegano, picante).
str: Método que devuelve el nombre del plato.
------------------------------------------------------------------------------------------------------------------

7. Mesa
Descripción general: Representa una mesa física en el restaurante, con capacidad y estado de actividad.

restaurante: models.ForeignKey(Restaurante, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Restaurante al que pertenece la mesa.
numero: models.PositiveIntegerField()

Tipo: Entero positivo.
Parámetros: Ninguno adicional.
Descripción: Número identificador de la mesa (e.g., 5).
capacidad: models.PositiveIntegerField()

Tipo: Entero positivo.
Parámetros: Ninguno adicional.
Descripción: Número máximo de personas que puede acomodar.
ubicacion: models.CharField(max_length=20, default="interior")

Tipo: Cadena de texto.
Parámetros: max_length=20, default="interior".
Descripción: Ubicación de la mesa (e.g., "terraza", "barra").
activa: models.BooleanField(default=True)

Tipo: Booleano.
Parámetros: default=True.
Descripción: Indica si la mesa está disponible para reservas.
str: Método que devuelve "Mesa {numero}".
------------------------------------------------------------------------------------------------------------------

8. Reserva
Descripción general: Representa una reserva de mesa por un cliente, con fecha, hora y estado. Puede estar ligada a un pedido.

cliente: models.ForeignKey(Cliente, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Cliente que realiza la reserva.
mesa: models.ForeignKey(Mesa, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Mesa reservada.
fecha: models.DateField()

Tipo: Fecha.
Parámetros: Ninguno adicional.
Descripción: Fecha de la reserva (e.g., 2023-12-25).
hora: models.TimeField()

Tipo: Hora.
Parámetros: Ninguno adicional.
Descripción: Hora de la reserva (e.g., 20:00).
estado: models.CharField(max_length=20, default="pendiente")

Tipo: Cadena de texto.
Parámetros: max_length=20, default="pendiente".
Descripción: Estado de la reserva (e.g., "confirmada", "cancelada").
notas: models.TextField(blank=True)

Tipo: Texto largo.
Parámetros: blank=True.
Descripción: Notas adicionales (e.g., "cumpleaños").
str: Método que devuelve "Reserva {cliente.nombre} {fecha} {hora}".
------------------------------------------------------------------------------------------------------------------

9. Pedido
Descripción general: Representa un pedido completo de un cliente en un restaurante, posiblemente ligado a una reserva. Incluye total y estado de pago, con líneas de platos detalladas.

cliente: models.ForeignKey(Cliente, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Cliente que realiza el pedido.
restaurante: models.ForeignKey(Restaurante, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Restaurante donde se realiza el pedido.
reserva: models.OneToOneField(Reserva, on_delete=models.SET_NULL, null=True, blank=True)

Tipo: Relación uno a uno.
Parámetros: on_delete=models.SET_NULL (establece null si se elimina la reserva), null=True, blank=True (opcional).
Descripción: Reserva asociada al pedido (si aplica).
total: models.DecimalField(max_digits=8, decimal_places=2, default=0)

Tipo: Decimal.
Parámetros: max_digits=8, decimal_places=2, default=0.
Descripción: Total del pedido (incluyendo descuentos).
pagado: models.BooleanField(default=False)

Tipo: Booleano.
Parámetros: default=False.
Descripción: Indica si el pedido ha sido pagado.
creado: models.DateTimeField(auto_now_add=True)

Tipo: Fecha y hora.
Parámetros: auto_now_add=True.
Descripción: Fecha y hora de creación del pedido.
platos: models.ManyToManyField("Plato", through="LineaPedido")

Tipo: Relación muchos a muchos.
Parámetros: through="LineaPedido" (usa un modelo intermedio para detalles como cantidad).
Descripción: Platos incluidos en el pedido (detallados en LineaPedido).
str: Método que devuelve "Pedido {id}".
------------------------------------------------------------------------------------------------------------------

10. LineaPedido
Descripción general: Representa una línea detallada en un pedido, especificando cantidad, precio unitario y descuentos para un plato específico. Sirve como tabla intermedia para la relación muchos a muchos entre Pedido y Plato.

pedido: models.ForeignKey(Pedido, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Pedido al que pertenece esta línea.
plato: models.ForeignKey(Plato, on_delete=models.CASCADE)

Tipo: Relación uno a muchos.
Parámetros: on_delete=models.CASCADE.
Descripción: Plato en esta línea.
cantidad: models.PositiveIntegerField(default=1)

Tipo: Entero positivo.
Parámetros: default=1.
Descripción: Número de unidades del plato pedidas.
precio_unitario: models.DecimalField(max_digits=6, decimal_places=2)

Tipo: Decimal.
Parámetros: max_digits=6, decimal_places=2.
Descripción: Precio del plato en el momento del pedido (puede diferir del precio actual).
comentario: models.CharField(max_length=120, blank=True)

Tipo: Cadena de texto.
Parámetros: max_length=120, blank=True.
Descripción: Comentarios específicos para esta línea (e.g., "sin cebolla").
descuento_porcentaje: models.PositiveIntegerField(default=0)

Tipo: Entero positivo.
Parámetros: default=0 (0% por defecto).
Descripción: Porcentaje de descuento aplicado a esta línea (e.g., 10 para 10%).
str: Método que devuelve "{cantidad}x {plato.nombre}".
-->

