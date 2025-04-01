from django.db import models
from django.conf import settings
from ..storage_backend import GymStorage
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify
from django.urls import reverse
from gym_pwa.utils import convert_to_webp

class Equipment(models.Model):
    """
    Modelo para gestionar el equipamiento de ejercicios.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipamiento"
        verbose_name_plural = "Equipamientos"
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_pk(cls):
        """Retorna la PK de un equipamiento por defecto o None si no existe ninguno."""
        equipment, created = cls.objects.get_or_create(name="Sin equipamiento")
        return equipment.pk

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
    MUSCLE_GROUPS = [
        ('chest', 'Pecho'),
        ('back', 'Espalda'),
        ('shoulders', 'Hombros'),
        ('arms', 'Brazos'),
        ('legs', 'Piernas'),
        ('core', 'Core'),
        ('full_body', 'Cuerpo completo'),
        ('cardio', 'Cardio'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUPS, verbose_name='Grupo muscular')
    primary_muscles = models.CharField(max_length=100, blank=True, verbose_name='Músculos principales')
    secondary_muscles = models.CharField(max_length=100, blank=True, verbose_name='Músculos secundarios')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='intermediate', verbose_name='Dificultad')
    equipment = models.CharField(max_length=100, blank=True, verbose_name='Equipamiento')
    tips = models.TextField(blank=True, null=True, verbose_name='Consejos')
    
    image = models.ImageField(upload_to='exercises/', blank=True, null=True, verbose_name='Imagen')
    video_url = models.URLField(blank=True, null=True, verbose_name='URL del video')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        # Generar slug si no existe
        if not self.slug:
            self.slug = slugify(self.name)
            
        # Convertir imagen a WebP si existe y no es ya WebP
        if self.image and not self.image.name.endswith('.webp'):
            self.image = convert_to_webp(self.image)
            
        super(Exercise, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('exercise_detail', args=[self.slug])
    
    def __str__(self):
        return self.name
    
    def clean(self):
        # Validar el link de YouTube
        if self.video_url and 'youtube.com' not in self.video_url and 'youtu.be' not in self.video_url:
            raise ValidationError({
                'video_url': 'El enlace debe ser de YouTube (youtube.com o youtu.be)'
            })

    def get_youtube_embed_url(self):
        """Convierte la URL de YouTube en una URL de embed"""
        if not self.video_url:
            return None
            
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[1]
        else:
            return None
            
        return f'https://www.youtube.com/embed/{video_id}'

    class Meta:
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'
        ordering = ['name']

class ExerciseImage(models.Model):
    """Modelo para imágenes adicionales de ejercicios."""
    exercise = models.ForeignKey(Exercise, related_name='images', on_delete=models.CASCADE, verbose_name='Ejercicio')
    image = models.ImageField(upload_to='exercises/gallery/', verbose_name='Imagen')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Leyenda')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Orden')
    
    def save(self, *args, **kwargs):
        # Convertir imagen a WebP si no es ya WebP
        if self.image and not self.image.name.endswith('.webp'):
            self.image = convert_to_webp(self.image)
            
        super(ExerciseImage, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Imagen de ejercicio'
        verbose_name_plural = 'Imágenes de ejercicios'
        ordering = ['order']