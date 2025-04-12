from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import date

from ..models import Measurement

User = get_user_model()

class MeasurementAPITests(TestCase):
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
        
        # Crear una medida de prueba
        self.measurement = Measurement.objects.create(
            user=self.user,
            date=date.today(),
            weight=75.5,
            height=180,
            body_fat=15.0,
            chest=100,
            waist=80,
            hips=95,
            biceps=35,
            thighs=55,
            notes='Test notes'
        )
        
        # Crear una medida de otro usuario
        self.other_measurement = Measurement.objects.create(
            user=self.other_user,
            date=date.today(),
            weight=70.0,
            height=175,
            body_fat=12.0,
            chest=95,
            waist=75,
            hips=90,
            biceps=32,
            thighs=52,
            notes='Other notes'
        )

    def test_list_measurements(self):
        """Test listar medidas"""
        url = reverse('measurements:measurement-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['weight'], 75.5)

    def test_create_measurement(self):
        """Test crear una nueva medida"""
        url = reverse('measurements:measurement-list-create-api')
        payload = {
            'date': date.today().isoformat(),
            'weight': 76.0,
            'height': 180,
            'body_fat': 14.5,
            'chest': 101,
            'waist': 81,
            'hips': 96,
            'biceps': 36,
            'thighs': 56,
            'notes': 'New notes'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Measurement.objects.count(), 3)  # 2 iniciales + 1 nueva
        self.assertEqual(Measurement.objects.get(weight=76.0).notes, 'New notes')

    def test_create_measurement_invalid_data(self):
        """Test crear una medida con datos inválidos"""
        url = reverse('measurements:measurement-list-create-api')
        payload = {
            'date': 'invalid-date',  # Fecha inválida
            'weight': -1,  # Peso negativo
            'height': 0,  # Altura cero
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Measurement.objects.count(), 2)  # No se creó ninguna medida

    def test_retrieve_measurement(self):
        """Test obtener una medida específica"""
        url = reverse('measurements:measurement-detail-api', args=[self.measurement.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], 75.5)

    def test_retrieve_other_user_measurement(self):
        """Test intentar obtener una medida de otro usuario"""
        url = reverse('measurements:measurement-detail-api', args=[self.other_measurement.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_measurement(self):
        """Test actualizar una medida"""
        url = reverse('measurements:measurement-detail-api', args=[self.measurement.id])
        payload = {
            'weight': 76.0,
            'body_fat': 14.5,
            'notes': 'Updated notes'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.measurement.refresh_from_db()
        self.assertEqual(self.measurement.weight, 76.0)
        self.assertEqual(self.measurement.body_fat, 14.5)
        self.assertEqual(self.measurement.notes, 'Updated notes')

    def test_update_other_user_measurement(self):
        """Test intentar actualizar una medida de otro usuario"""
        url = reverse('measurements:measurement-detail-api', args=[self.other_measurement.id])
        payload = {
            'weight': 71.0,
            'notes': 'Hacked notes'
        }
        response = self.client.patch(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_measurement.refresh_from_db()
        self.assertEqual(self.other_measurement.weight, 70.0)
        self.assertEqual(self.other_measurement.notes, 'Other notes')

    def test_delete_measurement(self):
        """Test eliminar una medida"""
        url = reverse('measurements:measurement-detail-api', args=[self.measurement.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Measurement.objects.count(), 1)  # Solo queda la medida del otro usuario

    def test_delete_other_user_measurement(self):
        """Test intentar eliminar una medida de otro usuario"""
        url = reverse('measurements:measurement-detail-api', args=[self.other_measurement.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Measurement.objects.count(), 2)  # No se eliminó ninguna medida

    def test_unauthorized_access(self):
        """Test acceso no autorizado"""
        self.client.logout()
        url = reverse('measurements:measurement-list-create-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_create(self):
        """Test crear medida sin autenticación"""
        self.client.logout()
        url = reverse('measurements:measurement-list-create-api')
        payload = {
            'date': date.today().isoformat(),
            'weight': 76.0,
            'height': 180,
            'body_fat': 14.5,
            'chest': 101,
            'waist': 81,
            'hips': 96,
            'biceps': 36,
            'thighs': 56,
            'notes': 'New notes'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Measurement.objects.count(), 2)  # No se creó ninguna medida 