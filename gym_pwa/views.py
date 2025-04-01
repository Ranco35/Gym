from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from gym_tracker.workouts.models import WeeklyRoutine, RoutineDay
from gym_tracker.trainings.models import Training, Set, UserProfile
from gym_tracker.exercises.models import Exercise, ExerciseImage
from trainers.models import TrainerTraining
import json
from django.contrib import messages
from gym_pwa.utils import convert_all_images_to_webp
from django.contrib.auth.models import User
import os

@login_required
def pwa_home(request):
    """Vista principal de la PWA."""
    # Obtener el nombre del usuario
    user_name = request.user.get_full_name() or request.user.username
    
    # Obtener estadísticas básicas - Corregido para usar el campo correcto 'completed'
    completed_trainings_count = Training.objects.filter(user=request.user, completed=True).count()
    
    # Obtener entrenamientos recientes - Corregido para usar el modelo directamente
    recent_trainings = Training.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Obtener rutinas semanales
    user_routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Obtener rutinas de entrenador
    trainer_routines = TrainerTraining.objects.filter(
        created_by=request.user
    ).select_related('created_by').order_by('-created_at')[:5]
    
    context = {
        'user_name': user_name,
        'completed_trainings_count': completed_trainings_count,
        'recent_trainings': recent_trainings,
        'user_routines': user_routines,
        'trainer_routines': trainer_routines
    }
    
    return render(request, 'gym_pwa/home.html', context)

@login_required
def pwa_workouts(request):
    """Vista que muestra las rutinas disponibles para el usuario."""
    # Obtener rutinas propias del usuario
    user_routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener entrenamientos propios
    user_trainings = Training.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener rutinas asignadas por entrenadores
    # TrainerTraining no tiene students, así que solo obtenemos aquellas donde el usuario es el creador o estudiante
    trainer_routines = TrainerTraining.objects.filter(
        created_by=request.user
    ).select_related('created_by').order_by('-created_at')
    
    # Calcular días activos de entrenamiento (días distintos)
    active_days = set()
    for training in user_trainings:
        if training.day_of_week:
            active_days.add(training.day_of_week)
    
    for routine in user_routines:
        for day in routine.days.all():
            if day.day_of_week:
                active_days.add(day.day_of_week)
    
    context = {
        'user_routines': user_routines,
        'user_trainings': user_trainings,
        'trainer_routines': trainer_routines,
        'active_days': len(active_days)
    }
    
    return render(request, 'gym_pwa/workouts.html', context)

