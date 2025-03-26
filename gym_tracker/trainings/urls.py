from django.urls import path
from .views import (
    TrainingListCreateView, 
    TrainingDetailView, 
    delete_training, 
    toggle_complete,
    get_routine_days,
    create_training_from_routine,
    execute_training,
    training_session_view,
    save_set,
    save_set_simple,
    get_completed_sets
)

app_name = 'trainings'

urlpatterns = [
    # URLs principales
    path('', TrainingListCreateView.as_view(), name='training-list-create'),
    path('<int:pk>/', TrainingDetailView.as_view(), name='training-detail'),
    path('<int:pk>/delete/', delete_training, name='training-delete'),
    path('<int:pk>/toggle-complete/', toggle_complete, name='training-toggle-complete'),
    
    # URLs de sesión de entrenamiento
    path('session/<int:training_id>/', training_session_view, name='session'),
    path('session/save-set/', save_set, name='save-set'),
    path('session/save-set-simple/', save_set_simple, name='save-set-simple'),
    path('session/<int:training_id>/completed-sets/', get_completed_sets, name='get-completed-sets'),
    
    # URLs de rutinas
    path('routine/<int:routine_id>/days/', get_routine_days, name='get-routine-days'),
    path('from-routine/', create_training_from_routine, name='training-from-routine'),
    path('execute/<int:routine_id>/<int:day_id>/', execute_training, name='execute-training'),
]