from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import uuid

def convert_to_webp(image_field):
    """
    Convierte una imagen a formato WebP.
    
    Args:
        image_field: ImageField de Django
        
    Returns:
        La imagen convertida a WebP
    """
    # Si la imagen ya está en formato WebP, no hacemos nada
    if image_field.name.endswith('.webp'):
        return image_field
    
    # Abrimos la imagen con PIL
    img = Image.open(image_field)
    
    # Determinamos el formato a convertir
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Generamos un nombre único para el archivo
    name = str(uuid.uuid4())
    webp_name = f"{name}.webp"
    
    # Creamos un buffer para guardar la imagen WebP
    buffer = BytesIO()
    img.save(buffer, 'WEBP', quality=80)
    buffer.seek(0)
    
    # Reemplazamos la imagen original con la versión WebP
    webp_file = ContentFile(buffer.read(), name=webp_name)
    
    return webp_file

def convert_all_images_to_webp(model, image_field_name):
    """
    Convierte todas las imágenes de un modelo a formato WebP.
    
    Args:
        model: Modelo de Django
        image_field_name: Nombre del campo ImageField
    """
    instances = model.objects.all()
    converted = 0
    
    for instance in instances:
        image_field = getattr(instance, image_field_name)
        
        # Si hay imagen y no es WebP
        if image_field and not image_field.name.endswith('.webp'):
            try:
                # Guardamos la ruta original para eliminar después
                original_path = image_field.path
                
                # Convertimos a WebP
                webp_image = convert_to_webp(image_field)
                image_field.save(webp_image.name, webp_image, save=False)
                
                # Guardamos la instancia
                instance.save(update_fields=[image_field_name])
                converted += 1
                
                # Eliminamos el archivo original
                if os.path.exists(original_path):
                    os.remove(original_path)
                    
            except Exception as e:
                print(f"Error al convertir imagen: {e}")
    
    return converted 