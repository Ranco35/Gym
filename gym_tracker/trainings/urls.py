from django.urls import path
from . import views
from .views import TrainingListCreateView, TrainingDetailView, save_set_simple, edit_user_training, delete_set, edit_set # Asegurarse de importar las vistas

app_name = 'trainings'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Perfil de usuario
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Ejercicios (redirección a la app de exercises)
    path('exercises/', views.exercise_list, name='exercise_list'),
    
    # Entrenamientos
    path('training/', views.training_list, name='training-list-create'),
    path('training/<int:pk>/', views.training_list, name='training-detail'),
    path('training/<int:pk>/delete/', views.delete_training, name='delete-training'),
    path('training/<int:pk>/edit/', views.edit_user_training, name='edit-training'),
    path('training/create-from-routine/', views.create_training_from_routine, name='create-training-from-routine'),
    path('routine/<int:routine_id>/days/', views.get_routine_days, name='get-routine-days'),
    
    # Series
    path('set/<int:set_id>/edit/', views.edit_set, name='edit-set'),
    path('set/<int:set_id>/delete/', views.delete_set, name='delete-set'),
    
    # Ejecución de entrenamientos
    path('execute/<int:routine_id>/day/<int:day_id>/', views.execute_training, name='execute-training'),
    
    # Sesiones de entrenamiento
    path('session/<int:training_id>/', views.training_session_view, name='session'),
    path('session/<int:training_id>/sets/', views.save_set, name='save-set'),
    path('session/<int:training_id>/sets/completed/', views.get_completed_sets, name='get-completed-sets'),
    
    # Estadísticas
    path('stats/', views.training_stats, name='training_stats'),
    
    path('api/trainings/', TrainingListCreateView.as_view(), name='training-list-create'),
    path('api/trainings/<int:pk>/', TrainingDetailView.as_view(), name='training-detail'),
    path('api/toggle_complete/<int:pk>/', views.toggle_complete, name='toggle-complete'),
    path('api/get_routine_days/<int:routine_id>/', views.get_routine_days, name='get-routine-days'),
    path('create_from_routine/', views.create_training_from_routine, name='create-from-routine'),
    path('execute/<int:routine_id>/<int:day_id>/', views.execute_training, name='execute-training'),
    path('session/<int:training_id>/', views.training_session_view, name='training-session'),
    path('api/save_set/', views.save_set, name='save-set'), # Para Sets del modelo Training
    path('api/save_set_simple/', save_set_simple, name='save_set_simple'), # Para guardar sets rápidos
    path('api/get_completed_sets/<int:training_id>/', views.get_completed_sets, name='get-completed-sets'),
    path('stats/', views.training_stats, name='training-stats'),
    path('routines/', views.routine_list, name='routine_list'),
    path('list/', views.training_list, name='training_list'), # Vista para listar entrenamientos completados
    path('set/<int:set_id>/delete/', delete_set, name='delete_set'),
    path('api/create_training_session/', views.create_training_session, name='create_training_session'),
    
    # Nueva ruta para ver detalles de rutina asignada por entrenador
    path('assigned-trainings/<int:training_id>/', views.assigned_training_detail, name='assigned_training_detail'),
]