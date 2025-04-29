from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('admin', 'Administrador'),
        ('entrenador', 'Entrenador'),
        ('atleta', 'Atleta'),
    )
    
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO, default='atleta')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    # Relaciones opcionales con los modelos existentes
    atleta_profile = models.OneToOneField(
        'Atleta', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuario'
    )
    entrenador_profile = models.OneToOneField(
        'Entrenador', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuario'
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="gymapp_users",
        related_query_name="gymapp_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="gymapp_users",
        related_query_name="gymapp_user",
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"

class Categoria(models.Model):
    Categoria_esp =(
        ('halterofilia', 'Halterofilia'),
        ('gimnasio', 'Gimnasio'),
        ('metcon', 'Metcon'),
        ('crossfit', 'CrossFit'),
    )
    Planes = [
    [0, "8 Clases"],
    [1, "12 Clases"],
    [2, "16 Clases"],
    [3, "Open Box"],
    [4, "Full Clases"],
    ]
    Nivel = (
        ('amateur', 'Amateur'),
        ('rookie', 'Rookie'),
        ('scaled', 'Scaled'),
        ('rx', 'Rx'),
        ('elite', 'Elite'),
    )

class Atleta(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    nivel = models.CharField(max_length=20, choices=Categoria.Nivel)
    email = models.EmailField(max_length=100)
    plan = models.IntegerField(choices=Categoria.Planes)

    def __str__(self):
        return f"{self.nombre} {self.apellido} "

class Entrenador(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=20)
    especialidad = models.CharField(max_length=20, choices=Categoria.Categoria_esp)

    def __str__(self):
        return self.nombre

class Biblioteca(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to="ejercicios", null=True)

    def __str__(self):
        return self.nombre
    
#aca agrego funcionalidad de reservas
class Clase(models.Model):
    HORARIOS = [
        ('06:00', '06:00 AM'),
        ('07:00', '07:00 AM'),
        ('08:00', '08:00 AM'),
        ('17:00', '05:00 PM'),
        ('18:00', '06:00 PM'),
        ('19:00', '07:00 PM'),
    ]
    
    nombre = models.CharField(max_length=50)
    horario = models.CharField(max_length=5, choices=HORARIOS)
    fecha = models.DateField()
    entrenador = models.ForeignKey(Entrenador, on_delete=models.SET_NULL, null=True)
    capacidad_maxima = models.PositiveIntegerField(default=15)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_horario_display()} - {self.fecha}"

class Reserva(models.Model):
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('atleta', 'clase')  # Evita reservas duplicadas
    
    def __str__(self):
        return f"{self.atleta} - {self.clase}"
    
class MarcaPersonal(models.Model):
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name='marcas_personales')
    ejercicio_id = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, verbose_name="Ejercicio")
    peso_lb = models.DecimalField(max_digits=6, decimal_places=2)
    fecha = models.DateField()
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Marcas Personales"
    
    # Actualizar este método para que devuelva el nombre del ejercicio desde Biblioteca
    @property
    def ejercicio(self):
        return self.ejercicio_id.nombre if self.ejercicio_id else "Desconocido"
    
    def get_nombre_ejercicio(self):
        return self.ejercicio_id.nombre if self.ejercicio_id else "Desconocido"
    
    def __str__(self):
        return f"{self.atleta}: {self.ejercicio_id} - {self.peso_lb} LB ({self.fecha})"
    
class Rutina(models.Model):
    TIPO_RUTINA = [
        ('calentamiento', 'Calentamiento'),
        ('trabajo', 'Trabajo Técnico/Principal'),
        ('wod', 'WOD (Entrenamiento del día)'),
        ('enfriamiento', 'Enfriamiento'),
    ]
    
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='rutinas')
    tipo = models.CharField(max_length=20, choices=TIPO_RUTINA)
    descripcion = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.clase.nombre}"

# models.py - Agregar al final del archivo
class RankingWOD(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='rankings')
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    tiempo_minutos = models.PositiveIntegerField(verbose_name="Minutos")
    tiempo_segundos = models.PositiveIntegerField(verbose_name="Segundos")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['tiempo_minutos', 'tiempo_segundos']
        verbose_name_plural = "Rankings WOD"
        unique_together = ('clase', 'atleta')  # Un atleta solo puede tener un tiempo por clase
    
    @property
    def tiempo_total_segundos(self):
        return (self.tiempo_minutos * 60) + self.tiempo_segundos
    
    @property
    def tiempo_formateado(self):
        return f"{self.tiempo_minutos}:{self.tiempo_segundos:02d}"
    
    def __str__(self):
        return f"{self.atleta} - {self.tiempo_formateado} - {self.clase.nombre}"