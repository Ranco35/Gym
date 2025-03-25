from rest_framework import generics, permissions
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.contrib import messages

from .models import Training
from .serializers import TrainingSerializer
from gym_tracker.exercises.models import Exercise
from gym_tracker.workouts.models import WeeklyRoutine, RoutineDay, RoutineExercise

# API REST Views
class TrainingListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear entrenamientos.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Obtiene los entrenamientos del usuario autenticado.
        """
        return Training.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asigna el usuario autenticado al crear un nuevo entrenamiento.
        """
        serializer.save(user=self.request.user)
        
    def get(self, request, *args, **kwargs):
        # Si la solicitud es para HTML, renderiza el template
        if 'text/html' in request.headers.get('Accept', ''):
            trainings = self.get_queryset().order_by('-date')
            
            # Filtros
            date_filter = request.GET.get('date')
            exercise_filter = request.GET.get('exercise')
            day_filter = request.GET.get('day')
            
            if date_filter:
                trainings = trainings.filter(date=date_filter)
            if exercise_filter:
                trainings = trainings.filter(exercise_id=exercise_filter)
            if day_filter:
                trainings = trainings.filter(day_of_week=day_filter)
                
            exercises = Exercise.objects.all()
            # Obtener rutinas del usuario para el formulario de entrenamiento basado en rutina
            routines = WeeklyRoutine.objects.filter(user=request.user).order_by('-created_at')
            
            return render(request, 'trainings/training_list.html', {
                'trainings': trainings,
                'exercises': exercises,
                'routines': routines
            })
        # Si no, continúa con la respuesta API normal
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Si la solicitud viene del formulario HTML
        if 'text/html' in request.headers.get('Accept', ''):
            # Extraer los datos del formulario
            exercise_id = request.POST.get('exercise')
            date_str = request.POST.get('date')
            sets = request.POST.get('sets', 3)
            reps = request.POST.get('reps', 10)
            weight = request.POST.get('weight', None)
            rest_time = request.POST.get('rest_time', 60)
            intensity = request.POST.get('intensity', 'Moderado')
            notes = request.POST.get('notes', '')
            completed = 'completed' in request.POST
            
            # Convertir fecha a objeto Date
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Determinar el día de la semana
            day_of_week = date.strftime('%A')
            # Traducir al español
            days_translation = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            day_of_week = days_translation.get(day_of_week, day_of_week)
            
            # Crear el entrenamiento
            Training.objects.create(
                user=request.user,
                exercise_id=exercise_id,
                date=date,
                day_of_week=day_of_week,
                sets=sets,
                reps=reps,
                weight=weight if weight and weight != '' else None,
                rest_time=rest_time,
                intensity=intensity,
                notes=notes,
                completed=completed
            )
            
            return redirect('trainings:training-list-create')
        
        # Si no, continuar con la creación API normal
        return super().post(request, *args, **kwargs)

class TrainingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un entrenamiento.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar por entrenamientos del usuario autenticado.
        """
        return Training.objects.filter(user=self.request.user)

@login_required
def delete_training(request, pk):
    """
    Elimina un entrenamiento.
    """
    training = get_object_or_404(Training, pk=pk, user=request.user)
    training.delete()
    return redirect('trainings:training-list-create')

@login_required
@require_POST
@csrf_exempt
def toggle_complete(request, pk):
    """
    Marca o desmarca un entrenamiento como completado.
    """
    training = get_object_or_404(Training, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        training.completed = data.get('completed', False)
        training.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def get_routine_days(request, routine_id):
    """
    Retorna los días y ejercicios de una rutina específica.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=routine_id, user=request.user)
    
    days = []
    for day in routine.days.all():
        exercises = []
        for routine_exercise in day.exercises.all():
            exercises.append({
                'id': routine_exercise.exercise.id,
                'name': routine_exercise.exercise.name,
                'sets': routine_exercise.sets,
                'reps': routine_exercise.reps,
                'weight': routine_exercise.weight,
                'rest_time': routine_exercise.rest_time
            })
        
        days.append({
            'id': day.id,
            'day_of_week': day.day_of_week,
            'focus': day.focus,
            'exercises': exercises
        })
    
    return JsonResponse({
        'routine': {
            'id': routine.id,
            'name': routine.name
        },
        'days': days
    })

