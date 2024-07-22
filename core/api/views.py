from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from .models import (
    ProjectModel,
    ProjectParticipantsModel,
    TaskModel,
    TasksAttachmentsModel,
    TaskSubscribersModel,
)
from .serializers import (
    AdminProjectActivationSerializer,
    AdminProjectSerializer,
    AdminTaskActivationSerializer,
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


class AdminProjectActivationView(UpdateAPIView):
    serializer_class = AdminProjectActivationSerializer

    def get_queryset(self):
        return ProjectModel.objects.all()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.active != self.request.data.get('active'):
            instance.deleted_at = (
                None if self.request.data.get('active') else datetime.utcnow()
            )
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
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
        return TaskModel.objects.filter(active=True)

    def perform_destroy(self, instance):
        instance.active = False
        instance.deleted_at = datetime.utcnow()
        instance.save()


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


class AdminTaskActivationView(UpdateAPIView):
    serializer_class = AdminTaskActivationSerializer

    def get_queryset(self):
        return TaskModel.objects.all()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.active != self.request.data.get('active'):
            instance.deleted_at = (
                None if self.request.data.get('active') else datetime.utcnow()
            )
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


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
