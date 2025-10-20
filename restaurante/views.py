# restaurante/views.py
from django.shortcuts import render
from django.db.models import Q, Count, Sum, Avg
from .models import (Restaurante, Direccion, Plato, Etiqueta, Mesa, Cliente, PerfilCliente, Reserva, Pedido, LineaPedido)

def index(request):
    """
    Índice con enlaces.
    """
    return render(request, 'restaurante/index.html')



def error_400(request, exception):
    return render(request, 'restaurante/400.html', status=400)
def error_403(request, exception):
    return render(request, 'restaurante/403.html', status=403)
def error_404(request, exception):
    return render(request, 'restaurante/404.html', status=404)
def error_500(request):
    return render(request, 'restaurante/500.html', status=500)

def lista_restaurantes(request):
    """
    restaurantes con su dirección (OneToOne) y contadores de platos/mesas.
    Optimización: select_related (O2O) + annotate(Count) + order_by.

    SQL:
      SELECT r.*, d.*, COUNT(DISTINCT p.id) AS num_platos, COUNT(DISTINCT m.id) AS num_mesas
      FROM restaurante_restaurante r
      JOIN restaurante_direccion d ON r.direccion_id=d.id
      LEFT JOIN restaurante_plato p ON p.restaurante_id=r.id
      LEFT JOIN restaurante_mesa  m ON m.restaurante_id=r.id
      GROUP BY r.id, d.id
      ORDER BY r.nombre ASC;
    """
    qs = (
        Restaurante.objects
        .select_related('direccion')
        .annotate(
            num_platos=Count('plato', distinct=True),
            num_mesas=Count('mesa', distinct=True),
        )
        .order_by('nombre')
    )
    return render(request, 'restaurante/restaurantes.html', {'restaurantes': qs})


def detalle_restaurante(request, id: int):
    """
    Muestra un restaurante con dirección, platos, mesas y clientes frecuentes.
    

    SQL (idea):
      SELECT * FROM restaurante_restaurante WHERE id=%s;
      SELECT * FROM restaurante_direccion WHERE id=%s;
      SELECT * FROM restaurante_plato WHERE restaurante_id=%s ORDER BY nombre;
      SELECT * FROM restaurante_mesa  WHERE restaurante_id=%s ORDER BY numero;
      SELECT c.* FROM restaurante_restaurante_clientes_frecuentes rc
        JOIN restaurante_cliente c ON c.id=rc.cliente_id
       WHERE rc.restaurante_id=%s;
    """
    r = (
        Restaurante.objects
        .select_related('direccion')
        .prefetch_related('clientes_frecuentes', 'plato_set', 'mesa_set')
        .get(pk=id)
    )
    return render(request, 'restaurante/restaurante_detalle.html', {'r': r})


def lista_platos(request):
    """
    Lista platos con su restaurante y etiquetas (M2M), ordenado por precio.
    Optimización: select_related (FK) + prefetch_related (M2M) + limit.

    SQL (idea):
      SELECT p.*, r.*
        FROM restaurante_plato p
        JOIN restaurante_restaurante r ON p.restaurante_id=r.id
       ORDER BY p.precio ASC
       LIMIT 100;
    """
    platos = (
        Plato.objects
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('precio')[:100]
    )
    return render(request, 'restaurante/platos.html', {'platos': platos})


def platos_por_categoria(request, categoria: str):
    """
    Filtra platos por categoría exacta (param str).
    Optimización: select_related + prefetch_related + order_by.

    SQL (idea):
      SELECT * FROM restaurante_plato
       WHERE categoria=%s
       ORDER BY nombre ASC;
    """
    platos = (
        Plato.objects
        .filter(categoria=categoria)
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('nombre')
    )
    return render(request, 'restaurante/platos_categoria.html', {
        'platos': platos,
        'categoria': categoria,
    })


