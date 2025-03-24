from django.db import models
from django.conf import settings
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
    sets = models.IntegerField(default=3)  # Número de series
    reps = models.IntegerField(default=10)  # Número de repeticiones
    weight = models.FloatField(null=True, blank=True)  # Peso utilizado (opcional)
    date = models.DateField()  # Fecha del entrenamiento
    day_of_week = models.CharField(max_length=10, blank=True)  # Día de la semana
    rest_time = models.IntegerField(default=60, help_text="Tiempo de descanso entre series en segundos")  # Tiempo de descanso
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='Moderado')  # Intensidad del ejercicio
    notes = models.TextField(blank=True, null=True)  # Notas adicionales
    completed = models.BooleanField(default=False)  # Si el entrenamiento fue completado
    duration = models.IntegerField(null=True, blank=True, help_text="Duración total en minutos")  # Duración total
    calories_burned = models.IntegerField(null=True, blank=True)  # Calorías quemadas estimadas
    
    # Para entrenamientos recurrentes
    is_recurring = models.BooleanField(default=False)  # Si es un entrenamiento recurrente
    recurring_days = models.CharField(max_length=100, blank=True, help_text="Días de la semana separados por comas")  # Días para entrenamientos recurrentes

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"
        
    class Meta:
        ordering = ['-date']  # Ordenar por fecha, más recientes primero
