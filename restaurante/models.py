from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q


class Usuario(AbstractUser):
    ROL_ADMINISTRADOR = "ADMINISTRADOR"
    ROL_GERENTE = "GERENTE"
    ROL_EMPLEADO = "EMPLEADO"
    ROL_CLIENTE = "CLIENTE"

    ROL_CHOICES = [
        (ROL_ADMINISTRADOR, "Administrador"),
        (ROL_GERENTE, "Gerente"),
        (ROL_EMPLEADO, "Empleado"),
        (ROL_CLIENTE, "Cliente"),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_CLIENTE)


# Create your models here.
class Direccion(models.Model):
    calle = models.CharField(max_length=120)
    numero = models.PositiveIntegerField()
    ciudad = models.CharField(max_length=80)
    codigo_postal = models.CharField(max_length=10)
    provincia = models.CharField(max_length=80)
    
    def __str__(self): 
        return f"{self.calle} {self.numero}, {self.ciudad}"

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clientes_creados",
    )
    
    def __str__(self): 
        return self.nombre

class PerfilCliente(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    alergias = models.TextField(blank=True)
    preferencias = models.TextField(blank=True)
    recibe_noticias = models.BooleanField(default=False)
    
    def __str__(self): 
        return f"Perfil de {self.cliente.nombre}"

class RestauranteQuerySet(models.QuerySet):
    """QuerySet con filtros reutilizables para búsquedas avanzadas."""

    def advanced_filter(self, nombre: str | None = None, telefono: str | None = None, direccion: str | None = None):
        qs = self.select_related("direccion").all()

        if nombre:
            qs = qs.filter(nombre__icontains=nombre)

        if telefono:
            qs = qs.filter(telefono__icontains=telefono)

        if direccion:
            qs = qs.filter(
                Q(direccion__calle__icontains=direccion)
                | Q(direccion__ciudad__icontains=direccion)
                | Q(direccion__codigo_postal__icontains=direccion)
            )

        return qs


class RestauranteManager(models.Manager):
    """Manager que expone métodos de búsqueda en el modelo."""

    def get_queryset(self):
        return RestauranteQuerySet(self.model, using=self._db)

    def advanced_filter(self, nombre: str | None = None, telefono: str | None = None, direccion: str | None = None):
        return self.get_queryset().advanced_filter(nombre=nombre, telefono=telefono, direccion=direccion)

class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE)
    clientes_frecuentes = models.ManyToManyField(Cliente, blank=True, related_name="restaurantes_favoritos")

    # Registrar el manager personalizado directamente en la clase
    objects = RestauranteManager()

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=10, default="verde")
    slug = models.SlugField(unique=True)
    
    def __str__(self): 
        return self.nombre

class Plato(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    categoria = models.CharField(max_length=20, default="principal")
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)
    
    def __str__(self): 
        return self.nombre

class Mesa(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)
    
    def __str__(self): 
        return f"Mesa {self.numero}"

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, default="pendiente")
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas_creadas",
    )

    def __str__(self): 
        return f"Reserva {self.cliente.nombre} {self.fecha} {self.hora}"

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    reserva = models.OneToOneField(Reserva, on_delete=models.SET_NULL, null=True, blank=True) #este codigo es para borrar la reserva pero el pedido lo dejaria "guardado" teni pensado crea una pagina de merma, o desperdicios, y con este codigo podria hacerlo.
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platos = models.ManyToManyField("Plato", through="LineaPedido")
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_creados",
    )
    
    def __str__(self): 
        return f"Pedido {self.id}"

class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)
    comentario = models.CharField(max_length=120, blank=True)
    descuento_porcentaje = models.PositiveIntegerField(default=0)
    cantidad = models.PositiveIntegerField(default=1)
    
    def __str__(self): 
        return f"{self.cantidad}x {self.plato.nombre}"
