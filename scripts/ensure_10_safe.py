from decimal import Decimal
from random import choice
from faker import Faker

from restaurante.models import (
    Direccion, Restaurante, Cliente, PerfilCliente, Etiqueta,
    Plato, Mesa, Reserva, Pedido, LineaPedido
)

fake = Faker('es_ES')

def ensure_count(model, create_fn, target=10):
    n = model.objects.count()
    needed = max(0, target - n)
    print(f"{model.__name__}: {n} (añadir {needed})")
    for _ in range(needed):
        create_fn()

# create functions

def create_direccion():
    return Direccion.objects.create(
        calle=fake.street_name(),
        numero=fake.random_int(1, 200),
        ciudad=fake.city(),
        codigo_postal=fake.postcode(),
        provincia=fake.state()
    )


def create_restaurante():
    # elegir una direccion que no esté ya asociada a restaurante
    direcciones_libres = list(Direccion.objects.filter(restaurante__isnull=True))
    if not direcciones_libres:
        d = create_direccion()
    else:
        d = direcciones_libres.pop(0)
    return Restaurante.objects.create(
        nombre=fake.company(),
        telefono=fake.phone_number(),
        email=fake.free_email(),
        web="",
        abierto=True,
        direccion=d
    )


def create_cliente_y_perfil():
    c = Cliente.objects.create(
        nombre=fake.name(),
        email=fake.unique.email(),
        telefono=fake.phone_number()
    )
    PerfilCliente.objects.create(cliente=c, alergias='', preferencias='', recibe_noticias=fake.boolean())
    return c


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
    return p


def create_mesa():
    restaurantes = list(Restaurante.objects.all())
    if not restaurantes:
        create_restaurante()
        restaurantes = list(Restaurante.objects.all())
    r = choice(restaurantes)
    return Mesa.objects.create(restaurante=r, numero=fake.random_int(1,100), capacidad=fake.random_int(2,8), ubicacion=choice(['interior','terraza']), activa=True)


def create_reserva():
    clientes = list(Cliente.objects.all())
    mesas = list(Mesa.objects.all())
    if not clientes:
        create_cliente_y_perfil()
        clientes = list(Cliente.objects.all())
    if not mesas:
        create_mesa()
        mesas = list(Mesa.objects.all())
    return Reserva.objects.create(cliente=choice(clientes), mesa=choice(mesas), fecha=fake.date_between(start_date='-5d', end_date='+5d'), hora=fake.time_object(), estado=choice(['pendiente','confirmada','cancelada']), notas='')


def create_pedido():
    clientes = list(Cliente.objects.all())
    restaurantes = list(Restaurante.objects.all())
    if not clientes:
        create_cliente_y_perfil()
        clientes = list(Cliente.objects.all())
    if not restaurantes:
        create_restaurante()
        restaurantes = list(Restaurante.objects.all())

    reservas_libres = list(Reserva.objects.filter(pedido__isnull=True))
    reserva = None
    if reservas_libres and fake.boolean():
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
    # intentar seleccionar platos del mismo restaurante, si no hay, cualquiera
    platos_rest = [p for p in platos if p.restaurante_id == ped.restaurante_id]
    plato = choice(platos_rest) if platos_rest else choice(platos)
    cantidad = fake.random_int(1,3)
    lp = LineaPedido.objects.create(pedido=ped, plato=plato, cantidad=cantidad, precio_unitario=plato.precio, comentario='', descuento_porcentaje=0)
    ped.total += plato.precio * cantidad
    ped.save()
    return lp

# ejecución
print('Asegurando etiquetas...')
ensure_etiquetas()

ensure_count(Direccion, create_direccion)
ensure_count(Restaurante, create_restaurante)
ensure_count(Cliente, create_cliente_y_perfil)
# perfil se crea con cliente, no hace falta crear separado
ensure_count(Etiqueta, ensure_etiquetas)
ensure_count(Plato, create_plato)
ensure_count(Mesa, create_mesa)
ensure_count(Reserva, create_reserva)
ensure_count(Pedido, create_pedido)
ensure_count(LineaPedido, create_linea_pedido)

print('Hecho. Conteos finales:')
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
