from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, request
from carrito.models import Carrito_Item
from .forms import PedidoForm
import datetime
from .models import Pedido, ProductoOrdenado, Pago
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.contrib import messages

# Importaciones para PayPal IPN
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.    
def pagos(request):
    return render(request, 'pedidos/pagos.html')

@login_required
def realizar_pedido(request, total=0, cantidad=0):
    current_user = request.user
    carrito_items = Carrito_Item.objects.filter(user=current_user).select_related('producto')
    contador_carrito = carrito_items.count()

    if contador_carrito <= 0:
        return redirect('tienda')

    # Calcular subtotal
    for carrito_item in carrito_items:
        total += (carrito_item.producto.precio * carrito_item.cantidad)
        cantidad += carrito_item.cantidad

    iva = (2 * total) / 100
    total_pagar = total + iva

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # Crear el pedido
            pedido = Pedido()
            pedido.user = current_user
            pedido.nombre = form.cleaned_data['nombre']
            pedido.apellido = form.cleaned_data['apellido']
            pedido.telefono = form.cleaned_data['telefono']
            pedido.direccion = form.cleaned_data['direccion']
            pedido.ciudad = form.cleaned_data['ciudad']
            pedido.pais = form.cleaned_data['pais']
            pedido.observacion_pedido = form.cleaned_data['observacion_pedido']
            pedido.total_pedido = total_pagar
            pedido.impuesto = iva
            pedido.ip = request.META.get('REMOTE_ADDR')
            pedido.save()

            # Generar número de pedido: YYYYMMDD + ID
            hoy = datetime.date.today()
            current_date = hoy.strftime("%Y%m%d")
            numero_pedido = current_date + str(pedido.id)
            pedido.numero_pedido = numero_pedido
            pedido.save()

            # === CREAR PRODUCTOS DEL PEDIDO ===
            for carrito_item in carrito_items:
                # Obtener la variación (si existe) del Carrito_Item
                variacion = None
                if hasattr(carrito_item, 'variaciones') and carrito_item.variaciones.exists():
                    variacion = carrito_item.variaciones.first()  # ForeignKey → solo una

                # Crear el ProductoOrdenado
                ProductoOrdenado.objects.create(
                    pedido=pedido,
                    pago=None,  # Se asignará cuando PayPal confirme
                    user=current_user,
                    producto=carrito_item.producto,
                    variaciones=variacion,  # ✅ Asignación correcta para ForeignKey
                    cantidad=carrito_item.cantidad,
                    precio_producto=carrito_item.producto.precio,  # Precio unitario
                    ordenado=False,  # Se marcará True tras confirmación de pago
                )

            print(f"Creados {carrito_items.count()} productos para el pedido {numero_pedido}")

            # Configuración de PayPal
            host = request.get_host()
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': str(round(total_pagar, 2)),
                'item_name': f'Pedido {numero_pedido}',
                'invoice': str(uuid.uuid4()),
                'currency_code': 'USD',
                'notify_url': f'http://{host}{reverse("paypal-ipn")}',
                'return_url': f'http://{host}{reverse("pago_exitoso")}',
                'cancel_return': f'http://{host}{reverse("pago_cancelado")}',
                'custom': str(pedido.id),
                'no_shipping': 1,
                'no_note': 1,
            }

            paypal_form = PayPalPaymentsForm(initial=paypal_dict)

            # Recuperar el pedido recién creado
            try:
                pedido_reciente = Pedido.objects.get(numero_pedido=numero_pedido)
            except Pedido.DoesNotExist:
                messages.error(request, 'No se pudo recuperar el pedido.')
                return redirect('tienda')

            context = {
                'pedido': pedido_reciente,
                'carrito_items': carrito_items,
                'total': total,
                'cantidad': cantidad,
                'iva': iva,
                'total_pagar': total_pagar,
                'paypal_form': paypal_form,
            }

            return render(request, 'pedidos/pagos.html', context)

    # Si no es POST, redirige al formulario de pago
    return redirect('pagar')

@login_required
def pago_exitoso(request):
    """Vista para mostrar confirmación de pago exitoso"""
    
    # Debug: imprimir información
    print("=== DEBUG PAGO EXITOSO ===")
    print("Usuario:", request.user)
    print("GET params:", request.GET)
    
    # Buscar pedidos del usuario
    pedidos_ordenados = Pedido.objects.filter(user=request.user, esta_ordenado=True)
    pedidos_no_ordenados = Pedido.objects.filter(user=request.user, esta_ordenado=False)
    
    print("Pedidos ordenados:", pedidos_ordenados.count())
    print("Pedidos NO ordenados:", pedidos_no_ordenados.count())
    
    try:
        # Intentar primero con pedidos ordenados
        pedido = Pedido.objects.filter(user=request.user, esta_ordenado=True).latest('fecha_creacion')
        print("Encontrado pedido ordenado:", pedido.numero_pedido)
    except Pedido.DoesNotExist:
        try:
            # Si no hay pedidos ordenados, buscar el último pedido
            pedido = Pedido.objects.filter(user=request.user).latest('fecha_creacion')
            print("Encontrado último pedido (no ordenado):", pedido.numero_pedido)
            
            # TEMPORAL: Marcar como ordenado para que funcione
            pedido.esta_ordenado = True
            pedido.save()
            print("Pedido marcado como ordenado")
            
        except Pedido.DoesNotExist:
            print("No se encontró ningún pedido")
            messages.error(request, 'No se encontró información del pedido.')
            return redirect('tienda')
    
    # Obtener los productos del pedido
    productos_db = ProductoOrdenado.objects.filter(pedido=pedido)
    print("Productos encontrados:", productos_db.count())
    
    # === 🔧 AQUÍ VIENE EL CAMBIO: calcular subtotal para cada producto ===
    pedido_productos = []
    for item in productos_db:
        subtotal = item.precio_producto * item.cantidad
        pedido_productos.append({
            'producto': item.producto,
            'precio_producto': item.precio_producto,
            'cantidad': item.cantidad,
            'subtotal': subtotal,  # Ya calculado aquí
        })

    context = {
        'pedido': pedido,
        'pedido_productos': pedido_productos,  # Lista con subtotales precalculados
    }
    
    # Limpiar el carrito después del pago exitoso
    carrito_items = Carrito_Item.objects.filter(user=request.user)
    carrito_items.delete()
    print("Carrito limpiado")
    
    return render(request, 'pedidos/pago_exitoso.html', context)

