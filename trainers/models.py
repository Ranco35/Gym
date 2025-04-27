from django.db import models
from django.conf import settings
from django.utils import timezone
from gym_tracker.trainings.models import Training, Set
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator

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

class TrainerTraining(models.Model):
    """Modelo para rutinas de entrenamiento creadas por entrenadores para sus estudiantes."""
    DAYS_OF_WEEK = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    name = models.CharField("Nombre", max_length=200)
    description = models.TextField("Descripción", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_trainings')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_trainings')
    start_date = models.DateField("Fecha de inicio")
    end_date = models.DateField("Fecha de fin", null=True, blank=True)
    duration = models.IntegerField("Duración (minutos)", null=True, blank=True)
    completed = models.BooleanField("Completado", default=False)
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = "Rutina de entrenamiento"
        verbose_name_plural = "Rutinas de entrenamiento"

    def __str__(self):
        return f"{self.name} - {self.start_date}"
        
    def get_total_exercises(self):
        """Calcula el número total de ejercicios en toda la rutina."""
        return sum(day.sets.filter(is_active=True).count() for day in self.days.filter(is_active=True))
        
    def get_days_display(self):
        """Devuelve una representación legible de los días de la semana programados."""
        days = self.days.filter(is_active=True).order_by(
            models.Case(
                models.When(day_of_week='Lunes', then=models.Value(1)),
                models.When(day_of_week='Martes', then=models.Value(2)),
                models.When(day_of_week='Miércoles', then=models.Value(3)),
                models.When(day_of_week='Jueves', then=models.Value(4)),
                models.When(day_of_week='Viernes', then=models.Value(5)),
                models.When(day_of_week='Sábado', then=models.Value(6)),
                models.When(day_of_week='Domingo', then=models.Value(7)),
                default=models.Value(10),
                output_field=models.IntegerField()
            )
        )
        if not days:
            return "No hay días programados"
        return ", ".join(day.day_of_week for day in days)

    def get_active_days(self):
        """Devuelve los días activos ordenados."""
        return self.days.filter(is_active=True).order_by(
            models.Case(
                models.When(day_of_week='Lunes', then=models.Value(1)),
                models.When(day_of_week='Martes', then=models.Value(2)),
                models.When(day_of_week='Miércoles', then=models.Value(3)),
                models.When(day_of_week='Jueves', then=models.Value(4)),
                models.When(day_of_week='Viernes', then=models.Value(5)),
                models.When(day_of_week='Sábado', then=models.Value(6)),
                models.When(day_of_week='Domingo', then=models.Value(7)),
                default=models.Value(10),
                output_field=models.IntegerField()
            )
        )

    @property
    def creator(self):
        """Devuelve el creador de la rutina."""
        return self.created_by

class TrainerTrainingDay(models.Model):
    """Modelo para almacenar los días de entrenamiento de una rutina."""
    DAYS_OF_WEEK = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    training = models.ForeignKey(TrainerTraining, on_delete=models.CASCADE, related_name='days')
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    focus = models.CharField(max_length=255, blank=True, verbose_name="Enfoque")
    day_order = models.IntegerField(default=0, verbose_name="Orden del día")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, verbose_name="Notas del día")

    class Meta:
        ordering = [
            models.Case(
                models.When(day_of_week='Lunes', then=models.Value(1)),
                models.When(day_of_week='Martes', then=models.Value(2)),
                models.When(day_of_week='Miércoles', then=models.Value(3)),
                models.When(day_of_week='Jueves', then=models.Value(4)),
                models.When(day_of_week='Viernes', then=models.Value(5)),
                models.When(day_of_week='Sábado', then=models.Value(6)),
                models.When(day_of_week='Domingo', then=models.Value(7)),
                default=models.Value(10),
                output_field=models.IntegerField()
            )
        ]
        unique_together = ('training', 'day_of_week')
        verbose_name = "Día de Entrenamiento"
        verbose_name_plural = "Días de Entrenamiento"

    def __str__(self):
        return f"{self.training.name} - {self.day_of_week}"

    def get_exercises(self):
        """Devuelve los ejercicios activos ordenados."""
        return self.sets.filter(is_active=True).order_by('order')

    def get_total_exercises(self):
        """Devuelve el total de ejercicios activos para este día."""
        return self.sets.filter(is_active=True).count()

