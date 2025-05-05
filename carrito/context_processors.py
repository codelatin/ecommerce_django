from .models import Carrito, Carrito_Item
from .views import _id_carrito

def contador_carrito(request):
    contar_carrito= 0
    if 'admin' in request.path:
        return{}
    else:
        try:
            carrito= Carrito.objects.filter(id_carrito=_id_carrito(request))
            carrito_items=Carrito_Item.objects.all().filter(carrito=carrito[:1])
            for carrito_item in carrito_items:
                contar_carrito += carrito_item.cantidad 
        except Carrito.DoesNotExist:
            contar_carrito=0
    return dict(contar_carrito=contar_carrito)
