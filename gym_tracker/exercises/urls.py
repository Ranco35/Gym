from django.urls import path
from .views import (
    # API
    ExerciseListView, 
    ExerciseDetailView,
    
    # Web
    exercise_list, 
    exercise_detail, 
    exercise_create, 
    exercise_edit, 
    exercise_delete,
    export_exercises,
    import_exercises
)

app_name = 'exercises'

# Patrones de URL para la API
api_patterns = [
    path('', ExerciseListView.as_view(), name='exercise-list-create-api'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail-api'),
]

# Patrones de URL para la interfaz web
web_urlpatterns = [
    path('', exercise_list, name='exercise-list'),
    path('create/', exercise_create, name='exercise-create'),
    path('export/', export_exercises, name='export-exercises'),
    path('export-json/', export_exercises, name='export-exercises-json'),
    path('import/', import_exercises, name='import-exercises'),
    path('<int:pk>/edit/', exercise_edit, name='exercise-edit'),
    path('<int:pk>/delete/', exercise_delete, name='exercise-delete'),
    path('<int:pk>/', exercise_detail, name='exercise-detail'),
    path('<slug:slug>/edit/', exercise_edit, name='exercise-edit-slug'),
    path('<slug:slug>/delete/', exercise_delete, name='exercise-delete-slug'),
    path('<str:slug>/', exercise_detail, name='exercise-detail-slug'),
]

# Mantener urlpatterns para compatibilidad
urlpatterns = web_urlpatterns