from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrito, name='carrito'),
    path('agregar_producto_carrito/<int:producto_id>/', views.agregar_producto_carrito, name='agregar_producto_carrito'),
    path('disminuir_cantidad_producto/<int:producto_id>/<int:carrito_item_id>/', views.disminuir_cantidad_producto, name='disminuir_cantidad_producto'),
    path('aumentar_cantidad_producto/<int:producto_id>/<int:carrito_item_id>/', views.aumentar_cantidad_producto, name='aumentar_cantidad_producto'),
    path('eliminar_producto_carrito/<int:producto_id>/<int:carrito_item_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('pagar/', views.pagar, name='pagar'),
        



]