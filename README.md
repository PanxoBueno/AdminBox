# AdmiBox 🏋️‍♂️

AdmiBox es una plataforma web diseñada para gestionar gimnasios de CrossFit, facilitando la administración de atletas, entrenadores y administradores. Su objetivo es unificar y centralizar la información relacionada con rutinas, reservas, marcas personales y la comunidad deportiva.

## Características

- **Gestión de Atletas**: Registro y seguimiento de marcas personales, rutinas y progreso.
- **Gestión de Entrenadores**: Asignación de rutinas, seguimiento de entrenamientos y comunicación con atletas.
- **Gestión de Administradores**: Control de reservas, administración de usuarios y gestión de la comunidad.
- **Comunidad Deportiva**: Espacio para la interacción entre atletas y entrenadores, compartiendo logros y motivación.

## Tecnologías Utilizadas 📋

- **Framework**: Django 5.2
- **Lenguaje de Programación**: Python 3.8
- **Frontend**: Bootstrap 5
- **Base de Datos**: MySQL

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/PanxoBueno/AdmiBox.git
    ```

2. Navega al directorio del proyecto:
    ```bash
    cd AdmiBox
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configura la base de datos en `settings.py`:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'nombre_de_tu_base_de_datos',
            'USER': 'tu_usuario',
            'PASSWORD': 'tu_contraseña',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    ```

5. Realiza las migraciones:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Realiza la creación de un superusuario
   ```bash
    python manage.py createsuperuser
    ```
8. Ejecuta el servidor:
    ```bash
    python manage.py runserver
    ```

## Uso

1. Accede a la aplicación en tu navegador:
    ```
    http://127.0.0.1:8000
    ```
2. Accede como superusuario:
   ```
    http://127.0.0.1:8000/admin
    ```
4. Registra usuarios y comienza a gestionar tu gimnasio de CrossFit.

---

¡Gracias por usar AdmiBox! Si tienes alguna pregunta o sugerencia, no dudes en contactar.

```
