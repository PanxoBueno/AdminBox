from django import forms
from .models import Atleta, Entrenador, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Usuario
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegistroForm(UserCreationForm):
    tipo_usuario = forms.ChoiceField(
        choices=Usuario.TIPO_USUARIO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de usuario'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'tipo_usuario', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
        
class AtletaForm(forms.ModelForm):
    class Meta:
        model = Atleta
        fields = ['nombre', 'apellido','nivel', 'email','plan']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'nivel': forms.Select(attrs={'class':'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
        }

class EntrenadorForm(forms.ModelForm):
    class Meta: 
        model = Entrenador
        fields = ['nombre', 'apellido','especialidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'especialidad': forms.Select(attrs={'class':'form-select'}),
        }

class BibliotecaForm(forms.ModelForm):
    class Meta:
        model = Biblioteca
        fields = ['nombre', 'descripcion', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ejercicio'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del ejercicio'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'imagen': 'Imagen del ejercicio'
        }
#aca pongo reservas
class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre', 'horario', 'fecha', 'entrenador', 'capacidad_maxima']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'horario': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'format': 'yyyy-mm-dd'  # Formato que acepta el input date
                },
                format='%Y-%m-%d'  # Formato en que Django espera recibir la fecha
            ),
            'entrenador': forms.Select(attrs={'class': 'form-select'}),
            'capacidad_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['atleta', 'clase']
        widgets = {
            'atleta': forms.Select(attrs={'class': 'form-select'}),
            'clase': forms.Select(attrs={'class': 'form-select'}),
        }
        
class MarcaPersonalForm(forms.ModelForm):
    class Meta:
        model = MarcaPersonal
        fields = ['ejercicio_id', 'peso_lb', 'fecha', 'comentarios']  # Añadido 'fecha'
        widgets = {
            'ejercicio_id': forms.Select(attrs={'class': 'form-select'}),
            'peso_lb': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
        labels = {
            'ejercicio_id': 'Ejercicio',
            'peso_lb': 'Peso (LB)',
            'fecha': 'Fecha de la marca'
        }

class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ['tipo', 'descripcion', 'orden']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ejemplo: 3 rondas de:\n- 10 Push Press\n- 15 Air Squats\n- 20 Double Unders'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'descripcion': 'Descripción de la rutina',
            'orden': 'Orden en la clase (0 para primero)'
        }

# forms.py - Agregar al final del archivo
class RankingWODForm(forms.ModelForm):
    class Meta:
        model = RankingWOD
        fields = ['atleta', 'tiempo_minutos', 'tiempo_segundos']
        widgets = {
            'atleta': forms.Select(attrs={'class': 'form-select'}),
            'tiempo_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minutos'
            }),
            'tiempo_segundos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 59,
                'placeholder': 'Segundos'
            }),
        }
        labels = {
            'tiempo_minutos': 'Minutos',
            'tiempo_segundos': 'Segundos'
        }
        