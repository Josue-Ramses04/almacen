from django.urls import path
from django.shortcuts import redirect
from django.conf.urls import handler404
from . import views
from .views import custom_admin_redirect, error403, error_404, error_502, error_505, toggle_favorite, favorite_products
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('signin/', views.signin, name='signin'),
     
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
 
    path('admin/', custom_admin_redirect, name='admin'),
    path('profile/', views.profile, name='profile'),
    
    path('product/', views.product_list, name='product'),
    
    
    path('manage_product/', views.manage_product, name='manage_product'),
    
    
    path('error403/', error403, name='error403'),
    path('error_404/', error_404, name='error_404'),
    path('error502/', error_502, name='error_502'),
    path('error505/', error_505, name='error_505'),
    
#CRUD PRODUCTS
    path('create-product/', views.create_product, name='create_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),

    path('', views.product_details, name='index'),
    
    path('toggle-favorite/<int:product_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorite_products, name='favorite_products'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler404 = 'account.error_404'
handler403 = 'account.error_403'
handler502 = 'account.views.error_502'
handler403 = 'account.error_505'



