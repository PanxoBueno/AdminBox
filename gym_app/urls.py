from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('', views.menu, name='menu'),
    path('biblioteca/', views.home, name='biblioteca'),
    path('crear_biblioteca/', views.crear_biblioteca, name='crear_biblioteca'),
    path('crear_atleta/', views.crear_atleta, name='crear_atleta'),
    path('listar_atleta/', views.listar_atleta, name='listar_atleta'),
    path('modificar_atleta/<int:pk>/', views.modificar_atleta, name='modificar_atleta'),
    path('borrar_atleta/<int:pk>/', views.borrar_atleta, name='borrar_atleta'),
    path('crear_entrenador/', views.crear_entrenador, name='crear_entrenador'),
    path('modificar_entrenador/<int:pk>/', views.modificar_entrenador, name='modificar_entrenador'),
    path('listar_entrenadores/', views.listar_entrenadores, name='listar_entrenadores'),
    path('borrar_entrenador/<int:pk>/', views.borrar_entrenador, name='borrar_entrenador'),
#REservar
    path('crear_clase/', views.crear_clase, name='crear_clase'),
    path('listar_clases/', views.listar_clases, name='listar_clases'),
    path('borrar_clase/<int:pk>/', views.borrar_clase, name='borrar_clase'),
    path('modificar_clase/<int:pk>/', views.modificar_clase, name='modificar_clase'),
    path('crear_reserva/', views.crear_reserva, name='crear_reserva'),
    path('ver_reservas/', views.ver_reservas, name='ver_reservas'),
    path('get_clase_info/<int:clase_id>/', views.get_clase_info, name='get_clase_info'),
    path('crear_marca/', views.crear_marca_personal, name='crear_marca_personal'),
    path('ver_marcas/<int:atleta_id>/', views.ver_marcas_personales, name='ver_marcas_personales'),
    path('dashboard/<int:atleta_id>/', views.dashboard_atleta, name='dashboard_atleta'),
    path('entrenador/<int:entrenador_id>/clases/', views.clases_entrenador, name='clases_entrenador'),
    path('clase/<int:clase_id>/detalle/', views.detalle_clase_entrenador, name='detalle_clase_entrenador'),
    path('clase/<int:clase_id>/rutinas/', views.detalle_rutinas, name='detalle_rutinas'),
    path('clase/<int:clase_id>/rutinas/crear/', views.crear_rutina, name='crear_rutina'),
    path('rutina/<int:rutina_id>/borrar/', views.borrar_rutina, name='borrar_rutina'),
    path('clase/<int:clase_id>/registrar-tiempo/', views.registrar_tiempo_wod, name='registrar_tiempo_wod'),
    path('clase/<int:clase_id>/ranking/', views.ver_ranking_wod, name='ver_ranking_wod'),
    path('eliminar-reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    
]
    