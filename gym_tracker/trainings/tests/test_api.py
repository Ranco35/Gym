from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import date

from ..models import Training, Set
from gym_tracker.exercises.models import Exercise

User = get_user_model()

class TrainingAPITests(TestCase):
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
        
        # Crear un entrenamiento de prueba
        self.training = Training.objects.create(
            user=self.user,
            name='Test Training',
            date=date.today(),
            notes='Test notes'
        )
        
        # Crear un entrenamiento de otro usuario
        self.other_training = Training.objects.create(
            user=self.other_user,
            name='Other Training',
            date=date.today(),
            notes='Other notes'
        )
        
        # Crear un ejercicio de prueba
        self.exercise = Exercise.objects.create(
            name='Test Exercise',
            description='Test description'
        )

    def test_list_trainings(self):
        """Test listar entrenamientos"""
        url = reverse('trainings:training-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Training')

    def test_create_training(self):
        """Test crear un nuevo entrenamiento"""
        url = reverse('trainings:training-list-create-api')
        payload = {
            'name': 'New Training',
            'date': date.today(),
            'notes': 'New notes'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Training.objects.count(), 3)  # 2 iniciales + 1 nuevo
        self.assertEqual(Training.objects.get(name='New Training').notes, 'New notes')

    def test_create_training_invalid_data(self):
        """Test crear un entrenamiento con datos inválidos"""
        url = reverse('trainings:training-list-create-api')
        payload = {
            'name': '',  # Nombre vacío
            'date': 'invalid-date',  # Fecha inválida
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Training.objects.count(), 2)  # No se creó ningún entrenamiento

    def test_retrieve_training(self):
        """Test obtener un entrenamiento específico"""
        url = reverse('trainings:training-detail-api', args=[self.training.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Training')

    def test_retrieve_other_user_training(self):
        """Test intentar obtener un entrenamiento de otro usuario"""
        url = reverse('trainings:training-detail-api', args=[self.other_training.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_training(self):
        """Test actualizar un entrenamiento"""
        url = reverse('trainings:training-detail-api', args=[self.training.id])
        payload = {
            'name': 'Updated Training',
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.training.refresh_from_db()
        self.assertEqual(self.training.name, 'Updated Training')
        self.assertEqual(self.training.notes, 'Updated notes')

    def test_update_other_user_training(self):
        """Test intentar actualizar un entrenamiento de otro usuario"""
        url = reverse('trainings:training-detail-api', args=[self.other_training.id])
        payload = {
            'name': 'Hacked Training',
            'notes': 'Hacked notes'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_training.refresh_from_db()
        self.assertEqual(self.other_training.name, 'Other Training')
        self.assertEqual(self.other_training.notes, 'Other notes')

    def test_delete_training(self):
        """Test eliminar un entrenamiento"""
        url = reverse('trainings:training-detail-api', args=[self.training.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Training.objects.count(), 1)  # Solo queda el entrenamiento del otro usuario

    def test_delete_other_user_training(self):
        """Test intentar eliminar un entrenamiento de otro usuario"""
        url = reverse('trainings:training-detail-api', args=[self.other_training.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Training.objects.count(), 2)  # No se eliminó ningún entrenamiento

    def test_save_set(self):
        """Test guardar un set"""
        url = reverse('trainings:save-set-api')
        payload = {
            'training_id': self.training.id,
            'exercise_id': self.exercise.id,
            'reps': 10,
            'weight': 50.0,
            'notes': 'Test set'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Set.objects.count(), 1)
        self.assertEqual(Set.objects.first().reps, 10)

    def test_save_set_invalid_data(self):
        """Test guardar un set con datos inválidos"""
        url = reverse('trainings:save-set-api')
        payload = {
            'training_id': self.training.id,
            'exercise_id': self.exercise.id,
            'reps': -1,  # Repeticiones negativas
            'weight': 'invalid',  # Peso inválido
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Set.objects.count(), 0)

    def test_save_set_other_user_training(self):
        """Test intentar guardar un set en un entrenamiento de otro usuario"""
        url = reverse('trainings:save-set-api')
        payload = {
            'training_id': self.other_training.id,
            'exercise_id': self.exercise.id,
            'reps': 10,
            'weight': 50.0,
            'notes': 'Test set'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Set.objects.count(), 0)

    def test_unauthorized_access(self):
        """Test acceso no autorizado"""
        self.client.logout()
        url = reverse('trainings:training-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_create(self):
        """Test crear entrenamiento sin autenticación"""
        self.client.logout()
        url = reverse('trainings:training-list-create-api')
        payload = {
            'name': 'New Training',
            'date': date.today(),
            'notes': 'New notes'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Training.objects.count(), 2)  # No se creó ningún entrenamiento 