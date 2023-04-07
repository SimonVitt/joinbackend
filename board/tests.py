import datetime
from django.test import TestCase

# Create your tests here.
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from board.models import Board, Category, Task

class TestBoard(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('test_user', password='test_user')
        self.client.login(username='test_user', password='test_user')
        self.token = Token.objects.create(user=self.user)
        group = Group.objects.create(name='boardgrouptest')
        group.user_set.add(self.user)
        self.board = Board.objects.create(name='test', group=group)        
        self.category = Category.objects.create(name='Test Category', board=self.board, color='blue')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        super().setUp()

        
    
    def test_getalluser(self):  
        response = self.client.get('/api/alluser/')
        self.assertEqual(response.status_code, 200)
        
    def test_get_all_boards(self):
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 200)
        
    def test_create_board(self):
        data = {
            "name": "test board",
            "board_users": [self.user.id]
        }
        response = self.client.post('/api/createboard/', data)
        self.assertEqual(response.status_code, 201)
        
    def test_create_task(self):
        url = f'/api/{str(self.board.id)}/tasks/'
        data = {
            'priority': 'urgent',
            'title': 'Test Task',
            'description': 'This is a test task',
            'due_date': '2023-04-30',
            'status': 'progress',
            'assigned_users': [self.user.id],
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title='Test Task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.status, 'progress')
        self.assertEqual(task.category, self.category)
        self.assertIn(self.user, task.assigned_users.all())
