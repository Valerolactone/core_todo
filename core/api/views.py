from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import ProjectModel
from .serializers import ProjectSerializer
from .services import get_personalized_queryset, get_personalized_serializer


class ProjectViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = get_personalized_queryset(request)
        serializer = get_personalized_serializer(request, queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        queryset = get_personalized_queryset(request)
        project = get_object_or_404(queryset, project_pk=pk)
        serializer = get_personalized_serializer(request, project)

        return Response(serializer.data)

    def create(self, request):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, **kwargs):
        instance = ProjectModel.objects.get(project_pk=kwargs.get('pk'))
        serializer = ProjectSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "active" in request.data:
            instance.deleted_at = None if request.data.get('active') else datetime.now()
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, **kwargs):
        instance = ProjectModel.objects.get(project_pk=kwargs.get('pk'))
        instance.active = False
        instance.deleted_at = datetime.now()
        instance.save()

        return Response(
            {
                "status": "Success",
                "Message": f"Record about project {instance.title} deleted",
            }
        )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
