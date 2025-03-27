from django.urls import path
from . import views

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
    path('training/create-from-routine/', views.create_training_from_routine, name='create-training-from-routine'),
    path('routine/<int:routine_id>/days/', views.get_routine_days, name='get-routine-days'),
    
    # Ejecución de entrenamientos
    path('execute/<int:routine_id>/day/<int:day_id>/', views.execute_training, name='execute-training'),
    
    # Sesiones de entrenamiento
    path('session/<int:training_id>/', views.training_session_view, name='session'),
    path('session/<int:training_id>/sets/', views.save_set, name='save-set'),
    path('session/<int:training_id>/sets/completed/', views.get_completed_sets, name='get-completed-sets'),
    
    # Estadísticas
    path('stats/', views.training_stats, name='training_stats'),
]