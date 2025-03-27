from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('exercise-progress/', views.exercise_progress, name='exercise-progress'),
    path('volume-analysis/', views.volume_analysis, name='volume-analysis'),
    path('personal-records/', views.personal_records, name='personal-records'),
    path('training-frequency/', views.training_frequency, name='training-frequency'),
] 