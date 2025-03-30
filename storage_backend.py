from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class GymStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = f"{settings.AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com"
    location = 'storage_Gym'
    default_acl = 'public-read'
    file_overwrite = False  # Evita sobrescribir archivos con el mismo nombre 