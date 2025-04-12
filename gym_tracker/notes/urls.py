from django.urls import path
from .views import (
    # API
    NoteListCreateView, 
    NoteDetailView,
    
    # Web
    note_list, 
    note_detail, 
    note_create, 
    note_edit, 
    note_delete
)

app_name = 'notes'

urlpatterns = [
    # API
    path('api/notes/', NoteListCreateView.as_view(), name='note-list-create-api'),
    path('api/notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail-api'),
    
    # Web
    path('', note_list, name='note-list'),
    path('<int:pk>/', note_detail, name='note-detail'),
    path('create/', note_create, name='note-create'),
    path('<int:pk>/edit/', note_edit, name='note-edit'),
    path('<int:pk>/delete/', note_delete, name='note-delete'),
] 