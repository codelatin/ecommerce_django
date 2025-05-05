from django.contrib import admin
from .models import Carrito,Carrito_Item

# Register your models here.

class CarritoAdmin(admin.ModelAdmin):
    list_display=('id_carrito','fecha_agregado')

class CarritoItemAdmin(admin.ModelAdmin):
    list_display=('producto','carrito','cantidad','is_active')
    
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Carrito_Item,CarritoItemAdmin)

