from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractMonth
from datetime import datetime, timedelta
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from rest_framework import generics, permissions
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from .models import Training, Set, UserProfile, Exercise
from .serializers import TrainingSerializer
from gym_tracker.exercises.models import Exercise as GymExercise
from gym_tracker.workouts.models import WeeklyRoutine as Routine, RoutineDay, RoutineExercise
from .forms import TrainingForm, SetForm
from trainers.models import LiveTrainingSession, TrainerStudent, TrainerTraining, TrainerTrainingDay, TrainerSet

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
            
            # Agrupar entrenamientos por fecha y rutina
            grouped_trainings = {}
            for training in trainings:
                date_str = training.date.strftime('%Y-%m-%d')
                # Extraer el nombre de la rutina y el día de las notas
                routine_info = 'Ejercicios Individuales'
                if training.notes and 'Rutina:' in training.notes:
                    try:
                        routine_parts = training.notes.split(' - ')
                        routine_name = routine_parts[0].replace('Rutina: ', '')
                        day_info = routine_parts[1] if len(routine_parts) > 1 else ''
                        routine_info = f"{routine_name} - {day_info}"
                    except:
                        pass
                
                if date_str not in grouped_trainings:
                    grouped_trainings[date_str] = {}
                
                if routine_info not in grouped_trainings[date_str]:
                    grouped_trainings[date_str][routine_info] = []
                
                # Asegurarse de que el entrenamiento tenga toda la información necesaria
                training.routine_name = routine_info
                # Añadir el conteo de series completadas al objeto de entrenamiento
                training.completed_sets_count = training.completed_sets_count
                # Añadir el conteo de series extras
                training.extra_sets_count = training.extra_sets_count
                grouped_trainings[date_str][routine_info].append(training)
            
            # Ordenar los entrenamientos dentro de cada rutina por el orden original
            for date in grouped_trainings:
                for routine in grouped_trainings[date]:
                    trainings_list = grouped_trainings[date][routine]
                    trainings_list.sort(key=lambda x: x.id)
                    
                    # Calcular el progreso total y verificar si hay pendientes
                    total_sets = sum(t.total_sets for t in trainings_list)
                    completed_sets = sum(t.completed_sets_count for t in trainings_list if "PENDIENTE" not in t.notes)
                    has_pending = any("PENDIENTE" in t.notes for t in trainings_list)
                    
                    # Verificar si todos los ejercicios tienen completadas todas sus series
                    all_sets_completed = True
                    # Solo consideramos como completado si se han hecho TODAS las series y hay al menos una serie por cada ejercicio
                    for t in trainings_list:
                        if t.completed_sets_count < t.total_sets:
                            all_sets_completed = False
                            break
                    
                    # Si algún ejercicio tiene 0 series completadas, el porcentaje no puede ser 100%
                    has_zero_progress = any(t.completed_sets_count == 0 for t in trainings_list)
                    
                    # Calcular porcentaje (mostrar 100% solo si todas las series están completadas y no hay ejercicios con 0 progreso)
                    if all_sets_completed and not has_pending and not has_zero_progress:
                        percentage = 100
                    else:
                        # Modificamos el cálculo para contar por ejercicios completos vs total de ejercicios
                        completed_exercises = sum(1 for t in trainings_list if t.completed_sets_count >= t.total_sets)
                        total_exercises = len(trainings_list)
                        percentage = int((completed_exercises / total_exercises * 100) if total_exercises > 0 else 0)
                    
                    # Añadir información de progreso para esta rutina
                    grouped_trainings[date][routine] = {
                        'trainings': trainings_list,
                        'progress': {
                            'total_sets': total_sets,
                            'completed_sets': completed_sets,
                            'percentage': percentage,
                            'has_pending': has_pending
                        }
                    }
            
            exercises = GymExercise.objects.all()
            # Obtener rutinas del usuario para el formulario de entrenamiento basado en rutina
            routines = Routine.objects.filter(user=request.user).order_by('-created_at')
            
            return render(request, 'trainings/training_list.html', {
                'grouped_trainings': grouped_trainings,
                'exercises': exercises,
                'routines': routines,
                'today': timezone.now().date()
            })
        # Si no, continúa con la respuesta API normal
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Si la solicitud viene del formulario HTML
        if 'text/html' in request.headers.get('Accept', ''):
            # Extraer los datos del formulario
            exercise_id = request.POST.get('exercise')
            date_str = request.POST.get('date')
            total_sets = request.POST.get('sets', 3)
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
                total_sets=total_sets,
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
@require_POST
def delete_training(request, pk):
    """
    Elimina un entrenamiento.
    """
    try:
        training = get_object_or_404(Training, pk=pk, user=request.user)
        training.delete()
        messages.success(request, 'Entrenamiento eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el entrenamiento: {str(e)}')
    
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
    routine = get_object_or_404(Routine, pk=routine_id, user=request.user)
    
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
    Prepara la ejecución de entrenamiento paso a paso.
    """
    routine_id = request.POST.get('routine_id')
    routine_day_id = request.POST.get('routine_day_id')
    training_date_str = request.POST.get('training_date')
    
    # Validar datos
    if not routine_id or not routine_day_id or not training_date_str:
        messages.error(request, 'Faltan datos requeridos')
        return redirect('trainings:training-list-create')
    
    # Guardar la fecha en la sesión para usarla en execute_training
    request.session['training_date'] = training_date_str
    
    # Redirigir a la vista de ejecución de entrenamiento
    return redirect('trainings:execute-training', routine_id=routine_id, day_id=routine_day_id)

@login_required
def execute_training(request, routine_id, day_id):
    """
    Vista para ejecutar un entrenamiento paso a paso.
    Muestra los ejercicios uno por uno y permite modificar los parámetros.
    """
    # Convertir IDs a enteros y verificar si son válidos (diferentes de 0)
    try:
        routine_id = int(routine_id)
        day_id = int(day_id)
    except (ValueError, TypeError):
        messages.warning(request, "IDs de rutina o día inválidos")
        return redirect('trainings:training-list-create')
        
    if routine_id == 0 or day_id == 0:
        messages.warning(request, "Por favor, selecciona una rutina y un día válidos")
        return redirect('trainings:training-list-create')
    
    # Intentar obtener rutina como WeeklyRoutine o como TrainerTraining
    routine = None
    routine_day = None
    is_trainer_routine = False
    
    try:
        # Primero intentar obtener como WeeklyRoutine
        routine = get_object_or_404(Routine, pk=routine_id, user=request.user)
        routine_day = get_object_or_404(RoutineDay, pk=day_id, routine=routine)
    except:
        # Si falla, intentar obtener como TrainerTraining
        try:
            routine = get_object_or_404(TrainerTraining, pk=routine_id, user=request.user)
            routine_day = get_object_or_404(TrainerTrainingDay, pk=day_id, training=routine)
            is_trainer_routine = True
        except:
            messages.error(request, "No se encontró la rutina especificada.")
            return redirect('trainings:training-list-create')
    
    # Obtener la fecha de entrenamiento de la sesión
    training_date_str = request.session.get('training_date')
    if not training_date_str:
        messages.error(request, "No se encontró la fecha de entrenamiento")
        return redirect('trainings:training-list-create')
    
    training_date = datetime.strptime(training_date_str, '%Y-%m-%d').date()
    
    # Obtener todos los ejercicios del día ordenados
    exercises = []
    if is_trainer_routine:
        # Para TrainerTraining, usar TrainerSet
        exercise_objects = routine_day.sets.all().order_by('order')
        
        # Convertir TrainerSet a formato compatible con la vista
        for trainer_set in exercise_objects:
            # Buscar o crear el objeto Exercise correspondiente
            # Usamos filter().first() en lugar de get() para evitar MultipleObjectsReturned
            exercise_obj = GymExercise.objects.filter(name=trainer_set.exercise).first()
            if not exercise_obj:
                # Si no existe, crear un objeto temporal (no se guarda en la BD)
                exercise_obj = GymExercise(name=trainer_set.exercise)
            
            # Crear un objeto similar a RoutineExercise para mantener la compatibilidad
            exercises.append({
                'exercise': exercise_obj,
                'sets': trainer_set.sets_count,
                'reps': trainer_set.reps,
                'weight': trainer_set.weight,
                'rest_time': 60,  # Valor por defecto
                'notes': trainer_set.notes,
                'order': trainer_set.order
            })
    else:
        # Para WeeklyRoutine, usar RoutineExercise
        exercise_objects = routine_day.exercises.all().order_by('order')
        exercises = list(exercise_objects)
    
    if not exercises:
        messages.error(request, "No hay ejercicios configurados para este día de entrenamiento.")
        return redirect('trainings:training-list-create')
    
    # Obtener el ejercicio actual (por defecto el primero)
    step_param = request.GET.get('step', '0')
    try:
        current_exercise_index = int(step_param)
    except (ValueError, TypeError):
        # Si no se puede convertir a entero, usar 0 como valor predeterminado
        current_exercise_index = 0
    
    # Procesar acción de saltar ejercicio
    action = request.GET.get('action', '')
    if action == 'skip':
        # Marcar el ejercicio actual como pendiente
        if is_trainer_routine:
            exercise_obj = exercises[current_exercise_index]['exercise']
        else:
            exercise_obj = exercises[current_exercise_index].exercise
            
        # Obtener o crear el entrenamiento
        training, created = Training.objects.get_or_create(
            user=request.user,
            exercise=exercise_obj,
            date=training_date,
            defaults={
                'day_of_week': training_date.strftime('%A'),
                'total_sets': exercises[current_exercise_index]['sets'] if is_trainer_routine else exercises[current_exercise_index].sets,
                'reps': exercises[current_exercise_index]['reps'] if is_trainer_routine else exercises[current_exercise_index].reps,
                'weight': exercises[current_exercise_index]['weight'] if is_trainer_routine else exercises[current_exercise_index].weight,
                'rest_time': exercises[current_exercise_index]['rest_time'] if is_trainer_routine else exercises[current_exercise_index].rest_time,
                'intensity': 'Moderado',
                'notes': f"Rutina: {routine.name} - Día: {routine_day.day_of_week} ({routine_day.focus if hasattr(routine_day, 'focus') else ''}) - PENDIENTE",
                'completed': False
            }
        )
        
        if not created:
            # Si ya existía, actualizar para marcar como pendiente
            training.notes = training.notes.replace(" - PENDIENTE", "") + " - PENDIENTE"
            training.completed = False
            training.save()
            
        messages.warning(request, f"Ejercicio {exercise_obj.name} marcado como pendiente.")
        
        # Si hay siguiente ejercicio, ir a él
        if current_exercise_index + 1 < len(exercises):
            return redirect(f"{request.path}?step={current_exercise_index + 1}")
        else:
            messages.success(request, "No hay más ejercicios. Entrenamiento finalizado.")
            return redirect('trainings:training-list-create')
    
    # Asegurar que el índice esté dentro de los límites
    if current_exercise_index < 0:
        current_exercise_index = 0
    elif current_exercise_index >= len(exercises):
        current_exercise_index = len(exercises) - 1
    
    current_exercise = exercises[current_exercise_index]
    
    # Obtener ejercicio anterior y siguiente
    prev_exercise = None
    next_exercise = None
    if current_exercise_index > 0:
        prev_exercise = exercises[current_exercise_index - 1]
    if current_exercise_index < len(exercises) - 1:
        next_exercise = exercises[current_exercise_index + 1]
    
    # Para TrainerTraining, necesitamos adaptar algunos objetos
    if is_trainer_routine:
        # Obtener el objeto exercise para histórico
        exercise_obj = current_exercise['exercise']
        exercise_sets = current_exercise['sets']
        exercise_reps = current_exercise['reps']
        exercise_weight = current_exercise['weight']
        exercise_rest_time = current_exercise['rest_time']
    else:
        exercise_obj = current_exercise.exercise
        exercise_sets = current_exercise.sets
        exercise_reps = current_exercise.reps
        exercise_weight = current_exercise.weight
        exercise_rest_time = current_exercise.rest_time
    
    # Obtener historial de entrenamientos para este ejercicio
    exercise_history = Training.objects.filter(
        user=request.user,
        exercise=exercise_obj,
        completed=True
    ).order_by('-date')[:5]
    
    # Obtener las series del historial
    history_sets = {}
    for training in exercise_history:
        history_sets[training.id] = Set.objects.filter(
            training=training
        ).order_by('set_number')
    
    # Procesar el peso del ejercicio actual
    if exercise_weight == '' or exercise_weight is None:
        exercise_weight = 0
    
    # Obtener o crear el entrenamiento actual
    training, created = Training.objects.get_or_create(
        user=request.user,
        exercise=exercise_obj,
        date=training_date,
        defaults={
            'day_of_week': training_date.strftime('%A'),
            'total_sets': exercise_sets,
            'reps': exercise_reps,
            'weight': exercise_weight,
            'rest_time': exercise_rest_time,
            'intensity': 'Moderado',
            'notes': f"Rutina: {routine.name} - Día: {routine_day.day_of_week} ({routine_day.focus if hasattr(routine_day, 'focus') else ''})",
            'completed': False
        }
    )

    # Si el entrenamiento estaba marcado como pendiente, quitarle esa marca
    if " - PENDIENTE" in training.notes:
        training.notes = training.notes.replace(" - PENDIENTE", "")
        training.save()

    # Obtener las series completadas
    completed_sets = Set.objects.filter(
        training=training,
        completed=True
    ).order_by('set_number')
    
    # Determinar la serie actual
    current_set = completed_sets.count() + 1
    if is_trainer_routine:
        if current_set > exercise_sets:
            current_set = exercise_sets
    else:
        if current_set > current_exercise.sets:
            current_set = current_exercise.sets

    # Obtener ejercicios pendientes para esta rutina
    pending_exercises = Training.objects.filter(
        user=request.user,
        date=training_date,
        notes__contains="PENDIENTE",
        completed=False
    ).select_related('exercise')
    
    # Mapear los ejercicios pendientes a sus índices en exercises
    pending_with_indices = []
    for pending in pending_exercises:
        # Buscar el índice del ejercicio en la lista de todos los ejercicios
        for i, ex in enumerate(exercises):
            if is_trainer_routine:
                ex_name = ex['exercise'].name
            else:
                ex_name = ex.exercise.name
                
            if ex_name == pending.exercise.name:
                pending.index_in_routine = i
                pending_with_indices.append(pending)
                break
    
    # Procesar el envío del formulario
    if request.method == 'POST':
        # Comprobar si se está solicitando saltar o terminar
        if 'skip_set' in request.POST:
            # Saltar a la siguiente serie sin completar la actual
            if current_set < exercise_sets:
                messages.warning(request, f"Serie {current_set} saltada.")
                # Crear una serie vacía marcada como no completada
                Set.objects.update_or_create(
                    training=training,
                    set_number=current_set,
                    defaults={
                        'user': request.user,
                        'exercise': exercise_obj,
                        'weight': 0,
                        'reps': 0,
                        'completed': False
                    }
                )
                return redirect(request.path + f"?step={current_exercise_index}")
            else:
                # Si era la última serie, ir al siguiente ejercicio
                if current_exercise_index + 1 < len(exercises):
                    messages.warning(request, f"Serie {current_set} saltada. Pasando al siguiente ejercicio.")
                    return redirect(f"{request.path}?step={current_exercise_index + 1}")
                else:
                    messages.success(request, "Entrenamiento completado con serie saltada.")
                    return redirect('trainings:training-list-create')
        else:
            # Guardar la serie normalmente
            set_number = int(request.POST.get('current_set', 1))
            weight = request.POST.get('weight')
            reps = int(request.POST.get('reps', exercise_reps))

            # Convertir peso a float si existe, o asignar 0 por defecto
            if weight:
                try:
                    weight = float(weight)
                except ValueError:
                    weight = 0
            else:
                weight = 0

            # Crear la serie
            Set.objects.update_or_create(
                training=training,
                set_number=set_number,
                defaults={
                    'user': request.user,
                    'exercise': exercise_obj,
                    'weight': weight,
                    'reps': reps,
                    'completed': True
                }
            )

            # Si completamos todas las series del ejercicio actual
            if is_trainer_routine:
                max_sets = exercise_sets
            else:
                max_sets = current_exercise.sets
                
            if set_number >= max_sets:
                # Marcar el entrenamiento como completado
                training.completed = True
                training.save()

                # Si hay siguiente ejercicio, ir a él
                if current_exercise_index + 1 < len(exercises):
                    if is_trainer_routine:
                        exercise_name = exercise_obj.name
                    else:
                        exercise_name = current_exercise.exercise.name
                        
                    messages.success(request, f"¡{exercise_name} completado! Siguiente ejercicio.")
                    return redirect(f"{request.path}?step={current_exercise_index + 1}")
                else:
                    # Si no hay más ejercicios, finalizar el entrenamiento
                    messages.success(request, "¡Entrenamiento completado!")
                    return redirect('trainings:training-list-create')
            else:
                # Continuar con la siguiente serie
                messages.success(request, f"Serie {set_number} completada. ¡{max_sets - set_number} series restantes!")
                return redirect(request.path + f"?step={current_exercise_index}")
    
    # Traducir el día de la semana
    days_translation = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    day_of_week = days_translation.get(training_date.strftime('%A'))
    
    # Calcular el progreso
    progress = {
        'current': current_exercise_index + 1,
        'total': len(exercises),
        'percentage': int(((current_exercise_index + 1) / len(exercises)) * 100)
    }
    
    context = {
        'routine': routine,
        'routine_day': routine_day,
        'exercise': current_exercise,
        'is_trainer_routine': is_trainer_routine,
        'training': training,
        'current_set': current_set,
        'completed_sets': completed_sets,
        'exercise_history': exercise_history,
        'history_sets': history_sets,
        'prev_exercise': prev_exercise,
        'next_exercise': next_exercise,
        'current_exercise_index': current_exercise_index,
        'total_exercises': len(exercises),
        'day_of_week': day_of_week,
        'training_date': training_date,
        'progress': progress,
        'all_exercises': exercises,
        'next_index': current_exercise_index + 1 if current_exercise_index + 1 < len(exercises) else None,
        'prev_index': current_exercise_index - 1 if current_exercise_index > 0 else None,
        'pending_exercises': pending_with_indices,  # Ahora incluye los índices
        'show_skip_button': True,  # Controla si se debe mostrar el botón de saltar
        'show_finish_button': True  # Controla si se debe mostrar el botón de terminar
    }
    
    return render(request, 'trainings/execute_training.html', context)

@login_required
def training_session_view(request, training_id):
    training = get_object_or_404(Training, id=training_id, user=request.user)
    
    # Buscar el siguiente ejercicio del mismo día
    next_training = None
    prev_training = None
    
    # Obtener entrenamientos del mismo día, ordenados por ID
    day_trainings = Training.objects.filter(
        user=request.user,
        date=training.date
    ).order_by('id')
    
    if day_trainings.count() > 1:
        # Buscar el índice del entrenamiento actual
        current_index = None
        for i, t in enumerate(day_trainings):
            if t.id == training.id:
                current_index = i
                break
        
        # Si encontramos el índice, podemos determinar el anterior y el siguiente
        if current_index is not None:
            if current_index > 0:
                prev_training = day_trainings[current_index - 1]
            
            if current_index < day_trainings.count() - 1:
                next_training = day_trainings[current_index + 1]
    
    # Identificar ejercicios pendientes
    pending_trainings = []
    for t in day_trainings:
        if t.id != training.id:  # No incluir el ejercicio actual
            # Contar las series completadas
            completed_sets = Set.objects.filter(training=t, completed=True).count()
            if completed_sets < t.total_sets:
                pending_trainings.append(t)
    
    context = {
        'exercise': training.exercise,
        'total_sets': training.total_sets or 4,
        'rest_time': training.rest_time or 90,
        'training': training,
        'initial_weight': training.weight,
        'initial_reps': training.reps,
        'next_training': next_training,
        'prev_training': prev_training,
        'is_last_exercise': next_training is None,
        'day_trainings_count': day_trainings.count(),
        'current_exercise_index': list(day_trainings).index(training) + 1 if day_trainings else 1,
        'pending_trainings': pending_trainings,  # Añadido para mostrar ejercicios pendientes
    }
    
    return render(request, 'trainings/training_session.html', context)

@login_required
@require_POST
def save_set(request, training_id=None):
    """
    Guarda una serie de entrenamiento.
    """
    try:
        # Debug: Imprimir información de la solicitud
        print("Content-Type:", request.content_type)
        print("Body:", request.body.decode('utf-8'))
        print("POST data:", request.POST)
        print("Headers:", dict(request.headers))
        print("Training ID desde URL:", training_id)
        
        # Verificar el tipo de contenido
        if not request.content_type or 'application/json' not in request.content_type.lower():
            print("Error: Tipo de contenido incorrecto")
            return JsonResponse({
                'status': 'error',
                'message': f'Se requiere Content-Type: application/json. Recibido: {request.content_type}'
            }, status=400)

        # Intentar parsear el JSON
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': f'JSON inválido: {str(e)}'
            }, status=400)

        # Si training_id se pasó en la URL, usarlo en lugar del que viene en el body
        if training_id is not None:
            data['training_id'] = training_id

        # Comprobar si tenemos exercise_id en lugar de training_id
        if 'exercise_id' in data and 'training_id' not in data:
            print("Recibido exercise_id en lugar de training_id")
            # Intentar obtener el training relacionado con este ejercicio
            try:
                exercise_id = int(data['exercise_id'])
                set_number = int(data['set_number'])
                trainings = Training.objects.filter(
                    user=request.user, 
                    exercise_id=exercise_id
                ).order_by('-date')
                
                if trainings.exists():
                    training = trainings.first()
                    data['training_id'] = training.id
                    print(f"Training inferido: {training.id} para exercise_id={exercise_id}")
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No se encontró un entrenamiento para el ejercicio {exercise_id}'
                    }, status=404)
            except (ValueError, TypeError) as e:
                print("Error al convertir exercise_id:", str(e))
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error al procesar exercise_id: {str(e)}'
                }, status=400)

        # Validar campos requeridos
        required_fields = ['training_id', 'set_number', 'reps']  # weight puede ser 0
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Campos faltantes:", missing_fields)
            return JsonResponse({
                'status': 'error',
                'message': f'Faltan campos requeridos: {", ".join(missing_fields)}'
            }, status=400)

        # Obtener y validar los datos
        try:
            training_id = int(data['training_id'])
            set_number = int(data['set_number'])
            weight = float(data['weight']) if data.get('weight', '') else 0
            reps = int(data['reps'])
            
            print(f"Datos validados: training_id={training_id}, set_number={set_number}, weight={weight}, reps={reps}")
            
        except (ValueError, TypeError) as e:
            print("Error en la conversión de datos:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': f'Error en el formato de los datos: {str(e)}'
            }, status=400)

        # Obtener el entrenamiento y verificar permisos
        try:
            training = Training.objects.get(id=training_id)
            print(f"Entrenamiento encontrado: {training.id}, Usuario: {training.user.id}, Solicitante: {request.user.id}")
            
            if training.user != request.user:
                print("Error de permisos: Usuario no autorizado")
                return JsonResponse({
                    'status': 'error',
                    'message': 'No tienes permiso para modificar este entrenamiento'
                }, status=403)
                
        except Training.DoesNotExist:
            print(f"Entrenamiento no encontrado: {training_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Entrenamiento no encontrado'
            }, status=404)

        # Crear o actualizar la serie
        set_obj, created = Set.objects.update_or_create(
            training=training,
            set_number=set_number,
            defaults={
                'user': request.user,
                'exercise': training.exercise,
                'weight': weight,
                'reps': reps,
                'completed': True
            }
        )
        
        print(f"Serie {'creada' if created else 'actualizada'}: {set_obj.id}")

        return JsonResponse({
            'status': 'success',
            'message': 'Serie guardada correctamente',
            'set': {
                'id': set_obj.id,
                'set_number': set_obj.set_number,
                'weight': set_obj.weight,
                'reps': set_obj.reps,
                'completed': set_obj.completed
            }
        })

    except Exception as e:
        import traceback
        print("Error inesperado:", str(e))
        print("Traceback:", traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': f'Error inesperado: {str(e)}'
        }, status=500)

@login_required
@require_POST
def save_set_simple(request):
    """
    Versión simplificada para guardar una serie.
    """
    try:
        print("Recibido en save_set_simple")
        print("POST:", request.POST)
        print("Cuerpo:", request.body.decode('utf-8'))
        
        if request.content_type and 'application/json' in request.content_type.lower():
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST.dict()
            
        # Intentar obtener datos de cualquier fuente posible
        training_id = data.get('training_id') or request.POST.get('training_id')
        set_number = data.get('set_number') or request.POST.get('set_number')
        weight = data.get('weight') or request.POST.get('weight', 0)
        reps = data.get('reps') or request.POST.get('reps', 0)
        
        if not training_id or not set_number:
            return JsonResponse({
                'status': 'error',
                'message': 'Faltan parámetros obligatorios'
            }, status=400)
            
        # Convertir a tipos adecuados
        try:
            training_id = int(training_id)
            set_number = int(set_number)
            weight = float(weight) if weight else 0
            reps = int(reps) if reps else 0
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'message': 'Valores inválidos'
            }, status=400)
            
        # Obtener entrenamiento
        try:
            training = Training.objects.get(id=training_id)
        except Training.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'No existe un entrenamiento con ID {training_id}'
            }, status=404)
            
        # Crear o actualizar serie
        set_obj, created = Set.objects.update_or_create(
            training=training,
            set_number=set_number,
            defaults={
                'user': request.user,
                'exercise': training.exercise,
                'weight': weight,
                'reps': reps,
                'completed': True
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Serie guardada correctamente',
            'set_id': set_obj.id
        })
        
    except Exception as e:
        print(f"Error en save_set_simple: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_completed_sets(request, training_id):
    """
    Devuelve las series completadas para un entrenamiento específico.
    """
    try:
        training = get_object_or_404(Training, id=training_id, user=request.user)
        completed_sets = Set.objects.filter(training=training, completed=True).order_by('set_number')
        
        sets_data = []
        for set_obj in completed_sets:
            sets_data.append({
                'id': set_obj.id,
                'set_number': set_obj.set_number,
                'weight': set_obj.weight,
                'reps': set_obj.reps,
                'completed': set_obj.completed
            })
        
        return JsonResponse({
            'status': 'success',
            'training_id': training_id,
            'completed_sets': sets_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def training_stats(request):
    """Vista para mostrar estadísticas de entrenamiento."""
    # Redirigir a la aplicación completa de estadísticas
    return redirect('stats:dashboard')

@login_required
def dashboard(request):
    # Obtener estadísticas generales
    total_exercises = Training.objects.filter(user=request.user).count()
    total_routines = Routine.objects.filter(user=request.user).count()
    
    # Obtener sesiones en vivo activas
    active_sessions = LiveTrainingSession.objects.filter(
        trainer_student__student=request.user,
        status='active',
        ended_at__isnull=True
    ).select_related('trainer_student__trainer', 'training')
    
    # Calcular progreso general
    completed_trainings = Training.objects.filter(
        user=request.user,
        completed=True
    ).count()
    
    total_trainings = Training.objects.filter(user=request.user).count()
    progress_percentage = (completed_trainings / total_trainings * 100) if total_trainings > 0 else 0
    
    context = {
        'total_exercises': total_exercises,
        'total_routines': total_routines,
        'active_sessions': active_sessions,
        'progress_percentage': round(progress_percentage, 1),
        'completed_trainings': completed_trainings,
        'total_trainings': total_trainings,
    }
    
    return render(request, 'trainings/dashboard.html', context)

@login_required
def profile_edit(request):
    """Vista para editar el perfil del usuario."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Actualizar información del perfil
        profile.phone = request.POST.get('phone', '')
        if request.POST.get('birth_date'):
            profile.birth_date = request.POST.get('birth_date')
        
        # Manejar la foto del perfil
        if request.FILES.get('photo'):
            try:
                photo_file = request.FILES['photo']
                
                # Validar tamaño máximo (5MB)
                if photo_file.size > 5 * 1024 * 1024:  # 5MB en bytes
                    raise ValidationError("La imagen es demasiado grande. El tamaño máximo es de 5MB.")
                
                # Validar que sea una imagen
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                file_ext = photo_file.name.split('.')[-1].lower()
                if file_ext not in valid_extensions:
                    raise ValidationError("Formato de archivo no soportado. Usa JPG, PNG o GIF.")
                
                # Redimensionar si es necesario
                from PIL import Image
                from io import BytesIO
                from django.core.files.base import ContentFile
                
                # Abrir la imagen
                img = Image.open(photo_file)
                
                # Convertir a RGB si es RGBA (para PNG con transparencia)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Redimensionar si la imagen es muy grande
                MAX_SIZE = (800, 800)
                if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                    img.thumbnail(MAX_SIZE, Image.LANCZOS)
                
                # Guardar la imagen redimensionada
                output = BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                # Reemplazar el archivo original con la versión redimensionada
                profile.photo.save(
                    f"{file_ext}_profile.jpg",
                    ContentFile(output.read()),
                    save=False
                )
                
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error al procesar la imagen: {str(e)}")
            else:
                messages.success(request, "Imagen de perfil actualizada correctamente.")
        
        profile.save()
        messages.success(request, '¡Perfil actualizado exitosamente!')
        return redirect('trainings:dashboard')
    
    return render(request, 'trainings/profile_edit.html', {
        'profile': profile
    })

