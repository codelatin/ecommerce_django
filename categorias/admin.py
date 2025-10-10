from django.contrib import admin
from .models import Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista del admin
    list_display = ('nombre_categoria', 'slug', 'descripcion_corta')
    
    # Permite buscar por estos campos
    search_fields = ('nombre_categoria', 'descripcion')
    
    # Filtros laterales (útil si tienes muchas categorías)
    list_filter = ('nombre_categoria',)
    
    # Campos que se autocompletan al escribir (slug se genera desde nombre_categoria)
    prepopulated_fields = {'slug': ('nombre_categoria',)}
        
    # Número de elementos por página en la lista
    list_per_page = 20

    # Método personalizado para mostrar una versión corta de la descripción
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'  # Nombre de la columna en el admin