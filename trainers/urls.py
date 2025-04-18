from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    # Dashboard del entrenador
    path('dashboard/', views.trainer_dashboard, name='dashboard'),
    
    # Gestión de estudiantes
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:student_id>/trainings/', views.get_student_trainings, name='get_student_trainings'),
    path('users/search/', views.search_users, name='search_users'),
    
    # Gestión de rutinas de estudiantes
    path('students/<int:student_id>/trainings/list/', views.student_trainings, name='student_trainings'),
    path('students/<int:student_id>/trainings/<int:training_id>/', views.training_detail, name='training_detail'),
    path('students/<int:student_id>/trainings/create/', views.create_training, name='create_training'),
    path('students/<int:student_id>/trainings/<int:training_id>/edit/', views.edit_training, name='edit_training'),
    path('students/<int:student_id>/trainings/<int:training_id>/copy/', views.copy_training, name='copy_training'),
    path('students/<int:student_id>/trainings/<int:training_id>/delete/', views.delete_training, name='delete_training'),
    
    # Sesiones de entrenamiento en vivo
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/<int:session_id>/', views.live_session, name='live_session'),
    path('student-sessions/<int:session_id>/', views.student_live_session, name='student_live_session'),
    path('sessions/start/<int:student_id>/', views.start_live_session, name='start_session'),
    path('students/<int:student_id>/select-routine/<int:session_id>/', views.select_session_routine, name='select_session_routine'),
    path('routine/<int:routine_id>/select-day/<int:session_id>/<int:student_id>/', views.select_routine_day, name='select_routine_day'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('save-set/', views.save_live_set, name='save_live_set'),
    path('end-session/<int:session_id>/', views.end_session, name='end_session'),
    
    # Añadir la nueva URL
    path('training/<int:training_id>/use/<int:session_id>/<int:student_id>/', views.use_training_routine, name='use_training_routine'),

    # Nueva ruta para editar un set individual
    path('set/<int:set_id>/edit/', views.edit_trainer_set, name='edit_trainer_set'),
] 