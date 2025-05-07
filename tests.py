from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
from django.db import IntegrityError
from .models import (Usuario, Atleta, Entrenador, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD)
from .forms import (UserRegisterForm, AtletaUpdateForm, EntrenadorUpdateForm,BibliotecaForm, ClaseForm, ReservaForm, MarcaPersonalForm, RutinaForm, RankingWODForm)
import sys
from django.contrib.messages.storage.fallback import FallbackStorage

Usuario = get_user_model()
# Decorador para imprimir el estado de la prueba
def print_test_status(func):
    """Decorador para imprimir el estado de la prueba"""
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        try:
            func(*args, **kwargs)
            print(f"✓ {test_name} - PASÓ")
        except AssertionError:
            print(f"✗ {test_name} - FALLÓ", file=sys.stderr)
            raise
    return wrapper
#pruebas de modelos
class UsuarioModelTests(TestCase):
    def setUp(self):
        self.usuario_atleta = Usuario.objects.create(
            username='atleta_user',
            email='atleta@test.com',
            first_name='Atleta',
            last_name='Test',
            tipo_usuario='atleta',
            plan='1',
            nivel='rookie'
        )
        self.usuario_entrenador = Usuario.objects.create(
            username='entrenador_user',
            email='entrenador@test.com',
            first_name='Entrenador',
            last_name='Test',
            tipo_usuario='entrenador',
            especialidad='crossfit'
        )

    @print_test_status
    def test_usuario_str_method(self):
        self.assertEqual(str(self.usuario_atleta), 'atleta_user (atleta)')
        self.assertEqual(str(self.usuario_entrenador), 'entrenador_user (entrenador)')

    @print_test_status
    def test_usuario_tipo_usuario_field(self):
        self.assertEqual(self.usuario_atleta.tipo_usuario, 'atleta')
        self.assertEqual(self.usuario_entrenador.tipo_usuario, 'entrenador')

    @print_test_status
    def test_usuario_plan_field(self):
        self.assertEqual(self.usuario_atleta.plan, '1')
        self.assertIsNone(self.usuario_entrenador.plan)

    @print_test_status
    def test_usuario_nivel_field(self):
        self.assertEqual(self.usuario_atleta.nivel, 'rookie')
        self.assertIsNone(self.usuario_entrenador.nivel)

    @print_test_status
    def test_usuario_especialidad_field(self):
        self.assertIsNone(self.usuario_atleta.especialidad)
        self.assertEqual(self.usuario_entrenador.especialidad, 'crossfit')
