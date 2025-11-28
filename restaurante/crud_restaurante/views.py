from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import RestauranteForm
from restaurante.models import Restaurante


class RestauranteListView(ListView):
    model = Restaurante
    template_name = 'restaurante/crud_restaurante/listar.html'
    context_object_name = 'restaurantes'


class RestauranteDetailView(DetailView):
    model = Restaurante
    # Use the shared detalle template already present in the project
    template_name = 'restaurante/restaurante_detalle.html'
    # The shared template expects the object in context as 'r'
    context_object_name = 'r'


class RestauranteCreateView(CreateView):
    model = Restaurante
    form_class = RestauranteForm
    template_name = 'restaurante/crud_restaurante/crear.html'
    success_url = reverse_lazy('crud_restaurante:listar')


class RestauranteUpdateView(UpdateView):
    model = Restaurante
    form_class = RestauranteForm
    template_name = 'restaurante/crud_restaurante/editar.html'
    success_url = reverse_lazy('crud_restaurante:listar')


class RestauranteDeleteView(DeleteView):
    model = Restaurante
    template_name = 'restaurante/crud_restaurante/eliminar.html'
    success_url = reverse_lazy('crud_restaurante:listar')

    def get(self, request, *args, **kwargs):
        # Don't render a separate confirmation page on GET; redirect to list.
        return redirect(self.success_url)
