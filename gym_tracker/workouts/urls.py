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
    edit_routine,
    delete_routine,
    view_assigned_routine
)

app_name = 'workouts'

# URLs para la API REST
api_patterns = [
    path('api/workouts/', WorkoutListCreateView.as_view(), name='workout-list-create-api'),
    path('api/workouts/<int:pk>/', WorkoutDetailView.as_view(), name='workout-detail-api'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', routine_list, name='workout-list'),  # Vista principal de rutinas
    path('new/', routine_selection, name='workout-new'),  # Crear nueva rutina
    path('<int:pk>/', routine_detail, name='workout-detail'),  # Ver detalle de rutina
    path('<int:pk>/edit/', edit_routine, name='workout-edit'),  # Editar rutina existente
    path('<int:pk>/delete/', delete_routine, name='workout-delete'),  # Eliminar rutina (solo admin/superuser)
    path('<int:routine_pk>/day/<int:day_pk>/', routine_day_detail, name='workout-day-detail'),
    path('exercise/<int:exercise_pk>/delete/', delete_routine_exercise, name='delete-routine-exercise'),
    path('day/<int:day_pk>/update-focus/', update_routine_focus, name='update-routine-focus'),
    path('rutina-asignada/', view_assigned_routine, name='view-assigned-routine'),
]
