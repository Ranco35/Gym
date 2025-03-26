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
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '134.199.224.217', '0.0.0.0'])

# Configuración de CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://134.199.224.217:8000',
]

# Configuración estándar de Django para CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = not DEBUG
# Deshabilitar la protección CSRF para desarrollo
CSRF_USE_SESSIONS = False 
CSRF_COOKIE_SAMESITE = None
CSRF_FAILURE_VIEW = 'gym_tracker.views.csrf_failure'

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Debe estar antes de django.contrib.admin
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
]

# Middleware - Deshabilitamos CSRF temporalmente en desarrollo
if DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        # 'django.middleware.csrf.CsrfViewMiddleware',  # Comentado temporalmente para desarrollo
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
        'NAME': 'gym_db',
        'USER': 'eduardo',
        'PASSWORD': '123llifen789.',
        'HOST': 'localhost',
        'PORT': '5432',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
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

# Configuración de autenticación estándar de Django
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# Configuración de Jazzmin
JAZZMIN_SETTINGS = {
    # título de la página de administración
    "site_title": "Gym Tracker Admin",
    "site_header": "Gym Tracker",
    "site_brand": "Gym Tracker",
    "welcome_sign": "Bienvenido al Panel de Administración",
    "copyright": "Gym Tracker",
    
    # Personalización del tema
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    
    # Personalización de colores
    "custom_css": None,
    "custom_js": None,
    
    # Iconos para los modelos
    "icons": {
        "users.User": "fas fa-users",
        "auth.Group": "fas fa-users-cog",
        "users.TrainerUser": "fas fa-dumbbell",
    },
    
    # Configuración del menú
    "order_with_respect_to": ["users", "auth"],
    
    # Elementos del menú superior
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
    ],
    
    # Personalización de la lista de usuarios
    "show_ui_builder": True,
    
    # Personalización del dashboard
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
