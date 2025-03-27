from django.core.management.base import BaseCommand
from django.utils import timezone
from trainers.models import TrainerTraining, TrainerSet, TrainerStudent
from gym_tracker.trainings.models import Training, Set

class Command(BaseCommand):
    help = 'Migra las rutinas existentes al nuevo modelo de rutinas para entrenadores'

    def handle(self, *args, **options):
        # Obtener las relaciones entrenador-estudiante
        trainer_students = TrainerStudent.objects.all()
        
        # Contador de objetos migrados
        trainings_migrated = 0
        sets_migrated = 0
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando migración de entrenamientos... Encontradas {trainer_students.count()} relaciones entrenador-estudiante'))
        
        for ts in trainer_students:
            # Obtener todos los entrenamientos del estudiante
            student_trainings = Training.objects.filter(user=ts.student)
            
            # Para cada entrenamiento, crear uno nuevo en el nuevo modelo
            for training in student_trainings:
                # Verificar si existe un nombre en las notas o usar el nombre del ejercicio
                name = training.notes or f"Rutina {training.date}"
                description = f"Migrado desde entrenamiento existente. Ejercicio: {training.exercise.name}" if hasattr(training, 'exercise') and training.exercise else "Migrado desde entrenamiento existente"
                
                try:
                    # Crear el nuevo entrenamiento
                    new_training = TrainerTraining.objects.create(
                        user=ts.student,
                        created_by=ts.trainer,
                        name=name,
                        description=description,
                        date=training.date,
                        duration=training.duration,
                        completed=training.completed,
                        created_at=training.created_at,
                        updated_at=training.updated_at
                    )
                    trainings_migrated += 1
                    
                    # Si el entrenamiento tiene ejercicio, añadirlo como el primer set
                    if hasattr(training, 'exercise') and training.exercise:
                        # Crear un set para este ejercicio
                        TrainerSet.objects.create(
                            training=new_training,
                            exercise=training.exercise.name,
                            sets_count=training.total_sets,
                            reps=training.reps,
                            weight=training.weight,
                            notes=training.notes,
                            order=1
                        )
                        sets_migrated += 1
                    
                    # Obtener todos los sets del entrenamiento
                    training_sets = Set.objects.filter(training=training)
                    
                    # Orden para los sets adicionales (comienza en 2 si ya hay un ejercicio principal)
                    order = 2 if hasattr(training, 'exercise') and training.exercise else 1
                    
                    # Para cada set, crear uno nuevo en el nuevo modelo
                    for training_set in training_sets:
                        exercise_name = training_set.exercise.name if hasattr(training_set, 'exercise') and training_set.exercise else "Ejercicio desconocido"
                        TrainerSet.objects.create(
                            training=new_training,
                            exercise=exercise_name,
                            sets_count=1,  # En el modelo anterior cada set era una repetición
                            reps=training_set.reps,
                            weight=training_set.weight,
                            notes="",
                            order=order
                        )
                        order += 1
                        sets_migrated += 1
                    
                    self.stdout.write(f"Migrado entrenamiento {training.id} -> {new_training.id} con {order-1} ejercicios")
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error al migrar entrenamiento {training.id}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f'Migración completada: {trainings_migrated} entrenamientos y {sets_migrated} sets migrados')) 