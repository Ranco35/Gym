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
        fields = [
            'id', 'name', 'slug', 'description', 'muscle_group', 
            'primary_muscles', 'secondary_muscles', 'difficulty', 
            'equipment', 'tips', 'video_url', 'image', 'images',
            'created_at', 'updated_at'
        ]
    
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
        fields = [
            'name', 'slug', 'description', 'muscle_group', 'difficulty',
            'primary_muscles', 'secondary_muscles', 'equipment', 'tips',
            'video_url'
        ]
        
    def validate_muscle_group(self, value):
        """
        Validar que el grupo muscular sea uno de los permitidos
        """
        valid_groups = dict(Exercise.MUSCLE_GROUPS).keys()
        if value not in valid_groups:
            raise serializers.ValidationError(
                f"Grupo muscular no válido. Debe ser uno de: {', '.join(valid_groups)}"
            )
        return value
    
    def validate_difficulty(self, value):
        """
        Validar que la dificultad sea una de las permitidas
        """
        valid_difficulties = dict(Exercise.DIFFICULTY_LEVELS).keys()
        if value not in valid_difficulties:
            raise serializers.ValidationError(
                f"Dificultad no válida. Debe ser una de: {', '.join(valid_difficulties)}"
            )
        return value
    
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