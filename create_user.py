# Script para crear un usuario administrador
import os
import sys
import django

# Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
django.setup()

# Importar el modelo de usuario
from django.contrib.auth import get_user_model
User = get_user_model()

# Verificar si el usuario admin ya existe
if User.objects.filter(username='admin').exists():
    print("El usuario 'admin' ya existe.")
else:
    # Crear usuario administrador
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin'
    )
    print(f"Usuario administrador creado: {admin_user.username}")

# Imprimir todos los usuarios existentes
print("\nUsuarios en la base de datos:")
for user in User.objects.all():
    print(f"- {user.username} (email: {user.email})") 