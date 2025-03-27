from django.db import models
from django.conf import settings
from django.utils import timezone
from gym_tracker.exercises.models import Exercise  # Importación corregida
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class TrainerStudent(models.Model):
    """Modelo para gestionar la relación entre entrenadores y alumnos."""
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='training_trainer_relationships'  # Cambiado para evitar conflictos
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='training_student_relationships'  # Cambiado para evitar conflictos
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['trainer', 'student']

    def __str__(self):
        return f"{self.trainer.username} -> {self.student.username}"

class LiveTraining(models.Model):
    """Modelo para gestionar entrenamientos en vivo."""
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('completed', 'Completado')
    ]

    training = models.ForeignKey('Training', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_trainings')
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supervised_trainings', null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Entrenamiento en vivo: {self.student.username} - {self.started_at}"

    def end_session(self):
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()

class LiveSet(models.Model):
    """Modelo para registrar series en tiempo real."""
    live_training = models.ForeignKey(LiveTraining, on_delete=models.CASCADE, related_name='live_sets')
    set = models.ForeignKey(
        Set,
        on_delete=models.CASCADE,
        related_name='training_live_sets'
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='training_completed_sets'  # Agregado para evitar conflictos
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    trainer_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Serie en vivo: {self.set} - {self.completed_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear o actualizar el perfil del usuario automáticamente."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
