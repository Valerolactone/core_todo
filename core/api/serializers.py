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
        exclude = ('deleted_at', 'active')
        read_only_fields = ['project_pk', 'created_at']


class AdminProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectModel
        fields = '__all__'
        read_only_fields = ['project_pk', 'created_at', 'deleted_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        exclude = ('deleted_at', 'active')
        read_only_fields = ['task_pk', 'created_at', 'project']


class AdminTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = '__all__'
        read_only_fields = ['task_pk', 'created_at', 'deleted_at', 'project']


class TaskSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubscribersModel
        fields = '__all__'


class ProjectParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectParticipantsModel
        fields = '__all__'


class TasksAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksAttachmentsModel
        fields = '__all__'
