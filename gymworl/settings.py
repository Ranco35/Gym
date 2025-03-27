ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'gym.360losrios.cl'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gym_tracker',
    'gym_tracker.exercises',
    'gym_tracker.workouts',
    'gym_tracker.trainings',
    'gym_tracker.users',
    'gym_tracker.stats',
    'trainers',
]

# Configuración de autenticación
AUTH_USER_MODEL = 'users.CustomUser'  # Si estás usando un modelo de usuario personalizado 