@login_required
@require_POST
def create_training_from_routine(request):
    """
    Crea entrenamientos a partir de un día de una rutina.
    """
    routine_id = request.POST.get('routine_id')
    routine_day_id = request.POST.get('routine_day_id')
    training_date_str = request.POST.get('training_date')
    
    # Validar datos
    if not routine_id or not routine_day_id or not training_date_str:
        return JsonResponse({'status': 'error', 'message': 'Faltan datos requeridos'}, status=400)
    
    # Obtener rutina y día
    routine = get_object_or_404(WeeklyRoutine, pk=routine_id, user=request.user)
    routine_day = get_object_or_404(RoutineDay, pk=routine_day_id, routine=routine)
    
    # Convertir fecha
    training_date = datetime.datetime.strptime(training_date_str, '%Y-%m-%d').date()
    
    # Determinar el día de la semana real de la fecha seleccionada
    real_day_of_week = training_date.strftime('%A')
    days_translation = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    real_day_of_week = days_translation.get(real_day_of_week, real_day_of_week)
    
    # Crear un entrenamiento por cada ejercicio en el día de la rutina
    created_count = 0
    for routine_exercise in routine_day.exercises.all():
        Training.objects.create(
            user=request.user,
            exercise=routine_exercise.exercise,
            date=training_date,
            day_of_week=real_day_of_week,
            sets=routine_exercise.sets,
            reps=routine_exercise.reps,
            weight=routine_exercise.weight,
            rest_time=routine_exercise.rest_time,
            intensity='Moderado',  # Valor predeterminado
            notes=f"Rutina: {routine.name} - Día: {routine_day.day_of_week} ({routine_day.focus})",
            completed=False
        )
        created_count += 1
    
    # Redirigir a la lista de entrenamientos
    return redirect('trainings:training-list-create')

@login_required
def execute_training(request, routine_id, day_id):
    """
    Vista para ejecutar un entrenamiento paso a paso.
    Muestra los ejercicios uno por uno y permite modificar los parámetros.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=routine_id, user=request.user)
    routine_day = get_object_or_404(RoutineDay, pk=day_id, routine=routine)
    
    # Obtener todos los ejercicios del día
    exercises = routine_day.exercises.all().order_by('order')
    
    if not exercises.exists():
        messages.error(request, "No hay ejercicios configurados para este día de entrenamiento.")
        return redirect('workouts:workout-detail', pk=routine_id)
    
    # Obtener el ejercicio actual (por defecto el primero)
    current_exercise_index = int(request.GET.get('step', 0))
    
    # Asegurar que el índice esté dentro de los límites
    if current_exercise_index < 0:
        current_exercise_index = 0
    elif current_exercise_index >= exercises.count():
        current_exercise_index = exercises.count() - 1
    
    current_exercise = exercises[current_exercise_index]
    
    # Progreso del entrenamiento
    progress = {
        'current': current_exercise_index + 1,
        'total': exercises.count(),
        'percentage': int(((current_exercise_index + 1) / exercises.count()) * 100)
    }
    
    # Manejar el envío del formulario para el ejercicio actual
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        sets = request.POST.get('sets', current_exercise.sets)
        reps = request.POST.get('reps', current_exercise.reps)
        weight = request.POST.get('weight', current_exercise.weight or '')
        
        # Guardar el entrenamiento para este ejercicio
        training_date = datetime.datetime.now().date()
        
        # Determinar el día de la semana real
        real_day_of_week = training_date.strftime('%A')
        days_translation = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        real_day_of_week = days_translation.get(real_day_of_week, real_day_of_week)
        
        # Crear el registro de entrenamiento
        Training.objects.create(
            user=request.user,
            exercise=current_exercise.exercise,
            date=training_date,
            day_of_week=real_day_of_week,
            sets=sets,
            reps=reps,
            weight=weight,
            rest_time=current_exercise.rest_time,
            intensity='Moderado',  # Por defecto
            notes=f"Rutina: {routine.name} - Día: {routine_day.day_of_week} ({routine_day.focus})",
            completed=True  # Marcado como completado automáticamente
        )
        
        # Ir al siguiente ejercicio
        next_exercise = current_exercise_index + 1
        
        # Si llegamos al final, redirigir a la página de resumen
        if next_exercise >= exercises.count():
            messages.success(request, "¡Entrenamiento completado con éxito!")
            return redirect('trainings:training-list-create')
        
        # Redirigir al siguiente ejercicio
        return redirect(f"{request.path}?step={next_exercise}")
    
    return render(request, 'trainings/execute_training.html', {
        'routine': routine,
        'routine_day': routine_day,
        'current_exercise': current_exercise,
        'progress': progress,
        'exercise_index': current_exercise_index,
        'total_exercises': exercises.count(),
        'next_index': current_exercise_index + 1 if current_exercise_index + 1 < exercises.count() else None,
        'prev_index': current_exercise_index - 1 if current_exercise_index > 0 else None,
    })