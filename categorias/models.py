from django.db import models
from django.urls import reverse

# Create your models here.

class Categoria(models.Model):
    nombre_categoria= models.CharField(max_length=50, unique=True)
    slug=models.SlugField(max_length=100, unique=True)
    descripcion=models.TextField(max_length=225, blank=True)
    imagen_categoria= models.ImageField(upload_to='fotos/mis_categorias', blank=True)

    def get_url(self):
        return reverse('productos_por_categoria', args=[self.slug])

    def __str__(self):
        return self.nombre_categoria

    
    