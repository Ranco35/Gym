from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import datetime

from ..models import Note

User = get_user_model()

class NoteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear una nota de prueba
        self.note = Note.objects.create(
            user=self.user,
            title='Test Note',
            content='Test content',
            category='workout',
            created_at=datetime.now()
        )
        
        # Crear una nota de otro usuario
        self.other_note = Note.objects.create(
            user=self.other_user,
            title='Other Note',
            content='Other content',
            category='workout',
            created_at=datetime.now()
        )

    def test_list_notes(self):
        """Test listar notas"""
        url = reverse('notes:note-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Note')

    def test_create_note(self):
        """Test crear una nueva nota"""
        url = reverse('notes:note-list-create-api')
        payload = {
            'title': 'New Note',
            'content': 'New content',
            'category': 'workout'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 3)  # 2 iniciales + 1 nueva
        self.assertEqual(Note.objects.get(title='New Note').content, 'New content')

    def test_create_note_invalid_data(self):
        """Test crear una nota con datos inválidos"""
        url = reverse('notes:note-list-create-api')
        payload = {
            'title': '',  # Título vacío
            'category': 'invalid-category'  # Categoría inválida
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Note.objects.count(), 2)  # No se creó ninguna nota

    def test_retrieve_note(self):
        """Test obtener una nota específica"""
        url = reverse('notes:note-detail-api', args=[self.note.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')

    def test_retrieve_other_user_note(self):
        """Test intentar obtener una nota de otro usuario"""
        url = reverse('notes:note-detail-api', args=[self.other_note.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_note(self):
        """Test actualizar una nota"""
        url = reverse('notes:note-detail-api', args=[self.note.id])
        payload = {
            'title': 'Updated Note',
            'content': 'Updated content'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.content, 'Updated content')

    def test_update_other_user_note(self):
        """Test intentar actualizar una nota de otro usuario"""
        url = reverse('notes:note-detail-api', args=[self.other_note.id])
        payload = {
            'title': 'Hacked Note',
            'content': 'Hacked content'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_note.refresh_from_db()
        self.assertEqual(self.other_note.title, 'Other Note')
        self.assertEqual(self.other_note.content, 'Other content')

    def test_delete_note(self):
        """Test eliminar una nota"""
        url = reverse('notes:note-detail-api', args=[self.note.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 1)  # Solo queda la nota del otro usuario

    def test_delete_other_user_note(self):
        """Test intentar eliminar una nota de otro usuario"""
        url = reverse('notes:note-detail-api', args=[self.other_note.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)  # No se eliminó ninguna nota

    def test_unauthorized_access(self):
        """Test acceso no autorizado"""
        self.client.logout()
        url = reverse('notes:note-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_create(self):
        """Test crear nota sin autenticación"""
        self.client.logout()
        url = reverse('notes:note-list-create-api')
        payload = {
            'title': 'New Note',
            'content': 'New content',
            'category': 'workout'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Note.objects.count(), 2)  # No se creó ninguna nota 