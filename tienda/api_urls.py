
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, VariacionViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'variaciones', VariacionViewSet)

urlpatterns = router.urls