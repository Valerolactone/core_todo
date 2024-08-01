from api.models import (
    Project,
    ProjectParticipant,
    Task,
    TasksAttachment,
    TaskSubscriber,
)
from api.serializers import (
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
from api.services import (
    ManageProjectService,
    ManageTaskService,
    UpdateTaskExecutorService,
)
from api.tasks import (
    send_join_to_project_notification,
    send_subscription_on_task_notification,
    send_task_status_update_notification,
)
from django.conf import settings
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response


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
        manage_project_service = ManageProjectService(instance, user_id=1)
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
        manage_project_service = ManageProjectService(instance, user_id=1)
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
        manage_task_serviced = ManageTaskService(instance, user_id=1)
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
        manage_task_serviced = ManageTaskService(instance, user_id=1)
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
        old_status = instance.status
        new_status = serializer.validated_data.get('status')

        if instance.status == new_status:
            return Response(serializer.data)

        self.perform_update(serializer)

        # TODO: получение списка имаилов для подписчиков задачи
        send_task_status_update_notification.delay(
            [settings.TEST_EMAIL_FOR_CELERY, settings.TEST_EMAIL_FOR_CELERY_1],
            instance.title,
            old_status,
            new_status,
        )

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

    # TODO: получить имейл участника
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data.get('task')
        subscriber_id = serializer.validated_data.get('subscriber_id')

        if TaskSubscriber.objects.filter(
            task=task.task_pk, subscriber_id=subscriber_id
        ).exists():
            return Response(serializer.data)

        self.perform_create(serializer)

        send_subscription_on_task_notification.delay(
            settings.TEST_EMAIL_FOR_CELERY, task.title
        )

        if not ProjectParticipant.objects.filter(
            project=task.project.project_pk, participant_id=subscriber_id
        ).exists():
            send_join_to_project_notification.delay(
                settings.TEST_EMAIL_FOR_CELERY, task.project.title
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectParticipantsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectParticipantsSerializer

    def get_queryset(self):
        return ProjectParticipant.objects.all()

    # TODO: получить имейл участника
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data.get('project')
        participant_id = serializer.validated_data.get('participant_id')

        if ProjectParticipant.objects.filter(
            project=project.project_pk, participant_id=participant_id
        ).exists():
            return Response(serializer.data)

        self.perform_create(serializer)

        send_join_to_project_notification.delay(
            settings.TEST_EMAIL_FOR_CELERY, project.title
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TasksAttachmentsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TasksAttachmentsSerializer

    def get_queryset(self):
        return TasksAttachment.objects.all()
