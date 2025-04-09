from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import TrainerProfile, TrainerStudent, LiveTrainingSession, LiveSet, TrainerFeedback, TrainerTraining, TrainerSet, TrainerTrainingDay
from gym_tracker.trainings.models import Training, Set
from .decorators import trainer_required
from django.contrib.auth import get_user_model
from gym_tracker.workouts.models import WeeklyRoutine
from gym_tracker.exercises.models import Exercise
from django.urls import reverse

@login_required
@trainer_required
def trainer_dashboard(request):
    """Dashboard principal del entrenador."""
    # Obtener los estudiantes asignados al entrenador
    students = TrainerStudent.objects.filter(
        trainer=request.user,
        active=True
    ).select_related('student', 'student__profile')
    
    # Obtener sesiones en vivo activas (incluyendo las iniciadas por estudiantes)
    active_sessions = LiveTrainingSession.objects.filter(
        Q(trainer_student__trainer=request.user) | Q(training__created_by=request.user),
        ended_at__isnull=True
    ).select_related(
        'trainer_student__student', 
        'training'
    ).order_by('-started_at')
    
    # Estadísticas básicas
    total_students = students.count()
    total_sessions = LiveTrainingSession.objects.filter(
        trainer_student__trainer=request.user
    ).count()
    active_sessions_count = active_sessions.count()
    
    context = {
        'title': 'Dashboard de Entrenador',
        'students': students,
        'active_sessions': active_sessions,
        'total_students': total_students,
        'total_sessions': total_sessions,
        'active_sessions_count': active_sessions_count
    }
    return render(request, 'trainers/dashboard.html', context)

@login_required
@trainer_required
def student_list(request):
    """Lista de estudiantes del entrenador."""
    # Obtener todos los estudiantes asignados al entrenador actual
    trainer_students = TrainerStudent.objects.filter(
        trainer=request.user,
        active=True
    ).select_related('student')
    
    context = {
        'title': 'Lista de Estudiantes',
        'trainer_students': trainer_students
    }
    return render(request, 'trainers/student_list.html', context)

@login_required
@trainer_required
def student_detail(request, student_id):
    """Detalle de un estudiante específico."""
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id
    )
    
    # Obtener entrenamientos recientes asignados al estudiante
    recent_trainings = TrainerTraining.objects.filter(
        user=trainer_student.student
    ).order_by('-date')[:5]
    
    # Obtener feedback reciente
    recent_feedback = TrainerFeedback.objects.filter(
        trainer_student=trainer_student
    ).order_by('-created_at')[:5]
    
    # Obtener entrenamientos completados
    completed_trainings = Training.objects.filter(
        user=trainer_student.student,
        completed=True
    ).order_by('-date')[:5]
    
    # Obtener rutinas semanales
    weekly_routines = WeeklyRoutine.objects.filter(
        user=trainer_student.student
    ).order_by('-created_at')[:5]
    
    context = {
        'trainer_student': trainer_student,
        'recent_trainings': recent_trainings,
        'recent_feedback': recent_feedback,
        'completed_trainings': completed_trainings,
        'weekly_routines': weekly_routines
    }
    return render(request, 'trainers/student_detail.html', context)

@login_required
@trainer_required
def live_session(request, session_id):
    """Vista de una sesión de entrenamiento en vivo."""
    session = get_object_or_404(
        LiveTrainingSession,
        id=session_id,
        trainer_student__trainer=request.user
    )
    
    # Obtener los días de entrenamiento de la sesión
    training_days = session.training.days.all()
    
    # Obtener todos los sets de todos los días
    all_sets = []
    for day in training_days:
        day_sets = day.sets.all().order_by('order')
        all_sets.extend(day_sets)
    
    # Si no hay sets, devolver un mensaje
    if not all_sets:
        messages.warning(request, "Esta sesión no tiene ejercicios configurados")
        return redirect('trainers:session_list')
    
    # Obtener los sets completados
    completed_sets = LiveSet.objects.filter(
        session=session
    ).select_related('set').order_by('-completed_at')
    
    # Obtener los IDs de los sets completados
    completed_set_ids = []
    for cs in completed_sets:
        # Solo añadir a IDs completados si todas las series están completadas
        set_complete_count = LiveSet.objects.filter(session=session, set=cs.set).count()
        if set_complete_count >= cs.set.sets_count and cs.set.id not in completed_set_ids:
            completed_set_ids.append(cs.set.id)
    
    # Determinar el set actual a mostrar
    current_set_index = request.GET.get('set', '1')
    try:
        current_set_index = int(current_set_index)
        if current_set_index < 1:
            current_set_index = 1
        elif current_set_index > len(all_sets):
            current_set_index = len(all_sets)
    except (ValueError, TypeError):
        current_set_index = 1
    
    # Obtener el set actual
    current_set = all_sets[current_set_index - 1]
    
    # Imprimir información para depuración
    print(f"Current Set ID: {current_set.id}, Exercise: {current_set.exercise}")
    print(f"Weight: {current_set.weight}")
    
    context = {
        'session': session,
        'completed_sets': completed_sets,
        'completed_set_ids': completed_set_ids,
        'current_set_index': current_set_index,
        'all_sets': all_sets,
        'current_set': current_set
    }
    return render(request, 'trainers/live_session.html', context)

