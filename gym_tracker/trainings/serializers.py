from rest_framework import serializers
from .models import Training
from datetime import datetime
from gym_tracker.exercises.serializers import ExerciseSerializer

class TrainingSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Training.
    """
    exercise_details = ExerciseSerializer(source='exercise', read_only=True)
    
    class Meta:
        model = Training
        fields = [
            'id', 'user', 'exercise', 'exercise_details', 'sets', 'reps', 'weight', 
            'date', 'day_of_week', 'rest_time', 'intensity', 'notes', 'completed',
            'duration', 'calories_burned', 'is_recurring', 'recurring_days'
        ]
        read_only_fields = ['user']
        
    def create(self, validated_data):
        # Asignar el día de la semana basado en la fecha
        date = validated_data.get('date')
        if date:
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            day_of_week = day_names[date.weekday()]
            validated_data['day_of_week'] = day_of_week
        
        return super().create(validated_data)