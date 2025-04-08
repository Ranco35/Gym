from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
import logging

from .models import Workout, WeeklyRoutine, RoutineDay, RoutineExercise
from .serializers import (
    WorkoutSerializer,
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

# API REST Views
class WorkoutListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear entrenamientos.
    """
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados

    def get_queryset(self):
        """
        Obtiene los entrenamientos del usuario autenticado.
        """
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asigna el usuario autenticado al crear un nuevo entrenamiento.
        """
        serializer.save(user=self.request.user)

class WorkoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un entrenamiento.
    """
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados
    
    def get_queryset(self):
        """
        Asegura que solo se puedan acceder a los entrenamientos del usuario.
        """
        return Workout.objects.filter(user=self.request.user)

# Django Views para Rutinas Semanales (no API)
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
        return redirect('workouts:workout-detail', pk=routine.id)
    
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

@login_required
def edit_routine(request, pk):
    """
    Vista para editar una rutina existente.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=pk, user=request.user)
    days_of_week = WeeklyRoutine.DAYS_OF_WEEK
    
    if request.method == 'POST':
        # Obtener datos del formulario
        routine_name = request.POST.get('routine_name', 'Mi Rutina Semanal')
        routine_description = request.POST.get('routine_description', '')
        selected_days = request.POST.getlist('days')
        
        # Actualizar la rutina existente
        routine.name = routine_name
        routine.description = routine_description
        routine.save()
        
        # Obtener los días actuales y crear un diccionario para facilitar la búsqueda
        current_days = {day.day_of_week: day for day in routine.days.all()}
        
        # Crear nuevos días si no existen
        for day_name in selected_days:
            if day_name not in current_days:
                # Crear un nuevo día
                RoutineDay.objects.create(
                    routine=routine,
                    day_of_week=day_name,
                    focus="Por definir"
                )
        
        # Añadir un mensaje de éxito
        messages.success(request, "Rutina actualizada correctamente.")
        
        # Redirigir a la vista de detalle
        return redirect('workouts:workout-detail', pk=routine.id)
    
    # Obtener los días seleccionados actualmente
    selected_days = [day.day_of_week for day in routine.days.all()]
    
    return render(request, 'workouts/routine_edit.html', {
        'routine': routine,
        'days_of_week': days_of_week,
        'selected_days': selected_days
    })

@login_required
def delete_routine(request, pk):
    """
    Elimina una rutina completa.
    Solo administradores o superusuarios pueden eliminar rutinas.
    """
    # Verificar si el usuario es administrador o superusuario
    if not is_admin_or_superuser(request.user):
        messages.error(request, "No tienes permisos para eliminar rutinas. Esta acción solo está permitida para administradores.")
        return redirect('workouts:workout-list')
    
    routine = get_object_or_404(WeeklyRoutine, pk=pk)
    
    if request.method == 'POST':
        # Guardar el nombre para mostrar en mensaje de confirmación
        routine_name = routine.name
        # Eliminar la rutina
        routine.delete()
        messages.success(request, f"La rutina '{routine_name}' ha sido eliminada.")
        return redirect('workouts:workout-list')
    
    # Si no es un método POST, mostrar página de confirmación
    return render(request, 'workouts/routine_confirm_delete.html', {
        'routine': routine
    })

# Vista de acceso directo para la rutina con ID 2
@login_required
def view_assigned_routine(request):
    """
    Vista de acceso directo para ver la rutina asignada.
    """
    try:
        # Intentar obtener la rutina con ID 2
        try:
            routine = TrainerTraining.objects.get(id=2)
        except TrainerTraining.DoesNotExist:
            # Si no se encuentra, buscar una rutina que contenga "Fer Marzo" en el nombre
            routine = TrainerTraining.objects.filter(name__icontains="Fer Marzo").first()
            
            if not routine:
                messages.error(request, "No se encontró la rutina 'Fer Marzo 2025' ni la rutina con ID 2.")
                return redirect('workouts:workout-list')
        
        is_assigned_routine = True
        trainer_info = {
            'name': routine.created_by.get_full_name() or routine.created_by.username,
            'date_assigned': routine.created_at
        }
        
        return render(request, 'workouts/routine_detail.html', {
            'routine': routine,
            'is_assigned_routine': is_assigned_routine,
            'trainer_info': trainer_info
        })
    except Exception as e:
        messages.error(request, f"Error al acceder a la rutina: {str(e)}")
        return redirect('workouts:workout-list')