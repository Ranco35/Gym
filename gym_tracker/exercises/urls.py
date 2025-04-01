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
    exercise_delete,
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
    path('export/', export_exercises, name='api-export-exercises'),
    path('export/template/', export_exercises_template, name='api-export-template'),
    path('import/', import_exercises, name='api-import-exercises'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='api-exercise-detail'),
    path('<slug:slug>/', ExerciseDetailView.as_view(), name='api-exercise-detail-slug'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', exercise_list, name='exercise-list'),
    path('create/', exercise_create, name='exercise-create'),
    path('export-template/', export_exercises_template, name='export-template'),
    path('export/', export_exercises, name='export-exercises'),
    path('export-json/', export_exercises, name='export-exercises-json'),
    path('import/', import_exercises, name='import-exercises'),
    path('<int:pk>/edit/', exercise_edit, name='exercise-edit'),
    path('<slug:slug>/edit/', exercise_edit, name='exercise-edit-slug'),
    path('<int:pk>/delete/', exercise_delete, name='exercise-delete'),
    path('<slug:slug>/delete/', exercise_delete, name='exercise-delete-slug'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('<str:slug>/', ExerciseDetailView.as_view(), name='exercise-detail-slug'),
    
    # URLs para gestión de categorías
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
]

# URLs específicas para cada tipo de ruta
web_urlpatterns = urlpatterns  # Para /web/exercises/