@login_required
@trainer_required
def start_live_session(request, student_id):
    """Iniciar una nueva sesión de entrenamiento en vivo."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    if request.method == 'POST':
        routine_type = request.POST.get('routine_type')
        routine_id = request.POST.get('routine_id')
        
        if not routine_type or not routine_id:
            messages.error(request, 'Debes seleccionar una rutina para iniciar la sesión')
            return redirect('trainers:select_session_routine', student_id=student_id, session_id=0)
        
        # Crear sesión según el tipo de rutina seleccionada
        if routine_type == 'trainer':
            # Rutina asignada por el entrenador
            training = get_object_or_404(TrainerTraining, id=routine_id, user=trainer_student.student)
            
            # Verificar que la rutina tenga al menos un día con ejercicios
            if not training.days.exists():
                messages.error(request, 'La rutina seleccionada no tiene días configurados')
                return redirect('trainers:select_session_routine', student_id=student_id, session_id=0)
                
            session = LiveTrainingSession.objects.create(
                training=training,
                trainer_student=trainer_student
            )
            
            return redirect('trainers:live_session', session_id=session.id)
            
        elif routine_type == 'weekly':
            # Para rutinas semanales, redirigir a la selección de día específico
            try:
                routine_id = int(routine_id)
                # Verificar que la rutina existe
                WeeklyRoutine.objects.get(id=routine_id, user=trainer_student.student)
                return redirect('trainers:select_routine_day', 
                               routine_id=routine_id, 
                               session_id=0, 
                               student_id=student_id)
            except (ValueError, WeeklyRoutine.DoesNotExist):
                messages.error(request, f"La rutina asignada con ID {routine_id} no existe.")
                return redirect('trainers:select_session_routine', student_id=student_id, session_id=0)
        else:
            messages.error(request, 'Tipo de rutina no válido')
            return redirect('trainers:select_session_routine', student_id=student_id, session_id=0)
    
    # Si es una solicitud GET, redirigir a la página de selección de rutina
    return redirect('trainers:select_session_routine', student_id=student_id, session_id=0)

@login_required
@trainer_required
def select_session_routine(request, student_id, session_id):
    """Permite seleccionar una rutina para la sesión de entrenamiento."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener las rutinas del estudiante (rutinas semanales)
    student_weekly_routines = WeeklyRoutine.objects.filter(user=trainer_student.student)
    
    # Obtener las rutinas asignadas (TrainerTraining)
    student_trainer_routines = TrainerTraining.objects.filter(user=trainer_student.student)
    
    # Obtener todas las rutinas semanales disponibles en el sistema
    all_weekly_routines = WeeklyRoutine.objects.all().select_related('user')
    
    # Si hay una ID de rutina proporcionada
    routine_id = request.GET.get('routine_id')
    routine_type = request.GET.get('type', 'weekly')  # Por defecto, asumimos rutina semanal
    
    if routine_id:
        if routine_type == 'training':
            # Si es una rutina de entrenador, redirigimos a una vista específica
            # que use esa rutina directamente para la sesión
            return redirect('trainers:use_training_routine', 
                          training_id=routine_id, 
                          session_id=session_id,
                          student_id=student_id)
        else:
            # Si es una rutina semanal, continuamos con el flujo normal
            return redirect('trainers:select_routine_day', 
                          routine_id=routine_id, 
                          session_id=session_id,
                          student_id=student_id)
    
    context = {
        'trainer_student': trainer_student,
        'student_id': student_id,
        'session_id': session_id,
        'student_weekly_routines': student_weekly_routines,
        'student_trainer_routines': student_trainer_routines,
        'all_weekly_routines': all_weekly_routines,
    }
    return render(request, 'trainers/select_session_routine.html', context)

@login_required
@trainer_required
def save_live_set(request):
    """Guardar una serie durante el entrenamiento en vivo."""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        set_id = request.POST.get('set_id')
        
        try:
            session = get_object_or_404(
                LiveTrainingSession,
                id=session_id,
                trainer_student__trainer=request.user
            )
            
            # Obtener el set que está relacionado con training_day
            set_obj = get_object_or_404(
                TrainerSet, 
                id=set_id
            )
            
            # Procesar el peso asegurando que se acepte tanto coma como punto
            weight_str = request.POST.get('weight', '0')
            weight_str = weight_str.replace(',', '.')
            weight = float(weight_str)
            
            reps = int(request.POST.get('reps', 0))
            form_rating = int(request.POST.get('form_rating', 3))
            feedback = request.POST.get('feedback', '')
            
            # Contar el número de series ya completadas para este ejercicio
            completed_sets_count = LiveSet.objects.filter(
                session=session,
                set=set_obj
            ).count()
            
            # El número de serie será el siguiente
            set_number = completed_sets_count + 1
            
            # Verificar que no se hayan completado todas las series
            if set_number <= set_obj.sets_count:
                live_set = LiveSet.objects.create(
                    session=session,
                    set=set_obj,
                    completed_by=request.user,
                    weight=weight,
                    reps=reps,
                    trainer_feedback=feedback,
                    form_rating=form_rating,
                    set_number=set_number
                )
                
                # Indicar si se han completado todas las series
                all_completed = set_number >= set_obj.sets_count
                
                return JsonResponse({
                    'status': 'success', 
                    'set_id': live_set.id,
                    'set_number': set_number,
                    'all_completed': all_completed,
                    'total_sets': set_obj.sets_count
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya se han completado todas las series para este ejercicio'
                }, status=400)
                
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error en los datos: {str(e)}'
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

