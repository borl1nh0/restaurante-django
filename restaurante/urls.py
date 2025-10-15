from django.urls import path, re_path  
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('restaurantes/', views.lista_restaurantes, name='lista_restaurantes'),
    path('restaurante/<int:id>/', views.detalle_restaurante, name='detalle_restaurante'),

]
