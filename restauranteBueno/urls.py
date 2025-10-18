# restauranteBueno/urls.py
from django.contrib import admin
from django.urls import path, include


handler400 = 'restaurante.views.error_400'
handler403 = 'restaurante.views.error_403'
handler404 = 'restaurante.views.error_404'
handler500 = 'restaurante.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurante.urls')),  
]
