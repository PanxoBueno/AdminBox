from django import forms
from .models import Usuario, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Atleta, Entrenador
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))
    first_name = forms.CharField(label='Nombre', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(label='Apellido', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    tipo_usuario = forms.ChoiceField(label='Tipo de usuario', choices=[('atleta', 'Atleta'), ('entrenador', 'Entrenador')], widget=forms.Select(attrs={'class': 'form-select'}))
    plan = forms.ChoiceField(
        label='Plan',
        choices=[
            ('', '-----'),
            ('1', '8 Clases'),
            ('2', '12 Clases'),
            ('3', '16 Clases'),
            ('4', 'Open Box'),
            ('5', 'Full Clases'),
            ('6', 'Staff')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False  # Solo requerido si es atleta
    )
    nivel = forms.ChoiceField(
        label='Nivel',
        choices=[
            ('amateur', 'Amateur'),
            ('rookie', 'Rookie'),
            ('scaled', 'Scaled'),
            ('rx', 'Rx'),
            ('elite', 'Elite')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False  # Solo requerido si es atleta
    )
    especialidad = forms.ChoiceField(
        label='Especialidad',
        choices=[
            ('crossfit', 'CrossFit'),
            ('halterofilia', 'Halterofilia'),
            ('metcon', 'Metcon')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False  # Solo requerido si es entrenador
    )
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'tipo_usuario', 'email', 'plan', 'username', 'password1', 'password2','nivel','especialidad']
        widgets = {
            
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }
        help_texts = {k: "" for k in fields}
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        plan = cleaned_data.get('plan')
        nivel = cleaned_data.get('nivel')
        especialidad = cleaned_data.get('especialidad')

        if tipo_usuario == 'atleta':
            if not plan or plan == '':
                raise forms.ValidationError({'plan': 'Debes seleccionar un plan si eres atleta.'})
            if not nivel or nivel == '':
                raise forms.ValidationError({'nivel': 'Debes seleccionar un nivel si eres atleta.'})
        elif tipo_usuario == 'entrenador':
            cleaned_data['plan'] = '6'  # Asignar automáticamente "Staff" al campo plan
            cleaned_data['nivel'] = None  # Limpiar el nivel si es entrenador
            if not especialidad or especialidad == '':
                raise forms.ValidationError({'especialidad': 'Debes seleccionar una especialidad si eres entrenador.'})

        return cleaned_data
"""""
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))
    first_name = forms.CharField(label='Nombre', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(label='Apellido', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    tipo_usuario = forms.ChoiceField(
        label='Tipo de usuario',
        choices=[('', '-----'), ('atleta', 'Atleta'), ('entrenador', 'Entrenador')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    plan = forms.ChoiceField(
        label='Plan',
        choices=[
            ('', '-----'),
            ('1', '8 Clases'),
            ('2', '12 Clases'),
            ('3', '16 Clases'),
            ('4', 'Open Box'),
            ('5', 'Full Clases'),
            ('6', 'Staff')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Por favor selecciona un plan válido.'}
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'tipo_usuario', 'email', 'plan', 'username', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }
        help_texts = {k: "" for k in fields}  # Eliminar los textos de ayuda por defecto

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        plan = cleaned_data.get('plan')

        if tipo_usuario == 'atleta':
            if not plan or plan == '':
                raise forms.ValidationError({'plan': 'Debes seleccionar un plan si eres atleta.'})
        elif tipo_usuario == 'entrenador':
            cleaned_data['plan'] = '6'  # Asignar automáticamente "Staff" al campo plan

        return cleaned_data
"""
"""
class AtletaForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombre', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(label='Apellido', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    plan = forms.ChoiceField(
        label='Plan',
        choices=[
            ('', '-----'),
            ('1', '8 Clases'),
            ('2', '12 Clases'),
            ('3', '16 Clases'),
            ('4', 'Open Box'),
            ('5', 'Full Clases'),
            ('6', 'Staff')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Atleta
        fields = ['nivel']  # Solo el campo nivel del modelo Atleta
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }
"""


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
    atleta = forms.ModelChoiceField(
        queryset=Atleta.objects.select_related('usuario').all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Atleta"
    )
    class Meta:
        model = Reserva
        fields = ['atleta', 'clase']
        widgets = {
            'clase': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar cómo se muestran las opciones del campo atleta
        self.fields['atleta'].label_from_instance = lambda obj: f"{obj.usuario.first_name} {obj.usuario.last_name}"
    def clean(self):
        cleaned_data = super().clean()
        atleta = cleaned_data.get('atleta')
        clase = cleaned_data.get('clase')

        # Verificar si ya existe una reserva para este atleta y clase
        if Reserva.objects.filter(atleta=atleta, clase=clase).exists():
            raise forms.ValidationError("El atleta ya está inscrito en esta clase.")

        return cleaned_data


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

     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar cómo se muestran las opciones del campo atleta
        self.fields['atleta'].label_from_instance = lambda obj: f"{obj.usuario.first_name} {obj.usuario.last_name}"

class AtletaUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'tipo_usuario', 'plan', 'nivel']  # Excluir username y contraseñas
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
        }

class EntrenadorUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'especialidad']  # Excluir username y contraseñas
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
        }
