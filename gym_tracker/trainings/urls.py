from django.urls import path
from .views import TrainingListCreateView, TrainingDetailView

urlpatterns = [
    path('', TrainingListCreateView.as_view(), name='training-list-create'),
    path('<int:pk>/', TrainingDetailView.as_view(), name='training-detail'),
]