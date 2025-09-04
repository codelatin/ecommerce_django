from django.urls import path,include
from . import views

urlpatterns = [
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('pagos/', views.pagos, name='pagos'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal/return/', views.paypal_return, name='paypal_return'),
    path('pago_exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago_cancelado/', views.pago_cancelado, name='pago_cancelado'),
]