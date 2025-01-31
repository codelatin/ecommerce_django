from django.contrib import admin
from .models import Producto

# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display =('nombre_producto','precio','stock','categoria','fecha_modificacion','esta_disponible')
    prepopulated_fields ={'slug':('nombre_producto',)}

admin.site.register(Producto,ProductoAdmin)