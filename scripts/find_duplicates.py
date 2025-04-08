import os
import django
import sys
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Agregar el directorio del proyecto al path de Python
sys.path.append(str(BASE_DIR))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from exercises.models import Exercise
from trainings.models import Set
from trainers.models import TrainerSet
from collections import defaultdict

def find_duplicate_exercises():
    # Crear un diccionario para agrupar ejercicios por nombre
    exercises_by_name = defaultdict(list)
    
    # Obtener todos los ejercicios
    exercises = Exercise.objects.all()
    
    # Agrupar ejercicios por nombre
    for exercise in exercises:
        exercises_by_name[exercise.name.lower()].append(exercise)
    
    # Encontrar duplicados
    duplicates = {name: exercises for name, exercises in exercises_by_name.items() if len(exercises) > 1}
    
    print("\n=== EJERCICIOS DUPLICADOS ===")
    for name, exercises in duplicates.items():
        print(f"\nNombre: {name}")
        print(f"Cantidad de duplicados: {len(exercises)}")
        for exercise in exercises:
            # Verificar si el ejercicio está en uso
            in_use = Set.objects.filter(exercise=exercise).exists() or \
                    TrainerSet.objects.filter(exercise=exercise).exists()
            
            status = "EN USO" if in_use else "NO USADO"
            print(f"  - ID: {exercise.id}, Slug: {exercise.slug}, Estado: {status}")
    
    return duplicates

def delete_unused_duplicates():
    duplicates = find_duplicate_exercises()
    
    if not duplicates:
        print("\nNo se encontraron ejercicios duplicados.")
        return
    
    print("\n=== ELIMINACIÓN DE EJERCICIOS DUPLICADOS NO USADOS ===")
    deleted_count = 0
    
    for name, exercises in duplicates.items():
        print(f"\nProcesando: {name}")
        # Mantener el primer ejercicio y eliminar los demás si no están en uso
        keep_exercise = exercises[0]
        for exercise in exercises[1:]:
            # Verificar si el ejercicio está en uso
            in_use = Set.objects.filter(exercise=exercise).exists() or \
                    TrainerSet.objects.filter(exercise=exercise).exists()
            
            if not in_use:
                print(f"  - Eliminando ID: {exercise.id} (no usado)")
                exercise.delete()
                deleted_count += 1
            else:
                print(f"  - Manteniendo ID: {exercise.id} (en uso)")
    
    print(f"\nTotal de ejercicios eliminados: {deleted_count}")

if __name__ == "__main__":
    print("=== INICIO DE BÚSQUEDA DE DUPLICADOS ===")
    delete_unused_duplicates()
    print("\n=== PROCESO COMPLETADO ===") 