@login_required
def pago_cancelado(request):
    """Vista para mostrar cancelación de pago"""
    # Obtener el último pedido no ordenado del usuario
    try:
        pedido = Pedido.objects.filter(user=request.user, esta_ordenado=False).latest('fecha_creacion')
        context = {
            'pedido': pedido,
        }
        return render(request, 'pedidos/pago_cancelado.html', context)
        
    except Pedido.DoesNotExist:
        return render(request, 'pedidos/pago_cancelado.html', {'pedido': None})

# ============= FUNCIONES DE PAYPAL IPN =============

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    """
    Función que se ejecuta cuando PayPal confirma un pago válido
    """
    ipn_obj = sender
    
    print("=== PAYPAL PAYMENT RECEIVED ===")
    print("Payment status:", ipn_obj.payment_status)
    print("Custom field:", ipn_obj.custom)
    print("Amount:", ipn_obj.mc_gross)
    
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # El pago fue completado exitosamente
        try:
            # Obtener el ID del pedido desde el campo custom
            pedido_id = int(ipn_obj.custom)
            pedido = Pedido.objects.get(id=pedido_id)
            
            print(f"Procesando pedido: {pedido.numero_pedido}")
            
            # Crear registro de pago
            pago = Pago.objects.create(
                user=pedido.user,
                id_pago=ipn_obj.txn_id,
                metodo_pago='PayPal',
                monto_pagado=str(ipn_obj.mc_gross),
                estado='Completado'
            )
            
            # Actualizar el pedido
            pedido.pago = pago
            pedido.esta_ordenado = True
            pedido.estado = 'Procesando'
            pedido.save()
            
            # Crear los ProductoOrdenado desde el carrito
            carrito_items = Carrito_Item.objects.filter(user=pedido.user)
            for item in carrito_items:
                ProductoOrdenado.objects.create(
                    pedido=pedido,
                    pago=pago,
                    user=pedido.user,
                    producto=item.producto,
                    variaciones=getattr(item, 'variaciones', None),
                    cantidad=item.cantidad,
                    precio_producto=item.producto.precio,
                    ordenado=True
                )
            
            print(f"Pedido {pedido.numero_pedido} procesado exitosamente")
            
        except Pedido.DoesNotExist:
            print(f"No se encontró el pedido con ID: {ipn_obj.custom}")
        except Exception as e:
            print(f"Error procesando el pago: {e}")
    else:
        print(f"Pago no completado. Estado: {ipn_obj.payment_status}")

@receiver(invalid_ipn_received)
def paypal_payment_failed(sender, **kwargs):
    """
    Función que se ejecuta cuando PayPal envía una notificación inválida
    """
    print("=== PAYPAL PAYMENT FAILED ===")
    print("Invalid IPN received")

# Vista alternativa para casos donde no funcionen las señales
@csrf_exempt
def paypal_return(request):
    """
    Vista que maneja el retorno desde PayPal (sin esperar IPN)
    """
    print("=== PAYPAL RETURN ===")
    print("GET params:", request.GET)
    
    # Obtener parámetros de PayPal
    payment_status = request.GET.get('st', '')  # Success/Fail
    tx = request.GET.get('tx', '')  # Transaction ID
    
    if payment_status.lower() == 'completed' or payment_status.lower() == 'success':
        # Intentar procesar el último pedido del usuario
        try:
            pedido = Pedido.objects.filter(user=request.user, esta_ordenado=False).latest('fecha_creacion')
            
            # Marcar como pagado (método simplificado)
            pedido.esta_ordenado = True
            pedido.estado = 'Procesando'
            
            # Crear un pago básico si no existe
            if not pedido.pago:
                pago = Pago.objects.create(
                    user=pedido.user,
                    id_pago=tx or f"paypal_{pedido.id}",
                    metodo_pago='PayPal',
                    monto_pagado=str(pedido.total_pedido),
                    estado='Completado'
                )
                pedido.pago = pago
            
            pedido.save()
            
            # Crear ProductoOrdenado desde el carrito
            carrito_items = Carrito_Item.objects.filter(user=request.user)
            for item in carrito_items:
                ProductoOrdenado.objects.create(
                    pedido=pedido,
                    pago=pedido.pago,
                    user=pedido.user,
                    producto=item.producto,
                    variaciones=getattr(item, 'variaciones', None),
                    cantidad=item.cantidad,
                    precio_producto=item.producto.precio,
                    ordenado=True
                )
            
            print("Pedido procesado exitosamente desde paypal_return")
            return redirect('pago_exitoso')
            
        except Pedido.DoesNotExist:
            messages.error(request, 'No se encontró el pedido.')
            return redirect('tienda')
        except Exception as e:
            print(f"Error en paypal_return: {e}")
            messages.error(request, 'Error procesando el pago.')
            return redirect('pago_cancelado')
    
    else:
        print("Pago no completado o cancelado")
        return redirect('pago_cancelado')
    