#pruebas de formularios
class TestForms(TestCase):
    def setUp(self):
        # Crear usuario y atleta para pruebas
        self.user, created = Usuario.objects.get_or_create(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            tipo_usuario='atleta'
        )
        self.atleta, created = Atleta.objects.get_or_create(
            usuario=self.user,
            nivel='amateur'
        )
        
        # Crear usuario entrenador
        self.entrenador_user, created = Usuario.objects.get_or_create(
            username='entrenador1',
            email='entrenador@test.com',
            password='testpass123',
            tipo_usuario='entrenador'
        )
        self.entrenador, created = Entrenador.objects.get_or_create(
            usuario=self.entrenador_user,
            especialidad='crossfit'
        )
        
        # Crear clase de prueba
        self.clase, created = Clase.objects.get_or_create(
            nombre='CrossFit AM',
            horario='06:00',
            fecha=date.today(),
            entrenador=self.entrenador,
            capacidad_maxima=15
        )
        
        # Crear ejercicio de prueba
        self.ejercicio, created = Biblioteca.objects.get_or_create(
            nombre='Deadlift',
            descripcion='Ejercicio de halterofilia',
            defaults={
                'imagen': SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
            }
        )
    @print_test_status
    def test_user_register_form_valid(self):
        """Prueba que el formulario de registro es válido con datos correctos"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'tipo_usuario': 'atleta',
            'plan': '1',
            'nivel': 'amateur'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_user_register_form_invalid(self):
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Email inválido
            'password1': 'short',  # Contraseña demasiado corta
            'password2': 'short',  # Contraseña demasiado corta
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)  # Verifica error en el campo email
        self.assertIn('password2', form.errors)  # Verifica error en el campo password2
        self.assertIn('first_name', form.errors)  # Verifica error en el campo first_name
        self.assertIn('last_name', form.errors)  # Verifica error en el campo last_name
        self.assertIn('tipo_usuario', form.errors)  # Verifica error en el campo tipo_usuario
    @print_test_status
    def test_biblioteca_form_valid(self):
        """Prueba el formulario de Biblioteca con imagen válida"""
        image = SimpleUploadedFile(
            "test_image.jpg",  # Nombre del archivo
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",  # Contenido binario de una imagen GIF mínima
            content_type="image/jpeg"  # Tipo MIME
        )
        form_data = {
            'nombre': 'New Exercise',
            'descripcion': 'Test description'
        }
        form = BibliotecaForm(data=form_data, files={'imagen': image})
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_biblioteca_form_invalid(self):
        """Prueba el formulario de Biblioteca sin nombre"""
        form_data = {
            'descripcion': 'Test description'  # Falta el nombre
        }
        form = BibliotecaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    @print_test_status
    def test_clase_form_valid(self):
        """Prueba el formulario de Clase con datos válidos"""
        form_data = {
            'nombre': 'New Class',
            'horario': '07:00',
            'fecha': date.today(),
            'entrenador': self.entrenador.id,
            'capacidad_maxima': 20
        }
        form = ClaseForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_clase_form_invalid(self):
        """Prueba el formulario de Clase con capacidad inválida"""
        form_data = {
            'nombre': 'New Class',
            'horario': '07:00',
            'fecha': date.today(),
            'entrenador': self.entrenador.id,
            'capacidad_maxima': -5  # Capacidad negativa
        }
        form = ClaseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('capacidad_maxima', form.errors)
    @print_test_status
    def test_reserva_form_valid(self):
        """Prueba el formulario de Reserva con datos válidos"""
        form_data = {
            'atleta': self.atleta.id,
            'clase': self.clase.id
        }
        form = ReservaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_marca_personal_form_valid(self):
        """Prueba el formulario de MarcaPersonal con datos válidos"""
        form_data = {
            'ejercicio_id': self.ejercicio.id,
            'peso_lb': 135.5,
            'fecha': date.today(),
            'comentarios': 'Test comment'
        }
        form = MarcaPersonalForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_marca_personal_form_invalid(self):
        """Prueba el formulario de MarcaPersonal con peso negativo"""
        form_data = {
            'ejercicio_id': self.ejercicio.id,
            'peso_lb': -10,  # Peso negativo
            'fecha': date.today()
        }
        form = MarcaPersonalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('peso_lb', form.errors)
    @print_test_status
    def test_rutina_form_valid(self):
        """Prueba el formulario de Rutina con datos válidos"""
        form_data = {
            'tipo': 'wod',
            'descripcion': 'Test WOD',
            'orden': 1
        }
        form = RutinaForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_rutina_form_invalid(self):
        """Prueba el formulario de Rutina sin descripción"""
        form_data = {
            'tipo': 'wod',
            'orden': 1
            # Falta descripción
        }
        form = RutinaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
    @print_test_status
    def test_ranking_wod_form_valid(self):
        """Prueba el formulario de RankingWOD con datos válidos"""
        form_data = {
            'atleta': self.atleta.id,
            'tiempo_minutos': 8,
            'tiempo_segundos': 45
        }
        form = RankingWODForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_ranking_wod_form_invalid(self):
        """Prueba el formulario de RankingWOD con segundos inválidos"""
        form_data = {
            'atleta': self.atleta.id,
            'tiempo_minutos': 8,
            'tiempo_segundos': 60  # Segundos >= 60
        }
        form = RankingWODForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tiempo_segundos', form.errors)
    @print_test_status
    def test_atleta_update_form_valid(self):
        """Prueba el formulario de actualización de Atleta con datos válidos"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'tipo_usuario': 'atleta',
            'plan': '2',
            'nivel': 'rookie'
        }
        form = AtletaUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors.as_json())
    @print_test_status
    def test_atleta_update_form_invalid(self):
        """Prueba el formulario de actualización de Atleta con email inválido"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'invalid-email',  # Email inválido
            'tipo_usuario': 'atleta',
            'plan': '2',
            'nivel': 'rookie'
        }
        form = AtletaUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

       # Crear usuarios
        self.admin, _ = Usuario.objects.get_or_create(
            username='admin',
            email='admin@test.com',
            defaults={
                'password': 'testpass123',
                'tipo_usuario': 'admin'
            }
        )
        self.atleta_user, _ = Usuario.objects.get_or_create(
            username='atleta1',
            email='atleta@test.com',
            defaults={
                'password': 'testpass123',
                'tipo_usuario': 'atleta',
                'plan': '1',
                'nivel': 'amateur'
            }
        )
        self.entrenador_user, _ = Usuario.objects.get_or_create(
            username='entrenador1',
            email='entrenador@test.com',
            defaults={
                'password': 'testpass123',
                'tipo_usuario': 'entrenador',
                'especialidad': 'crossfit'
            }
        )

        # Crear modelos relacionados
        self.entrenador, _ = Entrenador.objects.get_or_create(
            usuario=self.entrenador_user,
            defaults={'especialidad': 'crossfit'}
        )
        self.ejercicio, _ = Biblioteca.objects.get_or_create(
            nombre='Clean',
            descripcion='Cargada'
        )
        self.clase, _ = Clase.objects.get_or_create(
            nombre='WOD',
            horario='06:00',
            fecha=date.today() + timedelta(days=1),
            entrenador=self.entrenador,
            defaults={'capacidad_maxima': 15}
        )
        self.atleta, _ = Atleta.objects.get_or_create(
            usuario=self.atleta_user,
            defaults={'nivel': 'amateur'}
        )
        self.reserva, _ = Reserva.objects.get_or_create(
            atleta=self.atleta,
            clase=self.clase
        )
        self.marca, _ = MarcaPersonal.objects.get_or_create(
            atleta=self.atleta,
            ejercicio_id=self.ejercicio,
            defaults={
                'peso_lb': 185.5,
                'fecha': date.today()
            }
        )
        self.rutina, _ = Rutina.objects.get_or_create(
            clase=self.clase,
            tipo='wod',
            defaults={
                'descripcion': 'Test WOD',
                'orden': 1
            }
        )
        self.ranking, _ = RankingWOD.objects.get_or_create(
            clase=self.clase,
            atleta=self.atleta,
            defaults={
                'tiempo_minutos': 5,
                'tiempo_segundos': 30
            }
        )

    @print_test_status
    def test_menu_view(self):
        """Prueba que la vista del menú responde correctamente para un atleta"""
        from .views import menu
        request = self.factory.get('/menu/')
        request.user = self.atleta_user
        response = menu(request)
        self.assertEqual(response.status_code, 200)

    @print_test_status
    def test_listar_atleta_view(self):
        """Prueba que la vista para listar atletas responde correctamente para un administrador"""
        from .views import listar_atleta
        request = self.factory.get('/atletas/')
        request.user = self.admin
        response = listar_atleta(request)
        self.assertEqual(response.status_code, 200)

    @print_test_status
    def test_ver_marcas_personales_view(self):
        """Prueba que la vista para ver marcas personales responde correctamente para un atleta"""
        from .views import ver_marcas_personales
        request = self.factory.get(f'/marcas/{self.atleta_user.id}/')
        request.user = self.atleta_user
        response = ver_marcas_personales(request, self.atleta_user.id)
        self.assertEqual(response.status_code, 200)

    @print_test_status
    def test_listar_clases_view(self):
        """Prueba que la vista para listar clases responde correctamente para un atleta"""
        from .views import listar_clases
        request = self.factory.get('/clases/')
        request.user = self.atleta_user
        response = listar_clases(request)
        self.assertEqual(response.status_code, 200)

    @print_test_status
    def test_ver_ranking_wod_view(self):
        from .views import ver_ranking_wod
        request = self.factory.get(f'/ranking/{self.clase.id}/')
        request.user = self.atleta_user
        response = ver_ranking_wod(request, self.clase.id)
        self.assertEqual(response.status_code, 200)

    @print_test_status
    def test_crear_reserva_view(self):
        """Prueba que la vista para crear una reserva responde correctamente"""
        from .views import crear_reserva
        request = self.factory.post('/reservar/', {
            'atleta': self.atleta.id,
            'clase': self.clase.id
        })
        request.user = self.atleta_user
        response = crear_reserva(request)
        self.assertEqual(response.status_code, 200)  # Redirige al éxito

    @print_test_status
    def test_crear_marca_personal_view(self):
        request = self.factory.post('/marcas/nueva/', {
        'ejercicio_id': self.ejercicio.id,
        'peso_lb': 200,
        'fecha': date.today()
        })
        request.user = self.atleta_user

