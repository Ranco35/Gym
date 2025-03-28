from django.db import models
from django.conf import settings

class Exercise(models.Model):
    """
    Modelo para almacenar la información de los ejercicios.
    """
    CATEGORY_CHOICES = [
        ('Pecho', 'Pecho'),
        ('Espalda', 'Espalda'),
        ('Piernas', 'Piernas'),
        ('Hombros', 'Hombros'),
        ('Brazos', 'Brazos'),
        ('Abdominales', 'Abdominales'),
        ('Core', 'Core'),
        ('Cardio', 'Cardio'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('Principiante', 'Principiante'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Nuevos campos
    primary_muscles = models.CharField(max_length=255, blank=True, null=True)
    secondary_muscles = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.CharField(max_length=255, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    tips = models.TextField(blank=True, null=True)
    
    # Campo para registrar quién creó el ejercicio
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_exercises'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name