from django.urls import path
from . import views

app_name = 'crud_restaurante'

urlpatterns = [
    path('', views.RestauranteListView.as_view(), name='listar'),
    path('crear/', views.RestauranteCreateView.as_view(), name='crear'),
    path('editar/<int:pk>/', views.RestauranteUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.RestauranteDeleteView.as_view(), name='eliminar'),
    path('<int:pk>/', views.RestauranteDetailView.as_view(), name='detalle'),
]
