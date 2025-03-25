from django.urls import path
from .views import (
    TrainingListCreateView, 
    TrainingDetailView, 
    delete_training, 
    toggle_complete,
    get_routine_days,
    create_training_from_routine,
    execute_training
)

app_name = 'trainings'

# URLs para la API REST
api_patterns = [
    path('', TrainingListCreateView.as_view(), name='api-training-list'),
    path('<int:pk>/', TrainingDetailView.as_view(), name='api-training-detail'),
]

# URLs para la interfaz web
urlpatterns = [
    path('', TrainingListCreateView.as_view(), name='training-list-create'),
    path('<int:pk>/', TrainingDetailView.as_view(), name='training-detail'),
    path('<int:pk>/delete/', delete_training, name='training-delete'),
    path('<int:pk>/toggle-complete/', toggle_complete, name='training-toggle-complete'),
    # Nuevas URLs para entrenamientos basados en rutinas
    path('routine/<int:routine_id>/days/', get_routine_days, name='get-routine-days'),
    path('from-routine/', create_training_from_routine, name='training-from-routine'),
    path('execute/<int:routine_id>/<int:day_id>/', execute_training, name='execute-training'),
]