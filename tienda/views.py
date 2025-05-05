from django.shortcuts import render,get_object_or_404
from .models import Producto
from categorias.models import Categoria
from carrito.views import _id_carrito
from django.http import HttpResponse
from carrito.models import Carrito_Item
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.db.models import Q

# Create your views here.
def tienda(request, categoria_slug=None):
    categorias=None
    productos=None

    if categoria_slug !=None:
        categorias=get_object_or_404(Categoria, slug=categoria_slug)
        productos= Producto.objects.all().filter(categoria=categorias, esta_disponible=True)
        paginator=Paginator(productos,3)
        page=request.GET.get('page')
        pagina_productos=paginator.get_page(page)
        contar_productos= productos.count()
    
    else:
    
        productos= Producto.objects.all().filter(esta_disponible=True).order_by('id')
        paginator=Paginator(productos,3)
        page=request.GET.get('page')
        pagina_productos=paginator.get_page(page)
        contar_productos= productos.count()

    context ={
        'productos':pagina_productos,
        'contar_productos':contar_productos,
    }
    return render(request, 'tienda/tienda.html',context)
'''' 
def buscar_producto(request):
    if 'keypalabra' in request.GET:
        keypalabra= request.GET['keypalabra']
        if keypalabra:
            productos= Producto.objects.order_by('-fecha_creacion').filter(Q(descripcion__icontains=keypalabra) |Q(nombre_producto__icontains=keypalabra))
            contar_productos= productos.count()
    context ={
        'productos':productos,
        'contar_productos': contar_productos,

    }

    return render(request, 'tienda/tienda.html', context)
'''

def buscar_producto(request):
    

    if 'keypalabra' in request.GET:
        keypalabra = request.GET['keypalabra'].strip().lower()
        if keypalabra:
            productos = Producto.objects.order_by('-fecha_creacion').filter(Q(descripcion__icontains=keypalabra) | Q(nombre_producto__icontains=keypalabra))
                
            contar_productos = productos.count()

    context = {
        'productos': productos,
        'contar_productos': contar_productos,
    }

    return render(request, 'tienda/tienda.html', context)

#forma 1

'''def detalle_producto(request,categoria_slug,producto_slug):
    try:
        unico_producto= Producto.objects.get(categoria__slug=categoria_slug,slug=producto_slug)
    except Exception as e:
        raise e
    
    context = {
        'unico_producto':unico_producto,
    }
    return render(request, 'tienda/detalle_producto.html', context)
'''
#forma
def detalle_producto(request, categoria_slug, producto_slug):
    try:
        unico_producto = get_object_or_404(Producto, categoria__slug=categoria_slug, slug=producto_slug)
        esta_encarrito=Carrito_Item.objects.filter(carrito__id_carrito=_id_carrito(request),producto=unico_producto).exists()
        
    except Exception as e:
        raise e
    


    context = {
        'unico_producto': unico_producto,
        'esta_encarrito': esta_encarrito
    }
    return render(request, 'tienda/detalle_producto.html', context)