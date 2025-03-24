from django.urls import path
from .views import ExerciseListView, ExerciseDetailView, exercise_create

app_name = 'exercises'

# URLs para la API REST
api_patterns = [
    path('', ExerciseListView.as_view(), name='api-exercise-list'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='api-exercise-detail'),
]

# URLs para la interfaz web
web_patterns = [
    path('', ExerciseListView.as_view(), name='exercise-list'),
    path('create/', exercise_create, name='exercise-create'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
]

# URLs específicas para cada tipo de ruta
urlpatterns = web_patterns  # Para /exercises/
web_urlpatterns = web_patterns  # Para /web/exercises/