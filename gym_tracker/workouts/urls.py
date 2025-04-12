from django.urls import path
from .views import (
    # API
    WorkoutListCreateView, 
    WorkoutDetailView,
    
    # Routines
    routine_selection, 
    routine_list, 
    routine_detail,
    
    # Routine Days
    routine_day_detail, 
    delete_routine_exercise, 
    update_routine_focus,
    
    # Routine Management
    edit_routine, 
    delete_routine, 
    view_assigned_routine
)

app_name = 'workouts'

# Patrones de URL para la API
api_patterns = [
    path('workouts/', WorkoutListCreateView.as_view(), name='workout-list-create-api'),
    path('workouts/<int:pk>/', WorkoutDetailView.as_view(), name='workout-detail-api'),
]

# Patrones de URL para la interfaz web
web_urlpatterns = [
    path('', routine_selection, name='routine-selection'),
    path('routines/', routine_list, name='routine-list'),
    path('routines/<int:pk>/', routine_detail, name='routine-detail'),
    path('routines/<int:routine_id>/day/<int:day_id>/', routine_day_detail, name='routine-day-detail'),
    path('routines/<int:routine_id>/day/<int:day_id>/exercise/<int:exercise_id>/delete/', delete_routine_exercise, name='delete-routine-exercise'),
    path('routines/<int:routine_id>/day/<int:day_id>/update-focus/', update_routine_focus, name='update-routine-focus'),
    path('routines/<int:pk>/edit/', edit_routine, name='routine-edit'),
    path('routines/<int:pk>/delete/', delete_routine, name='routine-delete'),
    path('assigned/<int:pk>/', view_assigned_routine, name='view-assigned-routine'),
    path('routines/create/', routine_selection, name='routine-create'),
]

# Mantener urlpatterns para compatibilidad
urlpatterns = web_urlpatterns + api_patterns
