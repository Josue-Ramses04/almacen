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





# Función que verifica si el usuario es admin o staff
def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_staff  

# Vista para redirigir solo a usuarios con permisos a /admin/
@user_passes_test(is_admin, login_url='/error403/')  
def custom_admin_redirect(request):
    return redirect('/admin/') #django-admin


# Login view

def signin(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  
            return redirect('/admin/')  # Django-admin
        else:
            return redirect('/')  

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            user = User.objects.filter(email=email).first()
            if user:
                user = authenticate(request, username=user.username, password=password)
                if user:
                    login(request, user)
                    if user.is_staff:  
                        return redirect('/admin/')
                    else:  
                        return redirect("/")  
                else:
                    messages.error(request, "Incorrect username or password.")
            else:
                messages.error(request, "Incorrect username or password.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            print(f"Authentication error: {e}")

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

        # Capture user information
        user_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Define the time threshold (example: 1 hour)
        time_threshold = now() - datetime.timedelta(hours=1)

        # Count recent attempts from the same IP
        recent_attempts = RegistrationAttempt.objects.filter(ip_address=user_ip, timestamp__gte=time_threshold)

        # Limit the number of registration attempts per IP
        if recent_attempts.count() >= 3:
            messages.error(request, "Too many registration attempts. Please try again later.")
            return redirect('signup')

        # Check if the administrator has blocked registration
        if RegistrationAttempt.objects.filter(ip_address=user_ip, is_allowed=False).exists():
            messages.error(request, "Registration from this device has been blocked by an administrator.")
            return redirect('signup')

        # Basic validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('signup')

        # Password validation
        try:
            password_validation.validate_password(password)  # Validate password security

            # Create the user if everything is fine
            user = User.objects.create_user(username=username, email=email, password=password)
            user_group, _ = Group.objects.get_or_create(name='User')
            user.groups.add(user_group)

            # Register the successful registration attempt
            RegistrationAttempt.objects.create(user=user, ip_address=user_ip, user_agent=user_agent)

            messages.success(request, 'Registration successful.')
            return redirect('signin')

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)  # Show validation errors
            return redirect('signup')

        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            print(f"Error: {e}")

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



