from django.db import models

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
        # ... agrega más categorías si las necesitas
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    difficulty = models.CharField(max_length=10)  # Puedes usar opciones como 'Fácil', 'Medio', 'Difícil'
    # ... puedes agregar campos como imágenes o videos si lo necesitas

    def __str__(self):
        return self.name