from django.shortcuts import render,get_object_or_404
from .models import Producto
from categorias.models import Categoria

# Create your views here.
def tienda(request, categoria_slug=None):
    categorias=None
    productos=None

    if categoria_slug !=None:
        categorias=get_object_or_404(Categoria, slug=categoria_slug)
        productos= Producto.objects.all().filter(categoria=categorias, esta_disponible=True)
        contar_productos= productos.count()
    
    else:
    
        productos= Producto.objects.all().filter( esta_disponible=True)
        contar_productos= productos.count()

    context ={
        'productos':productos,
        'contar_productos':contar_productos,
    }
    return render(request, 'tienda/tienda.html',context)

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
    unico_producto = get_object_or_404(Producto, categoria__slug=categoria_slug, slug=producto_slug)

    context = {
        'unico_producto': unico_producto,
    }
    return render(request, 'tienda/detalle_producto.html', context)