from rest_framework import generics, permissions
from django.shortcuts import render, redirect, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from django.db.models import Prefetch
from trainers.models import TrainerTraining
from django.db.models import Count
from itertools import groupby
from operator import attrgetter
from django.views.generic import DetailView
from django.db.models.functions import TruncMonth
from datetime import datetime

from ..models import Training
from ..serializers import TrainingSerializer
from ...core.permissions import IsOwner
from ..api_docs import TRAINING_LIST_CREATE, TRAINING_DETAIL

class TrainingListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear entrenamientos.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'trainings/routine_list.html'

    def get(self, request, *args, **kwargs):
        # Obtener rutinas personales del usuario
        personal_trainings = Training.objects.filter(
            user=self.request.user
        ).exclude(
            id__in=TrainerTraining.objects.filter(
                user=self.request.user
            ).values_list('id', flat=True)
        ).order_by('-date')
        
        # Obtener rutinas asignadas por entrenadores
        assigned_trainings = Training.objects.filter(
            id__in=TrainerTraining.objects.filter(
                user=self.request.user
            ).values_list('id', flat=True)
        ).order_by('-date')
        
        # Agrupar entrenamientos por mes
        personal_routines = self._group_trainings_by_month(personal_trainings, is_assigned=False)
        assigned_routines = self._group_trainings_by_month(assigned_trainings, is_assigned=True)
        
        # Combinar todas las rutinas
        routines = personal_routines + assigned_routines
        
        # Ordenar por fecha más reciente
        routines.sort(key=lambda x: datetime.strptime(x['month_year'], '%B %Y'), reverse=True)

        context = {
            'routines': routines,
            'personal_count': len(personal_routines),
            'assigned_count': len(assigned_routines)
        }
        return Response(context)

    def _group_trainings_by_month(self, trainings, is_assigned=False):
        routines = []
        training_by_month = {}
        
        for training in trainings:
            month_year = training.date.strftime('%B %Y')
            
            if month_year not in training_by_month:
                training_by_month[month_year] = {
                    'name': f"{'Rutina Asignada' if is_assigned else 'Mi Rutina Personal'} - {month_year}",
                    'month_year': month_year,
                    'created_at': training.created_at,
                    'creator': training.user.get_full_name() or training.user.username,
                    'is_assigned': is_assigned,
                    'training_days': set(),
                    'description': f"{'Rutina asignada por entrenador' if is_assigned else 'Mi rutina de entrenamiento personal'} - {month_year}"
                }
            
            if training.day_of_week:
                training_by_month[month_year]['training_days'].add(training.day_of_week)
        
        # Convertir los sets de días a listas ordenadas
        for routine in training_by_month.values():
            routine['training_days'] = sorted(list(routine['training_days']))
            routines.append(routine)
        
        return routines

    def get_queryset(self):
        return Training.objects.filter(
            user=self.request.user
        ).select_related(
            'exercise', 
            'user'
        ).order_by('-date', '-created_at')

    def perform_create(self, serializer):
        """
        Asigna el usuario autenticado al crear un nuevo entrenamiento.
        """
        serializer.save(user=self.request.user)

class TrainingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un entrenamiento.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    @swagger_auto_schema(**TRAINING_DETAIL['get'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(**TRAINING_DETAIL['put'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(**TRAINING_DETAIL['delete'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Asegura que solo se puedan acceder a los entrenamientos del usuario.
        """
        return Training.objects.filter(user=self.request.user)

class RoutineDatesView(generics.ListAPIView):
    """
    Vista para listar las fechas de una rutina específica.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'trainings/routine_dates.html'

    def get(self, request, *args, **kwargs):
        month_year = kwargs.get('routine_name')
        try:
            date = datetime.strptime(month_year, '%B %Y')
            queryset = self.get_queryset().filter(date__month=date.month, date__year=date.year)
        except ValueError:
            queryset = self.get_queryset().none()
        
        # Agrupar por fecha
        trainings_by_date = {}
        for training in queryset:
            if training.date not in trainings_by_date:
                trainings_by_date[training.date] = {
                    'date': training.date,
                    'completed_count': 0,
                    'total_count': 0
                }
            trainings_by_date[training.date]['total_count'] += 1
            if training.completed:
                trainings_by_date[training.date]['completed_count'] += 1

        context = {
            'routine_name': f"Fer Rutina {month_year}",
            'dates': sorted(trainings_by_date.values(), key=lambda x: x['date'], reverse=True)
        }
        return Response(context)

    def get_queryset(self):
        return Training.objects.filter(user=self.request.user).select_related(
            'exercise', 'user'
        )

class RoutineDateExercisesView(generics.ListAPIView):
    """
    Vista para listar los ejercicios de una fecha específica de una rutina.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'trainings/routine_exercises.html'

    def get(self, request, *args, **kwargs):
        routine_name = kwargs.get('routine_name')
        date = kwargs.get('date')
        
        trainings = self.get_queryset().filter(
            exercise__muscle_group=routine_name,
            date=date
        )

        context = {
            'routine_name': routine_name,
            'date': date,
            'trainings': trainings
        }
        return Response(context)

    def get_queryset(self):
        return Training.objects.filter(user=self.request.user).select_related(
            'exercise', 'user'
        ).prefetch_related('training_sets') 