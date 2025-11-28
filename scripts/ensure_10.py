from decimal import Decimal
from random import choice
from faker import Faker

from restaurante.models import (
    Direccion, Restaurante, Cliente, PerfilCliente, Etiqueta,
    Plato, Mesa, Reserva, Pedido, LineaPedido
)

fake = Faker('es_ES')

# helper to create or report

def ensure_count(model, create_fn, target=10):
    n = model.objects.count()
    needed = max(0, target - n)
    print(f"{model.__name__}: {n} (añadir {needed})")
    for _ in range(needed):
        create_fn()

# create functions

def create_direccion():
    Direccion.objects.create(
        calle=fake.street_name(),
        numero=fake.random_int(1, 200),
        ciudad=fake.city(),
        codigo_postal=fake.postcode(),
        provincia=fake.state()
    )


def create_restaurante():
    direcciones = list(Direccion.objects.all())
    if not direcciones:
        create_direccion()
        direcciones = list(Direccion.objects.all())
    Restaurante.objects.create(
        nombre=fake.company(),
        telefono=fake.phone_number(),
        email=fake.free_email(),
        web="",
        abierto=True,
        direccion=choice(direcciones)
    )


def create_cliente_y_perfil():
    c = Cliente.objects.create(
        nombre=fake.name(),
        email=fake.unique.email(),
        telefono=fake.phone_number()
    )
    PerfilCliente.objects.create(
        cliente=c, alergias='', preferencias='', recibe_noticias=fake.boolean()
    )


def ensure_etiquetas():
    base = ["vegano", "picante", "sin_gluten", "postre", "bebida"]
    for nombre in base:
        Etiqueta.objects.get_or_create(nombre=nombre, slug=nombre)


def create_plato():
    restaurantes = list(Restaurante.objects.all())
    if not restaurantes:
        create_restaurante()
        restaurantes = list(Restaurante.objects.all())
    r = choice(restaurantes)
    p = Plato.objects.create(
        restaurante=r,
        nombre=fake.unique.word().capitalize(),
        precio=Decimal(str(fake.pydecimal(left_digits=2, right_digits=2, positive=True))),
        categoria=fake.random_element(elements=['entrada','principal','postre','bebida']),
        disponible=True
    )
    etiquetas = list(Etiqueta.objects.all())
    for e in fake.random_elements(elements=etiquetas, length=fake.random_int(0,2), unique=False):
        p.etiquetas.add(e)


def create_mesa():
    restaurantes = list(Restaurante.objects.all())
    if not restaurantes:
        create_restaurante()
        restaurantes = list(Restaurante.objects.all())
    r = choice(restaurantes)
    Mesa.objects.create(restaurante=r, numero=fake.random_int(1,100), capacidad=fake.random_int(2,8), ubicacion=choice(['interior','terraza']), activa=True)


def create_reserva():
    clientes = list(Cliente.objects.all())
    mesas = list(Mesa.objects.all())
    if not clientes:
        create_cliente_y_perfil()
        clientes = list(Cliente.objects.all())
    if not mesas:
        create_mesa()
        mesas = list(Mesa.objects.all())
    Reserva.objects.create(cliente=choice(clientes), mesa=choice(mesas), fecha=fake.date_between(start_date='-5d', end_date='+5d'), hora=fake.time_object(), estado=choice(['pendiente','confirmada','cancelada']), notas='')


def create_pedido():
    clientes = list(Cliente.objects.all())
    restaurantes = list(Restaurante.objects.all())
    if not clientes:
        create_cliente_y_perfil()
        clientes = list(Cliente.objects.all())
    if not restaurantes:
        create_restaurante()
        restaurantes = list(Restaurante.objects.all())

    # try to use a reserva libre sometimes
    reservas_libres = list(Reserva.objects.filter(pedido__isnull=True))
    reserva = None
    if reservas_libres:
        reserva = reservas_libres.pop(0)

    ped = Pedido.objects.create(cliente=choice(clientes), restaurante=choice(restaurantes), reserva=reserva, total=Decimal('0.00'), pagado=fake.boolean())
    return ped


def create_linea_pedido():
    pedidos = list(Pedido.objects.all())
    platos = list(Plato.objects.all())
    if not pedidos:
        create_pedido()
        pedidos = list(Pedido.objects.all())
    if not platos:
        create_plato()
        platos = list(Plato.objects.all())
    ped = choice(pedidos)
    plato = choice([p for p in platos if p.restaurante_id == ped.restaurante_id] or platos)
    cantidad = fake.random_int(1,3)
    lp = LineaPedido.objects.create(pedido=ped, plato=plato, cantidad=cantidad, precio_unitario=plato.precio, comentario='', descuento_porcentaje=0)
    # actualizar total
    ped.total += plato.precio * cantidad
    ped.save()


# Ensure etiquetas first
ensure_etiquetas()

# Ensure counts
ensure_count(Direccion, create_direccion)
ensure_count(Restaurante, create_restaurante)
ensure_count(Cliente, create_cliente_y_perfil)
ensure_count(PerfilCliente, lambda: None)  # perfiles creados junto a clientes
ensure_count(Etiqueta, ensure_etiquetas)
ensure_count(Plato, create_plato)
ensure_count(Mesa, create_mesa)
ensure_count(Reserva, create_reserva)
ensure_count(Pedido, create_pedido)
ensure_count(LineaPedido, create_linea_pedido)

print('Hecho. Conteos finales:')
from django.db import connection
print('Direcciones', Direccion.objects.count())
print('Restaurantes', Restaurante.objects.count())
print('Clientes', Cliente.objects.count())
print('Perfiles', PerfilCliente.objects.count())
print('Etiquetas', Etiqueta.objects.count())
print('Platos', Plato.objects.count())
print('Mesas', Mesa.objects.count())
print('Reservas', Reserva.objects.count())
print('Pedidos', Pedido.objects.count())
print('Lineas', LineaPedido.objects.count())
