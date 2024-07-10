from django.db import models

TASK_STATUS = (
    ('open', 'Open'),
    ('in progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),
)


class ProjectModel(models.Model):
    project_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    logo = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']


class TaskModel(models.Model):
    task_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(choices=TASK_STATUS)
    executor_id = models.PositiveIntegerField(null=True, blank=True)
    executor_name = models.CharField(max_length=255, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            'title',
            'project',
        )


class TaskSubscribersModel(models.Model):
    subscription_pk = models.AutoField(primary_key=True, editable=False)
    task_id = models.ForeignKey(TaskModel, on_delete=models.CASCADE)
    task_status = models.CharField(choices=TASK_STATUS)
    subscriber_id = models.PositiveIntegerField()


class ProjectParticipantsModel(models.Model):
    participation_pk = models.AutoField(primary_key=True, editable=False)
    project_id = models.ForeignKey(ProjectModel, on_delete=models.CASCADE)
    participant_id = models.PositiveIntegerField()


class TasksAttachmentsModel(models.Model):
    attachment_pk = models.AutoField(primary_key=True, editable=False)
    task_id = models.ForeignKey(TaskModel, on_delete=models.CASCADE)
    attachment = models.URLField(max_length=200)
