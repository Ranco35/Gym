from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
import logging

from ..models import WeeklyRoutine, RoutineDay, RoutineExercise
from ..serializers import (
    WeeklyRoutineSerializer,
    WeeklyRoutineCreateSerializer,
    RoutineDaySerializer,
    RoutineDayCreateSerializer,
    RoutineExerciseSerializer
)
from gym_tracker.exercises.models import Exercise
from trainers.models import TrainerTraining

# Función de verificación para comprobar si un usuario es administrador o superusuario
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@login_required
def routine_selection(request):
    """
    Vista para seleccionar los días de la semana que se entrena.
    """
    days_of_week = WeeklyRoutine.DAYS_OF_WEEK
    
    if request.method == 'POST':
        # Obtener días seleccionados
        selected_days = request.POST.getlist('days')
        routine_name = request.POST.get('routine_name', 'Mi Rutina Semanal')
        
        # Crear rutina semanal
        routine = WeeklyRoutine.objects.create(
            user=request.user,
            name=routine_name,
            description=f"Rutina para los días: {', '.join(selected_days)}"
        )
        
        # Crear días de rutina
        for day in selected_days:
            RoutineDay.objects.create(
                routine=routine,
                day_of_week=day,
                focus="Por definir"
            )
        
        # Redirigir a la vista de detalle de la rutina
        return redirect('workouts:routine-detail', pk=routine.id)
    
    return render(request, 'workouts/routine_selection.html', {
        'days_of_week': days_of_week
    })

@login_required
def routine_list(request):
    """
    Lista todas las rutinas del usuario, incluyendo las asignadas por entrenadores.
    """
    # Obtener rutinas personales del usuario
    personal_routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener rutinas asignadas por entrenadores - consulta directa por ID de usuario
    assigned_routines = TrainerTraining.objects.select_related('created_by').filter(
        user_id=request.user.id
    ).order_by('-created_at')
    
    # Verificar manualmente todas las rutinas para depuración
    all_trainings = list(TrainerTraining.objects.all())
    
    # Usar Force Evaluation para garantizar que las consultas se ejecuten
    personal_routines_list = list(personal_routines)
    assigned_routines_list = list(assigned_routines)
    
    context = {
        'personal_routines': personal_routines_list,
        'assigned_routines': assigned_routines_list,
        'debug_info': {
            'username': request.user.username,
            'user_id': request.user.id,
            'personal_count': len(personal_routines_list),
            'assigned_count': len(assigned_routines_list),
            'total_trainings': len(all_trainings)
        }
    }
    
    return render(request, 'workouts/routine_list.html', context)

@login_required
def routine_detail(request, pk):
    """
    Muestra los detalles de una rutina, sea personal o asignada por entrenador.
    """
    # Verificar si es una rutina personal
    routine = None
    is_assigned_routine = False
    trainer_info = None
    
    try:
        # Primero intentamos obtener como rutina personal
        routine = get_object_or_404(WeeklyRoutine, pk=pk, user=request.user)
    except:
        # Si no existe como rutina personal, verificar si es una rutina asignada por entrenador
        routine = get_object_or_404(TrainerTraining, pk=pk, user=request.user)
        is_assigned_routine = True
        trainer_info = {
            'name': routine.created_by.get_full_name() or routine.created_by.username,
            'date_assigned': routine.created_at
        }
    
    # Si la solicitud es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        days = []
        
        if is_assigned_routine:
            # Para rutinas asignadas por entrenador
            for day in routine.days.all():
                exercises = []
                for trainer_set in day.sets.all():
                    exercises.append({
                        'id': trainer_set.id,
                        'name': trainer_set.exercise.name,
                        'sets': trainer_set.sets_count,
                        'reps': trainer_set.reps,
                        'weight': trainer_set.weight,
                        'notes': trainer_set.notes
                    })
                
                days.append({
                    'id': day.id,
                    'day_of_week': day.day_of_week,
                    'focus': day.focus,
                    'exercises': exercises
                })
        else:
            # Para rutinas personales
            for day in routine.days.all():
                exercises = []
                for routine_exercise in day.exercises.all():
                    exercises.append({
                        'id': routine_exercise.exercise.id,
                        'name': routine_exercise.exercise.name,
                        'sets': routine_exercise.sets,
                        'reps': routine_exercise.reps,
                        'weight': routine_exercise.weight,
                        'rest_time': routine_exercise.rest_time
                    })
                
                days.append({
                    'id': day.id,
                    'day_of_week': day.day_of_week,
                    'focus': day.focus,
                    'exercises': exercises
                })
        
        return JsonResponse({
            'routine': {
                'id': routine.id,
                'name': routine.name,
                'is_assigned': is_assigned_routine
            },
            'days': days,
            'trainer_info': trainer_info
        })
    
    return render(request, 'workouts/routine_detail.html', {
        'routine': routine,
        'is_assigned_routine': is_assigned_routine,
        'trainer_info': trainer_info
    }) 