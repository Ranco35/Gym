import os
from pathlib import Path
import environ
from datetime import timedelta

# Definir BASE_DIR antes de leer el .env
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Variables de entorno
SECRET_KEY = env('SECRET_KEY', default='your-secret-key-change-in-production')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '134.199.224.217', '0.0.0.0', 'gym.360losrios.cl'])

# Configuración de CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://134.199.224.217:8000',
    'http://134.199.224.217',
    'http://gym.360losrios.cl',
    'https://gym.360losrios.cl',
]

# Configuración estándar de Django para CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_FAILURE_VIEW = 'gym_tracker.views.csrf_failure'

# Application definition
INSTALLED_APPS = [
    'admin_interface',  # debe estar antes de django.contrib.admin
    'colorfield',  # requerido por admin_interface
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'gym_tracker.users',
    'gym_tracker.workouts',
    'gym_tracker.exercises',
    'gym_tracker.trainings',
    'gym_tracker.stats',  # Nueva aplicación de estadísticas
    'trainers.apps.TrainersConfig',  # Usar la configuración completa de la app
    'gym_tracker.pwa',  # Aplicación PWA
    'gym_tracker.goals',
    'gym_tracker.notes',
    'gym_tracker.measurements',
]

# Middleware - Deshabilitamos CSRF temporalmente en desarrollo
if DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',  # Habilitamos CSRF
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'gym_tracker.middleware.OptionsMiddleware',
    ]
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'gym_tracker.middleware.OptionsMiddleware',
    ]

ROOT_URLCONF = 'gym_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'gym_tracker/templates'],
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

WSGI_APPLICATION = 'gym_tracker.wsgi.application'

# Configuración de la Base de Datos
#DATABASES = {
 #   'default': {
  #      'ENGINE': 'django.db.backends.sqlite3',
   #     'NAME': BASE_DIR / 'db.sqlite3',
    #}
#}
# Base da datos diggitalocean
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),  # Cambiado a 5432
    }
}


#3 Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacionalización
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'  # Zona horaria para Chile
USE_I18N = True
USE_L10N = True  # Formato de fechas local
USE_TZ = True

# Archivos estáticos y medios
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Configuración del campo de auto-incremento por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'users.User'

# Configuración de DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Configuración de Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Configuración de autenticación
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://gym.360losrios.cl",
    "https://gym.360losrios.cl",
    "https://nyc3.digitaloceanspaces.com",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
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

# Configuración del tema de admin-interface
X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']

# Configuración de admin-interface
ADMIN_INTERFACE_THEME_SETTINGS = {
    'name': 'Gym Tracker 360 Los Ríos',
    'title': 'Gym Tracker 360 Los Ríos',
    'logo': None,
    'copyright': '© 2024 by Eduardo Proboste Furet',
    
    # Colores principales
    'css_header_background_color': '#2C3E50',
    'css_header_text_color': '#FFFFFF',
    'css_header_link_color': '#FFFFFF',
    'css_header_link_hover_color': '#18BC9C',
    
    # Colores de módulos
    'css_module_background_color': '#18BC9C',
    'css_module_text_color': '#FFFFFF',
    'css_module_link_color': '#FFFFFF',
    'css_module_link_hover_color': '#2C3E50',
    'css_module_rounded_corners': True,
    
    # Colores de enlaces y botones
    'css_generic_link_color': '#18BC9C',
    'css_generic_link_hover_color': '#2C3E50',
    'css_generic_link_active_color': '#15967D',
    'css_save_button_background_color': '#18BC9C',
    'css_save_button_background_hover_color': '#2C3E50',
    'css_save_button_text_color': '#FFFFFF',
    
    # Configuración de la interfaz
    'list_filter_dropdown': True,
    'list_filter_sticky': True,
    'related_modal_active': True,
    'related_modal_background_color': '#2C3E50',
    'related_modal_background_opacity': '0.8',
    'show_fieldsets_as_tabs': True,
    'show_ui_builder': True,
    
    # Características adicionales
    'form_sticky': True,
    'foldable_apps': True,
    'language_chooser_active': False,
    'list_filter_highlight': True,
    'list_filter_removal_links': True,
    'collapsible_stacked_inlines': True,
    'recent_actions_visible': True,
    
    # Personalización de la navegación
    'show_nav_sidebar': True,
    'navigation_expanded': True,
    
    # Mensaje de bienvenida
    'welcome_sign': 'Bienvenido al Panel de Administración de Gym Tracker 360 Los Ríos',
    
    # Configuración del tema
    'theme': 'default',
    'dark_mode_theme': True
}


import os
from storages.backends.s3boto3 import S3Boto3Storage

# ----------------------------
# Configuración de DigitalOcean Spaces
# ----------------------------
AWS_ACCESS_KEY_ID = os.getenv('DO_SPACE_ACCESS_KEY_ID', 'DO00ELANT2VXA3J9G3Q9')
AWS_SECRET_ACCESS_KEY = os.getenv('DO_SPACE_SECRET_ACCESS_KEY', 'ed2stFqA+Oj0Avrpow2/Z1obmzjcx8NG9Iooh7k6Z/o')
AWS_STORAGE_BUCKET_NAME = os.getenv('DO_SPACE_BUCKET_NAME', 'lifen-cl-system')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_ENDPOINT_URL = os.getenv('DO_SPACE_ENDPOINT_URL', 'https://nyc3.digitaloceanspaces.com')  # Ajusta la región si es necesario
AWS_QUERYSTRING_AUTH = False

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # Control de caché para navegadores
    'ACL': 'public-read',
}

# ----------------------------
# Almacenamiento personalizado para el programa de Gym
# ----------------------------
class GymStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    custom_domain = f"{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com"
    location = 'storage_Gym'  # Aquí se define la carpeta "storage_Gym"
    default_acl = 'public-read'
    file_overwrite = False  # Evita sobrescribir archivos con el mismo nombre

# ----------------------------
# Opcional: configuración de MEDIA y STATIC si lo necesitas en otros contextos
# ----------------------------
# Para archivos subidos (media)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com/media/"

# Para archivos estáticos (si tienes un backend personalizado para estáticos)
AWS_STATIC_LOCATION = 'static'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configuración de PWA
PWA_APP_NAME = 'GymWorl'
PWA_APP_DESCRIPTION = "Tu entrenador personal"
PWA_APP_THEME_COLOR = '#007bff'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/pwa/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/gym_pwa/icons/icon-128x128.png',
        'sizes': '128x128'
    },
    {
        'src': '/static/gym_pwa/icons/icon-512x512.png',
        'sizes': '512x512'
    }
]
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'gym_pwa/static/gym_pwa/js', 'serviceworker.js')
