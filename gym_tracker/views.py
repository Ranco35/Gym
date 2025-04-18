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
    """Vista para la página de inicio."""
    return render(request, 'home.html')

@login_required
def dashboard_view(request):
    """Vista para el dashboard del usuario."""
    return render(request, 'dashboard.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Vista para obtener los datos del usuario actual autenticado
    """
    serializer = UserSerializer(request.user)
    return JsonResponse(serializer.data)
