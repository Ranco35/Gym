from django.db import models
from django.conf import settings  # Importa settings para acceder al modelo de usuario
from django.db.models import Count, Sum

class Workout(models.Model):
    """
    Modelo para almacenar la información de los entrenamientos.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Relación con el usuario
    name = models.CharField(max_length=255)  # Nombre del entrenamiento
    date = models.DateField(auto_now_add=True)  # Fecha del entrenamiento
    # ... otros campos que necesites, como duración, notas, etc.

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class WeeklyRoutine(models.Model):
    """
    Modelo para almacenar rutinas semanales de entrenamiento.
    """
    DAYS_OF_WEEK = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # Nombre de la rutina semanal
    description = models.TextField(blank=True, null=True)  # Descripción opcional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_total_exercises(self):
        """
        Calcula el número total de ejercicios en toda la rutina.
        """
        # Contar los ejercicios en todos los días de la rutina
        total = 0
        for day in self.routineday_set.all():
            total += day.routineexercise_set.count()
        return total
    
    def get_days_display(self):
        """
        Devuelve una cadena con los días de la semana en formato legible.
        """
        days = self.routineday_set.values_list('day_of_week', flat=True)
        return ", ".join(days)


class RoutineDay(models.Model):
    """
    Modelo para almacenar los días de entrenamiento de una rutina semanal.
    """
    routine = models.ForeignKey(WeeklyRoutine, related_name='days', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20, choices=WeeklyRoutine.DAYS_OF_WEEK)
    focus = models.CharField(max_length=255, blank=True, null=True)  # Ej: "Pecho", "Piernas", etc.

    def __str__(self):
        return f"{self.routine.name} - {self.day_of_week} ({self.focus})"


class RoutineExercise(models.Model):
    """
    Modelo para los ejercicios de un día específico en una rutina.
    """
    routine_day = models.ForeignKey(RoutineDay, related_name='exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.CharField(max_length=50, default='10')  # Puede ser "10", "8-12", etc.
    weight = models.CharField(max_length=50, blank=True, null=True)  # Puede ser "50kg", "Hasta fallo", etc.
    rest_time = models.IntegerField(default=60, help_text="Tiempo de descanso en segundos")
    order = models.IntegerField(default=0)  # Para ordenar los ejercicios
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"