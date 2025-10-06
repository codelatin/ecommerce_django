from django.db import models
from auths.models import Auth
from tienda.models import Producto, Variacion

class Pago(models.Model):
    user = models.ForeignKey(Auth, on_delete=models.CASCADE)
    id_pago = models.CharField(max_length=200)
    metodo_pago = models.CharField(max_length=200)
    monto_pagado = models.CharField(max_length=200)
    estado = models.CharField(max_length=200, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id_pago

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('Nuevo', 'Nuevo'),
        ('Procesando', 'Procesando'),
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    )
    user = models.ForeignKey(Auth, on_delete=models.SET_NULL, null=True, blank=True)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True)
    numero_pedido = models.CharField(max_length=200, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    observacion_pedido = models.TextField(blank=True, null=True)
    total_pedido = models.FloatField()
    impuesto = models.FloatField(default=0)
    estado = models.CharField(max_length=100, choices=ESTADO_CHOICES, default='Nuevo')
    ip = models.CharField(max_length=200, blank=True, null=True)
    esta_ordenado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class ProductoOrdenado(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Auth, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variaciones= models.ManyToManyField(Variacion, blank=True)

    cantidad = models.IntegerField()
    precio_producto = models.FloatField()
    ordenado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.producto.nombre_producto
        