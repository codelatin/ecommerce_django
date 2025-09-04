from django.db import models
from categorias.models import Categoria
from django.urls import reverse
# Create your models here.
class Producto(models.Model):
    nombre_producto= models.CharField(max_length=200,unique=True)
    slug= models.SlugField(max_length=200,unique=True)
    descripcion=models.TextField(max_length=500,unique=True)
    precio=models.IntegerField()
    imagen=models.ImageField(upload_to='fotos/mis_productos')
    stock=models.IntegerField()
    esta_disponible= models.BooleanField(default=True)
    categoria=models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    fecha_modificacion= models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('detalle_producto', args=[self.categoria.slug, self.slug])

    def __str__(self):
        return self.nombre_producto
    
class VariacionManager(models.Manager):
        def colores(self):
            return super(VariacionManager, self).filter(variacion_categoria='color', is_active=True)
        
        def tallas(self):
            return super(VariacionManager, self).filter(variacion_categoria='talla', is_active=True)
    
    

eleccion_variacion_categoria =(
    ('color', 'color'),
    ('talla','talla'),
)

class Variacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variacion_categoria = models.CharField(max_length=100, choices=eleccion_variacion_categoria)
    valor_variacion = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now=True)

    objects = VariacionManager()

    def __str__(self):
        return f"{self.producto.nombre_producto} - {self.variacion_categoria}: {self.valor_variacion}"

 


















