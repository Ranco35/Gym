from django.urls import path
from .views import (
    # API
    UserListCreateView, 
    UserDetailView,
    UserProfileListCreateView, 
    UserProfileDetailView,
    
    # Web
    user_list, 
    user_detail, 
    user_create, 
    user_edit, 
    user_delete,
    profile_list, 
    profile_detail, 
    profile_create, 
    profile_edit, 
    profile_delete
)

app_name = 'accounts'

urlpatterns = [
    # API
    path('api/users/', UserListCreateView.as_view(), name='user-list-create-api'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user-detail-api'),
    path('api/profiles/', UserProfileListCreateView.as_view(), name='profile-list-create-api'),
    path('api/profiles/<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail-api'),
    
    # Web
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/create/', user_create, name='user-create'),
    path('users/<int:pk>/edit/', user_edit, name='user-edit'),
    path('users/<int:pk>/delete/', user_delete, name='user-delete'),
    path('profiles/', profile_list, name='profile-list'),
    path('profiles/<int:pk>/', profile_detail, name='profile-detail'),
    path('profiles/create/', profile_create, name='profile-create'),
    path('profiles/<int:pk>/edit/', profile_edit, name='profile-edit'),
    path('profiles/<int:pk>/delete/', profile_delete, name='profile-delete'),
] 