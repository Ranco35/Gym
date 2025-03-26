from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    """
    Modelo de usuario personalizado que hereda de AbstractUser.
    Añade campos adicionales para el rol del usuario y medidas corporales.
    """
    ROLE_CHOICES = [
        ('USER', 'Usuario'),
        ('TRAINER', 'Entrenador'),
        ('ADMIN', 'Administrador General'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    
    # Medidas corporales
    peso = models.FloatField(null=True, blank=True)  # Permite valores nulos
    altura = models.FloatField(null=True, blank=True, help_text="Altura en centímetros")
    cuello = models.FloatField(null=True, blank=True)
    cintura = models.FloatField(null=True, blank=True)
    cadera = models.FloatField(null=True, blank=True)
    pecho = models.FloatField(null=True, blank=True)
    brazos = models.FloatField(null=True, blank=True)
    muslo = models.FloatField(null=True, blank=True)
    muñeca = models.FloatField(null=True, blank=True)

    def clean(self):
        if self.role == 'ADMIN' and not self.is_superuser:
            raise ValidationError('Los administradores generales deben ser superusuarios.')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class TrainerUser(models.Model):
    """
    Modelo para manejar la relación entre entrenadores y sus usuarios.
    Permite que un usuario tenga múltiples entrenadores y viceversa.
    """
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_users', limit_choices_to={'role': 'TRAINER'})
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_trainers', limit_choices_to={'role': 'USER'})
    fecha_inicio = models.DateField(auto_now_add=False, default=timezone.now)
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True)

    class Meta:
        unique_together = ['trainer', 'user']
        verbose_name = 'Relación Entrenador-Usuario'
        verbose_name_plural = 'Relaciones Entrenador-Usuario'

    def clean(self):
        if self.trainer.role != 'TRAINER':
            raise ValidationError('El entrenador debe tener el rol de TRAINER.')
        if self.user.role != 'USER':
            raise ValidationError('El usuario debe tener el rol de USER.')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trainer.username} - {self.user.username}"