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
    Lista todas las rutinas del usuario.
    """
    routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'workouts/routine_list.html', {
        'routines': routines
    })

@login_required
def routine_detail(request, pk):
    """
    Muestra los detalles de una rutina.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=pk, user=request.user)
    return render(request, 'workouts/routine_detail.html', {
        'routine': routine
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
    
    # Obtener todos los ejercicios para seleccionar
    all_exercises = Exercise.objects.all()
    
    if request.method == 'POST':
        # Añadir un nuevo ejercicio a la rutina del día
        exercise_id = request.POST.get('exercise_id')
        sets = request.POST.get('sets', 3)
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
        current_days = {day.day_of_week: day for day in routine.routineday_set.all()}
        
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
    selected_days = [day.day_of_week for day in routine.routineday_set.all()]
    
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