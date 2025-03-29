from django.urls import path
from .views import (
    ExerciseListView, 
    ExerciseDetailView, 
    exercise_create,
    exercise_edit,
    export_exercises_template,
    import_exercises,
    export_exercises,
    exercise_list,
    # Nuevas vistas para categorías
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView
)

app_name = 'exercises'

# URLs para la API REST
api_patterns = [
    path('', ExerciseListView.as_view(), name='api-exercise-list'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='api-exercise-detail'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', exercise_list, name='exercise-list'),
    path('create/', exercise_create, name='exercise-create'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('<int:pk>/edit/', exercise_edit, name='exercise-edit'),
    path('export-template/', export_exercises_template, name='export-template'),
    path('export/', export_exercises, name='export-exercises'),
    path('import/', import_exercises, name='import-exercises'),
    
    # URLs para gestión de categorías
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
]

# URLs específicas para cada tipo de ruta
web_urlpatterns = urlpatterns  # Para /web/exercises/