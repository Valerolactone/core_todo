from django.contrib import admin

from .models import (
    ProjectModel,
    ProjectParticipantsModel,
    TaskModel,
    TasksAttachmentsModel,
    TaskSubscribersModel,
)


@admin.register(ProjectModel)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskModel)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectParticipantsModel)
class ProjectParticipantsAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskSubscribersModel)
class TaskSubscribersAdmin(admin.ModelAdmin):
    pass


@admin.register(TasksAttachmentsModel)
class TasksAttachmentsModelAdmin(admin.ModelAdmin):
    pass
