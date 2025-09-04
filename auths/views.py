from django.shortcuts import render,redirect
from .forms import FormularioRegistro
from .models import Auth
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.http import HttpResponse
from carrito.views import _id_carrito as _carrito_id
from carrito.models import Carrito, Carrito_Item
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.



def registro(request):
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)

        if formulario.is_valid():
            nombre = formulario.cleaned_data['nombre']
            apellido = formulario.cleaned_data['apellido']
            email = formulario.cleaned_data['email']
            telefono = formulario.cleaned_data['telefono']
            password = formulario.cleaned_data['password']
            username = email.split("@")[0]

            user = Auth.objects.create_user(
                nombre=nombre, apellido=apellido, email=email,
                username=username, password=password
            )
            user.telefono = telefono
            user.save()

            # Activación de Usuario con correo en HTML
            sitio_actual = get_current_site(request)
            mensaje_html = render_to_string('cuentas/verificacion_cuenta_email.html', {
                'user': user,
                'domain': sitio_actual,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            asunto = 'Activa tu cuenta en Codelatin'
            mensaje_texto = strip_tags(mensaje_html)

            email_envio = EmailMultiAlternatives(
                subject=asunto,
                body=mensaje_texto,
                to=[email]
            )
            email_envio.attach_alternative(mensaje_html, "text/html")
            email_envio.send()

            return redirect('/auths/login/?command=verification&email=' + email)

    else:
        formulario = FormularioRegistro()

    context = {
        'formulario': formulario
    }
    return render(request, 'cuentas/registro.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                carrito = Carrito.objects.get(id_carrito=_carrito_id(request))
                existe_carrito_item = Carrito_Item.objects.filter(carrito=carrito).exists()
                print(f'Carrito encontrado: {carrito.id} - {carrito.id_carrito}')
                if existe_carrito_item.exists():
                    carrito_items = Carrito_Item.objects.filter(carrito=carrito)
                    variacion_producto = []
                    for item in carrito_items:
                        variacion = item.variaciones.all()
                        variacion_producto.append(list( variacion))
                
           

                # Buscar items del carrito
                carrito_items_sin_usuario = Carrito_Item.objects.filter(user=user)
                listaex_variacion_producto = []
                id = []
                for item in carrito_items:
                    existe_variacion = item.variaciones.all()
                    listaex_variacion_producto.append(list(existe_variacion))
                    id.append(item.id)
                
                for product in variacion_producto:
                    if product in listaex_variacion_producto:
                        index = listaex_variacion_producto.index(product)
                        item_id = id[index]
                        item = Carrito_Item.objects.get(id=item_id)
                        item.cantidad += 1
                        item.save()
                    else:
                        print('=== ASIGNANDO USUARIO A LOS ITEMS ===')
                        for item in carrito_items:
                          
                            item.user = user
                            item.save()
                            
                       
                    
                
                if carrito_items_sin_usuario.exists():
                    print('=== ASIGNANDO USUARIO A LOS ITEMS ===')
                    for item in carrito_items_sin_usuario:
                        print(f'Procesando item ID: {item.id} - Producto: {item.producto}')
                        print(f'Usuario antes: {item.user}')
                        item.user = user
                        item.save()
                        print(f'Usuario después: {item.user}')
                        print('---')
                    
                    print(f'✅ Se asignaron {carrito_items_sin_usuario.count()} items al usuario {user.email}')
                else:
                    print('❌ No se encontraron items sin usuario para asignar')
                    
                # Verificación final
                items_con_usuario = Carrito_Item.objects.filter(carrito=carrito, user=user)
                print(f'✅ Items finales con usuario {user.email}: {items_con_usuario.count()}')
                
            except Carrito.DoesNotExist:
                print('❌ No se encontró el carrito en la base de datos')
            except Exception as e:
                print(f'❌ Error inesperado: {str(e)}')
                import traceback
                print(traceback.format_exc()) #vamos Excelente con Este Proyecto!
                
            auth.login(request, user)
            messages.success(request, 'Te has logeado Perfectamente!')
            return redirect('dashboard_usuario')
        else:
            messages.error(request,'Email o contraseña Incorrectos')
            return redirect('login')
    return render(request, 'cuentas/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has salido con Exito!')
    return render(request, 'cuentas/login.html')


def activar_cuenta(request, uidb64, token):
    try:
        uid= urlsafe_base64_decode(uidb64).decode()
        user=Auth._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Auth.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, 'Felicitaciones Tu Cuenta Ha sido Activada!')
        return redirect('login')
    else:
        messages.error(request, 'Ups no se ha podido Validar la cuenta')
        return redirect('registro')



def dashboard_usuario(request):
    return render(request, 'cuentas/dashboard_usuario.html')

def olvidar_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Auth.objects.filter(email=email).exists():
            user = Auth.objects.get(email__exact=email)

            # Recuperación de contraseña con correo en HTML
            sitio_actual = get_current_site(request)
            mensaje_html = render_to_string('cuentas/recuperar_password_email.html', {
                'user': user,
                'domain': sitio_actual,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            asunto = 'Recupera tu contraseña en Codelatin'
            mensaje_texto = strip_tags(mensaje_html)

            email_envio = EmailMultiAlternatives(
                subject=asunto,
                body=mensaje_texto,
                to=[email]
            )
            email_envio.attach_alternative(mensaje_html, "text/html")
            email_envio.send()

            messages.success(request, 'Se ha enviado un enlace para recuperar tu contraseña a tu email.')
            return redirect('login')
        else:
            messages.error(request, 'Ups, este email no existe.')
            return redirect('olvidar_password')

    return render(request, 'cuentas/olvidar_password.html')


''' 

def validar_cuenta_recuperada(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Auth.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Auth.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid  # Guardar UID en sesión
        messages.success(request, 'Por favor, recupera tu contraseña.')
        return redirect('recuperar_password')
    else:
        messages.error(request, 'Ups, el enlace de recuperación ha expirado.')
        return redirect('login')
    




def recuperar_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirmar_password = request.POST['confirmar_password']

        if password == confirmar_password:
            uid = request.session.get('uid')
            user = Auth.objects.get(pk=uid)  # Buscar al usuario con el UID correcto
            user.set_password(password)  # Cambiar la contraseña
            user.save()
            messages.success(request, 'Has cambiado la contraseña correctamente!')
            return redirect('login')
        else:
            messages.error(request, 'Oh no, las contraseñas no coinciden!')
            return redirect('recuperar_password')
    else:
            return render(request, 'cuentas/recuperar_password.html')

            
'''

def validar_cuenta_recuperada(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Auth.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Auth.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid  # Aquí se guarda el UID decodificado
        messages.success(request, 'Por favor, recupera tu contraseña.')
        return redirect('recuperar_password')
    else:
        messages.error(request, 'Ups, el enlace de recuperación ha expirado.')
        return redirect('login')





            

         
        

def recuperar_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirmar_password = request.POST['confirmar_password']

        if password == confirmar_password:
            uid = request.session.get('uid')
            if not uid:
                messages.error(request, "Error: No se encontró el usuario en la sesión.")
                return redirect('recuperar_password')  # Redirige al formulario para solicitar de nuevo

            try:
                user = Auth.objects.get(pk=uid)
            except Auth.DoesNotExist:
                messages.error(request, "Error: Usuario no encontrado. Por favor, solicita un nuevo enlace de recuperación.")
                return redirect('recuperar_password')

            user.set_password(password)
            user.save()

            # Elimina el UID de la sesión
            if 'uid' in request.session:
                del request.session['uid']

            messages.success(request, 'Has cambiado la contraseña correctamente!')
            return redirect('login')
        else:
            messages.error(request, 'Oh no, las contraseñas no coinciden!')
            return redirect('recuperar_password')
    else:
        return render(request, 'cuentas/recuperar_password.html')
