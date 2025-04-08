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
from django.utils.text import slugify

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
    Vista para listar todos los ejercicios activos.
    """
    # Obtener todos los ejercicios activos
    exercises = Exercise.objects.filter(is_active=True).order_by('name')
    
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
        'exercise': Exercise,  # Para acceder a MUSCLE_GROUPS en el template
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
def exercise_delete(request, pk=None, slug=None):
    """
    Vista para eliminar un ejercicio existente.
    Implementa soft delete para mantener el historial de entrenamientos.
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
        # Verificar si el ejercicio está en uso
        from gym_tracker.trainings.models import Set
        from gym_tracker.trainers.models import TrainerSet
        
        is_in_use = Set.objects.filter(exercise=exercise).exists() or \
                   TrainerSet.objects.filter(exercise=exercise).exists()
        
        if is_in_use:
            # Si está en uso, implementar soft delete marcando como inactivo
            exercise.is_active = False
            exercise.save()
            messages.success(request, 'Ejercicio marcado como inactivo. Se mantendrá el historial de entrenamientos.')
        else:
            # Si no está en uso, eliminar completamente
            exercise.delete()
            messages.success(request, 'Ejercicio eliminado correctamente.')
        
        return redirect('exercises:exercise-list')
    
    return render(request, 'exercises/exercise_confirm_delete.html', {
        'exercise': exercise
    })

@login_required
def export_exercises(request):
    """
    Vista para exportar ejercicios en formato JSON o Excel.
    Los usuarios pueden exportar sus propios ejercicios o todos si son admin/superuser.
    """
    try:
        # Obtener ejercicios según permisos
        if is_admin_or_superuser(request.user):
            exercises = Exercise.objects.all()
        else:
            exercises = Exercise.objects.filter(created_by=request.user)
        
        if not exercises.exists():
            messages.error(request, 'No hay ejercicios para exportar.')
            return redirect('exercises:exercise-list')
        
        is_json_export = 'json' in request.path
        
        if is_json_export:
            serializer = ExerciseExportSerializer(exercises, many=True)
            json_data = json.dumps(serializer.data, indent=4, ensure_ascii=False)
            response = HttpResponse(json_data, content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="ejercicios_exportados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        # Exportar Excel
        data = []
        for exercise in exercises:
            exercise_data = {
                'ID': exercise.id,
                'Nombre': exercise.name,
                'Slug': exercise.slug,
                'Descripción': exercise.description,
                'Grupo Muscular': exercise.get_muscle_group_display(),
                'Dificultad': exercise.get_difficulty_display(),
                'Músculos Principales': exercise.primary_muscles or '',
                'Músculos Secundarios': exercise.secondary_muscles or '',
                'Equipamiento': exercise.equipment or '',
                'Consejos': exercise.tips or '',
                'URL del Video': exercise.video_url or '',
                'Imagen Principal': exercise.image.url if exercise.image else '',
                'Fecha de Creación': exercise.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Última Actualización': exercise.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(exercise_data)
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ejercicios')
            worksheet = writer.sheets['Ejercicios']
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + i)].width = column_width
        
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=ejercicios_exportados_{timestamp}.xlsx'
        return response
        
    except Exception as e:
        print(f"Error en export_exercises: {str(e)}")
        messages.error(request, f'Error al exportar ejercicios: {str(e)}')
        return redirect('exercises:exercise-list')

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
def import_exercises(request):
    """
    Vista para importar ejercicios desde un archivo JSON o Excel.
    """
    if request.method == 'GET':
        return render(request, 'exercises/import_exercises.html')
    
    if request.method == 'POST':
        try:
            file = request.FILES.get('file')
            if not file:
                messages.error(request, 'No se ha seleccionado ningún archivo.')
                return redirect('exercises:import-exercises')
            
            # Determinar el tipo de archivo
            file_extension = file.name.split('.')[-1].lower()
            
            if file_extension == 'json':
                # Procesar archivo JSON
                data = json.loads(file.read().decode('utf-8'))
                serializer = ExerciseImportSerializer(data=data, many=True)
                
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, f'Se importaron {len(data)} ejercicios correctamente.')
                else:
                    messages.error(request, f'Error al importar ejercicios: {serializer.errors}')
            elif file_extension in ['xlsx', 'xls']:
                # Procesar archivo Excel
                df = pd.read_excel(file)
                success_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    try:
                        # Convertir la fila a diccionario
                        exercise_data = row.to_dict()
                        
                        # Crear o actualizar el ejercicio
                        exercise, created = Exercise.objects.update_or_create(
                            slug=exercise_data['slug'],
                            defaults={
                                'name': exercise_data['name'],
                                'description': exercise_data['description'],
                                'muscle_group': exercise_data['muscle_group'],
                                'difficulty': exercise_data['difficulty'],
                                'primary_muscles': exercise_data['primary_muscles'],
                                'secondary_muscles': exercise_data['secondary_muscles'],
                                'equipment': exercise_data['equipment'],
                                'tips': exercise_data['tips'],
                                'video_url': exercise_data['video_url']
                            }
                        )
                        
                        if created:
                            exercise.created_by = request.user
                            exercise.save()
                        
                        success_count += 1
                    except Exception as e:
                        print(f"Error al importar ejercicio: {str(e)}")
                        error_count += 1
                
                if success_count > 0:
                    messages.success(request, f'Se importaron {success_count} ejercicios correctamente.')
                if error_count > 0:
                    messages.warning(request, f'No se pudieron importar {error_count} ejercicios.')
            else:
                messages.error(request, 'Formato de archivo no soportado. Use JSON o Excel.')
            
            return redirect('exercises:exercise-list')
            
        except Exception as e:
            print(f"Error en import_exercises: {str(e)}")
            messages.error(request, f'Error al importar ejercicios: {str(e)}')
            return redirect('exercises:import-exercises')

@login_required
def exercise_detail(request, pk=None, slug=None):
    """
    Vista para mostrar los detalles de un ejercicio.
    """
    # Buscar el ejercicio por pk o slug
    if slug:
        exercise = get_object_or_404(Exercise, slug=slug)
    else:
        exercise = get_object_or_404(Exercise, pk=pk)
    
    return render(request, 'exercises/exercise_detail.html', {
        'exercise': exercise,
        'can_edit': can_edit_exercise(request.user, exercise)
    }) 