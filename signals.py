from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Atleta, Entrenador

@receiver(post_save, sender=Usuario)
def crear_perfil_atleta(sender, instance, created, **kwargs):
    if created and instance.tipo_usuario == 'atleta':
        Atleta.objects.create(usuario=instance, nivel='amateur')  # Nivel predeterminado
def crear_perfil_entrenador(sender, instance, created, **kwargs):
    if created and instance.tipo_usuario == 'entrenador':
        Entrenador.objects.create(usuario=instance)