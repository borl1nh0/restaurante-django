from django.shortcuts import render, redirect, get_object_or_404
from django.views.defaults import page_not_found
from django.db.models import Q, Count, Sum, Avg
from restaurante.form import (RestauranteBusquedaAvanzadaForm, RestauranteForm,RestauranteCreateForm,DireccionForm,ClienteForm,PlatoForm,ReservaForm,ReservaCreateForm,PerfilClienteForm,PerfilClienteCreateForm,)
from .models import (Restaurante, Direccion, Plato, Etiqueta, Mesa, Cliente, PerfilCliente, Reserva, Pedido, LineaPedido)
from django.contrib import messages

def index(request):
    """Índice con enlaces."""
    return render(request, 'restaurante/index.html')

def error_400(request, exception=None):
    return render(request, 'errores/400.html', None, None, 400)

def error_403(request, exception=None):
    return render(request, 'errores/403.html', None, None, 403)

def error_404(request, exception=None):
    return render(request, 'errores/404.html', None, None, 404)

def error_500(request, exception=None):
    return render(request, 'errores/500.html', None, None, 500)

def lista_restaurantes(request):
    
    """
    restaurantes con su dirección (OneToOne) y contadores de platos/mesas.
   
    SQL:
      SELECT r.*, d.*, COUNT(DISTINCT p.id) AS num_platos, COUNT(DISTINCT m.id) AS num_mesas
      FROM restaurante_restaurante r
      JOIN restaurante_direccion d ON r.direccion_id=d.id
      LEFT JOIN restaurante_plato p ON p.restaurante_id=r.id
      LEFT JOIN restaurante_mesa  m ON m.restaurante_id=r.id
      GROUP BY r.id, d.id
      ORDER BY r.nombre ASC;
    """
    qs = (
        Restaurante.objects
        .select_related('direccion')
        .annotate(
            num_platos=Count('plato', distinct=True),
            num_mesas=Count('mesa', distinct=True),
        )
        .order_by('nombre')
    )
    return render(request, 'restaurante/restaurantes.html', {'restaurantes': qs})


def detalle_restaurante(request, id: int):
    """
    Muestra un restaurante con dirección, platos, mesas y clientes frecuentes.
    

    SQL:
      SELECT * FROM restaurante_restaurante WHERE id=%s;
      SELECT * FROM restaurante_direccion WHERE id=%s;
      SELECT * FROM restaurante_plato WHERE restaurante_id=%s ORDER BY nombre;
      SELECT * FROM restaurante_mesa  WHERE restaurante_id=%s ORDER BY numero;
      SELECT c.* FROM restaurante_restaurante_clientes_frecuentes rc
        JOIN restaurante_cliente c ON c.id=rc.cliente_id
       WHERE rc.restaurante_id=%s;
    """
    r = (
        Restaurante.objects
        .select_related('direccion')
        .prefetch_related('clientes_frecuentes', 'plato_set', 'mesa_set')
        .get(pk=id)
    )
    return render(request, 'restaurante/restaurante_detalle.html', {'r': r})


def lista_platos(request):
    """
    Lista platos con su restaurante y etiquetas (M2M), ordenado por precio.
    Optimización: select_related (FK) + prefetch_related (M2M) + limit.

    SQL:
      SELECT p.*, r.*
        FROM restaurante_plato p
        JOIN restaurante_restaurante r ON p.restaurante_id=r.id
       ORDER BY p.precio ASC
       LIMIT 100;
    """
    platos = (
        Plato.objects
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('precio')[:100]
    )
    return render(request, 'restaurante/platos.html', {'platos': platos})


def platos_por_categoria(request, categoria: str):
    """
    Filtra platos por categoría exacta (param str).
    Optimización: select_related + prefetch_related + order_by.

    SQL:
      SELECT * FROM restaurante_plato
       WHERE categoria=%s
       ORDER BY nombre ASC;
    """
    platos = (
        Plato.objects
        .filter(categoria=categoria)
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('nombre')
    )
    return render(request, 'restaurante/platos_categoria.html', {
        'platos': platos,
        'categoria': categoria,
    })


