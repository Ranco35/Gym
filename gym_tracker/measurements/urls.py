from django.urls import path
from .views import (
    # API
    MeasurementListCreateView, 
    MeasurementDetailView,
    
    # Web
    measurement_list, 
    measurement_detail, 
    measurement_create, 
    measurement_edit, 
    measurement_delete
)

app_name = 'measurements'

urlpatterns = [
    # API
    path('api/measurements/', MeasurementListCreateView.as_view(), name='measurement-list-create-api'),
    path('api/measurements/<int:pk>/', MeasurementDetailView.as_view(), name='measurement-detail-api'),
    
    # Web
    path('', measurement_list, name='measurement-list'),
    path('<int:pk>/', measurement_detail, name='measurement-detail'),
    path('create/', measurement_create, name='measurement-create'),
    path('<int:pk>/edit/', measurement_edit, name='measurement-edit'),
    path('<int:pk>/delete/', measurement_delete, name='measurement-delete'),
] 