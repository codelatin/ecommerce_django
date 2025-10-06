from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
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


# Create your views here.    
@login_required
def pagos(request):
    """
    Vista opcional: muestra el formulario de PayPal para el último pedido no pagado.
    """
    try:
        pedido = Pedido.objects.filter(user=request.user, esta_ordenado=False).latest('fecha_creacion')
        carrito_items = Carrito_Item.objects.filter(user=request.user)
        
        if not carrito_items.exists():
            messages.warning(request, 'Tu carrito está vacío.')
            return redirect('tienda')

        total = sum(item.producto.precio * item.cantidad for item in carrito_items)
        iva = total * 0.02
        total_pagar = total + iva

        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(round(total_pagar, 2)),
            'item_name': f'Pedido {pedido.numero_pedido}',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("pago_exitoso")}',
            'cancel_return': f'http://{host}{reverse("pago_cancelado")}',
            'custom': str(pedido.id),
            'no_shipping': 1,
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        context = {
            'pedido': pedido,
            'carrito_items': carrito_items,
            'total': total,
            'iva': iva,
            'total_pagar': total_pagar,
            'paypal_form': paypal_form,
        }
        return render(request, 'pedidos/pagos.html', context)
    except Pedido.DoesNotExist:
        messages.error(request, 'No hay un pedido pendiente.')
        return redirect('tienda')


@login_required
def realizar_pedido(request):
    current_user = request.user
    carrito_items = Carrito_Item.objects.filter(user=current_user).select_related('producto')

    if not carrito_items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('tienda')

    # Calcular totales
    total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    cantidad = sum(item.cantidad for item in carrito_items)
    iva = total * 0.02
    total_pagar = total + iva

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # Crear el pedido
            pedido = Pedido.objects.create(
                user=current_user,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                telefono=form.cleaned_data['telefono'],
                direccion=form.cleaned_data['direccion'],
                ciudad=form.cleaned_data['ciudad'],
                pais=form.cleaned_data['pais'],
                observacion_pedido=form.cleaned_data['observacion_pedido'],
                total_pedido=total_pagar,
                impuesto=iva,
                ip=request.META.get('REMOTE_ADDR'),
                esta_ordenado=False,
                estado='Pendiente'
            )

            # Generar número de pedido
            hoy = datetime.date.today().strftime("%Y%m%d")
            pedido.numero_pedido = f"{hoy}{pedido.id}"
            pedido.save()

            # === CREAR PRODUCTOS DEL PEDIDO (CORREGIDO PARA ManyToMany) ===
            for carrito_item in carrito_items:
                # Crear el ProductoOrdenado SIN variaciones primero
                producto_ordenado = ProductoOrdenado.objects.create(
                    pedido=pedido,
                    pago=None,
                    user=current_user,
                    producto=carrito_item.producto,
                    cantidad=carrito_item.cantidad,
                    precio_producto=carrito_item.producto.precio,
                    ordenado=False
                )
                # Asignar variaciones si existen (usando .set())
                if carrito_item.variaciones.exists():
                    producto_ordenado.variaciones.set(carrito_item.variaciones.all())

            print(f"Creados {carrito_items.count()} productos para el pedido {pedido.numero_pedido}")

            # Configuración de PayPal
            host = request.get_host()
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': str(round(total_pagar, 2)),
                'item_name': f'Pedido {pedido.numero_pedido}',
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

            context = {
                'pedido': pedido,
                'carrito_items': carrito_items,
                'total': total,
                'cantidad': cantidad,
                'iva': iva,
                'total_pagar': total_pagar,
                'paypal_form': paypal_form,
            }

            return render(request, 'pedidos/pagos.html', context)

    else:
        form = PedidoForm()

    context = {
        'form': form,
        'total': total,
        'cantidad': cantidad,
        'iva': iva,
        'total_pagar': total_pagar,
    }
    return render(request, 'pedidos/realizar_pedido.html', context)


@login_required
def pago_exitoso(request):
    try:
        pedido = Pedido.objects.filter(user=request.user, esta_ordenado=True).latest('fecha_creacion')
    except Pedido.DoesNotExist:
        messages.error(request, 'No se encontró un pedido confirmado.')
        return redirect('tienda')

    productos_db = ProductoOrdenado.objects.filter(pedido=pedido)
    pedido_productos = []
    for item in productos_db:
        subtotal = item.precio_producto * item.cantidad
        pedido_productos.append({
            'producto': item.producto,
            'precio_producto': item.precio_producto,
            'cantidad': item.cantidad,
            'subtotal': subtotal,
        })

    context = {
        'pedido': pedido,
        'pedido_productos': pedido_productos,
    }
    return render(request, 'pedidos/pago_exitoso.html', context)


@login_required
def pago_cancelado(request):
    try:
        pedido = Pedido.objects.filter(user=request.user, esta_ordenado=False).latest('fecha_creacion')
        context = {'pedido': pedido}
        return render(request, 'pedidos/pago_cancelado.html', context)
    except Pedido.DoesNotExist:
        return render(request, 'pedidos/pago_cancelado.html', {'pedido': None})


# ============= FUNCIONES DE PAYPAL IPN =============
@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            pedido_id = int(ipn_obj.custom)
            pedido = Pedido.objects.get(id=pedido_id, esta_ordenado=False)

            pago = Pago.objects.create(
                user=pedido.user,
                id_pago=ipn_obj.txn_id,
                metodo_pago='PayPal',
                monto_pagado=str(ipn_obj.mc_gross),
                estado='Completado'
            )

            pedido.pago = pago
            pedido.esta_ordenado = True
            pedido.estado = 'Procesando'
            pedido.save()

            # Actualizar productos existentes (NO crear nuevos)
            ProductoOrdenado.objects.filter(pedido=pedido).update(
                pago=pago,
                ordenado=True
            )

            # Limpiar carrito
            Carrito_Item.objects.filter(user=pedido.user).delete()

            print(f"✅ Pago confirmado para pedido {pedido.numero_pedido}")

        except Pedido.DoesNotExist:
            print(f"⚠️ Pedido no encontrado o ya procesado: {ipn_obj.custom}")
        except Exception as e:
            print(f"❌ Error en IPN: {e}")
    else:
        print(f"⚠️ Pago no completado: {ipn_obj.payment_status}")


@receiver(invalid_ipn_received)
def paypal_payment_failed(sender, **kwargs):
    print("=== PAYPAL PAYMENT FAILED ===")
    print("Invalid IPN received")


# Vista alternativa para casos donde no funcionen las señales
@csrf_exempt
def paypal_return(request):
    print("=== PAYPAL RETURN ===")
    payment_status = request.GET.get('st', '').lower()
    tx = request.GET.get('tx', '')

    if payment_status in ['completed', 'success']:
        try:
            pedido = Pedido.objects.filter(user=request.user, esta_ordenado=False).latest('fecha_creacion')
            
            if not pedido.pago:
                pago = Pago.objects.create(
                    user=pedido.user,
                    id_pago=tx or f"paypal_{pedido.id}",
                    metodo_pago='PayPal',
                    monto_pagado=str(pedido.total_pedido),
                    estado='Completado'
                )
                pedido.pago = pago
                pedido.esta_ordenado = True
                pedido.estado = 'Procesando'
                pedido.save()

                # ✅ SOLO ACTUALIZAR, NO CREAR NUEVOS
                ProductoOrdenado.objects.filter(pedido=pedido).update(
                    pago=pago,
                    ordenado=True
                )

                # Limpiar carrito
                Carrito_Item.objects.filter(user=request.user).delete()

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