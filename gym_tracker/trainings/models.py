from django.db import models
from django.conf import settings
from django.utils import timezone
from gym_tracker.exercises.models import Exercise  # Importación corregida

class Training(models.Model):
    """
    Modelo para almacenar la información de los entrenamientos.
    """
    INTENSITY_CHOICES = [
        ('Ligero', 'Ligero'),
        ('Moderado', 'Moderado'),
        ('Intenso', 'Intenso'),
        ('Muy Intenso', 'Muy Intenso'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)  # Relación con el ejercicio
    total_sets = models.IntegerField(default=4)  # Número de series
    reps = models.IntegerField(default=12)  # Número de repeticiones
    weight = models.FloatField(null=True, blank=True)  # Peso utilizado (opcional)
    date = models.DateField()  # Fecha del entrenamiento
    day_of_week = models.CharField(max_length=20)  # Día de la semana
    rest_time = models.IntegerField(default=90)  # tiempo en segundos
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='Moderado')  # Intensidad del ejercicio
    notes = models.TextField(null=True, blank=True)  # Permitimos valores nulos
    completed = models.BooleanField(default=False)  # Si el entrenamiento fue completado
    created_at = models.DateTimeField(default=timezone.now)  # Cambiado a default
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duración total en minutos")  # Duración total
    calories_burned = models.IntegerField(null=True, blank=True)  # Calorías quemadas estimadas
    
    # Para entrenamientos recurrentes
    is_recurring = models.BooleanField(default=False)  # Si es un entrenamiento recurrente
    recurring_days = models.CharField(max_length=100, blank=True, help_text="Días de la semana separados por comas")  # Días para entrenamientos recurrentes

    def __str__(self):
        return f"{self.exercise.name} - {self.date}"
        
    class Meta:
        ordering = ['-date', '-created_at']  # Ordenar por fecha, más recientes primero

class Set(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='training_sets')
    set_number = models.IntegerField()
    weight = models.FloatField(null=True, blank=True)  # Permitimos valores nulos
    reps = models.IntegerField()
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['training', 'set_number']
        unique_together = ['training', 'set_number']

    def __str__(self):
        return f"{self.training} - Serie {self.set_number}"
