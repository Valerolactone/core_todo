from datetime import datetime
from typing import Tuple

from .models import Project, ProjectParticipants, Task, TaskSubscribers


class UpdateTaskExecutorService:
    def __init__(self, instance: Task, new_executor: int):
        self.instance = instance
        self.new_executor = new_executor

    def _set_executor_id(self):
        TaskSubscribers.objects.get_or_create(
            task=self.instance, subscriber_id=self.new_executor
        )
        ProjectParticipants.objects.get_or_create(
            project=self.instance.project, participant_id=self.new_executor
        )

    def _unsubscribe_executor_from_task(self):
        TaskSubscribers.objects.filter(
            task=self.instance, subscriber_id=self.instance.executor_id
        ).delete()

    def _update_executor_id(self):
        subscription = TaskSubscribers.objects.get(
            task=self.instance, subscriber_id=self.instance.executor_id
        )
        participation = ProjectParticipants.objects.get(
            project=self.instance.project.project_pk,
            participant_id=self.instance.executor_id,
        )
        subscription.subscriber_id = self.new_executor
        participation.participant_id = self.new_executor
        subscription.save()
        participation.save()

    def execute(self):
        if self.instance.executor_id is None:
            self._set_executor_id()
        elif self.new_executor is None:
            self._unsubscribe_executor_from_task()
        else:
            self._update_executor_id()


class UpdateTaskStatusService:
    def __init__(self, instance: Task, new_status: str):
        self.instance = instance
        self.new_status = new_status

    def _update_task_status(self):
        task = Task.objects.get(task_pk=self.instance.task_pk)
        task.status = self.new_status
        task.save()

    def execute(self):
        self._update_task_status()


class UpdateProjectActiveStatusService:
    def __init__(self, instance: Project, active_status: bool):
        self.instance = instance
        self.active_status = active_status

    def _update_active_status(self):
        self.instance.deleted_at = None if self.active_status else datetime.utcnow()
        self.instance.active = self.active_status

    def execute(self):
        self._update_active_status()


class UpdateTaskActiveStatusService:
    def __init__(self, instance: Task, active_status: bool):
        self.instance = instance
        self.active_status = active_status

    def _update_active_status(self):
        if self.instance.project.active:
            self.instance.deleted_at = None if self.active_status else datetime.utcnow()
            self.instance.active = self.active_status

    def execute(self):
        self._update_active_status()


class CreateProjectParticipantService:
    def __init__(self, instance: Project, user_id: int):
        self.instance = instance
        self.user_id = user_id

    def _create_project_participant(self):
        ProjectParticipants.objects.get_or_create(
            project=self.instance, participant_id=self.user_id
        )

    def execute(self):
        self._create_project_participant()


class UpdateStatusForRelatedTasks:
    def __init__(self, instance: Project):
        self.instance = instance

    def _update_related_tasks_status(self):
        (
            Task.objects.filter(project=self.instance.project_pk).update(
                active=self.instance.active, deleted_at=None
            )
            if self.instance.active
            else Task.objects.filter(project=self.instance.project_pk).update(
                active=self.instance.active, deleted_at=datetime.utcnow()
            )
        )

    def execute(self):
        self._update_related_tasks_status()


class CreateTaskSubscriberService:
    def __init__(self, instance: Task, user_id: int):
        self.instance = instance
        self.user_id = user_id

    def _create_task_subscriber(self):
        TaskSubscribers.objects.get_or_create(
            task=self.instance, subscriber_id=self.user_id
        )
        if self.instance.executor_id:
            TaskSubscribers.objects.get_or_create(
                task=self.instance, subscriber_id=self.instance.executor_id
            )
            ProjectParticipants.objects.get_or_create(
                project=self.instance.project, participant_id=self.instance.executor_id
            )

    def execute(self):
        self._create_task_subscriber()


class DeleteTaskSubscriptionsService:
    def __init__(self, instance: Task):
        self.instance = instance

    def _delete_task_subscriptions(self):
        TaskSubscribers.objects.filter(task=self.instance).delete()

    def execute(self):
        self._delete_task_subscriptions()
