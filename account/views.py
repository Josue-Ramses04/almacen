from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.utils.timezone import now
import datetime
from .models import Product, Category, Branch, Favorite, RegistrationAttempt
from .forms import ProductForm
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
# Login view
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from django.core.validators import validate_email
from .models import EmailVerification
from .utils import send_verification_email


def request_email_verification(request):
    """
    Captura el email y envía un código de verificación.
    """
    if request.method == "POST":
        email = request.POST.get("email").strip().lower()

        # Generar código y guardarlo en la BD
        code = EmailVerification.generate_code()
        EmailVerification.objects.update_or_create(email=email, defaults={"code": code})
        send_verification_email(email, code)

        request.session["pending_email"] = email  # Guardar email en sesión
        return redirect("verify_email_code")

    return render(request, "request_email_verification.html")




def verify_email_code(request):
    """
    Verifica el código de verificación y permite continuar con el registro.
    """
    pending_email = request.session.get("pending_email")
    if not pending_email:
        return redirect("request_email_verification")

    if request.method == "POST":
        code = request.POST.get("code")

        verification = EmailVerification.objects.filter(email=pending_email, code=code).first()

        if verification:
            request.session["verified_email"] = pending_email  # Guardar email verificado en sesión
            verification.delete()  # Eliminar el registro temporal
            return redirect("signup_form")

        messages.error(request, "Código incorrecto.")

    return render(request, "verify_email_code.html")















# Función que verifica si el usuario es admin o staff
def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_staff  

# Vista para redirigir solo a usuarios con permisos a /admin/
@user_passes_test(is_admin, login_url='/error403/')  
def custom_admin_redirect(request):
    return redirect('/admin/') #django-admin





def signin(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')  # Redirige a Django Admin si es administrador
        return redirect('/')  # Redirige a home si es usuario normal

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.filter(email=email).first()

            if user:
                # 🔹 Bloqueo manual: Verificar si el usuario está activo
                if not user.is_active:
                    messages.error(request, "Tu cuenta ha sido bloqueada por un administrador.")
                    return redirect('signin')

                user = authenticate(request, username=user.username, password=password)

                if user:
                    login(request, user)
                    return redirect('/admin/' if user.is_staff else "/")
                else:
                    messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")

        except Exception as e:
            messages.error(request, "Ocurrió un error. Intenta nuevamente.")
            print(f"Error de autenticación: {e}")

    return render(request, "signin.html")



# Vista de registro

def get_client_ip(request):
    """ Obtiene la dirección IP del usuario """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import password_validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import EmailVerification
from .utils import send_verification_email

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')

    # Recuperar datos previos si existen
    saved_data = request.session.get("signup_data", {})

    if request.method == 'POST':
        username = request.POST.get('username', saved_data.get('username', '')).strip()
        email = request.POST.get('email', saved_data.get('email', '')).strip()
        password = request.POST.get('password', saved_data.get('password', ''))
        confirm_password = request.POST.get('confirm_password', saved_data.get('confirm_password', ''))
        verification_code = request.POST.get('verification_code', '').strip()

        # Si el usuario ingresó el código de verificación
        if verification_code:
            try:
                email_verification = EmailVerification.objects.get(email=email, code=verification_code)

                # Validar la seguridad de la contraseña antes de crear el usuario
                password_validation.validate_password(email_verification.password)

                # Crear el usuario con los datos almacenados
                user = User.objects.create_user(
                    username=email_verification.username,
                    email=email_verification.email,
                    password=email_verification.password
                )

                # Agregar al grupo 'User'
                user_group, _ = Group.objects.get_or_create(name='User')
                user.groups.add(user_group)

                email_verification.delete()  # Eliminar el registro temporal
                request.session.pop("signup_data", None)  # Eliminar sesión

                messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
                return redirect('signin')

            except EmailVerification.DoesNotExist:
                messages.error(request, "Código incorrecto.")
                return redirect('signup')

        # Si no hay código, significa que es la primera vez que se ingresa el email
        if not email:
            messages.error(request, "El email es obligatorio.")
            return redirect('signup')

        if not username:
            messages.error(request, "El nombre de usuario es obligatorio.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('signup')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email inválido.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El email ya está registrado.")
            return redirect('signup')

        # Guardar datos en sesión para que no se pierdan
        request.session["signup_data"] = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }

        # Generar código de verificación y guardarlo en la BD
        verification_code = EmailVerification.generate_code()
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={"code": verification_code, "username": username, "password": password}
        )

        send_verification_email(email, verification_code)

        messages.success(request, "Te enviamos un código de verificación a tu correo.")
        return redirect('signup')

    return render(request, 'signup.html', {"signup_data": saved_data})




# logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('signin') 

# Index
@login_required
def index(request):
    return render(request, 'index.html')


@user_passes_test(is_admin)
def card(request):
    return render(request, 'sidebar.html')


@user_passes_test(is_admin)
def mode(request):
    return render(request, 'mode.html')



# Vista para mostrar un mensaje de acceso denegado
def access_denied(request):
    #messages.error(request, "Acceso denegado. Solo administradores pueden acceder.")
    return redirect('/')  # Redirige al usuario a la página principal



#errores


def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_502(request):
    return render(request, '502.html', status=502)

def error_505(request):
    return render(request, '505.html', status=505)

#Error 403
def error403(request):
    return render(request, "403.html", status=403)
        






@login_required
def profile(request):
    return render(request, 'profile.html')




@login_required
def manage_product(request):
    products = Product.objects.filter(user=request.user)  
    categories = Category.objects.all()  
    branches = Branch.objects.all()  
    return render(request, 'manage_product.html', {'products': products, 'categories': categories, 'branches': branches})




@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product.html' , {'products': products})





@login_required
def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        branch_id = request.POST.get('branch')  
        img = request.FILES.get('img')
        
      
        category = Category.objects.get(id=category_id)
        branch = Branch.objects.get(id=branch_id)  
        
        # Crea Nuevos Productos
        new_product = Product.objects.create(
            name=name,
            category=category,
            stock=stock,
            price=price,
            user=request.user,
            branch=branch,  #Sucursal asociada al producto
            img =img
        )
        
        return redirect('manage_product')
    else:
        categories = Category.objects.all()
        branches = Branch.objects.all()  # Retrieve all branches
        return render(request, 'product.html', {'categories': categories, 'branches': branches})




@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)  # Ensure the product belongs to the user

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Include request.FILES to handle file uploads
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('manage_product') 
    else:
        form = ProductForm(instance=product)  

    categories = Category.objects.all()
    branches = Branch.objects.all()

    return render(request, 'account/edit_product.html', {
        'form': form,
        'categories': categories,
        'product': product,
        'branches': branches
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)  # Ensure the product belongs to the user
    if request.method == 'POST':
        product.delete()
       #messages.success(request, 'Product deleted successfully.')
        return redirect('manage_product')  # Ensure it redirects to manage_product
    return redirect('manage_product')  # Redirect to manage_product if not POST


 
 
 
 
 
@login_required 
def product_details(request):
    products = Product.objects.all()
    return render(request, 'product_details.html', {'products': products})



@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})




@login_required
def favorite_products(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    products = [favorite.product for favorite in favorites]
    return render(request, 'favorite_products.html', {'products': products})



