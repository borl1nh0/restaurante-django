from restaurante.models import Direccion, Restaurante
from faker import Faker
from decimal import Decimal

f = Faker('es_ES')

for i in range(10):
    d = Direccion.objects.create(
        calle=f.street_name(),
        numero=f.random_int(1, 200),
        ciudad=f.city(),
        codigo_postal=f.postcode(),
        provincia=f.state()
    )
    Restaurante.objects.create(
        nombre=f.company() + f' #{i+1}',
        telefono=f.phone_number(),
        email=f.free_email(),
        web='',
        abierto=True,
        direccion=d
    )
print('Añadidos 10 restaurantes con direcciones.')
