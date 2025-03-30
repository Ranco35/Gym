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
                grouped_trainings[date_str][routine_info].append(training)
            
            # Ordenar los entrenamientos dentro de cada rutina por el orden original
            for date in grouped_trainings:
                for routine in grouped_trainings[date]:
                    grouped_trainings[date][routine].sort(key=lambda x: x.id)
            
            exercises = GymExercise.objects.all()
            # Obtener rutinas del usuario para el formulario de entrenamiento basado en rutina
            routines = Routine.objects.filter(user=request.user).order_by('-created_at')
            
            return render(request, 'trainings/training_list.html', {
                'grouped_trainings': grouped_trainings,
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
            try:
                # Intentar buscar el ejercicio existente por nombre
                exercise_obj = GymExercise.objects.get(name=trainer_set.exercise)
            except GymExercise.DoesNotExist:
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
    current_exercise_index = int(request.GET.get('step', 0))
    
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

    # Procesar el envío del formulario
    if request.method == 'POST':
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
        Set.objects.create(
            training=training,
            user=request.user,
            exercise=exercise_obj,
            set_number=set_number,
            weight=weight,
            reps=reps,
            completed=True
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
        'prev_index': current_exercise_index - 1 if current_exercise_index > 0 else None
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
    }
    
    return render(request, 'trainings/training_session.html', context)

@login_required
@require_POST
def save_set(request):
    """
    Guarda una serie de entrenamiento.
    """
    try:
        # Debug: Imprimir información de la solicitud
        print("Content-Type:", request.content_type)
        print("Body:", request.body.decode('utf-8'))
        print("POST data:", request.POST)
        print("Headers:", dict(request.headers))
        
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
        required_fields = ['training_id', 'set_number', 'weight', 'reps']
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
            weight = float(data['weight']) if data['weight'] else 0
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
    total_exercises = Exercise.objects.count()
    total_trainings = Training.objects.filter(user=request.user).count()
    completed_trainings = Training.objects.filter(user=request.user, completed=True).count()
    
    # Calcular porcentaje de progreso
    progress_percentage = (completed_trainings / total_trainings * 100) if total_trainings > 0 else 0
    
    # Obtener sesiones en vivo activas
    active_sessions = []
    
    # Si el usuario es entrenador, mostrar las sesiones con sus estudiantes
    if hasattr(request.user, 'trainerprofile'):
        active_sessions = LiveTrainingSession.objects.filter(
            trainer_student__trainer=request.user,
            status='active',
            ended_at__isnull=True
        ).select_related('trainer_student__student', 'training')
    else:
        # Si es estudiante, mostrar las sesiones con sus entrenadores
        active_sessions = LiveTrainingSession.objects.filter(
            trainer_student__student=request.user,
            status='active',
            ended_at__isnull=True
        ).select_related('trainer_student__trainer', 'training')
    
    context = {
        'total_exercises': total_exercises,
        'total_trainings': total_trainings,
        'completed_trainings': completed_trainings,
        'progress_percentage': round(progress_percentage, 1),
        'active_sessions': active_sessions
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
            profile.photo = request.FILES['photo']
        
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
    return redirect('exercises:exercise-list')

@login_required
def routine_list(request):
    """Vista para listar rutinas."""
    return render(request, 'trainings/routine_list.html')

@login_required
def training_list(request):
    """Vista para listar entrenamientos."""
    trainings = Training.objects.filter(user=request.user).order_by('-date')
    
    # Obtener las rutinas del usuario
    routines = Routine.objects.filter(user=request.user).order_by('-created_at')
    
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
        grouped_trainings[date_str][routine_info].append(training)

    # Ordenar los entrenamientos dentro de cada rutina por el orden original
    for date in grouped_trainings:
        for routine in grouped_trainings[date]:
            grouped_trainings[date][routine].sort(key=lambda x: x.id)
    
    return render(request, 'trainings/training_list.html', {
        'grouped_trainings': grouped_trainings,
        'routines': routines,
        'today': timezone.now().date()
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