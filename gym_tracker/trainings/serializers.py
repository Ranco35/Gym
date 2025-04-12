from rest_framework import serializers
from .models import Training, Set
from datetime import datetime
from gym_tracker.exercises.serializers import ExerciseSerializer
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = ['id', 'set_number', 'weight', 'reps', 'completed']

class TrainingSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Training.
    """
    exercise_details = ExerciseSerializer(source='exercise', read_only=True)
    training_sets = SetSerializer(many=True, read_only=True)
    creator = UserSerializer(source='user', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            'id', 'user', 'creator', 'exercise', 'exercise_details', 'total_sets', 'reps', 'weight', 
            'date', 'day_of_week', 'rest_time', 'intensity', 'notes', 'completed',
            'duration', 'calories_burned', 'is_recurring', 'recurring_days', 'training_sets',
            'created_at', 'updated_at', 'created_at_formatted', 'updated_at_formatted'
        ]
        read_only_fields = ['user', 'creator', 'created_at', 'updated_at']
        
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
        
    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime("%d/%m/%Y %H:%M")
        
    def create(self, validated_data):
        # Asignar el día de la semana basado en la fecha
        date = validated_data.get('date')
        if date:
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            day_of_week = day_names[date.weekday()]
            validated_data['day_of_week'] = day_of_week
        
        return super().create(validated_data)