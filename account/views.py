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
from django.core.cache import cache




# Función que verifica si el usuario es admin o staff
def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_staff  

# Vista para redirigir solo a usuarios con permisos a /admin/
@user_passes_test(is_admin, login_url='/error403/')  
def custom_admin_redirect(request):
    return redirect('/admin/') #django-admin


@ratelimit(key='ip', rate='5/m') 
def signin(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  
            return redirect('/admin/')
        return redirect('/')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 🔹 Cachear la consulta del usuario por email
        cache_key = f"user_email_{email}"
        user = cache.get(cache_key)

        if not user:
            user = User.objects.filter(email=email).first()
            cache.set(cache_key, user, timeout=300)  # Guarda en caché por 5 minutos

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                return redirect('/admin/' if user.is_staff else "/")

        messages.error(request, "Incorrect username or password.")
    
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


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Capturar información del usuario
        user_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 🔹 Cachear intentos de registro por IP para evitar consultas repetitivas
        cache_key = f"registration_attempts_{user_ip}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 3:
            messages.error(request, "Too many registration attempts. Please try again later.")
            return redirect('signup')

        # Validaciones
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('signup')

        # Validación de contraseña
        try:
            password_validation.validate_password(password)

            # Crear usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            user_group, _ = Group.objects.get_or_create(name='User')
            user.groups.add(user_group)

            # Registrar intento exitoso y resetear intentos en Redis
            cache.delete(cache_key)

            messages.success(request, 'Registration successful.')
            return redirect('signin')

        except ValidationError as e:
            messages.error(request, str(e))
        
        # 🔹 Incrementar intentos en Redis
        cache.set(cache_key, attempts + 1, timeout=3600)  # Expira en 1 hora

    return render(request, 'signup.html')




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
    cache_key = "product_list_cache"
    products = cache.get(cache_key)

    if not products:
        products = list(Product.objects.all())  # Convierte a lista para evitar problemas con QuerySet
        cache.set(cache_key, products, timeout=600)  # Cachear por 10 minutos

    return render(request, 'product.html', {'products': products})




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

        Product.objects.create(
            name=name,
            category=category,
            stock=stock,
            price=price,
            user=request.user,
            branch=branch,
            img=img
        )

        cache.delete("categories_cache")  # Limpiar caché cuando se crea un nuevo producto
        cache.delete("branches_cache")  

        return redirect('manage_product')

    else:
        # Cachear categorías y sucursales
        categories = cache.get("categories_cache")
        branches = cache.get("branches_cache")

        if not categories:
            categories = list(Category.objects.all())
            cache.set("categories_cache", categories, timeout=3600)  # Cachear por 1 hora
        
        if not branches:
            branches = list(Branch.objects.all())
            cache.set("branches_cache", branches, timeout=3600)  

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



