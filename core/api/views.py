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


class ProjectViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProjectModel.objects.filter(active=True)
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.active = False
        instance.deleted_at = datetime.now()
        instance.save()

        return Response(
            {
                "Status": "Success",
                "Message": f"Record about project {instance.title} deleted.",
            }
        )


class AdminProjectViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProjectModel.objects.all()
    serializer_class = AdminProjectSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "active" in request.data:
            instance.deleted_at = None if request.data.get('active') else datetime.now()
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.active = False
        instance.deleted_at = datetime.now()
        instance.save()

        return Response(
            {
                "Status": "Success",
                "Message": f"Record about project {instance.title} deleted.",
            }
        )


class TaskViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TaskModel.objects.filter(active=True)
    serializer_class = TaskSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['title', 'status']
    ordering_fields = ['title', 'created_at']

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.active = False
        instance.deleted_at = datetime.now()
        instance.save()

        return Response(
            {
                "Status": "Success",
                "Message": f"Record about task {instance.title} deleted.",
            }
        )


class AdminTaskViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = AdminTaskSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['title', 'status']
    ordering_fields = ['title', 'created_at']

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "active" in request.data:
            instance.deleted_at = None if request.data.get('active') else datetime.now()
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.active = False
        instance.deleted_at = datetime.now()
        instance.save()

        return Response(
            {
                "Status": "Success",
                "Message": f"Record about task {instance.title} deleted.",
            }
        )


class TaskSubscribersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TaskSubscribersModel.objects.all()
    serializer_class = TaskSubscribersSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)


class ProjectParticipantsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProjectParticipantsModel.objects.all()
    serializer_class = ProjectParticipantsSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)


class TasksAttachmentsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TasksAttachmentsModel.objects.all()
    serializer_class = TasksAttachmentsSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)
