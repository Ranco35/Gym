from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from ..models import Training, Set
from ..forms import SetForm
from gym_tracker.workouts.models import WeeklyRoutine as Routine, RoutineDay, RoutineExercise
from trainers.models import LiveTrainingSession, TrainerStudent, TrainerTraining, TrainerTrainingDay, TrainerSet

@login_required
def execute_training(request, routine_id, day_id):
    """
    Ejecuta un entrenamiento basado en una rutina y un día específico.
    """
    try:
        # Intentar obtener como rutina personal
        routine = Routine.objects.get(id=routine_id, user=request.user)
        day = RoutineDay.objects.get(id=day_id, routine=routine)
        exercises = RoutineExercise.objects.filter(routine_day=day).order_by('order')
        is_assigned = False
    except (Routine.DoesNotExist, RoutineDay.DoesNotExist):
        # Intentar obtener como rutina asignada por entrenador
        try:
            routine = TrainerTraining.objects.get(id=routine_id, user=request.user)
            day = TrainerTrainingDay.objects.get(id=day_id, training=routine)
            exercises = day.sets.all().order_by('order')
            is_assigned = True
        except (TrainerTraining.DoesNotExist, TrainerTrainingDay.DoesNotExist):
            messages.error(request, "Rutina o día no encontrado.")
            return redirect('trainings:training-list')
    
    # Obtener o crear el entrenamiento actual
    training = Training.objects.filter(
        user=request.user,
        date=timezone.now().date(),
        day_of_week=day.day_of_week,
        completed=False
    ).first()
    
    if not training:
        if is_assigned:
            primer_set = exercises.first()
            training = Training.objects.create(
                user=request.user,
                exercise=primer_set.exercise if primer_set else None,
                total_sets=primer_set.sets_count if primer_set else 4,
                reps=primer_set.reps if primer_set else 12,
                weight=primer_set.weight if primer_set else 0,
                date=timezone.now().date(),
                day_of_week=day.day_of_week,
                rest_time=primer_set.rest_time if primer_set else 90,
                intensity='Moderado',
                notes=f"Entrenamiento basado en la rutina {routine.name}"
            )
        else:
            primer_ejercicio = exercises.first()
            training = Training.objects.create(
                user=request.user,
                exercise=primer_ejercicio.exercise if primer_ejercicio else None,
                total_sets=primer_ejercicio.sets if primer_ejercicio else 4,
                reps=primer_ejercicio.reps if primer_ejercicio else 12,
                weight=primer_ejercicio.weight if primer_ejercicio else 0,
                date=timezone.now().date(),
                day_of_week=day.day_of_week,
                rest_time=primer_ejercicio.rest_time if primer_ejercicio else 90,
                intensity='Moderado',
                notes=f"Entrenamiento basado en la rutina {routine.name}"
            )
    
    # Obtener los sets completados
    completed_sets = Set.objects.filter(training=training).order_by('exercise', 'set_number')
    
    # Agrupar sets por ejercicio
    exercise_sets = {}
    for set_obj in completed_sets:
        if set_obj.exercise.id not in exercise_sets:
            exercise_sets[set_obj.exercise.id] = []
        exercise_sets[set_obj.exercise.id].append(set_obj)
    
    # Determinar el ejercicio actual (por ejemplo, el primero)
    exercise = exercises.first() if exercises else None

    # Día de la rutina
    routine_day = day

    # Fecha del entrenamiento
    training_date = training.date if training else timezone.now().date()

    # Progreso (ejemplo simple)
    progress = {
        'current': 1,
        'total': exercises.count() if exercises else 0,
        'percentage': 100 * 1 // (exercises.count() if exercises else 1)
    }

    # Para la rutina del día y el listado de ejercicios
    all_exercises = list(exercises)
    current_exercise_index = 0  # Por defecto el primero, puedes ajustar según navegación

    # Obtener el índice de la serie actual desde el POST o la URL
    current_set = int(request.POST.get('current_set', 1)) if request.method == 'POST' else 1
    current_exercise_index = int(request.POST.get('current_exercise_index', 0)) if request.method == 'POST' else 0
    total_sets = 0
    if exercise:
        total_sets = exercise.sets_count if is_assigned else exercise.sets
        try:
            total_sets = int(total_sets)
        except:
            total_sets = 1

    entrenamiento_finalizado = False
    if request.method == 'POST':
        # Si se completó la serie, guardar el set
        if 'complete_set' in request.POST:
            # Guardar el set realizado
            Set.objects.create(
                user=request.user,
                training=training,
                exercise=exercise.exercise,
                set_number=current_set,
                reps=request.POST.get('reps', 0),
                weight=request.POST.get('weight', 0),
                completed=True
            )
            if current_set < total_sets:
                current_set += 1
            else:
                # Avanzar al siguiente ejercicio y reiniciar la serie
                if current_exercise_index + 1 < len(all_exercises):
                    current_exercise_index += 1
                    exercise = all_exercises[current_exercise_index]
                    current_set = 1
                else:
                    entrenamiento_finalizado = True

    # Actualizar el ejercicio actual según el índice
    if all_exercises and not entrenamiento_finalizado:
        exercise = all_exercises[current_exercise_index]

    # Obtener los sets completados y agruparlos DESPUÉS de guardar el nuevo set
    completed_sets = Set.objects.filter(training=training).order_by('exercise', 'set_number')
    exercise_sets = {}
    for set_obj in completed_sets:
        if set_obj.exercise.id not in exercise_sets:
            exercise_sets[set_obj.exercise.id] = []
        exercise_sets[set_obj.exercise.id].append(set_obj)

    context = {
        'training': training,
        'routine': routine,
        'day': day,
        'exercises': exercises,
        'exercise': exercise,
        'routine_day': routine_day,
        'training_date': training_date,
        'progress': progress,
        'completed_sets': completed_sets,
        'exercise_sets': exercise_sets,
        'is_assigned': is_assigned,
        'all_exercises': all_exercises,
        'current_exercise_index': current_exercise_index,
        'current_set': current_set,
        'entrenamiento_finalizado': entrenamiento_finalizado,
    }
    
    return render(request, 'trainings/execute_training.html', context)

