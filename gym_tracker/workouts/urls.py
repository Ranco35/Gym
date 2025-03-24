from django.urls import path
from .views import (
    WorkoutListCreateView, 
    WorkoutDetailView,
    routine_selection,
    routine_list,
    routine_detail,
    routine_day_detail,
    delete_routine_exercise,
    update_routine_focus
)

urlpatterns = [
    # API REST endpoints
    path('api/', WorkoutListCreateView.as_view(), name='workout-list-create'),
    path('api/<int:pk>/', WorkoutDetailView.as_view(), name='workout-detail'),
    
    # Django views para rutinas
    path('', routine_list, name='workout-home'),
    path('routine/new/', routine_selection, name='routine-selection'),
    path('routine/<int:pk>/', routine_detail, name='routine-detail'),
    path('routine/<int:routine_pk>/day/<int:day_pk>/', routine_day_detail, name='routine-day-detail'),
    path('routine/exercise/<int:exercise_pk>/delete/', delete_routine_exercise, name='delete-routine-exercise'),
    path('routine/day/<int:day_pk>/update-focus/', update_routine_focus, name='update-routine-focus'),
]
