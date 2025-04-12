from django.urls import path
from .views import (
    # API
    GoalListCreateView, 
    GoalDetailView,
    
    # Web
    goal_list, 
    goal_detail, 
    goal_create, 
    goal_edit, 
    goal_delete
)

app_name = 'goals'

urlpatterns = [
    # API
    path('api/goals/', GoalListCreateView.as_view(), name='goal-list-create-api'),
    path('api/goals/<int:pk>/', GoalDetailView.as_view(), name='goal-detail-api'),
    
    # Web
    path('', goal_list, name='goal-list'),
    path('<int:pk>/', goal_detail, name='goal-detail'),
    path('create/', goal_create, name='goal-create'),
    path('<int:pk>/edit/', goal_edit, name='goal-edit'),
    path('<int:pk>/delete/', goal_delete, name='goal-delete'),
] 