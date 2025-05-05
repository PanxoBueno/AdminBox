from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from gym_app.models import Usuario, Atleta, Entrenador, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Biblioteca
from gym_app.forms import UserRegisterForm, ClaseForm, ReservaForm, MarcaPersonalForm, RutinaForm, RankingWODForm

User = get_user_model()

class TestCrearAtleta(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'atleta_user',
            'password': 'password123',
            'email': 'atleta@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'tipo_usuario': 'atleta',
            'plan': '4',  # Open Box
            'nivel': 'rookie',
        }
        self.user = Usuario.objects.create_user(**self.user_data)

    def test_crear_atleta(self):
        # Verificar que el usuario se creó correctamente
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Atleta.objects.count(), 1)
        
        atleta = Atleta.objects.first()
        self.assertEqual(atleta.usuario, self.user)
        self.assertEqual(atleta.nivel, 'rookie')
        
        # Verificar los datos del usuario
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.tipo_usuario, 'atleta')
        self.assertEqual(self.user.plan, '4')

    def test_atleta_form_valido(self):
        form_data = {
            'username': 'new_atleta',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'email': 'new@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'tipo_usuario': 'atleta',
            'plan': '3',  # 16 Clases
            'nivel': 'scaled',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_atleta_form_invalido(self):
        # Falta el nivel (requerido para atletas)
        form_data = {
            'username': 'new_atleta',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'email': 'new@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'tipo_usuario': 'atleta',
            'plan': '3',  # 16 Clases
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nivel', form.errors)

class TestCrearEntrenador(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'entrenador_user',
            'password': 'password123',
            'email': 'entrenador@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'tipo_usuario': 'entrenador',
            'especialidad': 'crossfit',
        }
        self.user = Usuario.objects.create_user(**self.user_data)

    def test_crear_entrenador(self):
        # Verificar que el usuario se creó correctamente
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Entrenador.objects.count(), 1)
        
        entrenador = Entrenador.objects.first()
        self.assertEqual(entrenador.usuario, self.user)
        self.assertEqual(entrenador.especialidad, 'crossfit')
        
        # Verificar que el plan se estableció como "Staff" automáticamente
        self.assertEqual(self.user.plan, '6')

    def test_entrenador_form_valido(self):
        form_data = {
            'username': 'new_entrenador',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'email': 'new@example.com',
            'first_name': 'Coach',
            'last_name': 'Smith',
            'tipo_usuario': 'entrenador',
            'especialidad': 'halterofilia',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_entrenador_form_invalido(self):
        # Falta la especialidad (requerida para entrenadores)
        form_data = {
            'username': 'new_entrenador',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'email': 'new@example.com',
            'first_name': 'Coach',
            'last_name': 'Smith',
            'tipo_usuario': 'entrenador',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('especialidad', form.errors)

class TestClase(TestCase):
    def setUp(self):
        # Crear usuario y entrenador
        self.user = Usuario.objects.create_user(
            username='entrenador_user',
            password='password123',
            email='entrenador@example.com',
            first_name='Jane',
            last_name='Doe',
            tipo_usuario='entrenador',
            especialidad='crossfit'
        )
        self.entrenador = Entrenador.objects.create(
            usuario=self.user,
            especialidad='crossfit'
        )

    def test_crear_clase(self):
        data = {
            'nombre': 'Yoga Avanzado',
            'descripcion': 'Clase de yoga para niveles avanzados',
            'capacidad_maxima': 20,
            'fecha': '2025-04-25',
            'horario': '08:00',
            'entrenador': self.entrenador.id,
        }

        # Probar el formulario
        form = ClaseForm(data=data)
        self.assertTrue(form.is_valid())

        # Probar la vista
        response = self.client.post(reverse('crear_clase'), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito

        # Verificar que la clase se creó
        self.assertTrue(Clase.objects.filter(nombre='Yoga Avanzado').exists())
        clase = Clase.objects.get(nombre='Yoga Avanzado')
        self.assertEqual(clase.entrenador, self.entrenador)
        self.assertEqual(clase.capacidad_maxima, 20)

    def test_clase_form_invalido(self):
        # Faltan campos requeridos
        data = {
            'nombre': '',  # Nombre vacío
            'horario': '25:00',  # Horario inválido
        }
        form = ClaseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertIn('horario', form.errors)

class TestReserva(TestCase):
    def setUp(self):
        # Crear usuario atleta
        self.user_atleta = Usuario.objects.create_user(
            username='atleta_user',
            password='password123',
            email='atleta@example.com',
            first_name='John',
            last_name='Doe',
            tipo_usuario='atleta',
            plan='4',
            nivel='rookie'
        )
        self.atleta = Atleta.objects.create(
            usuario=self.user_atleta,
            nivel='rookie'
        )

        # Crear usuario entrenador y clase
        self.user_entrenador = Usuario.objects.create_user(
            username='entrenador_user',
            password='password123',
            email='entrenador@example.com',
            first_name='Jane',
            last_name='Doe',
            tipo_usuario='entrenador',
            especialidad='crossfit'
        )
        self.entrenador = Entrenador.objects.create(
            usuario=self.user_entrenador,
            especialidad='crossfit'
        )
        self.clase = Clase.objects.create(
            nombre='CrossFit Básico',
            horario='08:00',
            fecha='2025-05-01',
            entrenador=self.entrenador,
            capacidad_maxima=15
        )

    def test_crear_reserva(self):
        data = {
            'atleta': self.atleta.id,
            'clase': self.clase.id
        }

        # Probar el formulario
        form = ReservaForm(data=data)
        self.assertTrue(form.is_valid())

        # Probar la vista (necesita autenticación)
        self.client.login(username='atleta_user', password='password123')
        response = self.client.post(reverse('crear_reserva'), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito

        # Verificar que la reserva se creó
        self.assertTrue(Reserva.objects.filter(atleta=self.atleta, clase=self.clase).exists())
        self.assertEqual(Reserva.objects.count(), 1)

    def test_reserva_duplicada(self):
        # Crear primera reserva
        Reserva.objects.create(atleta=self.atleta, clase=self.clase)

        # Intentar crear reserva duplicada
        data = {
            'atleta': self.atleta.id,
            'clase': self.clase.id
        }
        form = ReservaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Error de validación general

    def test_capacidad_maxima(self):
        # Llenar la clase
        for i in range(self.clase.capacidad_maxima):
            user = Usuario.objects.create_user(
                username=f'atleta_{i}',
                password='password123',
                email=f'atleta_{i}@example.com',
                first_name=f'Atleta_{i}',
                last_name='Doe',
                tipo_usuario='atleta',
                plan='4',
                nivel='rookie'
            )
            atleta = Atleta.objects.create(usuario=user, nivel='rookie')
            Reserva.objects.create(atleta=atleta, clase=self.clase)

        # Intentar crear una reserva adicional
        data = {
            'atleta': self.atleta.id,
            'clase': self.clase.id
        }
        form = ReservaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('clase', form.errors)
"""'''
class TestMarcaPersonal(TestCase):
    def setUp(self):
        # Crear usuario atleta
        self.user = Usuario.objects.create_user(
            username='atleta_user',
            password='password123',
            email='atleta@example.com',
            first_name='John',
            last_name='Doe',
            tipo_usuario='atleta',
            plan='4',
            nivel='rookie'
        )
        self.atleta = Atleta.objects.create(
            usuario=self.user,
            nivel='rookie'
        )

        # Crear ejercicio en biblioteca
        self.ejercicio = Biblioteca.objects.create(
            nombre='Back Squat',
            descripcion='Sentadilla trasera'
        )

    def test_crear_marca_personal(self):
        data = {
            'ejercicio_id': self.ejercicio.id,
            'peso_lb': 185.5,
            'fecha': '2025-01-15',
            'comentarios': 'PR personal'
        }

        # Probar el formulario
        form = MarcaPersonalForm(data=data)
        self.assertTrue(form.is_valid())

        # Probar la vista (necesita autenticación)
        self.client.login(username='atleta_user', password='password123')
        response = self.client.post(reverse('crear_marca_personal'), {**data, 'atleta_id': self.atleta.id})
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito

        # Verificar que la marca se creó
        self.assertTrue(MarcaPersonal.objects.filter(atleta=self.atleta, ejercicio_id=self.ejercicio).exists())
        marca = MarcaPersonal.objects.first()
        self.assertEqual(marca.peso_lb, 185.5)
        self.assertEqual(marca.comentarios, 'PR personal')

class TestWOD(TestCase):
    def setUp(self):
        # Crear usuario atleta
        self.user_atleta = Usuario.objects.create_user(
            username='atleta_user',
            password='password123',
            email='atleta@example.com',
            first_name='John',
            last_name='Doe',
            tipo_usuario='atleta',
            plan='4',
            nivel='rookie'
        )
        self.atleta = Atleta.objects.create(
            usuario=self.user_atleta,
            nivel='rookie'
        )

        # Crear usuario entrenador y clase
        self.user_entrenador = Usuario.objects.create_user(
            username='entrenador_user',
            password='password123',
            email='entrenador@example.com',
            first_name='Jane',
            last_name='Doe',
            tipo_usuario='entrenador',
            especialidad='crossfit'
        )
        self.entrenador = Entrenador.objects.create(
            usuario=self.user_entrenador,
            especialidad='crossfit'
        )
        self.clase = Clase.objects.create(
            nombre='WOD Fran',
            horario='08:00',
            fecha='2025-05-01',
            entrenador=self.entrenador,
            capacidad_maxima=15
        )

        # Crear reserva para el atleta
        self.reserva = Reserva.objects.create(
            atleta=self.atleta,
            clase=self.clase
        )

    def test_registrar_tiempo_wod(self):
        data = {
            'atleta': self.atleta.id,
            'tiempo_minutos': 5,
            'tiempo_segundos': 30
        }

        # Probar el formulario
        form = RankingWODForm(data=data)
        self.assertTrue(form.is_valid())

        # Probar la vista (necesita autenticación)
        self.client.login(username='entrenador_user', password='password123')
        response = self.client.post(reverse('registrar_tiempo_wod', args=[self.clase.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito

        # Verificar que el tiempo se registró
        self.assertTrue(RankingWOD.objects.filter(atleta=self.atleta, clase=self.clase).exists())
        ranking = RankingWOD.objects.first()
        self.assertEqual(ranking.tiempo_minutos, 5)
        self.assertEqual(ranking.tiempo_segundos, 30)
        self.assertEqual(ranking.tiempo_formateado, '5:30')

    def test_actualizar_tiempo_wod(self):
        # Crear tiempo inicial
        RankingWOD.objects.create(
            clase=self.clase,
            atleta=self.atleta,
            tiempo_minutos=6,
            tiempo_segundos=0
        )

        # Datos para actualizar
        data = {
            'atleta': self.atleta.id,
            'tiempo_minutos': 4,
            'tiempo_segundos': 45
        }

        # Probar que se actualiza en lugar de crear duplicado
        form = RankingWODForm(data=data)
        self.assertTrue(form.is_valid())

        # Verificar que solo hay un registro (no se duplicó)
        self.assertEqual(RankingWOD.objects.count(), 1)
        ranking = RankingWOD.objects.first()
        self.assertEqual(ranking.tiempo_minutos, 6)  # Aún el valor original

        # Actualizar
        ranking.tiempo_minutos = 4
        ranking.tiempo_segundos = 45
        ranking.save()

        ranking.refresh_from_db()
        self.assertEqual(ranking.tiempo_minutos, 4)
        self.assertEqual(ranking.tiempo_segundos, 45)
"""
