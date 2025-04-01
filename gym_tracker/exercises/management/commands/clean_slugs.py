from django.core.management.base import BaseCommand
from gym_tracker.exercises.models import Exercise
import re

class Command(BaseCommand):
    help = 'Limpia y repara todos los slugs existentes en el modelo Exercise'

    def handle(self, *args, **options):
        exercises = Exercise.objects.all()
        updated_count = 0

        self.stdout.write(f"Encontrados {exercises.count()} ejercicios para revisar")

        for exercise in exercises:
            old_slug = exercise.slug
            if old_slug:
                # Limpiar el slug de caracteres especiales
                new_slug = re.sub(r'[^a-zA-Z0-9_-]', '-', old_slug)
                
                # Si el slug cambió, actualizar y guardar
                if new_slug != old_slug:
                    # Asegurar que el nuevo slug sea único
                    counter = 1
                    base_slug = new_slug
                    while Exercise.objects.filter(slug=new_slug).exclude(pk=exercise.pk).exists():
                        new_slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    exercise.slug = new_slug
                    exercise.save(update_fields=['slug'])
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Slug actualizado para '{exercise.name}': {old_slug} -> {new_slug}"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"Proceso completado. {updated_count} slugs actualizados."
        )) 