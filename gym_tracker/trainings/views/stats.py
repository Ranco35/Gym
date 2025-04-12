from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractMonth
from datetime import datetime, timedelta

from ..models import Training, Set
from gym_tracker.exercises.models import Exercise

@login_required
def training_stats(request):
    """
    Muestra estadísticas de los entrenamientos del usuario.
    """
    return render(request, 'trainings/stats.html')

@login_required
def dashboard(request):
    """
    Muestra el dashboard con estadísticas generales.
    """
    # Obtener estadísticas generales
    total_trainings = Training.objects.filter(user=request.user).count()
    completed_trainings = Training.objects.filter(user=request.user, completed=True).count()
    total_sets = Set.objects.filter(training__user=request.user).count()
    
    # Obtener los últimos 5 entrenamientos
    recent_trainings = Training.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Obtener los ejercicios más frecuentes
    top_exercises = Exercise.objects.filter(
        set__training__user=request.user
    ).annotate(
        count=Count('set')
    ).order_by('-count')[:5]
    
    context = {
        'total_trainings': total_trainings,
        'completed_trainings': completed_trainings,
        'total_sets': total_sets,
        'recent_trainings': recent_trainings,
        'top_exercises': top_exercises
    }
    
    return render(request, 'trainings/dashboard.html', context) 