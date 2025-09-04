from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import viewsets
from tienda.models import Producto
from tienda.serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer