from django.db import models

MUSCLE_GROUPS = [
    ('chest', 'Pecho'),
    ('back', 'Espalda'),
    ('shoulders', 'Hombros'),
    ('arms', 'Brazos'),
    ('legs', 'Piernas'),
    ('core', 'Core'),
    ('full_body', 'Cuerpo Completo'),
    ('cardio', 'Cardio'),
]

DIFFICULTY_CHOICES = [
    ('beginner', 'Principiante'),
    ('intermediate', 'Intermedio'),
    ('advanced', 'Avanzado'),
]

class Exercise(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    muscle_group = models.CharField(max_length=50, choices=MUSCLE_GROUPS, verbose_name="Grupo Muscular")
    equipment = models.ForeignKey('Equipment', on_delete=models.SET_NULL, null=True, verbose_name="Equipamiento")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="Dificultad")
    image = models.ImageField(upload_to='exercises/', null=True, blank=True, verbose_name="Imagen")
    youtube_url = models.URLField(max_length=200, null=True, blank=True, verbose_name="URL de YouTube")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['name']

    def __str__(self):
        return self.name

    def soft_delete(self):
        """Marca el ejercicio como inactivo en lugar de eliminarlo."""
        self.is_active = False
        self.save()

    def restore(self):
        """Restaura un ejercicio previamente marcado como inactivo."""
        self.is_active = True
        self.save() 