@login_required
def exercise_list(request):
    """
    Redirecciona a la vista principal de ejercicios.
    """
    return redirect('/exercises/')

@login_required
def routine_list(request):
    """Vista para listar rutinas."""
    return render(request, 'trainings/routine_list.html')

@login_required
def training_list(request):
    """Vista para listar entrenamientos."""
    # Verificar si se está terminando un entrenamiento anticipadamente
    action = request.GET.get('action', '')
    if action == 'end_early':
        messages.warning(request, "Entrenamiento finalizado anticipadamente. Los ejercicios pendientes han sido guardados.")
    
    trainings = Training.objects.filter(user=request.user).order_by('-date')
    
    # Obtener todas las series para contar las series completadas
    completed_sets_count = {}
    extra_sets_count = {}
    for training in trainings:
        sets_count = Set.objects.filter(training=training, completed=True).count()
        completed_sets_count[training.id] = sets_count
        
        # Calcular series extras (si hay más de las planificadas)
        if sets_count > training.total_sets:
            extra_sets_count[training.id] = sets_count - training.total_sets
        else:
            extra_sets_count[training.id] = 0
    
    # Obtener las rutinas del usuario
    routines = Routine.objects.filter(user=request.user).order_by('-created_at')
    
    # Agrupar entrenamientos por semana, fecha y rutina
    from datetime import datetime, timedelta
    from django.utils.dateparse import parse_date
    
    # Diccionario para agrupar por semana
    weekly_trainings = {}
    
    # Agrupar entrenamientos por fecha y rutina
    grouped_trainings = {}
    for training in trainings:
        date_str = training.date.strftime('%Y-%m-%d')
        
        # Calcular el número de semana
        week_start = training.date - timedelta(days=training.date.weekday())
        week_end = week_start + timedelta(days=6)
        week_key = f"{week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
        
        # Inicializar la semana si es nueva
        if week_key not in weekly_trainings:
            weekly_trainings[week_key] = {
                'dates': {},
                'total_exercises': 0,
                'completed_exercises': 0,
                'week_start': week_start,
                'week_end': week_end
            }
        
        # Extraer el nombre de la rutina y el día de las notas
        routine_info = 'Ejercicios Individuales'
        if training.notes and 'Rutina:' in training.notes:
            try:
                routine_parts = training.notes.split(' - ')
                routine_name = routine_parts[0].replace('Rutina: ', '')
                day_info = routine_parts[1] if len(routine_parts) > 1 else ''
                routine_info = f"{routine_name} - {day_info}"
            except:
                pass
        
        # Inicializar la fecha en la semana si es nueva
        if date_str not in weekly_trainings[week_key]['dates']:
            weekly_trainings[week_key]['dates'][date_str] = {}
        
        # Inicializar la rutina para esta fecha si es nueva
        if routine_info not in weekly_trainings[week_key]['dates'][date_str]:
            weekly_trainings[week_key]['dates'][date_str][routine_info] = []
        
        # Asegurarse de que el entrenamiento tenga toda la información necesaria
        training.routine_name = routine_info
        # Añadir el conteo de series completadas al objeto de entrenamiento
        training.completed_sets_count = completed_sets_count.get(training.id, 0)
        # Añadir el conteo de series extras
        training.extra_sets_count = extra_sets_count.get(training.id, 0)
        
        # Añadir el entrenamiento al grupo
        weekly_trainings[week_key]['dates'][date_str][routine_info].append(training)
        
        # Incrementar el contador de ejercicios totales de la semana
        weekly_trainings[week_key]['total_exercises'] += 1
        
        # Incrementar el contador de ejercicios completados de la semana si aplica
        if training.completed_sets_count >= training.total_sets:
            weekly_trainings[week_key]['completed_exercises'] += 1

    # Procesar los entrenamientos por semanas, calculando progreso por fecha y rutina
    for week_key, week_data in weekly_trainings.items():
        # Calcular el progreso semanal
        total_exercises = week_data['total_exercises']
        completed_exercises = week_data['completed_exercises']
        week_percentage = int((completed_exercises / total_exercises * 100) if total_exercises > 0 else 0)
        weekly_trainings[week_key]['percentage'] = week_percentage
        
        # Procesar cada fecha dentro de la semana
        for date_str, date_routines in week_data['dates'].items():
            for routine_name, trainings_list in date_routines.items():
                # Ordenar los entrenamientos dentro de cada rutina
                trainings_list.sort(key=lambda x: x.id)
                
                # Calcular el progreso total y verificar si hay pendientes
                total_sets = sum(t.total_sets for t in trainings_list)
                completed_sets = sum(t.completed_sets_count for t in trainings_list if "PENDIENTE" not in t.notes)
                has_pending = any("PENDIENTE" in t.notes for t in trainings_list)
                
                # Verificar si todos los ejercicios tienen completadas todas sus series
                all_sets_completed = True
                # Solo consideramos como completado si se han hecho TODAS las series y hay al menos una serie por cada ejercicio
                for t in trainings_list:
                    if t.completed_sets_count < t.total_sets:
                        all_sets_completed = False
                        break
                
                # Si algún ejercicio tiene 0 series completadas, el porcentaje no puede ser 100%
                has_zero_progress = any(t.completed_sets_count == 0 for t in trainings_list)
                
                # Calcular porcentaje (mostrar 100% solo si todas las series están completadas y no hay ejercicios con 0 progreso)
                if all_sets_completed and not has_pending and not has_zero_progress:
                    percentage = 100
                else:
                    # Modificamos el cálculo para contar por ejercicios completos vs total de ejercicios
                    completed_exercises = sum(1 for t in trainings_list if t.completed_sets_count >= t.total_sets)
                    total_exercises = len(trainings_list)
                    percentage = int((completed_exercises / total_exercises * 100) if total_exercises > 0 else 0)
                
                # Añadir información de progreso para esta rutina
                weekly_trainings[week_key]['dates'][date_str][routine_name] = {
                    'trainings': trainings_list,
                    'progress': {
                        'total_sets': total_sets,
                        'completed_sets': completed_sets,
                        'percentage': percentage,
                        'has_pending': has_pending
                    }
                }
    
    # Ordenar las semanas por fecha de inicio (más reciente primero)
    sorted_weeks = sorted(weekly_trainings.items(), 
                          key=lambda x: x[1]['week_start'], 
                          reverse=True)
    
    return render(request, 'trainings/training_list.html', {
        'weekly_trainings': dict(sorted_weeks),
        'routines': routines,
        'today': timezone.now().date(),
        'completed_sets_count': completed_sets_count,
        'extra_sets_count': extra_sets_count
    })

