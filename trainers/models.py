from django.db import models
from django.conf import settings
from django.utils import timezone
from gym_tracker.trainings.models import Training, Set

class TrainerProfile(models.Model):
    """Perfil del entrenador con información adicional."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_profile')
    specialization = models.CharField("Especialización", max_length=100, blank=True)
    experience_years = models.IntegerField("Años de experiencia", default=0)
    certification = models.CharField("Certificación", max_length=200, blank=True)
    bio = models.TextField("Biografía", blank=True)
    active = models.BooleanField("Activo", default=True)
    max_students = models.IntegerField("Máximo de estudiantes", default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'trainers'
        verbose_name = 'Perfil de Entrenador'
        verbose_name_plural = 'Perfiles de Entrenadores'

    def __str__(self):
        return f"Entrenador: {self.user.username}"

    def get_active_students_count(self):
        return self.trainer_relationships.filter(active=True).count()

    def is_accepting_students(self):
        return self.active and self.get_active_students_count() < self.max_students

class TrainerStudent(models.Model):
    """Relación entre entrenador y alumno."""
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_relationships')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_relationships')
    active = models.BooleanField(default=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['trainer', 'student']

    def __str__(self):
        return f"{self.trainer.username} -> {self.student.username}"

# Nuevo modelo para las rutinas de entrenamiento creadas por entrenadores
class TrainerTraining(models.Model):
    """Modelo para rutinas de entrenamiento creadas por entrenadores para sus estudiantes."""
    name = models.CharField("Nombre", max_length=200)
    description = models.TextField("Descripción", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_trainings')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_trainings')
    date = models.DateField("Fecha programada")
    duration = models.IntegerField("Duración (minutos)", null=True, blank=True)
    completed = models.BooleanField("Completado", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Rutina de entrenamiento"
        verbose_name_plural = "Rutinas de entrenamiento"

    def __str__(self):
        return f"{self.name} - {self.date}"

class TrainerSet(models.Model):
    """Series de ejercicios para rutinas de entrenamiento."""
    training = models.ForeignKey(TrainerTraining, on_delete=models.CASCADE, related_name='sets')
    exercise = models.CharField("Ejercicio", max_length=200)
    sets_count = models.IntegerField("Número de series", default=3)
    reps = models.IntegerField("Repeticiones", default=12)
    weight = models.FloatField("Peso (kg)", null=True, blank=True)
    notes = models.TextField("Notas", blank=True)
    order = models.IntegerField("Orden", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Serie de ejercicio"
        verbose_name_plural = "Series de ejercicios"

    def __str__(self):
        return f"{self.exercise} - {self.training.name}"

class LiveTrainingSession(models.Model):
    """Sesión de entrenamiento en vivo."""
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('completed', 'Completado')
    ]

    training = models.ForeignKey(TrainerTraining, on_delete=models.CASCADE)
    trainer_student = models.ForeignKey(TrainerStudent, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    trainer_notes = models.TextField(blank=True)
    student_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Sesión en vivo: {self.trainer_student} - {self.started_at}"

    def end_session(self):
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()

class LiveSet(models.Model):
    """Registro de series durante el entrenamiento en vivo."""
    session = models.ForeignKey(LiveTrainingSession, on_delete=models.CASCADE, related_name='live_sets')
    set = models.ForeignKey(TrainerSet, on_delete=models.CASCADE)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    weight = models.FloatField()
    reps = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    trainer_feedback = models.TextField(blank=True)
    form_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating de la forma
    perceived_effort = models.IntegerField(null=True, blank=True)  # 1-10 RPE

    def __str__(self):
        return f"Serie en vivo: {self.set} - {self.completed_at}"

class TrainerFeedback(models.Model):
    """Retroalimentación general del entrenador."""
    trainer_student = models.ForeignKey(TrainerStudent, on_delete=models.CASCADE)
    training = models.ForeignKey(TrainerTraining, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField(null=True, blank=True)  # 1-5 rating general
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback: {self.trainer_student} - {self.created_at}"
