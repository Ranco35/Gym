from rest_framework import generics
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Exercise, ExerciseCategory, Equipment
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
from .forms import ExerciseForm, ExerciseCategoryForm

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
def exercise_list(request):
    """Vista para mostrar todos los ejercicios disponibles."""
    # Obtener todos los ejercicios ordenados por nombre
    exercises = Exercise.objects.all().select_related('category', 'creator', 'equipment').order_by('name')
    
    # Obtener categorías y equipamiento para el filtrado
    categories = ExerciseCategory.objects.all().order_by('name')
    equipment_list = Equipment.objects.all().order_by('name')
    
    context = {
        'exercises': exercises,
        'categories': categories,
        'equipment_list': equipment_list,
    }
    
    return render(request, 'exercises/exercise_list.html', context)

@login_required
def exercise_create(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.creator = request.user
            exercise.save()
            messages.success(request, 'Ejercicio creado exitosamente.')
            return redirect('exercises:exercise-list')
    else:
        form = ExerciseForm()
    
    return render(request, 'exercises/exercise_form.html', {
        'form': form,
        'title': 'Crear Ejercicio',
        'button_text': 'Crear'
    })

@login_required
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ejercicio actualizado exitosamente.')
            return redirect('exercises:exercise-list')
    else:
        form = ExerciseForm(instance=exercise)
    
    return render(request, 'exercises/exercise_form.html', {
        'form': form,
        'exercise': exercise,
        'title': 'Editar Ejercicio',
        'button_text': 'Actualizar'
    })

@login_required
@user_passes_test(is_admin_or_superuser)
def export_exercises(request):
    """
    Vista para exportar ejercicios en formato Excel.
    - Superusuarios y admins pueden exportar todos los ejercicios
    - Entrenadores pueden exportar sus ejercicios creados
    - Usuarios finales pueden exportar sus ejercicios creados
    """
    if is_admin_or_superuser(request.user):
        # Admins y superusuarios ven todos los ejercicios
        exercises = Exercise.objects.all()
    else:
        # Otros usuarios solo ven sus ejercicios creados
        exercises = Exercise.objects.filter(creator=request.user)
    
    # Definir las columnas a exportar
    columns = [
        'name', 'description', 'category', 'difficulty', 
        'primary_muscles', 'secondary_muscles', 'equipment', 
        'instructions', 'tips', 'youtube_link', 'image_url'
    ]
    
    # Crear una lista de diccionarios con los datos de los ejercicios
    data = []
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    for exercise in exercises:
        # Generar URL de la imagen si existe
        image_url = ''
        if exercise.image and hasattr(exercise.image, 'url'):
            image_url = base_url + exercise.image.url
        
        exercise_data = {
            'name': exercise.name,
            'description': exercise.description,
            'category': str(exercise.category),
            'difficulty': exercise.difficulty,
            'primary_muscles': exercise.primary_muscles,
            'secondary_muscles': exercise.secondary_muscles,
            'equipment': str(exercise.equipment),
            'instructions': exercise.instructions,
            'tips': exercise.tips,
            'youtube_link': exercise.youtube_link,
            'image_url': image_url
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
        'instructions', 'tips', 'youtube_link'
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
            'tips': 'Mantén los codos hacia abajo para proteger los hombros',
            'youtube_link': 'https://www.youtube.com/watch?v=ejemplo'
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
        
        # Añadir información sobre la imagen
        worksheet['K1'] = 'Nota: Las imágenes deben subirse manualmente desde la interfaz web'
        worksheet.column_dimensions['K'].width = 50
    
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
@user_passes_test(is_trainer_or_admin)
def import_exercises(request):
    """
    Vista para importar ejercicios desde un archivo Excel.
    Solo disponible para entrenadores y administradores.
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
            updated_count = 0
            duplicated_count = 0
            duplicated_names = []
            
            # Crear los ejercicios
            for data in exercise_data:
                # Obtener el nombre del ejercicio
                exercise_name = data.get('name')
                if not exercise_name:
                    continue
                
                # Si no es admin/superuser, solo puede actualizar sus propios ejercicios
                if not is_admin_or_superuser(request.user):
                    existing_exercise = Exercise.objects.filter(name__iexact=exercise_name).first()
                    if existing_exercise and existing_exercise.creator != request.user:
                        duplicated_count += 1
                        duplicated_names.append(exercise_name)
                        continue
                
                # Verificar o crear categoría
                category_name = data.get('category')
                if category_name:
                    category, _ = ExerciseCategory.objects.get_or_create(name=category_name)
                else:
                    category = None
                
                # Verificar o crear equipamiento
                equipment_name = data.get('equipment')
                if equipment_name:
                    equipment, _ = Equipment.objects.get_or_create(name=equipment_name)
                else:
                    equipment = None
                
                # Verificar si ya existe un ejercicio con el mismo nombre
                exercise = Exercise.objects.filter(name__iexact=exercise_name).first()
                if exercise:
                    # Si el ejercicio existe y el usuario puede editarlo
                    if exercise.creator == request.user or is_admin_or_superuser(request.user):
                        # Actualizar campos
                        if 'description' in data and data['description']:
                            exercise.description = data['description']
                        if category:
                            exercise.category = category
                        if 'difficulty' in data and data['difficulty']:
                            exercise.difficulty = data['difficulty']
                        if 'primary_muscles' in data and data['primary_muscles']:
                            exercise.primary_muscles = data['primary_muscles']
                        if 'secondary_muscles' in data and data['secondary_muscles']:
                            exercise.secondary_muscles = data['secondary_muscles']
                        if equipment:
                            exercise.equipment = equipment
                        if 'instructions' in data and data['instructions']:
                            exercise.instructions = data['instructions']
                        if 'tips' in data and data['tips']:
                            exercise.tips = data['tips']
                        if 'youtube_link' in data and data['youtube_link']:
                            exercise.youtube_link = data['youtube_link']
                        
                        exercise.save()
                        updated_count += 1
                    else:
                        duplicated_count += 1
                        duplicated_names.append(exercise_name)
                else:
                    # Crear nuevo ejercicio
                    new_exercise = Exercise(
                        name=exercise_name,
                        description=data.get('description', ''),
                        category=category,
                        difficulty=data.get('difficulty', 'Principiante'),
                        primary_muscles=data.get('primary_muscles', ''),
                        secondary_muscles=data.get('secondary_muscles', ''),
                        equipment=equipment,
                        instructions=data.get('instructions', ''),
                        tips=data.get('tips', ''),
                        youtube_link=data.get('youtube_link', ''),
                        creator=request.user
                    )
                    new_exercise.save()
                    created_count += 1
            
            # Mostrar mensajes apropiados
            if created_count > 0:
                messages.success(request, f'Se crearon {created_count} ejercicios correctamente.')
            
            if updated_count > 0:
                messages.success(request, f'Se actualizaron {updated_count} ejercicios existentes.')
            
            if duplicated_count > 0:
                duplicated_list = ", ".join(duplicated_names[:5])
                if duplicated_count > 5:
                    duplicated_list += f" y {duplicated_count - 5} más."
                messages.warning(
                    request, 
                    f'Se encontraron {duplicated_count} ejercicios que no puedes modificar. '
                    f'Ejemplos: {duplicated_list}'
                )
            
            return redirect('exercises:exercise-list')
            
        except Exception as e:
            messages.error(request, f'Error al importar ejercicios: {str(e)}')
    
    return render(request, 'exercises/import_exercises.html')

@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, 'Ejercicio eliminado correctamente.')
        return redirect('exercises:exercise-list')
    return render(request, 'exercises/exercise_confirm_delete.html', {
        'exercise': exercise
    })

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