@login_required
@trainer_required
def end_session(request, session_id):
    """Finalizar una sesión de entrenamiento en vivo."""
    session = get_object_or_404(
        LiveTrainingSession,
        id=session_id,
        trainer_student__trainer=request.user
    )
    
    if request.method == 'POST':
        feedback = request.POST.get('feedback', '')
        rating = request.POST.get('rating')
        
        # Guardar feedback general
        TrainerFeedback.objects.create(
            trainer_student=session.trainer_student,
            training=session.training,
            feedback=feedback,
            rating=rating
        )
        
        # Finalizar sesión
        session.end_session()
        messages.success(request, 'Sesión finalizada correctamente')
        
        return redirect('trainers:student_detail', student_id=session.trainer_student.student.id)
    
    return redirect('trainers:live_session', session_id=session_id)

@login_required
@trainer_required
def session_list(request):
    """Lista de sesiones de entrenamiento del entrenador."""
    # Obtener todas las sesiones del entrenador con prefetch_related para optimizar consultas
    sessions = LiveTrainingSession.objects.filter(
        trainer_student__trainer=request.user
    ).select_related(
        'trainer_student__student', 
        'trainer_student__student__profile',
        'training'
    ).prefetch_related(
        'training__days',
        'training__days__sets'
    ).order_by('-started_at')
    
    context = {
        'sessions': sessions
    }
    return render(request, 'trainers/session_list.html', context)

@login_required
@trainer_required
def feedback_list(request):
    """Lista de retroalimentaciones dadas por el entrenador."""
    feedback = TrainerFeedback.objects.filter(
        trainer_student__trainer=request.user
    ).select_related('trainer_student__student', 'training').order_by('-created_at')
    
    context = {
        'feedback_list': feedback
    }
    return render(request, 'trainers/feedback_list.html', context)

@login_required
@trainer_required
def add_student(request):
    """Añadir un nuevo estudiante al entrenador."""
    if request.method == 'POST':
        student_email = request.POST.get('student_email', '')
        student_id = request.POST.get('student_id', '')
        notes = request.POST.get('notes', '')
        
        User = get_user_model()
        student = None
        
        # Intentar obtener el estudiante por ID o email
        try:
            if student_id:
                student = User.objects.get(id=student_id)
            elif student_email:
                student = User.objects.get(email=student_email)
            else:
                messages.error(request, 'Debes proporcionar un correo o seleccionar un usuario.')
                return redirect('trainers:student_list')
                
            # Verificar si ya existe la relación
            existing_relation = TrainerStudent.objects.filter(
                trainer=request.user,
                student=student
            ).first()
            
            if existing_relation:
                if not existing_relation.active:
                    # Reactivar la relación existente
                    existing_relation.active = True
                    existing_relation.end_date = None
                    existing_relation.notes = notes
                    existing_relation.save()
                    messages.success(request, f'¡Se ha reactivado la relación con {student.get_full_name() or student.username}!')
                else:
                    messages.warning(request, f'Este estudiante ya está asignado a tu perfil.')
            else:
                # Crear nueva relación
                TrainerStudent.objects.create(
                    trainer=request.user,
                    student=student,
                    notes=notes
                )
                messages.success(request, f'¡Se ha añadido a {student.get_full_name() or student.username} a tu lista de estudiantes!')
                
        except User.DoesNotExist:
            messages.error(request, f'No se encontró ningún usuario con el correo o ID proporcionado.')
        except Exception as e:
            messages.error(request, f'Error al añadir estudiante: {str(e)}')
    
    return redirect('trainers:student_list')

@login_required
@trainer_required
def get_student_trainings(request, student_id):
    """Obtener entrenamientos disponibles de un estudiante."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Verificar que el estudiante está asignado al entrenador
            trainer_student = get_object_or_404(
                TrainerStudent,
                trainer=request.user,
                student_id=student_id,
                active=True
            )
            
            # Obtener entrenamientos recientes del estudiante
            trainings = TrainerTraining.objects.filter(
                user=trainer_student.student
            ).order_by('-date')[:10]
            
            # Preparar datos para respuesta JSON
            training_list = [
                {'id': t.id, 'name': t.name, 'date': t.date.strftime('%d/%m/%Y')}
                for t in trainings
            ]
            
            return JsonResponse({'status': 'success', 'trainings': training_list})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud no válida'}, status=400)

@login_required
@trainer_required
def search_users(request):
    """Buscar usuarios disponibles para añadir como estudiantes."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        User = get_user_model()
        
        # Obtener usuarios ya asignados al entrenador
        assigned_students = TrainerStudent.objects.filter(
            trainer=request.user,
            active=True
        ).values_list('student_id', flat=True)
        
        # Buscar usuarios que coincidan con el término y no estén ya asignados
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) | 
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(
                id__in=assigned_students
            ).exclude(
                id=request.user.id  # Excluir al propio entrenador
            )[:10]  # Limitar a 10 resultados
        else:
            # Si no hay término de búsqueda, mostrar los 10 más recientes no asignados
            users = User.objects.exclude(
                id__in=assigned_students
            ).exclude(
                id=request.user.id
            ).order_by('-date_joined')[:10]
        
        # Preparar datos para respuesta JSON
        user_list = [
            {
                'id': user.id, 
                'username': user.username,
                'email': user.email,
                'name': user.get_full_name() or user.username
            }
            for user in users
        ]
        
        return JsonResponse({'status': 'success', 'users': user_list})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud no válida'}, status=400)

