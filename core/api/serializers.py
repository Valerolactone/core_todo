from datetime import datetime

from rest_framework import serializers

from .models import (
    ProjectModel,
    ProjectParticipantsModel,
    TaskModel,
    TasksAttachmentsModel,
    TaskSubscribersModel,
)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectModel
        fields = ('project_pk', 'title', 'description', 'logo_id', 'created_at')
        read_only_fields = ['created_at']


class AdminProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectModel
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
        model = ProjectModel
        fields = ('project_pk', 'title', 'deleted_at', 'active')
        read_only_fields = ['project_pk', 'title', 'deleted_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = (
            'task_pk',
            'title',
            'description',
            'status',
            'executor_id',
            'executor_name',
            'due_date',
            'created_at',
            'project_id',
        )
        read_only_fields = ['created_at', 'project']


class AdminTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = (
            'task_pk',
            'title',
            'description',
            'status',
            'executor_id',
            'executor_name',
            'due_date',
            'created_at',
            'deleted_at',
            'active',
            'project_id',
        )
        read_only_fields = ['created_at', 'deleted_at', 'project', 'active']


class AdminTaskActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = ('task_pk', 'title', 'deleted_at', 'active')
        read_only_fields = ['task_pk', 'title', 'deleted_at']


class TaskSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubscribersModel
        fields = ('subscription_pk', 'task_id', 'task_status', 'subscriber_id')


class ProjectParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectParticipantsModel
        fields = ('participation_pk', 'project_id', 'participant_id')


class TasksAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksAttachmentsModel
        fields = ('attachment_pk', 'task_id', 'attachment_id')
