# Configuración de DigitalOcean Spaces
AWS_ACCESS_KEY_ID = 'DO00ELANT2VXA3J9G3Q9'
AWS_SECRET_ACCESS_KEY = 'ed2stFqA+Oj0Avrpow2/Z1obmzjcx8NG9Iooh7k6Z/o'
AWS_STORAGE_BUCKET_NAME = 'lifen-cl-system'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_ENDPOINT_URL = 'https://nyc3.digitaloceanspaces.com'
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
    'trainers',
    'gym_tracker',
    'stats',
]

# Channels configuration
ASGI_APPLICATION = 'gymworl.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
} 