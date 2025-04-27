from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse

from ..models import Training, Set
from ..forms import TrainingForm, SetForm
from gym_tracker.workouts.models import WeeklyRoutine as Routine, RoutineDay, RoutineExercise
from trainers.models import LiveTrainingSession, TrainerStudent, TrainerTraining, TrainerTrainingDay, TrainerSet

@login_required
@require_POST
def delete_training(request, pk):
    """
    Elimina un entrenamiento.
    """
    training = get_object_or_404(Training, pk=pk, user=request.user)
    training.delete()
    messages.success(request, "Entrenamiento eliminado correctamente.")
    return redirect('trainings:training-list')

@login_required
@require_POST
@csrf_exempt
def toggle_complete(request, pk):
    """
    Cambia el estado de completado de un entrenamiento.
    """
    training = get_object_or_404(Training, pk=pk, user=request.user)
    training.completed = not training.completed
    training.save()
    
    return JsonResponse({
        'success': True,
        'completed': training.completed
    })

@login_required
def get_routine_days(request, routine_id):
    """
    Obtiene los días de una rutina para mostrarlos en un formulario.
    """
    try:
        # Intentar obtener como rutina personal
        routine = Routine.objects.get(id=routine_id, user=request.user)
        days = routine.days.all()
        is_assigned = False
    except Routine.DoesNotExist:
        # Intentar obtener como rutina asignada por entrenador
        try:
            routine = TrainerTraining.objects.get(id=routine_id, user=request.user)
            days = routine.days.all()
            is_assigned = True
        except TrainerTraining.DoesNotExist:
            return JsonResponse({'error': 'Rutina no encontrada'}, status=404)
    
    days_data = []
    for day in days:
        days_data.append({
            'id': day.id,
            'day_of_week': day.day_of_week,
            'focus': day.focus
        })
    
    return JsonResponse({
        'routine_id': routine_id,
        'routine_name': routine.name,
        'is_assigned': is_assigned,
        'days': days_data
    })

@login_required
@require_POST
def create_training_from_routine(request):
    """
    Crea un nuevo entrenamiento basado en una rutina.
    """
    # Aceptar ambos nombres de campo para compatibilidad
    routine_id = request.POST.get('routine_id')
    day_id = request.POST.get('day_id') or request.POST.get('routine_day_id')
    date = request.POST.get('date') or request.POST.get('training_date')
    
    if not all([routine_id, day_id, date]):
        return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
    
    try:
        # Intentar obtener como rutina personal
        routine = Routine.objects.get(id=routine_id, user=request.user)
        day = RoutineDay.objects.get(id=day_id, routine=routine)
        # Obtener ejercicios para rutina personal
        routine_exercise = day.exercises.first() if hasattr(day, 'exercises') else None
        if not routine_exercise:
            return JsonResponse({'error': 'No hay ejercicios configurados para este día'}, status=400)
        training = Training.objects.create(
            user=request.user,
            exercise=routine_exercise.exercise,
            total_sets=routine_exercise.sets or 4,
            reps=int(routine_exercise.reps) if routine_exercise.reps.isdigit() else 12,
            weight=float(routine_exercise.weight) if routine_exercise.weight and routine_exercise.weight.replace('.', '', 1).isdigit() else None,
            date=date,
            day_of_week=day.day_of_week,
            rest_time=routine_exercise.rest_time or 90,
            intensity='Moderado',
            notes=f"Entrenamiento basado en la rutina {routine.name}"
        )
        is_assigned = False
    except (Routine.DoesNotExist, RoutineDay.DoesNotExist):
        # Intentar obtener como rutina asignada por entrenador
        try:
            routine = TrainerTraining.objects.get(id=routine_id, user=request.user)
            day = TrainerTrainingDay.objects.get(id=day_id, training=routine)
            # Obtener ejercicios para rutina de entrenador
            trainer_set = day.sets.first() if hasattr(day, 'sets') else None
            if not trainer_set:
                return JsonResponse({'error': 'No hay ejercicios configurados para este día'}, status=400)
            training = Training.objects.create(
                user=request.user,
                exercise=trainer_set.exercise,
                total_sets=trainer_set.sets_count or 4,
                reps=int(trainer_set.reps) if str(trainer_set.reps).isdigit() else 12,
                weight=float(trainer_set.weight) if trainer_set.weight and str(trainer_set.weight).replace('.', '', 1).isdigit() else None,
                date=date,
                day_of_week=day.day_of_week,
                rest_time=trainer_set.rest_time or 90,
                intensity='Moderado',
                notes=f"Entrenamiento basado en la rutina {routine.name}"
            )
            is_assigned = True
        except (TrainerTraining.DoesNotExist, TrainerTrainingDay.DoesNotExist):
            return JsonResponse({'error': 'Rutina o día no encontrado'}, status=404)
    
    # Redirigir a la vista de ejecución del entrenamiento
    return redirect('trainings:execute-training', routine_id=routine_id, day_id=day_id) 