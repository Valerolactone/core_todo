from django.contrib import admin

from .models import (
    Project,
    ProjectParticipants,
    Task,
    TasksAttachments,
    TaskSubscribers,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectParticipants)
class ProjectParticipantsAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskSubscribers)
class TaskSubscribersAdmin(admin.ModelAdmin):
    pass


@admin.register(TasksAttachments)
class TasksAttachmentsModelAdmin(admin.ModelAdmin):
    pass
