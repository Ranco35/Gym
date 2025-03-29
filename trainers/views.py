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

@login_required
@trainer_required
def trainer_dashboard(request):
    """Dashboard principal del entrenador."""
    # Mostrar información básica sin necesidad de consultas complejas
    context = {
        'title': 'Dashboard de Entrenador',
        'message': 'Bienvenido al área de entrenador'
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
    
    # Obtener los días de entrenamiento
    training_days = session.training.days.all()
    
    # Estructura para almacenar sets por día
    days_with_sets = {}
    completed_sets = {}
    
    for day in training_days:
        # Obtener los sets de cada día
        sets = TrainerSet.objects.filter(training_day=day).order_by('order')
        days_with_sets[day] = sets
        
        # Obtener los sets completados para cada día
        day_completed_sets = {}
        for set_obj in sets:
            live_sets = LiveSet.objects.filter(
                session=session, 
                set=set_obj
            ).order_by('completed_at')
            if live_sets.exists():
                day_completed_sets[set_obj.id] = live_sets
                
        completed_sets[day.id] = day_completed_sets
    
    context = {
        'session': session,
        'days_with_sets': days_with_sets,
        'completed_sets': completed_sets
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
            return redirect('trainers:select_session_routine', student_id=student_id)
        
        # Crear sesión según el tipo de rutina seleccionada
        if routine_type == 'trainer':
            # Rutina asignada por el entrenador
            training = get_object_or_404(TrainerTraining, id=routine_id, user=trainer_student.student)
            
            # Verificar que la rutina tenga al menos un día con ejercicios
            if not training.days.exists():
                messages.error(request, 'La rutina seleccionada no tiene días configurados')
                return redirect('trainers:select_session_routine', student_id=student_id)
                
            session = LiveTrainingSession.objects.create(
                training=training,
                trainer_student=trainer_student
            )
            
        elif routine_type == 'weekly':
            # Rutina semanal del estudiante
            routine = get_object_or_404(WeeklyRoutine, id=routine_id, user=trainer_student.student)
            
            # Crear un TrainerTraining temporal basado en la rutina semanal
            today = timezone.now().date()
            training = TrainerTraining.objects.create(
                user=trainer_student.student,
                created_by=request.user,
                name=f"Sesión en vivo: {routine.name}",
                description=f"Sesión basada en la rutina semanal '{routine.name}'",
                date=today
            )
            
            # Obtener el día actual de la semana en español
            days_map = {
                0: 'Lunes',
                1: 'Martes',
                2: 'Miércoles',
                3: 'Jueves',
                4: 'Viernes',
                5: 'Sábado',
                6: 'Domingo'
            }
            current_day_name = days_map.get(today.weekday())
            
            # Intentar obtener los ejercicios del día actual, si no hay, usar cualquier día
            routine_day = routine.days.filter(day_of_week=current_day_name).first()
            if not routine_day:
                routine_day = routine.days.first()
            
            if routine_day:
                # Crear el día de entrenamiento
                training_day = TrainerTrainingDay.objects.create(
                    training=training,
                    day_of_week=routine_day.day_of_week,
                    focus=routine_day.focus
                )
                
                # Copiar los ejercicios de la rutina al entrenamiento temporal
                for i, exercise in enumerate(routine_day.exercises.all()):
                    TrainerSet.objects.create(
                        training_day=training_day,
                        exercise=exercise.exercise.name,
                        sets_count=exercise.sets,
                        reps=exercise.reps,
                        weight=exercise.weight,
                        notes=exercise.notes,
                        order=i+1
                    )
            
            # Crear la sesión con el entrenamiento temporal
            session = LiveTrainingSession.objects.create(
                training=training,
                trainer_student=trainer_student
            )
        else:
            messages.error(request, 'Tipo de rutina no válido')
            return redirect('trainers:select_session_routine', student_id=student_id)
            
        return redirect('trainers:live_session', session_id=session.id)
    
    # Si es una solicitud GET, redirigir a la página de selección de rutina
    return redirect('trainers:select_session_routine', student_id=student_id)

@login_required
@trainer_required
def select_session_routine(request, student_id):
    """Seleccionar rutina para iniciar una sesión en vivo."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener las rutinas asignadas por el entrenador
    trainer_trainings = TrainerTraining.objects.filter(
        user=trainer_student.student
    ).order_by('-date')[:10]
    
    # Obtener las rutinas semanales del estudiante
    weekly_routines = WeeklyRoutine.objects.filter(
        user=trainer_student.student
    ).order_by('-created_at')
    
    context = {
        'trainer_student': trainer_student,
        'trainer_trainings': trainer_trainings,
        'weekly_routines': weekly_routines
    }
    
    return render(request, 'trainers/select_session_routine.html', context)

@login_required
@trainer_required
def save_live_set(request):
    """Guardar una serie durante el entrenamiento en vivo."""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        set_id = request.POST.get('set_id')
        weight = request.POST.get('weight')
        reps = request.POST.get('reps')
        feedback = request.POST.get('feedback', '')
        form_rating = request.POST.get('form_rating')
        
        session = get_object_or_404(
            LiveTrainingSession,
            id=session_id,
            trainer_student__trainer=request.user
        )
        
        # Obtener el set que ahora está relacionado con training_day en lugar de training directamente
        set_obj = get_object_or_404(
            TrainerSet, 
            id=set_id, 
            training_day__training=session.training
        )
        
        live_set = LiveSet.objects.create(
            session=session,
            set=set_obj,
            completed_by=request.user,
            weight=weight,
            reps=reps,
            trainer_feedback=feedback,
            form_rating=form_rating
        )
        
        return JsonResponse({'status': 'success', 'set_id': live_set.id})
    
    return JsonResponse({'status': 'error'}, status=400)

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
        'trainer_student__student__userprofile',
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
    
    # Obtener todos los ejercicios de la base de datos
    all_exercises = Exercise.objects.all().order_by('category', 'name')

    if request.method == 'POST':
        # Si se está añadiendo un nuevo set
        if 'add_set' in request.POST:
            day_id = request.POST.get('day_id')
            exercise = request.POST.get('exercise')
            sets_count = request.POST.get('sets_count')
            reps = request.POST.get('reps')
            weight = request.POST.get('weight', None)
            notes = request.POST.get('notes', '')
            
            # Verificar que existe el día
            training_day = get_object_or_404(TrainerTrainingDay, id=day_id, training=training)
            
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
            
            messages.success(request, f'Ejercicio "{exercise}" añadido correctamente')
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
        
        # Si se está eliminando un set
        elif 'delete_set' in request.POST:
            set_id = request.POST.get('set_id')
            try:
                set_obj = TrainerSet.objects.get(id=set_id, training_day__training=training)
                exercise_name = set_obj.exercise
                set_obj.delete()
                messages.success(request, f'Ejercicio "{exercise_name}" eliminado correctamente')
            except TrainerSet.DoesNotExist:
                messages.error(request, 'El ejercicio no existe o no pertenece a esta rutina')
            
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
            
            try:
                day = TrainerTrainingDay.objects.get(id=day_id, training=training)
                day.focus = focus
                day.save()
                messages.success(request, f'Enfoque actualizado para {day.day_of_week}')
            except TrainerTrainingDay.DoesNotExist:
                messages.error(request, 'El día seleccionado no existe')
                
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
    
    context = {
        'trainer_student': trainer_student,
        'training': training,
        'days_of_week': days_of_week,
        'selected_days': selected_days,
        'days_with_sets': days_with_sets,
        'all_exercises': all_exercises,
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
