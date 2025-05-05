from django.contrib import admin
from .models import Producto, Variacion

# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display =('nombre_producto','precio','stock','categoria','fecha_modificacion','esta_disponible')
    prepopulated_fields ={'slug':('nombre_producto',)}

class VariacionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'variacion_categoria','valor_variacion','is_active')
    list_editable=('is_active',)
    list_filter= ('producto', 'variacion_categoria','valor_variacion')

admin.site.register(Producto,ProductoAdmin)
admin.site.register(Variacion,VariacionAdmin)