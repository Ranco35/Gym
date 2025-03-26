from rest_framework import generics, permissions
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.contrib import messages

from .models import Training, Set
from .serializers import TrainingSerializer
from gym_tracker.exercises.models import Exercise as GymExercise
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
                
            exercises = GymExercise.objects.all()
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
                total_sets=sets,
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
        # Convertir peso vacío o None a None
        weight = routine_exercise.weight
        if weight == '' or weight is None:
            weight = None
            
        Training.objects.create(
            user=request.user,
            exercise=routine_exercise.exercise,
            date=training_date,
            day_of_week=real_day_of_week,
            total_sets=routine_exercise.sets,
            reps=routine_exercise.reps,
            weight=weight,  # Ahora weight será None si está vacío
            rest_time=routine_exercise.rest_time,
            intensity='Moderado',  # Valor predeterminado
            notes=f"Rutina: {routine.name} - Día: {routine_day.day_of_week} ({routine_day.focus})",
            completed=False
        )
        created_count += 1
    
    messages.success(request, f'Se han creado {created_count} entrenamientos correctamente.')
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
        sets = request.POST.get('sets', current_exercise.total_sets)
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
            total_sets=sets,
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
            weight = float(data['weight']) if data['weight'] else None
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