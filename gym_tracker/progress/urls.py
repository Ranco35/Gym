from django.urls import path
from .views import (
    # API
    ProgressListCreateView, 
    ProgressDetailView,
    
    # Web
    progress_list, 
    progress_detail, 
    progress_create, 
    progress_edit, 
    progress_delete
)

app_name = 'progress'

urlpatterns = [
    # API
    path('api/progress/', ProgressListCreateView.as_view(), name='progress-list-create-api'),
    path('api/progress/<int:pk>/', ProgressDetailView.as_view(), name='progress-detail-api'),
    
    # Web
    path('', progress_list, name='progress-list'),
    path('<int:pk>/', progress_detail, name='progress-detail'),
    path('create/', progress_create, name='progress-create'),
    path('<int:pk>/edit/', progress_edit, name='progress-edit'),
    path('<int:pk>/delete/', progress_delete, name='progress-delete'),
] 