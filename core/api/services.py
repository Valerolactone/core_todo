from datetime import datetime

from api.models import Project, ProjectParticipant, Task, TaskSubscriber
from api.tasks import (
    send_join_to_project_notification,
    send_subscription_on_task_notification,
)
from api.utils import get_email_for_notification


class NotificationService:
    def _notify_new_member(
        self,
        to_email,
        created_subscriber=None,
        task_title=None,
        created_participant=None,
        project_title=None,
    ):

        if created_subscriber:
            send_subscription_on_task_notification.delay(to_email, task_title)
        if created_participant:
            send_join_to_project_notification.delay(to_email, project_title)

    def add_to_watch_list(
        self, request, task: Task = None, project: Project = None, user_pk: int = None
    ):

        _, created_subscriber = (
            TaskSubscriber.objects.get_or_create(task=task, subscriber_id=user_pk)
            if task
            else None
        ), None
        _, created_participant = (
            ProjectParticipant.objects.get_or_create(
                project=project, participant_id=user_pk
            )
            if project
            else None
        ), None

        email_for_notification = (
            get_email_for_notification(request, user_pk)
            if created_subscriber or created_participant
            else None
        )

        if email_for_notification:
            self._notify_new_member(
                email_for_notification,
                created_subscriber=created_subscriber,
                task_title=task.title,
                created_participant=created_participant,
                project_title=project.title,
            )


class UpdateTaskExecutorService(NotificationService):
    def __init__(self, request, instance: Task, new_executor_id: int):
        self.request = request
        self.instance = instance
        self.new_executor_id = new_executor_id

    def _subscribe_executor_to_task(self):
        self.add_to_watch_list(
            request=self.request,
            task=self.instance,
            project=self.instance.project,
            user_pk=self.new_executor_id,
        )

    def _unsubscribe_executor_from_task(self):
        TaskSubscriber.objects.filter(
            task=self.instance, subscriber_id=self.instance.executor_id
        ).delete()

    def _update_subscription(self):
        self._unsubscribe_executor_from_task()
        self._subscribe_executor_to_task()

    def update_executor(self):
        if self.instance.executor_id is None:
            self._subscribe_executor_to_task()
        elif self.new_executor_id is None:
            self._unsubscribe_executor_from_task()
        else:
            self._update_subscription()


class ManageProjectService(NotificationService):
    def __init__(self, request, instance: Project, active_status=None, user_id=None):
        self.request = request
        self.instance = instance
        self.active_status = active_status
        self.user_id = user_id

    def add_project_participant(self):
        self.add_to_watch_list(
            request=self.request, project=self.instance, user_pk=self.user_id
        )

    def _activate_related_tasks(self):
        Task.objects.filter(project=self.instance).update(
            active=self.instance.active, deleted_at=None
        )

    def _deactivate_related_tasks(self):
        Task.objects.filter(project=self.instance).update(
            active=self.instance.active, deleted_at=datetime.utcnow()
        )
        tasks = Task.objects.filter(project=self.instance)
        TaskSubscriber.objects.filter(task__in=tasks).delete()

    def update_project_active_status(self):
        self.instance.deleted_at = None if self.active_status else datetime.utcnow()
        self.instance.active = self.active_status

        (
            self._activate_related_tasks()
            if self.instance.active
            else self._deactivate_related_tasks()
        )

    def deactivate_project(self):
        self.instance.active = False
        self.instance.deleted_at = datetime.utcnow()
        self.instance.save()

        self._deactivate_related_tasks()


class ManageTaskService(NotificationService):
    def __init__(self, request, instance: Task, active_status=None, user_id=None):
        self.request = request
        self.instance = instance
        self.active_status = active_status
        self.user_id = user_id

    def add_task_subscription(self):
        self.add_to_watch_list(
            request=self.request,
            task=self.instance,
            project=self.instance.project,
            user_pk=self.user_id,
        )

        if self.instance.executor_id:
            self.add_to_watch_list(
                request=self.request,
                task=self.instance,
                project=self.instance.project,
                user_pk=self.instance.executor_id,
            )

    def update_task_active_status(self):
        if self.instance.project.active:
            self.instance.deleted_at = None if self.active_status else datetime.utcnow()
            self.instance.active = self.active_status

        if not self.active_status:
            TaskSubscriber.objects.filter(task=self.instance).delete()

    def deactivate_task(self):
        self.instance.active = False
        self.instance.deleted_at = datetime.utcnow()
        self.instance.save()

        TaskSubscriber.objects.filter(task=self.instance).delete()
