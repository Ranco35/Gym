from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from ..models import WeeklyRoutine, RoutineDay, RoutineExercise
from gym_tracker.exercises.models import Exercise

@login_required
def routine_day_detail(request, routine_pk, day_pk):
    """
    Muestra los detalles de un día de rutina y sus ejercicios.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=routine_pk, user=request.user)
    day = get_object_or_404(RoutineDay, pk=day_pk, routine=routine)
    
    # Obtener ejercicios para este día
    exercises = RoutineExercise.objects.filter(routine_day=day).order_by('order')
    
    # Obtener todos los ejercicios para seleccionar, incluyendo sus grupos musculares y músculos
    all_exercises = Exercise.objects.all().order_by('muscle_group', 'name')
    
    if request.method == 'POST':
        # Añadir un nuevo ejercicio a la rutina del día
        exercise_id = request.POST.get('exercise_id')
        sets = request.POST.get('sets', 4)
        reps = request.POST.get('reps', '10')
        weight = request.POST.get('weight', '')
        rest_time = request.POST.get('rest_time', 60)
        
        if exercise_id:
            exercise = get_object_or_404(Exercise, pk=exercise_id)
            
            # Determinar el siguiente orden
            next_order = 1
            if exercises.exists():
                next_order = exercises.last().order + 1
            
            # Crear el ejercicio de rutina
            RoutineExercise.objects.create(
                routine_day=day,
                exercise=exercise,
                sets=sets,
                reps=reps,
                weight=weight,
                rest_time=rest_time,
                order=next_order
            )
            
            # Si hay músculos principales en el ejercicio y no hay enfoque definido,
            # actualizar el enfoque del día con estos músculos
            if exercise.primary_muscles and not day.focus:
                day.focus = exercise.primary_muscles
                day.save()
            
            return redirect('workouts:workout-day-detail', routine_pk=routine_pk, day_pk=day_pk)
    
    return render(request, 'workouts/routine_day_detail.html', {
        'routine': routine,
        'day': day,
        'exercises': exercises,
        'all_exercises': all_exercises
    })

@login_required
def delete_routine_exercise(request, exercise_pk):
    """
    Elimina un ejercicio de la rutina.
    """
    exercise = get_object_or_404(RoutineExercise, pk=exercise_pk)
    
    # Verificar que el usuario es el propietario
    if exercise.routine_day.routine.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para eliminar este ejercicio'}, status=403)
    
    # Guardar referencias para redirigir después de eliminar
    day_pk = exercise.routine_day.pk
    routine_pk = exercise.routine_day.routine.pk
    
    # Eliminar ejercicio
    exercise.delete()
    
    # Redirigir a la página de detalle del día
    return redirect('workouts:workout-day-detail', routine_pk=routine_pk, day_pk=day_pk)

@login_required
def update_routine_focus(request, day_pk):
    """
    Actualiza el enfoque de un día de entrenamiento.
    """
    day = get_object_or_404(RoutineDay, pk=day_pk)
    
    # Verificar que el usuario es el propietario
    if day.routine.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para actualizar este día'}, status=403)
    
    if request.method == 'POST':
        focus = request.POST.get('focus', '')
        day.focus = focus
        day.save()
        
        return redirect('workouts:workout-day-detail', routine_pk=day.routine.pk, day_pk=day.pk)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405) 