@login_required
def pwa_workout_player(request, workout_id):
    """Reproductor de entrenamiento para la PWA."""
    # Obtener parámetros adicionales
    day_id = request.GET.get('day')
    workout_date = request.GET.get('date')
    workout_mode = request.GET.get('mode', 'step')  # Por defecto, usamos mode=step
    
    # Intentar obtener el entrenamiento (podría ser rutina personal o de entrenador)
    try:
        # Primero verificar si es un entrenamiento personal
        workout = Training.objects.get(id=workout_id, user=request.user)
        workout_type = 'personal'
        workout_name = workout.exercise.name  # Usar el nombre del ejercicio para entrenamientos personales
    except Training.DoesNotExist:
        try:
            # Luego verificar si es una rutina de entrenador
            workout = TrainerTraining.objects.get(
                id=workout_id,
                created_by=request.user
            )
            workout_type = 'trainer'
            workout_name = workout.name  # TrainerTraining sí tiene atributo name
        except TrainerTraining.DoesNotExist:
            # Si no se encuentra, intentar con rutina semanal
            workout = get_object_or_404(WeeklyRoutine, id=workout_id, user=request.user)
            workout_type = 'weekly'
            workout_name = workout.name  # WeeklyRoutine sí tiene atributo name
    
    # Preparar datos de ejercicios para el reproductor
    workout_data = {'id': workout_id, 'name': workout_name, 'exercises': []}
    
    # Obtener ejercicios según el tipo de entrenamiento
    if workout_type == 'personal':
        # Para entrenamientos personales
        sets = Set.objects.filter(training=workout).select_related('exercise').order_by('set_number')
        
        for set_obj in sets:
            exercise_data = {
                'id': set_obj.id,
                'exercise_id': set_obj.exercise.id,
                'name': set_obj.exercise.name,
                'weight': set_obj.weight,
                'reps': set_obj.reps,
                'sets_count': workout.total_sets,  # Usar total_sets del entrenamiento
                'notes': set_obj.exercise.tips if hasattr(set_obj.exercise, 'tips') else '',
                'target_muscles': set_obj.exercise.primary_muscles if hasattr(set_obj.exercise, 'primary_muscles') else '',
                'image_url': set_obj.exercise.image.url if hasattr(set_obj.exercise, 'image') and set_obj.exercise.image else None
            }
            workout_data['exercises'].append(exercise_data)
    
    elif workout_type == 'trainer':
        # Para rutinas de entrenador
        for day in workout.days.all():
            sets = day.sets.all().select_related('exercise').order_by('order')
            
            for set_obj in sets:
                exercise_data = {
                    'id': set_obj.id,
                    'exercise_id': set_obj.exercise.id,
                    'name': set_obj.exercise.name,
                    'weight': set_obj.weight,
                    'reps': set_obj.reps,
                    'sets_count': set_obj.sets_count,
                    'notes': set_obj.notes,
                    'target_muscles': set_obj.exercise.muscles_worked,
                    'image_url': set_obj.exercise.image.url if set_obj.exercise.image else None
                }
                workout_data['exercises'].append(exercise_data)
    
    else:
        # Para rutinas semanales
        # Si se especificó un día específico, filtrar solo por ese día
        if day_id:
            try:
                day = workout.days.get(id=day_id)
                days = [day]
                # Agregar información del día seleccionado
                workout_data['selected_day'] = {
                    'id': day.id,
                    'name': day.day_of_week,
                    'focus': day.focus
                }
            except:
                days = workout.days.all()
        else:
            days = workout.days.all()
            
        for day in days:
            for routine_exercise in day.exercises.all().select_related('exercise'):
                exercise_data = {
                    'id': routine_exercise.id,
                    'exercise_id': routine_exercise.exercise.id,
                    'name': routine_exercise.exercise.name,
                    'weight': routine_exercise.weight,
                    'reps': routine_exercise.reps,
                    'sets_count': routine_exercise.sets,
                    'notes': routine_exercise.notes,
                    'target_muscles': routine_exercise.exercise.muscles_worked,
                    'image_url': routine_exercise.exercise.image.url if routine_exercise.exercise.image else None,
                    'day': {
                        'id': day.id,
                        'name': day.day_of_week
                    }
                }
                workout_data['exercises'].append(exercise_data)
        
        # Si hay una fecha de entrenamiento, agregarla
        if workout_date:
            workout_data['workout_date'] = workout_date
    
    context = {
        'workout': workout,
        'workout_type': workout_type,
        'workout_data': json.dumps(workout_data),
        'workout_mode': workout_mode
    }
    
    return render(request, 'gym_pwa/workout_player.html', context)

@login_required
def auth_status(request):
    """Verificar estado de autenticación."""
    return JsonResponse({
        'authenticated': True,
        'user_id': request.user.id,
        'username': request.user.username,
        'full_name': request.user.get_full_name()
    })

@login_required
def pwa_exercises(request):
    """Vista que muestra los ejercicios disponibles para el usuario en la PWA."""
    # Obtener todos los ejercicios
    exercises = Exercise.objects.all().order_by('name')
    
    context = {
        'exercises': exercises
    }
    
    return render(request, 'gym_pwa/exercises.html', context)

@login_required
def pwa_profile(request):
    """Vista de perfil para la PWA."""
    # Obtener entrenamientos completados
    completed_workouts = Training.objects.filter(user=request.user, completed=True).count()
    
    # Obtener entrenamientos recientes
    recent_workouts = Training.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'completed_workouts': completed_workouts,
        'recent_workouts': recent_workouts
    }
    
    return render(request, 'gym_pwa/profile.html', context)

@login_required
def pwa_workout_detail(request, routine_id):
    """Vista que muestra los detalles de una rutina semanal."""
    # Obtener la rutina semanal
    routine = get_object_or_404(WeeklyRoutine, id=routine_id, user=request.user)
    
    context = {
        'routine': routine
    }
    
    return render(request, 'gym_pwa/workout_detail.html', context)

@login_required
def pwa_routine_detail(request, routine_id):
    """Vista detallada de una rutina semanal."""
    try:
        routine = WeeklyRoutine.objects.get(id=routine_id, user=request.user)
        routine_days = routine.days.all()
        
        context = {
            'routine': routine,
            'routine_days': routine_days
        }
        
        return render(request, 'gym_pwa/routine_detail.html', context)
        
    except WeeklyRoutine.DoesNotExist:
        messages.error(request, 'Rutina no encontrada')
        return redirect('gym_pwa:workouts')

