from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, AtletaUpdateForm, EntrenadorUpdateForm, BibliotecaForm, ClaseForm, ReservaForm, MarcaPersonalForm, RutinaForm, RankingWODForm, PerfilUpdateForm, AtletaProfileForm, EditarPlanForm
from .models import Atleta, Entrenador, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Usuario
from django.contrib import messages
from django.db.models import Max, Q, Count
import json
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, tipo_usuario_required
from django.core.exceptions import PermissionDenied
from django.db import models
from datetime import datetime, timedelta
from calendar import monthrange
from .utils.email import enviar_email_bienvenida
from django.contrib.auth import update_session_auth_hash

@admin_required
def registro(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not request.user.is_superuser:
                login(request, user)
            if user.tipo_usuario == 'atleta':
                # Crear el perfil de Atleta asegurando que el nivel se guarde
                nivel = form.cleaned_data.get('nivel')
                Atleta.objects.update_or_create(
                    usuario=user,
                    defaults={'nivel': nivel}
                )
                #messages.success(request, 'Atleta registrado con éxito!')
                 # Obtener datos para el email
                alumno_nombre = f"{user.first_name} {user.last_name}"
                plan = dict(form.fields['plan'].choices).get(form.cleaned_data['plan'])
                nivel = dict(form.fields['nivel'].choices).get(form.cleaned_data['nivel'])
                
                # Enviar email de bienvenida
                enviar_email_bienvenida(
                    alumno_email=user.email,
                    alumno_nombre=alumno_nombre,
                    plan=plan,
                    nivel=nivel
                ) 
                messages.success(request, 'Atleta registrado con éxito! Se ha enviado un email de bienvenida.')
            elif user.tipo_usuario == 'entrenador':
                    # Crear perfil de Entrenador
                    especialidad = form.cleaned_data.get('especialidad')
                    Entrenador.objects.update_or_create(
                        usuario=user,
                        defaults={'especialidad': especialidad}
                    )
                    messages.success(request, 'Entrenador registrado con éxito!')   
            return redirect('menu')
            #login(request, user)
            #return redirect('menu')
    else:
        form = UserRegisterForm()
    return render(request, 'registro.html', {'form': form})
@login_required
def home(request):
    biblioteca = Biblioteca.objects.all()
    data={
        'ejercicios': biblioteca
    }
    return render(request, 'home.html', data)
@login_required
def menu(request):
    atletas = Atleta.objects.all()
    entrenadores = Entrenador.objects.all()
    context = {'atletas': atletas, 'entrenadores': entrenadores}
    return render(request, 'menu.html', context)
@admin_required
def crear_atleta(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Atleta registrado con éxito.')
            return redirect('crear_atleta')
    else:
        form = UserRegisterForm()
    return render(request, 'create_atleta.html', {'form': form})

    def listar_atleta(request):
        atletas = Atleta.objects.all().order_by('nivel', 'plan')
        return render(request, 'listar_atletas.html', {'atletas': atletas})
@admin_required
def modificar_atleta(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    atleta = get_object_or_404(Atleta, usuario=usuario)
    
    if request.method == 'POST':
        user_form = AtletaUpdateForm(request.POST, instance=usuario)
        if user_form.is_valid():
            user = user_form.save()
            if user.tipo_usuario == 'atleta':
                atleta.nivel = user_form.cleaned_data.get('nivel')
                atleta.save()
            messages.success(request, 'Atleta actualizado con éxito.')
            return redirect('listar_atleta')
    else:
        initial_data = {
            'nivel': atleta.nivel
        }
        user_form = AtletaUpdateForm(instance=usuario, initial=initial_data)
    
    return render(request, 'update_atleta.html', {
        'form': user_form,
        'atleta': usuario
    })
@admin_required
def borrar_atleta(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Atleta eliminado con éxito.')
        return redirect('listar_atleta')
    return render(request, 'delete_atleta.html', {'atleta': usuario})
@admin_required
def crear_entrenador(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrenador registrado con éxito.')
            return redirect('crear_entrenador')
    else:
        form = UserRegisterForm()
    return render(request, 'create_entrenador.html', {'form': form})
@admin_required
def modificar_entrenador(request, pk):
    try:
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Verificar si el usuario tiene perfil de entrenador
        if not hasattr(usuario, 'perfil_entrenador'):
            messages.error(request, 'El usuario no tiene perfil de entrenador')
            return redirect('listar_entrenadores')
            
        # Verificar que el usuario que edita es el mismo o es admin
        if request.user != usuario and not request.user.is_superuser:
            raise PermissionDenied
            
        entrenador = usuario.perfil_entrenador
        
        if request.method == 'POST':
            form = EntrenadorUpdateForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, 'Entrenador actualizado con éxito.')
                return redirect('listar_entrenadores')
        else:
            initial_data = {'especialidad': entrenador.especialidad}
            form = EntrenadorUpdateForm(instance=usuario, initial=initial_data)
        
        return render(request, 'update_entrenador.html', {
            'form': form,
            'entrenador': usuario
        })
        
    except Exception as e:
        messages.error(request, f'Error al modificar entrenador: {str(e)}')
        return redirect('listar_entrenadores')
@admin_required
def borrar_entrenador(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Entrenador eliminado con éxito.')
        return redirect('listar_entrenadores')
    return render(request, 'delete_entrenador.html', {'entrenador': usuario})
@tipo_usuario_required('entrenador', 'admin')
def crear_biblioteca(request):
    if request.method == 'POST':
        form = BibliotecaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ejercicio registrado con éxito.')
            return redirect('crear_biblioteca')  
    else:
        form = BibliotecaForm()
    
    return render(request, 'create_biblioteca.html', {'form': form})
@tipo_usuario_required('entrenador', 'admin')
def crear_clase(request):
    initial_data = {}
    
    # Si viene fecha por GET, establecerla como inicial
    fecha_param = request.GET.get('fecha')
    if fecha_param:
        try:
            initial_data['fecha'] = datetime.strptime(fecha_param, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
    
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase registrada con éxito.')
            return redirect('calendario_clases')  # Redirigir al calendario
    else:
        form = ClaseForm(initial=initial_data)
    
    return render(request, 'create_clase.html', {'form': form})
@tipo_usuario_required('entrenador', 'admin')
def borrar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        clase.delete()
        messages.success(request, 'Clase eliminada con éxito.')
        return redirect('listar_clases')
    return render(request, 'delete_clase.html', {'clase': clase})
@tipo_usuario_required('entrenador', 'admin')
def modificar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        form = ClaseForm(request.POST, instance=clase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase modificada con éxito.')
            return redirect('listar_clases')
    else:
        form = ClaseForm(instance=clase)
    return render(request, 'update_clase.html', {'form': form, 'clase': clase})
@login_required
def listar_clases(request):
    clases = Clase.objects.all().order_by('fecha', 'horario')
    clases_con_reservas = []
    for clase in clases:
        cantidad_reservas = Reserva.objects.filter(clase=clase).count()
        clases_con_reservas.append({
            'clase': clase,
            'cantidad_reservas': cantidad_reservas
        })
    
    paginator = Paginator(clases_con_reservas, 10)  # Paginar los resultados
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'list_clases.html', {
        'page_obj': page_obj,
        'clases': page_obj,  # Mantener compatibilidad con el template existente
    })
@login_required
@tipo_usuario_required('atleta','entrenador')
def crear_reserva(request):
    #atleta = get_object_or_404(Atleta, usuario=request.user)
    atleta = None
    if request.user.tipo_usuario == 'entrenador':
        es_entrenador = True
    else:
        es_entrenador = False
        if hasattr(request.user, 'perfil_atleta'):
            atleta = request.user.perfil_atleta

    if request.method == 'POST':
        form = ReservaForm(request.POST, request=request)
        if form.is_valid():
            reserva = form.save(commit=False)
            if es_entrenador:
                atleta = form.cleaned_data.get('atleta')  # Seleccionar el atleta desde el formulario
            if atleta:
                reserva.atleta = atleta

            clase = form.cleaned_data['clase']
            reservas_count = Reserva.objects.filter(clase=clase).count()

            if reservas_count >= clase.capacidad_maxima:
                form.add_error('clase', 'Esta clase ha alcanzado su capacidad máxima')
            else:
                try:
                    reserva.save()
                    messages.success(request, 'Clase reservada con éxito.')
                    return redirect('listar_clases')
                except IntegrityError:
                    form.add_error(None, 'Ya existe una reserva para este atleta en esta clase.')
    else:
        form = ReservaForm(request=request)

    return render(request, 'create_reserva.html', {
        'form': form,
        'es_entrenador': es_entrenador
    })
@login_required
def ver_reservas(request):
    # Reservas agrupadas por atleta
    reservas_por_atleta = {}
    for atleta in Atleta.objects.all():
        reservas = Reserva.objects.filter(atleta=atleta)
        if reservas.exists():
            reservas_por_atleta[atleta] = reservas
    
    # Total de atletas por clase
    clases_con_atletas = []
    for clase in Clase.objects.all():
        count = Reserva.objects.filter(clase=clase).count()
        clases_con_atletas.append({
            'clase': clase,
            'count': count,
            'porcentaje': (count / clase.capacidad_maxima) * 100 if clase.capacidad_maxima > 0 else 0
        })
    
    context = {
        'reservas_por_atleta': reservas_por_atleta,
        'clases_con_atletas': clases_con_atletas,
    }
    return render(request, 'view_reservas.html', context)
@tipo_usuario_required('entrenador', 'admin')
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    clase_id = reserva.clase.id
    
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Atleta eliminado de la clase con éxito.')
        return redirect('detalle_clase_entrenador', clase_id=clase_id)
    
    return render(request, 'confirmar_eliminar_reserva.html', {'reserva': reserva})
@login_required
def crear_marca_personal(request):
    if not hasattr(request.user, 'perfil_atleta'):
        messages.error(request, 'Solo los atletas pueden registrar marcas personales.')
        return redirect('menu')
    atleta = request.user.perfil_atleta
    if request.method == 'POST':
        form = MarcaPersonalForm(request.POST)
        if form.is_valid():
            marca = form.save(commit=False)
            marca.atleta = atleta  # Asignar automáticamente al atleta logueado
            try:
                marca.save()
                messages.success(request, 'Marca personal registrada con éxito!')
                return redirect('ver_marcas_personales', atleta_id=request.user.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar la marca: {str(e)}')
    else:
        form = MarcaPersonalForm(initial={'fecha': timezone.now().date()})
    
    return render(request, 'create_marca_personal.html', {
        'form': form,
        'atleta': atleta 
    })
@login_required
def ver_marcas_personales(request, atleta_id):
    usuario_atleta = get_object_or_404(Usuario, pk=atleta_id)
    atleta = usuario_atleta.perfil_atleta
    marcas = MarcaPersonal.objects.filter(atleta=atleta).order_by('-fecha', 'ejercicio_id')
    # Paginación
    paginator = Paginator(marcas, 6)
    page_number = request.GET.get('page')
    marcas = paginator.get_page(page_number)
    # Obtener PRs (máximos pesos por ejercicio)
    prs = {}
    ejercicios = Biblioteca.objects.filter(marcapersonal__atleta=atleta).distinct()
    for ejercicio in ejercicios:
        max_peso = MarcaPersonal.objects.filter(
            atleta=atleta,
            ejercicio_id=ejercicio
        ).aggregate(Max('peso_lb'))['peso_lb__max']
        if max_peso:
            prs[ejercicio.nombre] = max_peso
    return render(request, 'view_marcas_personales.html', {
        'atleta': usuario_atleta,  # Pasamos el usuario para acceder
        'perfil_atleta': atleta,   # Pasamos el perfil atleta para acceder al nivel
        'marcas': marcas,
        'prs': prs
    })
@login_required
def editar_marca_personal(request, marca_id):
    marca = get_object_or_404(MarcaPersonal, pk=marca_id)
    # Verificar que el usuario es el dueño de la marca o es admin/entrenador
    if not (request.user == marca.atleta.usuario or request.user.tipo_usuario in ['entrenador', 'admin']):
        raise PermissionDenied 
    if request.method == 'POST':
        form = MarcaPersonalForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca personal actualizada con éxito!')
            return redirect('ver_marcas_personales', atleta_id=marca.atleta.usuario.pk)
    else:
        form = MarcaPersonalForm(instance=marca)
    
    return render(request, 'editar_marca_personal.html', {
        'form': form,
        'marca': marca
    })
@login_required 
def eliminar_marca_personal(request, marca_id):
    marca = get_object_or_404(MarcaPersonal, pk=marca_id)
    atleta_id = marca.atleta.usuario.pk
    
    # Verificar que el usuario es el dueño de la marca o es admin/entrenador
    if not (request.user == marca.atleta.usuario or request.user.tipo_usuario in ['entrenador', 'admin']):
        raise PermissionDenied
    
    if request.method == 'POST':
        marca.delete()
        messages.success(request, 'Marca personal eliminada con éxito!')
        return redirect('ver_marcas_personales', atleta_id=atleta_id)
    
    return render(request, 'eliminar_marca_personal.html', {
        'marca': marca
    })
@login_required
def dashboard_atleta(request, atleta_id):
    usuario = get_object_or_404(Usuario, pk=atleta_id)
    atleta = get_object_or_404(Atleta, usuario=usuario)
    marcas = MarcaPersonal.objects.filter(atleta=atleta).order_by('fecha')
    # Preparar datos para el gráfico
    series_data = []
    ejercicios = Biblioteca.objects.filter(marcapersonal__atleta=atleta).distinct()
    for ejercicio in ejercicios:
        marcas_ejercicio = marcas.filter(ejercicio_id=ejercicio)
        if marcas_ejercicio.exists():
            series_data.append({
                'name': ejercicio.nombre,
                'data': [
                    [m.fecha.strftime("%Y-%m-%d"), float(m.peso_lb)] 
                    for m in marcas_ejercicio
                ]
            })
    
    context = {
        'atleta': usuario,
        'series_data_json': json.dumps(series_data),
        'marcas_count': marcas.count(),
        'prs': {ejercicio.nombre: max([m.peso_lb for m in marcas.filter(ejercicio_id=ejercicio)])
                for ejercicio in ejercicios
                if marcas.filter(ejercicio_id=ejercicio).exists()}
    }
    return render(request, 'dashboard_atleta.html', context)
@login_required
def listar_atleta(request):
    query = request.GET.get('q', '')  
    usuarios_atletas = Usuario.objects.filter(tipo_usuario='atleta').select_related('perfil_atleta')
    
    # Anotar cada atleta con el conteo de reservas
    usuarios_atletas = usuarios_atletas.annotate(
        num_reservas=models.Count('perfil_atleta__reserva')
    )
    
    if query:
        usuarios_atletas = usuarios_atletas.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(perfil_atleta__nivel__icontains=query) | 
            Q(plan__icontains=query)
        ).order_by('first_name', 'last_name')
    
    # Calcular estadísticas
    total_atletas = usuarios_atletas.count()
    atletas_with_reservas = usuarios_atletas.filter(num_reservas__gt=0).count()
    atletas_without_reservas = total_atletas - atletas_with_reservas
    
    # Ordenar por cantidad de reservas (de menor a mayor)
    usuarios_atletas = usuarios_atletas.order_by('num_reservas')
    
    paginator = Paginator(usuarios_atletas, 10)  
    page_number = request.GET.get('page')
    usuarios_atletas = paginator.get_page(page_number)
    
    return render(request, 'listar_atletas.html', {
        'atletas': usuarios_atletas,
        'query': query,
        'total_atletas': total_atletas,
        'atletas_with_reservas_count': atletas_with_reservas,
        'atletas_without_reservas_count': atletas_without_reservas
    })
@login_required
def clases_entrenador(request, entrenador_id):
    entrenador = get_object_or_404(Entrenador, pk=entrenador_id)
    clases = Clase.objects.filter(entrenador=entrenador).order_by('fecha', 'horario')
    
    # Agrupar clases por fecha
    clases_por_fecha = {}
    for clase in clases:
        fecha_str = clase.fecha.strftime("%Y-%m-%d")
        if fecha_str not in clases_por_fecha:
            clases_por_fecha[fecha_str] = []
        clases_por_fecha[fecha_str].append(clase)
    
    context = {
        'entrenador': entrenador,
        'clases_por_fecha': clases_por_fecha,
    }
    return render(request, 'clases_entrenador.html', context)
@login_required
def detalle_clase_entrenador(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    reservas = Reserva.objects.filter(clase=clase).select_related('atleta')
    
    context = {
        'clase': clase,
        'reservas': reservas,
        'porcentaje_ocupacion': (reservas.count() / clase.capacidad_maxima) * 100,
    }
    return render(request, 'detalle_clase_entrenador.html', context)
@login_required
def listar_entrenadores(request):
    query = request.GET.get('q', '')
    usuarios_entrenador = Usuario.objects.filter(tipo_usuario='entrenador').select_related('perfil_entrenador')
    if query:
        # Filtrar por nombre, apellido, nivel o plan (búsqueda flexible)
        usuarios_entrenador = usuarios_entrenador.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            #Q(perfil_atleta__especialidad__icontains=query) |  # Filtrar por nivel del atleta
            Q(plan__icontains=query)
        )
    #entrenadores = Entrenador.objects.all().order_by('nombre', 'apellido')
    paginator = Paginator(usuarios_entrenador, 10)  # 10 entrenadores por página
    page_number = request.GET.get('page')
    usuarios_entrenador = paginator.get_page(page_number)
    return render(request, 'list_entrenador.html', {'entrenadores': usuarios_entrenador, 'query': query})
@login_required
def get_clase_info(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    reservas_count = Reserva.objects.filter(clase=clase).count()
    disponible = clase.capacidad_maxima - reservas_count
    
    return JsonResponse({
        'capacidad_maxima': clase.capacidad_maxima,
        'reservas_count': reservas_count,
        'disponible': disponible,
        'lleno': reservas_count >= clase.capacidad_maxima
    })
@tipo_usuario_required('entrenador', 'admin')
def crear_rutina(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.clase = clase
            rutina.save()
            messages.success(request, 'Rutina agregada con éxito!')
            return redirect('detalle_rutinas', clase_id=clase.id)
    else:
        form = RutinaForm()
    
    return render(request, 'crear_rutina.html', {
        'form': form,
        'clase': clase,
        'ejercicios': Biblioteca.objects.all()
    })
@login_required
def detalle_rutinas(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    rutinas = clase.rutinas.all()
    
    return render(request, 'detalle_rutinas.html', {
        'clase': clase,
        'rutinas': rutinas
    })
@tipo_usuario_required('entrenador', 'admin')
def borrar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, pk=rutina_id)
    clase_id = rutina.clase.id
    if request.method == 'POST':
        rutina.delete()
        messages.success(request, 'Rutina eliminada con éxito!')
        return redirect('detalle_rutinas', clase_id=clase_id)
    return render(request, 'borrar_rutina.html', {'rutina': rutina})
@login_required
def registrar_tiempo_wod(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    if request.method == 'POST':
        form = RankingWODForm(request.POST)
        if form.is_valid():
            atleta = form.cleaned_data['atleta']
            # Verificar si ya existe un tiempo para este atleta en esta clase
            existing_ranking = RankingWOD.objects.filter(clase=clase, atleta=atleta).first()
            
            if existing_ranking:
                # Si existe, actualizamos el tiempo existente
                existing_ranking.tiempo_minutos = form.cleaned_data['tiempo_minutos']
                existing_ranking.tiempo_segundos = form.cleaned_data['tiempo_segundos']
                existing_ranking.save()
                messages.success(request, 'Tiempo actualizado con éxito!')
            else:
                # Si no existe, creamos un nuevo registro
                ranking = form.save(commit=False)
                ranking.clase = clase
                ranking.save()
                messages.success(request, 'Tiempo registrado con éxito!')
            
            return redirect('ver_ranking_wod', clase_id=clase.id)
    else:
        form = RankingWODForm()
    
    # Solo mostrar atletas que tienen reserva para esta clase
    atletas_reservados = Atleta.objects.filter(reserva__clase=clase)
    form.fields['atleta'].queryset = atletas_reservados
    
    return render(request, 'registrar_tiempo_wod.html', {
        'form': form,
        'clase': clase
    })
@login_required
def ver_ranking_wod(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    rankings = RankingWOD.objects.filter(clase=clase).select_related('atleta__usuario').order_by('tiempo_minutos', 'tiempo_segundos')
    # Agregar posición (ranking) a cada resultado
    ranked_results = []
    for position, ranking in enumerate(rankings, start=1):
        ranked_results.append({
            'position': position,
            'ranking': ranking,
            'atleta': ranking.atleta,
            'nombre_completo': ranking.nombre_completo_atleta,
            'tiempo_formateado': ranking.tiempo_formateado,
            'nivel': ranking.atleta.get_nivel_display()
        })
    
    return render(request, 'ver_ranking_wod.html', {
        'clase': clase,
        'ranked_results': ranked_results
    })

def custom_permission_denied_view(request, exception):
    return render(request, '403.html', status=403)
@login_required
@tipo_usuario_required('entrenador', 'admin')
def calendario_clases(request):
    # Obtener el mes y año actual o de la solicitud
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = now.year
        month = now.month
    
    # Calcular el primer y último día del mes
    _, last_day = monthrange(year, month)
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, last_day)
    
    # Obtener todas las clases del mes
    clases = Clase.objects.filter(
        fecha__gte=first_day,
        fecha__lte=last_day
    ).order_by('fecha', 'horario')
    
    # Organizar las clases por día
    clases_por_dia = {}
    for clase in clases:
        day = clase.fecha.day
        if day not in clases_por_dia:
            clases_por_dia[day] = []
        clases_por_dia[day].append(clase)
    
    # Crear estructura del calendario
    calendar_data = []
    
    # Obtener el primer día de la semana del primer día del mes
    first_weekday = first_day.weekday()  # 0=Lunes, 6=Domingo
    
    # Días del mes anterior (si es necesario para completar la primera semana)
    prev_month_days = []
    if first_weekday > 0:  # Si no empieza en lunes
        prev_month = first_day - timedelta(days=first_weekday)
        for i in range(first_weekday):
            prev_month_days.append({
                'day': (prev_month + timedelta(days=i)).day,
                'is_current_month': False,
                'clases': []
            })
    
    # Días del mes actual
    current_month_days = []
    for day in range(1, last_day.day + 1):
        current_month_days.append({
            'day': day,
            'is_current_month': True,
            'clases': clases_por_dia.get(day, [])
        })
    
    # Días del próximo mes (si es necesario para completar la última semana)
    next_month_days = []
    last_weekday = last_day.weekday()
    if last_weekday < 6:  # Si no termina en domingo
        days_to_add = 6 - last_weekday
        for i in range(1, days_to_add + 1):
            next_month_days.append({
                'day': i,
                'is_current_month': False,
                'clases': []
            })
    
    # Combinar todos los días
    all_days = prev_month_days + current_month_days + next_month_days
    
    # Dividir en semanas (7 días por semana)
    weeks = []
    for i in range(0, len(all_days), 7):
        weeks.append(all_days[i:i+7])
    
    # Navegación entre meses
    prev_month = (month - 1) if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'weeks': weeks,
        'month': month,
        'month_name': first_day.strftime('%B'),
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'current_month': now.month,
        'current_year': now.year,
    }
    
    return render(request, 'calendario_clases.html', context)
@login_required
@tipo_usuario_required('entrenador', 'admin')
def atletas_por_categoria(request):
    # Filtrar SOLO los usuarios que son atletas
    atletas = Usuario.objects.filter(tipo_usuario='atleta')
    
    # Agrupar atletas por nivel con todos los conteos necesarios
    categorias = atletas.values('perfil_atleta__nivel').annotate(
        total=Count('id'),
        activos=Count('id', filter=Q(fecha_caducidad__gte=timezone.now())),
        no_activos=Count('id', filter=Q(fecha_caducidad__lt=timezone.now()) | Q(fecha_caducidad__isnull=True)),
        con_reservas=Count('id', filter=Q(perfil_atleta__reserva__isnull=False)),
        sin_reservas=Count('id', filter=Q(perfil_atleta__reserva__isnull=True))
    ).order_by('perfil_atleta__nivel')
    
    # Procesar los datos para incluir todos los campos necesarios
    categorias_procesadas = []
    for cat in categorias:
        nivel = cat['perfil_atleta__nivel']
        total = cat['total']
        activos = cat['activos']
        no_activos = cat['no_activos']
        con_reservas = cat['con_reservas']
        sin_reservas = cat['sin_reservas']
        
        # Calcular porcentaje de actividad (con reservas)
        porcentaje = (con_reservas / total * 100) if total > 0 else 0
        
        categorias_procesadas.append({
            'nivel': nivel,
            'total': total,
            'activos': activos,
            'no_activos': no_activos,
            'con_reservas': con_reservas,
            'sin_reservas': sin_reservas,
            'porcentaje_actividad': round(porcentaje, 2)
        })
    
    # Calcular totales generales SOLO de atletas
    total_general = {
        'total': sum(cat['total'] for cat in categorias_procesadas),
        'activos': sum(cat['activos'] for cat in categorias_procesadas),
        'no_activos': sum(cat['no_activos'] for cat in categorias_procesadas),
        'con_reservas': sum(cat['con_reservas'] for cat in categorias_procesadas),
        'sin_reservas': sum(cat['sin_reservas'] for cat in categorias_procesadas),
    }
    
    # Calcular porcentaje general
    if total_general['total'] > 0:
        total_general['porcentaje_actividad'] = round(
            (total_general['con_reservas'] / total_general['total'] * 100), 2
        )
    else:
        total_general['porcentaje_actividad'] = 0
    
    # Obtener todos los atletas con información detallada (ya filtrado por tipo_usuario='atleta')
    atletas_detallados = atletas.select_related('perfil_atleta').prefetch_related(
        'perfil_atleta__reserva_set'
    ).order_by('perfil_atleta__nivel', 'first_name')

    # Preparar datos para el template
    niveles = {
        'amateur': {'nombre': 'Amateur', 'atletas': []},
        'rookie': {'nombre': 'Rookie', 'atletas': []},
        'scaled': {'nombre': 'Scaled', 'atletas': []},
        'rx': {'nombre': 'Rx', 'atletas': []},
        'elite': {'nombre': 'Elite', 'atletas': []}
    }

    for atleta in atletas_detallados:
        nivel = atleta.perfil_atleta.nivel
        niveles[nivel]['atletas'].append({
            'id': atleta.id,
            'nombre_completo': f"{atleta.first_name} {atleta.last_name}",
            'email': atleta.email,
            'plan': atleta.plan,
            'get_plan_display': atleta.get_plan_display(),
            'fecha_contratacion': atleta.fecha_contratacion,
            'fecha_caducidad': atleta.fecha_caducidad,
            'tiene_plan_activo': atleta.tiene_plan_activo,
            'reservas_count': atleta.perfil_atleta.reserva_set.count(),
            'marcas_count': atleta.perfil_atleta.marcas_personales.count()
        })

    context = {
        'categorias': categorias_procesadas,
        'niveles': niveles,
        'total_atletas': total_general['total'],  # Usamos el total ya calculado
        'total_general': total_general
    }
    print(f"Total atletas encontrados: {atletas.count()}")
    return render(request, 'atletas_por_categoria.html', context)
@login_required
@tipo_usuario_required('entrenador', 'admin')
def detalle_atleta(request, atleta_id):
    usuario = get_object_or_404(Usuario, pk=atleta_id, tipo_usuario='atleta')
    atleta = get_object_or_404(Atleta, usuario=usuario)
    
    # Últimas 5 reservas
    reservas = Reserva.objects.filter(atleta=atleta).select_related(
        'clase', 'clase__entrenador__usuario'
    ).order_by('-clase__fecha', '-clase__horario')[:5]
    
    # Últimas 5 marcas
    marcas = MarcaPersonal.objects.filter(atleta=atleta).select_related(
        'ejercicio_id'
    ).order_by('-fecha')[:5]
    
    # PRs (mejores marcas por ejercicio)
    prs = MarcaPersonal.objects.filter(
        atleta=atleta
    ).values('ejercicio_id__nombre').annotate(
        max_peso=Max('peso_lb')
    ).order_by('ejercicio_id__nombre')
    
    context = {
        'atleta': usuario,
        'perfil_atleta': atleta,
        'reservas': reservas,
        'marcas': marcas,
        'prs': prs,
        'reservas_count': reservas.count(),
        'marcas_count': marcas.count()
    }
    
    return render(request, 'detalle_atleta.html', context)
@login_required
@tipo_usuario_required('entrenador', 'admin')
def ver_reservas_atleta(request, atleta_id):
    usuario = get_object_or_404(Usuario, pk=atleta_id, tipo_usuario='atleta')
    atleta = get_object_or_404(Atleta, usuario=usuario)
    
    reservas = Reserva.objects.filter(
        atleta=atleta
    ).select_related(
        'clase', 'clase__entrenador__usuario'
    ).order_by('-clase__fecha', '-clase__horario')
    
    # Agrupar por mes
    reservas_por_mes = {}
    for reserva in reservas:
        mes_key = reserva.clase.fecha.strftime("%Y-%m")
        mes_nombre = reserva.clase.fecha.strftime("%B %Y")
        
        if mes_key not in reservas_por_mes:
            reservas_por_mes[mes_key] = {
                'nombre': mes_nombre,
                'reservas': [],
                'count': 0
            }
        
        reservas_por_mes[mes_key]['reservas'].append(reserva)
        reservas_por_mes[mes_key]['count'] += 1
    
    context = {
        'atleta': usuario,
        'perfil_atleta': atleta,
        'reservas_por_mes': reservas_por_mes,
        'total_reservas': reservas.count()
    }
    
    return render(request, 'reservas_atleta.html', context)
@login_required
def detalle_atleta_plan(request, atleta_id):
    usuario = get_object_or_404(Usuario, pk=atleta_id, tipo_usuario='atleta')
    atleta = get_object_or_404(Atleta, usuario=usuario)
    
    context = {
        'atleta': usuario,
        'perfil_atleta': atleta,
    }
    
    return render(request, 'detalle_atleta_plan.html', context)
@login_required
def mi_perfil(request):
    usuario = request.user
    atleta = None
    
    if hasattr(usuario, 'perfil_atleta'):
        atleta = usuario.perfil_atleta
    
    # Formularios
    perfil_form = PerfilUpdateForm(instance=usuario)
    password_form = PasswordChangeForm(user=usuario)
    atleta_form = None
    
    if atleta:
        atleta_form = AtletaProfileForm(instance=atleta)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            perfil_form = PerfilUpdateForm(request.POST, instance=usuario)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Perfil actualizado con éxito!')
                return redirect('mi_perfil')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=usuario, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantener la sesión activa
                messages.success(request, 'Contraseña actualizada con éxito!')
                return redirect('mi_perfil')
        
        elif 'update_atleta_data' in request.POST and atleta:
            atleta_form = AtletaProfileForm(request.POST, instance=atleta)
            if atleta_form.is_valid():
                atleta_form.save()
                messages.success(request, 'Datos de atleta actualizados con éxito!')
                return redirect('mi_perfil')
    
    context = {
        'perfil_form': perfil_form,
        'password_form': password_form,
        'atleta_form': atleta_form,
        'atleta': atleta,
    }
    
    return render(request, 'mi_perfil.html', context)
@admin_required
def editar_plan_atleta(request, atleta_id):
    usuario = get_object_or_404(Usuario, pk=atleta_id, tipo_usuario='atleta')
    
    if request.method == 'POST':
        form = EditarPlanForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan actualizado correctamente')
            return redirect('detalle_atleta_plan', atleta_id=atleta_id)
    else:
        form = EditarPlanForm(instance=usuario)
    
    context = {
        'form': form,
        'atleta': usuario,
    }
    
    return render(request, 'editar_plan_atleta.html', context)
@login_required
def ranking_por_categoria(request):
    # Obtener parámetros de filtro
    wod_id = request.GET.get('wod_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Preparar filtros
    filtros = Q()
    if wod_id:
        filtros &= Q(clase_id=wod_id)
    if fecha_inicio:
        filtros &= Q(clase__fecha__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(clase__fecha__lte=fecha_fin)
    
    # Obtener todos los rankings agrupados por nivel
    niveles = {
        'amateur': {'nombre_display': 'Amateur', 'rankings': [], 'estadisticas': {}},
        'rookie': {'nombre_display': 'Rookie', 'rankings': [], 'estadisticas': {}},
        'scaled': {'nombre_display': 'Scaled', 'rankings': [], 'estadisticas': {}},
        'rx': {'nombre_display': 'Rx', 'rankings': [], 'estadisticas': {}},
        'elite': {'nombre_display': 'Elite', 'rankings': [], 'estadisticas': {}}
    }
    
    # Obtener los últimos 10 rankings por cada nivel, ordenados por tiempo
    for nivel in niveles.keys():
        rankings = RankingWOD.objects.filter(
            filtros,
            atleta__nivel=nivel
        ).select_related(
            'atleta__usuario', 'clase'
        ).order_by('tiempo_minutos', 'tiempo_segundos')[:10]
        
        # Calcular estadísticas básicas
        tiempos = [r.tiempo_total_segundos for r in rankings]
        
        niveles[nivel]['rankings'] = rankings
        niveles[nivel]['ultima_actualizacion'] = timezone.now()
        niveles[nivel]['estadisticas'] = {
            'promedio': sum(tiempos)/len(tiempos) if tiempos else 0,
            'mejor': min(tiempos) if tiempos else 0,
            'peor': max(tiempos) if tiempos else 0,
            'total_atletas': rankings.count()
        }
    
    # Obtener lista de WODs para el filtro
    wods = Clase.objects.filter(rankings__isnull=False).distinct().order_by('-fecha', 'nombre')
    
    context = {
        'rankings_por_nivel': niveles,
        'wods': wods,
        'filtro_wod': int(wod_id) if wod_id else None,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    return render(request, 'ranking_por_categoria.html', context)
@login_required
def seleccionar_atleta_comparacion(request):
# Obtener todos los atletas
    atletas = Atleta.objects.all().select_related('usuario').order_by('usuario__first_name')
    
    # Si es atleta, excluirse a sí mismo
    if hasattr(request.user, 'perfil_atleta'):
        atletas = atletas.exclude(usuario=request.user)
    
    return render(request, 'seleccionar_comparacion.html', {
        'atletas': atletas
    })
@login_required
def seleccionar_segundo_atleta(request, atleta1_id):
    atleta1 = get_object_or_404(Atleta, pk=atleta1_id)
    atletas = Atleta.objects.exclude(pk=atleta1_id).select_related('usuario').order_by('usuario__first_name')
    
    return render(request, 'seleccionar_segundo_atleta.html', {
        'atleta1': atleta1,
        'atletas': atletas
    })
@login_required
def comparar_marcas_atletas(request, atleta1_id, atleta2_id):
    # Obtener los atletas
    atleta1 = get_object_or_404(Atleta, pk=atleta1_id)
    atleta2 = get_object_or_404(Atleta, pk=atleta2_id)
    
    # Verificar permisos
    user = request.user
    if user.tipo_usuario == 'atleta':
        if not (hasattr(user, 'perfil_atleta') and 
                (user.perfil_atleta.pk in [atleta1_id, atleta2_id])):
            raise PermissionDenied("No tienes permiso para ver esta comparación")
    # Obtener ejercicios comunes entre ambos atletas
    ejercicios_atleta1 = set(MarcaPersonal.objects.filter(atleta=atleta1).values_list('ejercicio_id__nombre', flat=True).distinct())
    ejercicios_atleta2 = set(MarcaPersonal.objects.filter(atleta=atleta2).values_list('ejercicio_id__nombre', flat=True).distinct())
    ejercicios_comunes = list(ejercicios_atleta1.intersection(ejercicios_atleta2))
    
    # Obtener PRs (mejores marcas) para cada atleta en los ejercicios comunes
    prs_comparativa = []
    
    for ejercicio in ejercicios_comunes:
        # PR del atleta 1
        pr_atleta1 = MarcaPersonal.objects.filter(
            atleta=atleta1,
            ejercicio_id__nombre=ejercicio
        ).order_by('-peso_lb').first()
        
        # PR del atleta 2
        pr_atleta2 = MarcaPersonal.objects.filter(
            atleta=atleta2,
            ejercicio_id__nombre=ejercicio
        ).order_by('-peso_lb').first()
        
        if pr_atleta1 and pr_atleta2:
            diferencia = pr_atleta1.peso_lb - pr_atleta2.peso_lb
            porcentaje = (diferencia / pr_atleta2.peso_lb * 100) if pr_atleta2.peso_lb != 0 else 0
            
            prs_comparativa.append({
                'ejercicio': ejercicio,
                'atleta1': {
                    'peso': pr_atleta1.peso_lb,
                    'fecha': pr_atleta1.fecha,
                    'comentarios': pr_atleta1.comentarios
                },
                'atleta2': {
                    'peso': pr_atleta2.peso_lb,
                    'fecha': pr_atleta2.fecha,
                    'comentarios': pr_atleta2.comentarios
                },
                'diferencia': diferencia,
                'porcentaje': round(porcentaje, 2)
            })
    
    # Preparar datos para gráficos de progreso comparativo
    series_data = []
    
    for ejercicio in ejercicios_comunes[:5]: # Limitar a los primeros 5 ejercicios para el gráfico  
        # Datos atleta 1
        marcas_atleta1 = MarcaPersonal.objects.filter(
            atleta=atleta1,
            ejercicio_id__nombre=ejercicio
        ).order_by('fecha')
        
        # Datos atleta 2
        marcas_atleta2 = MarcaPersonal.objects.filter(
            atleta=atleta2,
            ejercicio_id__nombre=ejercicio
        ).order_by('fecha')
        
        if marcas_atleta1.exists() and marcas_atleta2.exists():
            series_data.append({
                'name': f"{atleta1.usuario.first_name} - {ejercicio}",
                'data': [
                    [m.fecha.strftime("%Y-%m-%d"), float(m.peso_lb)] 
                    for m in marcas_atleta1
                ],
                'color': '#FF0000'  # Rojo para atleta 1
            })
            
            series_data.append({
                'name': f"{atleta2.usuario.first_name} - {ejercicio}",
                'data': [
                    [m.fecha.strftime("%Y-%m-%d"), float(m.peso_lb)] 
                    for m in marcas_atleta2
                ],
                'color': '#0000FF'  # Azul para atleta 2
            })
    
    context = {
        'atleta1': atleta1,
        'atleta2': atleta2,
        'prs_comparativa': sorted(prs_comparativa, key=lambda x: abs(x['diferencia']), reverse=True),
        'ejercicios_comunes': ejercicios_comunes,
        'series_data_json': json.dumps(series_data),
        'total_ejercicios_comunes': len(ejercicios_comunes)
    }
    
    return render(request, 'comparar_marcas.html', context)

@login_required
@tipo_usuario_required('atleta')
def dashboard_atleta_reservas(request):
    usuario = request.user
    if not hasattr(usuario, 'perfil_atleta'):
        messages.error(request, 'Solo los atletas pueden acceder a este panel.')
        return redirect('menu')
    atleta = usuario.perfil_atleta

    # Próximas reservas (clases futuras)
    hoy = timezone.now().date()
    reservas_futuras = Reserva.objects.filter(
        atleta=atleta,
        clase__fecha__gte=hoy
    ).select_related('clase', 'clase__entrenador__usuario').order_by('clase__fecha', 'clase__horario')

    # Historial de reservas (clases pasadas)
    reservas_pasadas = Reserva.objects.filter(
        atleta=atleta,
        clase__fecha__lt=hoy
    ).select_related('clase', 'clase__entrenador__usuario').order_by('-clase__fecha', '-clase__horario')

    context = {
        'atleta': usuario,
        'reservas_futuras': reservas_futuras,
        'reservas_pasadas': reservas_pasadas,
    }
    return render(request, 'dashboard_atleta_reservas.html', context)