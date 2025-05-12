from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def enviar_email_bienvenida(alumno_email, alumno_nombre, plan, nivel):
    subject = f"Hola {alumno_nombre}, se ha registrado tu contratación al gimnasio de CrossFit"
    
    # Renderizar template HTML
    html_content = render_to_string('bienvenida_alumno.html', {
        'alumno_nombre': alumno_nombre,
        'plan': plan,
        'nivel': nivel,
    })
    
    # Crear versión de texto plano
    text_content = strip_tags(html_content)
    
    # Configurar el email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[alumno_email],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Enviar email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False