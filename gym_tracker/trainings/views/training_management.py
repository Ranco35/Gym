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
    routine_id = request.POST.get('routine_id')
    day_id = request.POST.get('day_id')
    date = request.POST.get('date')
    
    if not all([routine_id, day_id, date]):
        return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
    
    try:
        # Intentar obtener como rutina personal
        routine = Routine.objects.get(id=routine_id, user=request.user)
        day = RoutineDay.objects.get(id=day_id, routine=routine)
        is_assigned = False
    except (Routine.DoesNotExist, RoutineDay.DoesNotExist):
        # Intentar obtener como rutina asignada por entrenador
        try:
            routine = TrainerTraining.objects.get(id=routine_id, user=request.user)
            day = TrainerTrainingDay.objects.get(id=day_id, training=routine)
            is_assigned = True
        except (TrainerTraining.DoesNotExist, TrainerTrainingDay.DoesNotExist):
            return JsonResponse({'error': 'Rutina o día no encontrado'}, status=404)
    
    # Crear el entrenamiento
    training = Training.objects.create(
        user=request.user,
        name=f"{routine.name} - {day.day_of_week}",
        date=date,
        notes=f"Entrenamiento basado en la rutina {routine.name}"
    )
    
    # Redirigir a la vista de ejecución del entrenamiento
    return redirect('trainings:execute-training', routine_id=routine_id, day_id=day_id) 