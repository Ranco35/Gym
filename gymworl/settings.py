import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# === GENERAL DJANGO ===
DEBUG = env.bool('DEBUG', default=True)
DJANGO_ENV = env('DJANGO_ENV', default='development')
SECRET_KEY = env('SECRET_KEY')

# === HOSTS PERMITIDOS ===
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', '134.199.224.217', 'gym.360losrios.cl'])

# === DIGITALOCEAN SPACES ===
AWS_ACCESS_KEY_ID = env('DO_SPACE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('DO_SPACE_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('DO_SPACE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('DO_SPACE_ENDPOINT_URL')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'ACL': 'public-read',
}

# Configuración de almacenamiento de archivos
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com/media/"

# Configuración de archivos estáticos (opcional)
AWS_STATIC_LOCATION = 'static'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com/{AWS_STATIC_LOCATION}/"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'channels',
    'corsheaders',
    'gym_tracker.users',
    'gym_tracker.workouts',
    'gym_tracker.exercises',
    'gym_tracker.trainings',
    'gym_tracker.stats',
    'trainers.apps.TrainersConfig',
]

# Channels configuration
ASGI_APPLICATION = 'gymworl.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = ['content-disposition']

# Añadir middleware de CORS
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Debe estar antes de CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === BASE DE DATOS REMOTA (DIGITALOCEAN vía túnel SSH en local) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gym_db',
        'USER': 'eduardo',
        'PASSWORD': '123llifen789.',
        'HOST': 'localhost',
        'PORT': '5433',
        'OPTIONS': {
            'sslmode': 'disable',
            'connect_timeout': 10,
        }
    }
}

# Configuración de archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de autenticación
AUTH_USER_MODEL = 'users.User'

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' 