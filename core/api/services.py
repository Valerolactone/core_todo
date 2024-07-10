from .models import ProjectModel
from .serializers import ProjectSerializer


def get_personalized_queryset(request):
    if request.user.is_staff:
        queryset = ProjectModel.objects.all()
    else:
        queryset = ProjectModel.objects.filter(active=True)

    return queryset


def get_personalized_serializer(request, data, **kwargs):
    user_fields = ('project_pk', 'title', 'description', 'logo', 'created_at')
    if request.user.is_staff:
        serializer = (
            ProjectSerializer(data, many=kwargs.get('many'))
            if 'many' in kwargs
            else ProjectSerializer(data)
        )
    else:
        serializer = (
            ProjectSerializer(data, many=kwargs.get('many'), fields=user_fields)
            if 'many' in kwargs
            else ProjectSerializer(data, fields=user_fields)
        )

    return serializer
