from django.db import models


class Project(models.Model):
    project_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    logo_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)


class Task(models.Model):
    OPEN = 'open'
    IN_PROGRESS = 'in progress'
    RESOLVED = 'resolved'
    REOPENED = 'reopened'
    CLOSED = 'closed'
    TASK_STATUS = (
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED, 'Resolved'),
        (REOPENED, 'Reopened'),
        (CLOSED, 'Closed'),
    )
    task_pk = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(choices=TASK_STATUS, default=OPEN)
    executor_id = models.PositiveIntegerField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deadline_notified = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'title',
            'project',
        )


class TaskSubscriber(models.Model):
    task_subscriber_pk = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subscriber_id = models.PositiveIntegerField()


class ProjectParticipant(models.Model):
    project_participant_pk = models.AutoField(primary_key=True, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    participant_id = models.PositiveIntegerField()


class TasksAttachment(models.Model):
    task_attachment_pk = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    attachment_id = models.PositiveIntegerField()
