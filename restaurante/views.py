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

