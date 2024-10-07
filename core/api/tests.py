import os
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
from api.models import Project, ProjectParticipant, Task, TaskSubscriber
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class ProjectTestsAsAdmin(APITestCase):
    def setUp(self):
        self.admin = {
            'user_pk': 1,
            'sub': 'testadmin@example.com',
            'role': 'admin',
            'first_name': 'Test',
            'last_name': 'Admin',
        }

        self.admin_token = jwt.encode(
            self.admin,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.user = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.admin_project = Project.objects.create(
            title='Test Admin Project',
            description='Test Project',
            creator_id=self.admin['user_pk'],
        )

        self.user_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
        )

        self.inactive_user_project = Project.objects.create(
            title='Test Inactive User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
            active=False,
        )

        self.user_task = Task.objects.create(
            title='Test Task',
            description='Test Task',
            status='open',
            creator_id=self.user['user_pk'],
            project=self.user_project,
        )

        self.inactive_user_task = Task.objects.create(
            title='Test Inactive Task',
            description='Test Task',
            status='open',
            creator_id=self.user['user_pk'],
            project=self.inactive_user_project,
            active=False,
        )

    def test_read_projects(self):
        response = self.client.get(reverse('admin_project-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')), Project.objects.all().count()
        )
        self.assertTrue(
            all(
                ('active' in project and 'deleted_at' in project)
                for project in response.data.get('results')
            )
        )
        self.assertTrue(
            any(
                project.get('title') == self.user_project.title
                for project in response.data.get('results')
            )
        )

    def test_read_projects_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.get(reverse('admin_project-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_projects_without_authorization(self):
        self.client.credentials()

        response = self.client.get(reverse('admin_project-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_nonexistent_project(self):
        nonexistent_project_id = 999
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': nonexistent_project_id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_inactive_project(self):
        response = self.client.get(
            reverse(
                'admin_project-detail',
                kwargs={'pk': self.inactive_user_project.project_pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.inactive_user_project.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_read_active_project(self):
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.user_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.user_project.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_read_project_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.user_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_project_without_authorization(self):
        self.client.credentials()

        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.user_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_create_project(self, send_task_to_kafka):
        data = {
            'title': 'Test Admin Project 2',
            'description': 'Description for the second test admin project.',
        }
        response = self.client.post(reverse('admin_project-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(Project.objects.filter(title=data['title']).exists())
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=response.data.get("project_pk")
            ).exists()
        )

        send_task_to_kafka.assert_called_once()

    def test_create_project_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        data = {
            'title': 'Test Admin Project 2',
            'description': 'Description for the second test admin project.',
        }

        response = self.client.post(reverse('admin_project-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_project_without_authorization(self):
        self.client.credentials()
        data = {
            'title': 'Test Admin Project 2',
            'description': 'Description for the second test admin project.',
        }

        response = self.client.post(reverse('admin_project-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_active_project(self):
        response = self.client.patch(
            reverse(
                'admin_project-detail', kwargs={'pk': self.user_project.project_pk}
            ),
            {'title': 'Test Update User Active Project'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(title=self.user_project.title).exists())
        self.assertTrue(
            Project.objects.filter(title='Test Update User Active Project').exists()
        )

    def test_update_inactive_project(self):
        response = self.client.patch(
            reverse(
                'admin_project-detail',
                kwargs={'pk': self.inactive_user_project.project_pk},
            ),
            {'title': 'Test Update User Inactive Project'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Project.objects.filter(title=self.inactive_user_project.title).exists()
        )
        self.assertTrue(
            Project.objects.filter(title='Test Update User Inactive Project').exists()
        )

    def test_update_project_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.patch(
            reverse(
                'admin_project-detail', kwargs={'pk': self.user_project.project_pk}
            ),
            {'title': 'Test Update User Project'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_without_authorization(self):
        self.client.credentials()

        response = self.client.patch(
            reverse(
                'admin_project-detail', kwargs={'pk': self.user_project.project_pk}
            ),
            {'title': 'Test Update User Project'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_update_inactive_project_status(self, send_task_to_kafka):
        pk = self.inactive_user_project.project_pk

        response = self.client.put(
            reverse('admin_project_activation', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Project.objects.get(project_pk=pk).active)
        self.assertIsNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertTrue(Task.objects.get(project=self.inactive_user_project).active)

        send_task_to_kafka.assert_called_once()

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_update_active_project_status(self, send_task_to_kafka):
        pk = self.user_project.project_pk

        response = self.client.put(
            reverse('admin_project_activation', kwargs={'pk': pk}),
            {'active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.get(project_pk=pk).active)
        self.assertIsNotNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertFalse(Task.objects.get(project=self.user_project).active)

        send_task_to_kafka.assert_called_once()

    def test_update_project_status_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.put(
            reverse(
                'admin_project_activation', kwargs={'pk': self.user_project.project_pk}
            ),
            {'active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_status_without_authorization(self):
        self.client.credentials()

        response = self.client.put(
            reverse(
                'admin_project_activation', kwargs={'pk': self.user_project.project_pk}
            ),
            {'active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project(self):
        pk = self.user_project.project_pk

        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.get(project_pk=pk).active)
        self.assertIsNotNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertFalse(Task.objects.get(project=self.user_project).active)

    def test_delete_project_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': self.user_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_without_authorization(self):
        self.client.credentials()

        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': self.user_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProjectTests(APITestCase):
    def setUp(self):
        self.user_1 = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'First Test',
            'last_name': 'User',
        }
        self.user_2 = {
            'user_pk': 3,
            'sub': 'testuser_2@example.com',
            'role': 'user',
            'first_name': 'Second Test',
            'last_name': 'User',
        }

        self.token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.user_1_project = Project.objects.create(
            title='Test User 1 Project',
            description='Test Project',
            creator_id=self.user_1['user_pk'],
        )

        self.user_2_project = Project.objects.create(
            title='Test User 2 Project',
            description='Test Project',
            creator_id=self.user_2['user_pk'],
        )

        self.inactive_user_2_project = Project.objects.create(
            title='Test User 2 Inactive Project',
            description='Test Project',
            creator_id=self.user_2['user_pk'],
            active=False,
        )

        self.user_1_task = Task.objects.create(
            title='Test Task',
            description='Test Task',
            status='open',
            creator_id=self.user_1['user_pk'],
            project=self.user_1_project,
        )

    def test_read_active_projects(self):
        response = self.client.get(reverse('project-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            Project.objects.filter(active=True).count(),
        )
        self.assertFalse(
            all(
                ('active' in project and 'deleted_at' in project)
                for project in response.data.get('results')
            )
        )
        self.assertTrue(
            any(
                project.get('title') == self.user_1_project.title
                for project in response.data.get('results')
            )
        )

    def test_read_projects_without_authorization(self):
        self.client.credentials()

        response = self.client.get(reverse('project-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_nonexistent_project(self):
        nonexistent_project_id = 999

        response = self.client.get(
            reverse('project-detail', kwargs={'pk': nonexistent_project_id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_inactive_project(self):
        response = self.client.get(
            reverse(
                'project-detail', kwargs={'pk': self.inactive_user_2_project.project_pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_active_project(self):
        response = self.client.get(
            reverse('project-detail', kwargs={'pk': self.user_2_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.user_2_project.title)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_read_project_without_authorization(self):
        self.client.credentials()

        response = self.client.get(
            reverse('project-detail', kwargs={'pk': self.user_2_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_create_project(self, send_task_to_kafka):
        data = {
            'title': 'Test Project 3',
            'description': 'Description for the third test project.',
        }

        response = self.client.post(reverse('project-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())
        self.assertTrue(Project.objects.filter(title='Test Project 3').exists())
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=response.data.get("project_pk")
            ).exists()
        )

        send_task_to_kafka.assert_called_once()

    def test_create_project_without_authorization(self):
        self.client.credentials()

        data = {
            'title': 'Test Project 3',
            'description': 'Description for the third test project.',
        }

        response = self.client.post(reverse('project-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_by_creator(self):
        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': self.user_1_project.project_pk}),
            {'title': 'Test Update User 1 Project'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Project.objects.filter(title=self.user_1_project.title).exists()
        )
        self.assertTrue(
            Project.objects.filter(title='Test Update User 1 Project').exists()
        )

    def test_update_project_not_creator(self):
        self.client.credentials()
        self.not_creator_token = jwt.encode(
            self.user_2,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_creator_token}')

        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': self.user_1_project.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_without_authorization(self):
        self.client.credentials()

        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': self.user_1_project.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_creator(self):
        pk = self.user_1_project.project_pk

        response = self.client.delete(reverse('project-detail', kwargs={'pk': pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.get(project_pk=pk).active)
        self.assertIsNotNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertFalse(Task.objects.get(project=self.user_1_project).active)

    def test_delete_project_not_creator(self):
        self.client.credentials()
        self.not_creator_token = jwt.encode(
            self.user_2,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_creator_token}')

        response = self.client.delete(
            reverse('project-detail', kwargs={'pk': self.user_1_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_without_authorization(self):
        self.client.credentials()

        response = self.client.delete(
            reverse('project-detail', kwargs={'pk': self.user_1_project.project_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskTestsAsAdmin(APITestCase):
    def setUp(self):
        self.admin = {
            'user_pk': 1,
            'sub': 'testadmin@example.com',
            'role': 'admin',
            'first_name': 'Test',
            'last_name': 'Admin',
        }

        self.admin_token = jwt.encode(
            self.admin,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        self.user = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
        )

        self.inactive_user_project = Project.objects.create(
            title='Test Inactive User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
            active=False,
        )

        self.user_task = Task.objects.create(
            title='Test Task With Executor',
            description='Test Task With Executor',
            status='open',
            executor_id=self.user['user_pk'],
            creator_id=self.user['user_pk'],
            project=self.user_project,
        )

        self.inactive_user_task_with_inactive_project = Task.objects.create(
            title='Test Inactive Task With Inactive Project',
            description='Test Task',
            status='open',
            creator_id=self.user['user_pk'],
            project=self.inactive_user_project,
            active=False,
            deleted_at=datetime.utcnow(),
        )

        self.inactive_user_task_with_active_project = Task.objects.create(
            title='Test Inactive Task With Active Project',
            description='Test Task',
            status='open',
            creator_id=self.user['user_pk'],
            project=self.user_project,
            active=False,
            deleted_at=datetime.utcnow(),
        )

    def test_read_tasks(self):
        response = self.client.get(reverse('admin_task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), Task.objects.all().count())
        self.assertTrue(
            all(
                ('active' in task and 'deleted_at' in task)
                for task in response.data.get('results')
            )
        )
        self.assertTrue(
            any(
                task.get('title') == self.user_task.title
                for task in response.data.get('results')
            )
        )

    def test_read_tasks_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.get(reverse('admin_task-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_tasks_without_authorization(self):
        self.client.credentials()

        response = self.client.get(reverse('admin_task-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_nonexistent_task(self):
        nonexistent_task_id = 999
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': nonexistent_task_id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_inactive_task(self):
        response = self.client.get(
            reverse(
                'admin_task-detail',
                kwargs={'pk': self.inactive_user_task_with_inactive_project.task_pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('title'),
            self.inactive_user_task_with_inactive_project.title,
        )
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_read_active_task(self):
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.user_task.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_read_task_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_task_without_authorization(self):
        self.client.credentials()

        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_create_task(self, send_task_to_kafka):
        data = {
            'title': 'Test Admin Task',
            'description': 'Description for test admin task.',
            'project': self.user_project.project_pk,
            'status': 'reopened',
        }

        response = self.client.post(reverse('admin_task-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(Task.objects.filter(title=data['title']).exists())
        self.assertTrue(
            TaskSubscriber.objects.filter(task=response.data.get("task_pk")).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(project=data['project']).exists()
        )

        send_task_to_kafka.assert_called_once()

    def test_create_task_as_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')
        data = {
            'title': 'Test Admin Task',
            'description': 'Description for the test admin task.',
            'project': self.user_project.project_pk,
            'status': 'opened',
        }

        response = self.client.post(reverse('admin_task-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_without_authorization(self):
        self.client.credentials()
        data = {
            'title': 'Test Admin Task',
            'description': 'Description for the test admin task.',
            'project': self.user_project.project_pk,
            'status': 'opened',
        }

        response = self.client.post(reverse('admin_task-list'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_active_task(self):
        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk}),
            {'title': 'New Task title'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.filter(title=self.user_task.title).exists())
        self.assertTrue(Task.objects.filter(title='New Task title').exists())

    def test_update_inactive_task(self):
        response = self.client.patch(
            reverse(
                'admin_task-detail',
                kwargs={'pk': self.inactive_user_task_with_inactive_project.task_pk},
            ),
            {'title': 'Test Update User Inactive Task'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(title=self.inactive_user_project.title).exists()
        )
        self.assertTrue(
            Task.objects.filter(title='Test Update User Inactive Task').exists()
        )

    def test_update_task_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk}),
            {'title': 'Test Update User Task'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_without_authorization(self):
        self.client.credentials()

        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk}),
            {'title': 'Test Update User Task'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_update_inactive_task_status(self, send_task_to_kafka):
        pk = self.inactive_user_task_with_active_project.task_pk
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Task.objects.get(task_pk=pk).active)
        self.assertIsNone(Task.objects.get(task_pk=pk).deleted_at)

        send_task_to_kafka.assert_called_once()

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_update_active_task_status(self, send_task_to_kafka):
        pk = self.user_task.task_pk
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': pk}),
            {'active': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.get(task_pk=pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=pk).deleted_at)

        send_task_to_kafka.assert_called_once()

    def test_availability_task_status_activation(self):
        pk = self.inactive_user_task_with_inactive_project.task_pk
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.get(task_pk=pk).active)

    def test_update_task_status_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': self.user_task.task_pk}),
            {'active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_status_without_authorization(self):
        self.client.credentials()

        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': self.user_task.task_pk}),
            {'active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task(self):
        pk = self.user_task.task_pk
        response = self.client.delete(reverse('admin_task-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.get(task_pk=pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=pk).deleted_at)
        self.assertFalse(TaskSubscriber.objects.filter(task=self.user_task).exists())

    def test_delete_task_not_admin(self):
        self.client.credentials()
        self.not_admin_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_admin_token}')

        response = self.client.delete(
            reverse('admin_task-detail', kwargs={'pk': self.user_task.task_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_without_authorization(self):
        self.client.credentials()

        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': self.user_task.task_pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskTests(APITestCase):
    def setUp(self):
        self.user_1 = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        self.user_2 = {
            'user_pk': 3,
            'sub': 'testuser_2@example.com',
            'role': 'user',
            'first_name': 'Test 2',
            'last_name': 'User',
        }

        self.admin = {
            'user_pk': 1,
            'sub': 'admin@example.com',
            'role': 'admin',
            'first_name': 'Test',
            'last_name': 'Admin',
        }

        self.user_1_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user_1['user_pk'],
        )

        self.user_1_task_with_executor = Task.objects.create(
            title='Test Task With Executor',
            description='Test Task With Executor',
            status='open',
            executor_id=self.user_1['user_pk'],
            creator_id=self.user_1['user_pk'],
            project=self.user_1_project,
        )

        self.user_1_task_without_executor = Task.objects.create(
            title='Test Task Without Executor',
            description='Test Task Without Executor',
            status='open',
            creator_id=self.user_1['user_pk'],
            project=self.user_1_project,
        )

        self.inactive_user_1_task = Task.objects.create(
            title='Test Inactive Task With Active Project',
            description='Test Task',
            status='open',
            creator_id=self.user_1['user_pk'],
            project=self.user_1_project,
            active=False,
            deleted_at=datetime.utcnow(),
        )

    def test_read_active_tasks(self):
        response = self.client.get(reverse('task-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            Task.objects.filter(active=True).count(),
        )
        self.assertFalse(
            all(
                ('active' in task and 'deleted_at' in task)
                for task in response.data.get('results')
            )
        )
        self.assertTrue(
            any(
                task.get('title') == self.user_1_task_with_executor.title
                for task in response.data.get('results')
            )
        )

    def test_read_tasks_without_authorization(self):
        self.client.credentials()

        response = self.client.get(reverse('task-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_nonexistent_task(self):
        nonexistent_task_id = 999

        response = self.client.get(
            reverse('task-detail', kwargs={'pk': nonexistent_task_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_active_task(self):
        response = self.client.get(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_with_executor.task_pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('title'), self.user_1_task_with_executor.title
        )
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_read_inactive_task(self):
        response = self.client.get(
            reverse('task-detail', kwargs={'pk': self.inactive_user_1_task.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_task_without_authorization(self):
        self.client.credentials()

        response = self.client.get(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_with_executor.task_pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_task_to_kafka.delay')
    def test_create_task(self, send_task_to_kafka):
        data = {
            'title': 'Test User Task',
            'description': 'Description for test user task.',
            'project': self.user_1_project.project_pk,
            'status': 'reopened',
        }

        response = self.client.post(reverse('task-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())
        self.assertTrue(Task.objects.filter(title=data['title']).exists())
        self.assertTrue(
            TaskSubscriber.objects.filter(task=response.data.get("task_pk")).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(project=data['project']).exists()
        )

        send_task_to_kafka.assert_called_once()

    def test_create_task_without_authorization(self):
        self.client.credentials()
        data = {
            'title': 'Test User Task',
            'description': 'Description for test user task.',
            'project': self.user_1_project.project_pk,
            'status': 'reopened',
        }

        response = self.client.post(reverse('task-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_by_creator(self):
        response = self.client.patch(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_with_executor.task_pk}
            ),
            {'title': 'Test Update User 1 Task'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(title=self.user_1_task_with_executor.title).exists()
        )
        self.assertTrue(Task.objects.filter(title='Test Update User 1 Task').exists())

    def test_update_task_not_creator(self):
        self.client.credentials()
        self.not_creator_token = jwt.encode(
            self.user_2,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_creator_token}')

        response = self.client.patch(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_with_executor.task_pk}
            ),
            {'title': 'Test Task 4'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_without_authorization(self):
        self.client.credentials()

        response = self.client.patch(
            reverse(
                'project-detail', kwargs={'pk': self.user_1_task_with_executor.task_pk}
            ),
            {'title': 'Test Task 4'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_creator(self):
        pk = self.user_1_task_with_executor.task_pk

        response = self.client.delete(reverse('task-detail', kwargs={'pk': pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.get(task_pk=pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=pk).deleted_at)

    def test_delete_task_not_creator(self):
        self.client.credentials()
        self.not_creator_token = jwt.encode(
            self.user_2,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.not_creator_token}')

        response = self.client.delete(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_without_executor.task_pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_without_authorization(self):
        self.client.credentials()

        response = self.client.delete(
            reverse(
                'task-detail', kwargs={'pk': self.user_1_task_without_executor.task_pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskStatusUpdateViewTest(APITestCase):
    def setUp(self):
        self.admin = {
            'user_pk': 1,
            'sub': 'admin@example.com',
            'role': 'admin',
            'first_name': 'Test',
            'last_name': 'Admin',
        }

        self.user = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_1 = {
            'user_pk': 3,
            'sub': 'testuser_1@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.admin_token = jwt.encode(
            self.admin,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.user_1_token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.user_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )

        self.user_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
        )

        self.user_task = Task.objects.create(
            title='Test Task With Executor',
            description='Test Task With Executor',
            status='open',
            executor_id=self.user['user_pk'],
            creator_id=self.user['user_pk'],
            project=self.user_project,
        )

        self.subscriber = TaskSubscriber.objects.create(
            task=self.user_task, subscriber_id=self.user['user_pk']
        )

        self.url = reverse("task_status_update", kwargs={"pk": self.user_task.task_pk})

    # @patch("api.tasks.send_task_status_update_notification.delay")
    # @patch("api.tasks.send_task_to_kafka.delay")
    # def test_task_status_update_success(self, mock_send_task_to_kafka, mock_send_task_status_update_notification):
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    #
    #     data = {"status": "in_progress"}
    #     response = self.client.patch(self.url, data, format="json")
    #
    #     self.user_task.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(self.user_task.status, "in_progress")
    #
    #     mock_send_task_status_update_notification.assert_called_once()
    #     mock_send_task_to_kafka.assert_called_once_with(
    #         task_data={"title": self.user_task.title, "status": "in_progress"}, key="update_task"
    #     )

    def test_task_status_update_permission_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_1_token}')

        data = {"status": "in_progress"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # @patch("api.tasks.send_task_status_update_notification.delay")
    # @patch("api.tasks.send_task_to_kafka.delay")
    # def test_task_status_no_change(self, mock_send_task_to_kafka, mock_send_task_status_update_notification):
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
    #
    #     data = {"status": self.user_task.status}
    #     response = self.client.patch(self.url, data, format="json")
    #
    #     self.user_task.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(self.user_task.status, "open")
    #
    #     mock_send_task_status_update_notification.assert_not_called()
    #     mock_send_task_to_kafka.assert_not_called()


class TaskExecutorUpdateViewTest(APITestCase):
    def setUp(self):
        self.admin = {
            'user_pk': 1,
            'sub': 'admin@example.com',
            'role': 'admin',
            'first_name': 'Test',
            'last_name': 'Admin',
        }

        self.user = {
            'user_pk': 2,
            'sub': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_1 = {
            'user_pk': 3,
            'sub': 'testuser_1@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.admin_token = jwt.encode(
            self.admin,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.user_1_token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.user_token = jwt.encode(
            self.user, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )

        self.user_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user['user_pk'],
        )

        self.user_task = Task.objects.create(
            title='Test Task With Executor',
            description='Test Task With Executor',
            status='open',
            executor_id=self.user['user_pk'],
            creator_id=self.user['user_pk'],
            project=self.user_project,
        )

        self.url = reverse(
            "task_executor_update", kwargs={"pk": self.user_task.task_pk}
        )

    # @patch("api.tasks.send_task_to_kafka.delay")
    # def test_task_executor_update_success(self, mock_send_task_to_kafka):
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
    #
    #     new_executor_id = self.user_1['user_pk']
    #     data = {"executor_id": new_executor_id}
    #     response = self.client.patch(self.url, data, format="json")
    #
    #     self.user_task.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(self.user_task.executor_id, new_executor_id)
    #
    #     mock_send_task_to_kafka.assert_called_once_with(
    #         task_data={
    #             "title": self.user_task.title,
    #             "executor_id": new_executor_id,
    #             "assigner_id": self.user['user_pk'],
    #             "project_title": self.user_task.project_title,
    #         },
    #         key="update_task"
    #     )

    def test_task_executor_update_permission_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_1_token}')

        new_executor_id = self.admin['user_pk']
        data = {"executor_id": new_executor_id}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # @patch("api.tasks.send_task_to_kafka.delay")
    # def test_task_executor_no_change(self, mock_send_task_to_kafka):
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
    #
    #     data = {"executor_id": self.user_1['user_pk']}
    #     response = self.client.patch(self.url, data, format="json")
    #
    #     self.user_task.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(self.user_task.executor_id, self.user['user_pk'])
    #
    #     mock_send_task_to_kafka.assert_not_called()


class TaskSubscribersViewSetTests(APITestCase):
    def setUp(self):
        self.user_1 = {
            'user_pk': 2,
            'email': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_2 = {
            'user_pk': 3,
            'email': 'testuser_2@example.com',
            'role': 'user',
            'first_name': 'Second Test',
            'last_name': 'User',
        }

        self.token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.user_project = Project.objects.create(
            title='Test User Project',
            description='Test Project',
            creator_id=self.user_1['user_pk'],
        )

        self.task = Task.objects.create(
            title='Test Task',
            description='Test Task',
            status='open',
            creator_id=self.user_1.get('user_pk'),
            project=self.user_project,
        )

        self.subscription = TaskSubscriber.objects.create(
            task=self.task, subscriber_id=self.user_1.get('user_pk')
        )

        self.subscription = TaskSubscriber.objects.create(
            task=self.task, subscriber_id=self.user_2.get('user_pk')
        )

    def test_read_subscriptions(self):
        response = self.client.get(reverse('task_subscription-list'))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')), TaskSubscriber.objects.all().count()
        )
        self.assertTrue(
            any(
                subscription.get('subscriber_id') == self.user_2.get('user_pk')
                for subscription in response.data.get('results')
            )
        )

    def test_read_subscriptions_without_authorization(self):
        self.client.credentials()

        response = self.client.get(reverse('task_subscription-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_nonexistent_subscription(self):
        nonexistent_pk = 999
        response = self.client.get(
            reverse('task_subscription-detail', kwargs={'pk': nonexistent_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_subscription(self):
        response = self.client.get(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription.task_subscriber_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('subscriber_id'), self.subscription.subscriber_id
        )

    def test_read_subscription_without_authorization(self):
        self.client.credentials()

        response = self.client.get(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription.task_subscriber_pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    @patch('api.tasks.send_join_to_project_notification.delay')
    @patch('api.utils.get_email_for_notification')
    def test_create_subscription(
        self,
        mock_get_email_for_notification,
        mock_send_subscription_on_task_notification,
        mock_send_join_to_project_notification,
    ):
        mock_get_email_for_notification.return_value = 'test@example.com'

        response = self.client.post(
            reverse('task_subscription-list'),
            {'task': self.task.task_pk, 'subscriber_id': 10},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        mock_send_subscription_on_task_notification.assert_called_once()
        mock_send_join_to_project_notification.assert_called_once()

    def test_update_subscription(self):
        response = self.client.patch(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription.task_subscriber_pk},
            ),
            {'subscriber_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_subscription(self):
        response = self.client.delete(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription.task_subscriber_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectParticipantsViewSetTests(APITestCase):
    def setUp(self):
        self.user_1 = {
            'user_pk': 2,
            'email': 'testuser@example.com',
            'role': 'user',
            'first_name': 'Test',
            'last_name': 'User',
        }

        self.user_2 = {
            'user_pk': 3,
            'email': 'testuser_2@example.com',
            'role': 'user',
            'first_name': 'Second Test',
            'last_name': 'User',
        }

        self.token = jwt.encode(
            self.user_1,
            os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.project = Project.objects.create(
            title='Test Project',
            description='Description for the test project.',
            creator_id=self.user_1.get('user_pk'),
        )
        self.participation_1 = ProjectParticipant.objects.create(
            project=self.project, participant_id=self.user_1['user_pk']
        )
        self.participation_2 = ProjectParticipant.objects.create(
            project=self.project, participant_id=self.user_2['user_pk']
        )

    def test_get_participants_list(self):
        response = self.client.get(reverse('project_participant-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            ProjectParticipant.objects.all().count(),
        )
        self.assertIn(
            ('project', self.project.project_pk),
            response.data.get('results')[-1].items(),
        )
        self.assertIn(
            ('participant_id', self.participation_2.participant_id),
            response.data.get('results')[-1].items(),
        )

    def test_get_nonexistent_participation(self):
        response = self.client.get(
            reverse('project_participant-detail', kwargs={'pk': 10})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participation(self):
        response = self.client.get(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.project_participant_pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('participant_id'), self.participation_2.participant_id
        )
        self.assertEqual(
            response.data.get('participant_id'), self.participation_1.participant_id
        )

    @patch('api.tasks.send_join_to_project_notification.delay')
    @patch('api.utils.get_email_for_notification')
    def test_create_participation(self, mock_get_email, mock_send_notification):
        mock_get_email.return_value = "notification@example.com"

        response = self.client.post(
            reverse('project_participant-list'),
            {'project': self.project.project_pk, 'participant_id': 4},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=self.project.project_pk, participant_id=4
            ).exists()
        )
        mock_send_notification.assert_called_once_with(
            "notification@example.com", self.project.title
        )
        mock_get_email.assert_called_once()

    def test_update_participation(self):
        response = self.client.patch(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.project_participant_pk},
            ),
            {'participant_id': 3},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_participation(self):
        response = self.client.delete(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.project_participant_pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
