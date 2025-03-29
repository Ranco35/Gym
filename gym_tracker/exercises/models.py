from django.db import models
from django.conf import settings

class ExerciseCategory(models.Model):
    """
    Modelo para gestionar las categorías de ejercicios de forma dinámica.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoría de Ejercicio"
        verbose_name_plural = "Categorías de Ejercicios"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_default_pk(cls):
        """Retorna la PK de una categoría por defecto o None si no existe ninguna."""
        category, created = cls.objects.get_or_create(name="Otros")
        return category.pk

class Exercise(models.Model):
    """
    Modelo para almacenar la información de los ejercicios.
    """
    DIFFICULTY_CHOICES = [
        ('Principiante', 'Principiante'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        ExerciseCategory, 
        on_delete=models.SET_DEFAULT, 
        default=ExerciseCategory.get_default_pk,
        related_name='exercises'
    )
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