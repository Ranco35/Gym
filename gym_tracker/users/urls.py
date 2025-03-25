# Este archivo ya no se usa, las rutas se definen directamente en gym_tracker/urls.py
# Mantenemos este archivo para compatibilidad, pero está vacío

from django.urls import path
from .views import UserListView, UserDetailView, UserProfileView

app_name = 'users'

# Rutas para la API REST de usuarios
urlpatterns = [
    # API endpoints para administración de usuarios
    path('admin/', UserListView.as_view(), name='user-admin-list'),
    path('admin/<int:pk>/', UserDetailView.as_view(), name='user-admin-detail'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
]
