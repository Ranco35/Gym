from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Max, Min
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear
from datetime import datetime, timedelta
from gym_tracker.trainings.models import Training, Set
from gym_tracker.exercises.models import Exercise
from gym_tracker.workouts.models import WeeklyRoutine

@login_required
def dashboard(request):
    """Vista principal del dashboard de estadísticas."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)  # Por defecto muestra último mes

    # Estadísticas generales
    stats = {
        'total_trainings': Training.objects.filter(user=request.user, completed=True).count(),
        'total_exercises': Exercise.objects.filter(training__user=request.user).distinct().count(),
        'total_routines': WeeklyRoutine.objects.filter(user=request.user).count(),
        'total_volume': Set.objects.filter(training__user=request.user).aggregate(total=Sum('weight'))['total'] or 0
    }

    # Últimos entrenamientos
    recent_trainings = Training.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-date')[:5]

    context = {
        'stats': stats,
        'recent_trainings': recent_trainings,
    }
    return render(request, 'stats/dashboard.html', context)

@login_required
def exercise_progress(request):
    """Vista de progreso por ejercicio."""
    exercise_id = request.GET.get('exercise')
    period = request.GET.get('period', 'month')
    end_date = datetime.now().date()

    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)

    # Progreso de ejercicios
    exercises = Exercise.objects.filter(training__user=request.user).distinct()
    
    if exercise_id:
        exercises = exercises.filter(id=exercise_id)

    exercise_stats = {}
    for exercise in exercises:
        stats = Training.objects.filter(
            user=request.user,
            exercise=exercise,
            date__range=[start_date, end_date],
            completed=True
        ).values('date').annotate(
            max_weight=Max('training_sets__weight'),
            avg_weight=Avg('training_sets__weight'),
            total_volume=Sum('training_sets__weight'),
            total_sets=Count('training_sets')
        ).order_by('date')

        exercise_stats[exercise.name] = list(stats)

    context = {
        'exercises': exercises,
        'exercise_stats': exercise_stats,
        'selected_exercise': exercise_id,
        'period': period
    }
    return render(request, 'stats/exercise_progress.html', context)

@login_required
def volume_analysis(request):
    """Vista de análisis de volumen."""
    period = request.GET.get('period', 'month')
    end_date = datetime.now().date()

    if period == 'week':
        start_date = end_date - timedelta(days=7)
        extract_func = ExtractWeek
        group_by = 'week'
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
        extract_func = ExtractMonth
        group_by = 'month'
    else:
        start_date = end_date - timedelta(days=365)
        extract_func = ExtractYear
        group_by = 'year'

    # Obtener todos los sets completados en el período
    completed_sets = Set.objects.filter(
        training__user=request.user,
        training__date__range=[start_date, end_date],
        training__completed=True
    )

    # Análisis de volumen por período
    volume_data = {}
    trainings = Training.objects.filter(
        user=request.user,
        date__range=[start_date, end_date],
        completed=True
    ).order_by('date')

    for training in trainings:
        date_str = training.date.strftime('%Y-%m-%d')
        sets = Set.objects.filter(training=training)
        daily_volume = sets.aggregate(
            total_volume=Sum('weight', default=0),
            total_sets=Count('id')
        )
        if daily_volume['total_volume'] > 0:
            volume_data[date_str] = daily_volume['total_volume']

    # Estadísticas generales de volumen
    volume_stats = completed_sets.aggregate(
        total_volume=Sum('weight', default=0),
        avg_volume=Avg('weight', default=0),
        max_volume=Max('weight', default=0),
        min_volume=Min('weight', default=0)
    )

    # Volumen por grupo muscular
    muscle_group_stats = {}
    total_volume = volume_stats['total_volume'] or 0

    muscle_groups = Training.objects.filter(
        user=request.user,
        date__range=[start_date, end_date],
        completed=True
    ).values('exercise__category').distinct()

    for group in muscle_groups:
        category = group['exercise__category'] or 'Sin categoría'
        group_volume = completed_sets.filter(
            training__exercise__category=category
        ).aggregate(volume=Sum('weight', default=0))['volume']
        
        if group_volume > 0:
            percentage = (group_volume / total_volume * 100) if total_volume > 0 else 0
            muscle_group_stats[category] = {
                'volume': group_volume,
                'percentage': percentage
            }

    context = {
        'period': period,
        'volume_data': volume_data,
        'total_volume': volume_stats['total_volume'] or 0,
        'avg_volume': volume_stats['avg_volume'] or 0,
        'max_volume': volume_stats['max_volume'] or 0,
        'min_volume': volume_stats['min_volume'] or 0,
        'muscle_group_stats': muscle_group_stats
    }
    return render(request, 'stats/volume_analysis.html', context)

@login_required
def personal_records(request):
    """Vista de récords personales."""
    # Récords por ejercicio
    exercise_records = {}
    exercises = Exercise.objects.filter(training__user=request.user).distinct()

    for exercise in exercises:
        records = Training.objects.filter(
            user=request.user,
            exercise=exercise,
            completed=True
        ).aggregate(
            max_weight=Max('training_sets__weight'),
            max_reps=Max('training_sets__reps'),
            total_volume=Sum('training_sets__weight'),
            avg_weight=Avg('training_sets__weight')
        )
        
        # Obtener la fecha del récord de peso
        max_weight_set = Set.objects.filter(
            training__user=request.user,
            training__exercise=exercise,
            weight=records['max_weight']
        ).first()

        records['date_achieved'] = max_weight_set.training.date if max_weight_set else None
        exercise_records[exercise.name] = records

    context = {
        'exercise_records': exercise_records
    }
    return render(request, 'stats/personal_records.html', context)

@login_required
def training_frequency(request):
    """Vista de frecuencia de entrenamiento."""
    period = request.GET.get('period', 'month')
    end_date = datetime.now().date()

    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=365)

    # Lista de días de la semana en español
    days_of_week = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Lista de horas (de 5:00 a 23:00)
    hours = list(range(5, 24))

    # Inicializar datos de frecuencia
    frequency_data = {day: {hour: 0 for hour in hours} for day in days_of_week}

    # Obtener todos los entrenamientos en el período
    trainings = Training.objects.filter(
        user=request.user,
        date__range=[start_date, end_date],
        completed=True
    )

    # Calcular distribución por día
    day_distribution = {day: {'count': 0, 'percentage': 0} for day in days_of_week}
    total_trainings = trainings.count()

    for training in trainings:
        day = training.day_of_week
        # Asumimos que el campo created_at tiene la hora del entrenamiento
        hour = training.created_at.hour
        
        if day in frequency_data and hour in frequency_data[day]:
            frequency_data[day][hour] += 1
        
        if day in day_distribution:
            day_distribution[day]['count'] += 1

    # Calcular porcentajes
    if total_trainings > 0:
        for day in day_distribution:
            count = day_distribution[day]['count']
            day_distribution[day]['percentage'] = (count / total_trainings) * 100

    # Estadísticas de duración
    duration_stats = trainings.filter(duration__isnull=False).aggregate(
        avg_duration=Avg('duration'),
        max_duration=Max('duration'),
        min_duration=Min('duration')
    )

    # Datos de tendencia (últimos 30 días)
    trend_data = {}
    for i in range(30):
        date = end_date - timedelta(days=i)
        count = trainings.filter(date=date).count()
        if count > 0:  # Solo incluir días con entrenamientos
            trend_data[date] = count

    context = {
        'period': period,
        'days_of_week': days_of_week,
        'hours': hours,
        'frequency_data': frequency_data,
        'day_distribution': day_distribution,
        'avg_duration': duration_stats.get('avg_duration', 0) or 0,
        'max_duration': duration_stats.get('max_duration', 0) or 0,
        'min_duration': duration_stats.get('min_duration', 0) or 0,
        'trend_data': dict(sorted(trend_data.items())),  # Ordenar por fecha
    }

    return render(request, 'stats/training_frequency.html', context) 