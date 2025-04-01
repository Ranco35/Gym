from rest_framework import generics, status
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import Exercise, ExerciseCategory, Equipment
from .serializers import ExerciseSerializer, ExerciseExportSerializer, ExerciseImportSerializer
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
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
import tempfile
import os

class ExerciseListView(generics.ListCreateAPIView):
    """
    Vista API para listar y crear ejercicios.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista API para recuperar, actualizar y eliminar un ejercicio.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    lookup_field = 'slug'  # Usar slug en vez de pk

    def get_object(self):
        """
        Recupera el objeto basado en el slug o pk
        """
        lookup_value = self.kwargs.get(self.lookup_field, None)
        if lookup_value and lookup_value.isdigit():
            # Si es un número, buscar por pk
            self.lookup_field = 'pk'
        return super().get_object()

@login_required
def exercise_list(request):
    """
    Vista para listar todos los ejercicios.
    """
    # Obtener todos los ejercicios
    exercises = Exercise.objects.all().order_by('name')
    categories = ExerciseCategory.objects.all()
    equipment = Equipment.objects.all()
    
    # Para cada ejercicio, determinar si el usuario actual puede editarlo
    exercises_with_permissions = []
    for exercise in exercises:
        exercises_with_permissions.append({
            'exercise': exercise,
            'can_edit': can_edit_exercise(request.user, exercise)
        })
    
    return render(request, 'exercises/exercise_list.html', {
        'exercises_with_permissions': exercises_with_permissions,
        'exercises': exercises,  # Mantener compatibilidad
        'categories': categories,
        'equipment': equipment
    })

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
def exercise_edit(request, pk=None, slug=None):
    """
    Vista para editar un ejercicio existente.
    """
    # Buscar el ejercicio por pk o slug
    if slug:
        exercise = get_object_or_404(Exercise, slug=slug)
    else:
        exercise = get_object_or_404(Exercise, pk=pk)
    
    # Verificar permisos
    if not can_edit_exercise(request.user, exercise):
        messages.error(request, 'No tienes permiso para editar este ejercicio.')
        return redirect('exercises:exercise-list')
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ejercicio actualizado correctamente.')
            if slug:
                return redirect('exercises:exercise-detail-slug', slug=exercise.slug)
            else:
                return redirect('exercises:exercise-detail', pk=exercise.pk)
    else:
        form = ExerciseForm(instance=exercise)
    
    return render(request, 'exercises/exercise_form.html', {
        'form': form,
        'exercise': exercise,
        'is_edit': True
    })

@login_required
def export_exercises(request):
    """
    Vista para exportar ejercicios en formato JSON o Excel.
    """
    # Registrar información de la solicitud para depuración
    print(f"\n-------- INICIO EXPORTACIÓN --------")
    print(f"Método: {request.method}")
    print(f"Ruta: {request.path}")
    print(f"Query params: {request.GET}")
    print(f"Headers: {request.headers.get('User-Agent')}")
    
    # Determinar si se solicita JSON o Excel basado en la URL
    # Si la URL contiene 'json', exportar como JSON
    is_json_export = 'json' in request.path
    print(f"Formato solicitado: {'JSON' if is_json_export else 'Excel'}")
    
    if is_json_export:
        try:
            # Obtener IDs de ejercicios a exportar
            exercise_ids = request.GET.getlist('ids', [])
            print(f"IDs solicitados: {exercise_ids}")
            
            # Filtrar ejercicios según los IDs proporcionados o permisos
            if is_admin_or_superuser(request.user):
                if exercise_ids:
                    queryset = Exercise.objects.filter(id__in=exercise_ids)
                else:
                    queryset = Exercise.objects.all()
            else:
                # Usuarios normales solo ven sus ejercicios
                if exercise_ids:
                    queryset = Exercise.objects.filter(id__in=exercise_ids, created_by=request.user)
                else:
                    queryset = Exercise.objects.filter(created_by=request.user)
            
            print(f"Ejercicios encontrados: {len(queryset)}")
            
            # Serializar los datos
            serializer = ExerciseExportSerializer(queryset, many=True)
            json_data = json.dumps(serializer.data, indent=4)
            
            # Crear archivo para descargar directamente sin usar archivo temporal
            response = HttpResponse(
                json_data,
                content_type='application/json'
            )
            
            # Configurar encabezados para descarga
            filename = "exercises_export.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Añadir encabezados adicionales para CORS y caché
            response['Content-Length'] = len(json_data)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With, X-CSRFToken'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Debug: registrar información sobre la respuesta
            print(f"Exportación JSON completada: {len(queryset)} ejercicios")
            print(f"Tamaño de datos: {len(json_data)} bytes")
            print(f"Encabezados response: {dict(response.headers)}")
            print(f"-------- FIN EXPORTACIÓN --------\n")
            
            return response
        except Exception as e:
            # Capturar cualquier excepción para mostrar un error más descriptivo
            import traceback
            print(f"Error en export_exercises (JSON): {str(e)}")
            print(traceback.format_exc())
            print(f"-------- ERROR EXPORTACIÓN --------\n")
            
            # Devolver una respuesta de error en formato JSON
            error_response = JsonResponse({
                'error': str(e),
                'detail': 'Ha ocurrido un error durante la exportación de ejercicios.'
            }, status=500)
            
            # Añadir encabezados CORS
            error_response['Access-Control-Allow-Origin'] = '*'
            error_response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            error_response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
            
            return error_response
    else:
        try:
            # Exportación en formato Excel
            if is_admin_or_superuser(request.user):
                # Admins y superusuarios ven todos los ejercicios
                exercises = Exercise.objects.all()
            else:
                # Otros usuarios solo ven sus ejercicios creados
                exercises = Exercise.objects.filter(created_by=request.user)
            
            # Definir las columnas a exportar
            columns = [
                'id', 'name', 'slug', 'description', 'muscle_group', 'difficulty', 
                'primary_muscles', 'secondary_muscles', 'equipment', 
                'tips', 'video_url', 'image_url'
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
                    'id': exercise.id,
                    'name': exercise.name,
                    'slug': exercise.slug,
                    'description': exercise.description,
                    'muscle_group': exercise.muscle_group,
                    'difficulty': exercise.difficulty,
                    'primary_muscles': exercise.primary_muscles,
                    'secondary_muscles': exercise.secondary_muscles,
                    'equipment': exercise.equipment,
                    'tips': exercise.tips,
                    'video_url': exercise.video_url,
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
        except Exception as e:
            # Capturar cualquier excepción para mostrar un error más descriptivo
            import traceback
            print(f"Error en export_exercises (Excel): {str(e)}")
            print(traceback.format_exc())
            
            # Devolver una respuesta de error en formato JSON
            return JsonResponse({
                'error': str(e),
                'detail': 'Ha ocurrido un error durante la exportación de ejercicios a Excel.'
            }, status=500)

@api_view(['GET'])
def export_exercises_template(request):
    """
    Vista para exportar una plantilla JSON o Excel de ejercicios.
    """
    # Detectar si se solicita formato JSON
    is_json_format = request.GET.get('format') == 'json'
    
    if is_json_format:
        try:
            template = {
                "id": 0,  # Será ignorado en la importación
                "name": "Nombre del ejercicio",
                "slug": "nombre-del-ejercicio",
                "description": "Descripción detallada del ejercicio",
                "muscle_group": "chest",  # Opciones: chest, back, shoulders, arms, legs, core, full_body, cardio
                "primary_muscles": "Pectorales, tríceps",
                "secondary_muscles": "Hombros",
                "difficulty": "intermediate",  # Opciones: beginner, intermediate, advanced
                "equipment": "Barra, mancuernas",
                "tips": "Consejos para realizar correctamente el ejercicio",
                "video_url": "https://www.youtube.com/watch?v=ejemplo",
                "image": None,  # La imagen se debe cargar desde la interfaz
                "images": []  # Las imágenes adicionales se deben cargar desde la interfaz
            }
            
            # Convertir a JSON
            json_data = json.dumps(template, indent=4)
            
            # Crear respuesta directamente sin usar archivos temporales
            response = HttpResponse(
                json_data,
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="exercise_template.json"'
            
            # Añadir encabezados adicionales
            response['Content-Length'] = len(json_data)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Debug: registrar información
            print("Plantilla JSON de ejercicio exportada correctamente")
            print(f"Tamaño de datos: {len(json_data)} bytes")
            
            return response
        except Exception as e:
            # Capturar cualquier excepción para mostrar un error más descriptivo
            import traceback
            print(f"Error en export_exercises_template (JSON): {str(e)}")
            print(traceback.format_exc())
            
            # Devolver una respuesta de error en formato JSON
            return JsonResponse({
                'error': str(e),
                'detail': 'Ha ocurrido un error durante la exportación de la plantilla.'
            }, status=500)
    else:
        # Exportar en formato Excel (original)
        try:
            # Crear un DataFrame vacío con las columnas necesarias
            columns = [
                'id', 'name', 'slug', 'description', 'muscle_group', 'difficulty', 
                'primary_muscles', 'secondary_muscles', 'equipment', 
                'tips', 'video_url'
            ]
            
            # Opcionalmente, añadir algunas filas de ejemplo
            sample_data = [
                {
                    'id': 0,  # Será ignorado en la importación
                    'name': 'Press de Banca',
                    'slug': 'press-de-banca',
                    'description': 'Ejercicio compuesto para el desarrollo del pecho',
                    'muscle_group': 'chest',
                    'difficulty': 'intermediate',
                    'primary_muscles': 'Pectorales',
                    'secondary_muscles': 'Tríceps, Deltoides',
                    'equipment': 'Banca, Barra',
                    'tips': 'Mantén los codos hacia abajo para proteger los hombros',
                    'video_url': 'https://www.youtube.com/watch?v=ejemplo'
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
                worksheet['L1'] = 'Nota: Las imágenes deben subirse manualmente desde la interfaz web'
                worksheet.column_dimensions['L'].width = 50
                
                # Añadir información sobre el slug
                worksheet['M1'] = 'IMPORTANTE: El slug es el identificador único para actualizar ejercicios'
                worksheet.column_dimensions['M'].width = 60
            
            # Preparar la respuesta
            output.seek(0)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename=plantilla_ejercicios_{timestamp}.xlsx'
            
            return response
        except Exception as e:
            # Capturar cualquier excepción para mostrar un error más descriptivo
            import traceback
            print(f"Error en export_exercises_template (Excel): {str(e)}")
            print(traceback.format_exc())
            
            # Devolver una respuesta de error en formato JSON
            return JsonResponse({
                'error': str(e),
                'detail': 'Ha ocurrido un error durante la exportación de la plantilla Excel.'
            }, status=500)

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
            required_columns = ['name', 'description', 'muscle_group', 'difficulty']
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f'El archivo no contiene la columna "{col}" que es requerida.')
                    return redirect('exercises:import-exercises')
            
            # Procesar los ejercicios
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    # Crear o actualizar el ejercicio
                    exercise_name = row['name']
                    
                    # Si ya existe un ejercicio con ese nombre, actualizarlo
                    exercise, created = Exercise.objects.get_or_create(
                        name=exercise_name,
                        defaults={
                            'created_by': request.user,
                        }
                    )
                    
                    # Actualizar campos obligatorios
                    exercise.description = row['description']
                    exercise.muscle_group = row['muscle_group']
                    exercise.difficulty = row['difficulty']
                    
                    # Actualizar campos opcionales si están presentes en el Excel
                    if 'primary_muscles' in df.columns and not pd.isna(row['primary_muscles']):
                        exercise.primary_muscles = row['primary_muscles']
                    
                    if 'secondary_muscles' in df.columns and not pd.isna(row['secondary_muscles']):
                        exercise.secondary_muscles = row['secondary_muscles']
                    
                    if 'equipment' in df.columns and not pd.isna(row['equipment']):
                        exercise.equipment = row['equipment']
                    
                    if 'tips' in df.columns and not pd.isna(row['tips']):
                        exercise.tips = row['tips']
                    
                    if 'video_url' in df.columns and not pd.isna(row['video_url']):
                        exercise.video_url = row['video_url']
                    
                    # Guardar los cambios
                    exercise.save()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error importando ejercicio {row.get('name', 'desconocido')}: {e}")
            
            # Mostrar mensaje de éxito
            if success_count > 0:
                messages.success(request, f'Se han importado {success_count} ejercicios correctamente.')
            
            # Mostrar mensaje de error si hubo problemas
            if error_count > 0:
                messages.warning(request, f'No se pudieron importar {error_count} ejercicios. Revise el archivo.')
                
            return redirect('exercises:exercise-list')
                
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
            return redirect('exercises:import-exercises')
    
    return render(request, 'exercises/import_exercises.html')

@login_required
def exercise_delete(request, pk=None, slug=None):
    """
    Vista para eliminar un ejercicio.
    """
    # Buscar el ejercicio por pk o slug
    if slug:
        exercise = get_object_or_404(Exercise, slug=slug)
    else:
        exercise = get_object_or_404(Exercise, pk=pk)
    
    # Verificar permisos
    if not can_edit_exercise(request.user, exercise):
        messages.error(request, 'No tienes permiso para eliminar este ejercicio.')
        return redirect('exercises:exercise-list')
    
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

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def import_exercises(request):
    """
    Vista para importar ejercicios desde un archivo JSON.
    """
    print(f"\n-------- SOLICITUD IMPORT EXERCISES --------")
    print(f"Método: {request.method}")
    print(f"Headers: {request.headers}")
    
    # Si es una solicitud GET, solo mostrar la página
    if request.method == 'GET':
        print("Retornando plantilla HTML para importar ejercicios")
        return render(request, 'exercises/import_exercises.html')
    
    # Procesar solicitud POST con datos JSON
    try:
        data = json.loads(request.body)
        
        if not isinstance(data, list):
            data = [data]
            
        imported_count = 0
        updated_count = 0
        errors = []
        
        for exercise_data in data:
            # Verificar si existe por slug
            slug = exercise_data.get('slug')
            existing = None
            
            if slug:
                try:
                    existing = Exercise.objects.get(slug=slug)
                except Exercise.DoesNotExist:
                    pass
                
            serializer = ExerciseImportSerializer(instance=existing, data=exercise_data)
            
            if serializer.is_valid():
                if existing:
                    updated_count += 1
                else:
                    imported_count += 1
                
                serializer.save(created_by=request.user)
            else:
                errors.append({
                    'data': exercise_data.get('name', 'Desconocido'),
                    'errors': serializer.errors
                })
        
        return Response({
            'imported': imported_count,
            'updated': updated_count,
            'errors': errors
        })
    except json.JSONDecodeError:
        return Response({
            'error': 'El cuerpo de la solicitud debe contener JSON válido'
        }, status=400)
    except Exception as e:
        print(f"Error en import_exercises: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return Response({
            'error': str(e)
        }, status=500)