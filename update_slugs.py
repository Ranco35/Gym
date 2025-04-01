import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
django.setup()

# Importar modelos después de la configuración
from gym_tracker.exercises.models import Exercise
from django.utils.text import slugify
from django.db import connection

def update_slugs():
    """Actualiza los slugs de todos los ejercicios"""
    
    # Verificar si la columna slug existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='exercises_exercise' AND column_name='slug';")
        if not cursor.fetchone():
            print("La columna 'slug' no existe todavía. Asegúrate de que las migraciones se han aplicado.")
            return
    
    exercises = Exercise.objects.all()
    print(f"Actualizando {exercises.count()} ejercicios...")
    
    for exercise in exercises:
        # Generar un slug base
        slug_base = slugify(exercise.name) if exercise.name else f"ejercicio-{exercise.id}"
        slug = slug_base
        counter = 1
        
        # Verificar si ya existe un ejercicio con este slug
        while Exercise.objects.filter(slug=slug).exclude(id=exercise.id).exists():
            # Si existe, añadir un contador al final
            slug = f"{slug_base}-{counter}"
            counter += 1
        
        # Guardar el slug único
        exercise.slug = slug
        exercise.save()
        print(f"Actualizado: {exercise.name} -> {slug}")
    
    print(f"Se actualizaron {exercises.count()} ejercicios.")

if __name__ == "__main__":
    update_slugs() 