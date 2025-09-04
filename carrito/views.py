from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from tienda.models import Producto,Variacion
from .models import Carrito, Carrito_Item
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.auth.decorators import login_required
#perfecto!



def _id_carrito(request):
    carrito= request.session.session_key
    if not carrito:
        carrito =request.session.create()
    return carrito

def agregar_producto_carrito(request, producto_id):
    current_user = request.user
    producto = Producto.objects.get(id=producto_id)
    variacion_producto = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            valor = request.POST[key]
            try:
                variacion = Variacion.objects.get(
                    producto=producto,
                    variacion_categoria__iexact=key,
                    valor_variacion__iexact=valor
                )
                variacion_producto.append(variacion)
            except Variacion.DoesNotExist:
                pass

    # Obtener o crear el carrito antes de cualquier uso
    try:
        carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
    except Carrito.DoesNotExist:
        carrito = Carrito.objects.create(id_carrito=_id_carrito(request))
        carrito.save()

    if current_user.is_authenticated:
        existe_item_carrito = Carrito_Item.objects.filter(producto=producto, user=current_user)
    else:
        existe_item_carrito = Carrito_Item.objects.filter(producto=producto, carrito=carrito)

    carrito_items = Carrito_Item.objects.filter(producto=producto, carrito=carrito)

    if carrito_items.exists():
        lista_existe_variacion = []
        id_list = []

        for item in carrito_items:
            existe_variacion = item.variaciones.all()
            lista_existe_variacion.append(list(existe_variacion))
            id_list.append(item.id)

        if variacion_producto in lista_existe_variacion:
            index = lista_existe_variacion.index(variacion_producto)
            item_id = id_list[index]
            item = Carrito_Item.objects.get(producto=producto, id=item_id)
            item.cantidad += 1
            item.save()
        else:
            carrito_item = Carrito_Item.objects.create(
                producto=producto,
                carrito=carrito,
                cantidad=1,
                user=current_user if current_user.is_authenticated else None
            )
            if variacion_producto:
                carrito_item.variaciones.add(*variacion_producto)
            carrito_item.save()
    else:
        carrito_item = Carrito_Item.objects.create(
            producto=producto,
            carrito=carrito,
            cantidad=1,
            user=current_user if current_user.is_authenticated else None
        )
        if variacion_producto:
            carrito_item.variaciones.add(*variacion_producto)
        carrito_item.save()

    return redirect('carrito')
        
     
   

def disminuir_cantidad_producto(request, producto_id, carrito_item_id):
    producto=get_object_or_404(Producto, id=producto_id)
    # Verificar si el carrito existe antes de intentar obtenerlo
    try:
        if request.user.is_authenticated:
            carrito_item = Carrito_Item.objects.get(producto=producto, user=request.user, id=carrito_item_id)
        else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            carrito_item = Carrito_Item.objects.get(producto=producto, carrito=carrito, id=carrito_item_id)
        if carrito_item.cantidad > 1:
            carrito_item.cantidad -= 1
            carrito_item.save()
        else:
            carrito_item.delete()
    except Carrito.DoesNotExist:
        return redirect('carrito')
    return redirect('carrito')

def aumentar_cantidad_producto(request, producto_id, carrito_item_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.user.is_authenticated:
        carrito_item = get_object_or_404(Carrito_Item, producto=producto, user=request.user, id=carrito_item_id)
    else:
        carrito = get_object_or_404(Carrito, id_carrito=_id_carrito(request))
        carrito_item = get_object_or_404(Carrito_Item, producto=producto, carrito=carrito, id=carrito_item_id)
    
    carrito_item.cantidad += 1
    carrito_item.save()

    return redirect('carrito')
def eliminar_producto_carrito(request,producto_id, carrito_item_id):
    producto=get_object_or_404(Producto, id=producto_id)
    # Verificar si el carrito existe antes de intentar obtenerlo
    if request.user.is_authenticated:
            carrito_item = Carrito_Item.objects.get(producto=producto, user=request.user, id=carrito_item_id)
    else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            carrito_item = Carrito_Item.objects.get(producto=producto, carrito=carrito, id=carrito_item_id)
    
    carrito_item.delete()
    return redirect('carrito')



def carrito(request, total=0, cantidad=0, carrito_items=None):
    try:
        iva=0
        total_pagar=0
        if request.user.is_authenticated:
            carrito_items = Carrito_Item.objects.filter(user=request.user, is_active=True)
        else:
            # Si el usuario no está autenticado, usamos la sesión para obtener el carrito
            carrito= Carrito.objects.get(id_carrito=_id_carrito(request))
            carrito_items= Carrito_Item.objects.filter(carrito=carrito, is_active=True)
        for carrito_item in carrito_items:
            total += (carrito_item.producto.precio * carrito_item.cantidad)
            cantidad += carrito_item.cantidad
        iva=(2 * total)/100
        total_pagar= total + iva
    except ObjectDoesNotExist: 
        pass

    context= {
        'total': total,
        'cantidad': cantidad,
        'carrito_items': carrito_items,
        'iva':iva,
        'total_pagar':total_pagar,
    }
    return render(request, 'tienda/carrito.html', context)

login_required(login_url='login')
def pagar(request, total=0, cantidad=0, carrito_items=None):
    try:
        iva=0
        total_pagar=0
        carrito= Carrito.objects.get(id_carrito=_id_carrito(request))
        carrito_items= Carrito_Item.objects.filter(carrito=carrito, is_active=True)
        for carrito_item in carrito_items:
            total += (carrito_item.producto.precio * carrito_item.cantidad)
            cantidad += carrito_item.cantidad
        iva=(2 * total)/100
        total_pagar= total + iva
    except ObjectDoesNotExist:
        pass

    context= {
        'total': total,
        'cantidad': cantidad,
        'carrito_items': carrito_items,
        'iva':iva,
        'total_pagar':total_pagar,
    }
    return render(request, 'tienda/pagar.html', context)


''' 
def _id_carrito(request):
    carrito = request.session.session_key
    if not carrito:
        request.session.create()
        carrito = request.session.session_key  # Actualizar la variable después de crear la sesión
    return carrito

def agregar_producto_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)  # Manejo seguro de errores

    carrito, _ = Carrito.objects.get_or_create(id_carrito=_id_carrito(request))
    
    carrito_item, creado = Carrito_Item.objects.get_or_create(producto=producto, carrito=carrito)

    if not creado:
        carrito_item.cantidad += 1
        carrito_item.save()

    return redirect('carrito')  # Redirigir al carrito

def carrito(request):
    carrito_id = _id_carrito(request)
    carrito_items = Carrito_Item.objects.filter(carrito__id_carrito=carrito_id)

    context = {'carrito_items': carrito_items}
    return render(request, 'tienda/carrito.html', context)  # Pasar productos al template
'''

