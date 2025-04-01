from django.urls import path, include
from . import views

app_name = 'gym_pwa'

urlpatterns = [
    # Vistas principales de la PWA
    path('', views.pwa_home, name='home'),
    path('workouts/', views.pwa_workouts, name='workouts'),
    path('workout/<int:workout_id>/', views.pwa_workout_player, name='workout_player'),
    path('workout_detail/<int:workout_id>/', views.pwa_workout_detail, name='workout_detail'),
    path('exercises/', views.pwa_exercises, name='exercises'),
    path('profile/', views.pwa_profile, name='profile'),
    path('profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),
    
    # Selección y rutinas
    path('select-routine/', views.pwa_select_routine, name='select_routine'),
    path('routine/<int:routine_id>/', views.pwa_routine_detail, name='routine_detail'),
    path('routine/<int:routine_id>/start/', views.pwa_routine_start, name='routine_start'),
    
    # Utilidades
    path('admin/convert-images/', views.convert_images_to_webp, name='convert_images'),
    
    # API para la PWA
    path('api/', include('gym_pwa.api.urls')),
    
    # Vista para verificar autenticación
    path('auth-status/', views.auth_status, name='auth_status'),
    
    # Service Worker y Offline
    path('sw.js', views.service_worker, name='service_worker'),
    path('offline/', views.offline, name='offline'),
] 