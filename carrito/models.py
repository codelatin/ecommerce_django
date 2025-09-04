from django.db import models
from tienda.models import Producto,Variacion
from auths.models import Auth
# Create your models here.

class Carrito(models.Model):
    id_carrito= models.CharField(max_length=250, blank=True)
    fecha_agregado=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id_carrito


class Carrito_Item(models.Model):
    user =models.ForeignKey(Auth,on_delete=models.CASCADE, null=True)
    producto= models.ForeignKey(Producto, on_delete=models.CASCADE)
    variaciones= models.ManyToManyField(Variacion, blank=True)
    carrito= models.ForeignKey(Carrito, on_delete=models.CASCADE, null=True)
    cantidad= models.IntegerField()
    is_active= models.BooleanField(default=True)

    def sub_total(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto} - {self.cantidad} unidades"