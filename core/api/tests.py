from datetime import datetime
from unittest.mock import patch

from api.models import (
    Project,
    ProjectParticipant,
    Task,
    TasksAttachment,
    TaskSubscriber,
)
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ProjectTests(APITestCase):
    def setUp(self):
        self.project_1 = Project.objects.create(
            title='Test Project 1',
            description='Description for the first test project.',
        )
        self.project_2 = Project.objects.create(
            title='Test Project 2',
            description='Description for the second test project.',
        )
        self.project_3 = Project.objects.create(
            title='Test Inactive Project',
            description='Description for the inactive test project.',
            active=False,
        )
        self.task_1 = Task.objects.create(
            title='Test Task 1',
            description='Description for the first test task.',
            status='open',
            project=self.project_2,
        )
        self.task_2 = Task.objects.create(
            title='Test Task 2',
            description='Description for the second test task.',
            status='open',
            project=self.project_3,
        )

    def test_get_list_of_active_projects(self):
        """
        Ensure we can get a list of ACTIVE projects.
        """
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            Project.objects.filter(active=True).count(),
        )
        self.assertIn(
            ('title', self.project_1.title), response.data.get('results')[0].items()
        )
        self.assertNotIn('active', response.data.get('results')[-1].keys())
        self.assertNotIn('deleted_at', response.data.get('results')[-1].keys())

    def test_get_list_of_all_projects_as_admin(self):
        """
        Ensure we can get a list of ALL projects with ALL fields.
        """
        response = self.client.get(reverse('admin_project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')), Project.objects.all().count()
        )
        self.assertIn(
            ('title', self.project_1.title), response.data.get('results')[0].items()
        )
        self.assertIn('active', response.data.get('results')[-1].keys())
        self.assertIn('deleted_at', response.data.get('results')[-1].keys())

    def test_get_nonexistent_project(self):
        """
        Ensure we can't get non-existent project.
        """
        response = self.client.get(reverse('project-detail', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_project_as_admin(self):
        """
        Ensure we can't get non-existent project as admin.
        """
        response = self.client.get(reverse('admin_project-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_active_project(self):
        """
        Ensure we can get certain ACTIVE project object.
        """
        response = self.client.get(
            reverse('project-detail', kwargs={'pk': self.project_1.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.project_2.title)
        self.assertEqual(response.data.get('title'), self.project_1.title)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_get_inactive_project_as_admin(self):
        """
        Ensure we can get certain INACTIVE project.
        """
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.project_3.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.project_3.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_get_project_as_admin(self):
        """
        Ensure we can get certain project with ALL fields.
        """
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.project_1.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.project_2.title)
        self.assertEqual(response.data.get('title'), self.project_1.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_create_project(self, mock_send_join_to_project_notification):
        """
        Ensure we can create a new project and add new project participant.
        """
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

        mock_send_join_to_project_notification.assert_called_once()

    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_create_project_as_admin(self, mock_send_join_to_project_notification):
        """
        Ensure we can create a new project and add new project participant.
        """
        data = {
            'title': 'Test Project 3',
            'description': 'Description for the third test project.',
        }
        response = self.client.post(reverse('admin_project-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(Project.objects.filter(title='Test Project 3').exists())
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=response.data.get("project_pk")
            ).exists()
        )
        mock_send_join_to_project_notification.assert_called_once()

    def test_update_project(self):
        """
        Ensure we can update project object.
        """
        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': self.project_2.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(title='Test Project 2').exists())
        self.assertTrue(Project.objects.filter(title='Test Project 4').exists())

    def test_update_project_as_admin(self):
        """
        Ensure we can update project.
        """
        response = self.client.patch(
            reverse('admin_project-detail', kwargs={'pk': self.project_1.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(title='Test Project 1').exists())
        self.assertTrue(Project.objects.filter(title='Test Project 4').exists())

    def test_update_inactive_project_status_as_admin(self):
        """
        Ensure we can update 'active' field of project.
        """
        pk = self.project_3.project_pk
        response = self.client.put(
            reverse('admin_project_activation', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Project.objects.get(project_pk=pk).active)
        self.assertIsNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertTrue(Task.objects.get(project=self.project_3).active)

    def test_delete_project(self):
        """
        Ensure we can delete project and deactivate related tasks.
        """
        pk = self.project_2.project_pk
        response = self.client.delete(reverse('project-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.get(project_pk=pk).active)
        self.assertIsNotNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertFalse(Task.objects.get(project=self.project_2).active)

    def test_delete_project_as_admin(self):
        """
        Ensure we can delete project and deactivate related tasks.
        """
        pk = self.project_2.project_pk
        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.get(project_pk=pk).active)
        self.assertIsNotNone(Project.objects.get(project_pk=pk).deleted_at)
        self.assertFalse(Task.objects.get(project=self.project_2).active)


class TaskTests(APITestCase):
    def setUp(self):
        self.project_1 = Project.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.project_2 = Project.objects.create(
            title='Test Inactive Project',
            description='Description for the inactive test project.',
            active=False,
        )
        self.task_1 = Task.objects.create(
            title='Test Task 1',
            description='Description for the first test task.',
            status='open',
            project=self.project_1,
        )
        self.task_2 = Task.objects.create(
            title='Test Task 2',
            description='Description for the second test task.',
            status='in progress',
            executor_id=7,
            project=self.project_1,
        )
        self.task_3 = Task.objects.create(
            title='Test Inactive Task',
            description='Description for the inactive test task.',
            status='in progress',
            project=self.project_1,
            active=False,
            deleted_at=datetime.utcnow(),
        )
        self.task_4 = Task.objects.create(
            title='Test Inactive Task',
            description='Description for the inactive test task.',
            status='reopen',
            project=self.project_2,
            active=False,
        )

    def test_get_list_of_active_tasks(self):
        """
        Ensure we can get list of ACTIVE tasks.
        """
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            Task.objects.filter(active=True).count(),
        )
        self.assertIn(
            ('title', self.task_2.title), response.data.get('results')[-1].items()
        )
        self.assertNotIn('active', response.data.get('results')[-1].keys())
        self.assertNotIn('deleted_at', response.data.get('results')[-1].keys())

    def test_get_list_of_all_tasks_as_admin(self):
        """
        Ensure we can get list of ALL tasks with ALL fields.
        """
        response = self.client.get(reverse('admin_task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), Task.objects.all().count())
        self.assertIn(
            ('title', self.task_3.title), response.data.get('results')[-1].items()
        )
        self.assertIn('active', response.data.get('results')[-1].keys())
        self.assertIn('deleted_at', response.data.get('results')[-1].keys())

    def test_get_nonexistent_task(self):
        """
        Ensure we can't get non-existent task.
        """
        response = self.client.get(reverse('task-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_task_as_admin(self):
        """
        Ensure we can't get non-existent task.
        """
        response = self.client.get(reverse('admin_task-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_active_task(self):
        """
        Ensure we can get certain ACTIVE task object.
        """
        response = self.client.get(
            reverse('task-detail', kwargs={'pk': self.task_1.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.task_2.title)
        self.assertEqual(response.data.get('title'), self.task_1.title)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_get_inactive_task_as_admin(self):
        """
        Ensure we can get certain INACTIVE task.
        """
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.task_3.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.task_3.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_get_task_as_admin(self):
        """
        Ensure we can get certain task with ALL fields.
        """
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.task_1.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.task_2.title)
        self.assertEqual(response.data.get('title'), self.task_1.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_create_task(
        self,
        mock_send_subscription_on_task_notification,
        mock_send_join_to_project_notification,
    ):
        """
        Ensure we can create a new task and add a new task subscriber and new project participant.
        """
        data = {
            'title': 'Test Task 4',
            'description': 'Description for test task.',
            'project': self.project_1.project_pk,
            'status': 'reopened',
        }
        response = self.client.post(reverse('task-list'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())
        self.assertTrue(Task.objects.filter(title='Test Task 4').exists())
        self.assertTrue(
            TaskSubscriber.objects.filter(task=response.data.get("task_pk")).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(project=self.project_1).exists()
        )

        mock_send_subscription_on_task_notification.assert_called_once()
        mock_send_join_to_project_notification.assert_called_once()

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_create_task_as_admin(
        self,
        mock_send_subscription_on_task_notification,
        mock_send_join_to_project_notification,
    ):
        """
        Ensure we can create a new task and add a new task subscriber.
        """
        data = {
            'title': 'Test Task 5',
            'description': 'Description for test task.',
            'project': self.project_1.project_pk,
            'status': 'reopened',
        }
        response = self.client.post(reverse('admin_task-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(Task.objects.filter(title='Test Task 5').exists())
        self.assertTrue(
            TaskSubscriber.objects.filter(task=response.data.get("task_pk")).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(project=self.project_1).exists()
        )

        mock_send_subscription_on_task_notification.assert_called_once()
        mock_send_join_to_project_notification.assert_called_once()

    def test_update_task(self):
        """
        Ensure we can update task.
        """
        response = self.client.patch(
            reverse('task-detail', kwargs={'pk': self.task_1.task_pk}),
            {'title': 'New task title'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.filter(title=self.task_1.title).exists())
        self.assertTrue(Task.objects.filter(title='New task title').exists())

    def test_update_task_as_admin(self):
        """
        Ensure we can update task.
        """
        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': self.task_1.task_pk}),
            {'title': 'New Task title'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.filter(title=self.task_1.title).exists())
        self.assertTrue(Task.objects.filter(title='New Task title').exists())

    @patch('api.tasks.send_task_status_update_notification.delay')
    def test_update_task_status(self, mock_send_task_status_update_notification):
        """
        Ensure we can update task status.
        """
        response = self.client.patch(
            reverse('task_status_update', kwargs={'pk': self.task_1.task_pk}),
            {'status': 'closed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(task_pk=self.task_1.task_pk, status='open').exists()
        )
        self.assertTrue(
            Task.objects.filter(task_pk=self.task_1.task_pk, status='closed').exists()
        )

        mock_send_task_status_update_notification.assert_called_once()

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_add_task_executor(
        self,
        mock_send_subscription_on_task_notification,
        mock_send_join_to_project_notification,
    ):
        """
        Ensure we can add task executor and add new task subscription and new project participant.
        """
        response = self.client.patch(
            reverse('task_executor_update', kwargs={'pk': self.task_1.task_pk}),
            {'executor_id': 10},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(task_pk=self.task_1.task_pk, executor_id=None).exists()
        )
        self.assertTrue(
            Task.objects.filter(task_pk=self.task_1.task_pk, executor_id=10).exists()
        )
        self.assertTrue(
            TaskSubscriber.objects.filter(task=self.task_1, subscriber_id=10).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=self.task_1.project, participant_id=10
            ).exists()
        )

        mock_send_subscription_on_task_notification.assert_called_once()
        mock_send_join_to_project_notification.assert_called_once()

    def test_remove_task_executor(self):
        """
        Ensure we can remove task executor and remove him from task subscription.
        """

        response = self.client.patch(
            reverse('task_executor_update', kwargs={'pk': self.task_1.task_pk}),
            {'executor_id': None},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(task_pk=self.task_1.task_pk, executor_id=10).exists()
        )
        self.assertTrue(
            Task.objects.filter(task_pk=self.task_1.task_pk, executor_id=None).exists()
        )
        self.assertFalse(
            TaskSubscriber.objects.filter(task=self.task_1, subscriber_id=10).exists()
        )

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    @patch('api.tasks.send_join_to_project_notification.delay')
    def test_update_task_executor(
        self,
        mock_send_subscription_on_task_notification,
        mock_send_join_to_project_notification,
    ):
        """
        Ensure we can update task executor and remove old one from task subscription and add new one
        to project participants and task subscription.
        """

        response = self.client.patch(
            reverse('task_executor_update', kwargs={'pk': self.task_2.task_pk}),
            {'executor_id': 12},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Task.objects.filter(
                task_pk=self.task_2.task_pk, executor_id=self.task_2.executor_id
            ).exists()
        )
        self.assertTrue(
            Task.objects.filter(task_pk=self.task_2.task_pk, executor_id=12).exists()
        )
        self.assertFalse(
            TaskSubscriber.objects.filter(
                task=self.task_2, subscriber_id=self.task_2.executor_id
            ).exists()
        )
        self.assertTrue(
            TaskSubscriber.objects.filter(task=self.task_2, subscriber_id=12).exists()
        )
        self.assertTrue(
            ProjectParticipant.objects.filter(
                project=self.task_2.project, participant_id=12
            ).exists()
        )

        mock_send_subscription_on_task_notification.assert_called_once()
        mock_send_join_to_project_notification.assert_called_once()

    def test_delete_task(self):
        """
        Ensure we can delete task and related subscriptions.
        """
        pk = self.task_2.task_pk
        response = self.client.delete(reverse('task-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.get(task_pk=pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=pk).deleted_at)
        self.assertFalse(TaskSubscriber.objects.filter(task=self.task_2).exists())

    def test_delete_task_as_admin(self):
        """
        Ensure we can delete task and related subscriptions.
        """
        pk = self.task_1.task_pk
        response = self.client.delete(reverse('admin_task-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.get(task_pk=pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=pk).deleted_at)
        self.assertFalse(TaskSubscriber.objects.filter(task=self.task_1).exists())

    def test_update_inactive_task_status_as_admin(self):
        """
        Ensure we can update the 'active' field of a task.
        """
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': self.task_3.task_pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Task.objects.get(task_pk=self.task_3.task_pk).active)
        self.assertIsNone(Task.objects.get(task_pk=self.task_3.task_pk).deleted_at)

    def test_deactivate_task(self):
        """
        Ensure we can deactivate the task and the associated subscriptions will be deleted.
        """
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': self.task_2.task_pk}),
            {'active': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.get(task_pk=self.task_2.task_pk).active)
        self.assertIsNotNone(Task.objects.get(task_pk=self.task_2.task_pk).deleted_at)
        self.assertFalse(TaskSubscriber.objects.filter(task=self.task_2).exists())

    def test_availability_to_update_task_active_status(self):
        """
        Ensure we can only update the 'active' field of a task if its project is active.
        """
        response = self.client.put(
            reverse('admin_task_activation', kwargs={'pk': self.task_4.task_pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Task.objects.get(task_pk=self.task_4.task_pk).active)


class TaskSubscribersViewSetTests(APITestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Description for the test task.',
            status='open',
            project=self.project,
        )
        self.subscription_1 = TaskSubscriber.objects.create(
            task=self.task, subscriber_id=1
        )
        self.subscription_2 = TaskSubscriber.objects.create(
            task=self.task, subscriber_id=2
        )

    def test_get_subscribers_list(self):
        """
        Ensure we can get list of task subscribers.
        """
        response = self.client.get(reverse('task_subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            TaskSubscriber.objects.all().count(),
        )
        self.assertIn(
            ('task', self.task.task_pk), response.data.get('results')[-1].items()
        )
        self.assertIn(
            ('subscriber_id', self.subscription_2.subscriber_id),
            response.data.get('results')[-1].items(),
        )

    def test_get_nonexistent_subscription(self):
        """
        Ensure we can't get non-existent subscription.
        """
        response = self.client.get(
            reverse('task_subscription-detail', kwargs={'pk': 10})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_subscription(self):
        """
        Ensure we can get certain subscription.
        """
        response = self.client.get(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.task_subscriber_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('subscriber_id'), self.subscription_2.subscriber_id
        )
        self.assertEqual(
            response.data.get('subscriber_id'), self.subscription_1.subscriber_id
        )

    @patch('api.tasks.send_subscription_on_task_notification.delay')
    def test_create_subscription(self, mock_send_subscription_on_task_notification):
        """
        Ensure we can create a new subscription.
        """
        response = self.client.post(
            reverse('task_subscription-list'),
            {'task': self.task.task_pk, 'subscriber_id': 9},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        mock_send_subscription_on_task_notification.assert_called_once()

    def test_update_subscription(self):
        """
        Ensure we can't update subscription.
        """
        response = self.client.patch(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.task_subscriber_pk},
            ),
            {'subscriber_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_subscription(self):
        """
        Ensure we can't delete subscription.
        """
        response = self.client.delete(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.task_subscriber_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskAttachmentsViewSetTests(APITestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Description for the test task.',
            status='open',
            project=self.project,
        )
        self.attachment_1 = TasksAttachment.objects.create(
            task=self.task, attachment_id=1
        )
        self.attachment_2 = TasksAttachment.objects.create(
            task=self.task, attachment_id=2
        )

    def test_get_attachments_list(self):
        """
        Ensure we can get list of task attachments.
        """
        response = self.client.get(reverse('task_attachment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get('results')),
            TasksAttachment.objects.all().count(),
        )
        self.assertIn(
            ('task', self.task.task_pk), response.data.get('results')[-1].items()
        )
        self.assertIn(
            ('attachment_id', self.attachment_2.attachment_id),
            response.data.get('results')[-1].items(),
        )

    def test_get_nonexistent_attachment(self):
        """
        Ensure we can't get non-existent attachment.
        """
        response = self.client.get(
            reverse('task_attachment-detail', kwargs={'pk': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_attachment(self):
        """
        Ensure we can get certain attachment.
        """
        response = self.client.get(
            reverse(
                'task_attachment-detail',
                kwargs={'pk': self.attachment_1.task_attachment_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('attachment_id'), self.attachment_2.attachment_id
        )
        self.assertEqual(
            response.data.get('attachment_id'), self.attachment_1.attachment_id
        )

    def test_create_attachment(self):
        """
        Ensure we can create a new attachment.
        """
        response = self.client.post(
            reverse('task_attachment-list'),
            {'task': self.task.task_pk, 'attachment_id': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_attachment(self):
        """
        Ensure we can't update attachment.
        """
        response = self.client.patch(
            reverse(
                'task_attachment-detail',
                kwargs={'pk': self.attachment_1.task_attachment_pk},
            ),
            {'attachment_id': 6},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_attachment(self):
        """
        Ensure we can't delete attachment.
        """
        response = self.client.delete(
            reverse(
                'task_attachment-detail',
                kwargs={'pk': self.attachment_1.task_attachment_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectParticipantsViewSetTests(APITestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.participation_1 = ProjectParticipant.objects.create(
            project=self.project, participant_id=1
        )
        self.participation_2 = ProjectParticipant.objects.create(
            project=self.project, participant_id=2
        )

    def test_get_participants_list(self):
        """
        Ensure we can get list of project participations.
        """
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
        """
        Ensure we can't get non-existent participation.
        """
        response = self.client.get(
            reverse('project_participant-detail', kwargs={'pk': 10})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participation(self):
        """
        Ensure we can get certain participation.
        """
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
    def test_create_participation(self, mock_send_join_to_project_notification):
        """
        Ensure we can create a new participation.
        """
        response = self.client.post(
            reverse('project_participant-list'),
            {'project': self.project.project_pk, 'participant_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_join_to_project_notification.assert_called_once()

    def test_update_participation(self):
        """
        Ensure we can't update participation.
        """
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
        """
        Ensure we can't delete participation.
        """
        response = self.client.delete(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.project_participant_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
