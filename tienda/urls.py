from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, VariacionViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'variaciones', VariacionViewSet)

urlpatterns = [
    path('',views.tienda, name='tienda'),
    path('categoria/<slug:categoria_slug>/', views.tienda, name='productos_por_categoria'),
    path('categoria/<slug:categoria_slug>/<slug:producto_slug>/', views.detalle_producto, name='detalle_producto'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('api/', include('tienda.api_urls')),

]