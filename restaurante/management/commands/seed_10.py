from django.core.management.base import BaseCommand
from faker import Faker
from restaurante.models import *

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        fake = Faker("es_ES")

        direcciones = [Direccion.objects.create(
            calle=fake.street_name(),
            numero=fake.random_int(min=1, max=200),
            ciudad=fake.city(),
            codigo_postal=fake.postcode()[:10],
            provincia=fake.state()
        ) for _ in range(10)]

        clientes = [Cliente.objects.create(
            nombre=fake.name(),
            email=fake.unique.email(),
            telefono=fake.phone_number()
        ) for _ in range(10)]

        perfiles = [PerfilCliente.objects.create(
            cliente=c,
            alergias=fake.word(),
            preferencias=fake.sentence(nb_words=3),
            recibe_noticias=fake.boolean()
        ) for c in clientes]

        restaurantes = []
        for i in range(10):
            r = Restaurante.objects.create(
                nombre=f"Restaurante {i+1}",
                telefono=fake.phone_number(),
                email=fake.unique.company_email(),
                web=fake.url(),
                abierto=True,
                direccion=direcciones[i]
            )
            r.clientes_frecuentes.add(*fake.random_elements(elements=clientes, length=3, unique=False))
            restaurantes.append(r)

        etiquetas = [Etiqueta.objects.create(
            nombre=fake.unique.word().lower(),
            descripcion=fake.sentence(),
            color=fake.random_element(elements=["rojo","verde","azul"]),
            slug=fake.unique.slug()
        ) for _ in range(10)]

        platos = []
        for _ in range(10):
            p = Plato.objects.create(
                restaurante=fake.random_element(restaurantes),
                nombre=fake.word().capitalize(),
                precio="10.00",
                categoria=fake.random_element(elements=["entrante","principal","postre"]),
                disponible=True
            )
            p.etiquetas.add(*fake.random_elements(elements=etiquetas, length=2, unique=False))
            platos.append(p)

        mesas = [Mesa.objects.create(
            restaurante=fake.random_element(restaurantes),
            numero=i+1,
            capacidad=fake.random_int(min=2, max=8),
            ubicacion=fake.random_element(elements=["interior","terraza"]),
            activa=True
        ) for i in range(10)]

        reservas = [Reserva.objects.create(
            cliente=fake.random_element(clientes),
            mesa=fake.random_element(mesas),
            fecha=fake.date_this_month(),
            hora=fake.time_object(),
            estado=fake.random_element(elements=["pendiente","confirmada","cancelada"]),
            notas=fake.sentence()
        ) for _ in range(10)]

        # ---- ARREGLO OneToOne: no reutilizar la misma Reserva para varios Pedidos ----
        usados_reserva_ids = set()
        pedidos = []
        for _ in range(10):
            disponibles = [r for r in reservas if r.id not in usados_reserva_ids]
            reserva_elegida = fake.random_element([None] + disponibles)

            p = Pedido.objects.create(
                cliente=fake.random_element(clientes),
                restaurante=fake.random_element(restaurantes),
                reserva=reserva_elegida,
                total="0.00",
                pagado=fake.boolean()
            )
            if reserva_elegida:
                usados_reserva_ids.add(reserva_elegida.id)
            pedidos.append(p)
        # ---------------------------------------------------------------------------

        for ped in pedidos:
            plato = fake.random_element(platos)
            cantidad = fake.random_int(min=1, max=3)
            LineaPedido.objects.create(
                pedido=ped,
                plato=plato,
                cantidad=cantidad,
                precio_unitario=str(plato.precio),
                comentario="",
                descuento_porcentaje=0
            )

        # Recalcular totales
        for ped in pedidos:
            total = 0.0
            for lp in LineaPedido.objects.filter(pedido=ped):
                total += float(lp.precio_unitario) * lp.cantidad
            ped.total = f"{total:.2f}"
            ped.save()

        self.stdout.write(self.style.SUCCESS("10 registros por cada modelo creados."))