@login_required
@trainer_required
def student_trainings(request, student_id):
    """Ver todas las rutinas de un estudiante."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener todas las rutinas asignadas del estudiante
    trainer_trainings = TrainerTraining.objects.filter(
        user=trainer_student.student
    ).order_by('-date')
    
    # Obtener rutinas semanales del estudiante
    weekly_routines = WeeklyRoutine.objects.filter(
        user=trainer_student.student
    ).order_by('-created_at')
    
    context = {
        'trainer_student': trainer_student,
        'trainer_trainings': trainer_trainings,
        'weekly_routines': weekly_routines
    }
    return render(request, 'trainers/student_trainings.html', context)

@login_required
@trainer_required
def training_detail(request, student_id, training_id):
    """Ver detalles de una rutina específica."""
    trainer = request.user
    trainer_student = get_object_or_404(TrainerStudent, trainer=trainer, student_id=student_id)
    training = get_object_or_404(TrainerTraining, id=training_id, user=trainer_student.student)
    
    # Obtener los días de entrenamiento
    training_days = training.days.all()  # El orden ya está definido en el modelo
    
    # Crear un diccionario para almacenar los ejercicios por día
    days_with_sets = {}
    for day in training_days:
        sets = TrainerSet.objects.filter(training_day=day).order_by('order')
        days_with_sets[day] = sets
    
    context = {
        'trainer_student': trainer_student,
        'training': training,
        'days_with_sets': days_with_sets
    }
    
    return render(request, 'trainers/training_detail.html', context)

@login_required
@trainer_required
def create_training(request, student_id):
    """Crear una nueva rutina para un estudiante."""
    trainer = request.user
    trainer_student = get_object_or_404(TrainerStudent, trainer=trainer, student_id=student_id)
    
    # Definir días de la semana para el formulario
    days_of_week = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    form_errors = []
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        date = request.POST.get('date', '')
        selected_days = request.POST.getlist('days', [])
        
        # Validar datos
        if not name:
            form_errors.append('El nombre de la rutina es obligatorio.')
        if not date:
            form_errors.append('La fecha de inicio es obligatoria.')
        if not selected_days:
            form_errors.append('Debes seleccionar al menos un día de la semana.')
        
        # Si no hay errores, crear la rutina
        if not form_errors:
            training = TrainerTraining.objects.create(
                name=name,
                date=date,
                user=trainer_student.student,
                created_by=trainer
            )
            
            # Crear los días de entrenamiento
            for day in selected_days:
                TrainerTrainingDay.objects.create(
                    training=training,
                    day_of_week=day
                )
            
            messages.success(request, 'Rutina creada correctamente!')
            return redirect('trainers:edit_training', student_id=student_id, training_id=training.id)
    
    context = {
        'trainer_student': trainer_student,
        'days_of_week': days_of_week,
        'form_errors': form_errors
    }
    
    return render(request, 'trainers/create_training.html', context)

@login_required
@trainer_required
def edit_training(request, student_id, training_id):
    """Editar una rutina específica de un estudiante."""
    trainer = request.user
    trainer_student = get_object_or_404(TrainerStudent, trainer=trainer, student_id=student_id)
    training = get_object_or_404(TrainerTraining, id=training_id, user=trainer_student.student)
    
    # Definir días de la semana para el formulario
    days_of_week = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    # Obtener días seleccionados
    selected_days = [day.day_of_week for day in training.days.all()]
    
    # Obtener todos los días con sus ejercicios
    training_days = training.days.all()
    days_with_sets = {}
    
    for day in training_days:
        days_with_sets[day] = TrainerSet.objects.filter(training_day=day).order_by('order')
    
    # Obtener todos los ejercicios activos de la base de datos
    all_exercises = Exercise.objects.filter(is_active=True).order_by('muscle_group', 'name')
    
    # Depuración: contar ejercicios por grupo muscular
    print(f"Total de ejercicios: {all_exercises.count()}")
    for group, label in Exercise.MUSCLE_GROUPS:
        count = all_exercises.filter(muscle_group=group).count()
        print(f"  - {label} ({group}): {count} ejercicios")
    
    # Verificar específicamente los ejercicios de pecho
    chest_exercises = all_exercises.filter(muscle_group='chest')
    print(f"Ejercicios de pecho: {chest_exercises.count()}")
    for ex in chest_exercises:
        print(f"  - ID: {ex.id}, Nombre: {ex.name}, Grupo: {ex.muscle_group}")

    if request.method == 'POST':
        # Si se está añadiendo un nuevo set
        if 'add_set' in request.POST:
            day_id = request.POST.get('day_id')
            exercise_id = request.POST.get('exercise')
            sets_count = request.POST.get('sets_count', 4)
            reps = request.POST.get('reps')
            weight = request.POST.get('weight', None)
            notes = request.POST.get('notes', '')
            
            # Verificar que existe el día
            training_day = get_object_or_404(TrainerTrainingDay, id=day_id, training=training)
            
            # Obtener el ejercicio por ID
            exercise = get_object_or_404(Exercise, id=exercise_id)
            
            # Obtener el último orden
            last_order = TrainerSet.objects.filter(
                training_day=training_day
            ).order_by('-order').values_list('order', flat=True).first() or 0
            
            # Crear el nuevo set
            TrainerSet.objects.create(
                training_day=training_day,
                exercise=exercise,
                sets_count=sets_count,
                reps=reps,
                weight=weight if weight and weight.strip() else None,
                notes=notes,
                order=last_order + 1
            )
            
            messages.success(request, f'Ejercicio "{exercise.name}" añadido correctamente')
            # Redirigir a la misma página con un parámetro para mantener activa la pestaña del día donde se agregó el ejercicio
            base_url = reverse('trainers:edit_training', kwargs={'student_id': student_id, 'training_id': training_id})
            return redirect(f'{base_url}?active_day={day_id}')
        
        # Si se está eliminando un set
        elif 'delete_set' in request.POST:
            set_id = request.POST.get('set_id')
            day_id = request.POST.get('day_id') # Recuperamos el day_id
            try:
                set_obj = TrainerSet.objects.get(id=set_id, training_day__training=training)
                # Guardar el ID del día antes de eliminar el set
                day_id = set_obj.training_day.id
                exercise_name = set_obj.exercise.name
                set_obj.delete()
                messages.success(request, f'Ejercicio "{exercise_name}" eliminado correctamente')
            except TrainerSet.DoesNotExist:
                messages.error(request, 'El ejercicio no existe o no pertenece a esta rutina')
            
            # Si tenemos el ID del día, redirigir manteniendo activa esa pestaña
            if day_id:
                base_url = reverse('trainers:edit_training', kwargs={'student_id': student_id, 'training_id': training_id})
                return redirect(f'{base_url}?active_day={day_id}')
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
        
        # Si se están actualizando los datos básicos de la rutina
        elif 'update_training' in request.POST:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            date = request.POST.get('date')
            selected_days = request.POST.getlist('days')
            
            if not name or not date:
                messages.error(request, 'El nombre y la fecha son obligatorios')
                return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
                
            if not selected_days:
                messages.error(request, 'Debes seleccionar al menos un día de la semana')
                return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
            
            # Actualizar la rutina
            training.name = name
            training.description = description
            training.date = date
            training.save()
            
            # Actualizar los días de entrenamiento
            current_days = set(training.days.values_list('day_of_week', flat=True))
            selected_days_set = set(selected_days)
            
            # Eliminar días que ya no están seleccionados
            days_to_remove = current_days - selected_days_set
            if days_to_remove:
                TrainerTrainingDay.objects.filter(training=training, day_of_week__in=days_to_remove).delete()
            
            # Añadir nuevos días seleccionados
            days_to_add = selected_days_set - current_days
            for day in days_to_add:
                TrainerTrainingDay.objects.create(training=training, day_of_week=day)
            
            messages.success(request, 'Información actualizada correctamente')
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
            
        # Si se está actualizando el enfoque de un día
        elif 'update_focus' in request.POST:
            day_id = request.POST.get('day_id')
            focus = request.POST.get('focus', '')
            muscles = request.POST.getlist('muscles', [])
            
            try:
                day = TrainerTrainingDay.objects.get(id=day_id, training=training)
                
                # Si hay músculos seleccionados, incluirlos en el enfoque
                if muscles:
                    # Usar el enfoque ingresado manualmente o generar uno basado en los músculos
                    if not focus or focus.strip() == '':
                        focus = ', '.join(muscles)
                
                day.focus = focus
                day.save()
                messages.success(request, f'Enfoque actualizado para {day.day_of_week}')
            except TrainerTrainingDay.DoesNotExist:
                messages.error(request, 'El día seleccionado no existe')
            
            # Redirigir a la misma página con un parámetro para mantener activa la pestaña del día actualizado
            base_url = reverse('trainers:edit_training', kwargs={'student_id': student_id, 'training_id': training_id})
            return redirect(f'{base_url}?active_day={day_id}')
        
        # Si se está eliminando un ejercicio
        elif 'delete_exercise' in request.POST:
            exercise_id = request.POST.get('exercise_id')
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                # Verificar si el ejercicio está en uso
                if TrainerSet.objects.filter(exercise=exercise).exists():
                    # Si está en uso, marcar como inactivo
                    exercise.soft_delete()
                    messages.success(request, f'Ejercicio "{exercise.name}" marcado como inactivo')
                else:
                    # Si no está en uso, eliminar completamente
                    exercise.delete()
                    messages.success(request, f'Ejercicio "{exercise.name}" eliminado correctamente')
            except Exercise.DoesNotExist:
                messages.error(request, 'El ejercicio no existe')
            
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
    
    # Obtener el día activo de la URL (si existe)
    active_day = request.GET.get('active_day')
    
    context = {
        'trainer_student': trainer_student,
        'training': training,
        'days_of_week': days_of_week,
        'selected_days': selected_days,
        'days_with_sets': days_with_sets,
        'all_exercises': all_exercises,
        'active_day': active_day,  # Pasar el día activo al contexto
    }
    
    return render(request, 'trainers/edit_training.html', context)

@login_required
@trainer_required
def copy_training(request, student_id, training_id):
    """Copiar una rutina existente."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener la rutina a copiar
    source_training = get_object_or_404(
        TrainerTraining,
        id=training_id
    )
    
    if request.method == 'POST':
        name = request.POST.get('name', f"Copia de {source_training.name}")
        date = request.POST.get('date')
        
        if not date:
            messages.error(request, 'La fecha es obligatoria')
            return redirect('trainers:copy_training', student_id=student_id, training_id=training_id)
        
        # Crear la nueva rutina
        new_training = TrainerTraining.objects.create(
            user=trainer_student.student,
            name=name,
            description=source_training.description,
            date=date,
            created_by=request.user
        )
        
        # Copiar los días y sus sets
        for day in source_training.days.all():
            # Crear nuevo día
            new_day = TrainerTrainingDay.objects.create(
                training=new_training,
                day_of_week=day.day_of_week,
                focus=day.focus
            )
            
            # Copiar sets del día
            for set_obj in day.sets.all():
                TrainerSet.objects.create(
                    training_day=new_day,
                    exercise=set_obj.exercise,
                    sets_count=set_obj.sets_count,
                    reps=set_obj.reps,
                    weight=set_obj.weight,
                    notes=set_obj.notes,
                    order=set_obj.order
                )
        
        messages.success(request, f'Rutina "{new_training.name}" creada correctamente')
        return redirect('trainers:edit_training', student_id=student_id, training_id=new_training.id)
    
    context = {
        'trainer_student': trainer_student,
        'source_training': source_training
    }
    return render(request, 'trainers/copy_training.html', context)

