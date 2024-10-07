from api import utils
from api.models import Project, ProjectParticipant, Task, TaskSubscriber
from api.permissions import IsJWTAdmin, IsJWTAuthenticated
from api.serializers import (
    AdminProjectActivationSerializer,
    AdminProjectSerializer,
    AdminTaskActivationSerializer,
    AdminTaskSerializer,
    ProjectParticipantsSerializer,
    ProjectSerializer,
    TaskExecutorSerializer,
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
    send_task_to_kafka,
)
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
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
    permission_classes = [IsJWTAuthenticated]

    def _get_user_pk(self):
        return self.request.user_info.get("user_pk")

    def _check_project_creator_permission(self, instance):
        user_pk = self._get_user_pk()
        if instance.creator_id != user_pk:
            raise PermissionDenied("You do not have permission to modify this project.")

    def get_queryset(self):
        return Project.objects.filter(active=True)

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        user_id = self._get_user_pk()

        instance = serializer.save(creator_id=user_id)
        manage_project_service = ManageProjectService(
            self.request, instance, user_id=user_id
        )
        manage_project_service.add_project_participant()

        project_data = {"title": instance.title, "participant_id": user_id}
        send_task_to_kafka.delay(task_data=project_data, key="create_project")

    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()
        self._check_project_creator_permission(instance)

        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        self._check_project_creator_permission(instance)

        manage_project_service = ManageProjectService(self.request, instance)
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
    permission_classes = [IsJWTAdmin]

    def get_queryset(self):
        return Project.objects.all()

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        user_id = self.request.user_info.get("user_pk")

        instance = serializer.save(creator_id=user_id)
        manage_project_service = ManageProjectService(
            self.request, instance, user_id=user_id
        )
        manage_project_service.add_project_participant()

        project_data = {"title": instance.title, "participant_id": user_id}
        send_task_to_kafka.delay(task_data=project_data, key="create_project")

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_project_service = ManageProjectService(self.request, instance)
        manage_project_service.deactivate_project()


class AdminProjectActivationView(UpdateAPIView):
    serializer_class = AdminProjectActivationSerializer
    permission_classes = [IsJWTAdmin]

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
            self.request, instance, active_status=active_status
        )
        manage_project_service.update_project_active_status()

        self.perform_update(serializer)

        project_data = {"title": instance.title, "is_active": active_status}
        send_task_to_kafka.delay(task_data=project_data, key="update_project")

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
    permission_classes = [IsJWTAuthenticated]

    def _get_user_pk(self):
        return self.request.user_info.get("user_pk")

    def _check_task_creator_permission(self, instance):
        user_pk = self._get_user_pk()
        if instance.creator_id != user_pk:
            raise PermissionDenied("You do not have permission to modify this task.")

    def get_queryset(self):
        return Task.objects.filter(active=True)

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        user_id = self._get_user_pk()

        instance = serializer.save(creator_id=user_id)
        manage_task_serviced = ManageTaskService(
            self.request, instance, user_id=user_id
        )
        manage_task_serviced.add_task_subscription()

        task_data = {
            "title": instance.title,
            "project_title": instance.project.title,
            "status": instance.status,
            "executor_id": instance.executor_id,
            "assigner_id": user_id,
        }

        send_task_to_kafka.delay(task_data=task_data, key="create_task")

    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()
        self._check_task_creator_permission(instance)

        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        self._check_task_creator_permission(instance)

        manage_task_serviced = ManageTaskService(self.request, instance)
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
    permission_classes = [IsJWTAdmin]

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def perform_create(self, serializer, **kwargs):
        user_id = self.request.user_info.get("user_pk")

        instance = serializer.save(creator_id=user_id)
        manage_task_serviced = ManageTaskService(
            self.request, instance, user_id=user_id
        )
        manage_task_serviced.add_task_subscription()

        task_data = {
            "title": instance.title,
            "project_title": instance.project.title,
            "status": instance.status,
            "executor_id": instance.executor_id,
            "assigner_id": user_id,
        }

        send_task_to_kafka.delay(task_data=task_data, key="create_task")

    @transaction.atomic
    def perform_destroy(self, instance):
        manage_task_serviced = ManageTaskService(self.request, instance)
        manage_task_serviced.deactivate_task()


