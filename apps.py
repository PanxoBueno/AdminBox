from django.apps import AppConfig


class GymAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gym_app'
    
    def ready(self):
        import gym_app.signals 