@login_required
@trainer_required
def delete_training(request, student_id, training_id):
    """Eliminar una rutina existente."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener la rutina
    training = get_object_or_404(
        TrainerTraining,
        id=training_id,
        user=trainer_student.student
    )
    
    if request.method == 'POST':
        training_name = training.name
        training.delete()
        messages.success(request, f'Rutina "{training_name}" eliminada correctamente')
        return redirect('trainers:student_trainings', student_id=student_id)
    
    context = {
        'trainer_student': trainer_student,
        'training': training
    }
    return render(request, 'trainers/delete_training.html', context)

@login_required
@trainer_required
def select_routine_day(request, routine_id, session_id, student_id):
    """Permite seleccionar un día específico de una rutina semanal para una sesión."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Verificar si la rutina existe
    try:
        routine_id = int(routine_id)
        # Intentar obtener la rutina por ID
        try:
            routine = WeeklyRoutine.objects.get(id=routine_id)
        except WeeklyRoutine.DoesNotExist:
            # Si no existe, intentar buscar por nombre si la rutina se llama "Fer Marzo 2025"
            try:
                routine = WeeklyRoutine.objects.get(name__icontains="Fer Marzo")
                messages.info(request, f"Rutina con ID {routine_id} no encontrada. Usando rutina '{routine.name}' (ID: {routine.id}).")
            except WeeklyRoutine.DoesNotExist:
                # Si tampoco hay ninguna rutina con ese nombre, mostrar mensaje de error
                messages.error(request, f"La rutina con ID {routine_id} no existe y no se encontró una rutina con nombre similar a 'Fer Marzo 2025'.")
                return redirect('trainers:select_session_routine', student_id=student_id, session_id=session_id)
    except ValueError:
        messages.error(request, f"ID de rutina inválido: {routine_id}")
        return redirect('trainers:select_session_routine', student_id=student_id, session_id=session_id)
    
    # Si se envía el formulario con un día seleccionado
    if request.method == 'POST':
        day_id = request.POST.get('day_id')
        
        if not day_id:
            messages.error(request, 'Debes seleccionar un día de entrenamiento')
            return redirect('trainers:select_routine_day', routine_id=routine.id, session_id=session_id, student_id=student_id)
        
        # Obtener el día de la rutina
        routine_day = get_object_or_404(routine.days.all(), id=day_id)
        
        # Crear un TrainerTraining temporal basado en la rutina semanal
        today = timezone.now().date()
        training = TrainerTraining.objects.create(
            user=trainer_student.student,
            created_by=request.user,
            name=f"Sesión: {routine.name} - {routine_day.day_of_week}",
            description=f"Sesión basada en la rutina '{routine.name}', día {routine_day.day_of_week}",
            date=today
        )
        
        # Crear el día de entrenamiento
        training_day = TrainerTrainingDay.objects.create(
            training=training,
            day_of_week=routine_day.day_of_week,
            focus=routine_day.focus
        )
        
        # Copiar los ejercicios de la rutina al entrenamiento temporal
        for i, exercise in enumerate(routine_day.exercises.all()):
            # Obtener el objeto Exercise en lugar de solo usar el nombre
            try:
                # Intentar buscar el ejercicio por nombre
                exercise_obj = Exercise.objects.get(name=exercise.exercise.name)
            except Exercise.DoesNotExist:
                # Si no existe, crear el ejercicio
                exercise_obj = Exercise.objects.create(
                    name=exercise.exercise.name,
                    description=f"Ejercicio importado desde rutina: {routine.name}"
                )
                
            TrainerSet.objects.create(
                training_day=training_day,
                exercise=exercise_obj,  # Usar el objeto de ejercicio
                sets_count=exercise.sets,
                reps=exercise.reps,
                weight=exercise.weight,
                notes=exercise.notes,
                order=i + 1
            )
        
        # Crear la sesión con el entrenamiento creado
        session = LiveTrainingSession.objects.create(
            training=training,
            trainer_student=trainer_student
        )
        
        messages.success(request, f'Sesión iniciada para {routine.name} - {routine_day.day_of_week}')
        return redirect('trainers:live_session', session_id=session.id)
    
    # Mostrar la página para seleccionar un día
    context = {
        'routine': routine,
        'trainer_student': trainer_student,
        'session_id': session_id,
        'student_id': student_id
    }
    
    return render(request, 'trainers/select_routine_day.html', context)

