from django.urls import path
from .views import (
    WorkoutListCreateView, 
    WorkoutDetailView,
    routine_selection,
    routine_list,
    routine_detail,
    routine_day_detail,
    delete_routine_exercise,
    update_routine_focus,
    edit_routine
)

app_name = 'workouts'

# URLs para la API REST
api_patterns = [
    path('', WorkoutListCreateView.as_view(), name='api-workout-list-create'),
    path('<int:pk>/', WorkoutDetailView.as_view(), name='api-workout-detail'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', routine_list, name='workout-list'),  # Vista principal de rutinas
    path('new/', routine_selection, name='workout-new'),  # Crear nueva rutina
    path('<int:pk>/', routine_detail, name='workout-detail'),  # Ver detalle de rutina
    path('<int:pk>/edit/', edit_routine, name='workout-edit'),  # Editar rutina existente
    path('<int:routine_pk>/day/<int:day_pk>/', routine_day_detail, name='workout-day-detail'),
    path('exercise/<int:exercise_pk>/delete/', delete_routine_exercise, name='delete-routine-exercise'),
    path('day/<int:day_pk>/update-focus/', update_routine_focus, name='update-routine-focus'),
]
