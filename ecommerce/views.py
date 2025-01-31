from django.shortcuts import HttpResponse,render
from tienda.models import Producto

def inicio(request):
    productos= Producto.objects.all().filter(esta_disponible=True)
    context ={
        'productos':productos
    }
    return render(request,"inicio.html",context)