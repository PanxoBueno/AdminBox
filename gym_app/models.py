from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


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

class Usuario(AbstractUser):
    
    TIPO_USUARIO_CHOICES = [
        ('atleta', 'Atleta'),
        ('entrenador', 'Entrenador'),
        ('admin', 'Admin'),
    ]
    PLAN_CHOICES = [
        ('1', '8 Clases'),
        ('2', '12 Clases'),
        ('3', '16 Clases'),
        ('4', 'Open Box'),
        ('5', 'Full Clases'),
        ('6', 'Staff'),
    ]
    NIVEL_CHOICES = [
            ('amateur', 'Amateur'),
            ('rookie', 'Rookie'),
            ('scaled', 'Scaled'),
            ('rx', 'Rx'),
            ('elite', 'Elite')
        ]
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipo de Usuario"
    )
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        blank=True,
        null=True,
        verbose_name="Plan"
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Nivel"
    )
    ESPECIALIDAD_CHOICES = [
        ('crossfit', 'CrossFit'),
        ('halterofilia', 'Halterofilia'),
        ('metcon', 'Metcon'),
    ]
    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        blank=True,
        null=True,
        verbose_name="Especialidad"  
    )

    fecha_contratacion = models.DateField(null=True, blank=True, verbose_name="Fecha de Contratación")
    fecha_caducidad = models.DateField(null=True, blank=True, verbose_name="Fecha de Caducidad")
      
    def save(self, *args, **kwargs):
        # Si cambia el plan y no hay fecha de contratación
        if self.plan and not self.fecha_contratacion:
            self.fecha_contratacion = timezone.now().date()
            
            # Solo calcular caducidad automática si no está establecida
            if not self.fecha_caducidad:
                self.calcular_fecha_caducidad()
        # Si es un nuevo usuario con plan, establecer fechas
        if self.pk is None and self.plan and not self.fecha_contratacion:
            self.fecha_contratacion = timezone.now().date()
            
            # Calcular fecha de caducidad según el plan
            if self.plan == '1':  # 8 Clases (1 mes)
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)
            elif self.plan == '2':  # 12 Clases (1 mes)
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)
            elif self.plan == '3':  # 16 Clases (1 mes)
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)
            elif self.plan == '4':  # Open Box (1 mes)
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)
            elif self.plan == '5':  # Full Clases (1 mes)
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    @property
    def tiene_plan_activo(self):
        if not self.fecha_caducidad:
            return False
        return self.fecha_caducidad >= timezone.now().date()
    
    @property
    def dias_restantes_plan(self):
        if not self.tiene_plan_activo:
            return 0
        return (self.fecha_caducidad - timezone.now().date()).days
    
    def calcular_fecha_caducidad(self):
        if self.plan and self.fecha_contratacion:
            if self.plan in ['1', '2', '3', '4', '5']:  # Todos planes mensuales
                self.fecha_caducidad = self.fecha_contratacion + timedelta(days=30)

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"

class Atleta(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_atleta')
    nivel = models.CharField(max_length=20, choices=Categoria.Nivel, verbose_name="Nivel")
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    estatura_cm = models.PositiveIntegerField(null=True, blank=True, verbose_name="Estatura (cm)")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_nivel_display()}"
    
    def imc(self):
        if self.peso_kg and self.estatura_cm:
            try:
                # Convertir todo a float para el cálculo
                peso = float(self.peso_kg)
                estatura_m = float(self.estatura_cm) / 100  # Convertir cm a m
                imc_calculado = peso / (estatura_m ** 2)
                return round(imc_calculado, 1)
            except (TypeError, ValueError, ZeroDivisionError):
                return None
        return None

class AtletaUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'tipo_usuario', 'plan','nivel']  # Excluir username y contraseñas
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }

class Entrenador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_entrenador')
    especialidad = models.CharField(max_length=20, choices=Categoria.Categoria_esp, verbose_name="Especialidad")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_especialidad_display()}"

class Biblioteca(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField(null=True, blank=True)
    #imagen = models.ImageField(upload_to="ejercicios", null=True)
    video_url = models.URLField(null=True, blank=True, verbose_name="Enlace del Video")  # Campo para el enlace del video

    def __str__(self):
        return self.nombre
    
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
        entrenador_nombre = f"{self.entrenador.usuario.first_name} {self.entrenador.usuario.last_name}" if self.entrenador else "Sin asignar"
        return f"{self.nombre} - {self.get_horario_display()} - {self.fecha} - {entrenador_nombre}"

class Reserva(models.Model):
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('atleta', 'clase')  # Evita reservas duplicadas
    
    def __str__(self):
                return f"{self.atleta.usuario.first_name} {self.atleta.usuario.last_name} - {self.clase.nombre}"
    
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
    @property
    def nombre_completo_atleta(self):
        return f"{self.atleta.usuario.first_name} {self.atleta.usuario.last_name}"
    
    def __str__(self):
        return f"{self.nombre_completo_atleta} - {self.tiempo_formateado} - {self.clase.nombre}"
