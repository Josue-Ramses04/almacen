from django.shortcuts import redirect

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