class AdminTaskActivationView(UpdateAPIView):
    serializer_class = AdminTaskActivationSerializer
    permission_classes = [IsJWTAdmin]

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

        manage_task_service = ManageTaskService(
            self.request, instance, active_status=active_status
        )
        manage_task_service.update_task_active_status()

        self.perform_update(serializer)

        task_data = {"title": instance.title, "is_active": active_status}

        send_task_to_kafka.delay(task_data=task_data, key="update_task")

        return Response(serializer.data)


class TaskStatusUpdateView(UpdateAPIView):
    serializer_class = TaskStatusSerializer
    permission_classes = [IsJWTAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        user_pk = self.request.user_info.get("user_pk")
        user_role = self.request.user_info.get("role")
        instance = self.get_object()

        if (
            user_pk not in (instance.creator_id, instance.executor_id)
            or user_role != "admin"
        ):
            raise PermissionDenied(
                "You do not have permission to change the status of this task."
            )

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_status = instance.status
        new_status = serializer.validated_data.get('status')

        if instance.status == new_status:
            return Response(serializer.data)

        self.perform_update(serializer)

        ids = TaskSubscriber.objects.filter(task=instance).values_list(
            'subscriber_id', flat=True
        )
        emails_for_notification = utils.get_emails_for_notification_from_auth(ids=ids)
        send_task_status_update_notification.delay(
            emails_for_notification,
            instance.title,
            old_status,
            new_status,
        )

        task_data = {"title": instance.title, "status": new_status}

        send_task_to_kafka.delay(task_data=task_data, key="update_task")

        return Response(serializer.data)


class TaskExecutorUpdateView(UpdateAPIView):
    serializer_class = TaskExecutorSerializer
    permission_classes = [IsJWTAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        user_pk = self.request.user_info.get("user_pk")
        user_role = self.request.user_info.get("role")
        instance = self.get_object()

        if (
            user_pk not in (instance.creator_id, instance.executor_id)
            or user_role != "admin"
        ):
            raise PermissionDenied(
                "You do not have permission to change the executor of this task."
            )

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_executor_id = serializer.validated_data.get('executor_id')

        if instance.executor_id == new_executor_id:
            return Response(serializer.data)

        task_executor_update_service = UpdateTaskExecutorService(
            request, instance, new_executor_id
        )
        task_executor_update_service.update_executor()

        self.perform_update(serializer)

        task_data = {
            "title": instance.title,
            "executor_id": new_executor_id,
            "assigner_id": self.request.user_info.get("user_pk"),
            "project_title": instance.project.title,
        }

        send_task_to_kafka.delay(task_data=task_data, key="update_task")

        return Response(serializer.data)


class TaskSubscribersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TaskSubscribersSerializer
    permission_classes = [IsJWTAuthenticated]

    def get_queryset(self):
        return TaskSubscriber.objects.all()

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

        email_for_notification = utils.get_email_for_notification(
            request, subscriber_id
        )

        send_subscription_on_task_notification.delay(email_for_notification, task.title)

        if not ProjectParticipant.objects.filter(
            project=task.project.project_pk, participant_id=subscriber_id
        ).exists():
            send_join_to_project_notification.delay(
                email_for_notification, task.project.title
            )

        task_data = {
            "title": task.title,
            "executor_id": subscriber_id,
            "assigner_id": self.request.user_info.get("user_pk"),
            "project_title": task.project.title,
        }

        send_task_to_kafka.delay(task_data=task_data, key="update_task")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectParticipantsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectParticipantsSerializer
    permission_classes = [IsJWTAuthenticated]

    def get_queryset(self):
        return ProjectParticipant.objects.all()

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

        email_for_notification = utils.get_email_for_notification(
            request, participant_id
        )

        project_title = Project.objects.get(project_pk=project.project_pk).title
        send_join_to_project_notification.delay(email_for_notification, project_title)

        project_data = {"title": project_title, "participant_id": participant_id}

        send_task_to_kafka.delay(task_data=project_data, key="update_project")

        return Response(serializer.data, status=status.HTTP_201_CREATED)
