from django.db import models
from django.conf import settings
from ..storage_backend import GymStorage
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files import File

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
    
    name = models.CharField(max_length=255, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    category = models.ForeignKey(
        ExerciseCategory, 
        on_delete=models.SET_DEFAULT, 
        default=ExerciseCategory.get_default_pk,
        related_name='exercises',
        verbose_name='Categoría'
    )
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='Dificultad')
    
    # Nuevos campos
    primary_muscles = models.CharField(max_length=255, blank=True, null=True, verbose_name='Músculos principales')
    secondary_muscles = models.CharField(max_length=255, blank=True, null=True, verbose_name='Músculos secundarios')
    equipment = models.CharField(max_length=255, blank=True, null=True, verbose_name='Equipamiento')
    instructions = models.TextField(blank=True, null=True, verbose_name='Instrucciones')
    tips = models.TextField(blank=True, null=True, verbose_name='Consejos')
    
    # Campo para la imagen del ejercicio
    image = models.ImageField(
        upload_to='exercises',
        storage=GymStorage(),
        null=True,
        blank=True,
        verbose_name='Imagen del ejercicio (JPG, PNG o GIF)'
    )

    # Campo para el video de YouTube
    youtube_link = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Link de YouTube',
        help_text='Ingresa la URL del video de YouTube que muestra cómo realizar el ejercicio'
    )
    
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

    def clean(self):
        # Validar el link de YouTube
        if self.youtube_link and 'youtube.com' not in self.youtube_link and 'youtu.be' not in self.youtube_link:
            raise ValidationError({
                'youtube_link': 'El enlace debe ser de YouTube (youtube.com o youtu.be)'
            })

    def save(self, *args, **kwargs):
        # Comprimir imagen si se ha subido una nueva
        if self.image and hasattr(self.image, 'file'):
            # Abrir la imagen usando PIL
            img = Image.open(self.image)
            
            # Convertir a RGB si es necesario
            if img.mode != 'RGB' and img.format != 'GIF':
                img = img.convert('RGB')
            
            # No procesar GIFs
            if img.format != 'GIF':
                # Redimensionar si es muy grande (manteniendo proporción)
                max_size = (800, 800)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Guardar con compresión
                output = BytesIO()
                img.save(output, format='WEBP', quality=85, optimize=True)
                output.seek(0)
                
                # Reemplazar el archivo original
                self.image = File(output, name=self.image.name.split('/')[-1].rsplit('.', 1)[0] + '.webp')
            
        super().save(*args, **kwargs)

    def get_youtube_embed_url(self):
        """Convierte la URL de YouTube en una URL de embed"""
        if not self.youtube_link:
            return None
            
        if 'youtube.com/watch?v=' in self.youtube_link:
            video_id = self.youtube_link.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in self.youtube_link:
            video_id = self.youtube_link.split('youtu.be/')[1]
        else:
            return None
            
        return f'https://www.youtube.com/embed/{video_id}'