@login_required
def training_session_view(request, training_id):
    """
    Muestra una sesión de entrenamiento en curso.
    """
    training = get_object_or_404(Training, pk=training_id, user=request.user)
    
    # Obtener los sets completados
    completed_sets = Set.objects.filter(training=training).order_by('exercise', 'set_number')
    
    # Agrupar sets por ejercicio
    exercise_sets = {}
    for set_obj in completed_sets:
        if set_obj.exercise.id not in exercise_sets:
            exercise_sets[set_obj.exercise.id] = []
        exercise_sets[set_obj.exercise.id].append(set_obj)
    
    context = {
        'training': training,
        'completed_sets': completed_sets,
        'exercise_sets': exercise_sets
    }
    
    return render(request, 'trainings/training_session.html', context)

@login_required
@require_POST
def save_set(request, training_id=None):
    """
    Guarda un set de un ejercicio en un entrenamiento.
    """
    if training_id:
        training = get_object_or_404(Training, pk=training_id, user=request.user)
    else:
        training_id = request.POST.get('training_id')
        training = get_object_or_404(Training, pk=training_id, user=request.user)
    
    exercise_id = request.POST.get('exercise_id')
    set_number = request.POST.get('set_number', 1)
    reps = request.POST.get('reps', 0)
    weight = request.POST.get('weight', 0)
    notes = request.POST.get('notes', '')
    
    # Obtener el ejercicio
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    
    # Crear el set
    set_obj = Set.objects.create(
        training=training,
        exercise=exercise,
        set_number=set_number,
        reps=reps,
        weight=weight,
        notes=notes
    )
    
    # Si la solicitud es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'set_id': set_obj.id,
            'exercise_name': exercise.name,
            'set_number': set_number,
            'reps': reps,
            'weight': weight,
            'notes': notes
        })
    
    # Si no, redirigir a la vista de sesión
    return redirect('trainings:training-session', training_id=training.id)

@login_required
@require_POST
def save_set_simple(request):
    """
    Versión simplificada para guardar un set.
    """
    training_id = request.POST.get('training_id')
    exercise_id = request.POST.get('exercise_id')
    set_number = request.POST.get('set_number', 1)
    reps = request.POST.get('reps', 0)
    weight = request.POST.get('weight', 0)
    
    if not all([training_id, exercise_id]):
        return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
    
    training = get_object_or_404(Training, pk=training_id, user=request.user)
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    
    # Crear el set
    set_obj = Set.objects.create(
        training=training,
        exercise=exercise,
        set_number=set_number,
        reps=reps,
        weight=weight
    )
    
    return JsonResponse({
        'success': True,
        'set_id': set_obj.id,
        'exercise_name': exercise.name,
        'set_number': set_number,
        'reps': reps,
        'weight': weight
    })

@login_required
def get_completed_sets(request, training_id):
    """
    Obtiene los sets completados de un entrenamiento.
    """
    training = get_object_or_404(Training, pk=training_id, user=request.user)
    completed_sets = Set.objects.filter(training=training).order_by('exercise', 'set_number')
    
    sets_data = []
    for set_obj in completed_sets:
        sets_data.append({
            'id': set_obj.id,
            'exercise_id': set_obj.exercise.id,
            'exercise_name': set_obj.exercise.name,
            'set_number': set_obj.set_number,
            'reps': set_obj.reps,
            'weight': set_obj.weight,
            'notes': set_obj.notes
        })
    
    return JsonResponse({
        'training_id': training_id,
        'sets': sets_data
    }) 