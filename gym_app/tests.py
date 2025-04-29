from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from gym_app.models import Atleta, Entrenador, Biblioteca, Clase, Reserva, MarcaPersonal
from gym_app.forms import AtletaForm, EntrenadorForm, BibliotecaForm, ClaseForm

# filepath: AdminBoxes/gym_app/test_urls.py

class TestCrearAtleta(TestCase):
    
    def test_crear_atleta(self):
        # Define the data to send in the POST request
        data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'nivel': 'rookie',
            'plan': 4,
            'email': 'john.doe@example.com',
        }

        # Send a POST request to the 'crear_atleta' URL
        response = self.client.post(reverse('crear_atleta'), data)

        # Assert the response status code
        self.assertEqual(response.status_code, 302)  # Assuming a redirect on success

        # Assert that the Atleta object was created in the database
        self.assertTrue(Atleta.objects.filter(nombre='John', apellido='Doe').exists())

class TestCrearClase(TestCase):
    
    def setUp(self):
        # Crea un entrenador para usar en la prueba
        self.entrenador = Entrenador.objects.create(
            nombre='Jane',
            apellido='Doe',
            especialidad='crossfit'  # Usa una opción válida de Categoria.Categoria_esp
        )

    def test_crear_clase(self):
        # Define los datos para enviar en la solicitud POST
        data = {
            'nombre': 'Yoga Avanzado',
            'descripcion': 'Clase de yoga para niveles avanzados',
            'capacidad_maxima': 20,
            'fecha': '2025-04-25',
            'horario': '08:00',
            'entrenador': self.entrenador.id,  # Usa el ID del entrenador creado
        }

        # Envía una solicitud POST a la URL 'crear_clase'
        response = self.client.post(reverse('crear_clase'), data)

        # Verifica el código de estado de la respuesta
        self.assertEqual(response.status_code, 302)  # Suponiendo un redireccionamiento en caso de éxito

        # Verifica que el objeto Clase fue creado en la base de datos
        self.assertTrue(Clase.objects.filter(nombre='Yoga Avanzado').exists())