from rest_framework import generics
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Exercise
from .serializers import ExerciseSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
import pandas as pd
import io
from datetime import datetime
from gym_tracker.users.permissions import is_admin_or_superuser

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
                    return redirect('exercises:exercise-list')
            
            # Convertir DataFrame a lista de diccionarios
            exercise_data = df.replace({pd.NA: None}).to_dict('records')
            
            # Contar ejercicios creados
            created_count = 0
            
            # Crear los ejercicios
            for data in exercise_data:
                # Filtrar solo los campos que existen en el modelo
                valid_data = {k: v for k, v in data.items() if v is not None and hasattr(Exercise, k)}
                
                # Crear el ejercicio
                Exercise.objects.create(**valid_data)
                created_count += 1
            
            messages.success(request, f'Se importaron {created_count} ejercicios correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al importar ejercicios: {str(e)}')
        
        return redirect('exercises:exercise-list')
    
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