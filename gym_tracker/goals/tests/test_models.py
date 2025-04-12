from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Goal

User = get_user_model()

class GoalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_goal(self):
        goal = Goal.objects.create(
            title='New Goal',
            description='Description of the goal',
            start_date='2023-01-01',
            end_date='2023-12-31',
            status='in_progress',
            user=self.user
        )
        self.assertEqual(goal.title, 'New Goal')
        self.assertEqual(goal.user, self.user)

    def test_update_goal(self):
        goal = Goal.objects.create(
            title='New Goal',
            description='Description of the goal',
            start_date='2023-01-01',
            end_date='2023-12-31',
            status='in_progress',
            user=self.user
        )
        goal.title = 'Updated Goal'
        goal.save()
        self.assertEqual(goal.title, 'Updated Goal')

    def test_delete_goal(self):
        goal = Goal.objects.create(
            title='New Goal',
            description='Description of the goal',
            start_date='2023-01-01',
            end_date='2023-12-31',
            status='in_progress',
            user=self.user
        )
        goal_id = goal.id
        goal.delete()
        self.assertFalse(Goal.objects.filter(id=goal_id).exists()) 