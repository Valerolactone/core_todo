from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response

from .models import (
    ProjectModel,
    ProjectParticipantsModel,
    TaskModel,
    TasksAttachmentsModel,
    TaskSubscribersModel,
)
from .serializers import (
    AdminProjectSerializer,
    AdminTaskSerializer,
    ProjectParticipantsSerializer,
    ProjectSerializer,
    TasksAttachmentsSerializer,
    TaskSerializer,
    TaskSubscribersSerializer,
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
        return ProjectModel.objects.filter(active=True)

    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return ProjectModel.objects.all()

    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return TaskModel.objects.filter(active=True)

    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return TaskModel.objects.all()

    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskSubscribersViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = TaskSubscribersSerializer

    def get_queryset(self):
        return TaskSubscribersModel.objects.all()


class ProjectParticipantsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = ProjectParticipantsSerializer

    def get_queryset(self):
        return ProjectParticipantsModel.objects.all()


class TasksAttachmentsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = TasksAttachmentsSerializer

    def get_queryset(self):
        return TasksAttachmentsModel.objects.all()
