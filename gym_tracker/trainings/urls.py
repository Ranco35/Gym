from django.urls import path
from .views import (
    TrainingDetailView,
    TrainingListView,
    RoutineDatesView,
    RoutineDateExercisesView,
    delete_training, 
    toggle_complete, 
    get_routine_days, 
    create_training_from_routine,
    execute_training, 
    training_session_view, 
    save_set, 
    save_set_simple, 
    get_completed_sets,
    delete_set, 
    edit_set,
    training_stats, 
    dashboard,
    profile_edit,
    assigned_training_detail, 
    create_training_session, 
    edit_user_training,
)
from .views.training_history import training_history

app_name = 'trainings'

# Patrones de URL para la API
api_patterns = [
    path('api/trainings/', TrainingListView.as_view(), name='training-list-create'),
    path('api/trainings/<int:pk>/', TrainingDetailView.as_view(), name='training-detail-api'),
    path('api/toggle-complete/<int:pk>/', toggle_complete, name='toggle-complete-api'),
    path('api/routine-days/<int:routine_id>/', get_routine_days, name='get-routine-days-api'),
    path('api/save-set/', save_set, name='save-set-api'),
    path('api/save-set-simple/', save_set_simple, name='save-set-simple-api'),
    path('api/completed-sets/<int:training_id>/', get_completed_sets, name='get-completed-sets-api'),
    path('api/create-session/', create_training_session, name='create-session-api'),
]

# Patrones de URL para la interfaz web
web_urlpatterns = [
    # Dashboard y Perfil
    path('', dashboard, name='dashboard'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    
    # Rutinas
    path('routines/', TrainingListView.as_view(), name='routine-list'),
    path('routines/<str:routine_name>/', RoutineDatesView.as_view(), name='routine-dates'),
    path('routines/<str:routine_name>/<str:date>/', RoutineDateExercisesView.as_view(), name='routine-exercises'),
    
    # Historial
    path('history/', training_history, name='training-history'),
    
    # Entrenamientos
    path('trainings/<int:pk>/delete/', delete_training, name='training-delete'),
    path('trainings/<int:pk>/edit/', edit_user_training, name='training-edit'),
    path('trainings/create/', create_training_from_routine, name='training-create-from-routine'),
    
    # Series
    path('sets/<int:set_id>/edit/', edit_set, name='set-edit'),
    path('sets/<int:set_id>/delete/', delete_set, name='set-delete'),
    
    # Ejecución y Sesiones
    path('execute/<int:routine_id>/day/<int:day_id>/', execute_training, name='execute-training'),
    path('session/<int:training_id>/', training_session_view, name='session'),
    path('session/<int:training_id>/sets/', save_set, name='save-set'),
    path('session/<int:training_id>/sets/completed/', get_completed_sets, name='get-completed-sets'),
    
    # Estadísticas
    path('stats/', training_stats, name='training-stats'),
    
    # Asignaciones
    path('assigned/<int:training_id>/', assigned_training_detail, name='assigned-training-detail'),
]

# Mantener urlpatterns para compatibilidad
urlpatterns = web_urlpatterns + api_patterns