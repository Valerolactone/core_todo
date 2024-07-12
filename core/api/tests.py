from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ProjectModel


class ProjectTests(APITestCase):
    fixtures = ['projects.json']

    def test_get_projects_list(self):
        """
        Ensure we can get list of project objects.
        """
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_project(self):
        """
        Ensure we can get certain project object.
        """
        response = self.client.get(reverse('project-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), 'First project for test.')

    def test_create_project(self):
        """
        Ensure we can create a new project object.
        """
        data = {'title': 'Test Project', 'description': 'Description for test project.'}
        response = self.client.post(reverse('project-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('title'), 'Test Project')
        self.assertEqual(
            response.data.get('description'), 'Description for test project.'
        )
        self.assertEqual(ProjectModel.objects.filter(active=True).count(), 3)

    def test_update_project(self):
        """
        Ensure we can update project object.
        """
        data = {'title': 'Updated second project for test.'}
        response = self.client.patch(
            reverse('project-detail', kwargs={'pk': 2}), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data.get('title'), 'Updated second project for test.')
        self.assertEqual(
            response.data.get('description'),
            'Description for the second project for test.',
        )

    def test_delete_project(self):
        """
        Ensure we can delete project object.
        """
        response = self.client.delete(reverse('project-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'Status': 'Success',
                'Message': "Record about project First project for test. deleted.",
            },
        )
        self.assertEqual(ProjectModel.objects.get(project_pk=1).active, False)


'''class TaskProjectTests(APITestCase):
    fixtures = ['projects.json', 'tasks.json']

    def test_get_tasks_list(self):
        """
        Ensure we can get list of task objects.
        """
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_task(self):
        """
        Ensure we can get certain task object.
        """
        response = self.client.get(reverse('task-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), 'Test task1')

    def test_create_task(self):
        """
        Ensure we can create a new task object.
        """
        data = {'title': 'Test Task', 'description': 'Description for test task.', 'project': 1,
                'status': 'open'}
        response = self.client.post(reverse('task-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('title'), 'Test Task')
        self.assertEqual(response.data.get('status'), 'open')
        self.assertEqual(TaskModel.objects.filter(active=True).count(), 3)

    def test_update_project(self):
        """
        Ensure we can update task object.
        """
        data = {'title': 'Updated second task for test.'}
        response = self.client.patch(reverse('task-detail', kwargs={'pk': 2}), data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data.get('title'), 'Updated second task for test.')
        self.assertEqual(response.data.get('description'), 'Description for task2.')

    def test_delete_project(self):
        """
        Ensure we can delete task object.
        """
        response = self.client.delete(reverse('task-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'Status': 'Success', 'Message': f"Record about task Test task1 deleted."})
        self.assertEqual(TaskModel.objects.get(task_pk=1).active, False)
'''


class TaskSubscribersTests(APITestCase):
    fixtures = ['projects.json', 'tasks.json', 'task_subscribers.json']

    def test_get_subscribers_list(self):
        """
        Ensure we can get list of task subscriber objects.
        """
        response = self.client.get(reverse('task_subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_subscription(self):
        """
        Ensure we can get certain subscription object.
        """
        response = self.client.get(
            reverse('task_subscription-detail', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('task_id'), 1)
        self.assertEqual(response.data.get('subscriber_id'), 2)


class TaskAttachmentsTests(APITestCase):
    fixtures = ['projects.json', 'tasks.json', 'task_attachments.json']

    def test_get_attachments_list(self):
        """
        Ensure we can get list of task attachment objects.
        """
        response = self.client.get(reverse('task_attachment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_attachment(self):
        """
        Ensure we can get certain attachment object.
        """
        response = self.client.get(reverse('task_attachment-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('task_id'), 1)
        self.assertEqual(
            response.data.get('attachment'),
            "http://127.0.0.1:8000/admin/api/tasksattachmentsmodel/add/",
        )


class ProjectParticipantsTests(APITestCase):
    fixtures = ['projects.json', 'project_participants.json']

    def test_get_participants_list(self):
        """
        Ensure we can get list of project participant objects.
        """
        response = self.client.get(reverse('project_participant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_participation(self):
        """
        Ensure we can get certain participation object.
        """
        response = self.client.get(
            reverse('project_participant-detail', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('project_id'), 1)
        self.assertEqual(response.data.get('participant_id'), 1)
