from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from ..models import Goal

User = get_user_model()

class GoalAPITests(TestCase):
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
        
        # Crear un objetivo de prueba
        self.goal = Goal.objects.create(
            user=self.user,
            title='Test Goal',
            description='Test description',
            target_date=date.today() + timedelta(days=30),
            status='pending'
        )
        
        # Crear un objetivo de otro usuario
        self.other_goal = Goal.objects.create(
            user=self.other_user,
            title='Other Goal',
            description='Other description',
            target_date=date.today() + timedelta(days=30),
            status='pending'
        )

    def test_list_goals(self):
        """Test listar objetivos"""
        url = reverse('goals:goal-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Goal')

    def test_create_goal(self):
        """Test crear un nuevo objetivo"""
        url = reverse('goals:goal-list-create-api')
        payload = {
            'title': 'New Goal',
            'description': 'New description',
            'target_date': (date.today() + timedelta(days=30)).isoformat(),
            'status': 'pending'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.count(), 3)  # 2 iniciales + 1 nuevo
        self.assertEqual(Goal.objects.get(title='New Goal').description, 'New description')

    def test_create_goal_invalid_data(self):
        """Test crear un objetivo con datos inválidos"""
        url = reverse('goals:goal-list-create-api')
        payload = {
            'title': '',  # Título vacío
            'target_date': 'invalid-date',  # Fecha inválida
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Goal.objects.count(), 2)  # No se creó ningún objetivo

    def test_retrieve_goal(self):
        """Test obtener un objetivo específico"""
        url = reverse('goals:goal-detail-api', args=[self.goal.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Goal')

    def test_retrieve_other_user_goal(self):
        """Test intentar obtener un objetivo de otro usuario"""
        url = reverse('goals:goal-detail-api', args=[self.other_goal.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_goal(self):
        """Test actualizar un objetivo"""
        url = reverse('goals:goal-detail-api', args=[self.goal.id])
        payload = {
            'title': 'Updated Goal',
            'description': 'Updated description'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.title, 'Updated Goal')
        self.assertEqual(self.goal.description, 'Updated description')

    def test_update_other_user_goal(self):
        """Test intentar actualizar un objetivo de otro usuario"""
        url = reverse('goals:goal-detail-api', args=[self.other_goal.id])
        payload = {
            'title': 'Hacked Goal',
            'description': 'Hacked description'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_goal.refresh_from_db()
        self.assertEqual(self.other_goal.title, 'Other Goal')
        self.assertEqual(self.other_goal.description, 'Other description')

    def test_delete_goal(self):
        """Test eliminar un objetivo"""
        url = reverse('goals:goal-detail-api', args=[self.goal.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Goal.objects.count(), 1)  # Solo queda el objetivo del otro usuario

    def test_delete_other_user_goal(self):
        """Test intentar eliminar un objetivo de otro usuario"""
        url = reverse('goals:goal-detail-api', args=[self.other_goal.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Goal.objects.count(), 2)  # No se eliminó ningún objetivo

    def test_unauthorized_access(self):
        """Test acceso no autorizado"""
        self.client.logout()
        url = reverse('goals:goal-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_create(self):
        """Test crear objetivo sin autenticación"""
        self.client.logout()
        url = reverse('goals:goal-list-create-api')
        payload = {
            'title': 'New Goal',
            'description': 'New description',
            'target_date': (date.today() + timedelta(days=30)).isoformat(),
            'status': 'pending'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Goal.objects.count(), 2)  # No se creó ningún objetivo 