from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import TrainerProfile, TrainerStudent, LiveTrainingSession, LiveSet, TrainerFeedback, TrainerTraining, TrainerSet
from gym_tracker.trainings.models import Training, Set
from .decorators import trainer_required
from django.contrib.auth import get_user_model

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
    
    # Obtener entrenamientos recientes
    recent_trainings = Training.objects.filter(
        user=trainer_student.student
    ).order_by('-date')[:10]
    
    # Obtener feedback reciente
    recent_feedback = TrainerFeedback.objects.filter(
        trainer_student=trainer_student
    ).order_by('-created_at')[:5]
    
    context = {
        'trainer_student': trainer_student,
        'recent_trainings': recent_trainings,
        'recent_feedback': recent_feedback
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
    
    # Obtener sets completados
    completed_sets = LiveSet.objects.filter(
        session=session
    ).order_by('completed_at')
    
    context = {
        'session': session,
        'completed_sets': completed_sets
    }
    return render(request, 'trainers/live_session.html', context)

@login_required
@trainer_required
def start_live_session(request, student_id):
    """Iniciar una nueva sesión de entrenamiento en vivo."""
    if request.method == 'POST':
        trainer_student = get_object_or_404(
            TrainerStudent,
            trainer=request.user,
            student_id=student_id,
            active=True
        )
        
        training_id = request.POST.get('training_id')
        training = get_object_or_404(TrainerTraining, id=training_id, user=trainer_student.student)
        
        session = LiveTrainingSession.objects.create(
            training=training,
            trainer_student=trainer_student
        )
        
        return redirect('trainers:live_session', session_id=session.id)
    
    return redirect('trainers:student_detail', student_id=student_id)

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
        
        set_obj = get_object_or_404(Set, id=set_id)
        
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
    sessions = LiveTrainingSession.objects.filter(
        trainer_student__trainer=request.user
    ).select_related('trainer_student__student', 'training').order_by('-started_at')
    
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
    
    # Obtener todas las rutinas del estudiante
    trainings = TrainerTraining.objects.filter(
        user=trainer_student.student
    ).order_by('-date')
    
    context = {
        'trainer_student': trainer_student,
        'trainings': trainings
    }
    return render(request, 'trainers/student_trainings.html', context)

@login_required
@trainer_required
def training_detail(request, student_id, training_id):
    """Ver detalle de una rutina específica de un estudiante."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener la rutina específica
    training = get_object_or_404(
        TrainerTraining,
        id=training_id,
        user=trainer_student.student
    )
    
    # Obtener los sets de la rutina
    sets = TrainerSet.objects.filter(
        training=training
    ).order_by('order')
    
    context = {
        'trainer_student': trainer_student,
        'training': training,
        'sets': sets
    }
    return render(request, 'trainers/training_detail.html', context)

@login_required
@trainer_required
def create_training(request, student_id):
    """Crear una nueva rutina para un estudiante."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        
        if not name or not date:
            messages.error(request, 'El nombre y la fecha son obligatorios')
            return redirect('trainers:create_training', student_id=student_id)
        
        # Crear la nueva rutina
        training = TrainerTraining.objects.create(
            user=trainer_student.student,
            name=name,
            description=description,
            date=date,
            created_by=request.user
        )
        
        messages.success(request, f'Rutina "{name}" creada correctamente')
        return redirect('trainers:edit_training', student_id=student_id, training_id=training.id)
    
    context = {
        'trainer_student': trainer_student
    }
    return render(request, 'trainers/create_training.html', context)

@login_required
@trainer_required
def edit_training(request, student_id, training_id):
    """Editar una rutina específica de un estudiante."""
    # Verificar la relación entrenador-estudiante
    trainer_student = get_object_or_404(
        TrainerStudent,
        trainer=request.user,
        student_id=student_id,
        active=True
    )
    
    # Obtener la rutina a editar
    training = get_object_or_404(
        TrainerTraining,
        id=training_id,
        user=trainer_student.student
    )
    
    if request.method == 'POST':
        # Si se está añadiendo un nuevo set
        if 'add_set' in request.POST:
            exercise = request.POST.get('exercise')
            sets_count = request.POST.get('sets_count')
            reps = request.POST.get('reps')
            weight = request.POST.get('weight', None)
            notes = request.POST.get('notes', '')
            
            # Obtener el último orden
            last_order = TrainerSet.objects.filter(
                training=training
            ).order_by('-order').values_list('order', flat=True).first() or 0
            
            # Crear el nuevo set
            TrainerSet.objects.create(
                training=training,
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
                set_obj = TrainerSet.objects.get(id=set_id, training=training)
                exercise_name = set_obj.exercise
                set_obj.delete()
                messages.success(request, f'Ejercicio "{exercise_name}" eliminado correctamente')
            except TrainerSet.DoesNotExist:
                messages.error(request, 'El ejercicio no existe o no pertenece a esta rutina')
            
            return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
        
        # Si se están actualizando los datos básicos de la rutina
        else:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            date = request.POST.get('date')
            
            if not name or not date:
                messages.error(request, 'El nombre y la fecha son obligatorios')
                return redirect('trainers:edit_training', student_id=student_id, training_id=training_id)
            
            # Actualizar la rutina
            training.name = name
            training.description = description
            training.date = date
            training.save()
            
            messages.success(request, f'Rutina "{name}" actualizada correctamente')
            return redirect('trainers:training_detail', student_id=student_id, training_id=training_id)
    
    # Obtener los sets de la rutina
    sets = TrainerSet.objects.filter(
        training=training
    ).order_by('order')
    
    context = {
        'trainer_student': trainer_student,
        'training': training,
        'sets': sets
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
        
        # Copiar los sets
        sets = TrainerSet.objects.filter(training=source_training).order_by('order')
        for set_obj in sets:
            TrainerSet.objects.create(
                training=new_training,
                exercise=set_obj.exercise,
                weight=set_obj.weight,
                reps=set_obj.reps,
                sets_count=set_obj.sets_count,
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
