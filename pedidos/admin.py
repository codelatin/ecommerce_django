from django.contrib import admin
from .models import Pago, Pedido, ProductoOrdenado


class ProductoOrdenadoInline(admin.TabularInline):
    model = ProductoOrdenado
    extra = 0
    readonly_fields = ('pago', 'user', 'producto', 'variaciones', 'cantidad', 'precio_producto')
    can_delete = False
    fields = ('producto', 'variaciones', 'cantidad', 'precio_producto')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'user', 'metodo_pago', 'monto_pagado', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('id_pago', 'user__email', 'user__username')
    readonly_fields = ('id_pago', 'fecha_creacion')
    list_per_page = 25
    ordering = ('-fecha_creacion',)

    fieldsets = (
        ('Información del Pago', {
            'fields': ('user', 'id_pago', 'metodo_pago', 'monto_pagado')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_creacion')
        }),
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'get_nombre_completo', 'user', 'total_pedido', 'estado', 'esta_ordenado', 'fecha_creacion')
    list_filter = ('estado', 'esta_ordenado', 'fecha_creacion', 'pais', 'ciudad')
    search_fields = ('numero_pedido', 'nombre', 'apellido', 'user__email', 'user__username')
    readonly_fields = ('numero_pedido', 'fecha_creacion', 'actualizado', 'ip')
    list_per_page = 25
    ordering = ('-fecha_creacion',)
    inlines = [ProductoOrdenadoInline]

    fieldsets = (
        ('Información del Cliente', {
            'fields': ('user', 'nombre', 'apellido', 'direccion', 'ciudad', 'pais')
        }),
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'pago', 'total_pedido', 'impuesto', 'observacion_pedido')
        }),
        ('Estado y Control', {
            'fields': ('estado', 'esta_ordenado', 'ip')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'actualizado'),
            'classes': ('collapse',)
        }),
    )

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'nombre'

    actions = ['marcar_como_procesando', 'marcar_como_enviado', 'marcar_como_entregado']

    def marcar_como_procesando(self, request, queryset):
        updated = queryset.update(estado='Procesando')
        self.message_user(request, f'{updated} pedidos marcados como procesando.')
    marcar_como_procesando.short_description = "Marcar como Procesando"

    def marcar_como_enviado(self, request, queryset):
        updated = queryset.update(estado='Enviado')
        self.message_user(request, f'{updated} pedidos marcados como enviado.')
    marcar_como_enviado.short_description = "Marcar como Enviado"

    def marcar_como_entregado(self, request, queryset):
        updated = queryset.update(estado='Entregado')
        self.message_user(request, f'{updated} pedidos marcados como entregado.')
    marcar_como_entregado.short_description = "Marcar como Entregado"


@admin.register(ProductoOrdenado)
class ProductoOrdenadoAdmin(admin.ModelAdmin):
    list_display = ('get_numero_pedido', 'producto', 'user', 'cantidad', 'precio_producto', 'color', 'size', 'ordenado', 'fecha_creacion')
    list_filter = ('ordenado', 'fecha_creacion', 'variaciones')
    search_fields = ('pedido__numero_pedido', 'producto__nombre_producto', 'user__email', 'user__username')
    readonly_fields = ('fecha_creacion', 'actualizado', 'color_display', 'size_display')
    list_per_page = 25
    ordering = ('-fecha_creacion',)

    fieldsets = (
        ('Información del Pedido', {
            'fields': ('pedido', 'pago', 'user')
        }),
        ('Información del Producto', {
            'fields': ('producto', 'variaciones', 'cantidad', 'precio_producto')
        }),
        ('Estado y Fechas', {
            'fields': ('ordenado', 'fecha_creacion', 'actualizado')
        }),
    )

    # === FUNCIONES CORREGIDAS PARA TU MODELO VARIACION ===
    def get_variacion_valor(self, obj, tipo):
        """Busca una variación por categoría (ej. 'color', 'talla') y devuelve su valor."""
        for variacion in obj.variaciones.all():
            if variacion.variacion_categoria == tipo:
                return variacion.valor_variacion
        return '-'

    def color(self, obj):
        return self.get_variacion_valor(obj, 'color')
    color.short_description = 'Color'

    def size(self, obj):
        return self.get_variacion_valor(obj, 'talla')
    size.short_description = 'Talla/Size'

    def color_display(self, obj):
        return self.color(obj)
    color_display.short_description = 'Color'

    def size_display(self, obj):
        return self.size(obj)
    size_display.short_description = 'Talla/Size'

    def get_numero_pedido(self, obj):
        return obj.pedido.numero_pedido
    get_numero_pedido.short_description = 'Número de Pedido'
    get_numero_pedido.admin_order_field = 'pedido__numero_pedido'

    actions = ['marcar_como_ordenado']

    def marcar_como_ordenado(self, request, queryset):
        updated = queryset.update(ordenado=True)
        self.message_user(request, f'{updated} productos marcados como ordenados.')
    marcar_como_ordenado.short_description = "Marcar como Ordenado"