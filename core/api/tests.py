from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    ProjectModel,
    ProjectParticipantsModel,
    TaskModel,
    TasksAttachmentsModel,
    TaskSubscribersModel,
)


class ProjectViewSetTests(APITestCase):
    def setUp(self):
        self.project_1 = ProjectModel.objects.create(
            title='Test Project 1',
            description='Description for the first test project.',
        )
        self.project_2 = ProjectModel.objects.create(
            title='Test Project 2',
            description='Description for the second test project.',
        )
        self.project_3 = ProjectModel.objects.create(
            title='Test Inactive Project',
            description='Description for the inactive test project.',
            active=False,
        )

    def test_get_projects_list(self):
        """
        Ensure we can get list of active project objects.
        """
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), ProjectModel.objects.filter(active=True).count()
        )
        self.assertIn(('title', self.project_1.title), response.data[-1].items())
        self.assertNotIn('active', response.data[-1].keys())
        self.assertNotIn('deleted_at', response.data[-1].keys())

    def test_get_nonexistent_project(self):
        """
        Ensure we can't get non-existent project object.
        """
        response = self.client.get(reverse('project-detail', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project(self):
        """
        Ensure we can get certain project object.
        """
        response = self.client.get(
            reverse('project-detail', kwargs={'pk': self.project_1.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.project_2.title)
        self.assertEqual(response.data.get('title'), self.project_1.title)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_create_project(self):
        """
        Ensure we can create a new project object.
        """
        data = {
            'title': 'Test Project 3',
            'description': 'Description for the third test project.',
        }
        response = self.client.post(reverse('project-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())
        self.assertTrue(ProjectModel.objects.filter(title='Test Project 3').exists())

    def test_update_project(self):
        """
        Ensure we can update project object.
        """
        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': self.project_2.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(ProjectModel.objects.filter(title='Test Project 2').exists())
        self.assertTrue(ProjectModel.objects.filter(title='Test Project 4').exists())

    def test_delete_project(self):
        """
        Ensure we can delete project object.
        """
        pk = self.project_2.project_pk
        response = self.client.delete(reverse('project-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'Status': 'Success',
                'Message': "Record about project Test Project 2 deleted.",
            },
        )
        self.assertFalse(ProjectModel.objects.get(project_pk=pk).active)
        self.assertIsNotNone(ProjectModel.objects.get(project_pk=pk).deleted_at)

    def test_not_shown_deleted_project(self):
        """
        Ensure that deleted projects are not displayed.
        """
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for obj in response.data:
            self.assertNotIn(('active', False), obj.items())


class AdminProjectViewSetTests(APITestCase):
    def setUp(self):
        self.project_1 = ProjectModel.objects.create(
            title='Test Project 1',
            description='Description for the first test project.',
        )
        self.project_2 = ProjectModel.objects.create(
            title='Test Project 2',
            description='Description for the second test project.',
        )
        self.project_3 = ProjectModel.objects.create(
            title='Test Inactive Project',
            description='Description for the inactive test project.',
            active=False,
        )

    def test_get_projects_list(self):
        """
        Ensure we can get list of all project objects with all fields.
        """
        response = self.client.get(reverse('admin_project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), ProjectModel.objects.all().count())
        self.assertIn(('title', self.project_1.title), response.data[-1].items())
        self.assertIn('active', response.data[-1].keys())
        self.assertIn('deleted_at', response.data[-1].keys())

    def test_get_nonexistent_project(self):
        """
        Ensure we can't get non-existent project object.
        """
        response = self.client.get(reverse('admin_project-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_project(self):
        """
        Ensure we can get project object with false active field.
        """
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.project_3.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.project_3.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_get_project(self):
        """
        Ensure we can get certain project object with all fields.
        """
        response = self.client.get(
            reverse('admin_project-detail', kwargs={'pk': self.project_1.project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.project_2.title)
        self.assertEqual(response.data.get('title'), self.project_1.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_create_project(self):
        """
        Ensure we can create a new project object.
        """
        data = {
            'title': 'Test Project 3',
            'description': 'Description for the third test project.',
        }
        response = self.client.post(reverse('admin_project-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(ProjectModel.objects.filter(title='Test Project 3').exists())

    def test_update_project(self):
        """
        Ensure we can update project object.
        """
        response = self.client.patch(
            reverse('admin_project-detail', kwargs={'pk': self.project_1.project_pk}),
            {'title': 'Test Project 4'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(ProjectModel.objects.filter(title='Test Project 1').exists())
        self.assertTrue(ProjectModel.objects.filter(title='Test Project 4').exists())

    def test_delete_project(self):
        """
        Ensure we can delete project object.
        """
        pk = self.project_2.project_pk
        response = self.client.delete(
            reverse('admin_project-detail', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'Status': 'Success',
                'Message': "Record about project Test Project 2 deleted.",
            },
        )
        self.assertFalse(ProjectModel.objects.get(project_pk=pk).active)
        self.assertIsNotNone(ProjectModel.objects.get(project_pk=pk).deleted_at)

    def test_update_inactive_project(self):
        """
        Ensure we can update 'active' field of project object.
        """
        pk = self.project_3.project_pk
        response = self.client.patch(
            reverse('admin_project-detail', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(ProjectModel.objects.get(project_pk=pk).active)
        self.assertIsNone(ProjectModel.objects.get(project_pk=pk).deleted_at)


class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.project = ProjectModel.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task_1 = TaskModel.objects.create(
            title='Test Task 1',
            description='Description for the first test task.',
            status='open',
            project_id=self.project,
        )
        self.task_2 = TaskModel.objects.create(
            title='Test Task 2',
            description='Description for the second test task.',
            status='in progress',
            project_id=self.project,
        )
        self.task_3 = TaskModel.objects.create(
            title='Test Inactive Task',
            description='Description for the inactive test task.',
            status='in progress',
            project_id=self.project,
            active=False,
        )

    def test_get_tasks_list(self):
        """
        Ensure we can get list of active task objects.
        """
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), TaskModel.objects.filter(active=True).count()
        )
        self.assertIn(('title', self.task_2.title), response.data[-1].items())
        self.assertNotIn('active', response.data[-1].keys())
        self.assertNotIn('deleted_at', response.data[-1].keys())

    def test_get_nonexistent_task(self):
        """
        Ensure we can't get non-existent task object.
        """
        response = self.client.get(reverse('task-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_task(self):
        """
        Ensure we can get certain task object.
        """
        response = self.client.get(
            reverse('task-detail', kwargs={'pk': self.task_1.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.task_2.title)
        self.assertEqual(response.data.get('title'), self.task_1.title)
        self.assertNotIn('active', response.data.keys())
        self.assertNotIn('deleted_at', response.data.keys())

    def test_create_task(self):
        """
        Ensure we can create a new task object.
        """
        data = {
            'title': 'Test Task 4',
            'description': 'Description for test task.',
            'project_id': self.project.project_pk,
            'status': 'reopened',
        }
        response = self.client.post(reverse('task-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(TaskModel.objects.filter(title='Test Task 4').exists())

    def test_update_task(self):
        """
        Ensure we can update task object.
        """
        response = self.client.patch(
            reverse('task-detail', kwargs={'pk': self.task_1.task_pk}),
            {'status': 'closed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(TaskModel.objects.filter(status='open').exists())
        self.assertTrue(TaskModel.objects.filter(status='closed').exists())

    def test_delete_task(self):
        """
        Ensure we can delete task object.
        """
        pk = self.task_2.task_pk
        response = self.client.delete(reverse('task-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'Status': 'Success',
                'Message': "Record about task Test Task 2 deleted.",
            },
        )
        self.assertFalse(TaskModel.objects.get(task_pk=pk).active)
        self.assertIsNotNone(TaskModel.objects.get(task_pk=pk).deleted_at)

    def test_not_shown_deleted_task(self):
        """
        Ensure that deleted task are not displayed.
        """
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for obj in response.data:
            self.assertNotIn(('active', False), obj.items())


class AdminTaskViewSetTests(APITestCase):
    def setUp(self):
        self.project = ProjectModel.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task_1 = TaskModel.objects.create(
            title='Test Task 1',
            description='Description for the first test task.',
            status='open',
            project_id=self.project,
        )
        self.task_2 = TaskModel.objects.create(
            title='Test Task 2',
            description='Description for the second test task.',
            status='in progress',
            project_id=self.project,
        )
        self.task_3 = TaskModel.objects.create(
            title='Test Inactive Task',
            description='Description for the inactive test task.',
            status='in progress',
            project_id=self.project,
            active=False,
        )

    def test_get_tasks_list(self):
        """
        Ensure we can get list of active task objects.
        """
        response = self.client.get(reverse('admin_task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), TaskModel.objects.all().count())
        self.assertIn(('title', self.task_3.title), response.data[-1].items())
        self.assertIn('active', response.data[-1].keys())
        self.assertIn('deleted_at', response.data[-1].keys())

    def test_get_nonexistent_task(self):
        """
        Ensure we can't get non-existent task object.
        """
        response = self.client.get(reverse('admin_task-detail', kwargs={'pk': 5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_task(self):
        """
        Ensure we can get task object with false active field.
        """
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.task_3.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), self.task_3.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_get_task(self):
        """
        Ensure we can get certain task object.
        """
        response = self.client.get(
            reverse('admin_task-detail', kwargs={'pk': self.task_1.task_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('title'), self.task_2.title)
        self.assertEqual(response.data.get('title'), self.task_1.title)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())

    def test_create_task(self):
        """
        Ensure we can create a new task object.
        """
        data = {
            'title': 'Test Task 4',
            'description': 'Description for test task.',
            'project_id': self.project.project_pk,
            'status': 'reopened',
        }
        response = self.client.post(reverse('admin_task-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('active', response.data.keys())
        self.assertIn('deleted_at', response.data.keys())
        self.assertTrue(TaskModel.objects.filter(title='Test Task 4').exists())

    def test_update_task(self):
        """
        Ensure we can update task object.
        """
        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': self.task_1.task_pk}),
            {'status': 'closed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(TaskModel.objects.filter(status='open').exists())
        self.assertTrue(TaskModel.objects.filter(status='closed').exists())

    def test_delete_task(self):
        """
        Ensure we can delete task object.
        """
        pk = self.task_2.task_pk
        response = self.client.delete(reverse('admin_task-detail', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'Status': 'Success',
                'Message': "Record about task Test Task 2 deleted.",
            },
        )
        self.assertFalse(TaskModel.objects.get(task_pk=pk).active)
        self.assertIsNotNone(TaskModel.objects.get(task_pk=pk).deleted_at)

    def test_update_inactive_task(self):
        """
        Ensure we can update 'active' field of task object.
        """
        pk = self.task_3.task_pk
        response = self.client.patch(
            reverse('admin_task-detail', kwargs={'pk': pk}),
            {'active': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(TaskModel.objects.get(task_pk=pk).active)
        self.assertIsNone(TaskModel.objects.get(task_pk=pk).deleted_at)


class TaskSubscribersViewSetTests(APITestCase):
    def setUp(self):
        self.project = ProjectModel.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task = TaskModel.objects.create(
            title='Test Task',
            description='Description for the test task.',
            status='open',
            project_id=self.project,
        )
        self.subscription_1 = TaskSubscribersModel.objects.create(
            task_id=self.task, task_status=self.task.status, subscriber_id=1
        )
        self.subscription_2 = TaskSubscribersModel.objects.create(
            task_id=self.task, task_status=self.task.status, subscriber_id=2
        )

    def test_get_subscribers_list(self):
        """
        Ensure we can get list of task subscriber objects.
        """
        response = self.client.get(reverse('task_subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), TaskSubscribersModel.objects.all().count())
        self.assertIn(('task_id', self.task.task_pk), response.data[-1].items())
        self.assertIn(
            ('subscriber_id', self.subscription_2.subscriber_id),
            response.data[-1].items(),
        )

    def test_get_nonexistent_subscription(self):
        """
        Ensure we can't get non-existent subscription object.
        """
        response = self.client.get(
            reverse('task_subscription-detail', kwargs={'pk': 10})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_subscription(self):
        """
        Ensure we can get certain subscription object.
        """
        response = self.client.get(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.subscription_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('subscriber_id'), self.subscription_2.subscriber_id
        )
        self.assertEqual(
            response.data.get('subscriber_id'), self.subscription_1.subscriber_id
        )

    def test_create_subscription(self):
        """
        Ensure we can't create a new subscription object.
        """
        response = self.client.post(
            reverse('task_subscription-list'),
            {'project_id': self.project.project_pk, 'subscriber_id': 9},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_subscription(self):
        """
        Ensure we can't update subscription object.
        """
        response = self.client.patch(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.subscription_pk},
            ),
            {'subscriber_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_subscription(self):
        """
        Ensure we can't delete subscription object.
        """
        response = self.client.delete(
            reverse(
                'task_subscription-detail',
                kwargs={'pk': self.subscription_1.subscription_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskAttachmentsViewSetTests(APITestCase):
    def setUp(self):
        self.project = ProjectModel.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.task = TaskModel.objects.create(
            title='Test Task',
            description='Description for the test task.',
            status='open',
            project_id=self.project,
        )
        self.attachment_1 = TasksAttachmentsModel.objects.create(
            task_id=self.task, attachment_id=1
        )
        self.attachment_2 = TasksAttachmentsModel.objects.create(
            task_id=self.task, attachment_id=2
        )

    def test_get_attachments_list(self):
        """
        Ensure we can get list of task attachment objects.
        """
        response = self.client.get(reverse('task_attachment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), TasksAttachmentsModel.objects.all().count()
        )
        self.assertIn(('task_id', self.task.task_pk), response.data[-1].items())
        self.assertIn(
            ('attachment_id', self.attachment_2.attachment_id),
            response.data[-1].items(),
        )

    def test_get_nonexistent_attachment(self):
        """
        Ensure we can't get non-existent attachment object.
        """
        response = self.client.get(
            reverse('task_attachment-detail', kwargs={'pk': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_attachment(self):
        """
        Ensure we can get certain attachment object.
        """
        response = self.client.get(
            reverse(
                'task_attachment-detail', kwargs={'pk': self.attachment_1.attachment_pk}
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
        Ensure we can't create a new attachment object.
        """
        response = self.client.post(
            reverse('task_attachment-list'),
            {'task_id': self.task.task_pk, 'attachment_id': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_attachment(self):
        """
        Ensure we can't update attachment object.
        """
        response = self.client.patch(
            reverse(
                'task_attachment-detail', kwargs={'pk': self.attachment_1.attachment_pk}
            ),
            {'attachment_id': 6},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_attachment(self):
        """
        Ensure we can't delete attachment object.
        """
        response = self.client.delete(
            reverse(
                'task_attachment-detail', kwargs={'pk': self.attachment_1.attachment_pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProjectParticipantsViewSetTests(APITestCase):
    def setUp(self):
        self.project = ProjectModel.objects.create(
            title='Test Project', description='Description for the test project.'
        )
        self.participation_1 = ProjectParticipantsModel.objects.create(
            project_id=self.project, participant_id=1
        )
        self.participation_2 = ProjectParticipantsModel.objects.create(
            project_id=self.project, participant_id=2
        )

    def test_get_participants_list(self):
        """
        Ensure we can get list of project participation objects.
        """
        response = self.client.get(reverse('project_participant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), ProjectParticipantsModel.objects.all().count()
        )
        self.assertIn(
            ('project_id', self.project.project_pk), response.data[-1].items()
        )
        self.assertIn(
            ('participant_id', self.participation_2.participant_id),
            response.data[-1].items(),
        )

    def test_get_nonexistent_participation(self):
        """
        Ensure we can't get non-existent participation object.
        """
        response = self.client.get(
            reverse('project_participant-detail', kwargs={'pk': 10})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participation(self):
        """
        Ensure we can get certain participation object.
        """
        response = self.client.get(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.participation_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            response.data.get('participant_id'), self.participation_2.participant_id
        )
        self.assertEqual(
            response.data.get('participant_id'), self.participation_1.participant_id
        )

    def test_create_participation(self):
        """
        Ensure we can't create a new participation object.
        """
        response = self.client.post(
            reverse('project_participant-list'),
            {'project_id': self.project.project_pk, 'participant_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_participation(self):
        """
        Ensure we can't update participation object.
        """
        response = self.client.patch(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.participation_pk},
            ),
            {'participant_id': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_participation(self):
        """
        Ensure we can't delete participation object.
        """
        response = self.client.delete(
            reverse(
                'project_participant-detail',
                kwargs={'pk': self.participation_1.participation_pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