def buscar_platos(request, texto: str, precio_min: int):
    """
    Búsqueda con AND/OR:
      - AND: precio >= precio_min
      - OR : nombre contiene 'texto'  OR  etiqueta.nombre = 'texto'
    Optimización: select_related + prefetch_related + distinct (por M2M).

    SQL:
      SELECT DISTINCT p.*
        FROM restaurante_plato p
   LEFT JOIN restaurante_plato_etiquetas pe ON pe.plato_id=p.id
   LEFT JOIN restaurante_etiqueta e        ON e.id=pe.etiqueta_id
       WHERE p.precio >= %s
         AND (p.nombre LIKE %texto% OR e.nombre = %s)
       ORDER BY p.precio ASC;
    """
    platos = (
        Plato.objects
        .filter(
            Q(precio__gte=precio_min) &
            (Q(nombre__icontains=texto) | Q(etiquetas__nombre__iexact=texto))
        )
        .select_related('restaurante')
        .prefetch_related('etiquetas')
        .order_by('precio')
        .distinct()
    )
    return render(request, 'restaurante/platos_buscar.html', {
        'platos': platos,
        'texto': texto,
        'precio_min': precio_min,
    })


def lista_pedidos(request):
    """
    Muestra pedidos recientes y un resumen global (SUM/AVG).
    Optimización: select_related (FK/O2O) + prefetch_related (reversa de líneas).

    SQL:
      SELECT SUM(total) AS suma, AVG(total) AS promedio
        FROM restaurante_pedido;

      SELECT p.*, c.*, r.*
        FROM restaurante_pedido p
        JOIN restaurante_cliente c     ON p.cliente_id=c.id
        JOIN restaurante_restaurante r ON p.restaurante_id=r.id
       ORDER BY p.creado DESC
       LIMIT 100;
    """
    resumen = Pedido.objects.aggregate(
        suma=Sum('total'),
        promedio=Avg('total')
    )
    pedidos = (
        Pedido.objects
        .select_related('cliente', 'restaurante', 'reserva')
        .prefetch_related('lineapedido_set__plato')
        .order_by('-id')[:100]

    )
    return render(request, 'restaurante/pedidos.html', {
        'resumen': resumen,
        'pedidos': pedidos,
    })


def pedidos_sin_lineas(request):
    """
    Lista pedidos que no tienen ninguna línea (reversa isnull=True).

    SQL:
      SELECT p.*
        FROM restaurante_pedido p
   LEFT JOIN restaurante_lineapedido lp ON lp.pedido_id=p.id
       WHERE lp.id IS NULL;
    """
    pedidos = (
        Pedido.objects
        .filter(lineapedido__isnull=True)
        .select_related('cliente', 'restaurante', 'reserva')
        .order_by('id')
    )
    return render(request, 'restaurante/pedidos_sin_lineas.html', {'pedidos': pedidos})


def clientes_frecuentes(request):
    """
    Clientes con nº de pedidos (aggregate por fila) y favoritos (M2M).
    Requisito HAVING: filtrar por anotación (num_pedidos >= 1).

    SQL:
      SELECT c.*, COUNT(p.id) AS num_pedidos
        FROM restaurante_cliente c
   LEFT JOIN restaurante_pedido p ON p.cliente_id=c.id
    GROUP BY c.id
      HAVING COUNT(p.id) >= 1
    ORDER BY c.nombre ASC;
    """
    clientes = (
        Cliente.objects
        .annotate(num_pedidos=Count('pedido'))
        .filter(num_pedidos__gte=1)
        .prefetch_related('restaurantes_favoritos')
        .order_by('nombre')
    )
    return render(request, 'restaurante/clientes_frecuentes.html', {'clientes': clientes})


def buscar_simple(request, texto: str):
    """
    Búsqueda sencilla con re_path: clientes y platos por nombre (OR).
    Optimización: order_by + limit; select_related para mostrar restaurante.

    SQL:
      SELECT * FROM restaurante_cliente
       WHERE nombre LIKE %texto%
       ORDER BY nombre ASC
       LIMIT 50;

      SELECT * FROM restaurante_plato
       WHERE nombre LIKE %texto%
       ORDER BY nombre ASC
       LIMIT 50;
    """
    clientes = (
        Cliente.objects
        .filter(nombre__icontains=texto)
        .order_by('nombre')[:50]
    )
    platos = (
        Plato.objects
        .filter(nombre__icontains=texto)
        .select_related('restaurante')
        .order_by('nombre')[:50]
    )
    return render(request, 'restaurante/buscar_simple.html', {
        'texto': texto,
        'clientes': clientes,
        'platos': platos,
    })

def restaurantes_listar(request):
    restaurantes = Restaurante.objects.all()
    return render(request, 'restaurante/CRUD_direccion/listar.html', {'restaurantes': restaurantes})