@login_required
def student_live_session(request, session_id):
    """Vista de una sesión de entrenamiento en vivo para estudiantes."""
    # Obtener la sesión en vivo, verificando que el estudiante sea parte de ella
    session = get_object_or_404(
        LiveTrainingSession,
        id=session_id,
        trainer_student__student=request.user,
        status='active',
        ended_at__isnull=True
    )
    
    # Obtener los días de entrenamiento de la sesión
    training_days = session.training.days.all()
    
    # Obtener todos los sets de todos los días
    all_sets = []
    for day in training_days:
        day_sets = day.sets.all().order_by('order')
        all_sets.extend(day_sets)
    
    # Si no hay sets, devolver un mensaje
    if not all_sets:
        messages.warning(request, "Esta sesión no tiene ejercicios configurados")
        return redirect('trainings:dashboard')
    
    # Obtener los sets completados
    completed_sets = LiveSet.objects.filter(
        session=session
    ).select_related('set').order_by('-completed_at')
    
    # Obtener los IDs de los sets completados
    completed_set_ids = []
    
    # Crear un diccionario para almacenar el último peso y reps por ejercicio y por set_id
    # Esto permite conservar valores entre series del mismo ejercicio
    last_weights_by_exercise = {}
    last_reps_by_exercise = {}
    last_weights_by_set = {}
    last_reps_by_set = {}
    
    for cs in completed_sets:
        # Añadir a IDs completados solo si todas las series están completadas
        set_complete_count = LiveSet.objects.filter(session=session, set=cs.set).count()
        if set_complete_count >= cs.set.sets_count and cs.set.id not in completed_set_ids:
            completed_set_ids.append(cs.set.id)
        
        # Guardar el último peso y repeticiones por ejercicio
        exercise_key = None
        if hasattr(cs.set.exercise, 'name'):
            exercise_key = cs.set.exercise.name
        else:
            exercise_key = cs.set.exercise
            
        # Almacenar por ejercicio (para usar entre diferentes ocurrencias del mismo ejercicio)
        if exercise_key not in last_weights_by_exercise or cs.completed_at > last_weights_by_exercise[exercise_key]['time']:
            last_weights_by_exercise[exercise_key] = {'weight': cs.weight, 'time': cs.completed_at}
            last_reps_by_exercise[exercise_key] = {'reps': cs.reps, 'time': cs.completed_at}
        
        # Almacenar por set_id (para usar entre series del mismo ejercicio específico)
        set_id = cs.set.id
        if set_id not in last_weights_by_set or cs.completed_at > last_weights_by_set[set_id]['time']:
            last_weights_by_set[set_id] = {'weight': cs.weight, 'time': cs.completed_at}
            last_reps_by_set[set_id] = {'reps': cs.reps, 'time': cs.completed_at}
    
    # Determinar el set actual a mostrar
    current_set_index = request.GET.get('set', '1')
    try:
        current_set_index = int(current_set_index)
        if current_set_index < 1:
            current_set_index = 1
        elif current_set_index > len(all_sets):
            current_set_index = len(all_sets)
    except (ValueError, TypeError):
        current_set_index = 1
    
    # Ajustar all_sets para mostrar el ejercicio actual primero
    current_set = all_sets[current_set_index - 1]
    
    # GARANTIZAR que siempre hay un peso original disponible
    current_set.original_weight = current_set.weight
    current_set.original_reps = current_set.reps
    
    # Verificar primero si hay un valor anterior del mismo ejercicio específico (mismo set_id)
    if current_set.id in last_weights_by_set:
        current_set.last_used_weight = last_weights_by_set[current_set.id]['weight']
    
    if current_set.id in last_reps_by_set:
        current_set.last_used_reps = last_reps_by_set[current_set.id]['reps']
    else:
        # Si no hay un valor para el mismo ejercicio específico, buscar por nombre de ejercicio
        exercise_key = None
        if hasattr(current_set.exercise, 'name'):
            exercise_key = current_set.exercise.name
        else:
            exercise_key = current_set.exercise
            
        if exercise_key in last_weights_by_exercise:
            # Solo usar estos valores si no se han encontrado valores por set_id específico
            if not hasattr(current_set, 'last_used_weight'):
                current_set.last_used_weight = last_weights_by_exercise[exercise_key]['weight']
        
        if exercise_key in last_reps_by_exercise:
            if not hasattr(current_set, 'last_used_reps'):
                current_set.last_used_reps = last_reps_by_exercise[exercise_key]['reps']
    
    context = {
        'session': session,
        'completed_sets': completed_sets,
        'completed_set_ids': completed_set_ids,
        'current_set_index': current_set_index,
        'all_sets': all_sets,
        'is_student': True,
        'current_set': current_set,
        'session_start_time': session.started_at.isoformat()
    }
    return render(request, 'trainers/student_live_session.html', context)

