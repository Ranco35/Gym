from django.urls import path
from . import views

app_name = 'gym_pwa_api'

urlpatterns = [
    # Endpoints para obtener datos
    path('workouts/', views.get_user_workouts, name='workouts'),
    path('workout/<int:workout_id>/', views.get_workout_detail, name='workout_detail'),
    
    # Endpoints para sincronización
    path('sync/completed-set/', views.sync_completed_set, name='sync_completed_set'),
    path('sync/workout-progress/', views.sync_workout_progress, name='sync_workout_progress'),
    
    # Endpoints para datos específicos
    path('routine/<int:routine_id>/days/', views.get_routine_days, name='get_routine_days'),
] 