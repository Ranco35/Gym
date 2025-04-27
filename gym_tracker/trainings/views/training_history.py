from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from gym_tracker.workouts.models import WeeklyRoutine, RoutineDay, RoutineExercise
from trainers.models import TrainerTraining, TrainerTrainingDay, TrainerSet
from ..models import Training
from itertools import groupby
from django.db.models.functions import ExtractWeekDay
from django.db.models import F
from datetime import datetime
from collections import defaultdict

@login_required
def training_history(request):
    routine_id = request.GET.get('routine')
    selected_date = request.GET.get('date')
    
    # Intentar obtener la rutina (puede ser personal o asignada)
    routine = None
    trainings = []
    
    try:
        routine = TrainerTraining.objects.get(id=routine_id, user=request.user)
        # Obtener la estructura de la rutina
        routine_days = routine.days.all().order_by('day_of_week')
        routine_structure = {}
        
        # Organizar los ejercicios por día según la estructura de la rutina
        for day in routine_days:
            routine_structure[day.day_of_week] = {
                'name': day.get_day_of_week_display(),
                'exercises': [set_exercise.exercise for set_exercise in day.sets.all() if set_exercise.exercise]
            }
        
        # Obtener los entrenamientos relacionados con esta rutina asignada
        trainings_query = Training.objects.filter(
            user=request.user,
            trainer_training=routine
        ).select_related('exercise')
        
    except TrainerTraining.DoesNotExist:
        try:
            routine = WeeklyRoutine.objects.get(id=routine_id, user=request.user)
            routine_days = routine.days.all().order_by('day_of_week')
            routine_structure = {}
            
            for day in routine_days:
                routine_structure[day.day_of_week] = {
                    'name': day.get_day_of_week_display(),
                    'exercises': [exercise.exercise for exercise in day.exercises.all()]
                }
            
            trainings_query = Training.objects.filter(
                user=request.user,
                exercise_id__in=[ex.id for day_data in routine_structure.values() 
                               for ex in day_data['exercises']]
            ).select_related('exercise')
            
        except WeeklyRoutine.DoesNotExist:
            trainings_query = Training.objects.none()
            routine_structure = {}

    # Si no hay fecha seleccionada, mostrar lista de fechas agrupadas por día
    if not selected_date:
        # Agrupar entrenamientos por fecha
        trainings_by_date = defaultdict(list)
        for training in trainings_query:
            trainings_by_date[training.date].append(training)
        
        # Organizar fechas por día de la semana según la estructura de la rutina
        organized_dates = []
        for date, date_trainings in sorted(trainings_by_date.items(), reverse=True):
            weekday = date.weekday()
            day_name = routine_structure.get(weekday, {}).get('name', 'Otro')
            organized_dates.append({
                'date': date,
                'weekday': day_name,
                'exercise_count': len(date_trainings),
                'expected_exercises': len(routine_structure.get(weekday, {}).get('exercises', [])),
                'is_complete': len(date_trainings) >= len(routine_structure.get(weekday, {}).get('exercises', []))
            })
        
        context = {
            'routine': routine,
            'available_dates': organized_dates,
            'show_dates': True
        }
    else:
        # Mostrar ejercicios de la fecha seleccionada organizados según la rutina
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        weekday = date_obj.weekday()
        
        # Obtener los ejercicios esperados para ese día
        expected_exercises = routine_structure.get(weekday, {}).get('exercises', [])
        
        # Obtener los entrenamientos realizados
        trainings = trainings_query.filter(date=date_obj)
        
        # Organizar los entrenamientos según la estructura de la rutina
        organized_trainings = []
        completed_exercise_ids = set(t.exercise_id for t in trainings)
        
        for expected_exercise in expected_exercises:
            training = next((t for t in trainings if t.exercise_id == expected_exercise.id), None)
            organized_trainings.append({
                'exercise': expected_exercise,
                'training': training,
                'is_completed': expected_exercise.id in completed_exercise_ids
            })
        
        context = {
            'routine': routine,
            'selected_date': date_obj,
            'weekday': routine_structure.get(weekday, {}).get('name', 'Otro'),
            'organized_trainings': organized_trainings,
            'show_dates': False
        }
    
    return render(request, 'trainings/training_history.html', context) 