@login_required
def create_training_session(request):
    """Crear una nueva sesión de entrenamiento."""
    if request.method == 'POST':
        routine_id = request.POST.get('routine_id')
        routine_day_id = request.POST.get('routine_day_id')
        training_date = request.POST.get('training_date')
        
        try:
            routine = get_object_or_404(Routine, id=routine_id, user=request.user)
            routine_day = get_object_or_404(RoutineDay, id=routine_day_id, routine=routine)
            
            # Crear entrenamientos para cada ejercicio del día
            trainings = []
            for routine_exercise in routine_day.exercises.all():
                training = Training.objects.create(
                    user=request.user,
                    exercise=routine_exercise.exercise,
                    date=training_date,
                    total_sets=routine_exercise.sets,
                    reps=routine_exercise.reps,
                    weight=routine_exercise.weight,
                    rest_time=routine_exercise.rest_time
                )
                trainings.append(training)
            
            if trainings:
                # Redirigir al primer ejercicio
                return redirect('trainings:session', training_id=trainings[0].id)
            
        except Exception as e:
            messages.error(request, f'Error al crear la sesión: {str(e)}')
            return redirect('workouts:workout-detail', pk=routine_id)
    
    return redirect('workouts:workout-list')

@login_required
def edit_user_training(request, pk):
    """
    Permite a un usuario editar su propio entrenamiento.
    """
    training = get_object_or_404(Training, pk=pk, user=request.user)
    
    # Cargar todas las series explícitamente - usar Set directamente en lugar de set_set
    training_sets = Set.objects.filter(training=training).order_by('set_number')
    
    # Calcular cuántas series completadas hay
    completed_sets_count = training_sets.count()
    
    # Calcular cuántas series extras hay (si hay más de las planificadas)
    extra_sets_count = 0
    if completed_sets_count > training.total_sets:
        extra_sets_count = completed_sets_count - training.total_sets
    
    # Añadir esta información al objeto training para uso en el template
    training.completed_sets_count = completed_sets_count
    training.extra_sets_count = extra_sets_count
    
    if request.method == 'POST':
        # Imprimir datos recibidos para depuración
        print("Datos recibidos para actualizar entrenamiento:", request.POST)
        
        # Actualizar datos del entrenamiento
        try:
            # Actualizar ejercicio si se proporcionó
            exercise_id = request.POST.get('exercise')
            if exercise_id:
                training.exercise_id = exercise_id
            
            # Actualizar fecha si se proporcionó
            date_str = request.POST.get('date')
            if date_str:
                training.date = date_str
            
            # Actualizar series totales
            sets_str = request.POST.get('sets')
            if sets_str and sets_str.strip():
                training.total_sets = int(sets_str)
            
            # Actualizar repeticiones
            reps_str = request.POST.get('reps')
            if reps_str and reps_str.strip():
                training.reps = int(reps_str)
            
            # Manejar el peso (puede ser vacío)
            weight = request.POST.get('weight')
            if weight and weight.strip():
                try:
                    training.weight = float(weight)
                except ValueError:
                    training.weight = 0
            else:
                training.weight = 0
            
            # Actualizar tiempo de descanso
            rest_time = request.POST.get('rest_time')
            if rest_time and rest_time.strip():
                training.rest_time = int(rest_time)
            
            # Actualizar intensidad
            intensity = request.POST.get('intensity')
            if intensity:
                training.intensity = intensity
            
            # Actualizar notas
            notes = request.POST.get('notes')
            if notes is not None:  # Permitir notas vacías
                training.notes = notes
            
            # Actualizar estado completado
            training.completed = 'completed' in request.POST
            
            # Guardar cambios
            training.save()
            
            # Informar éxito
            messages.success(request, 'Entrenamiento actualizado correctamente.')
            
            # Redirección después de guardar
            return redirect('trainings:training-list-create')
        except Exception as e:
            # Si hay algún error, mostrarlo al usuario
            print("Error al actualizar entrenamiento:", str(e))
            messages.error(request, f'Error al actualizar el entrenamiento: {str(e)}')
    
    # Preparar datos para la vista
    exercises = GymExercise.objects.all().order_by('name')
    
    return render(request, 'trainings/edit_training.html', {
        'training': training,
        'training_sets': training_sets,
        'exercises': exercises
    })