@login_required
@trainer_required
def use_training_routine(request, training_id, session_id, student_id):
    """Usa directamente una rutina de entrenador para una sesión en vivo."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Verificar si la rutina existe
    try:
        training_id = int(training_id)
        # Buscar la rutina de entrenador
        try:
            training = TrainerTraining.objects.get(id=training_id)
        except TrainerTraining.DoesNotExist:
            # Si no existe con ese ID exacto, intentar buscar por nombre
            try:
                training = TrainerTraining.objects.filter(name__icontains="Fer Marzo").first()
                if training:
                    messages.info(request, f"Rutina con ID {training_id} no encontrada. Usando rutina '{training.name}' (ID: {training.id}).")
                else:
                    messages.error(request, f"No se encontró ninguna rutina con ID {training_id} o con nombre similar a 'Fer Marzo'.")
                    return redirect('trainers:select_session_routine', student_id=student_id, session_id=session_id)
            except Exception as e:
                messages.error(request, f"Error al buscar rutina: {e}")
                return redirect('trainers:select_session_routine', student_id=student_id, session_id=session_id)
    except ValueError:
        messages.error(request, f"ID de rutina inválido: {training_id}")
        return redirect('trainers:select_session_routine', student_id=student_id, session_id=session_id)
    
    # Crear la sesión con el entrenamiento existente
    session = LiveTrainingSession.objects.create(
        training=training,
        trainer_student=trainer_student
    )
    
    messages.success(request, f'Sesión iniciada para la rutina {training.name}')
    return redirect('trainers:live_session', session_id=session.id)

@login_required
@trainer_required
def edit_trainer_set(request, set_id):
    """Vista para editar un ejercicio específico (TrainerSet) dentro de una rutina."""
    set_obj = get_object_or_404(TrainerSet, id=set_id)
    # Asegurarnos de que el entrenador actual es el que creó la rutina original
    if request.user != set_obj.training_day.training.created_by:
        messages.error(request, "No tienes permiso para editar este ejercicio.")
        # Redirigir a una página segura, p.ej., el dashboard del entrenador
        return redirect('trainers:dashboard') 

    training = set_obj.training_day.training
    student = training.user

    if request.method == 'POST':
        # Procesar formulario
        sets_count_str = request.POST.get('sets_count')
        reps = request.POST.get('reps')
        weight_str = request.POST.get('weight')
        notes = request.POST.get('notes', '')

        try:
            set_obj.sets_count = int(sets_count_str) if sets_count_str else 1
            set_obj.reps = reps
            set_obj.notes = notes
            
            if weight_str and weight_str.strip():
                # Reemplazar coma por punto para conversión a float
                weight_str = weight_str.replace(',', '.')
                set_obj.weight = float(weight_str)
            else:
                set_obj.weight = None
                
            set_obj.save()
            messages.success(request, f'Ejercicio "{set_obj.exercise.name}" actualizado correctamente.')
            
            # Redirigir de vuelta a la página de edición de la rutina, manteniendo la pestaña activa
            base_url = reverse('trainers:edit_training', kwargs={'student_id': student.id, 'training_id': training.id})
            return redirect(f'{base_url}?active_day={set_obj.training_day.id}')

        except (ValueError, TypeError) as e:
            messages.error(request, f'Error al actualizar el ejercicio: Datos inválidos. {e}')
        except Exception as e:
             messages.error(request, f'Ocurrió un error inesperado: {e}')
             
        # Si hay error, volver a mostrar el formulario con los datos ingresados
        context = {
            'set_obj': set_obj,
            'student': student,
            'training': training,
            'sets_count': sets_count_str, # Pasar los valores POST para repoblar
            'reps': reps,
            'weight': weight_str,
            'notes': notes,
        }
        return render(request, 'trainers/edit_trainer_set.html', context)

    # Si es GET, mostrar formulario con datos actuales
    context = {
        'set_obj': set_obj,
        'student': student,
        'training': training,
        'sets_count': set_obj.sets_count,
        'reps': set_obj.reps,
        'weight': set_obj.weight,
        'notes': set_obj.notes,
    }
    return render(request, 'trainers/edit_trainer_set.html', context)
