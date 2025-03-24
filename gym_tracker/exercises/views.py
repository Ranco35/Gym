from rest_framework import generics
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Exercise
from .serializers import ExerciseSerializer

class ExerciseListView(generics.ListAPIView):
    """
    Vista para listar todos los ejercicios.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get(self, request, *args, **kwargs):
        if request.path.startswith('/api/'):
            return super().get(request, *args, **kwargs)
        return render(request, 'exercises/exercise_list.html', {
            'exercises': self.get_queryset()
        })

class ExerciseDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener los detalles de un ejercicio específico.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get(self, request, *args, **kwargs):
        if request.path.startswith('/api/'):
            return super().get(request, *args, **kwargs)
        exercise = self.get_object()
        return render(request, 'exercises/exercise_detail.html', {
            'exercise': exercise
        })

def exercise_create(request):
    """
    Vista para crear un nuevo ejercicio.
    """
    if request.method == 'POST':
        try:
            exercise = Exercise.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                difficulty=request.POST.get('difficulty'),
                primary_muscles=request.POST.get('primary_muscles'),
                secondary_muscles=request.POST.get('secondary_muscles'),
                equipment=request.POST.get('equipment'),
                instructions=request.POST.get('instructions'),
                tips=request.POST.get('tips')
            )
            messages.success(request, 'Ejercicio creado exitosamente.')
            return redirect('web:exercises:exercise-list')
        except Exception as e:
            messages.error(request, f'Error al crear el ejercicio: {str(e)}')
    
    return render(request, 'exercises/exercise_form.html')