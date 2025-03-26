from rest_framework import serializers
from .models import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Exercise.
    """
    class Meta:
        model = Exercise
        fields = '__all__'