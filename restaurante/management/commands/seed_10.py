
from django.core.management.base import BaseCommand
from django.db import transaction
<<<<<<< HEAD
from faker import Faker
from decimal import Decimal

from restaurante.models import (
    Direccion, Restaurante, Cliente, PerfilCliente, Etiqueta,
    Plato, Mesa, Reserva, Pedido, LineaPedido
)

class Command(BaseCommand):
    help = "Genera 10 datos de cada modelo con Faker (simple y sin cosas raras)."

    @transaction.atomic  # Todo o nada: si falla algo, no deja datos a medias
=======
from django.db.models import Sum
from faker import Faker

from restaurante.models import (Direccion, Restaurante, Cliente, PerfilCliente, Etiqueta,Plato, Mesa, Reserva, Pedido, LineaPedido)

class Command(BaseCommand):
>>>>>>> urls_tarea
    def handle(self, *args, **options):
        fake = Faker('es_ES')

        # 1) Direcciones
        direcciones = []
        for _ in range(10):
            d = Direccion.objects.create(
                calle=fake.street_name(),
                numero=fake.random_int(1, 200),
                ciudad=fake.city(),
                codigo_postal=fake.postcode(),
                provincia=fake.state()
            )
            direcciones.append(d)

<<<<<<< HEAD
        # 2) Restaurantes (cada uno con una direccion)
=======
        # 2) Restaurantes (cada uno con una dirección)
>>>>>>> urls_tarea
        restaurantes = []
        for i in range(10):
            r = Restaurante.objects.create(
                nombre=fake.company(),
                telefono=fake.phone_number(),
                email=fake.free_email(),
                web="",
                abierto=True,
                direccion=direcciones[i % len(direcciones)]
            )
            restaurantes.append(r)

<<<<<<< HEAD
        # 3) Clientes y 4) PerfilCliente (uno a uno)
=======
        # 3) Clientes + 4) Perfiles
>>>>>>> urls_tarea
        clientes = []
        for _ in range(10):
            c = Cliente.objects.create(
                nombre=fake.name(),
<<<<<<< HEAD
                email=fake.unique.email(),  # que no se repita
=======
                email=fake.unique.email(),   # único para no chocar
>>>>>>> urls_tarea
                telefono=fake.phone_number()
            )
            PerfilCliente.objects.create(
                cliente=c,
                alergias="",
                preferencias="",
                recibe_noticias=fake.boolean()
            )
            clientes.append(c)

<<<<<<< HEAD
        # 5) Etiquetas 
=======
        # 5) Etiquetas básicas
>>>>>>> urls_tarea
        etiquetas = []
        for nombre in ["vegano", "picante", "sin_gluten", "postre", "bebida"]:
            e, _ = Etiqueta.objects.get_or_create(nombre=nombre, slug=nombre)
            etiquetas.append(e)

        # 6) Platos (2 por restaurante, con 0–2 etiquetas)
        platos = []
        for r in restaurantes:
            for _ in range(2):
                p = Plato.objects.create(
                    restaurante=r,
                    nombre=fake.unique.word().capitalize(),
                    precio=Decimal(str(fake.pydecimal(left_digits=2, right_digits=2, positive=True))),
                    categoria=fake.random_element(elements=['entrada','principal','postre','bebida']),
                    disponible=True
                )
<<<<<<< HEAD
                # añadir algunas etiquetas (opcional)
=======
                # añade algunas etiquetas (opcional)
>>>>>>> urls_tarea
                for e in fake.random_elements(elements=etiquetas, length=fake.random_int(0,2), unique=False):
                    p.etiquetas.add(e)
                platos.append(p)

        # 7) Mesas (2 por restaurante)
        mesas = []
        for r in restaurantes:
            for i in range(2):
                m = Mesa.objects.create(
                    restaurante=r,
                    numero=i + 1,
                    capacidad=fake.random_int(2, 8),
                    ubicacion=fake.random_element(elements=['interior', 'terraza']),
                    activa=True
                )
                mesas.append(m)

        # 8) Reservas (10 en total)
        reservas = []
        for _ in range(10):
            res = Reserva.objects.create(
                cliente=fake.random_element(elements=clientes),
                mesa=fake.random_element(elements=mesas),
                fecha=fake.date_between(start_date='-5d', end_date='+5d'),
                hora=fake.time_object(),
                estado=fake.random_element(elements=['pendiente', 'confirmada', 'cancelada']),
                notas=""
            )
            reservas.append(res)

<<<<<<< HEAD
        # 9) Pedidos (10 en total) —  (OneToOne)
        pedidos = []
        reservas_libres = list(Reserva.objects.filter(pedido__isnull=True))
        for _ in range(10):
            reserva_opcional = None
            if reservas_libres and fake.boolean():
                reserva_opcional = reservas_libres.pop(0)  
=======
        # 9) Pedidos (10 en total) — usa una reserva libre si quiere
        pedidos = []
        reservas_libres = list(Reserva.objects.filter(pedido__isnull=True))  # OneToOne seguro
        for _ in range(10):
            reserva_opcional = None
            if reservas_libres and fake.boolean():
                reserva_opcional = reservas_libres.pop(0)  # la saco para no reutilizarla
>>>>>>> urls_tarea

            ped = Pedido.objects.create(
                cliente=fake.random_element(elements=clientes),
                restaurante=fake.random_element(elements=restaurantes),
                reserva=reserva_opcional,
                total=Decimal('0.00'),
                pagado=fake.boolean()
            )
            pedidos.append(ped)

<<<<<<< HEAD
        # 10) Líneas de pedido (1–3 por pedido) + cálculo del total
        for ped in pedidos:
            platos_del_restaurante = [p for p in platos if p.restaurante_id == ped.restaurante_id]
            total = Decimal('0.00')
            for _ in range(fake.random_int(1, 3)):
                if not platos_del_restaurante:
                    break
                plato = fake.random_element(elements=platos_del_restaurante)
                cantidad = fake.random_int(1, 3)
                LineaPedido.objects.create(
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

        self.stdout.write(self.style.SUCCESS("Seed listo: 10 de cada modelo (aprox.)."))
=======
        # 10) Líneas de pedido (1–3 por pedido) y cálculo del total
        for ped in pedidos:
            platos_del_restaurante = [p for p in platos if p.restaurante_id == ped.restaurante_id]
            num_lineas = fake.random_int(1, 3)
            total = Decimal('0.00')

            for _ in range(num_lineas):
                if not platos_del_restaurante:
                    break
                plato = fake.random_element(elements=platos_del_restaurante)
                precio = plato.precio
                cantidad = fake.random_int(1, 3)

                lp = LineaPedido.objects.create(
                    pedido=ped,
                    plato=plato,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    comentario="",
                    descuento_porcentaje=0
                )
                total += precio * cantidad

            ped.total = total
            ped.save()

        self.stdout.write(self.style.SUCCESS("Seed completado: 10 registros por modelo (aprox.)."))
>>>>>>> urls_tarea
