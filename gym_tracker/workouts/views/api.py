from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden

from ..models import Workout, WeeklyRoutine, RoutineDay, RoutineExercise
from ..serializers import (
    WorkoutSerializer,
    WeeklyRoutineSerializer,
    WeeklyRoutineCreateSerializer,
    RoutineDaySerializer,
    RoutineDayCreateSerializer,
    RoutineExerciseSerializer
)

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