import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymworl.settings')
django.setup()

from django.contrib.auth import get_user_model
from trainers.models import TrainerProfile

User = get_user_model()

def create_trainer_profile(username):
    try:
        user = User.objects.get(username=username)
        
        # Crear perfil de entrenador si no existe
        trainer_profile, created = TrainerProfile.objects.get_or_create(
            user=user,
            defaults={
                'specialization': 'Entrenador Personal',
                'experience_years': 1,
                'certification': 'Certificación Básica',
                'bio': 'Entrenador profesional',
                'is_available': True,
                'max_students': 10
            }
        )
        
        if created:
            print(f'Perfil de entrenador creado para {username}')
        else:
            print(f'El perfil de entrenador ya existe para {username}')
            
    except User.DoesNotExist:
        print(f'El usuario {username} no existe')

if __name__ == '__main__':
    username = 'Fernanda'  # Establecemos directamente el nombre de usuario
    create_trainer_profile(username) 