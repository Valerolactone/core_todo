from datetime import datetime

from api.models import Project, ProjectParticipant, Task, TaskSubscriber


class UpdateTaskExecutorService:
    def __init__(self, instance: Task, new_executor_id: int):
        self.instance = instance
        self.new_executor_id = new_executor_id

    def _subscribe_executor_to_task(self):
        TaskSubscriber.objects.get_or_create(
            task=self.instance, subscriber_id=self.new_executor_id
        )
        ProjectParticipant.objects.get_or_create(
            project=self.instance.project, participant_id=self.new_executor_id
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


class ManageProjectService:
    def __init__(self, instance: Project, **kwargs):
        self.instance = instance
        if 'active_status' in kwargs:
            self.active_status = kwargs['active_status']
        if 'user_id' in kwargs:
            self.user_id = kwargs['user_id']

    def add_project_participant(self):
        ProjectParticipant.objects.get_or_create(
            project=self.instance, participant_id=self.user_id
        )

    def update_project_active_status(self):
        self.instance.deleted_at = None if self.active_status else datetime.utcnow()
        self.instance.active = self.active_status

        (
            Task.objects.filter(project=self.instance.project_pk).update(
                active=self.instance.active, deleted_at=None
            )
            if self.instance.active
            else Task.objects.filter(project=self.instance.project_pk).update(
                active=self.instance.active, deleted_at=datetime.utcnow()
            )
        )
        if not self.active_status:
            tasks = Task.objects.filter(project=self.instance)
            TaskSubscriber.objects.filter(task__in=tasks).delete()

    def deactivate_project(self):
        self.instance.active = False
        self.instance.deleted_at = datetime.utcnow()
        self.instance.save()

        Task.objects.filter(project=self.instance.project_pk).update(
            active=self.instance.active, deleted_at=datetime.utcnow()
        )
        tasks = Task.objects.filter(project=self.instance)
        TaskSubscriber.objects.filter(task__in=tasks).delete()


class ManageTaskService:
    def __init__(self, instance: Task, **kwargs):
        self.instance = instance
        if 'active_status' in kwargs:
            self.active_status = kwargs['active_status']
        if 'user_id' in kwargs:
            self.user_id = kwargs['user_id']

    def add_task_subscription(self):
        TaskSubscriber.objects.get_or_create(
            task=self.instance, subscriber_id=self.user_id
        )
        ProjectParticipant.objects.get_or_create(
            project=self.instance.project, participant_id=self.user_id
        )
        if self.instance.executor_id:
            TaskSubscriber.objects.get_or_create(
                task=self.instance, subscriber_id=self.instance.executor_id
            )
            ProjectParticipant.objects.get_or_create(
                project=self.instance.project, participant_id=self.instance.executor_id
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
