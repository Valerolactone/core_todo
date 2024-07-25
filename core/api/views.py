from datetime import datetime

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from .models import (
    Project,
    ProjectParticipants,
    Task,
    TasksAttachments,
    TaskSubscribers,
)
from .serializers import (
    AdminProjectActivationSerializer,
    AdminProjectSerializer,
    AdminTaskActivationSerializer,
    AdminTaskSerializer,
    ProjectParticipantsSerializer,
    ProjectSerializer,
    TaskExecutorSerializer,
    TasksAttachmentsSerializer,
    TaskSerializer,
    TaskStatusSerializer,
    TaskSubscribersSerializer,
)
from .services import (
    CreateProjectParticipantService,
    CreateTaskSubscriberService,
    DeleteTaskSubscriptionsService,
    UpdateProjectActiveStatusService,
    UpdateStatusForRelatedTasks,
    UpdateTaskActiveStatusService,
    UpdateTaskExecutorService,
    UpdateTaskStatusService,
)


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(active=True)

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        instance = serializer.save()
        user_id = 1
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        project_participation_service = CreateProjectParticipantService(
            instance, user_id
        )
        project_participation_service.execute()

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        status_update_service = UpdateStatusForRelatedTasks(instance)
        status_update_service.execute()


class AdminProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminProjectSerializer

    def get_queryset(self):
        return Project.objects.all()

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        instance = serializer.save()
        user_id = 1
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        project_participation_service = CreateProjectParticipantService(
            instance, user_id
        )
        project_participation_service.execute()

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        status_update_service = UpdateStatusForRelatedTasks(instance)
        status_update_service.execute()


class AdminProjectActivationView(UpdateAPIView):
    serializer_class = AdminProjectActivationSerializer

    def get_queryset(self):
        return Project.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        active_status = serializer.validated_data.get('active')

        if instance.active == active_status:
            return Response(serializer.data)

        activation_service = UpdateProjectActiveStatusService(instance, active_status)
        activation_service.execute()

        status_update_service = UpdateStatusForRelatedTasks(instance)
        status_update_service.execute()

        self.perform_update(serializer)

        return Response(serializer.data)


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['title', 'status']
    ordering_fields = ['title', 'created_at']

    def get_queryset(self):
        return Task.objects.filter(active=True)

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        instance = serializer.save()
        user_id = 1
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        task_subscription_serviced = CreateTaskSubscriberService(instance, user_id)
        project_participation_service = CreateProjectParticipantService(
            instance.project, user_id
        )
        task_subscription_serviced.execute()
        project_participation_service.execute()

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        delete_task_subscriptions_service = DeleteTaskSubscriptionsService(instance)
        delete_task_subscriptions_service.execute()


class AdminTaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdminTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['title', 'status']
    ordering_fields = ['title', 'created_at']

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        instance = serializer.save()
        user_id = 1
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        task_subscription_serviced = CreateTaskSubscriberService(instance, user_id)
        project_participation_service = CreateProjectParticipantService(
            instance.project, user_id
        )
        task_subscription_serviced.execute()
        project_participation_service.execute()

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        delete_task_subscriptions_service = DeleteTaskSubscriptionsService(instance)
        delete_task_subscriptions_service.execute()


class AdminTaskActivationView(UpdateAPIView):
    serializer_class = AdminTaskActivationSerializer

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        active_status = serializer.validated_data.get('active')

        if instance.active == active_status or not instance.project.active:
            return Response(serializer.data)

        activation_service = UpdateTaskActiveStatusService(instance, active_status)
        activation_service.execute()
        if not active_status:
            delete_task_subscriptions_service = DeleteTaskSubscriptionsService(instance)
            delete_task_subscriptions_service.execute()

        self.perform_update(serializer)

        return Response(serializer.data)


class TaskStatusUpdateView(UpdateAPIView):
    serializer_class = TaskStatusSerializer

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get('status')

        if instance.status == new_status:
            return Response(serializer.data)

        task_status_update_service = UpdateTaskStatusService(instance, new_status)
        task_status_update_service.execute()

        self.perform_update(serializer)

        return Response(serializer.data)


class TaskExecutorUpdateView(UpdateAPIView):
    serializer_class = TaskExecutorSerializer

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_executor = serializer.validated_data.get('executor_id')

        if instance.executor_id == new_executor:
            return Response(serializer.data)

        task_executor_update_service = UpdateTaskExecutorService(instance, new_executor)
        task_executor_update_service.execute()

        self.perform_update(serializer)

        return Response(serializer.data)


class TaskSubscribersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TaskSubscribersSerializer

    def get_queryset(self):
        return TaskSubscribers.objects.all()


class ProjectParticipantsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectParticipantsSerializer

    def get_queryset(self):
        return ProjectParticipants.objects.all()


class TasksAttachmentsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TasksAttachmentsSerializer

    def get_queryset(self):
        return TasksAttachments.objects.all()
