from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('restaurantes/', views.lista_restaurantes, name='lista_restaurantes'),
    path('restaurante/<int:id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('restaurante/crear/', views.crear_restaurante, name='crear_restaurante'),
    path('platos/', views.lista_platos, name='lista_platos'),
    path('platos/categoria/<str:categoria>/', views.platos_por_categoria, name='platos_por_categoria'),
    path('platos/buscar/<str:texto>/<int:precio_min>/', views.buscar_platos, name='buscar_platos'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/sin-lineas/', views.pedidos_sin_lineas, name='pedidos_sin_lineas'),
    path('clientes/frecuentes/', views.clientes_frecuentes, name='clientes_frecuentes'),
    re_path(r'^buscar/(?P<texto>\w{3,20})/$', views.buscar_simple, name='buscar_simple'),
    
    
]
