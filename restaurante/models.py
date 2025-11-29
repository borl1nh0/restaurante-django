from django.db import models

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
    
    def __str__(self): 
        return self.nombre

class PerfilCliente(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    alergias = models.TextField(blank=True)
    preferencias = models.TextField(blank=True)
    recibe_noticias = models.BooleanField(default=False)
    
    def __str__(self): 
        return f"Perfil de {self.cliente.nombre}"

class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE)
    clientes_frecuentes = models.ManyToManyField(Cliente, blank=True, related_name="restaurantes_favoritos")
    
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

    def __str__(self): 
        return f"Reserva {self.cliente.nombre} {self.fecha} {self.hora}"

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    reserva = models.OneToOneField(Reserva, on_delete=models.SET_NULL, null=True, blank=True) #este codigo es para borrar la reserva pero el pedido lo dejaria "guardado" teni pensado crea una pagina de merma, o desperdicios, y con este codigo podria hacerlo.
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platos = models.ManyToManyField("Plato", through="LineaPedido")
    
    def __str__(self): 
        return f"Pedido {self.id}"

class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)
    comentario = models.CharField(max_length=120, blank=True)
    descuento_porcentaje = models.PositiveIntegerField(default=0)
    
    def __str__(self): 
        return f"{self.cantidad}x {self.plato.nombre}"
