from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, AtletaUpdateForm, EntrenadorUpdateForm, BibliotecaForm, ClaseForm, ReservaForm, MarcaPersonalForm, RutinaForm, RankingWODForm
from .models import Atleta, Entrenador, Biblioteca, Clase, Reserva, MarcaPersonal, Rutina, RankingWOD, Usuario
from django.contrib import messages
from django.db.models import Max, Q
import json
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


@login_required
def registro(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.tipo_usuario == 'atleta':
                # Crear el perfil de Atleta asegurando que el nivel se guarde
                nivel = form.cleaned_data.get('nivel')
                Atleta.objects.update_or_create(
                    usuario=user,
                    defaults={'nivel': nivel}
                )
                messages.success(request, 'Atleta registrado con éxito!')
            elif user.tipo_usuario == 'entrenador':
                    # Crear perfil de Entrenador
                    especialidad = form.cleaned_data.get('especialidad')
                    Entrenador.objects.update_or_create(
                        usuario=user,
                        defaults={'especialidad': especialidad}
                    )
                    messages.success(request, 'Entrenador registrado con éxito!')   
            login(request, user)
            return redirect('menu')
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
@login_required
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
@login_required
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

def borrar_atleta(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Atleta eliminado con éxito.')
        return redirect('listar_atleta')
    return render(request, 'delete_atleta.html', {'atleta': usuario})
@login_required
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
@login_required
def modificar_entrenador(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    entrenador = get_object_or_404(Entrenador, usuario=usuario)
    if request.method == 'POST':
        user_form = EntrenadorUpdateForm(request.POST, instance=usuario)
        if user_form.is_valid():
            user = user_form.save()
            if user.tipo_usuario == 'entrenador':
                entrenador.especialidad = user_form.cleaned_data.get('especialidad')
                entrenador.save()
            messages.success(request, 'Entrenador actualizado con éxito.')
            return redirect('listar_entrenadores')
    else:
        initial_data = {
            'especialidad': entrenador.especialidad
        }
        user_form = EntrenadorUpdateForm(instance=usuario, initial=initial_data)
    
    return render(request, 'update_entrenador.html', {'form': user_form, 'entrenador': usuario})

def borrar_entrenador(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Entrenador eliminado con éxito.')
        return redirect('listar_entrenadores')
    return render(request, 'delete_entrenador.html', {'entrenador': usuario})

@login_required
def crear_biblioteca(request):
    if request.method == 'POST':
        form = BibliotecaForm(request.POST, request.FILES)  # Importante incluir request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Ejercicio registrado con éxito.')
            return redirect('crear_biblioteca')  
    else:
        form = BibliotecaForm()
    
    return render(request, 'create_biblioteca.html', {'form': form})

@login_required
def crear_clase(request):
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clase registrada con éxito.')
            return redirect('crear_clase')
    else:
        form = ClaseForm()
    return render(request, 'create_clase.html', {'form': form})
@login_required
def borrar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        clase.delete()
        messages.success(request, 'Clase eliminada con éxito.')
        return redirect('listar_clases')
    return render(request, 'delete_clase.html', {'clase': clase})
@login_required
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
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            # Verificar capacidad de la clase
            clase = form.cleaned_data['clase']
            reservas_count = Reserva.objects.filter(clase=clase).count()
            if reservas_count >= clase.capacidad_maxima:
                form.add_error('clase', 'Esta clase ha alcanzado su capacidad máxima')
            else:
                try:
                    form.save()
                    messages.success(request, 'Clase reservada con éxito.')
                    return redirect('crear_reserva')
                except IntegrityError:
                    form.add_error(None, 'Ya existe una reserva para este atleta en esta clase.')
    else:
        form = ReservaForm()
    return render(request, 'create_reserva.html', {'form': form})
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
@login_required
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
    if request.method == 'POST':
        form = MarcaPersonalForm(request.POST)
        if form.is_valid():
            marca = form.save(commit=False)
            atleta_id = request.POST.get('atleta_id')
            if not atleta_id:
                messages.error(request, 'Debes seleccionar un atleta.')
                return redirect('crear_marca_personal')
            
            try:
                marca.atleta = Atleta.objects.get(pk=atleta_id)
                marca.save()
                messages.success(request, 'Marca personal registrada con éxito!')
                return redirect('ver_marcas_personales', atleta_id=atleta_id)
            except Atleta.DoesNotExist:
                messages.error(request, 'El atleta seleccionado no existe.')
    else:
        form = MarcaPersonalForm(initial={'fecha': timezone.now().date()})  # Fecha actual por defecto
    
    return render(request, 'create_marca_personal.html', {
        'form': form,
        'atletas': Atleta.objects.select_related('usuario').all()
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
    query = request.GET.get('q', '')  # Obtiene el parámetro de búsqueda (si existe)
    # Filtrar usuarios cuyo tipo_usuario sea "atleta"
    usuarios_atletas = Usuario.objects.filter(tipo_usuario='atleta').select_related('perfil_atleta')
    if query:
        # Filtrar por nombre, apellido, nivel o plan (búsqueda flexible)
        usuarios_atletas = usuarios_atletas.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(perfil_atleta__nivel__icontains=query) |  # Filtrar por nivel del atleta
            Q(plan__icontains=query)
        )
    paginator = Paginator(usuarios_atletas, 10)  # Paginación: 10 usuarios por página
    page_number = request.GET.get('page')
    usuarios_atletas = paginator.get_page(page_number)
    
    return render(request, 'listar_atletas.html', {
        'atletas': usuarios_atletas,
        'query': query
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
@login_required
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
@login_required
def borrar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, pk=rutina_id)
    clase_id = rutina.clase.id
    if request.method == 'POST':
        rutina.delete()
        messages.success(request, 'Rutina eliminada con éxito!')
        return redirect('detalle_rutinas', clase_id=clase_id)
    return render(request, 'borrar_rutina.html', {'rutina': rutina})

@login_required# views.py - Agregar al final del archivo
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