class TrainerTrainingExercise(models.Model):
    training_day = models.ForeignKey(TrainerTrainingDay, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.CASCADE)
    sets = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Número de series")
    reps = models.CharField(
        max_length=50,
        validators=[RegexValidator(r'^\d+(-\d+)?$', 'Formato: número o rango (ej: 10-12)')],
        verbose_name="Repeticiones"
    )
    weight = models.CharField(
        max_length=50,
        blank=True,
        validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Formato: número decimal')],
        verbose_name="Peso sugerido"
    )
    rest_time = models.IntegerField(default=60, help_text="Tiempo de descanso en segundos")
    exercise_order = models.IntegerField(default=0, verbose_name="Orden del ejercicio")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, verbose_name="Notas del ejercicio")

    class Meta:
        verbose_name = "Ejercicio de Entrenamiento"
        verbose_name_plural = "Ejercicios de Entrenamiento"
        ordering = ['exercise_order']

    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"

class CompletedExercise(models.Model):
    training_exercise = models.ForeignKey(TrainerTrainingExercise, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    actual_sets = models.IntegerField(verbose_name="Series realizadas")
    actual_reps = models.CharField(max_length=50, verbose_name="Repeticiones realizadas")
    actual_weight = models.CharField(max_length=50, blank=True, verbose_name="Peso utilizado")
    notes = models.TextField(blank=True, verbose_name="Notas de la sesión")
    duration = models.IntegerField(null=True, blank=True, verbose_name="Duración en segundos")
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('Fácil', 'Fácil'),
            ('Moderado', 'Moderado'),
            ('Difícil', 'Difícil')
        ],
        default='Moderado'
    )

    class Meta:
        verbose_name = "Ejercicio Completado"
        verbose_name_plural = "Ejercicios Completados"
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.training_exercise.exercise.name} - {self.completed_at.date()}"

class TrainerSet(models.Model):
    """Series de ejercicios para rutinas de entrenamiento."""
    training_day = models.ForeignKey(TrainerTrainingDay, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.CASCADE, verbose_name="Ejercicio")
    sets_count = models.IntegerField(
        "Número de series",
        default=3,
        validators=[MinValueValidator(1)]
    )
    reps = models.CharField(
        "Repeticiones",
        max_length=50,
        default="12",
        validators=[RegexValidator(r'^\d+(-\d+)?$', 'Formato: número o rango (ej: 10-12)')]
    )
    weight = models.CharField(
        "Peso (kg)",
        max_length=50,
        blank=True,
        default="0",
        validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Formato: número decimal')]
    )
    rest_time = models.IntegerField("Tiempo de descanso (segundos)", default=60)
    order = models.IntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Serie de ejercicio"
        verbose_name_plural = "Series de ejercicios"

    def __str__(self):
        return f"{self.exercise.name} - {self.sets_count}x{self.reps}"
        
    @property
    def suggested_weight(self):
        """Devuelve el peso sugerido para este ejercicio."""
        return self.weight

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
    student_notes = models.TextField(blank=True, null=True)
    timer_started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sesión en vivo: {self.trainer_student} - {self.started_at}"

    def end_session(self):
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()

    def start_timer(self):
        if not self.timer_started_at:
            self.timer_started_at = timezone.now()
            self.save()
    
    def reset_timer(self):
        self.timer_started_at = None
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
    # Añadir campo para llevar un seguimiento de las series completadas
    set_number = models.IntegerField(default=1)  # Número de serie (1, 2, 3, etc)

    def __str__(self):
        return f"Serie en vivo: {self.set} - Serie #{self.set_number} - {self.completed_at}"

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
