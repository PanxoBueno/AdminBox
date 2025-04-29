from django.contrib import admin
from .models import Atleta, Entrenador, Biblioteca, Usuario
# Register your models here. aca se registran los modelos para ser CRUD en perfil admin
from django.contrib.auth.admin import UserAdmin
@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('tipo_usuario', 'telefono')}),
    )

admin.site.register(Atleta)
admin.site.register(Entrenador)
admin.site.register(Biblioteca)