from django.http import HttpResponse
from django.views import View
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

class GenerateImagesView(View):
    def get(self, request):
        # Crear directorios si no existen
        icons_dir = os.path.join(settings.STATIC_ROOT, 'gym_pwa', 'icons')
        img_dir = os.path.join(settings.STATIC_ROOT, 'gym_pwa', 'img')
        
        os.makedirs(icons_dir, exist_ok=True)
        os.makedirs(img_dir, exist_ok=True)

        # Generar iconos
        self.generate_icon('icon-192x192.png', 192, icons_dir)
        self.generate_icon('icon-512x512.png', 512, icons_dir)
        self.generate_default_exercise(icons_dir)
        self.generate_no_image(img_dir)

        return HttpResponse("Imágenes generadas correctamente")

    def generate_icon(self, filename, size, directory):
        # Crear una imagen con fondo azul
        img = Image.new('RGB', (size, size), color='#007bff')
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar una fuente, si no está disponible usar la predeterminada
        try:
            font = ImageFont.truetype("arial.ttf", size//4)
        except:
            font = ImageFont.load_default()

        # Dibujar texto
        text = "GYM"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='white')
        
        # Guardar la imagen
        img.save(os.path.join(directory, filename))

    def generate_default_exercise(self, directory):
        # Crear una imagen para ejercicio por defecto
        size = 200
        img = Image.new('RGB', (size, size), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", size//4)
        except:
            font = ImageFont.load_default()

        # Dibujar un ícono simple de ejercicio
        draw.rectangle([20, 20, size-20, size-20], outline='#007bff', width=3)
        text = "GYM"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='#007bff')
        
        img.save(os.path.join(directory, 'default-exercise.png'))

    def generate_no_image(self, directory):
        # Crear una imagen por defecto
        size = 300
        img = Image.new('RGB', (size, size), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", size//6)
        except:
            font = ImageFont.load_default()

        # Dibujar un marco y texto
        draw.rectangle([10, 10, size-10, size-10], outline='#6c757d', width=2)
        text = "No Image"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='#6c757d')
        
        img.save(os.path.join(directory, 'no-image.png')) 