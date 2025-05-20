from django import forms
from .models import Usuario, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Atleta
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

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

class BibliotecaForm(forms.ModelForm):
    class Meta:
        model = Biblioteca
        fields = ['nombre', 'descripcion', 'video_url']
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
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enlace del video'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'video_url': 'Imagen del ejercicio'
        }

class ClaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasa una fecha por GET, establecerla como valor inicial
        if 'initial' in kwargs and 'fecha' in kwargs['initial']:
            self.fields['fecha'].initial = kwargs['initial']['fecha']
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
        label="Atleta",
        required=False  # Hacer el campo opcional para entrenadores
    )

    class Meta:
        model = Reserva
        fields = ['clase']
        widgets = {
            'clase': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Personalizar cómo se muestran las opciones del campo atleta
        self.fields['atleta'].label_from_instance = lambda obj: f"{obj.usuario.first_name} {obj.usuario.last_name}"

        # Si el usuario es atleta, establecerlo como opción predeterminada
        if self.request and hasattr(self.request.user, 'perfil_atleta'):
            self.fields['atleta'].initial = self.request.user.perfil_atleta
            self.fields['atleta'].disabled = True
            self.fields['atleta'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        atleta = cleaned_data.get('atleta')
        clase = cleaned_data.get('clase')

        # Si el usuario es atleta, usar su perfil
        if self.request and hasattr(self.request.user, 'perfil_atleta'):
            atleta = self.request.user.perfil_atleta
            cleaned_data['atleta'] = atleta

        if not atleta:
            raise forms.ValidationError("Debes seleccionar un atleta.")

        # Verificar si ya existe una reserva para este atleta y clase
        if Reserva.objects.filter(atleta=atleta, clase=clase).exists():
            raise forms.ValidationError("El atleta ya está inscrito en esta clase.")

        return cleaned_data

class MarcaPersonalForm(forms.ModelForm):
    class Meta:
        model = MarcaPersonal
        fields = ['ejercicio_id', 'peso_lb', 'fecha', 'comentarios']  
        widgets = {
            'ejercicio_id': forms.Select(attrs={'class': 'form-select'}),
            'peso_lb': forms.NumberInput(attrs={
                'class': 'form-control'
               
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
    def clean_peso_lb(self):
        peso_lb = self.cleaned_data.get('peso_lb')
        if peso_lb is not None and peso_lb < 0:
            raise forms.ValidationError("El peso no puede ser negativo.")
        return peso_lb

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
    def clean_tiempo_segundos(self):
        tiempo_segundos = self.cleaned_data.get('tiempo_segundos')
        if tiempo_segundos < 0 or tiempo_segundos >= 60:
            raise forms.ValidationError("El campo 'Segundos' debe estar entre 0 y 59.")
        return tiempo_segundos

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

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AtletaProfileForm(forms.ModelForm):
    class Meta:
        model = Atleta
        fields = ['peso_kg', 'estatura_cm', 'fecha_nacimiento']
        widgets = {
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatura_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class EditarPlanForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['plan', 'fecha_contratacion', 'fecha_caducidad']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'fecha_contratacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el formato de fecha para los inputs
        if self.instance.fecha_contratacion:
            self.initial['fecha_contratacion'] = self.instance.fecha_contratacion.strftime('%Y-%m-%d')
        if self.instance.fecha_caducidad:
            self.initial['fecha_caducidad'] = self.instance.fecha_caducidad.strftime('%Y-%m-%d')
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_contratacion = cleaned_data.get('fecha_contratacion')
        fecha_caducidad = cleaned_data.get('fecha_caducidad')
        
        if fecha_contratacion and fecha_caducidad:
            if fecha_caducidad < fecha_contratacion:
                raise forms.ValidationError("La fecha de caducidad no puede ser anterior a la fecha de contratación")
        
        return cleaned_data