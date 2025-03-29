from rest_framework import generics
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Exercise, ExerciseCategory
from .serializers import ExerciseSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
import pandas as pd
import io
from datetime import datetime
from gym_tracker.users.permissions import is_admin_or_superuser, is_trainer_or_admin, can_edit_exercise
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import ExerciseCategoryForm

class ExerciseListView(generics.ListAPIView):
    """
    Vista para listar todos los ejercicios.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get(self, request, *args, **kwargs):
        if request.path.startswith('/api/'):
            return super().get(request, *args, **kwargs)
        
        # Obtener todos los ejercicios
        exercises = self.get_queryset()
        
        # Para cada ejercicio, determinar si el usuario actual puede editarlo
        exercises_with_permissions = []
        for exercise in exercises:
            exercises_with_permissions.append({
                'exercise': exercise,
                'can_edit': can_edit_exercise(request.user, exercise)
            })
        
        return render(request, 'exercises/exercise_list.html', {
            'exercises_with_permissions': exercises_with_permissions
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
        can_edit = can_edit_exercise(request.user, exercise)
        return render(request, 'exercises/exercise_detail.html', {
            'exercise': exercise,
            'can_edit': can_edit
        })

@login_required
@user_passes_test(is_trainer_or_admin)
def exercise_create(request):
    """Vista para crear un nuevo ejercicio."""
    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            name = request.POST.get('name')
            description = request.POST.get('description')
            
            # Obtener la categoría como objeto ExerciseCategory
            category_id = request.POST.get('category')
            try:
                category = ExerciseCategory.objects.get(id=category_id)
            except ExerciseCategory.DoesNotExist:
                messages.error(request, f'La categoría seleccionada no existe.')
                return render(request, 'exercises/exercise_form.html', {
                    'editing': False,
                    'categories': ExerciseCategory.objects.all().order_by('name')
                })
                
            difficulty = request.POST.get('difficulty')
            
            # Crear el ejercicio con los campos obligatorios
            exercise = Exercise(
                name=name,
                description=description,
                category=category,
                difficulty=difficulty,
                creator=request.user
            )
            
            # Agregar campos opcionales si están presentes
            optional_fields = [
                'primary_muscles', 
                'secondary_muscles', 
                'equipment', 
                'instructions', 
                'tips'
            ]
            
            for field in optional_fields:
                if request.POST.get(field):
                    setattr(exercise, field, request.POST.get(field))
            
            # Guardar el ejercicio
            exercise.save()
            
            messages.success(request, 'Ejercicio creado exitosamente.')
            return redirect('exercises:exercise-detail', pk=exercise.pk)
        except Exception as e:
            messages.error(request, f'Error al crear el ejercicio: {str(e)}')
    
    # Renderizar el formulario vacío
    return render(request, 'exercises/exercise_form.html', {
        'editing': False,
        'categories': ExerciseCategory.objects.all().order_by('name')
    })

@login_required
@user_passes_test(is_trainer_or_admin)
def exercise_edit(request, pk):
    """
    Vista para editar un ejercicio existente.
    Solo los administradores pueden editar cualquier ejercicio.
    Los entrenadores solo pueden editar los ejercicios que ellos crearon.
    """
    exercise = get_object_or_404(Exercise, pk=pk)
    
    # Verificar si el usuario tiene permiso para editar
    if not can_edit_exercise(request.user, exercise):
        messages.error(request, 'No tienes permiso para editar este ejercicio.')
        return redirect('exercises:exercise-detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del ejercicio
            exercise.name = request.POST.get('name')
            exercise.description = request.POST.get('description')
            
            # Obtener la categoría como objeto ExerciseCategory
            category_id = request.POST.get('category')
            if category_id:
                try:
                    category = ExerciseCategory.objects.get(id=category_id)
                    exercise.category = category
                except ExerciseCategory.DoesNotExist:
                    messages.error(request, f'La categoría seleccionada no existe.')
                    return render(request, 'exercises/exercise_form.html', {
                        'exercise': exercise,
                        'editing': True,
                        'categories': ExerciseCategory.objects.all().order_by('name')
                    })
            
            exercise.difficulty = request.POST.get('difficulty')
            
            # Actualizar campos opcionales
            optional_fields = [
                'primary_muscles', 
                'secondary_muscles', 
                'equipment', 
                'instructions', 
                'tips'
            ]
            
            for field in optional_fields:
                if hasattr(Exercise, field) and request.POST.get(field) is not None:
                    setattr(exercise, field, request.POST.get(field))
            
            exercise.save()
            messages.success(request, 'Ejercicio actualizado exitosamente.')
            return redirect('exercises:exercise-detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar el ejercicio: {str(e)}')
    
    return render(request, 'exercises/exercise_form.html', {
        'exercise': exercise,
        'editing': True,
        'categories': ExerciseCategory.objects.all().order_by('name')
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def export_exercises_template(request):
    """
    Vista para exportar una plantilla Excel para los ejercicios.
    """
    # Crear un DataFrame vacío con las columnas necesarias
    columns = [
        'name', 'description', 'category', 'difficulty', 
        'primary_muscles', 'secondary_muscles', 'equipment', 
        'instructions', 'tips'
    ]
    
    # Opcionalmente, añadir algunas filas de ejemplo
    sample_data = [
        {
            'name': 'Press de Banca',
            'description': 'Ejercicio compuesto para el desarrollo del pecho',
            'category': 'Pecho',
            'difficulty': 'Intermedio',
            'primary_muscles': 'Pectorales',
            'secondary_muscles': 'Tríceps, Deltoides',
            'equipment': 'Banca, Barra',
            'instructions': 'Acuéstate en el banco, agarra la barra, baja hasta el pecho y empuja hacia arriba.',
            'tips': 'Mantén los codos hacia abajo para proteger los hombros'
        }
    ]
    
    df = pd.DataFrame(sample_data, columns=columns)
    
    # Crear el archivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ejercicios')
        
        # Ajustar el ancho de las columnas
        worksheet = writer.sheets['Ejercicios']
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    # Preparar la respuesta
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=plantilla_ejercicios_{timestamp}.xlsx'
    
    return response

@login_required
@user_passes_test(is_admin_or_superuser)
def import_exercises(request):
    """
    Vista para importar ejercicios desde un archivo Excel.
    Verifica si ya existen ejercicios con el mismo nombre para evitar duplicados.
    """
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']
            
            # Leer el archivo Excel
            df = pd.read_excel(excel_file)
            
            # Validar que el archivo tenga las columnas requeridas
            required_columns = ['name', 'description', 'category', 'difficulty']
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f'El archivo no contiene la columna requerida: {col}')
                    return redirect('exercises:import-exercises')
            
            # Convertir DataFrame a lista de diccionarios
            exercise_data = df.replace({pd.NA: None}).to_dict('records')
            
            # Contar ejercicios creados y duplicados
            created_count = 0
            duplicated_count = 0
            duplicated_names = []
            
            # Crear los ejercicios
            for data in exercise_data:
                # Obtener el nombre del ejercicio
                exercise_name = data.get('name')
                if not exercise_name:
                    continue
                
                # Verificar si ya existe un ejercicio con el mismo nombre
                if Exercise.objects.filter(name__iexact=exercise_name).exists():
                    duplicated_count += 1
                    duplicated_names.append(exercise_name)
                    continue
                
                # Filtrar solo los campos que existen en el modelo
                valid_data = {k: v for k, v in data.items() if v is not None and hasattr(Exercise, k)}
                
                # Asignar el creador como el usuario actual
                valid_data['creator'] = request.user
                
                # Crear el ejercicio
                exercise = Exercise.objects.create(**valid_data)
                
                # Verificar que el creador se guardó correctamente
                if not exercise.creator and hasattr(exercise, 'creator'):
                    exercise.creator = request.user
                    exercise.save()
                
                created_count += 1
            
            # Mostrar mensaje de éxito con detalles
            if created_count > 0:
                messages.success(request, f'Se importaron {created_count} ejercicios correctamente.')
            
            # Mostrar mensaje de advertencia con detalles de duplicados
            if duplicated_count > 0:
                duplicated_list = ", ".join(duplicated_names[:5])
                if duplicated_count > 5:
                    duplicated_list += f" y {duplicated_count - 5} más."
                messages.warning(
                    request, 
                    f'Se encontraron {duplicated_count} ejercicios duplicados (ya existentes) y se omitieron. '
                    f'Ejemplos: {duplicated_list}'
                )
            
            # Si no se creó ningún ejercicio pero había datos, todos estaban duplicados
            if created_count == 0 and exercise_data:
                messages.warning(request, 'No se importó ningún ejercicio. Todos los ejercicios ya existían en el sistema.')
            
            return redirect('exercises:exercise-list')
        except Exception as e:
            messages.error(request, f'Error al importar ejercicios: {str(e)}')
    
    return render(request, 'exercises/import_exercises.html')

@login_required
@user_passes_test(is_admin_or_superuser)
def export_exercises(request):
    """
    Vista para exportar todos los ejercicios existentes en formato Excel.
    Solo accesible para administradores.
    """
    # Obtener todos los ejercicios de la base de datos
    exercises = Exercise.objects.all()
    
    # Definir las columnas a exportar
    columns = [
        'name', 'description', 'category', 'difficulty', 
        'primary_muscles', 'secondary_muscles', 'equipment', 
        'instructions', 'tips'
    ]
    
    # Crear una lista de diccionarios con los datos de los ejercicios
    data = []
    for exercise in exercises:
        exercise_data = {
            'name': exercise.name,
            'description': exercise.description,
            'category': exercise.category,
            'difficulty': exercise.difficulty,
            'primary_muscles': exercise.primary_muscles,
            'secondary_muscles': exercise.secondary_muscles,
            'equipment': exercise.equipment,
            'instructions': exercise.instructions,
            'tips': exercise.tips
        }
        data.append(exercise_data)
    
    # Crear un DataFrame con los datos
    df = pd.DataFrame(data, columns=columns)
    
    # Crear el archivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ejercicios')
        
        # Ajustar el ancho de las columnas
        worksheet = writer.sheets['Ejercicios']
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    # Preparar la respuesta
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=ejercicios_exportados_{timestamp}.xlsx'
    
    return response

def exercise_list(request):
    """Vista para mostrar todos los ejercicios disponibles."""
    # Obtener todos los ejercicios ordenados por nombre
    exercises = Exercise.objects.all().select_related('category').order_by('name')
    
    # Lista para almacenar ejercicios con permisos
    exercises_with_permissions = []
    
    # Obtener categorías únicas para las pestañas
    categories = ExerciseCategory.objects.all().order_by('name')
    
    # Contadores para cada nivel de dificultad
    beginner_count = 0
    intermediate_count = 0
    advanced_count = 0
    
    # Verificar permisos para cada ejercicio
    for exercise in exercises:
        can_edit = False
        # Si el usuario es administrador o el creador del ejercicio, puede editarlo
        if request.user.is_superuser or request.user.role == 'ADMIN' or (
            exercise.creator and exercise.creator == request.user):
            can_edit = True
        
        exercises_with_permissions.append({
            'exercise': exercise,
            'can_edit': can_edit
        })
        
        # Contar ejercicios por dificultad
        if exercise.difficulty == 'Principiante':
            beginner_count += 1
        elif exercise.difficulty == 'Intermedio':
            intermediate_count += 1
        elif exercise.difficulty == 'Avanzado':
            advanced_count += 1
    
    # Agregar información de depuración si en modo DEBUG
    debug_info = {}
    if settings.DEBUG:
        debug_info = {
            'user_id': request.user.id,
            'username': request.user.username,
            'role': request.user.role,
            'is_superuser': request.user.is_superuser,
            'beginner_count': beginner_count,
            'intermediate_count': intermediate_count,
            'advanced_count': advanced_count,
            'total_count': len(exercises_with_permissions)
        }
    
    context = {
        'exercises_with_permissions': exercises_with_permissions,
        'debug_info': debug_info,
        'categories': categories,
        'beginner_count': beginner_count,
        'intermediate_count': intermediate_count,
        'advanced_count': advanced_count,
        'total_count': len(exercises_with_permissions)
    }
    
    return render(request, 'exercises/exercise_list.html', context)

# Verificación de permisos
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'ADMIN')

# Vistas de CRUD para categorías
class CategoryListView(UserPassesTestMixin, ListView):
    model = ExerciseCategory
    template_name = 'exercises/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir contador de ejercicios por categoría
        categories = context['categories']
        for category in categories:
            category.exercise_count = Exercise.objects.filter(category=category).count()
        return context

class CategoryCreateView(UserPassesTestMixin, CreateView):
    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    template_name = 'exercises/category_form.html'
    success_url = reverse_lazy('exercises:category-list')
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.name}" creada correctamente.')
        return super().form_valid(form)

class CategoryUpdateView(UserPassesTestMixin, UpdateView):
    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    template_name = 'exercises/category_form.html'
    success_url = reverse_lazy('exercises:category-list')
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.name}" actualizada correctamente.')
        return super().form_valid(form)

class CategoryDeleteView(UserPassesTestMixin, DeleteView):
    model = ExerciseCategory
    template_name = 'exercises/category_confirm_delete.html'
    success_url = reverse_lazy('exercises:category-list')
    context_object_name = 'category'
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, f'Categoría "{category.name}" eliminada correctamente.')
            return result
        except Exception as e:
            messages.error(request, f'No se pudo eliminar la categoría. Error: {str(e)}')
            return redirect('exercises:category-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir contador de ejercicios que usan esta categoría
        category = context['category']
        context['exercise_count'] = category.exercises.count()
        return context