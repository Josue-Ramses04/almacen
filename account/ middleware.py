from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from datetime import timedelta
class RequireLoginMiddleware:
    
    
    
    """ Middleware que redirige a los usuarios no autenticados a /signin/ y a usuarios no admins a / """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs públicas que no requieren autenticación
        allowed_urls = ['/signin/', '/signup/', '/admin/']  # Asegúrate de permitir el login de admin

        # Si el usuario NO está autenticado y NO está en una URL permitida, lo redirige a /signin/
        if not request.user.is_authenticated and request.path not in allowed_urls:
            return redirect('/signin/')
        
        # Si el usuario no es admin (normal), y está intentando acceder a /admin/, lo redirige a la ruta raíz
        if request.user.is_authenticated and not request.user.is_staff and request.path.startswith('/admin'):
            return redirect('/')  # Redirige a la ruta raíz si el usuario no es admin

        # Si el usuario es admin o está en un path permitido, no redirigimos
        return self.get_response(request)
 



class LimitUserCreationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificamos si la solicitud es para crear un usuario
        if request.path.startswith('/signup/') and request.method == 'POST':
            ip_address = self.get_ip(request)
            key = f'user_creation_{ip_address}'
            attempts = cache.get(key, 0)

            # Limitar la cantidad de registros (por ejemplo, 3 usuarios por IP en 24 horas)
            if attempts >= 3:
                return HttpResponseForbidden("Se ha alcanzado el límite de registros desde esta IP.")

            # Si aún no se alcanza el límite, aumentamos el contador
            cache.set(key, attempts + 1, timeout=86400)  # 24 horas en segundos

        response = self.get_response(request)
        return response

    def get_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip