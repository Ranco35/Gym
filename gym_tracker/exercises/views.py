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
            # Crear un diccionario con los campos requeridos
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'category': request.POST.get('category'),
                'difficulty': request.POST.get('difficulty'),
            }
            
            # Añadir campos opcionales si existen en el modelo
            optional_fields = [
                'primary_muscles', 
                'secondary_muscles', 
                'equipment', 
                'instructions', 
                'tips'
            ]
            
            for field in optional_fields:
                if hasattr(Exercise, field) and request.POST.get(field):
                    data[field] = request.POST.get(field)
            
            # Crear el ejercicio con los datos limpios
            exercise = Exercise.objects.create(**data)
            messages.success(request, 'Ejercicio creado exitosamente.')
            return redirect('exercises:exercise-list')
        except Exception as e:
            messages.error(request, f'Error al crear el ejercicio: {str(e)}')
    
    return render(request, 'exercises/exercise_form.html')