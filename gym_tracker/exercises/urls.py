from django.urls import path
from .views import (
    ExerciseListView, 
    ExerciseDetailView, 
    exercise_create,
    export_exercises_template,
    import_exercises,
    export_exercises
)

app_name = 'exercises'

# URLs para la API REST
api_patterns = [
    path('', ExerciseListView.as_view(), name='api-exercise-list'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='api-exercise-detail'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise-list'),
    path('create/', exercise_create, name='exercise-create'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('export-template/', export_exercises_template, name='export-template'),
    path('export/', export_exercises, name='export-exercises'),
    path('import/', import_exercises, name='import-exercises'),
]

# URLs específicas para cada tipo de ruta
web_urlpatterns = urlpatterns  # Para /web/exercises/