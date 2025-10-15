from django.urls import path, re_path  
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('restaurantes/', views.lista_restaurantes, name='lista_restaurantes'),
    path('restaurante/<int:id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('platos/', views.lista_platos, name='lista_platos'),
    path('platos/categoria/<str:categoria>/', views.platos_por_categoria, name='platos_por_categoria'),

]