@login_required
def pwa_routine_start(request, routine_id):
    """Vista para seleccionar el día y el modo de entrenamiento."""
    try:
        routine = WeeklyRoutine.objects.get(id=routine_id, user=request.user)
        
        # Obtener parámetros
        training_date = request.GET.get('date')
        day_id = request.GET.get('day')
        
        if not training_date:
            messages.error(request, 'Falta la fecha para iniciar el entrenamiento')
            return redirect('gym_pwa:home')
        
        # Si ya tenemos un día seleccionado, ir directamente a la selección de modo
        if day_id:
            try:
                day = RoutineDay.objects.get(id=day_id, weekly_routine=routine)
                context = {
                    'routine': routine,
                    'day': day,
                    'training_date': training_date
                }
                return render(request, 'gym_pwa/workout_mode_select.html', context)
            except RoutineDay.DoesNotExist:
                messages.error(request, 'El día seleccionado no existe')
                return redirect('gym_pwa:home')
        
        # Si no tenemos un día, mostrar la selección de días
        routine_days = routine.days.all()
        
        if not routine_days.exists():
            messages.error(request, 'Esta rutina no tiene días configurados')
            return redirect('gym_pwa:select_routine')
        
        context = {
            'routine': routine,
            'routine_days': routine_days,
            'training_date': training_date
        }
        
        return render(request, 'gym_pwa/select_day.html', context)
        
    except WeeklyRoutine.DoesNotExist:
        messages.error(request, 'Rutina no encontrada')
        return redirect('gym_pwa:home')

@login_required
def pwa_select_routine(request):
    """Vista para seleccionar una rutina después de elegir fecha."""
    # Obtener la fecha seleccionada
    training_date = request.GET.get('date')
    
    if not training_date:
        messages.error(request, 'Debes seleccionar una fecha para el entrenamiento')
        return redirect('gym_pwa:home')
    
    # Obtener rutinas propias del usuario
    user_routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener rutinas asignadas por entrenadores (por ahora solo las creadas por el usuario)
    # En un sistema real, se obtendrían las rutinas donde el usuario es estudiante
    assigned_routines = TrainerTraining.objects.filter(
        created_by=request.user
    ).select_related('created_by').order_by('-created_at')
    
    context = {
        'user_routines': user_routines,
        'assigned_routines': assigned_routines,
        'training_date': training_date
    }
    
    return render(request, 'gym_pwa/select_routine.html', context)

def service_worker(request):
    """Sirve el archivo service-worker.js."""
    return render(request, 'gym_pwa/sw.js', 
                content_type='application/javascript',
                context={'version': '1.0.0'})


def offline(request):
    """Muestra la página offline cuando no hay conexión."""
    return render(request, 'gym_pwa/offline.html')

@login_required
def convert_images_to_webp(request):
    """Vista para convertir todas las imágenes a formato WebP."""
    # Verificar que el usuario sea staff
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('gym_pwa:home')
    
    # Convertir imágenes de ejercicios
    exercise_count = convert_all_images_to_webp(Exercise, 'image')
    
    # Convertir imágenes adicionales de ejercicios
    exercise_image_count = convert_all_images_to_webp(ExerciseImage, 'image')
    
    # Convertir imágenes de perfil
    user_profile_count = convert_all_images_to_webp(UserProfile, 'photo')
    
    # Mensaje de éxito
    messages.success(
        request, 
        f'Conversión completada. Se convirtieron {exercise_count} imágenes de ejercicios, '
        f'{exercise_image_count} imágenes adicionales y {user_profile_count} imágenes de perfil.'
    )
    
    return redirect('gym_pwa:home')

@login_required
def update_profile_photo(request):
    """Vista para actualizar la foto de perfil."""
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            # Obtener el perfil del usuario
            profile = request.user.profile
            
            # Guardar la foto anterior para eliminarla después
            old_photo = None
            if profile.photo:
                old_photo = profile.photo.path
            
            # Asignar nueva foto (se convertirá a WebP automáticamente en el modelo)
            profile.photo = request.FILES['photo']
            profile.save()
            
            # Eliminar la foto anterior si existe
            if old_photo and os.path.exists(old_photo):
                os.unlink(old_photo)
            
            messages.success(request, 'Foto de perfil actualizada correctamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la foto: {str(e)}')
    else:
        messages.error(request, 'No se ha seleccionado ninguna foto')
    
    return redirect('gym_pwa:profile') 