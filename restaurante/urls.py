from django.urls import include, path, re_path
from . import views

crud_restaurante_patterns = [
    path('', views.restaurantes_listar, name='listar'),
    path('crear/', views.restaurantes_crear, name='crear'),
    path('detalle/<int:id>/', views.detalle_restaurante, name='detalle'),
    path('editar/<int:pk>/', views.restaurantes_editar, name='editar'),
    path('eliminar/<int:pk>/', views.restaurantes_eliminar, name='eliminar'),
]

crud_clientes_patterns = [
    path('', views.clientes_listar, name='listar'),
    path('crear/', views.clientes_crear, name='crear'),
    path('editar/<int:pk>/', views.clientes_editar, name='editar'),
    path('eliminar/<int:pk>/', views.clientes_eliminar, name='eliminar'),
]

urlpatterns = [
    # CRUD RESTAURANTE 
    path('crud_restaurante/', include((crud_restaurante_patterns, 'crud_restaurante'), namespace='crud_restaurante')),
    path('crud_clientes/', include((crud_clientes_patterns, 'crud_clientes'), namespace='crud_clientes')),

    path('', views.index, name='index'),
    path('restaurante/', views.restaurantes_listar, name='restaurantes_listar'),
    path('restaurante/crear/', views.restaurantes_crear, name='restaurantes_crear'),
    path('restaurante/editar/<int:pk>/', views.restaurantes_editar, name='restaurantes_editar'),
    path('restaurante/eliminar/<int:pk>/', views.restaurantes_eliminar, name='restaurantes_eliminar'),
     # CRUD de Direccion
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/crear/', views.direccion_crear, name='direccion_crear'),
    path('direcciones/editar/<int:id>/', views.direccion_editar, name='direccion_editar'),
    path('direcciones/eliminar/<int:id>/', views.direccion_eliminar, name='direccion_eliminar'),
    
    path('restaurante/<int:id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('platos/', views.lista_platos, name='lista_platos'),
    path('platos/categoria/<str:categoria>/', views.platos_por_categoria, name='platos_por_categoria'),
    path('platos/buscar/<str:texto>/<int:precio_min>/', views.buscar_platos, name='buscar_platos'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    # CRUD para Reservas
    path('reservas/', views.reservas_listar, name='reservas_listar'),
    path('reservas/crear/', views.reservas_crear, name='reservas_crear'),
    path('reservas/editar/<int:pk>/', views.reservas_editar, name='reservas_editar'),
    path('reservas/eliminar/<int:pk>/', views.reservas_eliminar, name='reservas_eliminar'),
    path('pedidos/sin-lineas/', views.pedidos_sin_lineas, name='pedidos_sin_lineas'),
    path('clientes/frecuentes/', views.clientes_frecuentes, name='clientes_frecuentes'),
    # CRUD para PerfilCliente
    path('perfiles/', views.perfil_listar, name='perfil_listar'),
    path('perfiles/crear/', views.perfil_crear, name='perfil_crear'),
    path('perfiles/editar/<int:pk>/', views.perfil_editar, name='perfil_editar'),
    path('perfiles/eliminar/<int:pk>/', views.perfil_eliminar, name='perfil_eliminar'),
    re_path(r'^buscar/(?P<texto>\w{3,20})/$', views.buscar_simple, name='buscar_simple'),
    
    
]
