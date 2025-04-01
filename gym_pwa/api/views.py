from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from gym_tracker.workouts.models import WeeklyRoutine
from gym_tracker.trainings.models import Training, Set
from trainers.models import TrainerTraining, TrainerSet
from gym_tracker.trainings.models import LiveTraining, LiveSet
import json
from django.utils import timezone

@api_view(['GET'])
@login_required
def get_user_workouts(request):
    """
    Obtener todas las rutinas disponibles para el usuario.
    Este endpoint es para cargar datos offline en la PWA.
    """
    # Entrenamientos personales
    user_trainings = Training.objects.filter(user=request.user)
    user_trainings_data = []
    
    for training in user_trainings:
        sets = Set.objects.filter(training=training).select_related('exercise')
        exercises = []
        
        for set_obj in sets:
            exercise_data = {
                'id': set_obj.id,
                'exercise_id': set_obj.exercise.id,
                'name': set_obj.exercise.name,
                'weight': set_obj.weight,
                'reps': set_obj.reps,
                'sets_count': set_obj.sets_count,
                'notes': set_obj.notes or '',
                'target_muscles': set_obj.exercise.muscles_worked,
                'image_url': request.build_absolute_uri(set_obj.exercise.image.url) if set_obj.exercise.image else None
            }
            exercises.append(exercise_data)
        
        user_trainings_data.append({
            'id': training.id,
            'name': training.name,
            'description': training.description or '',
            'type': 'personal',
            'created_at': training.created_at.isoformat(),
            'exercises': exercises
        })
    
    # Rutinas de entrenador
    trainer_trainings = TrainerTraining.objects.filter(
        created_by=request.user
    )
    trainer_trainings_data = []
    
    for training in trainer_trainings:
        exercises = []
        for day in training.days.all():
            sets = day.sets.all().select_related('exercise').order_by('order')
            
            for set_obj in sets:
                exercise_data = {
                    'id': set_obj.id,
                    'exercise_id': set_obj.exercise.id,
                    'name': set_obj.exercise.name,
                    'weight': set_obj.weight,
                    'reps': set_obj.reps,
                    'sets_count': set_obj.sets_count,
                    'notes': set_obj.notes or '',
                    'target_muscles': set_obj.exercise.muscles_worked,
                    'image_url': request.build_absolute_uri(set_obj.exercise.image.url) if set_obj.exercise.image else None
                }
                exercises.append(exercise_data)
        
        trainer_trainings_data.append({
            'id': training.id,
            'name': training.name,
            'description': training.description or '',
            'type': 'trainer',
            'trainer_name': training.created_by.get_full_name() or training.created_by.username,
            'created_at': training.created_at.isoformat(),
            'exercises': exercises
        })
    
    # Rutinas semanales
    weekly_routines = WeeklyRoutine.objects.filter(user=request.user)
    weekly_routines_data = []
    
    for routine in weekly_routines:
        exercises = []
        for day in routine.days.all():
            for routine_exercise in day.exercises.all().select_related('exercise'):
                exercise_data = {
                    'id': routine_exercise.id,
                    'exercise_id': routine_exercise.exercise.id,
                    'name': routine_exercise.exercise.name,
                    'weight': routine_exercise.weight,
                    'reps': routine_exercise.reps,
                    'sets_count': routine_exercise.sets,
                    'notes': routine_exercise.notes or '',
                    'target_muscles': routine_exercise.exercise.muscles_worked,
                    'image_url': request.build_absolute_uri(routine_exercise.exercise.image.url) if routine_exercise.exercise.image else None
                }
                exercises.append(exercise_data)
        
        weekly_routines_data.append({
            'id': routine.id,
            'name': routine.name,
            'description': '',  # No tiene campo description
            'type': 'weekly',
            'created_at': routine.created_at.isoformat(),
            'exercises': exercises
        })
    
    # Combinar todos los datos
    all_workouts = {
        'user_trainings': user_trainings_data,
        'trainer_trainings': trainer_trainings_data,
        'weekly_routines': weekly_routines_data
    }
    
    return Response(all_workouts)

