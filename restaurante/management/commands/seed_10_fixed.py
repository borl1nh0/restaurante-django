from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from faker import Faker

from restaurante.models import (
    Direccion, Restaurante, Cliente, PerfilCliente, Etiqueta,
    Plato, Mesa, Reserva, Pedido, LineaPedido
)


class Command(BaseCommand):
    help = "Crea datos de prueba: ~10 registros por modelo (sin merge conflicts)."

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker('es_ES')

        # Limpiar datos previos opcional (NO BORRAR por seguridad). Comentado.
        # Direccion.objects.all().delete()

        # 1) Direcciones
        direcciones = []
        for i in range(10):
            d = Direccion.objects.create(
                calle=f"Calle {fake.street_name()}",
                numero=100 + i,
                ciudad=fake.city(),
                codigo_postal=fake.postcode(),
                provincia=fake.state()
            )
            direcciones.append(d)

        # 2) Restaurantes
        restaurantes = []
        for i in range(10):
            r = Restaurante.objects.create(
                nombre=f"Restaurante {i+1} {fake.company()}",
                telefono=fake.phone_number(),
                email=fake.free_email(),
                web=f"https://www.example{i+1}.com",
                abierto=bool(i % 2 == 0),
                direccion=direcciones[i]
            )
            restaurantes.append(r)

        # 3) Clientes y Perfiles
        clientes = []
        for i in range(10):
            c = Cliente.objects.create(
                nombre=fake.name(),
                email=fake.unique.email(),
                telefono=fake.phone_number()
            )
            PerfilCliente.objects.create(
                cliente=c,
                alergias="",
                preferencias="",
                recibe_noticias=fake.boolean()
            )
            clientes.append(c)

        # 4) Etiquetas
        etiquetas = []
        for nombre in ["vegano", "picante", "sin_gluten", "postre", "bebida"]:
            e, _ = Etiqueta.objects.get_or_create(nombre=nombre, slug=nombre)
            etiquetas.append(e)

        # 5) Platos (2 por restaurante)
        platos = []
        for r in restaurantes:
            for j in range(2):
                p = Plato.objects.create(
                    restaurante=r,
                    nombre=f"Plato {r.id}-{j+1} {fake.word().capitalize()}",
                    precio=Decimal(f"{5 + j + (r.id % 5)}.99"),
                    categoria=fake.random_element(elements=['entrada','principal','postre','bebida']),
                    disponible=True
                )
                # asignar 0-2 etiquetas
                for e in fake.random_elements(elements=etiquetas, length=fake.random_int(0,2), unique=False):
                    p.etiquetas.add(e)
                platos.append(p)

        # 6) Mesas (2 por restaurante)
        mesas = []
        for r in restaurantes:
            for n in range(2):
                m = Mesa.objects.create(
                    restaurante=r,
                    numero=(n+1),
                    capacidad=fake.random_int(2, 8),
                    ubicacion=fake.random_element(elements=['interior','terraza']),
                    activa=True
                )
                mesas.append(m)

        # 7) Reservas (10)
        reservas = []
        for i in range(10):
            res = Reserva.objects.create(
                cliente=fake.random_element(elements=clientes),
                mesa=fake.random_element(elements=mesas),
                fecha=fake.date_between(start_date='-5d', end_date='+5d'),
                hora=fake.time_object(),
                estado=fake.random_element(elements=['pendiente','confirmada','cancelada']),
                notas=""
            )
            reservas.append(res)

        # 8) Pedidos (10) - asigna reservas únicas si se usan
        pedidos = []
        reservas_disponibles = reservas.copy()
        for i in range(10):
            reserva_asignada = None
            if reservas_disponibles and fake.boolean():
                reserva_asignada = reservas_disponibles.pop(0)

            ped = Pedido.objects.create(
                cliente=fake.random_element(elements=clientes),
                restaurante=fake.random_element(elements=restaurantes),
                reserva=reserva_asignada,
                total=Decimal('0.00'),
                pagado=fake.boolean()
            )
            pedidos.append(ped)

        # 9) Lineas de pedido (1-3 por pedido) y calcular total
        for ped in pedidos:
            platos_del_rest = [p for p in platos if p.restaurante_id == ped.restaurante_id]
            total = Decimal('0.00')
            num = fake.random_int(1,3)
            for _ in range(num):
                if not platos_del_rest:
                    break
                plato = fake.random_element(elements=platos_del_rest)
                cantidad = fake.random_int(1,3)
                lp = LineaPedido.objects.create(
                    pedido=ped,
                    plato=plato,
                    cantidad=cantidad,
                    precio_unitario=plato.precio,
                    comentario="",
                    descuento_porcentaje=0
                )
                total += plato.precio * cantidad
            ped.total = total
            ped.save()

        self.stdout.write(self.style.SUCCESS('Seed OK: creado ~10 registros por modelo.'))
