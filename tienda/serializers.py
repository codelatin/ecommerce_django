# tienda/serializers.py
from rest_framework import serializers
from .models import Producto, Variacion

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.StringRelatedField(source='categoria', read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'

class VariacionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.StringRelatedField(source='producto', read_only=True)

    class Meta:
        model = Variacion
        fields = '__all__'