def buscar_platos(request, texto: str, precio_min: int):
    """
    Búsqueda con AND/OR:
      - AND: precio >= precio_min
      - OR : nombre contiene 'texto'  OR  etiqueta.nombre = 'texto'
    Optimización: select_related + prefetch_related + distinct (por M2M).

    SQL (idea):
      SELECT DISTINCT p.*
        FROM restaurante_plato p
   LEFT JOIN restaurante_plato_etiquetas pe ON pe.plato_id=p.id
   LEFT JOIN restaurante_etiqueta e        ON e.id=pe.etiqueta_id
       WHERE p.precio >= %s
         AND (p.nombre LIKE %texto% OR e.nombre = %s)
       ORDER BY p.precio ASC;
    """
    platos = (
        Plato.objects
        .filter(
            Q(precio__gte=precio_min) &
            (Q(nombre__icontains=texto) | Q(etiquetas__nombre__iexact=texto))
        )
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('precio')
        .distinct()
    )
    return render(request, 'restaurante/platos_buscar.html', {
        'platos': platos,
        'texto': texto,
        'precio_min': precio_min,
    })


def lista_pedidos(request):
    """
    Muestra pedidos recientes y un resumen global (SUM/AVG).
    Optimización: select_related (FK/O2O) + prefetch_related (reversa de líneas).

    SQL (idea):
      SELECT SUM(total) AS suma, AVG(total) AS promedio
        FROM restaurante_pedido;

      SELECT p.*, c.*, r.*
        FROM restaurante_pedido p
        JOIN restaurante_cliente c     ON p.cliente_id=c.id
        JOIN restaurante_restaurante r ON p.restaurante_id=r.id
       ORDER BY p.creado DESC
       LIMIT 100;
    """
    resumen = Pedido.objects.aggregate(
        suma=Sum('total'),
        promedio=Avg('total')
    )
    pedidos = (
        Pedido.objects
        .select_related('cliente', 'restaurante', 'reserva')
        .prefetch_related('lineapedido_set__plato')
        .order_by('-creado')[:100]
    )
    return render(request, 'restaurante/pedidos.html', {
        'resumen': resumen,
        'pedidos': pedidos,
    })


def pedidos_sin_lineas(request):
    """
    Lista pedidos que no tienen ninguna línea (reversa isnull=True).

    SQL (idea):
      SELECT p.*
        FROM restaurante_pedido p
   LEFT JOIN restaurante_lineapedido lp ON lp.pedido_id=p.id
       WHERE lp.id IS NULL;
    """
    pedidos = (
        Pedido.objects
        .filter(lineapedido__isnull=True)
        .select_related('cliente', 'restaurante', 'reserva')
        .order_by('id')
    )
    return render(request, 'restaurante/pedidos_sin_lineas.html', {'pedidos': pedidos})


def clientes_frecuentes(request):
    """
    Clientes con nº de pedidos (aggregate por fila) y favoritos (M2M).
    Requisito HAVING: filtrar por anotación (num_pedidos >= 1).

    SQL (idea):
      SELECT c.*, COUNT(p.id) AS num_pedidos
        FROM restaurante_cliente c
   LEFT JOIN restaurante_pedido p ON p.cliente_id=c.id
    GROUP BY c.id
      HAVING COUNT(p.id) >= 1
    ORDER BY c.nombre ASC;
    """
    clientes = (
        Cliente.objects
        .annotate(num_pedidos=Count('pedido'))
        .filter(num_pedidos__gte=1)
        .prefetch_related('restaurantes_favoritos')
        .order_by('nombre')
    )
    return render(request, 'restaurante/clientes_frecuentes.html', {'clientes': clientes})


def buscar_simple(request, texto: str):
    """
    Búsqueda sencilla con re_path: clientes y platos por nombre (OR).
    Optimización: order_by + limit; select_related para mostrar restaurante.

    SQL (idea):
      SELECT * FROM restaurante_cliente
       WHERE nombre LIKE %texto%
       ORDER BY nombre ASC
       LIMIT 50;

      SELECT * FROM restaurante_plato
       WHERE nombre LIKE %texto%
       ORDER BY nombre ASC
       LIMIT 50;
    """
    clientes = (
        Cliente.objects
        .filter(nombre__icontains=texto)
        .order_by('nombre')[:50]
    )
    platos = (
        Plato.objects
        .filter(nombre__icontains=texto)
        .select_related('restaurante')
        .order_by('nombre')[:50]
    )
    return render(request, 'restaurante/buscar_simple.html', {
        'texto': texto,
        'clientes': clientes,
        'platos': platos,
    })
