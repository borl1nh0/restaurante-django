from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from .models import Restaurante, Direccion, Plato, Etiqueta, Mesa, Cliente, PerfilCliente, Reserva, Pedido, LineaPedido

def index(request):
    """
    enlaces a las 10 URLs (índice).
    
    """
    return render(request, 'restaurante/index.html')

# Errores personalizados (punto 5)
def error_400(request, exception): return render(request, 'restaurante/400.html', status=400)
def error_403(request, exception): return render(request, 'restaurante/403.html', status=403)
def error_404(request, exception): return render(request, 'restaurante/404.html', status=404)
def error_500(request):             return render(request, 'restaurante/500.html', status=500)
def lista_restaurantes(request):
    """
    Lista restaurantes con dirección (OneToOne) y contadores de platos/mesas.
    SQL (idea):
      SELECT r.*, d.*, COUNT(DISTINCT p.id) AS num_platos, COUNT(DISTINCT m.id) AS num_mesas
      FROM restaurante_restaurante r
      JOIN restaurante_direccion d ON r.direccion_id=d.id
      LEFT JOIN restaurante_plato p ON p.restaurante_id=r.id
      LEFT JOIN restaurante_mesa  m ON m.restaurante_id=r.id
      GROUP BY r.id, d.id
      ORDER BY r.nombre ASC;
    """
    qs = (Restaurante.objects
          .select_related('direccion')
          .annotate(num_platos=Count('plato', distinct=True),
                    num_mesas=Count('mesa', distinct=True))
          .order_by('nombre'))
    return render(request, 'restaurante/restaurantes.html', {'restaurantes': qs})

def detalle_restaurante(request, id: int):
    """
    Restaurante con dirección, platos, mesas y clientes frecuentes (M2M).
    SQL (idea):
      SELECT * FROM restaurante_restaurante WHERE id=%s;
      SELECT * FROM restaurante_direccion WHERE id=%s;
      SELECT * FROM restaurante_plato WHERE restaurante_id=%s ORDER BY nombre;
      SELECT * FROM restaurante_mesa  WHERE restaurante_id=%s ORDER BY numero;
      SELECT c.* FROM restaurante_restaurante_clientes_frecuentes rc
        JOIN restaurante_cliente c ON c.id=rc.cliente_id
        WHERE rc.restaurante_id=%s;
    """
    r = (Restaurante.objects
         .select_related('direccion')
         .prefetch_related('clientes_frecuentes', 'plato_set', 'mesa_set')
         .get(pk=id))
    return render(request, 'restaurante/restaurante_detalle.html', {'r': r})
def lista_platos(request):
    """
    Platos con restaurante y etiquetas (M2M) + limit.
    SQL (idea):
      SELECT p.*, r.* FROM restaurante_plato p JOIN restaurante_restaurante r ON p.restaurante_id=r.id
      ORDER BY p.precio ASC LIMIT 100;
    """
    platos = (Plato.objects
              .select_related('restaurante')
              .prefetch_related('etiquetas')
              .order_by('precio')[:100])
    return render(request, 'restaurante/platos.html', {'platos': platos})
def platos_por_categoria(request, categoria: str):
    """
    Filtra platos por categoría exacta.
    SQL (idea):
      SELECT * FROM restaurante_plato WHERE categoria=%s ORDER BY nombre ASC;
    """
    platos = (Plato.objects
              .filter(categoria=categoria)
              .select_related('restaurante')
              .prefetch_related('etiquetas')
              .order_by('nombre'))
    return render(request, 'restaurante/platos_categoria.html', {'platos': platos, 'categoria': categoria})
def buscar_platos(request, texto: str, precio_min: int):
    """
    AND: precio >= precio_min; OR: nombre contiene texto OR etiqueta.nombre = texto.
    SQL (idea):
      SELECT DISTINCT p.* FROM restaurante_plato p
      LEFT JOIN restaurante_plato_etiquetas pe ON pe.plato_id=p.id
      LEFT JOIN restaurante_etiqueta e ON e.id=pe.etiqueta_id
      WHERE p.precio >= %s AND (p.nombre LIKE %texto% OR e.nombre = %s)
      ORDER BY p.precio ASC;
    """
    platos = (Plato.objects
              .filter(Q(precio__gte=precio_min) &
                      (Q(nombre__icontains=texto) | Q(etiquetas__nombre__iexact=texto)))
              .select_related('restaurante')
              .prefetch_related('etiquetas')
              .order_by('precio')
              .distinct())
    return render(request, 'restaurante/platos_buscar.html', {'platos': platos, 'texto': texto, 'precio_min': precio_min})
