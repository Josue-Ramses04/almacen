from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(email, code):
    """Envía un email con el código de verificación"""
    subject = "Verifica tu email"
    message = f"Tu código de verificación es: {code}. Introduce este código en el formulario para continuar con tu registro."
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
