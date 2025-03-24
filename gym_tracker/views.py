from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from gym_tracker.exercises.models import Exercise
from gym_tracker.workouts.models import Workout
from gym_tracker.trainings.models import Training
from django.db.models import Count, Sum

# Vista para servir la plantilla principal de React
def index(request):
    return render(request, 'index.html')

def csrf_failure(request, reason=""):
    """
    Vista personalizada para manejar errores CSRF.
    En desarrollo, esto permitirá que se muestre un mensaje más amigable
    y se evite el error 403.
    """
    context = {'reason': reason}
    return render(request, 'login.html', context)

@login_required
def home_view(request):
    """
    Vista principal del dashboard que muestra estadísticas y accesos rápidos.
    """
    # Obtener datos para los widgets
    user = request.user
    
    # Contar ejercicios
    total_exercises = Exercise.objects.count()
    
    # Contar entrenamientos (workouts)
    try:
        total_workouts = Workout.objects.filter(user=user).count()
    except:
        total_workouts = 0
    
    # Contar entrenamientos completados
    try:
        completed_trainings = Training.objects.filter(user=user, completed=True).count()
        total_trainings = Training.objects.filter(user=user).count()
        
        # Calcular porcentaje de progreso
        if total_trainings > 0:
            progress_percentage = int((completed_trainings / total_trainings) * 100)
        else:
            progress_percentage = 0
    except:
        completed_trainings = 0
        total_trainings = 0
        progress_percentage = 0
    
    # Preparar contexto para la plantilla
    context = {
        'user': user,
        'total_exercises': total_exercises,
        'total_workouts': total_workouts,
        'completed_trainings': completed_trainings,
        'total_trainings': total_trainings,
        'progress_percentage': progress_percentage,
    }
    
    return render(request, 'index.html', context)
