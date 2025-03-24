from rest_framework import serializers
from .models import Workout, WeeklyRoutine, RoutineDay, RoutineExercise
from gym_tracker.exercises.serializers import ExerciseSerializer
from gym_tracker.exercises.models import Exercise

class WorkoutSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Workout.
    """
    class Meta:
        model = Workout
        fields = ['id', 'name', 'date', 'user']
        read_only_fields = ['user']

class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise_detail = ExerciseSerializer(source='exercise', read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )
    
    class Meta:
        model = RoutineExercise
        fields = ['id', 'exercise_detail', 'exercise_id', 'sets', 'reps', 'weight', 'rest_time', 'order', 'notes']

class RoutineDaySerializer(serializers.ModelSerializer):
    exercises = RoutineExerciseSerializer(many=True, read_only=True)
    
    class Meta:
        model = RoutineDay
        fields = ['id', 'day_of_week', 'focus', 'exercises']

class RoutineDayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineDay
        fields = ['id', 'day_of_week', 'focus']

class WeeklyRoutineSerializer(serializers.ModelSerializer):
    days = RoutineDaySerializer(many=True, read_only=True)
    
    class Meta:
        model = WeeklyRoutine
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'days']
        read_only_fields = ['user', 'created_at', 'updated_at']

class WeeklyRoutineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyRoutine
        fields = ['id', 'name', 'description']