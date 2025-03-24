from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de usuario personalizado que hereda de AbstractUser.
    Añade campos adicionales para el rol del usuario y medidas corporales.
    """
    ROLE_CHOICES = [
        ('USER', 'Usuario'),
        ('TRAINER', 'Entrenador'),
        ('ADMIN', 'Administrador'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    
    # Medidas corporales
    peso = models.FloatField(null=True, blank=True)  # Permite valores nulos
    cuello = models.FloatField(null=True, blank=True)
    cintura = models.FloatField(null=True, blank=True)
    cadera = models.FloatField(null=True, blank=True)
    pecho = models.FloatField(null=True, blank=True)
    brazos = models.FloatField(null=True, blank=True)
    muslo = models.FloatField(null=True, blank=True)
    muñeca = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username