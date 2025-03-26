from django.shortcuts import render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from gym_tracker.exercises.models import Exercise
from gym_tracker.workouts.models import Workout
from gym_tracker.trainings.models import Training
from django.db.models import Count, Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from gym_tracker.users.serializers import UserSerializer

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
    total_workouts = Workout.objects.filter(user=user).count() if hasattr(Workout, 'objects') else 0
    
    # Contar entrenamientos completados
    if hasattr(Training, 'objects'):
        completed_trainings = Training.objects.filter(user=user, completed=True).count()
        total_trainings = Training.objects.filter(user=user).count()
        
        # Calcular porcentaje de progreso
        progress_percentage = int((completed_trainings / total_trainings) * 100) if total_trainings > 0 else 0
    else:
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
    
    return render(request, 'home.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Vista para obtener los datos del usuario actual autenticado
    """
    serializer = UserSerializer(request.user)
    return JsonResponse(serializer.data)
