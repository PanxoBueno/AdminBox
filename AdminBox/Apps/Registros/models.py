from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class Usuario(models.Model):
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
class Entrenador(models.Model):
    run = models.CharField(max_length=12, primary_key=True, verbose_name="RUN")
    correo = models.EmailField(max_length=50, unique=True)
    clave = models.CharField(max_length=255)  # Se almacenará encriptada
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=Usuario.GENERO_CHOICES, null=True, blank=True)
    altura = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    telefono = models.CharField(max_length=15)
    #id_gimnasio = models.ForeignKey('gimnasio', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
