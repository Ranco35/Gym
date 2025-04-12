from django.urls import path
from .views import (
    # API
    WorkoutSessionListCreateView, 
    WorkoutSessionDetailView,
    WorkoutSetListCreateView, 
    WorkoutSetDetailView,
    
    # Web
    workout_session_list, 
    workout_session_detail, 
    workout_session_create, 
    workout_session_edit, 
    workout_session_delete,
    workout_set_create, 
    workout_set_edit, 
    workout_set_delete
)

app_name = 'tracking'

urlpatterns = [
    # API
    path('api/sessions/', WorkoutSessionListCreateView.as_view(), name='session-list-create-api'),
    path('api/sessions/<int:pk>/', WorkoutSessionDetailView.as_view(), name='session-detail-api'),
    path('api/sets/', WorkoutSetListCreateView.as_view(), name='set-list-create-api'),
    path('api/sets/<int:pk>/', WorkoutSetDetailView.as_view(), name='set-detail-api'),
    
    # Web
    path('', workout_session_list, name='session-list'),
    path('<int:pk>/', workout_session_detail, name='session-detail'),
    path('create/', workout_session_create, name='session-create'),
    path('<int:pk>/edit/', workout_session_edit, name='session-edit'),
    path('<int:pk>/delete/', workout_session_delete, name='session-delete'),
    path('<int:session_id>/sets/create/', workout_set_create, name='set-create'),
    path('sets/<int:pk>/edit/', workout_set_edit, name='set-edit'),
    path('sets/<int:pk>/delete/', workout_set_delete, name='set-delete'),
] 