from rest_framework import serializers
from .models import Exercise, ExerciseImage

class ExerciseImageSerializer(serializers.ModelSerializer):
    """
    Serializador para imágenes de ejercicios
    """
    class Meta:
        model = ExerciseImage
        fields = ['image', 'caption', 'order']

class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Exercise.
    """
    images = ExerciseImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'slug', 'description', 'muscle_group', 
                 'primary_muscles', 'secondary_muscles', 'difficulty', 
                 'equipment', 'tips', 'image', 'video_url', 'images']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

class ExerciseExportSerializer(serializers.ModelSerializer):
    """
    Serializador para exportar ejercicios
    """
    # Personalizar representación de la imagen principal
    image = serializers.SerializerMethodField()
    # Personalizar representación de imágenes adicionales
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        exclude = ['created_by']
    
    def get_image(self, obj):
        """Devolver URL de la imagen si existe, o None"""
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return None
        return None
    
    def get_images(self, obj):
        """Simplificar la representación de imágenes adicionales"""
        images = []
        try:
            for img in obj.images.all():
                images.append({
                    'url': img.image.url,
                    'caption': img.caption,
                    'order': img.order
                })
        except Exception:
            pass
        return images

class ExerciseImportSerializer(serializers.ModelSerializer):
    """
    Serializador para importar ejercicios
    """
    class Meta:
        model = Exercise
        exclude = ['id', 'created_by', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # Verificar si ya existe un ejercicio con este slug
        slug = validated_data.get('slug')
        if slug and Exercise.objects.filter(slug=slug).exists():
            # Actualizar el ejercicio existente
            exercise = Exercise.objects.get(slug=slug)
            for attr, value in validated_data.items():
                setattr(exercise, attr, value)
            exercise.save()
            return exercise
        return super().create(validated_data)