from api.models import (
    Project,
    ProjectParticipant,
    Task,
    TasksAttachment,
    TaskSubscriber,
)
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_pk', 'title', 'description', 'logo_id', 'created_at')
        read_only_fields = ['created_at']


class AdminProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'project_pk',
            'title',
            'description',
            'logo_id',
            'created_at',
            'deleted_at',
            'active',
        )
        read_only_fields = ['created_at', 'deleted_at', 'active']


class AdminProjectActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_pk', 'title', 'deleted_at', 'active')
        read_only_fields = ['project_pk', 'title', 'deleted_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'task_pk',
            'title',
            'description',
            'status',
            'executor_id',
            'due_date',
            'created_at',
            'project',
        )
        read_only_fields = ['status', 'executor_id', 'created_at']


class AdminTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'task_pk',
            'title',
            'description',
            'status',
            'executor_id',
            'due_date',
            'created_at',
            'deleted_at',
            'active',
            'project',
        )
        read_only_fields = [
            'status',
            'executor_id',
            'created_at',
            'deleted_at',
            'active',
        ]


class AdminTaskActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('task_pk', 'title', 'deleted_at', 'active')
        read_only_fields = ['task_pk', 'title', 'deleted_at']


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('task_pk', 'title', 'status')
        read_only_fields = ['task_pk', 'title']


class TaskExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('task_pk', 'title', 'executor_id')
        read_only_fields = ['task_pk', 'title']


class TaskSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubscriber
        fields = ('task_subscriber_pk', 'task', 'subscriber_id')


class ProjectParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectParticipant
        fields = ('project_participant_pk', 'project', 'participant_id')


class TasksAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksAttachment
        fields = ('task_attachment_pk', 'task', 'attachment_id')
