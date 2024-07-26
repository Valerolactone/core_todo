from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from .models import Project, ProjectParticipant, Task, TasksAttachment, TaskSubscriber
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
from .services import ManageProjectService, ManageTaskService, UpdateTaskExecutorService


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
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            manage_project_service = ManageProjectService(instance, user_id=user_id)
            manage_project_service.add_project_participant()

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_project_service = ManageProjectService(instance)
        manage_project_service.deactivate_project()


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
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            manage_project_service = ManageProjectService(instance, user_id=user_id)
            manage_project_service.add_project_participant()

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_project_service = ManageProjectService(instance)
        manage_project_service.deactivate_project()


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

        manage_project_service = ManageProjectService(
            instance, active_status=active_status
        )
        manage_project_service.update_project_active_status()

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
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            manage_task_serviced = ManageTaskService(instance, user_id=user_id)
            manage_task_serviced.add_task_subscription()

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_task_serviced = ManageTaskService(instance)
        manage_task_serviced.deactivate_task()


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
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            manage_task_serviced = ManageTaskService(instance, user_id=user_id)
            manage_task_serviced.add_task_subscription()

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_task_serviced = ManageTaskService(instance)
        manage_task_serviced.deactivate_task()


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

        manage_task_service = ManageTaskService(instance, active_status=active_status)
        manage_task_service.update_task_active_status()

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

        task = Task.objects.get(task_pk=instance.task_pk)
        task.status = new_status

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
        new_executor_id = serializer.validated_data.get('executor_id')

        if instance.executor_id == new_executor_id:
            return Response(serializer.data)

        task_executor_update_service = UpdateTaskExecutorService(
            instance, new_executor_id
        )
        task_executor_update_service.update_executor()

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
        return TaskSubscriber.objects.all()


class ProjectParticipantsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectParticipantsSerializer

    def get_queryset(self):
        return ProjectParticipant.objects.all()


class TasksAttachmentsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TasksAttachmentsSerializer

    def get_queryset(self):
        return TasksAttachment.objects.all()