def restaurantes_crear(request):
    if request.method == 'POST':
        form = RestauranteCreateForm(request.POST)
        if form.is_valid():
            
            nombre = form.cleaned_data['nombre']
            telefono = form.cleaned_data['telefono']
            direccion = form.cleaned_data['direccion']
            clientes = form.cleaned_data.get('clientes_frecuentes')
            r = Restaurante.objects.create(nombre=nombre, telefono=telefono, direccion=direccion)
            if clientes:
                r.clientes_frecuentes.set(clientes)
            messages.success(request, 'Restaurante creado correctamente.')
            return redirect('restaurantes_listar')
    else:
        form = RestauranteCreateForm()
    return render(request, 'restaurante/CRUD_direccion/crear.html', {'form': form})


def restaurantes_editar(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        form = RestauranteForm(request.POST)
        if form.is_valid():
            restaurante.nombre = form.cleaned_data['nombre']
            restaurante.telefono = form.cleaned_data['telefono']
            
            if 'email' in form.cleaned_data:
                restaurante.email = form.cleaned_data.get('email') or ''
            if 'web' in form.cleaned_data:
                restaurante.web = form.cleaned_data.get('web') or ''
            if 'abierto' in form.cleaned_data:
                restaurante.abierto = form.cleaned_data.get('abierto', True)
            restaurante.direccion = form.cleaned_data['direccion']
            
            if restaurante.email is None:
                restaurante.email = ''
            if restaurante.web is None:
                restaurante.web = ''
            restaurante.save()
            clientes = form.cleaned_data.get('clientes_frecuentes')
            if clientes is not None:
                restaurante.clientes_frecuentes.set(clientes)
            messages.success(request, 'Restaurante actualizado correctamente.')
            return redirect('restaurantes_listar')
    else:
        
        initial = {
            'nombre': restaurante.nombre,
            'telefono': restaurante.telefono,
            'email': restaurante.email,
            'web': restaurante.web,
            'abierto': restaurante.abierto,
            'direccion': restaurante.direccion,
            'clientes_frecuentes': restaurante.clientes_frecuentes.all(),
        }
        form = RestauranteForm(initial=initial)
    return render(request, 'restaurante/CRUD_direccion/editar.html', {'form': form, 'restaurante': restaurante})

def restaurantes_eliminar(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        restaurante.delete()
        messages.success(request, 'Restaurante eliminado correctamente.')
        return redirect('restaurantes_listar')
   
    return redirect('restaurantes_listar')


# CRUD para Direccion

def direccion_listar(request):
    direcciones = Direccion.objects.all()
    return render(request, 'restaurante/direcciones.html', {'direcciones': direcciones})

def direccion_crear(request):
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección creada.')
            return redirect('direccion_listar')
    else:
        form = DireccionForm()
    return render(request, 'restaurante/form_direccion.html', {'form': form})

def direccion_editar(request, id):
    direccion = get_object_or_404(Direccion, pk=id)
    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada.')
            return redirect('direccion_listar')
    else:
        form = DireccionForm(instance=direccion)
    return render(request, 'restaurante/form_direccion.html', {'form': form, 'direccion': direccion})

def direccion_eliminar(request, id):
    direccion = get_object_or_404(Direccion, pk=id)
    if request.method == 'POST':
        direccion.delete()
        messages.success(request, 'Dirección eliminada.')
        return redirect('direccion_listar')
  
    return redirect('direccion_listar')


# CRUD para Reserva
from restaurante.form import ReservaForm, ReservaCreateForm, PerfilClienteForm, PerfilClienteCreateForm

def reservas_listar(request):
    reservas = Reserva.objects.select_related('cliente', 'mesa').order_by('-fecha', '-hora')
    return render(request, 'restaurante/crud_reservas/listar.html', {'reservas': reservas})


def reservas_crear(request):
    if request.method == 'POST':
        form = ReservaCreateForm(request.POST)
        if form.is_valid():
            r = Reserva.objects.create(
                cliente=form.cleaned_data['cliente'],
                mesa=form.cleaned_data['mesa'],
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                estado='pendiente',
                notas=form.cleaned_data.get('notas', ''),
            )
            messages.success(request, 'Reserva creada correctamente.')
            return redirect('reservas_listar')
    else:
        form = ReservaCreateForm()
    return render(request, 'restaurante/crud_reservas/crear.html', {'form': form})


def reservas_editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva.cliente = form.cleaned_data['cliente']
            reserva.mesa = form.cleaned_data['mesa']
            reserva.fecha = form.cleaned_data['fecha']
            reserva.hora = form.cleaned_data['hora']
            reserva.estado = form.cleaned_data.get('estado', reserva.estado)
            reserva.notas = form.cleaned_data.get('notas', reserva.notas)
            reserva.save()
            messages.success(request, 'Reserva actualizada correctamente.')
            return redirect('reservas_listar')
    else:
        initial = {
            'cliente': reserva.cliente,
            'mesa': reserva.mesa,
            'fecha': reserva.fecha,
            'hora': reserva.hora,
            'estado': reserva.estado,
            'notas': reserva.notas,
        }
        form = ReservaForm(initial=initial)
    return render(request, 'restaurante/crud_reservas/editar.html', {'form': form, 'reserva': reserva})


def reservas_eliminar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva eliminada correctamente.')
        return redirect('reservas_listar')
    
    return redirect('reservas_listar')


# CRUD para PerfilCliente
def perfil_listar(request):
    perfiles = PerfilCliente.objects.select_related('cliente').order_by('cliente__nombre')
    return render(request, 'restaurante/crud_perfilClientes/listar.html', {'perfiles': perfiles})


def perfil_crear(request):
    if request.method == 'POST':
        form = PerfilClienteCreateForm(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            perfil = PerfilCliente.objects.create(
                cliente=cliente,
                alergias=form.cleaned_data.get('alergias', ''),
                preferencias=form.cleaned_data.get('preferencias', ''),
            )
            messages.success(request, 'Perfil de cliente creado correctamente.')
            return redirect('perfil_listar')
    else:
        form = PerfilClienteCreateForm()
    return render(request, 'restaurante/crud_perfilClientes/crear.html', {'form': form})


def perfil_editar(request, pk):
    perfil = get_object_or_404(PerfilCliente, pk=pk)
    if request.method == 'POST':
        form = PerfilClienteForm(request.POST)
        if form.is_valid():
            perfil.alergias = form.cleaned_data.get('alergias', '')
            perfil.preferencias = form.cleaned_data.get('preferencias', '')
           
            perfil.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_listar')
    else:
        initial = {
            'alergias': perfil.alergias,
            'preferencias': perfil.preferencias,
        }
        form = PerfilClienteForm(initial=initial)
    return render(request, 'restaurante/crud_perfilClientes/editar.html', {'form': form, 'perfil': perfil})


def perfil_eliminar(request, pk):
    perfil = get_object_or_404(PerfilCliente, pk=pk)
    if request.method == 'POST':
        perfil.delete()
        messages.success(request, 'Perfil eliminado correctamente.')
        return redirect('perfil_listar')
    
    return redirect('perfil_listar')


# CRUD para Cliente.

def clientes_listar(request):
    clientes = Cliente.objects.order_by('nombre')
    return render(request, 'restaurante/crud_clientes/listar.html', {'clientes': clientes})

def clientes_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('crud_clientes:listar')
    else:
        form = ClienteForm()
    return render(request, 'restaurante/crud_clientes/crear.html', {'form': form})

def clientes_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('crud_clientes:listar')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'restaurante/crud_clientes/editar.html', {'form': form, 'cliente': cliente})

def clientes_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('crud_clientes:listar')
    return render(request, 'restaurante/crud_clientes/eliminar.html', {'cliente': cliente})


# CRUD para Plato .

def platos_listar(request):
    platos = Plato.objects.select_related('restaurante').order_by('nombre')
    return render(request, 'restaurante/crud_platos/listar.html', {'platos': platos})

def platos_crear(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato creado correctamente.')
            return redirect('crud_platos:listar')
    else:
        form = PlatoForm()
    return render(request, 'restaurante/crud_platos/crear.html', {'form': form})

def platos_editar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato actualizado correctamente.')
            return redirect('crud_platos:listar')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'restaurante/crud_platos/editar.html', {'form': form, 'plato': plato})

def platos_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, 'Plato eliminado correctamente.')
        return redirect('crud_platos:listar')
    return render(request, 'restaurante/crud_platos/eliminar.html', {'plato': plato})


def restaurante_busqueda_avanzada(request):
    QS = Restaurante.objects.select_related("direccion").all()

  
    if request.GET:
        form = RestauranteBusquedaAvanzadaForm(request.GET)

        if form.is_valid():
            nombre = form.cleaned_data.get("nombre")
            telefono = form.cleaned_data.get("telefono")
            direccion = form.cleaned_data.get("direccion")

            if nombre:
                QS = QS.filter(nombre__icontains=nombre)

            if telefono:
                QS = QS.filter(telefono__icontains=telefono)

            if direccion:
                QS = QS.filter(
                    Q(direccion__calle__icontains=direccion) |
                    Q(direccion__ciudad__icontains=direccion) |
                    Q(direccion__codigo_postal__icontains=direccion)
                )

    else:
       
        form = RestauranteBusquedaAvanzadaForm()

   
    return render(
        request,
        "restaurante/busqueda_avanzada.html",
        {
            "form": form,             
            "restaurantes": QS,
        }
    )