@api_view(['GET'])
@login_required
def get_workout_detail(request, workout_id):
    """
    Obtener detalles de un entrenamiento específico.
    """
    workout_type = request.GET.get('type', 'personal')
    
    try:
        if workout_type == 'personal':
            workout = Training.objects.get(id=workout_id, user=request.user)
            sets = Set.objects.filter(training=workout).select_related('exercise').order_by('order')
            
            exercises = []
            for set_obj in sets:
                exercise_data = {
                    'id': set_obj.id,
                    'exercise_id': set_obj.exercise.id,
                    'name': set_obj.exercise.name,
                    'weight': set_obj.weight,
                    'reps': set_obj.reps,
                    'sets_count': set_obj.sets_count,
                    'notes': set_obj.notes or '',
                    'target_muscles': set_obj.exercise.muscles_worked,
                    'image_url': request.build_absolute_uri(set_obj.exercise.image.url) if set_obj.exercise.image else None
                }
                exercises.append(exercise_data)
            
            workout_data = {
                'id': workout.id,
                'name': workout.name,
                'description': workout.description or '',
                'type': 'personal',
                'created_at': workout.created_at.isoformat(),
                'exercises': exercises
            }
            
            return Response(workout_data)
            
        elif workout_type == 'trainer':
            workout = TrainerTraining.objects.get(
                id=workout_id,
                created_by=request.user
            )
            
            exercises = []
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
                        'notes': set_obj.notes or '',
                        'target_muscles': set_obj.exercise.muscles_worked,
                        'image_url': request.build_absolute_uri(set_obj.exercise.image.url) if set_obj.exercise.image else None
                    }
                    exercises.append(exercise_data)
            
            workout_data = {
                'id': workout.id,
                'name': workout.name,
                'description': workout.description or '',
                'type': 'trainer',
                'trainer_name': workout.created_by.get_full_name() or workout.created_by.username,
                'created_at': workout.created_at.isoformat(),
                'exercises': exercises
            }
            
            return Response(workout_data)
            
        else:  # weekly
            workout = WeeklyRoutine.objects.get(id=workout_id, user=request.user)
            
            exercises = []
            for day in workout.days.all():
                for routine_exercise in day.exercises.all().select_related('exercise'):
                    exercise_data = {
                        'id': routine_exercise.id,
                        'exercise_id': routine_exercise.exercise.id,
                        'name': routine_exercise.exercise.name,
                        'weight': routine_exercise.weight,
                        'reps': routine_exercise.reps,
                        'sets_count': routine_exercise.sets,
                        'notes': routine_exercise.notes or '',
                        'target_muscles': routine_exercise.exercise.muscles_worked,
                        'image_url': request.build_absolute_uri(routine_exercise.exercise.image.url) if routine_exercise.exercise.image else None
                    }
                    exercises.append(exercise_data)
            
            workout_data = {
                'id': workout.id,
                'name': workout.name,
                'description': '',  # No tiene campo description
                'type': 'weekly',
                'created_at': workout.created_at.isoformat(),
                'exercises': exercises
            }
            
            return Response(workout_data)
            
    except (Training.DoesNotExist, TrainerTraining.DoesNotExist, WeeklyRoutine.DoesNotExist):
        return Response(
            {'error': 'No se encontró el entrenamiento solicitado'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@login_required
def sync_completed_set(request):
    """
    Sincronizar una serie completada desde la PWA.
    """
    try:
        data = request.data
        workout_type = data.get('workout_type', 'personal')
        workout_id = data.get('workout_id')
        exercise_id = data.get('exercise_id')
        set_number = data.get('set_number')
        weight = data.get('weight')
        reps = data.get('reps')
        
        if workout_type == 'personal':
            # Verificar que el entrenamiento existe y pertenece al usuario
            training = Training.objects.get(id=workout_id, user=request.user)
            
            # Buscar la serie correspondiente
            set_obj = Set.objects.get(id=exercise_id, training=training)
            
            # Crear o actualizar el registro de entrenamiento en vivo
            live_training, created = LiveTraining.objects.get_or_create(
                training=training,
                student=request.user,
                status='active',
                defaults={'started_at': timezone.now()}
            )
            
            # Registrar la serie completada
            live_set = LiveSet.objects.create(
                live_training=live_training,
                set=set_obj,
                completed_by=request.user,
                completed_at=timezone.now()
            )
            
            return Response({
                'success': True,
                'message': 'Serie registrada correctamente',
                'live_set_id': live_set.id
            })
            
        elif workout_type == 'trainer':
            # Para rutinas de entrenador
            trainer_training = TrainerTraining.objects.get(
                id=workout_id,
                created_by=request.user
            )
            
            # Buscar la serie correspondiente
            trainer_set = TrainerSet.objects.get(id=exercise_id)
            
            # En lugar de usar LiveTrainingSession, usamos LiveTraining que tiene un esquema más simple
            live_training, created = LiveTraining.objects.get_or_create(
                training_id=trainer_training.id,  # Usando el ID directamente
                student=request.user,
                status='active',
                defaults={'started_at': timezone.now()}
            )
            
            # Registrar la serie completada usando LiveSet del modelo training
            live_set = LiveSet.objects.create(
                live_training=live_training,
                set_id=trainer_set.id,  # Usando el ID directamente
                completed_by=request.user,
                weight=weight,
                reps=reps,
                completed_at=timezone.now()
            )
            
            return Response({
                'success': True,
                'message': 'Serie registrada correctamente',
                'live_set_id': live_set.id
            })
            
        return Response({
            'success': False,
            'message': 'Tipo de entrenamiento no soportado'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al sincronizar: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@login_required
def sync_workout_progress(request):
    """
    Sincronizar el progreso completo de un entrenamiento desde la PWA.
    """
    try:
        data = request.data
        workout_type = data.get('workout_type', 'personal')
        workout_id = data.get('workout_id')
        sets_data = data.get('sets', [])
        
        # Dependiendo del tipo de entrenamiento, crear los registros correspondientes
        if workout_type == 'personal':
            training = Training.objects.get(id=workout_id, user=request.user)
            
            # Crear LiveTraining si no existe
            live_training, created = LiveTraining.objects.get_or_create(
                training=training,
                student=request.user,
                status='active',
                defaults={'started_at': timezone.now()}
            )
            
            # Procesar cada serie
            for set_data in sets_data:
                set_obj = Set.objects.get(id=set_data['exercise_id'], training=training)
                
                # Verificar si ya existe esta serie
                existing_set = LiveSet.objects.filter(
                    live_training=live_training,
                    set=set_obj,
                    completed_by=request.user
                ).exists()
                
                if not existing_set:
                    LiveSet.objects.create(
                        live_training=live_training,
                        set=set_obj,
                        completed_by=request.user,
                        completed_at=timezone.now()
                    )
            
            return Response({
                'success': True,
                'message': 'Progreso sincronizado correctamente'
            })
            
        elif workout_type == 'trainer':
            trainer_training = TrainerTraining.objects.get(
                id=workout_id,
                created_by=request.user
            )
            
            # Usar LiveTraining en lugar de LiveTrainingSession
            live_training, created = LiveTraining.objects.get_or_create(
                training_id=trainer_training.id,
                student=request.user,
                status='active',
                defaults={'started_at': timezone.now()}
            )
            
            # Procesar cada serie
            for set_data in sets_data:
                trainer_set = TrainerSet.objects.get(id=set_data['exercise_id'])
                
                # Verificar si ya existe esta serie con el mismo número
                existing_set = LiveSet.objects.filter(
                    live_training=live_training,
                    set_id=trainer_set.id,
                    completed_by=request.user
                ).exists()
                
                if not existing_set:
                    LiveSet.objects.create(
                        live_training=live_training,
                        set_id=trainer_set.id,
                        completed_by=request.user,
                        weight=set_data['weight'],
                        reps=set_data['reps'],
                        completed_at=timezone.now()
                    )
            
            return Response({
                'success': True,
                'message': 'Progreso sincronizado correctamente'
            })
            
        return Response({
            'success': False,
            'message': 'Tipo de entrenamiento no soportado'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al sincronizar: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@login_required
def get_weekly_routine_details(request, routine_id):
    """Obtener detalles de una rutina semanal."""
    try:
        routine = WeeklyRoutine.objects.get(id=routine_id, user=request.user)
        
        # Preparar datos de la rutina
        days_data = []
        for day in routine.days.all():
            exercises = []
            for exercise in day.exercises.all().select_related('exercise'):
                exercises.append({
                    'id': exercise.id,
                    'name': exercise.exercise.name,
                    'sets': exercise.sets,
                    'reps': exercise.reps,
                    'weight': exercise.weight or '',
                    'notes': exercise.notes or '',
                    'order': exercise.order
                })
            
            days_data.append({
                'id': day.id,
                'day': day.day_of_week,
                'focus': day.focus or '',
                'exercises': exercises
            })
        
        routine_data = {
            'id': routine.id,
            'name': routine.name,
            'description': routine.description or '',
            'days': days_data
        }
        
        return JsonResponse({'routine': routine_data})
    except WeeklyRoutine.DoesNotExist:
        return JsonResponse({'error': 'Rutina no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@login_required
def get_routine_days(request, routine_id):
    """Obtener los días disponibles para una rutina semanal."""
    try:
        # Verificar si la rutina pertenece al usuario
        routine = WeeklyRoutine.objects.get(id=routine_id, user=request.user)
        
        # Obtener los días de la rutina
        days = []
        for day in routine.days.all():
            days.append({
                'id': day.id,
                'day_of_week': day.day_of_week,
                'focus': day.focus
            })
        
        return Response({
            'routine_id': routine_id,
            'routine_name': routine.name,
            'days': days
        })
        
    except WeeklyRoutine.DoesNotExist:
        return Response({
            'error': 'Rutina no encontrada'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500) 