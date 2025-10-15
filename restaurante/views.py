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
