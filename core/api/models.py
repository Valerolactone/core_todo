from django.db import models

TASK_STATUS = (
    ('open', 'Open'),
    ('in progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),
)


class Project(models.Model):
    project_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    logo_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)


class Task(models.Model):
    task_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(choices=TASK_STATUS, default='open')
    executor_id = models.PositiveIntegerField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            'title',
            'project',
        )


class TaskSubscribers(models.Model):
    task_subscribers_pk = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subscriber_id = models.PositiveIntegerField()


class ProjectParticipants(models.Model):
    project_participants_pk = models.AutoField(primary_key=True, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    participant_id = models.PositiveIntegerField()


class TasksAttachments(models.Model):
    task_attachments_pk = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    attachment_id = models.PositiveIntegerField()
