from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Max, Min
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear
from datetime import datetime, timedelta
from gym_tracker.trainings.models import Training, Set
from gym_tracker.exercises.models import Exercise, ExerciseCategory
from gym_tracker.workouts.models import WeeklyRoutine
from django.db import connection

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
    
    # Consulta SQL directa para obtener nombres de categorías y volúmenes
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ec.name as category_name, SUM(s.weight) as total_volume
            FROM trainings_set s
            JOIN trainings_training t ON s.training_id = t.id
            JOIN exercises_exercise e ON t.exercise_id = e.id
            JOIN exercises_exercisecategory ec ON e.category_id = ec.id
            WHERE t.user_id = %s
            AND t.date BETWEEN %s AND %s
            AND t.completed = true
            GROUP BY ec.id, ec.name
            HAVING SUM(s.weight) > 0
            ORDER BY ec.name
        """, [request.user.id, start_date, end_date])
        
        results = cursor.fetchall()
        
        # Calcular volumen total para porcentajes
        sql_total_volume = sum(row[1] for row in results) or 0
        
        # Crear diccionario con los resultados
        for row in results:
            category_name = row[0]
            volume = row[1]
            percentage = (volume / sql_total_volume * 100) if sql_total_volume > 0 else 0
            
            muscle_group_stats[category_name] = {
                'volume': volume,
                'percentage': percentage
            }
    
    print("MUSCLE GROUP STATS:", muscle_group_stats)

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
    period = request.GET.get('period', 'all')
    end_date = datetime.now().date()
    
    # Definir el rango de fechas según el período seleccionado
    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = None  # Sin límite para todos los datos
    
    # Récords por ejercicio
    exercise_records = {}
    
    # Variables para el resumen total
    total_max_weight = 0
    total_max_weight_date = None
    total_max_reps = 0
    total_max_reps_date = None
    total_max_volume = 0
    total_max_volume_date = None
    
    # Filtrar ejercicios realizados por el usuario
    exercises = Exercise.objects.filter(training__user=request.user).distinct()

    for exercise in exercises:
        # Crear el filtro base para los entrenamientos
        training_filter = {
            'user': request.user,
            'exercise': exercise,
            'completed': True
        }
        
        # Añadir filtro de fecha si se ha seleccionado un período
        if start_date:
            training_filter['date__range'] = [start_date, end_date]
        
        # Obtener récords para este ejercicio
        records = Training.objects.filter(**training_filter).aggregate(
            max_weight=Max('training_sets__weight'),
            max_reps=Max('training_sets__reps'),
            total_volume=Sum('training_sets__weight'),
            avg_weight=Avg('training_sets__weight')
        )
        
        # Si no hay datos para este ejercicio, continuar con el siguiente
        if not records['max_weight'] and not records['max_reps'] and not records['total_volume']:
            continue
            
        # Obtener las fechas de los récords
        
        # Fecha del récord de peso máximo
        max_weight_set = Set.objects.filter(
            training__user=request.user,
            training__exercise=exercise,
            weight=records['max_weight']
        ).order_by('-training__date').first()
        
        records['max_weight_date'] = max_weight_set.training.date if max_weight_set else None
        
        # Fecha del récord de repeticiones máximas
        max_reps_set = Set.objects.filter(
            training__user=request.user,
            training__exercise=exercise,
            reps=records['max_reps']
        ).order_by('-training__date').first()
        
        records['max_reps_date'] = max_reps_set.training.date if max_reps_set else None
        
        # Fecha del volumen total (usamos la fecha más reciente)
        volume_training = Training.objects.filter(
            **training_filter
        ).order_by('-date').first()
        
        records['total_volume_date'] = volume_training.date if volume_training else None
        
        # Actualizar los totales para el resumen
        if records['max_weight'] and records['max_weight'] > total_max_weight:
            total_max_weight = records['max_weight']
            total_max_weight_date = records['max_weight_date']
            
        if records['max_reps'] and records['max_reps'] > total_max_reps:
            total_max_reps = records['max_reps']
            total_max_reps_date = records['max_reps_date']
            
        # Para volumen, sumamos todos los volúmenes de ejercicios
        if records['total_volume']:
            total_max_volume += records['total_volume']
            # Para la fecha, usamos la más reciente
            if not total_max_volume_date or (records['total_volume_date'] and records['total_volume_date'] > total_max_volume_date):
                total_max_volume_date = records['total_volume_date']
        
        # Agregar al diccionario de récords
        exercise_records[exercise.name] = records
    
    # Contexto para la plantilla
    context = {
        'exercise_records': exercise_records,
        'period': period,
        'total_max_weight': total_max_weight,
        'total_max_weight_date': total_max_weight_date,
        'total_max_reps': total_max_reps,
        'total_max_reps_date': total_max_reps_date,
        'total_max_volume': total_max_volume,
        'total_max_volume_date': total_max_volume_date
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