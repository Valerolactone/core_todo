from api.models import (
    Project,
    ProjectParticipant,
    Task,
    TasksAttachment,
    TaskSubscriber,
)
from django.contrib import admin


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectParticipant)
class ProjectParticipantsAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskSubscriber)
class TaskSubscribersAdmin(admin.ModelAdmin):
    pass


@admin.register(TasksAttachment)
class TasksAttachmentsModelAdmin(admin.ModelAdmin):
    pass