@login_required
@require_POST
def delete_set(request, set_id):
    """
    Elimina una serie específica de un entrenamiento.
    """
    try:
        # Obtener la serie
        set_obj = get_object_or_404(Set, id=set_id)
        
        # Verificar que el usuario sea el propietario
        if set_obj.user != request.user:
            messages.error(request, 'No tienes permiso para eliminar esta serie.')
            return redirect('trainings:training-list-create')
        
        # Guardar el ID del entrenamiento para redireccionar después
        training_id = set_obj.training.id
        
        # Eliminar la serie
        set_obj.delete()
        
        messages.success(request, 'Serie eliminada correctamente.')
        
        # Redireccionar a la edición del entrenamiento
        return redirect('trainings:edit-training', pk=training_id)
    
    except Exception as e:
        messages.error(request, f'Error al eliminar la serie: {str(e)}')
        return redirect('trainings:training-list-create')

@login_required
def edit_set(request, set_id):
    """
    Edita una serie existente.
    """
    # Obtener la serie
    set_obj = get_object_or_404(Set, id=set_id)
    
    # Verificar que el usuario es el propietario de la serie
    if set_obj.user != request.user:
        messages.error(request, "No tienes permiso para editar esta serie.")
        return redirect('trainings:training-list-create')
    
    # Obtener el entrenamiento asociado
    training = set_obj.training
    
    if request.method == 'POST':
        try:
            # Actualizar los valores de la serie
            weight_str = request.POST.get('weight', '')
            reps_str = request.POST.get('reps', '')
            
            # Validar datos
            if not reps_str:
                messages.error(request, "El campo de repeticiones es obligatorio.")
                return redirect('trainings:edit-training', pk=training.id)
            
            # Convertir a tipos adecuados
            reps = int(reps_str)
            weight = float(weight_str) if weight_str.strip() else 0
            
            # Actualizar la serie
            set_obj.weight = weight
            set_obj.reps = reps
            set_obj.save()
            
            messages.success(request, f"Serie {set_obj.set_number} actualizada correctamente.")
            return redirect('trainings:edit-training', pk=training.id)
            
        except ValueError:
            messages.error(request, "Por favor ingresa valores numéricos válidos.")
            return redirect('trainings:edit-set', set_id=set_id)
        except Exception as e:
            messages.error(request, f"Error al actualizar la serie: {str(e)}")
            return redirect('trainings:edit-set', set_id=set_id)
    
    # Si es GET, mostrar el formulario
    return render(request, 'trainings/edit_set.html', {
        'set': set_obj,
        'training': training
    })