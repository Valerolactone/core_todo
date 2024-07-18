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
        read_only_fields = ['created_at', 'deleted_at']

    def update(self, instance, validated_data):
        self.fields['deleted_at'].read_only = False

        if instance.active is not self.validated_data.get('active'):
            instance.deleted_at = (
                None if self.validated_data.get('active') else datetime.utcnow()
            )

        instance = super(AdminProjectSerializer, self).update(instance, validated_data)
        instance.save()

        self.fields['deleted_at'].read_only = True

        return instance


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
        read_only_fields = ['created_at', 'deleted_at', 'project']

    def update(self, instance, validated_data):
        self.fields['deleted_at'].read_only = False

        if instance.active is not self.validated_data.get('active'):
            instance.deleted_at = (
                None if self.validated_data.get('active') else datetime.utcnow()
            )

        instance = super(AdminTaskSerializer, self).update(instance, validated_data)
        instance.save()

        self.fields['deleted_at'].read_only = True

        return instance


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
