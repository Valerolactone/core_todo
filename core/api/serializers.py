from rest_framework import serializers

from .models import ProjectModel


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProjectSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProjectModel
        fields = '__all__'
        read_only_fields = ['project_pk', 'created_at', 'deleted_at']
